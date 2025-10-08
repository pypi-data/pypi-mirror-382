import io
import sys
import json
import docker
import tarfile
import junitparser

from typing import Dict, Any
from docker.models.containers import Container
from datasets import load_dataset

from .test_collectors.factory import TestResultCollectorFactory


client = docker.from_env()


def __get_repository(instance_id: str) -> str:
    return instance_id.rsplit("-", 1)[0].split("__")[1]


def start_instance(
    repository: str, instance_id: str, version: str, dataset_name: str
) -> Container:
    instance_id = instance_id.lower()
    container = client.containers.run(
        image=f"{repository}/{dataset_name}.{instance_id}:{version}",
        command=["tail", "-f", "/dev/null"],
        detach=True,
        stdin_open=True,
        tty=True,
    )
    return container



def get_test_results(
    instance_id: str, container: Container, language
) -> junitparser.JUnitXml:
    """
    Get test results using the appropriate collector for the language.

    Args:
        instance_id: The instance ID being processed
        container: Docker container instance
        language: The programming language (default: "python")

    Returns:
        JUnitXml test suite from the appropriate test framework

    Raises:
        RuntimeError: If test results cannot be retrieved
    """
    try:
        collector = TestResultCollectorFactory.get_collector(language)
        return collector.get_test_results(instance_id, container)
    except Exception as e:
        error_msg = f"Failed to get test results for {instance_id} with language {language}: {e}"
        raise RuntimeError(error_msg)


def run_verifier(instance_id: str, container: Container) -> Dict[str, Any]:
    repository = __get_repository(instance_id)
    # Remove previous test results
    container.exec_run(f"rm /{repository}/report.xml")
    container.exec_run(f"rm -rf /{repository}/test_reports")
    result = container.exec_run("/verifier.sh")
    return {"stdout": result.output.decode(), "exit_code": result.exit_code}


def stop_instance(container: Container):
    container.stop()
    container.remove()


def apply_patch(sample: Dict[str, Any], container: Container):
    repository = __get_repository(sample["instance_id"])
    patch_content = sample["patch"]
    non_code_patch_content = sample["non_code_patch"]
    stdout = ""

    for patch in [
        (patch_content, "patch"),
        (non_code_patch_content, "non_code_patch"),
    ]:
        if not patch[0]:
            continue

        patch_bytes = patch[0].encode("utf-8")
        patch_tar = io.BytesIO()

        with tarfile.open(
            fileobj=patch_tar, mode="w", format=tarfile.GNU_FORMAT
        ) as tar:
            info = tarfile.TarInfo(name=f"{patch[1]}.diff")
            info.size = len(patch_bytes)
            tar.addfile(info, io.BytesIO(patch_bytes))

        patch_tar.seek(0)
        container.put_archive(path=f"/tmp", data=patch_tar.getvalue())

        result = container.exec_run(
            f"git apply /tmp/{patch[1]}.diff", workdir=f"/{repository}"
        )
        stdout += result.output.decode()
        if result.exit_code != 0:
            return {"stdout": stdout, "exit_code": result.exit_code}

    return {"stdout": stdout, "exit_code": 0}


