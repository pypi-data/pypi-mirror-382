"""
Core unfuck modules for error capture, analysis, and fixing.
"""

from .error_capture import ErrorCapture
from .fix_engine import FixEngine
from .pattern_database import PatternDatabase
from .error_analyzer import ErrorAnalyzer

__all__ = [
    "ErrorCapture",
    "FixEngine",
    "PatternDatabase", 
    "ErrorAnalyzer",
]
