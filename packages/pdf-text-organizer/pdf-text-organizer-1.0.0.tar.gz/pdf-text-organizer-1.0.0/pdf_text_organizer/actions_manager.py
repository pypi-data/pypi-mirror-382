"""Actions manager for centralized UI command logic."""

import sys
import os
from typing import Dict, Callable, Optional
from tkinter import filedialog, messagebox

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from vultus_serpentis.actions import Action
from vultus_serpentis.events import EventBus
from vultus_serpentis.commands import CommandManager

from .models import PDFDataModel
from .extractor import PDFExtractor
from .events import PDFLoadedEvent, StatusMessageEvent
from .utils.config import Config


class ActionsManager:
    """
    Manages all application actions with centralized state management.
    
    Actions are created once and their enabled state is managed based on
    application state (PDF loaded, items selected, etc.).
    """
    
    def __init__(
        self,
        model: PDFDataModel,
        extractor: PDFExtractor,
        config: Config,
        bus: EventBus,
        command_manager: CommandManager
    ):
        """
        Initialize actions manager.
        
        Args:
            model: Application data model
            extractor: PDF extractor
            config: Configuration manager
            bus: Event bus
            command_manager: Command manager for undo/redo
        """
        self.model = model
        self.extractor = extractor
        self.config = config
        self.bus = bus
        self.command_manager = command_manager
        
        # Callbacks (set by application)
        self.on_settings_callback: Optional[Callable[[], None]] = None
        self.on_about_callback: Optional[Callable[[], None]] = None
        self.on_zoom_in_callback: Optional[Callable[[], None]] = None
        self.on_zoom_out_callback: Optional[Callable[[], None]] = None
        self.on_zoom_fit_callback: Optional[Callable[[], None]] = None
        
        # Create all actions
        self.actions = self._create_actions()
        
        # Subscribe to events for state management
        self._setup_event_subscriptions()
        
        # Observe model for state changes
        self.model.add_observer(self._on_model_changed)
        
        # Observe command stack for undo/redo state
        self.command_manager.stack.add_observer(self._on_command_stack_changed)
    
    def _create_actions(self) -> Dict[str, Action]:
        """
        Create all application actions.
        
        Returns:
            Dictionary mapping action names to Action instances
        """
        return {
            # File menu
            'open': Action(
                text="Open PDF...",
                command=self._open_pdf,
                tooltip_text="Open a PDF file",
                accelerator="Ctrl+O"
            ),
            'export_json': Action(
                text="Export to JSON...",
                command=self._export_json,
                enabled=False,
                tooltip_text="Export grouped text to JSON"
            ),
            'export_csv': Action(
                text="Export to CSV...",
                command=self._export_csv,
                enabled=False,
                tooltip_text="Export grouped text to CSV"
            ),
            'exit': Action(
                text="Exit",
                command=self._exit_app,
                accelerator="Alt+F4"
            ),
            
            # Edit menu
            'undo': Action(
                text="Undo",
                command=self.command_manager.undo,
                enabled=False,
                accelerator="Ctrl+Z",
                tooltip_text="Undo last action"
            ),
            'redo': Action(
                text="Redo",
                command=self.command_manager.redo,
                enabled=False,
                accelerator="Ctrl+Y",
                tooltip_text="Redo last undone action"
            ),
            
            # Tools menu
            'auto_group': Action(
                text="Auto Group",
                command=self._auto_group,
                enabled=False,
                tooltip_text="Automatically group text by proximity",
                accelerator="Ctrl+G"
            ),
            'group_selected': Action(
                text="Group Selected",
                command=self._group_selected,
                enabled=False,
                tooltip_text="Group selected text items"
            ),
            'ungroup': Action(
                text="Ungroup",
                command=self._ungroup_selected,
                enabled=False,
                tooltip_text="Ungroup selected group"
            ),
            'settings': Action(
                text="Settings...",
                command=self._show_settings,
                tooltip_text="Configure grouping parameters"
            ),
            
            # View menu
            'zoom_in': Action(
                text="Zoom In",
                command=self._zoom_in,
                enabled=False,
                accelerator="Ctrl+Plus",
                tooltip_text="Zoom in canvas"
            ),
            'zoom_out': Action(
                text="Zoom Out",
                command=self._zoom_out,
                enabled=False,
                accelerator="Ctrl+Minus",
                tooltip_text="Zoom out canvas"
            ),
            'zoom_fit': Action(
                text="Fit to Window",
                command=self._zoom_fit,
                enabled=False,
                accelerator="Ctrl+0",
                tooltip_text="Fit page to window"
            ),
            
            # Help menu
            'about': Action(
                text="About",
                command=self._show_about,
                tooltip_text="About PDF Text Organizer"
            ),
        }
    
    def _setup_event_subscriptions(self) -> None:
        """Subscribe to events for action state management."""
        self.bus.subscribe(PDFLoadedEvent, self._on_pdf_loaded)
    
    def _on_pdf_loaded(self, event: PDFLoadedEvent) -> None:
        """
        Handle PDF loaded event.
        
        Args:
            event: PDF loaded event
        """
        # Enable actions that require a loaded PDF
        self.actions['export_json'].enabled = True
        self.actions['export_csv'].enabled = True
        self.actions['zoom_in'].enabled = True
        self.actions['zoom_out'].enabled = True
        self.actions['zoom_fit'].enabled = True
        self.actions['auto_group'].enabled = True
    
    def _on_model_changed(self, **kwargs) -> None:
        """
        Handle model changes.
        
        Args:
            **kwargs: Event details
        """
        event = kwargs.get('event')
        
        if event == 'data_cleared':
            # Disable actions when data is cleared
            self.actions['export_json'].enabled = False
            self.actions['export_csv'].enabled = False
            self.actions['auto_group'].enabled = False
            self.actions['zoom_in'].enabled = False
            self.actions['zoom_out'].enabled = False
            self.actions['zoom_fit'].enabled = False
        
        elif event == 'selection_changed':
            # Update selection-dependent actions
            items = kwargs.get('items', [])
            has_selection = len(items) > 0
            multiple_selected = len(items) > 1
            
            self.actions['group_selected'].enabled = multiple_selected
            self.actions['ungroup'].enabled = has_selection
    
    def _on_command_stack_changed(self, **kwargs) -> None:
        """
        Handle command stack changes.
        
        Args:
            **kwargs: Event details
        """
        self.actions['undo'].enabled = self.command_manager.can_undo()
        self.actions['redo'].enabled = self.command_manager.can_redo()
    
    # Action implementations
    
    def _open_pdf(self) -> None:
        """Open a PDF file."""
        filepath = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return
        
        self.bus.publish(StatusMessageEvent(
            message=f"Loading: {os.path.basename(filepath)}...",
            level="info"
        ))
        
        try:
            # Extract text from PDF
            pages_data = self.extractor.extract_pdf(filepath)
            
            # Load into model
            self.model.load_pdf_data(filepath, pages_data)
            
            # Add to recent files
            self.config.add_recent_file(filepath)
            
            # Publish event
            self.bus.publish(PDFLoadedEvent(
                filepath=filepath,
                page_count=len(pages_data)
            ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF:\n{str(e)}")
            self.bus.publish(StatusMessageEvent(
                message="Error loading PDF",
                level="error"
            ))
    
    def _export_json(self) -> None:
        """Export grouped text to JSON."""
        self._export_file('json')
    
    def _export_csv(self) -> None:
        """Export grouped text to CSV."""
        self._export_file('csv')
    
    def _export_file(self, format_type: str) -> None:
        """
        Export grouped text to file.
        
        Args:
            format_type: Export format ('json', 'csv', 'txt', 'md')
        """
        from tkinter import filedialog
        from .exporters import get_exporter
        
        # Check if we have data
        if not self.model.pages:
            messagebox.showwarning("No Data", "No PDF loaded to export")
            return
        
        # Check if we have groups
        if not self.model.groups:
            if not messagebox.askyesno(
                "No Groups",
                "No groups have been created. Export individual words instead?"
            ):
                return
            # Create single-word groups for export
            temp_groups = {}
            for page_num, words in self.model.pages.items():
                temp_groups[page_num] = [[w] for w in words]
        else:
            temp_groups = self.model.groups
        
        # Get file extension
        extensions = {
            'json': [("JSON Files", "*.json"), ("All Files", "*.*")],
            'csv': [("CSV Files", "*.csv"), ("All Files", "*.*")],
            'txt': [("Text Files", "*.txt"), ("All Files", "*.*")],
            'md': [("Markdown Files", "*.md"), ("All Files", "*.*")]
        }
        
        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            title=f"Export to {format_type.upper()}",
            defaultextension=f".{format_type}",
            filetypes=extensions.get(format_type, [("All Files", "*.*")])
        )
        
        if not filepath:
            return
        
        try:
            # Get exporter and export
            exporter = get_exporter(format_type)
            include_coords = self.config.get('export.include_coordinates', True)
            
            exporter.export(
                filepath,
                self.model.pages,
                temp_groups,
                include_coordinates=include_coords
            )
            
            # Success message
            messagebox.showinfo(
                "Export Successful",
                f"Exported to {filepath}"
            )
            
            self.bus.publish(StatusMessageEvent(
                message=f"Exported to {format_type.upper()}: {filepath}",
                level="info"
            ))
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")
            self.bus.publish(StatusMessageEvent(
                message="Export failed",
                level="error"
            ))
    
    def _exit_app(self) -> None:
        """Exit the application."""
        # Will be set by main app
        pass
    
    def _auto_group(self) -> None:
        """Automatically group text by proximity."""
        from .utils.geometry import auto_group_words
        from .commands import AutoGroupCommand
        
        # Get current page
        current_page = self.model.current_page
        if current_page not in self.model.pages:
            messagebox.showwarning("No Page", "No page selected")
            return
        
        # Get words for current page
        words = self.model.get_page_data(current_page)
        if not words:
            messagebox.showwarning("No Data", "No text data on current page")
            return
        
        # Get grouping parameters from config
        y_threshold = self.config.get('grouping.y_threshold', 20.0)
        dist_threshold = self.config.get('grouping.dist_threshold', 50.0)
        
        try:
            # Perform auto-grouping
            groups = auto_group_words(words, y_threshold, dist_threshold)
            
            # Create and execute command (enables undo/redo)
            command = AutoGroupCommand(self.model, current_page, groups, self.bus)
            self.command_manager.execute(command)
            
        except Exception as e:
            messagebox.showerror("Grouping Error", f"Failed to group text:\n{str(e)}")
            self.bus.publish(StatusMessageEvent(
                message="Auto-grouping failed",
                level="error"
            ))
    
    def _group_selected(self) -> None:
        """Group selected text items."""
        from .commands import ManualGroupCommand
        
        # Get current page and selection
        current_page = self.model.current_page
        selection = self.model.selection
        
        if not selection or len(selection) < 2:
            messagebox.showwarning("Selection Required", "Please select at least 2 items to group")
            return
        
        try:
            # Extract word indices from selection
            # Selection format: ['word_0', 'word_1', ...] or ['group_0_word_1', ...]
            word_indices = []
            for item in selection:
                if item.startswith('word_'):
                    idx = int(item.split('_')[1])
                    word_indices.append(idx)
            
            if len(word_indices) < 2:
                messagebox.showwarning("Invalid Selection", "Please select individual words to group")
                return
            
            # Create and execute command
            command = ManualGroupCommand(self.model, current_page, word_indices, self.bus)
            self.command_manager.execute(command)
            
        except Exception as e:
            messagebox.showerror("Grouping Error", f"Failed to group selection:\n{str(e)}")
    
    def _ungroup_selected(self) -> None:
        """Ungroup selected group."""
        from .commands import UngroupCommand, ClearGroupsCommand
        
        # Get current page and selection
        current_page = self.model.current_page
        selection = self.model.selection
        
        if not selection:
            # No selection - offer to clear all groups
            if messagebox.askyesno("Clear All Groups", 
                                   "No group selected. Clear all groups on this page?"):
                command = ClearGroupsCommand(self.model, current_page, self.bus)
                self.command_manager.execute(command)
            return
        
        try:
            # Extract group index from selection
            # Selection format: ['group_0', 'group_1', ...]
            group_indices = []
            for item in selection:
                if item.startswith('group_') and '_word_' not in item:
                    idx = int(item.split('_')[1])
                    group_indices.append(idx)
            
            if not group_indices:
                messagebox.showwarning("Invalid Selection", "Please select a group to ungroup")
                return
            
            # Ungroup first selected group
            command = UngroupCommand(self.model, current_page, group_indices[0], self.bus)
            self.command_manager.execute(command)
            
        except Exception as e:
            messagebox.showerror("Ungroup Error", f"Failed to ungroup:\n{str(e)}")
    
    def _show_settings(self) -> None:
        """Show settings dialog."""
        if self.on_settings_callback:
            self.on_settings_callback()
        else:
            messagebox.showinfo("Settings", "Settings dialog will be implemented shortly")
    
    def _zoom_in(self) -> None:
        """Zoom in current page."""
        if self.on_zoom_in_callback:
            self.on_zoom_in_callback()
    
    def _zoom_out(self) -> None:
        """Zoom out current page."""
        if self.on_zoom_out_callback:
            self.on_zoom_out_callback()
    
    def _zoom_fit(self) -> None:
        """Fit current page to window."""
        if self.on_zoom_fit_callback:
            self.on_zoom_fit_callback()
    
    def _show_about(self) -> None:
        """Show about dialog."""
        if self.on_about_callback:
            self.on_about_callback()
        else:
            messagebox.showinfo(
                "About PDF Text Organizer",
                "PDF Text Organizer v1.0\n\n"
                "A demonstration application for the Vultus Serpentis framework.\n\n"
                "Built with:\n"
                "- Tkinter/TTKBootstrap\n"
                "- pdfplumber\n"
                "- Vultus Serpentis\n\n"
                "© 2025"
            )
    
    def get_action(self, name: str) -> Optional[Action]:
        """
        Get an action by name.
        
        Args:
            name: Action name
        
        Returns:
            Action instance or None if not found
        """
        return self.actions.get(name)
