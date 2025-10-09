from typing import Dict, Any

import junitparser
from docker.models.containers import Container

from .base import TestResultCollector
from .container_adapter import ContainerTestResultCollector


class RustTestResultCollector(TestResultCollector):
    """Test result collector for Rust projects (backward compatibility wrapper)."""

    def __init__(self):
        self._adapter = ContainerTestResultCollector("rust")

    def get_test_results(
        self, instance_id: str, container: Container
    ) -> junitparser.JUnitXml:
        """
        Get test results using the new container adapter.

        Args:
            instance_id: The instance ID being processed
            container: Docker container instance

        Returns:
            JUnitXml test suite

        Raises:
            RuntimeError: If test results cannot be retrieved
        """
        return self._adapter.get_test_results(instance_id, container)
