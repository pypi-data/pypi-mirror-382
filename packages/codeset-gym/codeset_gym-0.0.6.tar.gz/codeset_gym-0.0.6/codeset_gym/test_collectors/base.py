import io
import tarfile
from abc import ABC, abstractmethod
from typing import Dict, Any

import junitparser
from docker.models.containers import Container


class TestResultCollector(ABC):
    """Base class for test result collectors."""

    @abstractmethod
    def get_test_results(
        self, instance_id: str, container: Container
    ) -> junitparser.JUnitXml:
        """
        Get test results from the container.

        Args:
            instance_id: The instance ID being processed
            container: Docker container instance

        Returns:
            JUnitXml test suite

        Raises:
            Exception: If test results cannot be retrieved
        """
        pass

    def _get_repository(self, instance_id: str) -> str:
        """Extract repository name from instance ID."""
        return instance_id.rsplit("-", 1)[0].split("__")[1]

    def _extract_archive(self, container: Container, path: str) -> tarfile.TarFile:
        """Extract archive from container."""
        archive_data, _ = container.get_archive(path=path)
        archive_bytes = b"".join(archive_data)
        return tarfile.open(fileobj=io.BytesIO(archive_bytes))

    def _get_single_xml_from_archive(
        self, instance_id: str, container: Container, path: str
    ) -> junitparser.JUnitXml:
        """Extract and parse a single XML file from container archive."""
        repository = self._get_repository(instance_id)
        tar = self._extract_archive(container, f"/{repository}{path}")
        xml_content = tar.extractfile(tar.getnames()[0]).read()
        return junitparser.JUnitXml.fromstring(xml_content)

    def _get_multiple_xml_from_archive(
        self, instance_id: str, container: Container, path: str
    ) -> junitparser.JUnitXml:
        """Extract and parse multiple XML files from container archive."""
        repository = self._get_repository(instance_id)
        tar = self._extract_archive(container, f"/{repository}{path}")
        combined_suite = junitparser.JUnitXml()

        for member in tar.getmembers():
            if member.name.endswith(".xml"):
                try:
                    xml_content = tar.extractfile(member).read()
                    xml_suite = junitparser.JUnitXml.fromstring(xml_content)
                    combined_suite.add_testsuite(xml_suite)
                except Exception:
                    continue

        if len(combined_suite) == 0:
            raise RuntimeError("No valid XML files found")

        return combined_suite
