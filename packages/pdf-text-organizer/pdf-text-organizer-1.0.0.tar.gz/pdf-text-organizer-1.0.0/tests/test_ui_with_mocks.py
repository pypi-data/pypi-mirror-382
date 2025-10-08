"""Tests for UI components using Imitatio Ostendendi mocks."""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

# Add Imitatio Ostendendi to path - use the correct absolute path
# From the check script, we know the correct path
imitatio_path = r'C:\SurveyOS\SVN\sandbox\Vultus Serpentis\Code\Python\Scaffold\Test Utils\Imitatio Ostendendi\Code\Python\Code'
if os.path.exists(imitatio_path) and imitatio_path not in sys.path:
    sys.path.insert(0, imitatio_path)

# Try to import, skip tests if not available
try:
    from imitatio_ostendendi.widgets import Widget, Button, Frame, Entry
    from imitatio_ostendendi.constants import NORMAL, DISABLED
    HAS_IMITATIO = True
except ImportError as e:
    HAS_IMITATIO = False
    print(f"DEBUG: Failed to import Imitatio Ostendendi: {e}")
    print(f"DEBUG: Path exists: {os.path.exists(imitatio_path)}")
    print(f"DEBUG: Path: {imitatio_path}")
    print(f"DEBUG: sys.path: {sys.path[:5]}")
    pytestmark = pytest.mark.skip(reason=f"Imitatio Ostendendi not available: {e}")

from pdf_text_organizer.ui.status_bar import StatusBar
from pdf_text_organizer.events import StatusMessageEvent
from vultus_serpentis.events import EventBus


class TestStatusBarWithMocks:
    """Tests for StatusBar using Imitatio Ostendendi mocks."""
    
    @patch('pdf_text_organizer.ui.status_bar.ttk.Frame')
    @patch('pdf_text_organizer.ui.status_bar.ttk.Label')
    @patch('pdf_text_organizer.ui.status_bar.tk.StringVar')
    def test_initialization(self, mock_stringvar, mock_label, mock_frame):
        """Test status bar initializes correctly."""
        parent = Mock()
        mock_var = Mock()
        mock_stringvar.return_value = mock_var
        
        status_bar = StatusBar(parent)
        
        # Check that StringVar was created
        mock_stringvar.assert_called_once()
        mock_var.set.assert_called_with("Ready")
        
        # Check that label was created
        mock_label.assert_called_once()
    
    @patch('pdf_text_organizer.ui.status_bar.ttk.Frame')
    @patch('pdf_text_organizer.ui.status_bar.ttk.Label')
    @patch('pdf_text_organizer.ui.status_bar.tk.StringVar')
    def test_set_message_info(self, mock_stringvar, mock_label, mock_frame):
        """Test setting info message."""
        parent = Mock()
        mock_var = Mock()
        mock_stringvar.return_value = mock_var
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance
        
        status_bar = StatusBar(parent)
        status_bar.set_message("Test message", level="info")
        
        # Check message was set
        calls = [call for call in mock_var.set.call_args_list]
        assert any("Test message" in str(call) for call in calls)
        
        # Check color was set to black (info)
        mock_label_instance.config.assert_called()
    
    @patch('pdf_text_organizer.ui.status_bar.ttk.Frame')
    @patch('pdf_text_organizer.ui.status_bar.ttk.Label')
    @patch('pdf_text_organizer.ui.status_bar.tk.StringVar')
    def test_set_message_error(self, mock_stringvar, mock_label, mock_frame):
        """Test setting error message."""
        parent = Mock()
        mock_var = Mock()
        mock_stringvar.return_value = mock_var
        mock_label_instance = Mock()
        mock_label.return_value = mock_label_instance
        
        status_bar = StatusBar(parent)
        status_bar.set_message("Error message", level="error")
        
        # Check message was set
        calls = [call for call in mock_var.set.call_args_list]
        assert any("Error message" in str(call) for call in calls)
        
        # Check color was set to red (error)
        config_calls = mock_label_instance.config.call_args_list
        assert any('foreground' in str(call) and 'red' in str(call) for call in config_calls)
    
    @patch('pdf_text_organizer.ui.status_bar.ttk.Frame')
    @patch('pdf_text_organizer.ui.status_bar.ttk.Label')
    @patch('pdf_text_organizer.ui.status_bar.tk.StringVar')
    def test_event_subscription(self, mock_stringvar, mock_label, mock_frame):
        """Test that status bar subscribes to events."""
        parent = Mock()
        mock_var = Mock()
        mock_stringvar.return_value = mock_var
        
        bus = EventBus.default()
        status_bar = StatusBar(parent)
        
        # Publish event
        bus.publish(StatusMessageEvent(message="Event message", level="info"))
        
        # Message should be updated
        calls = [call for call in mock_var.set.call_args_list]
        assert any("Event message" in str(call) for call in calls)


