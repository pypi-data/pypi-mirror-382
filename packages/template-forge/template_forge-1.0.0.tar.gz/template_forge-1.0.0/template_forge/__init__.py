"""Template Forge - Structured Data Edition.

A Python package for generating text files using Jinja2 templates with tokens
extracted from structured data files (JSON, YAML, XML, ARXML).
"""

__version__ = "1.0.0"
__author__ = "Carlo Fornari"
# __email__ = "carlo.fornari@example.com"
__description__ = (
    "Advanced template generation with full Jinja2 power and enhanced data extraction"
)

# Import main classes for easy access
from .cli import main as cli_main
from .core import TemplateForge
from .extraction import StructuredDataExtractor
from .hooks import HookExecutor
from .preservation import PreservationHandler
from .processing import TemplateProcessor

__all__ = [
    "HookExecutor",
    "PreservationHandler",
    "StructuredDataExtractor",
    "TemplateForge",
    "TemplateProcessor",
    "cli_main",
]
