"""Application configuration management."""

import json
import os
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """
    Application configuration manager.
    
    Stores user preferences in a JSON file in the user's home directory.
    Provides get/set methods with dot-notation for nested keys.
    
    Example:
        >>> config = Config()
        >>> config.set('grouping.y_threshold', 25.0)
        >>> threshold = config.get('grouping.y_threshold')
        >>> print(threshold)
        25.0
    """
    
    DEFAULT_CONFIG = {
        'grouping': {
            'y_threshold': 20.0,
            'dist_threshold': 50.0,
        },
        'ui': {
            'theme': 'cosmo',  # TTKBootstrap theme
            'recent_files': [],
            'max_recent': 10,
            'window_width': 1200,
            'window_height': 800,
        },
        'export': {
            'default_format': 'json',
            'include_coordinates': True,
        }
    }
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / '.pdf_text_organizer'
        self.config_file = self.config_dir / 'config.json'
        self.config: Dict[str, Any] = self._deep_copy(self.DEFAULT_CONFIG)
        self.load()
    
    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy a dictionary."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        return obj
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self._merge_config(loaded)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _merge_config(self, loaded: Dict[str, Any]) -> None:
        """Merge loaded config with defaults."""
        for key, value in loaded.items():
            if key in self.config:
                if isinstance(value, dict) and isinstance(self.config[key], dict):
                    self.config[key].update(value)
                else:
                    self.config[key] = value
            else:
                self.config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., 'grouping.y_threshold')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., 'grouping.y_threshold')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def add_recent_file(self, filepath: str) -> None:
        """
        Add file to recent files list.
        
        Args:
            filepath: Path to add to recent files
        """
        recent: List[str] = self.config['ui']['recent_files']
        if filepath in recent:
            recent.remove(filepath)
        recent.insert(0, filepath)
        
        max_recent: int = self.config['ui']['max_recent']
        self.config['ui']['recent_files'] = recent[:max_recent]
        self.save()
    
    def get_recent_files(self) -> List[str]:
        """
        Get list of recent files.
        
        Returns:
            List of recent file paths
        """
        return self.config['ui']['recent_files']
    
    def clear_recent_files(self) -> None:
        """Clear recent files list."""
        self.config['ui']['recent_files'] = []
        self.save()
