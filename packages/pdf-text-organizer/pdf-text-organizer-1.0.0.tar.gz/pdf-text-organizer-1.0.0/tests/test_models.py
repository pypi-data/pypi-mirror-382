"""Tests for data models."""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from pdf_text_organizer.models import PDFDataModel
from vultus_serpentis.common import VultusException


class TestPDFDataModel:
    """Tests for PDFDataModel class."""
    
    def test_initialization(self):
        """Test model initializes correctly."""
        model = PDFDataModel()
        assert model.filepath == ""
        assert len(model.pages) == 0
        assert model.current_page == 1
        assert model.page_count == 0
    
    def test_load_pdf_data(self):
        """Test loading PDF data."""
        model = PDFDataModel()
        pages = {1: [{"text": "hello"}], 2: [{"text": "world"}]}
        
        model.load_pdf_data("test.pdf", pages)
        
        assert model.filepath == "test.pdf"
        assert len(model.pages) == 2
        assert model.page_count == 2
        assert model.current_page == 1
    
    def test_load_empty_data_raises(self):
        """Test that loading empty data raises exception."""
        model = PDFDataModel()
        
        with pytest.raises(VultusException):
            model.load_pdf_data("test.pdf", {})
    
    def test_notifies_on_data_load(self, observer_calls):
        """Test that model notifies observers when data loads."""
        model = PDFDataModel()
        model.add_observer(lambda **kwargs: observer_calls.append(kwargs))
        
        model.load_pdf_data("test.pdf", {1: [{"text": "test"}]})
        
        assert len(observer_calls) == 1
        assert observer_calls[0]['event'] == 'data_loaded'
        assert observer_calls[0]['page_count'] == 1
    
    def test_page_change_notifies(self, observer_calls):
        """Test that changing page notifies observers."""
        model = PDFDataModel()
        model.load_pdf_data("test.pdf", {1: [], 2: []})
        model.add_observer(lambda **kwargs: observer_calls.append(kwargs))
        
        model.current_page = 2
        
        assert len(observer_calls) == 1
        assert observer_calls[0]['event'] == 'page_changed'
        assert observer_calls[0]['page'] == 2
    
    def test_page_change_to_invalid_page_ignored(self, observer_calls):
        """Test that changing to invalid page is ignored."""
        model = PDFDataModel()
        model.load_pdf_data("test.pdf", {1: []})
        model.add_observer(lambda **kwargs: observer_calls.append(kwargs))
        
        model.current_page = 99  # Invalid page
        
        assert len(observer_calls) == 0
        assert model.current_page == 1
    
    def test_set_groups(self):
        """Test setting groups for a page."""
        model = PDFDataModel()
        model.load_pdf_data("test.pdf", {1: [{"text": "a"}, {"text": "b"}]})
        
        groups = [[{"text": "a"}], [{"text": "b"}]]
        model.set_groups(1, groups)
        
        assert model.has_groups(1)
        assert len(model.get_page_groups(1)) == 2
    
    def test_set_groups_notifies(self, observer_calls):
        """Test that setting groups notifies observers."""
        model = PDFDataModel()
        model.load_pdf_data("test.pdf", {1: []})
        model.add_observer(lambda **kwargs: observer_calls.append(kwargs))
        
        model.set_groups(1, [[{"text": "test"}]])
        
        # Should have 1 notification (data_loaded is before observer added)
        groups_events = [c for c in observer_calls if c.get('event') == 'groups_changed']
        assert len(groups_events) == 1
        assert groups_events[0]['page'] == 1
        assert groups_events[0]['group_count'] == 1
    
    def test_get_page_data(self):
        """Test getting page data."""
        model = PDFDataModel()
        words = [{"text": "hello"}, {"text": "world"}]
        model.load_pdf_data("test.pdf", {1: words})
        
        page_data = model.get_page_data(1)
        
        assert len(page_data) == 2
        assert page_data[0]['text'] == "hello"
    
    def test_get_page_data_nonexistent(self):
        """Test getting data for nonexistent page."""
        model = PDFDataModel()
        model.load_pdf_data("test.pdf", {1: []})
        
        page_data = model.get_page_data(99)
        
        assert page_data == []
    
    def test_clear(self):
        """Test clearing all data."""
        model = PDFDataModel()
        model.load_pdf_data("test.pdf", {1: [{"text": "test"}]})
        model.set_groups(1, [[{"text": "test"}]])
        
        model.clear()
        
        assert model.filepath == ""
        assert len(model.pages) == 0
        assert len(model.groups) == 0
        assert model.current_page == 1
    
    def test_clear_notifies(self, observer_calls):
        """Test that clear notifies observers."""
        model = PDFDataModel()
        model.load_pdf_data("test.pdf", {1: []})
        model.add_observer(lambda **kwargs: observer_calls.append(kwargs))
        
        model.clear()
        
        clear_events = [c for c in observer_calls if c.get('event') == 'data_cleared']
        assert len(clear_events) == 1
    
    def test_selection_property(self):
        """Test selection property."""
        model = PDFDataModel()
        
        assert model.selection == []
        
        model.selection = [1, 2, 3]
        assert model.selection == [1, 2, 3]
    
    def test_selection_notifies(self, observer_calls):
        """Test that selection change notifies observers."""
        model = PDFDataModel()
        model.add_observer(lambda **kwargs: observer_calls.append(kwargs))
        
        model.selection = [1, 2]
        
        assert len(observer_calls) == 1
        assert observer_calls[0]['event'] == 'selection_changed'
        assert observer_calls[0]['items'] == [1, 2]
