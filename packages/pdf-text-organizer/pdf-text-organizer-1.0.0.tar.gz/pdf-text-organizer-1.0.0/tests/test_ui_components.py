"""Tests for UI components."""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from pdf_text_organizer.ui.status_bar import StatusBar
from pdf_text_organizer.ui.tree_view import TextTreeView
from pdf_text_organizer.ui.canvas_view import CanvasView
from pdf_text_organizer.ui.page_view import PageView
from pdf_text_organizer.events import StatusMessageEvent, SelectionChangedEvent
from vultus_serpentis.events import EventBus


class TestStatusBar:
    """Tests for StatusBar component."""
    
    @patch('tkinter.Tk')
    def test_initialization(self, mock_tk):
        """Test status bar initializes correctly."""
        parent = Mock()
        status_bar = StatusBar(parent)
        
        assert status_bar.message_var is not None
        assert status_bar.message_label is not None
    
    @patch('tkinter.Tk')
    def test_set_message_info(self, mock_tk):
        """Test setting info message."""
        parent = Mock()
        status_bar = StatusBar(parent)
        
        status_bar.set_message("Test message", level="info")
        
        assert status_bar.message_var.get() == "Test message"
    
    @patch('tkinter.Tk')
    def test_set_message_error(self, mock_tk):
        """Test setting error message."""
        parent = Mock()
        status_bar = StatusBar(parent)
        
        status_bar.set_message("Error message", level="error")
        
        assert status_bar.message_var.get() == "Error message"
    
    @patch('tkinter.Tk')
    def test_event_subscription(self, mock_tk):
        """Test that status bar subscribes to events."""
        parent = Mock()
        bus = EventBus.default()
        
        status_bar = StatusBar(parent)
        
        # Publish event
        bus.publish(StatusMessageEvent(message="Event message", level="info"))
        
        # Message should be updated
        assert status_bar.message_var.get() == "Event message"


