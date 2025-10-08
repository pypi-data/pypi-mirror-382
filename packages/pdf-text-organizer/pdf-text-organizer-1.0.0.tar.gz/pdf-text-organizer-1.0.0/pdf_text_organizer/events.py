"""Custom event definitions for PDF Text Organizer."""

from dataclasses import dataclass
from typing import List, Any
import sys
import os

# Add parent directory to path to import vultus_serpentis
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from vultus_serpentis.events import Event


@dataclass
class PDFLoadedEvent(Event):
    """Published when PDF file is loaded."""

    filepath: str
    page_count: int


@dataclass
class ExtractionStartedEvent(Event):
    """Published when text extraction starts."""

    page_num: int


@dataclass
class ExtractionCompleteEvent(Event):
    """Published when text extraction completes."""

    page_num: int
    word_count: int
    success: bool
    error_message: str = ""


@dataclass
class GroupingStartedEvent(Event):
    """Published when grouping starts."""

    page_num: int


@dataclass
class GroupingCompleteEvent(Event):
    """Published when grouping completes."""

    page_num: int
    group_count: int
    success: bool


@dataclass
class SelectionChangedEvent(Event):
    """Published when user selects different items."""

    page_num: int
    selected_items: List[Any]


@dataclass
class StatusMessageEvent(Event):
    """Published to update status bar."""

    message: str
    level: str = "info"  # info, warning, error


@dataclass
class ProgressEvent(Event):
    """Published to update progress bar."""

    current: int
    total: int
    message: str = ""
