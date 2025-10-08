"""
Logging configuration for Astra MCP Server

Provides centralized logging setup with different log levels and formats.
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional

class LoggerConfig:
    """Configuration class for logging setup."""
    
    def __init__(
        self,
        name: str = "astra_mcp_server",
        level: str = "INFO",
        log_file: Optional[str] = "logs/logs.log",
        format_string: Optional[str] = None
    ):
        self.name = name
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.log_file = log_file
        self.format_string = format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
    def setup_logger(self) -> logging.Logger:
        """Set up and configure the logger."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(self.format_string)
        
        # Console handler removed - all logs go to file only
        # console_handler = logging.StreamHandler(sys.stdout)
        # console_handler.setLevel(self.level)
        # console_handler.setFormatter(formatter)
        # logger.addHandler(console_handler)
        
        # File handler (if log_file is specified)
        if self.log_file:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger

def get_logger(
    name: str = "astra_mcp_server",
    level: str = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    # Use environment variable for log level if not specified
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")
    
    # Use environment variable for log file if not specified
    if log_file is None:
        log_file = os.getenv("LOG_FILE")
    
    config = LoggerConfig(name=name, level=level, log_file=log_file)
    return config.setup_logger()

# Create default logger instance
logger = get_logger()

def log_function_call(func_name: str, args: dict = None, kwargs: dict = None):
    """Decorator helper to log function calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func_name} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed with error: {str(e)}")
                raise
        return wrapper
    return decorator
