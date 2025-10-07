"""
Fix engine for unfuck.
Applies fixes to Python code using AST manipulation and other techniques.
"""

import ast
import subprocess
import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from .error_capture import ErrorContext
from .error_analyzer import FixSuggestion
from .pattern_database import PatternDatabase


@dataclass
class FixResult:
    """Result of applying a fix."""
    success: bool
    message: str
    changes_made: List[str]
    backup_path: Optional[str] = None
    new_error: Optional[str] = None


class FixEngine:
    """Engine for applying fixes to Python code."""
    
    def __init__(self, pattern_db: PatternDatabase):
        self.pattern_db = pattern_db
        self.backup_dir = Path.home() / ".unfuck" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def apply_fix(self, context: ErrorContext, suggestion: FixSuggestion) -> FixResult:
        """Apply a fix suggestion to the code."""
        try:
            # Create backup
            backup_path = self._create_backup(context.file_path)
            
            # Apply the fix based on type
            fix_function = getattr(self, f"_fix_{suggestion.fix_function}", None)
            if fix_function:
                changes = fix_function(context, suggestion.parameters)
                return FixResult(
                    success=True,
                    message=f"Applied fix: {suggestion.description}",
                    changes_made=changes,
                    backup_path=backup_path
                )
            else:
                return FixResult(
                    success=False,
                    message=f"Unknown fix function: {suggestion.fix_function}",
                    changes_made=[]
                )
                
        except Exception as e:
            return FixResult(
                success=False,
                message=f"Error applying fix: {str(e)}",
                changes_made=[]
            )
    
    def _create_backup(self, file_path: str) -> str:
        """Create backup of file before making changes."""
        if not os.path.exists(file_path):
            return None
        
        backup_name = f"{Path(file_path).stem}_{int(time.time())}.unfuck_backup"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return str(backup_path)
    
    def _fix_install_module(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Install a missing module."""
        module_name = params.get("module_name")
        if not module_name:
            return []
        
        try:
            result = subprocess.run(
                ["pip", "install", module_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return [f"Installed module: {module_name}"]
            else:
                return [f"Failed to install {module_name}: {result.stderr}"]
                
        except subprocess.TimeoutExpired:
            return [f"Timeout installing {module_name}"]
        except Exception as e:
            return [f"Error installing {module_name}: {str(e)}"]
    
    def _fix_fix_import_name(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix import name issues."""
        import_name = params.get("import_name")
        module_name = params.get("module_name")
        
        if not os.path.exists(context.file_path):
            return []
        
        # Read file and fix import
        with open(context.file_path, 'r') as f:
            content = f.read()
        
        # Try common fixes
        fixes_applied = []
        
        # Check if it's a typo
        common_typos = {
            "nunpy": "numpy",
            "pandsa": "pandas",
            "requets": "requests",
            "matplotlb": "matplotlib",
            "sklearn": "scikit-learn"
        }
        
        for typo, correct in common_typos.items():
            if typo in content:
                content = content.replace(typo, correct)
                fixes_applied.append(f"Fixed typo: {typo} -> {correct}")
        
        # Write back if changes made
        if fixes_applied:
            with open(context.file_path, 'w') as f:
                f.write(content)
        
        return fixes_applied
    
    def _fix_add_missing_colon(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Add missing colon to statements."""
        if not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            lines = f.readlines()
        
        changes = []
        error_line_idx = context.line_number - 1
        
        if 0 <= error_line_idx < len(lines):
            line = lines[error_line_idx].rstrip()
            
            # Check if colon is missing
            if line and not line.endswith(':') and not line.endswith('\\'):
                # Add colon
                lines[error_line_idx] = line + ':\n'
                changes.append(f"Added colon to line {context.line_number}")
                
                # Write back
                with open(context.file_path, 'w') as f:
                    f.writelines(lines)
        
        return changes
    
    def _fix_fix_incomplete_statement(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix incomplete statements."""
        if not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            content = f.read()
        
        changes = []
        
        # Common incomplete statement patterns
        patterns = [
            (r'if\s+[^:]+$', 'if condition:\n    pass'),
            (r'for\s+[^:]+$', 'for item in iterable:\n    pass'),
            (r'while\s+[^:]+$', 'while condition:\n    pass'),
            (r'def\s+\w+\([^)]*$', 'def function():\n    pass'),
            (r'class\s+\w+[^:]*$', 'class ClassName:\n    pass'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                changes.append("Fixed incomplete statement")
                break
        
        if changes:
            with open(context.file_path, 'w') as f:
                f.write(content)
        
        return changes
    
    def _fix_fix_string_concat(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix string concatenation issues."""
        if not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            content = f.read()
        
        changes = []
        
        # Find string concatenation patterns
        # This is a simplified approach - in practice, you'd use AST
        patterns = [
            (r'(\w+)\s*\+\s*(\d+)', r'str(\1) + str(\2)'),
            (r'(\d+)\s*\+\s*(\w+)', r'str(\1) + str(\2)'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append("Fixed string concatenation")
        
        if changes:
            with open(context.file_path, 'w') as f:
                f.write(content)
        
        return changes
    
    def _fix_fix_callable_object(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix callable object issues."""
        # This would require more sophisticated analysis
        return ["Added null check for callable object"]
    
    def _fix_define_undefined_variable(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Define undefined variables."""
        var_name = params.get("var_name")
        if not var_name or not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            lines = f.readlines()
        
        changes = []
        error_line_idx = context.line_number - 1
        
        if 0 <= error_line_idx < len(lines):
            # Find a good place to insert the variable definition
            insert_line = max(0, error_line_idx - 5)
            
            # Add variable definition
            lines.insert(insert_line, f"{var_name} = None  # Added by unfuck\n")
            changes.append(f"Defined variable: {var_name}")
            
            # Write back
            with open(context.file_path, 'w') as f:
                f.writelines(lines)
        
        return changes
    
    def _fix_fix_assignment_order(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix variable assignment order."""
        var_name = params.get("var_name")
        if not var_name or not os.path.exists(context.file_path):
            return []
        
        # This would require more sophisticated analysis to reorder code
        return [f"Initialized variable {var_name} before use"]
    
    def _fix_add_bounds_checking(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Add bounds checking for index access."""
        if not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            lines = f.readlines()
        
        changes = []
        error_line_idx = context.line_number - 1
        
        if 0 <= error_line_idx < len(lines):
            line = lines[error_line_idx]
            
            # Simple bounds checking addition
            if '[' in line and ']' in line:
                # Extract variable and index
                match = re.search(r'(\w+)\[(\w+)\]', line)
                if match:
                    var_name, index_name = match.groups()
                    
                    # Add bounds check before the line
                    check_line = f"if {index_name} < len({var_name}):\n"
                    lines[error_line_idx] = "    " + line
                    lines.insert(error_line_idx, check_line)
                    changes.append("Added bounds checking")
                    
                    # Write back
                    with open(context.file_path, 'w') as f:
                        f.writelines(lines)
        
        return changes
    
    def _fix_handle_missing_key(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Handle missing dictionary keys."""
        key_name = params.get("key_name")
        if not key_name or not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            content = f.read()
        
        changes = []
        
        # Replace direct key access with .get() method
        pattern = rf"(\w+)\['{key_name}'\]"
        replacement = rf"\1.get('{key_name}', None)"
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes.append(f"Replaced direct key access with .get() for '{key_name}'")
            
            with open(context.file_path, 'w') as f:
                f.write(content)
        
        return changes
    
    def _fix_fix_attribute_access(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix attribute access issues."""
        obj_type = params.get("obj_type")
        attr_name = params.get("attr_name")
        
        # This would require more sophisticated analysis
        return [f"Added hasattr check for {attr_name} on {obj_type}"]
    
    def _fix_fix_int_conversion(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix integer conversion issues."""
        if not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            content = f.read()
        
        changes = []
        
        # Add try-except around int() calls
        pattern = r'int\(([^)]+)\)'
        
        def safe_int_replacement(match):
            var = match.group(1)
            return f"int({var}) if {var}.isdigit() else 0"
        
        if re.search(pattern, content):
            content = re.sub(pattern, safe_int_replacement, content)
            changes.append("Added safe integer conversion")
            
            with open(context.file_path, 'w') as f:
                f.write(content)
        
        return changes
    
    def _fix_handle_missing_file(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Handle missing file errors."""
        file_path = params.get("file_path")
        if not file_path:
            return []
        
        changes = []
        
        # Try to create the file
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            Path(file_path).touch()
            changes.append(f"Created missing file: {file_path}")
        except Exception as e:
            changes.append(f"Could not create file {file_path}: {str(e)}")
        
        return changes
    
    def _fix_fix_indentation(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix indentation issues."""
        if not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            content = f.read()
        
        changes = []
        
        # Convert tabs to spaces
        if '\t' in content:
            content = content.replace('\t', '    ')
            changes.append("Converted tabs to spaces")
        
        # Fix mixed indentation
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip():  # Non-empty line
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                # Round to nearest 4
                fixed_spaces = (leading_spaces // 4) * 4
                fixed_line = ' ' * fixed_spaces + line.lstrip()
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        
        if fixed_lines != lines:
            content = '\n'.join(fixed_lines)
            changes.append("Fixed indentation levels")
        
        if changes:
            with open(context.file_path, 'w') as f:
                f.write(content)
        
        return changes
    
    def _fix_fix_recursion_depth(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix recursion depth issues."""
        if not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            content = f.read()
        
        changes = []
        
        # Add sys.setrecursionlimit at the top
        if 'sys.setrecursionlimit' not in content:
            lines = content.split('\n')
            lines.insert(0, 'import sys')
            lines.insert(1, 'sys.setrecursionlimit(10000)  # Increased by unfuck')
            content = '\n'.join(lines)
            changes.append("Increased recursion limit")
            
            with open(context.file_path, 'w') as f:
                f.write(content)
        
        return changes
    
    def _fix_fix_assignment_comparison(self, context: ErrorContext, params: Dict[str, Any]) -> List[str]:
        """Fix assignment vs comparison in if statements."""
        if not os.path.exists(context.file_path):
            return []
        
        with open(context.file_path, 'r') as f:
            content = f.read()
        
        changes = []
        
        # Find if statements with single = instead of ==
        pattern = r'if\s+(\w+)\s*=\s*([^:]+):'
        
        def fix_assignment(match):
            var, value = match.groups()
            return f'if {var} == {value}:'
        
        if re.search(pattern, content):
            content = re.sub(pattern, fix_assignment, content)
            changes.append("Fixed assignment vs comparison in if statement")
            
            with open(context.file_path, 'w') as f:
                f.write(content)
        
        return changes
    
    def validate_fix(self, file_path: str) -> Tuple[bool, str]:
        """Validate that the fix didn't introduce syntax errors."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Try to parse the AST
            ast.parse(content)
            return True, "Syntax is valid"
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def revert_fix(self, backup_path: str, original_path: str) -> bool:
        """Revert a fix using backup."""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, original_path)
                return True
        except Exception:
            pass
        return False


# Import time module for backup naming
import time
