import configparser
import os
from pathlib import Path

class ConfigManager:
    """Centralized configuration management for the AI agent."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one config instance."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = configparser.ConfigParser()
        self.config_path = 'config.ini'
        self._load_config()
        self._create_directories()
        self._initialized = True
    
    def _load_config(self):
        """Load configuration from config.ini file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file '{self.config_path}' not found!")
        
        self.config.read(self.config_path)
        print(f"✅ Configuration loaded from {self.config_path}")
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.get('Paths', 'data_directory', './agent_data'),
            self.get('Paths', 'logs_directory', './logs')
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get(self, section, key, fallback=None):
        """Get a configuration value with optional fallback."""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getint(self, section, key, fallback=None):
        """Get an integer configuration value."""
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getfloat(self, section, key, fallback=None):
        """Get a float configuration value."""
        try:
            return self.config.getfloat(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getboolean(self, section, key, fallback=None):
        """Get a boolean configuration value."""
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()
        print("✅ Configuration reloaded")

# Global config instance
config = ConfigManager()