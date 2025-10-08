"""Tests for custom validators."""

import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from pdf_text_organizer.validators import (
    PDFPathValidator,
    ThresholdValidator,
    PositiveIntegerValidator,
    PositiveFloatValidator
)


class TestPDFPathValidator:
    """Tests for PDFPathValidator."""
    
    def test_empty_path(self):
        """Test that empty path fails validation."""
        validator = PDFPathValidator()
        result = validator("")
        
        assert result.is_valid is False
        assert "select" in result.message.lower() and "pdf" in result.message.lower()
    
    def test_nonexistent_file(self):
        """Test that nonexistent file fails validation."""
        validator = PDFPathValidator()
        result = validator("/nonexistent/file.pdf")
        
        assert result.is_valid is False
        assert "does not exist" in result.message.lower()
    
    def test_non_pdf_extension(self):
        """Test that non-PDF file fails validation."""
        # Create a temp file with wrong extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name
        
        try:
            validator = PDFPathValidator()
            result = validator(temp_path)
            
            assert result.is_valid is False
            assert ".pdf" in result.message.lower()
        finally:
            os.unlink(temp_path)
    
    def test_valid_pdf_extension(self):
        """Test that file with .pdf extension passes basic checks."""
        # Create a temp file with .pdf extension
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name
        
        try:
            validator = PDFPathValidator()
            result = validator(temp_path)
            
            # Will fail PDF validation but pass path/extension checks
            # (unless pdfplumber is not installed)
            assert "does not exist" not in result.message.lower()
            assert ".pdf" not in result.message.lower() or "invalid pdf" in result.message.lower()
        finally:
            os.unlink(temp_path)


class TestThresholdValidator:
    """Tests for ThresholdValidator."""
    
    def test_valid_threshold(self):
        """Test that valid threshold passes."""
        validator = ThresholdValidator(min_val=1, max_val=100)
        result = validator("50")
        
        assert result.is_valid is True
    
    def test_below_minimum(self):
        """Test that value below minimum fails."""
        validator = ThresholdValidator(min_val=10, max_val=100)
        result = validator("5")
        
        assert result.is_valid is False
        assert "10" in result.message
    
    def test_above_maximum(self):
        """Test that value above maximum fails."""
        validator = ThresholdValidator(min_val=1, max_val=100)
        result = validator("150")
        
        assert result.is_valid is False
        assert "100" in result.message
    
    def test_empty_value(self):
        """Test that empty value fails."""
        validator = ThresholdValidator()
        result = validator("")
        
        assert result.is_valid is False
        assert "required" in result.message.lower()
    
    def test_non_numeric(self):
        """Test that non-numeric value fails."""
        validator = ThresholdValidator()
        result = validator("abc")
        
        assert result.is_valid is False
    
    def test_boundary_values(self):
        """Test boundary values."""
        validator = ThresholdValidator(min_val=1, max_val=100)
        
        # Minimum boundary
        assert validator("1").is_valid is True
        
        # Maximum boundary
        assert validator("100").is_valid is True
        
        # Just below minimum
        assert validator("0.9").is_valid is False
        
        # Just above maximum
        assert validator("100.1").is_valid is False


class TestPositiveIntegerValidator:
    """Tests for PositiveIntegerValidator."""
    
    def test_positive_integer(self):
        """Test that positive integer passes."""
        validator = PositiveIntegerValidator()
        result = validator("42")
        
        assert result.is_valid is True
    
    def test_zero(self):
        """Test that zero fails."""
        validator = PositiveIntegerValidator()
        result = validator("0")
        
        assert result.is_valid is False
        assert "positive" in result.message.lower()
    
    def test_negative(self):
        """Test that negative number fails."""
        validator = PositiveIntegerValidator()
        result = validator("-5")
        
        assert result.is_valid is False
        assert "positive" in result.message.lower()
    
    def test_float(self):
        """Test that float fails."""
        validator = PositiveIntegerValidator()
        result = validator("3.14")
        
        assert result.is_valid is False
        assert "integer" in result.message.lower()
    
    def test_non_numeric(self):
        """Test that non-numeric value fails."""
        validator = PositiveIntegerValidator()
        result = validator("abc")
        
        assert result.is_valid is False
        assert "integer" in result.message.lower()


class TestPositiveFloatValidator:
    """Tests for PositiveFloatValidator."""
    
    def test_positive_float(self):
        """Test that positive float passes."""
        validator = PositiveFloatValidator()
        result = validator("3.14")
        
        assert result.is_valid is True
    
    def test_positive_integer(self):
        """Test that positive integer passes."""
        validator = PositiveFloatValidator()
        result = validator("42")
        
        assert result.is_valid is True
    
    def test_zero(self):
        """Test that zero fails."""
        validator = PositiveFloatValidator()
        result = validator("0.0")
        
        assert result.is_valid is False
        assert "positive" in result.message.lower()
    
    def test_negative(self):
        """Test that negative number fails."""
        validator = PositiveFloatValidator()
        result = validator("-3.14")
        
        assert result.is_valid is False
        assert "positive" in result.message.lower()
    
    def test_non_numeric(self):
        """Test that non-numeric value fails."""
        validator = PositiveFloatValidator()
        result = validator("abc")
        
        assert result.is_valid is False
        assert "number" in result.message.lower()
