import junitparser

from .core import CoreTestResultCollector


class RustCoreTestResultCollector(CoreTestResultCollector):
    """Core test result collector for Rust projects."""

    def get_test_results_from_path(self, working_dir: str) -> junitparser.JUnitXml:
        """
        Get test results from Rust projects.

        Args:
            working_dir: Path to the working directory containing test results

        Returns:
            JUnitXml test suite from Rust test

        Raises:
            RuntimeError: If test results are not found
        """
        # Try standard Rust test output
        rust_result = self._try_single_xml_path(working_dir, "target/nextest/junit.xml")
        if rust_result:
            return rust_result

        # Try alternative path
        rust_result = self._try_single_xml_path(working_dir, "test-results.xml")
        if rust_result:
            return rust_result

        raise RuntimeError(f"No Rust test results found in {working_dir}")
