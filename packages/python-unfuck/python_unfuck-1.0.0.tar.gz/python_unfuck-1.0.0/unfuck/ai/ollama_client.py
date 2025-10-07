"""
Ollama client for unfuck AI features.
Provides local LLM integration for complex error analysis.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class AIResponse:
    """Response from AI analysis."""
    success: bool
    message: str
    suggestions: List[Dict[str, Any]]
    confidence: float
    reasoning: str


class OllamaClient:
    """Client for interacting with Ollama local LLM."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        self.session.timeout = 30
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception:
            pass
        return []
    
    def analyze_error(self, error_context: Dict[str, Any]) -> AIResponse:
        """Analyze an error using AI."""
        if not self.is_available():
            return AIResponse(
                success=False,
                message="Ollama is not available",
                suggestions=[],
                confidence=0.0,
                reasoning="Ollama service not running"
            )
        
        prompt = self._create_analysis_prompt(error_context)
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_ai_response(data.get("response", ""))
            else:
                return AIResponse(
                    success=False,
                    message=f"Ollama API error: {response.status_code}",
                    suggestions=[],
                    confidence=0.0,
                    reasoning="API request failed"
                )
                
        except Exception as e:
            return AIResponse(
                success=False,
                message=f"Error communicating with Ollama: {str(e)}",
                suggestions=[],
                confidence=0.0,
                reasoning="Communication error"
            )
    
    def _create_analysis_prompt(self, error_context: Dict[str, Any]) -> str:
        """Create a prompt for error analysis."""
        return f"""
You are an expert Python debugging assistant. Analyze this error and provide specific, actionable fixes.

Error Details:
- Type: {error_context.get('error_type', 'Unknown')}
- Message: {error_context.get('error_message', 'No message')}
- File: {error_context.get('file_path', 'Unknown')}
- Line: {error_context.get('line_number', 0)}
- Function: {error_context.get('function_name', 'Unknown')}

Code Context:
{chr(10).join(error_context.get('code_context', []))}

Local Variables:
{json.dumps(error_context.get('local_vars', {}), indent=2)}

Please provide:
1. Root cause analysis
2. Specific fix suggestions with code examples
3. Confidence level (0.0-1.0)
4. Alternative approaches if the primary fix fails

Format your response as JSON:
{{
    "root_cause": "Brief explanation of what went wrong",
    "fixes": [
        {{
            "description": "What this fix does",
            "code_changes": "Specific code changes needed",
            "confidence": 0.9,
            "explanation": "Why this fix works"
        }}
    ],
    "confidence": 0.8,
    "reasoning": "Detailed explanation of the analysis"
}}
"""
    
    def _parse_ai_response(self, response_text: str) -> AIResponse:
        """Parse AI response into structured format."""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                return AIResponse(
                    success=True,
                    message="AI analysis completed",
                    suggestions=data.get("fixes", []),
                    confidence=data.get("confidence", 0.5),
                    reasoning=data.get("reasoning", "")
                )
            else:
                # Fallback: parse as text
                return AIResponse(
                    success=True,
                    message="AI analysis completed (text format)",
                    suggestions=[{
                        "description": "AI suggested fix",
                        "code_changes": response_text,
                        "confidence": 0.6,
                        "explanation": "AI-generated suggestion"
                    }],
                    confidence=0.6,
                    reasoning="Parsed from text response"
                )
                
        except json.JSONDecodeError:
            return AIResponse(
                success=False,
                message="Could not parse AI response",
                suggestions=[],
                confidence=0.0,
                reasoning="Invalid JSON response"
            )
        except Exception as e:
            return AIResponse(
                success=False,
                message=f"Error parsing AI response: {str(e)}",
                suggestions=[],
                confidence=0.0,
                reasoning="Parse error"
            )
    
    def generate_fix_code(self, error_context: Dict[str, Any], fix_description: str) -> str:
        """Generate specific fix code for an error."""
        prompt = f"""
Generate Python code to fix this error:

Error: {error_context.get('error_type')} - {error_context.get('error_message')}
File: {error_context.get('file_path')}
Line: {error_context.get('line_number')}

Code around error:
{chr(10).join(error_context.get('code_context', []))}

Fix needed: {fix_description}

Provide only the corrected code, with minimal changes to fix the specific error.
Include comments explaining what was changed.
"""
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "max_tokens": 500
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                return f"Error generating fix: {response.status_code}"
                
        except Exception as e:
            return f"Error generating fix: {str(e)}"
    
    def explain_fix(self, error_context: Dict[str, Any], fix_applied: str) -> str:
        """Generate explanation for an applied fix."""
        prompt = f"""
Explain this Python error fix in simple terms:

Original Error:
{error_context.get('error_type')} - {error_context.get('error_message')}

Fix Applied:
{fix_applied}

Provide a clear, educational explanation of:
1. What the error meant
2. Why the fix works
3. How to avoid this error in the future

Keep it concise and beginner-friendly.
"""
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "max_tokens": 300
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                return f"Error generating explanation: {response.status_code}"
                
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
