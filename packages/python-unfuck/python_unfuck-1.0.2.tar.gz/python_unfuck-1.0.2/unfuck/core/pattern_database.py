"""
Pattern database for unfuck.
Contains pre-loaded fixes for common Python errors.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .error_analyzer import ErrorCategory, FixSuggestion


@dataclass
class FixPattern:
    """A fix pattern for a specific error."""
    error_type: str
    error_pattern: str
    fix_type: str
    fix_code: str
    confidence: float
    description: str
    examples: List[str]


class PatternDatabase:
    """Database of error fix patterns."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path.home() / ".unfuck" / "patterns.db")
        self._setup_database()
        self._load_default_patterns()
    
    def _setup_database(self):
        """Initialize SQLite database for pattern storage."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    error_pattern TEXT NOT NULL,
                    fix_type TEXT NOT NULL,
                    fix_code TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    description TEXT NOT NULL,
                    examples TEXT,
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_type 
                ON patterns(error_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pattern 
                ON patterns(error_pattern)
            """)
    
    def _load_default_patterns(self):
        """Load default fix patterns."""
        patterns = self._get_default_patterns()
        
        with sqlite3.connect(self.db_path) as conn:
            for pattern in patterns:
                # Check if pattern already exists
                cursor = conn.execute("""
                    SELECT id FROM patterns 
                    WHERE error_type = ? AND error_pattern = ?
                """, (pattern.error_type, pattern.error_pattern))
                
                if not cursor.fetchone():
                    conn.execute("""
                        INSERT INTO patterns (
                            error_type, error_pattern, fix_type, fix_code,
                            confidence, description, examples
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pattern.error_type,
                        pattern.error_pattern,
                        pattern.fix_type,
                        pattern.fix_code,
                        pattern.confidence,
                        pattern.description,
                        json.dumps(pattern.examples)
                    ))
    
    def _get_default_patterns(self) -> List[FixPattern]:
        """Get default fix patterns."""
        return [
            # Import errors
            FixPattern(
                error_type="ModuleNotFoundError",
                error_pattern="No module named 'numpy'",
                fix_type="install_module",
                fix_code="pip install numpy",
                confidence=0.95,
                description="Install numpy package",
                examples=["import numpy as np"]
            ),
            FixPattern(
                error_type="ModuleNotFoundError", 
                error_pattern="No module named 'pandas'",
                fix_type="install_module",
                fix_code="pip install pandas",
                confidence=0.95,
                description="Install pandas package",
                examples=["import pandas as pd"]
            ),
            FixPattern(
                error_type="ModuleNotFoundError",
                error_pattern="No module named 'requests'",
                fix_type="install_module", 
                fix_code="pip install requests",
                confidence=0.95,
                description="Install requests package",
                examples=["import requests"]
            ),
            FixPattern(
                error_type="ImportError",
                error_pattern="cannot import name 'nunpy'",
                fix_type="fix_typo",
                fix_code="numpy",
                confidence=0.9,
                description="Fix typo in import name",
                examples=["import nunpy as np -> import numpy as np"]
            ),
            
            # Syntax errors
            FixPattern(
                error_type="SyntaxError",
                error_pattern="expected ':'",
                fix_type="add_colon",
                fix_code=":",
                confidence=0.9,
                description="Add missing colon",
                examples=["if x > 5 -> if x > 5:"]
            ),
            FixPattern(
                error_type="IndentationError",
                error_pattern="expected an indented block",
                fix_type="fix_indentation",
                fix_code="    pass",
                confidence=0.85,
                description="Add indented block",
                examples=["if True: -> if True:\n    pass"]
            ),
            
            # Type errors
            FixPattern(
                error_type="TypeError",
                error_pattern="can only concatenate str",
                fix_type="string_conversion",
                fix_code="str()",
                confidence=0.8,
                description="Convert to string for concatenation",
                examples=['"Hello" + 123 -> "Hello" + str(123)']
            ),
            FixPattern(
                error_type="TypeError",
                error_pattern="'NoneType' object is not callable",
                fix_type="null_check",
                fix_code="if obj is not None:",
                confidence=0.8,
                description="Add null check before calling",
                examples=["obj() -> if obj is not None: obj()"]
            ),
            
            # Name errors
            FixPattern(
                error_type="NameError",
                error_pattern="name 'x' is not defined",
                fix_type="define_variable",
                fix_code="x = None",
                confidence=0.7,
                description="Define undefined variable",
                examples=["print(x) -> x = None; print(x)"]
            ),
            FixPattern(
                error_type="UnboundLocalError",
                error_pattern="local variable 'x' referenced before assignment",
                fix_type="initialize_variable",
                fix_code="x = None",
                confidence=0.8,
                description="Initialize variable before use",
                examples=["def f(): print(x); x = 1 -> def f(): x = None; print(x); x = 1"]
            ),
            
            # Index errors
            FixPattern(
                error_type="IndexError",
                error_pattern="list index out of range",
                fix_type="bounds_check",
                fix_code="if i < len(lst):",
                confidence=0.85,
                description="Add bounds checking",
                examples=["lst[i] -> if i < len(lst): lst[i]"]
            ),
            FixPattern(
                error_type="IndexError",
                error_pattern="string index out of range",
                fix_type="string_bounds_check",
                fix_code="if i < len(s):",
                confidence=0.85,
                description="Add string bounds checking",
                examples=["s[i] -> if i < len(s): s[i]"]
            ),
            
            # Key errors
            FixPattern(
                error_type="KeyError",
                error_pattern="'key'",
                fix_type="safe_dict_access",
                fix_code=".get('key', default)",
                confidence=0.9,
                description="Use safe dictionary access",
                examples=["d['key'] -> d.get('key', None)"]
            ),
            
            # Attribute errors
            FixPattern(
                error_type="AttributeError",
                error_pattern="'str' object has no attribute 'append'",
                fix_type="fix_data_type",
                fix_code="[]",
                confidence=0.8,
                description="Fix data type for method",
                examples=["s.append(1) -> s = []; s.append(1)"]
            ),
            FixPattern(
                error_type="AttributeError",
                error_pattern="'list' object has no attribute 'split'",
                fix_type="fix_data_type",
                fix_code="''",
                confidence=0.8,
                description="Fix data type for method",
                examples=["lst.split(',') -> s = ''; s.split(',')"]
            ),
            
            # Value errors
            FixPattern(
                error_type="ValueError",
                error_pattern="invalid literal for int",
                fix_type="safe_conversion",
                fix_code="try: int(x) except ValueError: 0",
                confidence=0.8,
                description="Add safe conversion with default",
                examples=["int('abc') -> try: int('abc') except ValueError: 0"]
            ),
            FixPattern(
                error_type="ValueError",
                error_pattern="could not convert string to float",
                fix_type="safe_float_conversion",
                fix_code="try: float(x) except ValueError: 0.0",
                confidence=0.8,
                description="Add safe float conversion",
                examples=["float('abc') -> try: float('abc') except ValueError: 0.0"]
            ),
            
            # File errors
            FixPattern(
                error_type="FileNotFoundError",
                error_pattern="No such file or directory",
                fix_type="create_file",
                fix_code="open(path, 'w').close()",
                confidence=0.7,
                description="Create missing file",
                examples=["open('missing.txt') -> open('missing.txt', 'w').close(); open('missing.txt')"]
            ),
            FixPattern(
                error_type="PermissionError",
                error_pattern="Permission denied",
                fix_type="fix_permissions",
                fix_code="chmod 644",
                confidence=0.6,
                description="Fix file permissions",
                examples=["open('/root/file') -> chmod 644 /root/file"]
            ),
            
            # Common typos and mistakes
            FixPattern(
                error_type="SyntaxError",
                error_pattern="invalid syntax",
                fix_type="fix_assignment_comparison",
                fix_code="==",
                confidence=0.7,
                description="Fix assignment vs comparison",
                examples=["if x = 5: -> if x == 5:"]
            ),
            FixPattern(
                error_type="NameError",
                error_pattern="name 'print' is not defined",
                fix_type="add_print_import",
                fix_code="from __future__ import print_function",
                confidence=0.9,
                description="Add print function import for Python 2 compatibility",
                examples=["print 'hello' -> from __future__ import print_function; print('hello')"]
            ),
            
            # Indentation fixes
            FixPattern(
                error_type="IndentationError",
                error_pattern="unindent does not match any outer indentation level",
                fix_type="fix_mixed_indentation",
                fix_code="    ",
                confidence=0.8,
                description="Fix mixed tabs and spaces",
                examples=["Mixed tabs and spaces -> Convert all to 4 spaces"]
            ),
            
            # Recursion fixes
            FixPattern(
                error_type="RecursionError",
                error_pattern="maximum recursion depth exceeded",
                fix_type="add_base_case",
                fix_code="if n <= 1: return 1",
                confidence=0.7,
                description="Add base case to recursive function",
                examples=["def fib(n): return fib(n-1) + fib(n-2) -> def fib(n): if n <= 1: return 1; return fib(n-1) + fib(n-2)"]
            ),
            
            # Memory optimization
            FixPattern(
                error_type="MemoryError",
                error_pattern="",
                fix_type="optimize_memory",
                fix_code="del large_var; gc.collect()",
                confidence=0.6,
                description="Optimize memory usage",
                examples=["Large data processing -> Delete unused variables and garbage collect"]
            ),
        ]
    
    def get_patterns_for_error(self, error_type: str, error_message: str) -> List[FixPattern]:
        """Get patterns that match the given error."""
        patterns = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM patterns 
                WHERE error_type = ? 
                ORDER BY confidence DESC, success_count DESC
            """, (error_type,))
            
            for row in cursor.fetchall():
                pattern = FixPattern(
                    error_type=row[1],
                    error_pattern=row[2],
                    fix_type=row[3],
                    fix_code=row[4],
                    confidence=row[5],
                    description=row[6],
                    examples=json.loads(row[7] or "[]")
                )
                
                # Check if pattern matches error message
                if self._pattern_matches(pattern, error_message):
                    patterns.append(pattern)
        
        return patterns
    
    def _pattern_matches(self, pattern: FixPattern, error_message: str) -> bool:
        """Check if a pattern matches the error message."""
        import re
        
        # Simple string matching for now
        if pattern.error_pattern in error_message:
            return True
        
        # Try regex matching
        try:
            if re.search(pattern.error_pattern, error_message):
                return True
        except re.error:
            pass
        
        return False
    
    def record_pattern_usage(self, pattern_id: int, success: bool):
        """Record usage of a pattern."""
        with sqlite3.connect(self.db_path) as conn:
            if success:
                conn.execute("""
                    UPDATE patterns 
                    SET usage_count = usage_count + 1, success_count = success_count + 1
                    WHERE id = ?
                """, (pattern_id,))
            else:
                conn.execute("""
                    UPDATE patterns 
                    SET usage_count = usage_count + 1
                    WHERE id = ?
                """, (pattern_id,))
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get statistics about pattern usage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_patterns,
                    SUM(usage_count) as total_usage,
                    SUM(success_count) as total_success,
                    AVG(confidence) as avg_confidence
                FROM patterns
            """)
            
            row = cursor.fetchone()
            if row:
                return {
                    "total_patterns": row[0],
                    "total_usage": row[1] or 0,
                    "total_success": row[2] or 0,
                    "success_rate": (row[2] or 0) / max(row[1] or 1, 1),
                    "avg_confidence": row[3] or 0
                }
        
        return {}
    
    def add_custom_pattern(self, pattern: FixPattern):
        """Add a custom pattern to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO patterns (
                    error_type, error_pattern, fix_type, fix_code,
                    confidence, description, examples
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.error_type,
                pattern.error_pattern,
                pattern.fix_type,
                pattern.fix_code,
                pattern.confidence,
                pattern.description,
                json.dumps(pattern.examples)
            ))
    
    def search_patterns(self, query: str) -> List[FixPattern]:
        """Search patterns by description or error type."""
        patterns = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM patterns 
                WHERE error_type LIKE ? OR description LIKE ? OR error_pattern LIKE ?
                ORDER BY confidence DESC
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            
            for row in cursor.fetchall():
                pattern = FixPattern(
                    error_type=row[1],
                    error_pattern=row[2],
                    fix_type=row[3],
                    fix_code=row[4],
                    confidence=row[5],
                    description=row[6],
                    examples=json.loads(row[7] or "[]")
                )
                patterns.append(pattern)
        
        return patterns
