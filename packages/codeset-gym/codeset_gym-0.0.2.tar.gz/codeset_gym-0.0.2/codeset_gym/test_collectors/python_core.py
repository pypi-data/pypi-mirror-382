import junitparser

from .core import CoreTestResultCollector


class PythonCoreTestResultCollector(CoreTestResultCollector):
    """Core test result collector for Python projects."""

    def get_test_results_from_path(self, working_dir: str) -> junitparser.JUnitXml:
        """
        Get test results using pytest first, fallback to unittest if pytest fails.

        Args:
            working_dir: Path to the working directory containing test results

        Returns:
            JUnitXml test suite from either pytest or unittest

        Raises:
            RuntimeError: If both pytest and unittest methods fail
        """
        # Try pytest first (report.xml)
        pytest_result = self._try_single_xml_path(working_dir, "report.xml")
        if pytest_result:
            return pytest_result

        # Fallback to unittest (test_reports folder)
        unittest_result = self._try_multiple_xml_pattern(working_dir, "test_reports/*.xml")
        if unittest_result:
            return unittest_result

        raise RuntimeError(f"No test results found in {working_dir}")