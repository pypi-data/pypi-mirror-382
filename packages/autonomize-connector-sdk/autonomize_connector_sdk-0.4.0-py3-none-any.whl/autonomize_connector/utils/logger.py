"""
Logging utility for the Autonomize Connector SDK.
Provides consistent logging configuration across all components.
"""

import logging
import sys
import os
from typing import Optional
from .env_manager import env_manager

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to the log level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
            )
        
        return super().format(record)

def get_logger(name: str = None, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (defaults to calling module name)
        level: Log level override (defaults to environment LOG_LEVEL)
        
    Returns:
        Configured logger instance
    """
    # Use provided name or calling module name
    logger_name = name or __name__
    
    # Get or create logger
    logger = logging.getLogger(logger_name)
    
    # Don't add multiple handlers to the same logger
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = level or env_manager.log_level
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logger.level)
    
    # Create formatter
    formatter_class = ColoredFormatter if _supports_color() else logging.Formatter
    formatter = formatter_class(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def _supports_color() -> bool:
    """
    Check if the terminal supports ANSI color codes.
    
    Returns:
        True if colors are supported, False otherwise
    """
    # Check if we're in a terminal that supports colors
    return (
        hasattr(sys.stdout, 'isatty') and 
        sys.stdout.isatty() and 
        'TERM' in os.environ and
        os.environ['TERM'] != 'dumb'
    )

def configure_logging(level: str = None, format_string: str = None):
    """
    Configure global logging settings.
    
    Args:
        level: Global log level
        format_string: Custom format string for log messages
    """
    # Set root logger level
    root_logger = logging.getLogger()
    log_level = level or env_manager.log_level
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create new handler with custom format if provided
    handler = logging.StreamHandler(sys.stdout)
    if format_string:
        formatter = logging.Formatter(format_string)
    else:
        formatter_class = ColoredFormatter if _supports_color() else logging.Formatter
        formatter = formatter_class(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

# Create a default logger for the SDK
sdk_logger = get_logger('autonomize.connector') 