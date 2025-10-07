"""
Tests for error capture functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unfuck.core.error_capture import ErrorCapture, ErrorContext


class TestErrorCapture:
    """Test error capture functionality."""
    
    def test_error_capture_initialization(self):
        """Test error capture initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test_errors.db")
            capture = ErrorCapture(db_path)
            assert capture.db_path == db_path
    
    def test_error_context_creation(self):
        """Test error context creation."""
        context = ErrorContext(
            error_type="ValueError",
            error_message="invalid literal for int()",
            file_path="/test/script.py",
            line_number=10,
            function_name="test_function",
            code_context=["x = int('abc')"],
            traceback="Traceback...",
            local_vars={"x": "abc"},
            global_vars={},
            python_version="3.9.0",
            platform="Linux",
            working_directory="/test",
            command_history=["python script.py"],
            timestamp="2023-01-01T00:00:00"
        )
        
        assert context.error_type == "ValueError"
        assert context.line_number == 10
        assert context.confidence == 0.0
    
    def test_database_creation(self):
        """Test database creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test_errors.db")
            capture = ErrorCapture(db_path)
            
            # Check if database file was created
            assert os.path.exists(db_path)
    
    def test_error_storage(self):
        """Test error storage in database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test_errors.db")
            capture = ErrorCapture(db_path)
            
            # Create test error context
            context = ErrorContext(
                error_type="TestError",
                error_message="Test error message",
                file_path="/test/script.py",
                line_number=5,
                function_name="test_func",
                code_context=["test code"],
                traceback="Test traceback",
                local_vars={},
                global_vars={},
                python_version="3.9.0",
                platform="Linux",
                working_directory="/test",
                command_history=[],
                timestamp="2023-01-01T00:00:00"
            )
            
            # Store error
            capture._store_error(context)
            
            # Retrieve error
            last_error = capture.get_last_error()
            assert last_error is not None
            assert last_error.error_type == "TestError"
            assert last_error.error_message == "Test error message"
    
    def test_error_history(self):
        """Test error history retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test_errors.db")
            capture = ErrorCapture(db_path)
            
            # Store multiple errors
            for i in range(3):
                context = ErrorContext(
                    error_type=f"Error{i}",
                    error_message=f"Error message {i}",
                    file_path=f"/test/script{i}.py",
                    line_number=i,
                    function_name="test_func",
                    code_context=[],
                    traceback="",
                    local_vars={},
                    global_vars={},
                    python_version="3.9.0",
                    platform="Linux",
                    working_directory="/test",
                    command_history=[],
                    timestamp=f"2023-01-01T00:00:{i:02d}"
                )
                capture._store_error(context)
            
            # Get history
            history = capture.get_error_history(5)
            assert len(history) == 3
            assert history[0].error_type == "Error2"  # Most recent first
