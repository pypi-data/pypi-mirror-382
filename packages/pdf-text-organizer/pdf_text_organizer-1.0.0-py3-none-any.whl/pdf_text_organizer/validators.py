"""Custom validators for PDF Text Organizer."""

import os
import sys
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from vultus_serpentis.validation import (
    Validator,
    ValidationResult,
    CompositeValidator,
    RangeValidator,
    RequiredValidator
)

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


class PDFPathValidator(Validator):
    """
    Validates PDF file paths.
    
    Checks that:
    - Path is not empty
    - File exists
    - File has .pdf extension
    - File can be opened as a PDF (if pdfplumber available)
    """
    
    def __call__(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate PDF file path.
        
        Args:
            value: File path to validate
            context: Optional context dictionary
        
        Returns:
            ValidationResult indicating success or failure
        """
        if not value:
            return ValidationResult(False, "Please select a PDF file")
        
        if not os.path.exists(value):
            return ValidationResult(False, "File does not exist")
        
        if not value.lower().endswith('.pdf'):
            return ValidationResult(False, "File must be a PDF (.pdf extension)")
        
        # Try to open as PDF if pdfplumber is available
        if HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(value) as pdf:
                    if len(pdf.pages) == 0:
                        return ValidationResult(False, "PDF has no pages")
            except Exception as e:
                return ValidationResult(False, f"Invalid PDF file: {str(e)}")
        
        return ValidationResult(True)


class ThresholdValidator(CompositeValidator):
    """
    Validates grouping threshold values.
    
    Combines RequiredValidator and RangeValidator to ensure
    threshold is present and within valid range.
    """
    
    def __init__(self, min_val: float = 1.0, max_val: float = 200.0):
        """
        Initialize threshold validator.
        
        Args:
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        """
        super().__init__([
            RequiredValidator("Threshold is required"),
            RangeValidator(
                min_value=min_val,
                max_value=max_val,
                message=f"Threshold must be between {min_val} and {max_val}"
            )
        ])


class PositiveIntegerValidator(Validator):
    """Validates positive integer values."""
    
    def __call__(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate positive integer.
        
        Args:
            value: Value to validate
            context: Optional context dictionary
        
        Returns:
            ValidationResult indicating success or failure
        """
        try:
            num = int(value)
            if num <= 0:
                return ValidationResult(False, "Value must be positive")
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, "Value must be an integer")


class PositiveFloatValidator(Validator):
    """Validates positive float values."""
    
    def __call__(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate positive float.
        
        Args:
            value: Value to validate
            context: Optional context dictionary
        
        Returns:
            ValidationResult indicating success or failure
        """
        try:
            num = float(value)
            if num <= 0:
                return ValidationResult(False, "Value must be positive")
            return ValidationResult(True)
        except ValueError:
            return ValidationResult(False, "Value must be a number")
