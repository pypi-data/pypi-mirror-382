"""
LangLint: A scalable, domain-agnostic platform for automated translation 
and standardization of structured text in scientific collaboration.

This package provides a pluggable parser architecture for detecting, 
translating, and standardizing text in various file types including 
source code, documentation, configuration files, and Jupyter Notebooks.
"""

__version__ = "0.0.5"
__author__ = "LangLint Team"
__email__ = "langlint@example.com"
__license__ = "MIT"

from .core.dispatcher import Dispatcher
from .parsers.base import Parser, TranslatableUnit
from .translators.base import Translator
from .cli import main

__all__ = [
    "Dispatcher",
    "Parser", 
    "TranslatableUnit",
    "Translator",
    "main",
]