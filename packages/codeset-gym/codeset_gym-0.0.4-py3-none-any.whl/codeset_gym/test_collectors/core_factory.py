from typing import Dict, Type

from .core import CoreTestResultCollector
from .python_core import PythonCoreTestResultCollector
from .java_core import JavaCoreTestResultCollector
from .javascript_core import JavaScriptCoreTestResultCollector
from .go_core import GoCoreTestResultCollector
from .rust_core import RustCoreTestResultCollector
from .csharp_core import CSharpCoreTestResultCollector
from .cpp_core import CppCoreTestResultCollector


class CoreTestResultCollectorFactory:
    """Factory for creating container-agnostic test result collectors."""

    _collectors: Dict[str, Type[CoreTestResultCollector]] = {
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

    @classmethod
    def get_collector(cls, language: str) -> CoreTestResultCollector:
        """
        Get a core test result collector for the specified language.

        Args:
            language: The programming language (e.g., 'python', 'java', 'javascript')

        Returns:
            CoreTestResultCollector instance for the language

        Raises:
            ValueError: If the language is not supported
        """
        language_lower = language.lower()

        if language_lower not in cls._collectors:
            supported_languages = ", ".join(cls._collectors.keys())
            raise ValueError(
                f"Unsupported language: {language}. Supported languages: {supported_languages}"
            )

        collector_class = cls._collectors[language_lower]
        return collector_class()

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """Get list of supported languages."""
        return list(cls._collectors.keys())