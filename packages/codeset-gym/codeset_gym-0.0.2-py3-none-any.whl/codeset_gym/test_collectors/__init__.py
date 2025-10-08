"""Test result collectors for different programming languages."""

# Container-based collectors (backward compatibility)
from .factory import TestResultCollectorFactory
from .base import TestResultCollector

# Core collectors (container-agnostic)
from .core_factory import CoreTestResultCollectorFactory
from .core import CoreTestResultCollector

# Container adapter
from .container_adapter import ContainerTestResultCollector

__all__ = [
    # Backward compatibility - container-based
    "TestResultCollectorFactory",
    "TestResultCollector",

    # Core - container-agnostic
    "CoreTestResultCollectorFactory",
    "CoreTestResultCollector",

    # Container adapter
    "ContainerTestResultCollector",
]