class TestTextTreeView:
    """Tests for TextTreeView component."""
    
    @patch('tkinter.Tk')
    def test_initialization(self, mock_tk):
        """Test tree view initializes correctly."""
        parent = Mock()
        tree_view = TextTreeView(parent, page_num=1)
        
        assert tree_view.page_num == 1
        assert tree_view.tree is not None
    
    @patch('tkinter.Tk')
    def test_load_words(self, mock_tk):
        """Test loading words into tree."""
        parent = Mock()
        tree_view = TextTreeView(parent, page_num=1)
        
        words = [
            {'text': 'hello', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
            {'text': 'world', 'x0': 60, 'top': 20, 'x1': 100, 'bottom': 30}
        ]
        
        tree_view.load_words(words)
        
        # Check that items were added
        children = tree_view.tree.get_children()
        assert len(children) == 2
    
    @patch('tkinter.Tk')
    def test_load_groups(self, mock_tk):
        """Test loading groups into tree."""
        parent = Mock()
        tree_view = TextTreeView(parent, page_num=1)
        
        groups = [
            [
                {'text': 'hello', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
                {'text': 'world', 'x0': 60, 'top': 20, 'x1': 100, 'bottom': 30}
            ]
        ]
        
        tree_view.load_groups(groups)
        
        # Check that group was added
        children = tree_view.tree.get_children()
        assert len(children) == 1  # One group
    
    @patch('tkinter.Tk')
    def test_clear(self, mock_tk):
        """Test clearing tree."""
        parent = Mock()
        tree_view = TextTreeView(parent, page_num=1)
        
        words = [{'text': 'test', 'x0': 0, 'top': 0, 'x1': 10, 'bottom': 10}]
        tree_view.load_words(words)
        
        tree_view.clear()
        
        children = tree_view.tree.get_children()
        assert len(children) == 0
    
    @patch('tkinter.Tk')
    def test_get_selected_items(self, mock_tk):
        """Test getting selected items."""
        parent = Mock()
        tree_view = TextTreeView(parent, page_num=1)
        
        # Mock selection
        tree_view.tree.selection = Mock(return_value=['item1', 'item2'])
        
        selected = tree_view.get_selected_items()
        
        assert selected == ['item1', 'item2']


class TestCanvasView:
    """Tests for CanvasView component."""
    
    @patch('tkinter.Tk')
    def test_initialization(self, mock_tk):
        """Test canvas view initializes correctly."""
        parent = Mock()
        canvas_view = CanvasView(parent, page_num=1)
        
        assert canvas_view.page_num == 1
        assert canvas_view.canvas is not None
        assert canvas_view.scale == 1.0
    
    @patch('tkinter.Tk')
    def test_load_words(self, mock_tk):
        """Test loading words."""
        parent = Mock()
        canvas_view = CanvasView(parent, page_num=1)
        
        words = [
            {'text': 'test', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30,
             'page_width': 612, 'page_height': 792}
        ]
        
        canvas_view.load_words(words)
        
        assert len(canvas_view.words) == 1
        assert canvas_view.page_width == 612
        assert canvas_view.page_height == 792
    
    @patch('tkinter.Tk')
    def test_load_groups(self, mock_tk):
        """Test loading groups."""
        parent = Mock()
        canvas_view = CanvasView(parent, page_num=1)
        
        groups = [
            [
                {'text': 'test', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30,
                 'page_width': 612, 'page_height': 792}
            ]
        ]
        
        canvas_view.load_groups(groups)
        
        assert len(canvas_view.groups) == 1
    
    @patch('tkinter.Tk')
    def test_zoom_in(self, mock_tk):
        """Test zoom in."""
        parent = Mock()
        canvas_view = CanvasView(parent, page_num=1)
        
        initial_scale = canvas_view.scale
        canvas_view.zoom_in()
        
        assert canvas_view.scale > initial_scale
    
    @patch('tkinter.Tk')
    def test_zoom_out(self, mock_tk):
        """Test zoom out."""
        parent = Mock()
        canvas_view = CanvasView(parent, page_num=1)
        
        canvas_view.scale = 1.0
        canvas_view.zoom_out()
        
        assert canvas_view.scale < 1.0
    
    @patch('tkinter.Tk')
    def test_clear(self, mock_tk):
        """Test clearing canvas."""
        parent = Mock()
        canvas_view = CanvasView(parent, page_num=1)
        
        canvas_view.words = [{'text': 'test'}]
        canvas_view.clear()
        
        assert len(canvas_view.words) == 0


class TestPageView:
    """Tests for PageView component."""
    
    @patch('tkinter.Tk')
    def test_initialization(self, mock_tk):
        """Test page view initializes correctly."""
        parent = Mock()
        page_view = PageView(parent, page_num=1)
        
        assert page_view.page_num == 1
        assert page_view.tree_view is not None
        assert page_view.canvas_view is not None
    
    @patch('tkinter.Tk')
    def test_load_words(self, mock_tk):
        """Test loading words into both views."""
        parent = Mock()
        page_view = PageView(parent, page_num=1)
        
        words = [
            {'text': 'test', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30,
             'page_width': 612, 'page_height': 792}
        ]
        
        page_view.load_words(words)
        
        # Both views should have words
        assert len(page_view.tree_view.tree.get_children()) == 1
        assert len(page_view.canvas_view.words) == 1
    
    @patch('tkinter.Tk')
    def test_load_groups(self, mock_tk):
        """Test loading groups into both views."""
        parent = Mock()
        page_view = PageView(parent, page_num=1)
        
        groups = [
            [
                {'text': 'test', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30,
                 'page_width': 612, 'page_height': 792}
            ]
        ]
        
        page_view.load_groups(groups)
        
        # Both views should have groups
        assert len(page_view.tree_view.tree.get_children()) == 1
        assert len(page_view.canvas_view.groups) == 1
    
    @patch('tkinter.Tk')
    def test_clear(self, mock_tk):
        """Test clearing both views."""
        parent = Mock()
        page_view = PageView(parent, page_num=1)
        
        words = [{'text': 'test', 'x0': 0, 'top': 0, 'x1': 10, 'bottom': 10,
                  'page_width': 612, 'page_height': 792}]
        page_view.load_words(words)
        
        page_view.clear()
        
        assert len(page_view.tree_view.tree.get_children()) == 0
        assert len(page_view.canvas_view.words) == 0
    
    @patch('tkinter.Tk')
    def test_zoom_methods(self, mock_tk):
        """Test zoom methods delegate to canvas."""
        parent = Mock()
        page_view = PageView(parent, page_num=1)
        
        # Mock canvas zoom methods
        page_view.canvas_view.zoom_in = Mock()
        page_view.canvas_view.zoom_out = Mock()
        page_view.canvas_view.zoom_fit = Mock()
        
        page_view.zoom_in()
        page_view.zoom_out()
        page_view.zoom_fit()
        
        page_view.canvas_view.zoom_in.assert_called_once()
        page_view.canvas_view.zoom_out.assert_called_once()
        page_view.canvas_view.zoom_fit.assert_called_once()
