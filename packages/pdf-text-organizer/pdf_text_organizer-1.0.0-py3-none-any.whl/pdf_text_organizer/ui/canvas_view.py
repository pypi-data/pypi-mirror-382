"""Canvas component for visual preview of text layout."""

import sys
import os
import tkinter as tk
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Main')))

try:
    import ttkbootstrap as ttk
except ImportError:
    import tkinter.ttk as ttk  # type: ignore


class CanvasView(ttk.Frame):
    """
    Canvas for displaying visual preview of text layout.
    
    Draws bounding boxes for words and groups with scaling to fit the canvas.
    """
    
    def __init__(self, parent, page_num: int):
        """
        Initialize canvas view.
        
        Args:
            parent: Parent widget
            page_num: Page number this view represents
        """
        super().__init__(parent)
        
        self.page_num = page_num
        self.page_width = 612  # Default letter size
        self.page_height = 792
        self.scale = 1.0
        self.words: List[Dict[str, Any]] = []
        self.groups: List[List[Dict[str, Any]]] = []
        
        # Create canvas with scrollbars
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create canvas and scrollbars."""
        # Scrollbars
        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        
        # Canvas
        self.canvas = tk.Canvas(
            self,
            bg='white',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            width=600,
            height=800
        )
        
        vsb.config(command=self.canvas.yview)
        hsb.config(command=self.canvas.xview)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Bind resize event
        self.canvas.bind('<Configure>', self._on_resize)
    
    def load_words(self, words: List[Dict[str, Any]]) -> None:
        """
        Load words and draw bounding boxes.
        
        Args:
            words: List of word dictionaries with coordinates
        """
        self.words = words
        self.groups = []
        
        if words and len(words) > 0:
            # Get page dimensions from first word
            self.page_width = words[0].get('page_width', 612)
            self.page_height = words[0].get('page_height', 792)
        
        self._calculate_scale()
        self._draw()
    
    def load_groups(self, groups: List[List[Dict[str, Any]]]) -> None:
        """
        Load grouped words and draw group bounding boxes.
        
        Args:
            groups: List of groups, each containing word dictionaries
        """
        self.groups = groups
        
        # Extract all words for page dimensions
        all_words = []
        for group in groups:
            all_words.extend(group)
        
        if all_words:
            self.page_width = all_words[0].get('page_width', 612)
            self.page_height = all_words[0].get('page_height', 792)
        
        self._calculate_scale()
        self._draw()
    
    def _calculate_scale(self) -> None:
        """Calculate scale factor to fit page in canvas."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet sized
            canvas_width = 600
            canvas_height = 800
        
        # Calculate scale to fit with padding
        padding = 20
        scale_x = (canvas_width - 2 * padding) / self.page_width
        scale_y = (canvas_height - 2 * padding) / self.page_height
        
        self.scale = min(scale_x, scale_y, 1.0)  # Don't scale up
    
    def _draw(self) -> None:
        """Draw all bounding boxes on canvas."""
        # Clear canvas
        self.canvas.delete('all')
        
        # Update scroll region
        scaled_width = int(self.page_width * self.scale)
        scaled_height = int(self.page_height * self.scale)
        self.canvas.config(scrollregion=(0, 0, scaled_width, scaled_height))
        
        if self.groups:
            self._draw_groups()
        elif self.words:
            self._draw_words()
    
    def _draw_words(self) -> None:
        """Draw individual word bounding boxes."""
        for word in self.words:
            x0 = word.get('x0', 0) * self.scale
            y0 = word.get('top', 0) * self.scale
            x1 = word.get('x1', 0) * self.scale
            y1 = word.get('bottom', 0) * self.scale
            
            # Draw rectangle
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline='blue',
                width=1,
                tags='word'
            )
    
    def _draw_groups(self) -> None:
        """Draw group bounding boxes."""
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'brown']
        
        for group_idx, group in enumerate(self.groups):
            if not group:
                continue
            
            # Calculate group bounds
            x0 = min(w.get('x0', 0) for w in group) * self.scale
            y0 = min(w.get('top', 0) for w in group) * self.scale
            x1 = max(w.get('x1', 0) for w in group) * self.scale
            y1 = max(w.get('bottom', 0) for w in group) * self.scale
            
            # Draw group rectangle
            color = colors[group_idx % len(colors)]
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline=color,
                width=2,
                tags=f'group_{group_idx}'
            )
            
            # Draw label
            self.canvas.create_text(
                x0 + 5, y0 + 5,
                text=f'Group {group_idx + 1}',
                anchor='nw',
                fill=color,
                font=('Arial', 10, 'bold'),
                tags=f'group_{group_idx}_label'
            )
    
    def _on_resize(self, event) -> None:
        """Handle canvas resize."""
        self._calculate_scale()
        self._draw()
    
    def clear(self) -> None:
        """Clear canvas."""
        self.canvas.delete('all')
        self.words = []
        self.groups = []
    
    def zoom_in(self) -> None:
        """Zoom in (increase scale)."""
        self.scale *= 1.2
        self._draw()
    
    def zoom_out(self) -> None:
        """Zoom out (decrease scale)."""
        self.scale *= 0.8
        self._draw()
    
    def zoom_fit(self) -> None:
        """Fit page to canvas."""
        self._calculate_scale()
        self._draw()
