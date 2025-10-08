"""Tests for configuration management."""

import pytest
import tempfile
import os
from pathlib import Path

from pdf_text_organizer.utils.config import Config


class TestConfig:
    """Tests for Config class."""
    
    def test_initialization(self):
        """Test config initializes with defaults."""
        config = Config()
        
        assert config.get('grouping.y_threshold') == 20.0
        assert config.get('ui.theme') == 'cosmo'
        assert config.get('ui.max_recent') == 10
    
    def test_get_with_default(self):
        """Test getting value with default."""
        config = Config()
        
        value = config.get('nonexistent.key', 'default')
        
        assert value == 'default'
    
    def test_set_value(self):
        """Test setting a value."""
        config = Config()
        
        config.set('grouping.y_threshold', 25.0)
        
        assert config.get('grouping.y_threshold') == 25.0
    
    def test_set_nested_value(self):
        """Test setting nested value."""
        config = Config()
        
        config.set('new.nested.key', 'value')
        
        assert config.get('new.nested.key') == 'value'
    
    def test_add_recent_file(self):
        """Test adding recent file."""
        config = Config()
        
        config.add_recent_file('/path/to/file1.pdf')
        config.add_recent_file('/path/to/file2.pdf')
        
        recent = config.get_recent_files()
        assert len(recent) == 2
        assert recent[0] == '/path/to/file2.pdf'  # Most recent first
        assert recent[1] == '/path/to/file1.pdf'
    
    def test_add_duplicate_recent_file(self):
        """Test that duplicate recent file moves to top."""
        config = Config()
        
        config.add_recent_file('/path/to/file1.pdf')
        config.add_recent_file('/path/to/file2.pdf')
        config.add_recent_file('/path/to/file1.pdf')  # Duplicate
        
        recent = config.get_recent_files()
        assert len(recent) == 2
        assert recent[0] == '/path/to/file1.pdf'
    
    def test_max_recent_files(self):
        """Test that recent files list is limited."""
        config = Config()
        config.set('ui.max_recent', 3)
        
        for i in range(5):
            config.add_recent_file(f'/path/to/file{i}.pdf')
        
        recent = config.get_recent_files()
        assert len(recent) == 3
    
    def test_clear_recent_files(self):
        """Test clearing recent files."""
        config = Config()
        config.add_recent_file('/path/to/file.pdf')
        
        config.clear_recent_files()
        
        assert len(config.get_recent_files()) == 0
