"""
Logging configuration for the fitness app.
"""
import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for the fitness app.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("fitness_app").setLevel(numeric_level)
    logging.getLogger("agents").setLevel(logging.WARNING)  # Reduce noise from agents library
    logging.getLogger("httpx").setLevel(logging.WARNING)    # Reduce HTTP noise
    logging.getLogger("gradio").setLevel(logging.INFO)      # Keep Gradio info


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
