"""Dialog windows for PDF Text Organizer."""

import sys
import os
import tkinter as tk
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Main')))

try:
    import ttkbootstrap as ttk
except ImportError:
    import tkinter.ttk as ttk  # type: ignore

from vultus_serpentis.validation import ValidationBinder, default_feedback

from ..utils.config import Config
from ..validators import ThresholdValidator, PositiveFloatValidator


class SettingsDialog:
    """
    Settings dialog for configuring grouping parameters.
    
    Uses ValidationBinder to provide real-time validation feedback
    for threshold values.
    """
    
    def __init__(self, parent: tk.Widget, config: Config):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent widget
            config: Configuration manager
        """
        self.config = config
        self.result = False
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.geometry("400x300")
        
        # Create UI
        self._create_widgets()
        
        # Load current values
        self._load_values()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Grouping Settings",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Y-threshold setting
        y_frame = ttk.LabelFrame(main_frame, text="Y-Axis Threshold", padding=10)
        y_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            y_frame,
            text="Maximum vertical distance for same-line grouping (points):"
        ).pack(anchor=tk.W)
        
        self.y_threshold_var = tk.StringVar()
        y_entry = ttk.Entry(y_frame, textvariable=self.y_threshold_var, width=10)
        y_entry.pack(anchor=tk.W, pady=5)
        
        # Bind validation
        self.y_validator = ValidationBinder(
            y_entry,
            self.y_threshold_var,
            [ThresholdValidator(min_val=1, max_val=100)],
            feedback_strategy=default_feedback,
            debounce_ms=500
        )
        
        # Distance threshold setting
        dist_frame = ttk.LabelFrame(main_frame, text="Distance Threshold", padding=10)
        dist_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            dist_frame,
            text="Maximum distance for block clustering (points):"
        ).pack(anchor=tk.W)
        
        self.dist_threshold_var = tk.StringVar()
        dist_entry = ttk.Entry(dist_frame, textvariable=self.dist_threshold_var, width=10)
        dist_entry.pack(anchor=tk.W, pady=5)
        
        # Bind validation
        self.dist_validator = ValidationBinder(
            dist_entry,
            self.dist_threshold_var,
            [ThresholdValidator(min_val=1, max_val=200)],
            feedback_strategy=default_feedback,
            debounce_ms=500
        )
        
        # Theme setting
        theme_frame = ttk.LabelFrame(main_frame, text="Appearance", padding=10)
        theme_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(anchor=tk.W)
        
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=['cosmo', 'flatly', 'litera', 'minty', 'lumen', 'sandstone',
                   'yeti', 'pulse', 'united', 'morph', 'journal', 'darkly',
                   'superhero', 'solar', 'cyborg', 'vapor'],
            state='readonly',
            width=15
        )
        theme_combo.pack(anchor=tk.W, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Save",
            command=self._save,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_defaults,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _load_values(self) -> None:
        """Load current configuration values."""
        self.y_threshold_var.set(str(self.config.get('grouping.y_threshold', 20.0)))
        self.dist_threshold_var.set(str(self.config.get('grouping.dist_threshold', 50.0)))
        self.theme_var.set(self.config.get('ui.theme', 'cosmo'))
    
    def _save(self) -> None:
        """Save settings."""
        # Validate all fields
        if not self.y_validator.validate():
            tk.messagebox.showerror(
                "Validation Error",
                "Please fix the Y-threshold value",
                parent=self.dialog
            )
            return
        
        if not self.dist_validator.validate():
            tk.messagebox.showerror(
                "Validation Error",
                "Please fix the distance threshold value",
                parent=self.dialog
            )
            return
        
        # Save to config
        try:
            self.config.set('grouping.y_threshold', float(self.y_threshold_var.get()))
            self.config.set('grouping.dist_threshold', float(self.dist_threshold_var.get()))
            self.config.set('ui.theme', self.theme_var.get())
            self.config.save()
            
            self.result = True
            self.dialog.destroy()
            
            tk.messagebox.showinfo(
                "Settings Saved",
                "Settings have been saved.\n\n"
                "Note: Theme changes will take effect after restart.",
                parent=self.dialog.master
            )
        except Exception as e:
            tk.messagebox.showerror(
                "Error",
                f"Failed to save settings:\n{str(e)}",
                parent=self.dialog
            )
    
    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = False
        self.dialog.destroy()
    
    def _reset_defaults(self) -> None:
        """Reset to default values."""
        if tk.messagebox.askyesno(
            "Reset to Defaults",
            "Reset all settings to default values?",
            parent=self.dialog
        ):
            self.y_threshold_var.set("20.0")
            self.dist_threshold_var.set("50.0")
            self.theme_var.set("cosmo")


class AboutDialog:
    """About dialog showing application information."""
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize about dialog.
        
        Args:
            parent: Parent widget
        """
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About PDF Text Organizer")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set size
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        
        # Create UI
        self._create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="PDF Text Organizer",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 5))
        
        # Version
        version_label = ttk.Label(
            main_frame,
            text="Version 1.0.0",
            font=('Arial', 10)
        )
        version_label.pack(pady=(0, 20))
        
        # Description
        desc_text = (
            "A demonstration application for the Vultus Serpentis framework.\n\n"
            "Extract and organize text from PDF files using spatial grouping algorithms."
        )
        desc_label = ttk.Label(
            main_frame,
            text=desc_text,
            justify=tk.CENTER,
            wraplength=350
        )
        desc_label.pack(pady=(0, 20))
        
        # Technologies frame
        tech_frame = ttk.LabelFrame(main_frame, text="Built With", padding=10)
        tech_frame.pack(fill=tk.X, pady=10)
        
        technologies = [
            "• Vultus Serpentis Framework",
            "• Tkinter / TTKBootstrap",
            "• pdfplumber",
            "• Python 3.9+"
        ]
        
        for tech in technologies:
            ttk.Label(tech_frame, text=tech).pack(anchor=tk.W)
        
        # Copyright
        copyright_label = ttk.Label(
            main_frame,
            text="© 2025 Vultus Serpentis Team",
            font=('Arial', 9)
        )
        copyright_label.pack(pady=(20, 10))
        
        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=self.dialog.destroy,
            width=10
        ).pack()
