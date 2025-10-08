"""Potential requirements for the different QA class.

Some class might require a specific external package to be installed.
This file provides helper functions for the requirements.

"""

from enum import Enum


class PythonPackageRequirement(Enum):
    """Python package that can be required by a QA class."""

    PYTORCH = "torch"
    SKLEARN = "sklearn"

    def check(self) -> bool:
        """Check if the package is installed."""
        try:
            __import__(self.value)
            return True
        except ImportError:
            return False
