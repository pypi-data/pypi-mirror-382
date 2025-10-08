"""Main application entry point for PDF Text Organizer."""

import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Dict

# Add parent directory to path to import vultus_serpentis
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    import tkinter.ttk as ttk  # type: ignore
    HAS_TTKBOOTSTRAP = False

from vultus_serpentis.events import EventBus
from vultus_serpentis.commands import CommandManager

from .models import PDFDataModel
from .extractor import PDFExtractor
from .events import PDFLoadedEvent, StatusMessageEvent
from .utils.config import Config
from .ui.status_bar import StatusBar
from .ui.page_view import PageView
from .ui.dialogs import SettingsDialog, AboutDialog
from .actions_manager import ActionsManager


class PDFOrganizerApp:
    """
    Main application class for PDF Text Organizer.
    
    Phase 2 implementation: UI display with notebook, treeview, and canvas.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("PDF Text Organizer v1.0")
        
        # Initialize framework components
        self.model = PDFDataModel()
        self.bus = EventBus.default()
        self.command_manager = CommandManager.default()
        self.command_manager._event_bus = self.bus
        self.config = Config()
        self.extractor = PDFExtractor(event_bus=self.bus)
        
        # Initialize actions manager
        self.actions_manager = ActionsManager(
            model=self.model,
            extractor=self.extractor,
            config=self.config,
            bus=self.bus,
            command_manager=self.command_manager
        )
        
        # Set action callbacks
        self.actions_manager.on_settings_callback = self._show_settings
        self.actions_manager.on_about_callback = self._show_about
        self.actions_manager.on_zoom_in_callback = self._zoom_in
        self.actions_manager.on_zoom_out_callback = self._zoom_out
        self.actions_manager.on_zoom_fit_callback = self._zoom_fit
        
        # Set window size from config
        width = self.config.get('ui.window_width', 1200)
        height = self.config.get('ui.window_height', 800)
        self.root.geometry(f"{width}x{height}")
        
        # Subscribe to events
        self.bus.subscribe(PDFLoadedEvent, self._on_pdf_loaded)
        self.bus.subscribe(StatusMessageEvent, self._on_status_message)
        
        # Observe model changes
        self.model.add_observer(self._on_model_changed)
        
        # Page views dictionary
        self.page_views: Dict[int, PageView] = {}
        
        # Build UI
        self._create_ui()
    
    def _create_ui(self) -> None:
        """Create the user interface."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        self._bind_action_to_menu(file_menu, 'open')
        file_menu.add_separator()
        self._bind_action_to_menu(file_menu, 'export_json')
        self._bind_action_to_menu(file_menu, 'export_csv')
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        self._bind_action_to_menu(edit_menu, 'undo')
        self._bind_action_to_menu(edit_menu, 'redo')
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        self._bind_action_to_menu(tools_menu, 'auto_group')
        self._bind_action_to_menu(tools_menu, 'group_selected')
        self._bind_action_to_menu(tools_menu, 'ungroup')
        tools_menu.add_separator()
        self._bind_action_to_menu(tools_menu, 'settings')
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        self._bind_action_to_menu(view_menu, 'zoom_in')
        self._bind_action_to_menu(view_menu, 'zoom_out')
        self._bind_action_to_menu(view_menu, 'zoom_fit')
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        self._bind_action_to_menu(help_menu, 'about')
        
        # Bind keyboard shortcuts
        self._bind_keyboard_shortcuts()
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        self._create_toolbar(main_container)
        
        # Notebook for pages
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind notebook tab change
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        
        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.set_message("Ready. Open a PDF to begin.")
    
    def _create_toolbar(self, parent: ttk.Frame) -> None:
        """Create toolbar with action buttons using grid layout for consistent sizing."""
        toolbar = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        col = 0
        
        # Open button
        open_btn = ttk.Button(
            toolbar,
            text="📂 Open",
            command=lambda: self.actions_manager.get_action('open').execute()
        )
        open_btn.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
        col += 1
        
        # Separator
        sep1 = ttk.Separator(toolbar, orient=tk.VERTICAL)
        sep1.grid(row=0, column=col, padx=5, pady=2, sticky='ns')
        col += 1
        
        # Undo button
        self.undo_btn = ttk.Button(
            toolbar,
            text="↶ Undo",
            command=lambda: self.actions_manager.get_action('undo').execute()
        )
        self.undo_btn.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
        col += 1
        
        # Redo button
        self.redo_btn = ttk.Button(
            toolbar,
            text="↷ Redo",
            command=lambda: self.actions_manager.get_action('redo').execute()
        )
        self.redo_btn.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
        col += 1
        
        # Separator
        sep2 = ttk.Separator(toolbar, orient=tk.VERTICAL)
        sep2.grid(row=0, column=col, padx=5, pady=2, sticky='ns')
        col += 1
        
        # Auto-group button
        auto_group_btn = ttk.Button(
            toolbar,
            text="🔗 Auto Group",
            command=lambda: self.actions_manager.get_action('auto_group').execute()
        )
        auto_group_btn.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
        col += 1
        
        # Group selected button
        group_btn = ttk.Button(
            toolbar,
            text="➕ Group",
            command=lambda: self.actions_manager.get_action('group_selected').execute()
        )
        group_btn.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
        col += 1
        
        # Ungroup button
        ungroup_btn = ttk.Button(
            toolbar,
            text="➖ Ungroup",
            command=lambda: self.actions_manager.get_action('ungroup').execute()
        )
        ungroup_btn.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
        col += 1
        
        # Separator
        sep3 = ttk.Separator(toolbar, orient=tk.VERTICAL)
        sep3.grid(row=0, column=col, padx=5, pady=2, sticky='ns')
        col += 1
        
        # Export button with menu
        export_btn = ttk.Menubutton(toolbar, text="💾 Export")
        export_btn.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
        
        export_menu = tk.Menu(export_btn, tearoff=0)
        export_btn.config(menu=export_menu)
        export_menu.add_command(
            label="Export to JSON...",
            command=lambda: self.actions_manager.get_action('export_json').execute()
        )
        export_menu.add_command(
            label="Export to CSV...",
            command=lambda: self.actions_manager.get_action('export_csv').execute()
        )
        
        # Configure all button columns to have equal weight
        for i in [0, 2, 3, 5, 6, 7, 9]:  # Button columns (skip separator columns)
            toolbar.columnconfigure(i, weight=1, uniform='button')
        
        # Update button states based on actions
        self._update_toolbar_buttons()
    
    def _update_toolbar_buttons(self) -> None:
        """Update toolbar button states based on action states."""
        # This will be called when action states change
        undo_action = self.actions_manager.get_action('undo')
        redo_action = self.actions_manager.get_action('redo')
        
        if undo_action:
            self.undo_btn.config(state=tk.NORMAL if undo_action.enabled else tk.DISABLED)
        if redo_action:
            self.redo_btn.config(state=tk.NORMAL if redo_action.enabled else tk.DISABLED)
    
    def _bind_action_to_menu(self, menu: tk.Menu, action_name: str) -> None:
        """
        Bind an action to a menu item.
        
        Args:
            menu: Menu to add item to
            action_name: Name of action
        """
        action = self.actions_manager.get_action(action_name)
        if action:
            menu.add_command(
                label=action.text,
                command=action.execute,
                accelerator=action.accelerator if hasattr(action, 'accelerator') else None
            )
    
    def _bind_keyboard_shortcuts(self) -> None:
        """Bind keyboard shortcuts to actions."""
        # File
        self.root.bind('<Control-o>', lambda e: self.actions_manager.get_action('open').execute())
        
        # Edit
        self.root.bind('<Control-z>', lambda e: self.actions_manager.get_action('undo').execute())
        self.root.bind('<Control-y>', lambda e: self.actions_manager.get_action('redo').execute())
        
        # Tools
        self.root.bind('<Control-g>', lambda e: self.actions_manager.get_action('auto_group').execute())
        
        # View
        self.root.bind('<Control-plus>', lambda e: self.actions_manager.get_action('zoom_in').execute())
        self.root.bind('<Control-equal>', lambda e: self.actions_manager.get_action('zoom_in').execute())
        self.root.bind('<Control-minus>', lambda e: self.actions_manager.get_action('zoom_out').execute())
        self.root.bind('<Control-0>', lambda e: self.actions_manager.get_action('zoom_fit').execute())
    
    def _show_settings(self) -> None:
        """Show settings dialog."""
        SettingsDialog(self.root, self.config)
    
    def _show_about(self) -> None:
        """Show about dialog."""
        AboutDialog(self.root)
    
    def _on_pdf_loaded(self, event: PDFLoadedEvent) -> None:
        """Handle PDF loaded event."""
        filename = os.path.basename(event.filepath)
        self.status_bar.set_message(f"Loaded: {filename} ({event.page_count} pages)")
    
    def _on_status_message(self, event: StatusMessageEvent) -> None:
        """Handle status message event - handled by StatusBar component."""
        pass  # StatusBar subscribes directly
    
    def _on_model_changed(self, **kwargs) -> None:
        """Handle model changes."""
        event = kwargs.get('event')
        
        if event == 'data_loaded':
            # Create page tabs
            self._create_page_tabs()
        
        elif event == 'data_cleared':
            # Clear all tabs
            self._clear_page_tabs()
        
        elif event == 'groups_changed':
            # Update specific page
            page_num = kwargs.get('page')
            if page_num and page_num in self.page_views:
                self._update_page_view(page_num)
    
    def _create_page_tabs(self) -> None:
        """Create tabs for each page."""
        # Clear existing tabs
        self._clear_page_tabs()
        
        # Create tab for each page
        for page_num in sorted(self.model.pages.keys()):
            page_view = PageView(self.notebook, page_num)
            self.page_views[page_num] = page_view
            
            # Add tab
            self.notebook.add(page_view, text=f"Page {page_num}")
            
            # Load words
            words = self.model.get_page_data(page_num)
            page_view.load_words(words)
    
    def _clear_page_tabs(self) -> None:
        """Clear all page tabs."""
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        self.page_views.clear()
    
    def _update_page_view(self, page_num: int) -> None:
        """Update a specific page view with groups."""
        if page_num in self.page_views:
            page_view = self.page_views[page_num]
            groups = self.model.get_page_groups(page_num)
            if groups:
                page_view.load_groups(groups)
            else:
                words = self.model.get_page_data(page_num)
                page_view.load_words(words)
    
    def _on_tab_changed(self, event) -> None:
        """Handle notebook tab change."""
        try:
            current_tab = self.notebook.index(self.notebook.select())
            # Page numbers are 1-indexed, tabs are 0-indexed
            page_num = list(sorted(self.model.pages.keys()))[current_tab]
            self.model.current_page = page_num
        except (IndexError, tk.TclError):
            pass
    
    def _zoom_in(self) -> None:
        """Zoom in current page."""
        if self.model.current_page in self.page_views:
            self.page_views[self.model.current_page].zoom_in()
    
    def _zoom_out(self) -> None:
        """Zoom out current page."""
        if self.model.current_page in self.page_views:
            self.page_views[self.model.current_page].zoom_out()
    
    def _zoom_fit(self) -> None:
        """Fit current page to window."""
        if self.model.current_page in self.page_views:
            self.page_views[self.model.current_page].zoom_fit()


def main() -> None:
    """Main application entry point."""
    # Create root window
    if HAS_TTKBOOTSTRAP:
        root = ttk.Window(themename='cosmo')
    else:
        root = tk.Tk()
    
    # Create application
    app = PDFOrganizerApp(root)
    
    # Run
    root.mainloop()


if __name__ == "__main__":
    main()
