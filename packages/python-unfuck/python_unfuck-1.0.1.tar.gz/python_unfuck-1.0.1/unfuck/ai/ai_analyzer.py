"""
AI-powered error analyzer for unfuck.
Combines pattern matching with AI analysis for complex errors.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .ollama_client import OllamaClient, AIResponse
from ..core.error_capture import ErrorContext
from ..core.error_analyzer import FixSuggestion, ErrorCategory


@dataclass
class AIAnalysisResult:
    """Result of AI-powered error analysis."""
    suggestions: List[FixSuggestion]
    confidence: float
    reasoning: str
    ai_used: bool


class AIAnalyzer:
    """AI-powered error analyzer."""
    
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama_client = ollama_client or OllamaClient()
        self.ai_available = self.ollama_client.is_available()
    
    def analyze_error(self, context: ErrorContext) -> AIAnalysisResult:
        """Analyze error using both pattern matching and AI."""
        suggestions = []
        confidence = 0.0
        reasoning = ""
        ai_used = False
        
        # First, try pattern-based analysis
        pattern_suggestions = self._analyze_with_patterns(context)
        suggestions.extend(pattern_suggestions)
        
        # If pattern analysis didn't find good suggestions, try AI
        if not suggestions or max(s.get('confidence', 0) for s in suggestions) < 0.7:
            if self.ai_available:
                ai_result = self._analyze_with_ai(context)
                if ai_result.success:
                    ai_suggestions = self._convert_ai_suggestions(ai_result.suggestions)
                    suggestions.extend(ai_suggestions)
                    confidence = max(confidence, ai_result.confidence)
                    reasoning = ai_result.reasoning
                    ai_used = True
        
        # Calculate overall confidence
        if suggestions:
            confidence = max(s.get('confidence', 0) for s in suggestions)
        
        return AIAnalysisResult(
            suggestions=suggestions,
            confidence=confidence,
            reasoning=reasoning,
            ai_used=ai_used
        )
    
    def _analyze_with_patterns(self, context: ErrorContext) -> List[FixSuggestion]:
        """Analyze error using pattern matching (placeholder)."""
        # This would integrate with the pattern database
        # For now, return empty list to trigger AI analysis
        return []
    
    def _analyze_with_ai(self, context: ErrorContext) -> AIResponse:
        """Analyze error using AI."""
        error_context = {
            "error_type": context.error_type,
            "error_message": context.error_message,
            "file_path": context.file_path,
            "line_number": context.line_number,
            "function_name": context.function_name,
            "code_context": context.code_context,
            "local_vars": context.local_vars,
            "global_vars": context.global_vars,
            "traceback": context.traceback
        }
        
        return self.ollama_client.analyze_error(error_context)
    
    def _convert_ai_suggestions(self, ai_suggestions: List[Dict[str, Any]]) -> List[FixSuggestion]:
        """Convert AI suggestions to FixSuggestion objects."""
        suggestions = []
        
        for suggestion in ai_suggestions:
            fix_suggestion = FixSuggestion(
                category=ErrorCategory.UNKNOWN,  # AI doesn't categorize
                confidence=suggestion.get("confidence", 0.5),
                description=suggestion.get("description", "AI suggested fix"),
                fix_function="ai_fix",
                parameters={
                    "code_changes": suggestion.get("code_changes", ""),
                    "explanation": suggestion.get("explanation", "")
                },
                explanation=suggestion.get("explanation", "AI-generated fix")
            )
            suggestions.append(fix_suggestion)
        
        return suggestions
    
    def generate_fix_code(self, context: ErrorContext, fix_description: str) -> str:
        """Generate specific fix code using AI."""
        if not self.ai_available:
            return "AI not available for code generation"
        
        error_context = {
            "error_type": context.error_type,
            "error_message": context.error_message,
            "file_path": context.file_path,
            "line_number": context.line_number,
            "code_context": context.code_context
        }
        
        return self.ollama_client.generate_fix_code(error_context, fix_description)
    
    def explain_fix(self, context: ErrorContext, fix_applied: str) -> str:
        """Generate explanation for an applied fix."""
        if not self.ai_available:
            return "AI not available for explanation"
        
        error_context = {
            "error_type": context.error_type,
            "error_message": context.error_message,
            "file_path": context.file_path,
            "line_number": context.line_number
        }
        
        return self.ollama_client.explain_fix(error_context, fix_applied)
    
    def is_ai_available(self) -> bool:
        """Check if AI features are available."""
        return self.ai_available
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get status of AI integration."""
        status = {
            "available": self.ai_available,
            "models": [],
            "current_model": None
        }
        
        if self.ai_available:
            status["models"] = self.ollama_client.get_available_models()
            status["current_model"] = self.ollama_client.model
        
        return status
