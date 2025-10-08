"""Status bar component with message display."""

import sys
import os
import tkinter as tk

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Main')))

try:
    import ttkbootstrap as ttk
except ImportError:
    import tkinter.ttk as ttk  # type: ignore

from vultus_serpentis.events import EventBus
from ..events import StatusMessageEvent


class StatusBar(ttk.Frame):
    """
    Status bar with message display.
    
    Subscribes to StatusMessageEvent and displays messages with color coding
    based on level (info, warning, error).
    """
    
    def __init__(self, parent):
        """
        Initialize status bar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Status message
        self.message_var = tk.StringVar(value="Ready")
        self.message_label = ttk.Label(
            self,
            textvariable=self.message_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.message_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        
        # Subscribe to events
        bus = EventBus.default()
        bus.subscribe(StatusMessageEvent, self._on_status_message)
    
    def _on_status_message(self, event: StatusMessageEvent) -> None:
        """
        Update status message.
        
        Args:
            event: Status message event
        """
        self.message_var.set(event.message)
        
        # Color based on level
        if event.level == "error":
            self.message_label.config(foreground="red")
        elif event.level == "warning":
            self.message_label.config(foreground="orange")
        else:
            self.message_label.config(foreground="black")
    
    def set_message(self, message: str, level: str = "info") -> None:
        """
        Set status message directly.
        
        Args:
            message: Message text
            level: Message level (info, warning, error)
        """
        self.message_var.set(message)
        
        if level == "error":
            self.message_label.config(foreground="red")
        elif level == "warning":
            self.message_label.config(foreground="orange")
        else:
            self.message_label.config(foreground="black")
