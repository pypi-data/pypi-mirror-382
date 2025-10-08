"""Logging utilities for CloudTools services."""
from __future__ import annotations

import logging
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union

# Default logs directory
DEFAULT_LOGS_DIR = Path("logs")

def ensure_logs_dir(custom_dir: Optional[Path] = None) -> Path:
    """Ensure logs directory exists and return its path."""
    logs_dir = custom_dir or DEFAULT_LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


@contextmanager
def temporary_log_file(
    file_path: Optional[Union[str, Path]] = None,
    level: int = logging.INFO,
    format_string: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    also_console: bool = True,
    logger_name: Optional[str] = None,
    use_logs_dir: bool = True,
) -> Generator[Path, None, None]:
    """Context manager that temporarily streams logs to a file.
    
    Args:
        file_path: Path to log file. If None, creates temporary file in logs/ dir.
        level: Logging level (default: INFO)
        format_string: Log format string
        also_console: Whether to also stream to console (default: True)
        logger_name: Specific logger name to configure (default: root logger)
        use_logs_dir: Whether to place files in logs/ directory by default (default: True)
        
    Yields:
        Path: The log file path
        
    Example:
        with temporary_log_file("debug.log") as log_file:
            logging.info("This goes to both console and logs/debug.log")
            # ... your code here ...
        # Log file streaming automatically stops here
    """
    # Determine log file path
    if file_path is None:
        # Create temporary file in logs directory
        logs_dir = ensure_logs_dir() if use_logs_dir else Path(".")
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.log', prefix='cloudtools_', 
            dir=logs_dir, delete=False
        )
        log_path = Path(temp_file.name)
        temp_file.close()
    else:
        log_path = Path(file_path)
        if use_logs_dir and not log_path.is_absolute():
            # Place relative paths in logs directory
            logs_dir = ensure_logs_dir()
            log_path = logs_dir / log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get logger
    logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
    
    # Store original handlers and level
    original_handlers = logger.handlers.copy()
    original_level = logger.level
    
    # Create file handler
    file_handler = logging.FileHandler(log_path, mode="w")
    file_handler.setFormatter(logging.Formatter(format_string))
    
    # Create console handler if requested
    console_handler = None
    if also_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(format_string))
    
    try:
        # Configure logger
        logger.setLevel(level)
        logger.addHandler(file_handler)
        if console_handler:
            logger.addHandler(console_handler)
            
        print(f"📄 Streaming logs to: {log_path}")
        yield log_path
        
    finally:
        # Restore original configuration
        logger.handlers = original_handlers
        logger.setLevel(original_level)
        
        # Close handlers
        file_handler.close()
        if console_handler:
            console_handler.close()
            
        print(f"📄 Log streaming stopped. File: {log_path}")


@contextmanager 
def capture_service_logs(
    service_name: str,
    file_path: Optional[Union[str, Path]] = None,
    level: int = logging.DEBUG,
    use_logs_dir: bool = True,
) -> Generator[Path, None, None]:
    """Context manager specifically for capturing CloudTools service logs.
    
    Args:
        service_name: Name of the service (used in filename if file_path is None)
        file_path: Path to log file. If None, creates file in logs/ dir based on service name.
        level: Logging level (default: DEBUG for detailed service logs)
        use_logs_dir: Whether to place files in logs/ directory by default (default: True)
        
    Example:
        with capture_service_logs("hello") as log_file:
            service = CloudService("hello")
            # ... run your service ...
        # Service logs are now in logs/hello_service.log
    """
    if file_path is None:
        file_path = f"{service_name}_service.log"
    
    # Capture logs from both the service and cloudtools modules
    cloudtools_logger = logging.getLogger("cloudtools")
    
    with temporary_log_file(
        file_path=file_path,
        level=level,
        logger_name="cloudtools",
        format_string=f"%(asctime)s [{service_name}] [%(levelname)s] %(name)s: %(message)s",
        use_logs_dir=use_logs_dir
    ) as log_path:
        yield log_path


def tail_log_file(file_path: Union[str, Path], lines: int = 20) -> None:
    """Print the last N lines of a log file (like tail -n)."""
    log_path = Path(file_path)
    if not log_path.exists():
        print(f"❌ Log file not found: {log_path}")
        return
        
    with open(log_path, 'r') as f:
        all_lines = f.readlines()
        tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
    print(f"📄 Last {len(tail_lines)} lines from {log_path}:")
    print("=" * 50)
    for line in tail_lines:
        print(line.rstrip())
    print("=" * 50)


def stream_log_file_live(file_path: Union[str, Path]) -> None:
    """Stream a log file live (like tail -f). Press Ctrl+C to stop."""
    import time
    
    log_path = Path(file_path)
    if not log_path.exists():
        print(f"❌ Log file not found: {log_path}")
        return
    
    print(f"📄 Live streaming: {log_path} (Press Ctrl+C to stop)")
    print("=" * 50)
    
    try:
        with open(log_path, 'r') as f:
            # Go to end of file
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    print(line.rstrip())
                else:
                    time.sleep(0.1)  # Short sleep to avoid busy waiting
    except KeyboardInterrupt:
        print("\n📄 Live streaming stopped.")