class TestDialogsWithMocks:
    """Tests for dialog windows using mocks."""
    
    @patch('pdf_text_organizer.ui.dialogs.tk.Toplevel')
    @patch('pdf_text_organizer.ui.dialogs.ttk.Frame')
    @patch('pdf_text_organizer.ui.dialogs.ttk.Label')
    @patch('pdf_text_organizer.ui.dialogs.ttk.Entry')
    @patch('pdf_text_organizer.ui.dialogs.ttk.Button')
    @patch('pdf_text_organizer.ui.dialogs.ttk.LabelFrame')
    @patch('pdf_text_organizer.ui.dialogs.ttk.Combobox')
    @patch('pdf_text_organizer.ui.dialogs.tk.StringVar')
    def test_settings_dialog_creation(
        self, mock_stringvar, mock_combo, mock_labelframe,
        mock_button, mock_entry, mock_label, mock_frame, mock_toplevel
    ):
        """Test settings dialog creates all widgets."""
        from pdf_text_organizer.ui.dialogs import SettingsDialog
        from pdf_text_organizer.utils.config import Config
        
        parent = Mock()
        config = Config()
        
        # Mock Toplevel to prevent actual window creation
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.wait_window = Mock()
        
        # Mock StringVar
        mock_var = Mock()
        mock_stringvar.return_value = mock_var
        
        dialog = SettingsDialog(parent, config)
        
        # Check that Toplevel was created
        mock_toplevel.assert_called_once()
        
        # Check that widgets were created
        assert mock_frame.call_count >= 1
        assert mock_label.call_count >= 3  # Multiple labels
        assert mock_entry.call_count >= 2  # Y-threshold and distance threshold
        assert mock_button.call_count >= 3  # Save, Cancel, Reset
        assert mock_labelframe.call_count >= 3  # Three setting sections
    
    @patch('pdf_text_organizer.ui.dialogs.tk.Toplevel')
    @patch('pdf_text_organizer.ui.dialogs.ttk.Frame')
    @patch('pdf_text_organizer.ui.dialogs.ttk.Label')
    @patch('pdf_text_organizer.ui.dialogs.ttk.Button')
    def test_about_dialog_creation(
        self, mock_button, mock_label, mock_frame, mock_toplevel
    ):
        """Test about dialog creates widgets."""
        from pdf_text_organizer.ui.dialogs import AboutDialog
        
        parent = Mock()
        
        # Mock Toplevel
        mock_dialog = Mock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.wait_window = Mock()
        
        dialog = AboutDialog(parent)
        
        # Check that Toplevel was created
        mock_toplevel.assert_called_once()
        
        # Check that widgets were created
        assert mock_frame.call_count >= 1
        assert mock_label.call_count >= 5  # Title, version, description, etc.
        assert mock_button.call_count >= 1  # Close button


