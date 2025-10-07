"""
Helper functions for unfuck.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


def get_python_version() -> str:
    """Get Python version string."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_platform_info() -> Dict[str, str]:
    """Get platform information."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": get_python_version(),
        "python_executable": sys.executable
    }


def is_python_file(file_path: str) -> bool:
    """Check if file is a Python file."""
    return file_path.endswith(('.py', '.pyw', '.pyc', '.pyo'))


def get_file_encoding(file_path: str) -> str:
    """Detect file encoding."""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # Try common encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                raw_data.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'  # Default fallback
    except Exception:
        return 'utf-8'


def safe_read_file(file_path: str) -> Optional[str]:
    """Safely read file with encoding detection."""
    try:
        encoding = get_file_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception:
        return None


def safe_write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """Safely write file."""
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False


def run_command(command: List[str], timeout: int = 30) -> Tuple[int, str, str]:
    """Run command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def is_git_repo(path: str) -> bool:
    """Check if path is a git repository."""
    return os.path.exists(os.path.join(path, '.git'))


def get_git_info(path: str) -> Dict[str, str]:
    """Get git repository information."""
    if not is_git_repo(path):
        return {}
    
    info = {}
    
    # Get current branch
    exit_code, stdout, _ = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=path)
    if exit_code == 0:
        info['branch'] = stdout.strip()
    
    # Get last commit
    exit_code, stdout, _ = run_command(['git', 'log', '-1', '--oneline'], cwd=path)
    if exit_code == 0:
        info['last_commit'] = stdout.strip()
    
    # Get remote URL
    exit_code, stdout, _ = run_command(['git', 'remote', 'get-url', 'origin'], cwd=path)
    if exit_code == 0:
        info['remote_url'] = stdout.strip()
    
    return info


def find_python_files(directory: str, recursive: bool = True) -> List[str]:
    """Find Python files in directory."""
    python_files = []
    
    try:
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if is_python_file(file):
                        python_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                if is_python_file(file):
                    python_files.append(os.path.join(directory, file))
    except Exception:
        pass
    
    return python_files


def get_file_stats(file_path: str) -> Dict[str, Any]:
    """Get file statistics."""
    try:
        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "is_file": os.path.isfile(file_path),
            "is_dir": os.path.isdir(file_path),
            "readable": os.access(file_path, os.R_OK),
            "writable": os.access(file_path, os.W_OK),
            "executable": os.access(file_path, os.X_OK)
        }
    except Exception:
        return {}


def create_backup_name(original_path: str) -> str:
    """Create backup filename."""
    path = Path(original_path)
    timestamp = int(time.time())
    return f"{path.stem}_{timestamp}.unfuck_backup{path.suffix}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    
    return filename


def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in human readable string."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-len(suffix)] + suffix


def extract_error_info(traceback_text: str) -> Dict[str, Any]:
    """Extract error information from traceback."""
    lines = traceback_text.split('\n')
    error_info = {
        "error_type": "Unknown",
        "error_message": "No message",
        "file_path": "Unknown",
        "line_number": 0,
        "function_name": "Unknown"
    }
    
    # Find the last exception line
    for line in lines:
        if 'Traceback (most recent call last):' in line:
            continue
        elif 'File "' in line and '", line ' in line:
            # Extract file and line info
            try:
                parts = line.split('", line ')
                if len(parts) == 2:
                    file_part = parts[0].split('File "')[1]
                    line_part = parts[1].split(',')[0]
                    error_info["file_path"] = file_part
                    error_info["line_number"] = int(line_part)
            except (ValueError, IndexError):
                pass
        elif 'in ' in line and ('def ' in line or 'class ' in line):
            # Extract function/class name
            try:
                func_part = line.split('in ')[1].strip()
                error_info["function_name"] = func_part
            except IndexError:
                pass
        elif ':' in line and not line.startswith(' '):
            # This is likely the error line
            try:
                error_type, error_message = line.split(':', 1)
                error_info["error_type"] = error_type.strip()
                error_info["error_message"] = error_message.strip()
            except ValueError:
                pass
    
    return error_info


def is_virtual_environment() -> bool:
    """Check if running in a virtual environment."""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        os.environ.get('VIRTUAL_ENV') is not None
    )


def get_virtual_env_info() -> Dict[str, str]:
    """Get virtual environment information."""
    info = {}
    
    if hasattr(sys, 'real_prefix'):
        info['type'] = 'virtualenv'
        info['path'] = sys.prefix
    elif hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        info['type'] = 'venv'
        info['path'] = sys.prefix
    elif os.environ.get('VIRTUAL_ENV'):
        info['type'] = 'virtualenv'
        info['path'] = os.environ['VIRTUAL_ENV']
    
    return info


# Import time for backup naming
import time
