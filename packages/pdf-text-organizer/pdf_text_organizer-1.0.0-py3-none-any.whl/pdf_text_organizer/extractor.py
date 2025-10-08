"""PDF text extraction with coordinates."""

from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path to import vultus_serpentis
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # type: ignore

from vultus_serpentis.events import EventBus
from .events import ExtractionStartedEvent, ExtractionCompleteEvent, StatusMessageEvent


class PDFExtractor:
    """
    Handles PDF text extraction with bounding box coordinates.
    
    Uses pdfplumber to extract text with position information.
    Publishes events during extraction for UI updates.
    
    Example:
        >>> extractor = PDFExtractor()
        >>> pages = extractor.extract_pdf("document.pdf")
        >>> print(f"Extracted {len(pages)} pages")
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize the extractor.
        
        Args:
            event_bus: Optional EventBus for publishing events
        """
        if pdfplumber is None:
            raise ImportError("pdfplumber is required. Install with: pip install pdfplumber")
        
        self.bus = event_bus or EventBus.default()
    
    def extract_pdf(self, filepath: str) -> Dict[int, List[Dict[str, Any]]]:
        """
        Extract text from PDF with bounding boxes.
        
        Args:
            filepath: Path to PDF file
        
        Returns:
            Dictionary mapping page numbers to lists of word dictionaries.
            Each word dict contains: text, x0, top, x1, bottom, width, height,
            page_width, page_height
        
        Raises:
            Exception: If PDF cannot be opened or parsed
        """
        pages_data: Dict[int, List[Dict[str, Any]]] = {}
        
        self.bus.publish(StatusMessageEvent(
            message=f"Opening PDF: {os.path.basename(filepath)}",
            level="info"
        ))
        
        try:
            with pdfplumber.open(filepath) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Publish extraction started event
                    self.bus.publish(ExtractionStartedEvent(page_num=page_num))
                    self.bus.publish(StatusMessageEvent(
                        message=f"Extracting page {page_num} of {total_pages}...",
                        level="info"
                    ))
                    
                    # Extract words with coordinates
                    words = page.extract_words(
                        x_tolerance=3,
                        y_tolerance=3,
                        keep_blank_chars=False
                    )
                    
                    # Add page dimensions for scaling
                    for word in words:
                        word['page_width'] = page.width
                        word['page_height'] = page.height
                    
                    pages_data[page_num] = words
                    
                    # Publish extraction complete event
                    self.bus.publish(ExtractionCompleteEvent(
                        page_num=page_num,
                        word_count=len(words),
                        success=True
                    ))
            
            self.bus.publish(StatusMessageEvent(
                message=f"Extraction complete: {total_pages} pages, "
                        f"{sum(len(words) for words in pages_data.values())} words",
                level="info"
            ))
        
        except Exception as e:
            error_msg = f"Error extracting PDF: {str(e)}"
            self.bus.publish(ExtractionCompleteEvent(
                page_num=0,
                word_count=0,
                success=False,
                error_message=error_msg
            ))
            self.bus.publish(StatusMessageEvent(
                message=error_msg,
                level="error"
            ))
            raise
        
        return pages_data
    
    def extract_page(self, filepath: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Extract text from a single page.
        
        Args:
            filepath: Path to PDF file
            page_num: Page number (1-indexed)
        
        Returns:
            List of word dictionaries
        """
        try:
            with pdfplumber.open(filepath) as pdf:
                if 1 <= page_num <= len(pdf.pages):
                    page = pdf.pages[page_num - 1]
                    words = page.extract_words(
                        x_tolerance=3,
                        y_tolerance=3,
                        keep_blank_chars=False
                    )
                    
                    for word in words:
                        word['page_width'] = page.width
                        word['page_height'] = page.height
                    
                    return words
        except Exception as e:
            print(f"Error extracting page {page_num}: {e}")
        
        return []
    
    def get_page_count(self, filepath: str) -> int:
        """
        Get the number of pages in a PDF.
        
        Args:
            filepath: Path to PDF file
        
        Returns:
            Number of pages, or 0 if error
        """
        try:
            with pdfplumber.open(filepath) as pdf:
                return len(pdf.pages)
        except Exception:
            return 0