def check_test_results(
    sample: Dict[str, Any],
    test_results: junitparser.JUnitXml,
    previous_commit: bool = False,
) -> Dict[str, Any]:
    fail_to_pass_tests = json.loads(sample["FAIL_TO_PASS"])
    pass_to_pass_tests = json.loads(sample["PASS_TO_PASS"])
    fail_to_fail_tests = json.loads(sample["FAIL_TO_FAIL"])

    if previous_commit:
        expected_failures = set(fail_to_pass_tests + fail_to_fail_tests)
        expected_passes = set(pass_to_pass_tests)

        actual_failures = set()
        actual_passes = set()
        actual_skipped = set()

        for test_case in test_results:
            if hasattr(test_case, "result"):
                test_name = f"{test_case.classname}::{test_case.name}"
                if test_case.is_skipped:
                    actual_skipped.add(test_name)
                elif test_case.result:
                    actual_failures.add(test_name)
                else:
                    actual_passes.add(test_name)
            else:
                for sub_test in test_case:
                    test_name = f"{sub_test.classname}::{sub_test.name}"
                    if sub_test.is_skipped:
                        actual_skipped.add(test_name)
                    elif sub_test.result:
                        actual_failures.add(test_name)
                    else:
                        actual_passes.add(test_name)

        expected_failures_correct = expected_failures == actual_failures
        expected_passes_correct = expected_passes == actual_passes

        return {
            "correct": expected_failures_correct and expected_passes_correct,
            "expected_failures_correct": expected_failures_correct,
            "expected_passes_correct": expected_passes_correct,
            "expected_failures": list(expected_failures),
            "actual_failures": list(actual_failures),
            "expected_passes": list(expected_passes),
            "actual_passes": list(actual_passes),
            "actual_skipped": list(actual_skipped),
        }
    else:
        expected_passes = set(fail_to_pass_tests + pass_to_pass_tests)
        expected_failures = set(fail_to_fail_tests)

        actual_passes = set()
        actual_failures = set()
        actual_skipped = set()
        for test_case in test_results:
            if hasattr(test_case, "result"):
                if test_case.is_skipped:
                    test_name = f"{test_case.classname}::{test_case.name}"
                    actual_skipped.add(test_name)
                elif test_case.result:
                    test_name = f"{test_case.classname}::{test_case.name}"
                    actual_failures.add(test_name)
                else:
                    test_name = f"{test_case.classname}::{test_case.name}"
                    actual_passes.add(test_name)
            else:
                for sub_test in test_case:
                    if sub_test.is_skipped:
                        test_name = f"{sub_test.classname}::{sub_test.name}"
                        actual_skipped.add(test_name)
                    elif sub_test.result:
                        test_name = f"{sub_test.classname}::{sub_test.name}"
                        actual_failures.add(test_name)
                    else:
                        test_name = f"{sub_test.classname}::{sub_test.name}"
                        actual_passes.add(test_name)

        expected_passes_correct = expected_passes == actual_passes
        expected_failures_correct = expected_failures == actual_failures

        return {
            "correct": expected_passes_correct and expected_failures_correct,
            "expected_failures_correct": expected_failures_correct,
            "expected_passes_correct": expected_passes_correct,
            "expected_passes": list(expected_passes),
            "expected_failures": list(expected_failures),
            "actual_passes": list(actual_passes),
            "actual_failures": list(actual_failures),
            "actual_skipped": list(actual_skipped),
        }


def get_sample_by_id(dataset, instance_id: str):
    for sample in dataset:
        if sample["instance_id"] == instance_id:
            return sample
    return None


def main():
    instance_id = sys.argv[1]
    repository = sys.argv[2]
    version = "0.0.1"
    dataset_name = sys.argv[3] if len(sys.argv) > 3 else None
    if not dataset_name:
        print("Error: dataset_name is required as the third argument")
        sys.exit(1)

    dataset = load_dataset("codeset/codeset-gym-python", split="train")
    sample = get_sample_by_id(dataset, instance_id)

    container = start_instance(repository, instance_id, version, dataset_name)
    try:
        run_verifier(instance_id, container)
        test_results = get_test_results(instance_id, container, "python")
        assert check_test_results(sample, test_results, previous_commit=True)["correct"]
        print("✅ Successfully processed without patch", instance_id)

        # Apply the patch first
        apply_patch(sample, container)

        # Then run verifier and tests
        run_verifier(instance_id, container)
        test_results = get_test_results(instance_id, container, "python")
        assert check_test_results(sample, test_results)["correct"]
        print("✅ Successfully processed with patch", instance_id)
    finally:
        stop_instance(container)


if __name__ == "__main__":
    main()
