import io
import tarfile
import tempfile
import os
from typing import Dict, Type

import junitparser
from docker.models.containers import Container

from .core import CoreTestResultCollector
from .python_core import PythonCoreTestResultCollector
from .java_core import JavaCoreTestResultCollector
from .javascript_core import JavaScriptCoreTestResultCollector
from .go_core import GoCoreTestResultCollector
from .rust_core import RustCoreTestResultCollector
from .csharp_core import CSharpCoreTestResultCollector
from .cpp_core import CppCoreTestResultCollector


class ContainerTestResultCollector:
    """Adapter that wraps core test collectors to work with Docker containers."""

    _core_collectors: Dict[str, Type[CoreTestResultCollector]] = {
        "python": PythonCoreTestResultCollector,
        "java": JavaCoreTestResultCollector,
        "javascript": JavaScriptCoreTestResultCollector,
        "typescript": JavaScriptCoreTestResultCollector,
        "go": GoCoreTestResultCollector,
        "rust": RustCoreTestResultCollector,
        "csharp": CSharpCoreTestResultCollector,
        "c": CppCoreTestResultCollector,
        "cpp": CppCoreTestResultCollector,
        "c++": CppCoreTestResultCollector,
    }

    def __init__(self, language: str):
        """
        Initialize the container adapter for a specific language.

        Args:
            language: The programming language

        Raises:
            ValueError: If the language is not supported
        """
        language_lower = language.lower()
        if language_lower not in self._core_collectors:
            supported_languages = ", ".join(self._core_collectors.keys())
            raise ValueError(
                f"Unsupported language: {language}. Supported languages: {supported_languages}"
            )

        self.language = language_lower
        self.core_collector = self._core_collectors[language_lower]()

    def get_test_results(self, instance_id: str, container: Container) -> junitparser.JUnitXml:
        """
        Get test results from the container by extracting files to a temporary directory.

        Args:
            instance_id: The instance ID being processed
            container: Docker container instance

        Returns:
            JUnitXml test suite

        Raises:
            Exception: If test results cannot be retrieved
        """
        repository = self._get_repository(instance_id)

        # Create a temporary directory to extract container files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the entire repository directory from the container
            try:
                archive_data, _ = container.get_archive(path=f"/{repository}")
                archive_bytes = b"".join(archive_data)

                # Extract the archive to the temporary directory
                with tarfile.open(fileobj=io.BytesIO(archive_bytes)) as tar:
                    tar.extractall(temp_dir)

                # The extracted directory will be temp_dir/repository
                extracted_path = os.path.join(temp_dir, repository)

                # Use the core collector to parse the results
                return self.core_collector.get_test_results_from_path(extracted_path)

            except Exception as e:
                raise RuntimeError(f"Failed to extract and parse test results for {instance_id}: {e}")

    def _get_repository(self, instance_id: str) -> str:
        """Extract repository name from instance ID."""
        return instance_id.rsplit("-", 1)[0].split("__")[1]

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """Get list of supported languages."""
        return list(cls._core_collectors.keys())