"""
Error analysis engine for unfuck.
Analyzes errors and determines the best fix strategy.
"""

import re
import ast
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from .error_capture import ErrorContext


class ErrorCategory(Enum):
    """Categories of Python errors."""
    SYNTAX = "syntax"
    IMPORT = "import"
    TYPE = "type"
    VALUE = "value"
    NAME = "name"
    INDEX = "index"
    KEY = "key"
    ATTRIBUTE = "attribute"
    FILE = "file"
    INDENTATION = "indentation"
    MEMORY = "memory"
    RECURSION = "recursion"
    UNKNOWN = "unknown"


@dataclass
class FixSuggestion:
    """A suggested fix for an error."""
    category: ErrorCategory
    confidence: float
    description: str
    fix_function: str
    parameters: Dict[str, Any]
    explanation: str


class ErrorAnalyzer:
    """Analyzes errors and suggests fixes."""
    
    def __init__(self):
        self.patterns = self._load_error_patterns()
    
    def _load_error_patterns(self) -> Dict[str, Dict]:
        """Load error pattern matching rules."""
        return {
            # Import errors
            "ModuleNotFoundError": {
                "category": ErrorCategory.IMPORT,
                "patterns": [
                    r"No module named '([^']+)'",
                    r"cannot import name '([^']+)' from '([^']+)'",
                ],
                "confidence": 0.9
            },
            "ImportError": {
                "category": ErrorCategory.IMPORT,
                "patterns": [
                    r"cannot import name '([^']+)'",
                    r"No module named '([^']+)'",
                ],
                "confidence": 0.8
            },
            
            # Syntax errors
            "SyntaxError": {
                "category": ErrorCategory.SYNTAX,
                "patterns": [
                    r"invalid syntax",
                    r"unexpected EOF while parsing",
                    r"expected ':'",
                    r"unindent does not match any outer indentation level",
                ],
                "confidence": 0.95
            },
            "IndentationError": {
                "category": ErrorCategory.INDENTATION,
                "patterns": [
                    r"expected an indented block",
                    r"unindent does not match any outer indentation level",
                ],
                "confidence": 0.9
            },
            
            # Type errors
            "TypeError": {
                "category": ErrorCategory.TYPE,
                "patterns": [
                    r"can only concatenate str \(not \"([^\"]+)\"\) to str",
                    r"unsupported operand type\(s\) for",
                    r"object of type '([^']+)' has no len\(\)",
                    r"'([^']+)' object is not callable",
                ],
                "confidence": 0.8
            },
            
            # Name errors
            "NameError": {
                "category": ErrorCategory.NAME,
                "patterns": [
                    r"name '([^']+)' is not defined",
                    r"free variable '([^']+)' referenced before assignment",
                ],
                "confidence": 0.85
            },
            "UnboundLocalError": {
                "category": ErrorCategory.NAME,
                "patterns": [
                    r"local variable '([^']+)' referenced before assignment",
                ],
                "confidence": 0.9
            },
            
            # Index/Key errors
            "IndexError": {
                "category": ErrorCategory.INDEX,
                "patterns": [
                    r"list index out of range",
                    r"string index out of range",
                ],
                "confidence": 0.9
            },
            "KeyError": {
                "category": ErrorCategory.KEY,
                "patterns": [
                    r"'([^']+)'",
                ],
                "confidence": 0.9
            },
            
            # Attribute errors
            "AttributeError": {
                "category": ErrorCategory.ATTRIBUTE,
                "patterns": [
                    r"'([^']+)' object has no attribute '([^']+)'",
                    r"module '([^']+)' has no attribute '([^']+)'",
                ],
                "confidence": 0.8
            },
            
            # Value errors
            "ValueError": {
                "category": ErrorCategory.VALUE,
                "patterns": [
                    r"invalid literal for int\(\) with base \d+: '([^']+)'",
                    r"could not convert string to float: '([^']+)'",
                    r"too many values to unpack",
                ],
                "confidence": 0.8
            },
            
            # File errors
            "FileNotFoundError": {
                "category": ErrorCategory.FILE,
                "patterns": [
                    r"No such file or directory: '([^']+)'",
                ],
                "confidence": 0.95
            },
            "PermissionError": {
                "category": ErrorCategory.FILE,
                "patterns": [
                    r"Permission denied: '([^']+)'",
                ],
                "confidence": 0.9
            },
            
            # Memory/Recursion errors
            "MemoryError": {
                "category": ErrorCategory.MEMORY,
                "patterns": [
                    r"",
                ],
                "confidence": 0.7
            },
            "RecursionError": {
                "category": ErrorCategory.RECURSION,
                "patterns": [
                    r"maximum recursion depth exceeded",
                ],
                "confidence": 0.9
            },
        }
    
    def analyze_error(self, context: ErrorContext) -> List[FixSuggestion]:
        """Analyze an error and return fix suggestions."""
        suggestions = []
        
        # Get error pattern info
        error_info = self.patterns.get(context.error_type, {})
        category = error_info.get("category", ErrorCategory.UNKNOWN)
        base_confidence = error_info.get("confidence", 0.5)
        
        # Pattern matching
        patterns = error_info.get("patterns", [])
        for pattern in patterns:
            match = re.search(pattern, context.error_message)
            if match:
                suggestions.extend(self._generate_fixes_for_pattern(
                    context, category, pattern, match, base_confidence
                ))
        
        # Code context analysis
        suggestions.extend(self._analyze_code_context(context, category))
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _generate_fixes_for_pattern(self, context: ErrorContext, category: ErrorCategory, 
                                  pattern: str, match: re.Match, base_confidence: float) -> List[FixSuggestion]:
        """Generate fixes based on pattern matching."""
        suggestions = []
        
        if category == ErrorCategory.IMPORT:
            suggestions.extend(self._fix_import_errors(context, match, base_confidence))
        elif category == ErrorCategory.SYNTAX:
            suggestions.extend(self._fix_syntax_errors(context, match, base_confidence))
        elif category == ErrorCategory.TYPE:
            suggestions.extend(self._fix_type_errors(context, match, base_confidence))
        elif category == ErrorCategory.NAME:
            suggestions.extend(self._fix_name_errors(context, match, base_confidence))
        elif category == ErrorCategory.INDEX:
            suggestions.extend(self._fix_index_errors(context, match, base_confidence))
        elif category == ErrorCategory.KEY:
            suggestions.extend(self._fix_key_errors(context, match, base_confidence))
        elif category == ErrorCategory.ATTRIBUTE:
            suggestions.extend(self._fix_attribute_errors(context, match, base_confidence))
        elif category == ErrorCategory.VALUE:
            suggestions.extend(self._fix_value_errors(context, match, base_confidence))
        elif category == ErrorCategory.FILE:
            suggestions.extend(self._fix_file_errors(context, match, base_confidence))
        elif category == ErrorCategory.INDENTATION:
            suggestions.extend(self._fix_indentation_errors(context, match, base_confidence))
        elif category == ErrorCategory.RECURSION:
            suggestions.extend(self._fix_recursion_errors(context, match, base_confidence))
        
        return suggestions
    
    def _fix_import_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for import errors."""
        suggestions = []
        
        if "No module named" in context.error_message:
            module_name = match.group(1)
            suggestions.append(FixSuggestion(
                category=ErrorCategory.IMPORT,
                confidence=confidence,
                description=f"Install missing module '{module_name}'",
                fix_function="install_module",
                parameters={"module_name": module_name},
                explanation=f"The module '{module_name}' is not installed. Installing it with pip."
            ))
        
        elif "cannot import name" in context.error_message:
            if len(match.groups()) >= 2:
                import_name = match.group(1)
                module_name = match.group(2)
                suggestions.append(FixSuggestion(
                    category=ErrorCategory.IMPORT,
                    confidence=confidence * 0.8,
                    description=f"Fix import '{import_name}' from '{module_name}'",
                    fix_function="fix_import_name",
                    parameters={"import_name": import_name, "module_name": module_name},
                    explanation=f"The import '{import_name}' doesn't exist in module '{module_name}'. Checking for correct name."
                ))
        
        return suggestions
    
    def _fix_syntax_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for syntax errors."""
        suggestions = []
        
        if "expected ':'" in context.error_message:
            suggestions.append(FixSuggestion(
                category=ErrorCategory.SYNTAX,
                confidence=confidence,
                description="Add missing colon",
                fix_function="add_missing_colon",
                parameters={},
                explanation="Missing colon after if/for/while/def/class statement."
            ))
        
        elif "unexpected EOF" in context.error_message:
            suggestions.append(FixSuggestion(
                category=ErrorCategory.SYNTAX,
                confidence=confidence * 0.8,
                description="Fix incomplete statement",
                fix_function="fix_incomplete_statement",
                parameters={},
                explanation="Incomplete statement detected. Adding missing syntax elements."
            ))
        
        return suggestions
    
    def _fix_type_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for type errors."""
        suggestions = []
        
        if "can only concatenate str" in context.error_message:
            suggestions.append(FixSuggestion(
                category=ErrorCategory.TYPE,
                confidence=confidence,
                description="Convert to string for concatenation",
                fix_function="fix_string_concat",
                parameters={},
                explanation="Cannot concatenate string with non-string. Converting to string."
            ))
        
        elif "object is not callable" in context.error_message:
            suggestions.append(FixSuggestion(
                category=ErrorCategory.TYPE,
                confidence=confidence * 0.8,
                description="Fix callable object",
                fix_function="fix_callable_object",
                parameters={},
                explanation="Trying to call a non-callable object. Checking if it should be a function."
            ))
        
        return suggestions
    
    def _fix_name_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for name errors."""
        suggestions = []
        
        if "is not defined" in context.error_message:
            var_name = match.group(1)
            suggestions.append(FixSuggestion(
                category=ErrorCategory.NAME,
                confidence=confidence,
                description=f"Define undefined variable '{var_name}'",
                fix_function="define_undefined_variable",
                parameters={"var_name": var_name},
                explanation=f"Variable '{var_name}' is not defined. Adding definition."
            ))
        
        elif "referenced before assignment" in context.error_message:
            var_name = match.group(1)
            suggestions.append(FixSuggestion(
                category=ErrorCategory.NAME,
                confidence=confidence,
                description=f"Fix variable '{var_name}' assignment order",
                fix_function="fix_assignment_order",
                parameters={"var_name": var_name},
                explanation=f"Variable '{var_name}' used before assignment. Reordering code."
            ))
        
        return suggestions
    
    def _fix_index_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for index errors."""
        suggestions = []
        
        suggestions.append(FixSuggestion(
            category=ErrorCategory.INDEX,
            confidence=confidence,
            description="Add bounds checking",
            fix_function="add_bounds_checking",
            parameters={},
            explanation="Index out of range. Adding bounds checking to prevent crash."
        ))
        
        return suggestions
    
    def _fix_key_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for key errors."""
        suggestions = []
        
        key_name = match.group(1)
        suggestions.append(FixSuggestion(
            category=ErrorCategory.KEY,
            confidence=confidence,
            description=f"Handle missing key '{key_name}'",
            fix_function="handle_missing_key",
            parameters={"key_name": key_name},
            explanation=f"Key '{key_name}' not found in dictionary. Using .get() with default value."
        ))
        
        return suggestions
    
    def _fix_attribute_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for attribute errors."""
        suggestions = []
        
        if len(match.groups()) >= 2:
            obj_type = match.group(1)
            attr_name = match.group(2)
            suggestions.append(FixSuggestion(
                category=ErrorCategory.ATTRIBUTE,
                confidence=confidence * 0.8,
                description=f"Fix attribute '{attr_name}' on '{obj_type}'",
                fix_function="fix_attribute_access",
                parameters={"obj_type": obj_type, "attr_name": attr_name},
                explanation=f"Attribute '{attr_name}' doesn't exist on '{obj_type}'. Checking for correct attribute name."
            ))
        
        return suggestions
    
    def _fix_value_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for value errors."""
        suggestions = []
        
        if "invalid literal for int" in context.error_message:
            suggestions.append(FixSuggestion(
                category=ErrorCategory.VALUE,
                confidence=confidence,
                description="Fix invalid integer conversion",
                fix_function="fix_int_conversion",
                parameters={},
                explanation="Invalid value for integer conversion. Adding validation or using try-except."
            ))
        
        return suggestions
    
    def _fix_file_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for file errors."""
        suggestions = []
        
        if "No such file or directory" in context.error_message:
            file_path = match.group(1)
            suggestions.append(FixSuggestion(
                category=ErrorCategory.FILE,
                confidence=confidence,
                description=f"Handle missing file '{file_path}'",
                fix_function="handle_missing_file",
                parameters={"file_path": file_path},
                explanation=f"File '{file_path}' not found. Creating it or fixing the path."
            ))
        
        return suggestions
    
    def _fix_indentation_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for indentation errors."""
        suggestions = []
        
        suggestions.append(FixSuggestion(
            category=ErrorCategory.INDENTATION,
            confidence=confidence,
            description="Fix indentation",
            fix_function="fix_indentation",
            parameters={},
            explanation="Indentation error detected. Fixing indentation levels."
        ))
        
        return suggestions
    
    def _fix_recursion_errors(self, context: ErrorContext, match: re.Match, confidence: float) -> List[FixSuggestion]:
        """Generate fixes for recursion errors."""
        suggestions = []
        
        suggestions.append(FixSuggestion(
            category=ErrorCategory.RECURSION,
            confidence=confidence,
            description="Fix recursion depth",
            fix_function="fix_recursion_depth",
            parameters={},
            explanation="Maximum recursion depth exceeded. Adding base case or increasing limit."
        ))
        
        return suggestions
    
    def _analyze_code_context(self, context: ErrorContext, category: ErrorCategory) -> List[FixSuggestion]:
        """Analyze code context for additional fix suggestions."""
        suggestions = []
        
        # Look for common patterns in the code
        if context.code_context:
            error_line_idx = None
            for i, line in enumerate(context.code_context):
                if i == len(context.code_context) // 2:  # Assume error is in middle
                    error_line_idx = i
                    break
            
            if error_line_idx is not None:
                error_line = context.code_context[error_line_idx]
                
                # Check for common typos
                if "=" in error_line and "==" not in error_line and "if" in context.code_context[max(0, error_line_idx-2):error_line_idx]:
                    suggestions.append(FixSuggestion(
                        category=ErrorCategory.SYNTAX,
                        confidence=0.7,
                        description="Fix assignment vs comparison",
                        fix_function="fix_assignment_comparison",
                        parameters={},
                        explanation="Possible assignment instead of comparison in if statement."
                    ))
        
        return suggestions
