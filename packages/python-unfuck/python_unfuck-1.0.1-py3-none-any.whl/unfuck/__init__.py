"""
unfuck - The magical Python error fixing tool 🔥

Because life's too short to debug!
"""

__version__ = "1.0.0"
__author__ = "Sherin Joseph"
__email__ = "sherin.joseph2217@gmail.com"

from .core.error_capture import ErrorCapture
from .core.fix_engine import FixEngine
from .core.pattern_database import PatternDatabase

__all__ = [
    "ErrorCapture",
    "FixEngine", 
    "PatternDatabase",
    "__version__",
    "__author__",
    "__email__",
]