class TestTreeViewWithMocks:
    """Tests for TreeView using mocks."""
    
    @patch('pdf_text_organizer.ui.tree_view.ttk.Frame')
    @patch('pdf_text_organizer.ui.tree_view.ttk.Treeview')
    @patch('pdf_text_organizer.ui.tree_view.ttk.Scrollbar')
    def test_tree_view_initialization(self, mock_scrollbar, mock_treeview, mock_frame):
        """Test tree view initializes correctly."""
        from pdf_text_organizer.ui.tree_view import TextTreeView
        
        parent = Mock()
        mock_tree = Mock()
        mock_treeview.return_value = mock_tree
        
        tree_view = TextTreeView(parent, page_num=1)
        
        assert tree_view.page_num == 1
        mock_treeview.assert_called_once()
        assert mock_scrollbar.call_count == 2  # Vertical and horizontal
    
    @patch('pdf_text_organizer.ui.tree_view.ttk.Frame')
    @patch('pdf_text_organizer.ui.tree_view.ttk.Treeview')
    @patch('pdf_text_organizer.ui.tree_view.ttk.Scrollbar')
    def test_load_words(self, mock_scrollbar, mock_treeview, mock_frame):
        """Test loading words into tree."""
        from pdf_text_organizer.ui.tree_view import TextTreeView
        
        parent = Mock()
        mock_tree = Mock()
        mock_tree.get_children.return_value = []
        mock_treeview.return_value = mock_tree
        
        tree_view = TextTreeView(parent, page_num=1)
        
        words = [
            {'text': 'hello', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
            {'text': 'world', 'x0': 60, 'top': 20, 'x1': 100, 'bottom': 30}
        ]
        
        tree_view.load_words(words)
        
        # Check that items were inserted
        assert mock_tree.insert.call_count == 2
    
    @patch('pdf_text_organizer.ui.tree_view.ttk.Frame')
    @patch('pdf_text_organizer.ui.tree_view.ttk.Treeview')
    @patch('pdf_text_organizer.ui.tree_view.ttk.Scrollbar')
    def test_clear(self, mock_scrollbar, mock_treeview, mock_frame):
        """Test clearing tree."""
        from pdf_text_organizer.ui.tree_view import TextTreeView
        
        parent = Mock()
        mock_tree = Mock()
        mock_tree.get_children.return_value = ['item1', 'item2']
        mock_treeview.return_value = mock_tree
        
        tree_view = TextTreeView(parent, page_num=1)
        tree_view.clear()
        
        # Check that items were deleted
        assert mock_tree.delete.call_count == 2


class TestCanvasViewWithMocks:
    """Tests for CanvasView using mocks."""
    
    @patch('pdf_text_organizer.ui.canvas_view.ttk.Frame')
    @patch('pdf_text_organizer.ui.canvas_view.tk.Canvas')
    @patch('pdf_text_organizer.ui.canvas_view.ttk.Scrollbar')
    def test_canvas_view_initialization(self, mock_scrollbar, mock_canvas, mock_frame):
        """Test canvas view initializes correctly."""
        from pdf_text_organizer.ui.canvas_view import CanvasView
        
        parent = Mock()
        mock_canvas_instance = Mock()
        mock_canvas.return_value = mock_canvas_instance
        
        canvas_view = CanvasView(parent, page_num=1)
        
        assert canvas_view.page_num == 1
        assert canvas_view.scale == 1.0
        mock_canvas.assert_called_once()
    
    @patch('pdf_text_organizer.ui.canvas_view.ttk.Frame')
    @patch('pdf_text_organizer.ui.canvas_view.tk.Canvas')
    @patch('pdf_text_organizer.ui.canvas_view.ttk.Scrollbar')
    def test_load_words(self, mock_scrollbar, mock_canvas, mock_frame):
        """Test loading words."""
        from pdf_text_organizer.ui.canvas_view import CanvasView
        
        parent = Mock()
        mock_canvas_instance = Mock()
        mock_canvas_instance.winfo_width.return_value = 600
        mock_canvas_instance.winfo_height.return_value = 800
        mock_canvas.return_value = mock_canvas_instance
        
        canvas_view = CanvasView(parent, page_num=1)
        
        words = [
            {'text': 'test', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30,
             'page_width': 612, 'page_height': 792}
        ]
        
        canvas_view.load_words(words)
        
        assert len(canvas_view.words) == 1
        assert canvas_view.page_width == 612
    
    @patch('pdf_text_organizer.ui.canvas_view.ttk.Frame')
    @patch('pdf_text_organizer.ui.canvas_view.tk.Canvas')
    @patch('pdf_text_organizer.ui.canvas_view.ttk.Scrollbar')
    def test_zoom_in(self, mock_scrollbar, mock_canvas, mock_frame):
        """Test zoom in."""
        from pdf_text_organizer.ui.canvas_view import CanvasView
        
        parent = Mock()
        mock_canvas_instance = Mock()
        mock_canvas.return_value = mock_canvas_instance
        
        canvas_view = CanvasView(parent, page_num=1)
        initial_scale = canvas_view.scale
        
        canvas_view.zoom_in()
        
        assert canvas_view.scale > initial_scale


class TestPageViewWithMocks:
    """Tests for PageView using mocks."""
    
    @patch('pdf_text_organizer.ui.page_view.ttk.Frame')
    @patch('pdf_text_organizer.ui.page_view.ttk.PanedWindow')
    @patch('pdf_text_organizer.ui.page_view.ttk.LabelFrame')
    @patch('pdf_text_organizer.ui.page_view.TextTreeView')
    @patch('pdf_text_organizer.ui.page_view.CanvasView')
    def test_page_view_initialization(
        self, mock_canvas, mock_tree, mock_labelframe,
        mock_paned, mock_frame
    ):
        """Test page view initializes correctly."""
        from pdf_text_organizer.ui.page_view import PageView
        
        parent = Mock()
        mock_tree_instance = Mock()
        mock_canvas_instance = Mock()
        mock_tree.return_value = mock_tree_instance
        mock_canvas.return_value = mock_canvas_instance
        
        page_view = PageView(parent, page_num=1)
        
        assert page_view.page_num == 1
        mock_paned.assert_called_once()
        mock_tree.assert_called_once()
        mock_canvas.assert_called_once()
    
    @patch('pdf_text_organizer.ui.page_view.ttk.Frame')
    @patch('pdf_text_organizer.ui.page_view.ttk.PanedWindow')
    @patch('pdf_text_organizer.ui.page_view.ttk.LabelFrame')
    @patch('pdf_text_organizer.ui.page_view.TextTreeView')
    @patch('pdf_text_organizer.ui.page_view.CanvasView')
    def test_load_words(
        self, mock_canvas, mock_tree, mock_labelframe,
        mock_paned, mock_frame
    ):
        """Test loading words into both views."""
        from pdf_text_organizer.ui.page_view import PageView
        
        parent = Mock()
        mock_tree_instance = Mock()
        mock_canvas_instance = Mock()
        mock_tree.return_value = mock_tree_instance
        mock_canvas.return_value = mock_canvas_instance
        
        page_view = PageView(parent, page_num=1)
        
        words = [
            {'text': 'test', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30,
             'page_width': 612, 'page_height': 792}
        ]
        
        page_view.load_words(words)
        
        # Both views should have load_words called
        mock_tree_instance.load_words.assert_called_once_with(words)
        mock_canvas_instance.load_words.assert_called_once_with(words)
