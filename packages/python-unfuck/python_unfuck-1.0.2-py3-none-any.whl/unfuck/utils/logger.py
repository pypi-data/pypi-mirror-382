"""
Logging system for unfuck.
"""

import logging
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


class UnfuckLogger:
    """Logger for unfuck operations."""
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file or str(Path.home() / ".unfuck" / "unfuck.log")
        
        # Create log directory
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger("unfuck")
        self.logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)
    
    def log_error_capture(self, error_context: dict):
        """Log error capture event."""
        self.info(f"Error captured: {error_context.get('error_type')} - {error_context.get('error_message')}")
    
    def log_fix_attempt(self, fix_description: str, confidence: float):
        """Log fix attempt."""
        self.info(f"Fix attempt: {fix_description} (confidence: {confidence:.2f})")
    
    def log_fix_success(self, fix_description: str, changes: list):
        """Log successful fix."""
        self.info(f"Fix successful: {fix_description}")
        for change in changes:
            self.debug(f"  - {change}")
    
    def log_fix_failure(self, fix_description: str, error: str):
        """Log failed fix."""
        self.warning(f"Fix failed: {fix_description} - {error}")
    
    def log_ai_usage(self, model: str, success: bool):
        """Log AI usage."""
        status = "success" if success else "failure"
        self.info(f"AI usage ({model}): {status}")
    
    def log_performance(self, operation: str, duration: float):
        """Log performance metrics."""
        self.debug(f"Performance: {operation} took {duration:.3f}s")
    
    def get_log_stats(self) -> dict:
        """Get logging statistics."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                
                stats = {
                    "total_lines": len(lines),
                    "file_size": os.path.getsize(self.log_file),
                    "last_modified": datetime.fromtimestamp(os.path.getmtime(self.log_file)).isoformat()
                }
                
                # Count log levels
                level_counts = {}
                for line in lines:
                    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                        if f" - {level} - " in line:
                            level_counts[level] = level_counts.get(level, 0) + 1
                
                stats["level_counts"] = level_counts
                return stats
        except Exception:
            pass
        
        return {"error": "Could not read log file"}
    
    def clear_logs(self):
        """Clear log file."""
        try:
            with open(self.log_file, 'w') as f:
                f.write("")
            self.info("Log file cleared")
        except Exception as e:
            self.error(f"Could not clear log file: {e}")
    
    def set_level(self, level: str):
        """Set logging level."""
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(self.log_level)
        
        for handler in self.logger.handlers:
            handler.setLevel(self.log_level)
