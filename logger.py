# logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime
from config_manager import config

class AgentLogger:
    """Centralized logging system for the AI agent."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.logger = logging.getLogger('AIAgent')
        self._setup_logger()
        self._initialized = True
    
    def _setup_logger(self):
        """Configure the logger with file and console handlers."""
        log_level = config.get('Logging', 'log_level', 'INFO')
        self.logger.setLevel(getattr(logging, log_level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with color support
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler if enabled
        if config.getboolean('Logging', 'log_to_file', True):
            logs_dir = Path(config.get('Paths', 'logs_directory', './logs'))
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = logs_dir / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def info(self, message):
        """Log info level message."""
        self.logger.info(message)
    
    def debug(self, message):
        """Log debug level message."""
        self.logger.debug(message)
    
    def warning(self, message):
        """Log warning level message."""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error level message."""
        self.logger.error(message)
    
    def critical(self, message):
        """Log critical level message."""
        self.logger.critical(message)
    
    def log_conversation(self, user_input, agent_response, tools_used=None):
        """Log conversation exchanges with optional tool usage."""
        if config.getboolean('Logging', 'log_conversations', True):
            log_entry = f"\n{'='*60}\nUSER: {user_input}\n"
            if tools_used:
                log_entry += f"TOOLS: {tools_used}\n"
            log_entry += f"AGENT: {agent_response}\n{'='*60}"
            self.logger.info(log_entry)

# Global logger instance
logger = AgentLogger()