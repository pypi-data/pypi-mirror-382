"""Tests for ActionsManager."""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from pdf_text_organizer.actions_manager import ActionsManager
from pdf_text_organizer.models import PDFDataModel
from pdf_text_organizer.extractor import PDFExtractor
from pdf_text_organizer.utils.config import Config
from pdf_text_organizer.events import PDFLoadedEvent
from vultus_serpentis.events import EventBus
from vultus_serpentis.commands import CommandManager


class TestActionsManager:
    """Tests for ActionsManager class."""
    
    def test_initialization(self):
        """Test that ActionsManager initializes correctly."""
        model = PDFDataModel()
        extractor = Mock(spec=PDFExtractor)
        config = Config()
        bus = EventBus.default()
        cmd_manager = CommandManager.default()
        cmd_manager._event_bus = bus
        
        manager = ActionsManager(model, extractor, config, bus, cmd_manager)
        
        assert manager.model is model
        assert manager.extractor is extractor
        assert manager.config is config
        assert len(manager.actions) > 0
    
    def test_all_actions_created(self):
        """Test that all expected actions are created."""
        model = PDFDataModel()
        extractor = Mock(spec=PDFExtractor)
        config = Config()
        bus = EventBus.default()
        cmd_manager = CommandManager.default()
        cmd_manager._event_bus = bus
        
        manager = ActionsManager(model, extractor, config, bus, cmd_manager)
        
        expected_actions = [
            'open', 'export_json', 'export_csv', 'exit',
            'undo', 'redo',
            'auto_group', 'group_selected', 'ungroup', 'settings',
            'zoom_in', 'zoom_out', 'zoom_fit',
            'about'
        ]
        
        for action_name in expected_actions:
            assert action_name in manager.actions
            assert manager.actions[action_name] is not None
    
    def test_actions_initially_disabled(self):
        """Test that PDF-dependent actions are initially disabled."""
        model = PDFDataModel()
        extractor = Mock(spec=PDFExtractor)
        config = Config()
        bus = EventBus.default()
        cmd_manager = CommandManager.default()
        cmd_manager._event_bus = bus
        
        manager = ActionsManager(model, extractor, config, bus, cmd_manager)
        
        # These should be disabled initially
        assert manager.actions['export_json'].enabled is False
        assert manager.actions['export_csv'].enabled is False
        assert manager.actions['auto_group'].enabled is False
        assert manager.actions['zoom_in'].enabled is False
    
    def test_actions_enabled_on_pdf_loaded(self):
        """Test that actions are enabled when PDF is loaded."""
        model = PDFDataModel()
        extractor = Mock(spec=PDFExtractor)
        config = Config()
        bus = EventBus.default()
        cmd_manager = CommandManager.default()
        cmd_manager._event_bus = bus
        
        manager = ActionsManager(model, extractor, config, bus, cmd_manager)
        
        # Publish PDF loaded event
        bus.publish(PDFLoadedEvent(filepath="test.pdf", page_count=1))
        
        # Actions should now be enabled
        assert manager.actions['export_json'].enabled is True
        assert manager.actions['export_csv'].enabled is True
        assert manager.actions['auto_group'].enabled is True
        assert manager.actions['zoom_in'].enabled is True
    
    def test_undo_redo_state_management(self):
        """Test that undo/redo actions update with command stack."""
        model = PDFDataModel()
        extractor = Mock(spec=PDFExtractor)
        config = Config()
        bus = EventBus.default()
        cmd_manager = CommandManager.default()
        cmd_manager._event_bus = bus
        
        manager = ActionsManager(model, extractor, config, bus, cmd_manager)
        
        # Initially disabled
        assert manager.actions['undo'].enabled is False
        assert manager.actions['redo'].enabled is False
        
        # Add a mock command
        mock_cmd = Mock()
        mock_cmd.execute.return_value = True
        mock_cmd.undo.return_value = True
        
        cmd_manager.execute(mock_cmd)
        
        # Undo should now be enabled
        assert manager.actions['undo'].enabled is True
        assert manager.actions['redo'].enabled is False
    
    def test_get_action(self):
        """Test getting an action by name."""
        model = PDFDataModel()
        extractor = Mock(spec=PDFExtractor)
        config = Config()
        bus = EventBus.default()
        cmd_manager = CommandManager.default()
        cmd_manager._event_bus = bus
        
        manager = ActionsManager(model, extractor, config, bus, cmd_manager)
        
        action = manager.get_action('open')
        assert action is not None
        assert action.text == "Open PDF..."
    
    def test_get_nonexistent_action(self):
        """Test getting a nonexistent action returns None."""
        model = PDFDataModel()
        extractor = Mock(spec=PDFExtractor)
        config = Config()
        bus = EventBus.default()
        cmd_manager = CommandManager.default()
        cmd_manager._event_bus = bus
        
        manager = ActionsManager(model, extractor, config, bus, cmd_manager)
        
        action = manager.get_action('nonexistent')
        assert action is None
    
    def test_selection_dependent_actions(self):
        """Test that selection-dependent actions update correctly."""
        model = PDFDataModel()
        extractor = Mock(spec=PDFExtractor)
        config = Config()
        bus = EventBus.default()
        cmd_manager = CommandManager.default()
        cmd_manager._event_bus = bus
        
        manager = ActionsManager(model, extractor, config, bus, cmd_manager)
        
        # Initially disabled
        assert manager.actions['group_selected'].enabled is False
        assert manager.actions['ungroup'].enabled is False
        
        # Simulate selection change with multiple items
        model.selection = ['item1', 'item2']
        
        # group_selected should be enabled (multiple items)
        assert manager.actions['group_selected'].enabled is True
        assert manager.actions['ungroup'].enabled is True
        
        # Single item selection
        model.selection = ['item1']
        
        # group_selected should be disabled (need multiple)
        assert manager.actions['group_selected'].enabled is False
        assert manager.actions['ungroup'].enabled is True
