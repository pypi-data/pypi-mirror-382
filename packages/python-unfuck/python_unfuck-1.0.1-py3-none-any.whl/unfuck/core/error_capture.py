"""
Error capture system for unfuck.
Captures Python exceptions and provides rich context for fixing.
"""

import sys
import traceback
import inspect
import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import platform


@dataclass
class ErrorContext:
    """Rich context about an error for fixing."""
    error_type: str
    error_message: str
    file_path: str
    line_number: int
    function_name: str
    code_context: List[str]  # ±5 lines around error
    traceback: str
    local_vars: Dict[str, Any]
    global_vars: Dict[str, Any]
    python_version: str
    platform: str
    working_directory: str
    command_history: List[str]
    timestamp: str
    confidence: float = 0.0


class ErrorCapture:
    """Captures and stores Python errors with rich context."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path.home() / ".unfuck" / "errors.db")
        self._setup_database()
        self._setup_exception_hook()
        
    def _setup_database(self):
        """Initialize SQLite database for error storage."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    function_name TEXT,
                    code_context TEXT,
                    traceback TEXT,
                    local_vars TEXT,
                    global_vars TEXT,
                    python_version TEXT,
                    platform TEXT,
                    working_directory TEXT,
                    command_history TEXT,
                    confidence REAL DEFAULT 0.0,
                    fixed BOOLEAN DEFAULT FALSE,
                    fix_applied TEXT
                )
            """)
            
            # Create index for fast lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_type 
                ON errors(error_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON errors(timestamp DESC)
            """)
    
    def _setup_exception_hook(self):
        """Set up global exception hook to capture errors."""
        original_excepthook = sys.excepthook
        
        def unfuck_excepthook(exc_type, exc_value, exc_traceback):
            # Capture the error
            self.capture_error(exc_type, exc_value, exc_traceback)
            # Call original hook
            original_excepthook(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = unfuck_excepthook
    
    def capture_error(self, exc_type, exc_value, exc_traceback) -> ErrorContext:
        """Capture an error with full context."""
        try:
            # Get the last frame in the traceback
            tb = exc_traceback
            while tb.tb_next:
                tb = tb.tb_next
            
            frame = tb.tb_frame
            filename = frame.f_code.co_filename
            line_number = tb.tb_lineno
            function_name = frame.f_code.co_name
            
            # Get code context (±5 lines)
            code_context = self._get_code_context(filename, line_number)
            
            # Get local and global variables (sanitized)
            local_vars = self._sanitize_vars(frame.f_locals)
            global_vars = self._sanitize_vars(frame.f_globals)
            
            # Get command history
            command_history = self._get_command_history()
            
            # Create error context
            context = ErrorContext(
                error_type=exc_type.__name__,
                error_message=str(exc_value),
                file_path=filename,
                line_number=line_number,
                function_name=function_name,
                code_context=code_context,
                traceback=traceback.format_exc(),
                local_vars=local_vars,
                global_vars=global_vars,
                python_version=platform.python_version(),
                platform=platform.platform(),
                working_directory=os.getcwd(),
                command_history=command_history,
                timestamp=datetime.now().isoformat()
            )
            
            # Store in database
            self._store_error(context)
            
            return context
            
        except Exception as e:
            # Fallback - at least capture basic info
            print(f"Warning: Could not capture full error context: {e}")
            return self._create_fallback_context(exc_type, exc_value, exc_traceback)
    
    def _get_code_context(self, filename: str, line_number: int, context_lines: int = 5) -> List[str]:
        """Get code context around the error line."""
        try:
            if not os.path.exists(filename):
                return []
            
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)
            
            return [line.rstrip() for line in lines[start:end]]
            
        except Exception:
            return []
    
    def _sanitize_vars(self, vars_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize variables for storage (remove large objects)."""
        sanitized = {}
        for key, value in vars_dict.items():
            try:
                # Skip private variables and modules
                if key.startswith('_') or inspect.ismodule(value):
                    continue
                
                # Convert to string representation, limit size
                str_value = str(value)
                if len(str_value) > 1000:
                    str_value = str_value[:1000] + "... (truncated)"
                
                sanitized[key] = str_value
            except Exception:
                sanitized[key] = "<unable to serialize>"
        
        return sanitized
    
    def _get_command_history(self) -> List[str]:
        """Get recent command history."""
        try:
            # Try to get bash history
            history_file = os.path.expanduser("~/.bash_history")
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    lines = f.readlines()
                    return [line.strip() for line in lines[-10:]]  # Last 10 commands
        except Exception:
            pass
        
        return []
    
    def _store_error(self, context: ErrorContext):
        """Store error context in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO errors (
                        timestamp, error_type, error_message, file_path, line_number,
                        function_name, code_context, traceback, local_vars, global_vars,
                        python_version, platform, working_directory, command_history
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    context.timestamp,
                    context.error_type,
                    context.error_message,
                    context.file_path,
                    context.line_number,
                    context.function_name,
                    json.dumps(context.code_context),
                    context.traceback,
                    json.dumps(context.local_vars),
                    json.dumps(context.global_vars),
                    context.python_version,
                    context.platform,
                    context.working_directory,
                    json.dumps(context.command_history)
                ))
        except Exception as e:
            print(f"Warning: Could not store error in database: {e}")
    
    def _create_fallback_context(self, exc_type, exc_value, exc_traceback) -> ErrorContext:
        """Create minimal error context when full capture fails."""
        return ErrorContext(
            error_type=exc_type.__name__,
            error_message=str(exc_value),
            file_path="<unknown>",
            line_number=0,
            function_name="<unknown>",
            code_context=[],
            traceback=traceback.format_exc(),
            local_vars={},
            global_vars={},
            python_version=platform.python_version(),
            platform=platform.platform(),
            working_directory=os.getcwd(),
            command_history=[],
            timestamp=datetime.now().isoformat()
        )
    
    def get_last_error(self) -> Optional[ErrorContext]:
        """Get the most recent error from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM errors 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """)
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_context(row)
        except Exception as e:
            print(f"Warning: Could not retrieve last error: {e}")
        
        return None
    
    def _row_to_context(self, row) -> ErrorContext:
        """Convert database row to ErrorContext."""
        return ErrorContext(
            error_type=row[2],
            error_message=row[3],
            file_path=row[4],
            line_number=row[5],
            function_name=row[6] or "<unknown>",
            code_context=json.loads(row[7] or "[]"),
            traceback=row[8] or "",
            local_vars=json.loads(row[9] or "{}"),
            global_vars=json.loads(row[10] or "{}"),
            python_version=row[11],
            platform=row[12],
            working_directory=row[13],
            command_history=json.loads(row[14] or "[]"),
            timestamp=row[1],
            confidence=row[15] or 0.0
        )
    
    def get_error_history(self, limit: int = 10) -> List[ErrorContext]:
        """Get recent error history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM errors 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                return [self._row_to_context(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Warning: Could not retrieve error history: {e}")
            return []
    
    def mark_error_fixed(self, error_id: int, fix_applied: str):
        """Mark an error as fixed with the applied fix."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE errors 
                    SET fixed = TRUE, fix_applied = ? 
                    WHERE id = ?
                """, (fix_applied, error_id))
        except Exception as e:
            print(f"Warning: Could not mark error as fixed: {e}")
