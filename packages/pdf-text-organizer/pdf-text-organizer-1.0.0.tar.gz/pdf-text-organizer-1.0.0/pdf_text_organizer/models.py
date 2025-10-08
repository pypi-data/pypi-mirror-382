"""Data models for PDF Text Organizer."""

from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path to import vultus_serpentis
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from vultus_serpentis.common import Observable, VultusException


class PDFDataModel(Observable):
    """
    Observable data model for PDF extraction results.
    
    Notifies observers when data changes, enabling reactive UI updates.
    
    Example:
        >>> model = PDFDataModel()
        >>> model.add_observer(lambda **kwargs: print(f"Event: {kwargs['event']}"))
        >>> model.load_pdf_data("test.pdf", {1: [{"text": "hello"}]})
        Event: data_loaded
    """
    
    def __init__(self):
        super().__init__()
        self.filepath: str = ""
        self.pages: Dict[int, List[Dict[str, Any]]] = {}
        self.groups: Dict[int, List[List[Dict[str, Any]]]] = {}
        self._current_page: int = 1
        self._selection: List[Any] = []
    
    @property
    def current_page(self) -> int:
        """Get current page number."""
        return self._current_page
    
    @current_page.setter
    def current_page(self, value: int) -> None:
        """Set current page and notify observers."""
        if value != self._current_page and value in self.pages:
            self._current_page = value
            self._notify_observers(event='page_changed', page=value)
    
    @property
    def selection(self) -> List[Any]:
        """Get current selection."""
        return self._selection
    
    @selection.setter
    def selection(self, value: List[Any]) -> None:
        """Set selection and notify observers."""
        self._selection = value
        self._notify_observers(event='selection_changed', items=value)
    
    @property
    def page_count(self) -> int:
        """Get total number of pages."""
        return len(self.pages)
    
    def load_pdf_data(self, filepath: str, pages: Dict[int, List[Dict[str, Any]]]) -> None:
        """
        Load extracted PDF data.
        
        Args:
            filepath: Path to the PDF file
            pages: Dictionary mapping page numbers to lists of word dictionaries
        
        Raises:
            VultusException: If pages dictionary is empty
        """
        if not pages:
            raise VultusException("No data extracted from PDF")
        self.filepath = filepath
        self.pages = pages
        self.groups = {}  # Reset groups
        self._current_page = min(pages.keys()) if pages else 1
        self._selection = []
        self._notify_observers(event='data_loaded', page_count=len(pages))
    
    def set_groups(self, page_num: int, groups: List[List[Dict[str, Any]]]) -> None:
        """
        Set groups for a specific page.
        
        Args:
            page_num: Page number
            groups: List of groups, where each group is a list of words
        """
        self.groups[page_num] = groups
        self._notify_observers(event='groups_changed', page=page_num, group_count=len(groups))
    
    def get_page_data(self, page_num: int) -> List[Dict[str, Any]]:
        """
        Get raw words for a page.
        
        Args:
            page_num: Page number
        
        Returns:
            List of word dictionaries
        """
        return self.pages.get(page_num, [])
    
    def get_page_groups(self, page_num: int) -> List[List[Dict[str, Any]]]:
        """
        Get groups for a page.
        
        Args:
            page_num: Page number
        
        Returns:
            List of groups
        """
        return self.groups.get(page_num, [])
    
    def has_groups(self, page_num: int) -> bool:
        """
        Check if a page has groups.
        
        Args:
            page_num: Page number
        
        Returns:
            True if page has groups
        """
        return page_num in self.groups and len(self.groups[page_num]) > 0
    
    def clear(self) -> None:
        """Clear all data."""
        self.filepath = ""
        self.pages = {}
        self.groups = {}
        self._current_page = 1
        self._selection = []
        self._notify_observers(event='data_cleared')
