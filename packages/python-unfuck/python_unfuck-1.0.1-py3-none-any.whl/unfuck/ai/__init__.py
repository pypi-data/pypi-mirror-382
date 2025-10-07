"""
AI integration for unfuck.
Uses Ollama for complex error analysis and fix generation.
"""

from .ollama_client import OllamaClient
from .ai_analyzer import AIAnalyzer

__all__ = [
    "OllamaClient",
    "AIAnalyzer",
]
