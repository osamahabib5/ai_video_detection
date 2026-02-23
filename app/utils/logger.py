"""
Logging utilities for the video detection system
"""
import logging
import logging.handlers
from pathlib import Path
from app.config.config import LOGGING_CONFIG


class Logger:
    """Custom logger class for application"""
    
    _loggers = {}
    
    @staticmethod
    def get_logger(name):
        """Get or create a logger"""
        if name in Logger._loggers:
            return Logger._loggers[name]
        
        logger = logging.getLogger(name)
        
        if not logger.handlers:
            logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
            
            # Create formatters
            formatter = logging.Formatter(LOGGING_CONFIG['format'])
            
            # File handler
            log_file = Path(LOGGING_CONFIG['log_file'])
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=LOGGING_CONFIG['max_bytes'],
                backupCount=LOGGING_CONFIG['backup_count']
            )
            file_handler.setFormatter(formatter)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        Logger._loggers[name] = logger
        return logger
