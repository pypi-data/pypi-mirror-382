"""
regex-vault: A general-purpose engine for detecting and masking personal information.

This package provides tools for PII detection, validation, and redaction using
pattern-based matching organized by country and information type.
"""

__version__ = "0.1.2"

from regexvault.engine import Engine
from regexvault.models import FindResult, RedactionResult, ValidationResult
from regexvault.registry import PatternRegistry, load_registry

__all__ = [
    "Engine",
    "load_registry",
    "PatternRegistry",
    "FindResult",
    "ValidationResult",
    "RedactionResult",
]
