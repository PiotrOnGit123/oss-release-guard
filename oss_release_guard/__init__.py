"""Offline checksum and archive-metadata checks for release maintainers."""

__version__ = "0.1.0"

from .core import AuditError, inspect_release

__all__ = ["AuditError", "inspect_release", "__version__"]
