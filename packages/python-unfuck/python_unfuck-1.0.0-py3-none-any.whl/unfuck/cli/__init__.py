"""
CLI interface for unfuck.
The magical command-line experience that makes debugging fun!
"""

from .main import main
from .ui import UnfuckUI
from .personality import UnfuckPersonality

__all__ = [
    "main",
    "UnfuckUI", 
    "UnfuckPersonality",
]
