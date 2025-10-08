"""MeoMaya package initialization.

Avoid importing subpackages at import time so build backends (flit/poetry)
can import this module to read metadata without triggering package-level
imports that assume the package is already installed.
"""

__version__ = "v1"

__all__ = ["core", "ml", "data", "cli"]
