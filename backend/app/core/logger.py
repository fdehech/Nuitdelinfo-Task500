import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configure logging for the application."""
    
    # Create logger
    logger = logging.getLogger("document_vault")
    logger.setLevel(getattr(logging, settings.ENVIRONMENT == "development" and "DEBUG" or "INFO"))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to handler
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Create global logger instance
logger = setup_logging()
