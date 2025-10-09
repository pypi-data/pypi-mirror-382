import junitparser

from .core import CoreTestResultCollector


class JavaCoreTestResultCollector(CoreTestResultCollector):
    """Core test result collector for Java projects."""

    def get_test_results_from_path(self, working_dir: str) -> junitparser.JUnitXml:
        """
        Get test results from Java projects, trying Maven first, then Gradle.

        Args:
            working_dir: Path to the working directory containing test results

        Returns:
            JUnitXml test suite from either Maven or Gradle

        Raises:
            RuntimeError: If both Maven and Gradle methods fail
        """
        # Try Maven surefire reports first
        maven_result = self._try_multiple_xml_pattern(working_dir, "target/surefire-reports/*.xml")
        if maven_result:
            return maven_result

        # Fallback to Gradle test results
        gradle_result = self._try_multiple_xml_pattern(working_dir, "build/test-results/test/*.xml")
        if gradle_result:
            return gradle_result

        raise RuntimeError(f"No Maven or Gradle test results found in {working_dir}")