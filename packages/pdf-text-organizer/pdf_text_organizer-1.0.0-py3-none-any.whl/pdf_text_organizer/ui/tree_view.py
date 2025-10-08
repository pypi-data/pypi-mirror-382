"""Treeview component for displaying extracted text."""

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

from vultus_serpentis.events import EventBus
from ..events import SelectionChangedEvent


class TextTreeView(ttk.Frame):
    """
    Treeview for displaying extracted text and groups.
    
    Shows a hierarchical view of:
    - Groups (if available)
    - Individual words with coordinates
    """
    
    def __init__(self, parent, page_num: int):
        """
        Initialize tree view.
        
        Args:
            parent: Parent widget
            page_num: Page number this view represents
        """
        super().__init__(parent)
        
        self.page_num = page_num
        self.bus = EventBus.default()
        
        # Create treeview with scrollbars
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create treeview and scrollbars."""
        # Scrollbars
        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        
        # Treeview
        self.tree = ttk.Treeview(
            self,
            columns=('text', 'x', 'y', 'width', 'height'),
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode='extended'
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Column headers
        self.tree.heading('#0', text='Item')
        self.tree.heading('text', text='Text')
        self.tree.heading('x', text='X')
        self.tree.heading('y', text='Y')
        self.tree.heading('width', text='Width')
        self.tree.heading('height', text='Height')
        
        # Column widths
        self.tree.column('#0', width=100)
        self.tree.column('text', width=300)
        self.tree.column('x', width=60)
        self.tree.column('y', width=60)
        self.tree.column('width', width=60)
        self.tree.column('height', width=60)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_changed)
    
    def load_words(self, words: List[Dict[str, Any]]) -> None:
        """
        Load words into treeview.
        
        Args:
            words: List of word dictionaries with text and coordinates
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add words
        for i, word in enumerate(words):
            text = word.get('text', '')
            x = f"{word.get('x0', 0):.1f}"
            y = f"{word.get('top', 0):.1f}"
            width = f"{word.get('x1', 0) - word.get('x0', 0):.1f}"
            height = f"{word.get('bottom', 0) - word.get('top', 0):.1f}"
            
            self.tree.insert(
                '',
                'end',
                iid=f'word_{i}',
                text=f'Word {i+1}',
                values=(text, x, y, width, height)
            )
    
    def load_groups(self, groups: List[List[Dict[str, Any]]]) -> None:
        """
        Load grouped words into treeview.
        
        Args:
            groups: List of groups, each containing word dictionaries
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add groups
        for group_idx, group in enumerate(groups):
            # Calculate group bounds
            if not group:
                continue
            
            x0 = min(w.get('x0', 0) for w in group)
            y0 = min(w.get('top', 0) for w in group)
            x1 = max(w.get('x1', 0) for w in group)
            y1 = max(w.get('bottom', 0) for w in group)
            
            # Group text (first few words)
            group_text = ' '.join(w.get('text', '') for w in group[:5])
            if len(group) > 5:
                group_text += '...'
            
            # Insert group
            group_id = f'group_{group_idx}'
            self.tree.insert(
                '',
                'end',
                iid=group_id,
                text=f'Group {group_idx + 1} ({len(group)} words)',
                values=(group_text, f'{x0:.1f}', f'{y0:.1f}', 
                       f'{x1-x0:.1f}', f'{y1-y0:.1f}')
            )
            
            # Add words in group
            for word_idx, word in enumerate(group):
                text = word.get('text', '')
                x = f"{word.get('x0', 0):.1f}"
                y = f"{word.get('top', 0):.1f}"
                width = f"{word.get('x1', 0) - word.get('x0', 0):.1f}"
                height = f"{word.get('bottom', 0) - word.get('top', 0):.1f}"
                
                self.tree.insert(
                    group_id,
                    'end',
                    iid=f'{group_id}_word_{word_idx}',
                    text=f'  Word {word_idx + 1}',
                    values=(text, x, y, width, height)
                )
    
    def _on_selection_changed(self, event) -> None:
        """Handle selection change."""
        selected = self.tree.selection()
        
        # Publish selection changed event
        self.bus.publish(SelectionChangedEvent(
            page_num=self.page_num,
            selected_items=list(selected)
        ))
    
    def get_selected_items(self) -> List[str]:
        """
        Get selected item IDs.
        
        Returns:
            List of selected item IDs
        """
        return list(self.tree.selection())
    
    def clear(self) -> None:
        """Clear all items from tree."""
        for item in self.tree.get_children():
            self.tree.delete(item)
