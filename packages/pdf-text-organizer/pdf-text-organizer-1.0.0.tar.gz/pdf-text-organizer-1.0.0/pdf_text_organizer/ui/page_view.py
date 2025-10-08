"""Page view component with split pane (tree + canvas)."""

import sys
import os
import tkinter as tk
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Main')))

try:
    import ttkbootstrap as ttk
except ImportError:
    import tkinter.ttk as ttk  # type: ignore

from .tree_view import TextTreeView
from .canvas_view import CanvasView


class PageView(ttk.Frame):
    """
    Page view with split pane showing tree and canvas.
    
    Left side: Treeview with text/groups
    Right side: Canvas with visual preview
    """
    
    def __init__(self, parent, page_num: int):
        """
        Initialize page view.
        
        Args:
            parent: Parent widget
            page_num: Page number this view represents
        """
        super().__init__(parent)
        
        self.page_num = page_num
        
        # Create split pane
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Left: Tree view
        tree_frame = ttk.LabelFrame(self.paned, text="Text Items", padding=5)
        self.tree_view = TextTreeView(tree_frame, page_num)
        self.tree_view.pack(fill=tk.BOTH, expand=True)
        self.paned.add(tree_frame, weight=1)
        
        # Right: Canvas view
        canvas_frame = ttk.LabelFrame(self.paned, text="Visual Preview", padding=5)
        self.canvas_view = CanvasView(canvas_frame, page_num)
        self.canvas_view.pack(fill=tk.BOTH, expand=True)
        self.paned.add(canvas_frame, weight=1)
    
    def load_words(self, words: List[Dict[str, Any]]) -> None:
        """
        Load words into both tree and canvas.
        
        Args:
            words: List of word dictionaries
        """
        self.tree_view.load_words(words)
        self.canvas_view.load_words(words)
    
    def load_groups(self, groups: List[List[Dict[str, Any]]]) -> None:
        """
        Load groups into both tree and canvas.
        
        Args:
            groups: List of groups
        """
        self.tree_view.load_groups(groups)
        self.canvas_view.load_groups(groups)
    
    def clear(self) -> None:
        """Clear both tree and canvas."""
        self.tree_view.clear()
        self.canvas_view.clear()
    
    def zoom_in(self) -> None:
        """Zoom in canvas."""
        self.canvas_view.zoom_in()
    
    def zoom_out(self) -> None:
        """Zoom out canvas."""
        self.canvas_view.zoom_out()
    
    def zoom_fit(self) -> None:
        """Fit canvas to window."""
        self.canvas_view.zoom_fit()
