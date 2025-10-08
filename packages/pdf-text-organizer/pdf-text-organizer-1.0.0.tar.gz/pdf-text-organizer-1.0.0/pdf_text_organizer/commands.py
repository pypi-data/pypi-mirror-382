"""Command implementations for undoable operations."""

import sys
import os
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from vultus_serpentis.commands import Command
from vultus_serpentis.events import EventBus

from .models import PDFDataModel
from .events import StatusMessageEvent


class AutoGroupCommand(Command):
    """
    Command to auto-group words on a page.
    
    Stores the previous state to enable undo.
    """
    
    def __init__(
        self,
        model: PDFDataModel,
        page_num: int,
        new_groups: List[List[Dict[str, Any]]],
        event_bus: Optional[EventBus] = None
    ):
        """
        Initialize auto-group command.
        
        Args:
            model: Data model
            page_num: Page number to group
            new_groups: New groups to apply
            event_bus: Optional event bus for status messages
        """
        super().__init__()
        self.model = model
        self.page_num = page_num
        self.new_groups = new_groups
        self.event_bus = event_bus
        
        # Store previous state for undo
        self.previous_groups: Optional[List[List[Dict[str, Any]]]] = None
    
    def execute(self) -> bool:
        """
        Execute the grouping operation.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Save current state for undo
            self.previous_groups = self.model.get_page_groups(self.page_num)
            
            # Apply new groups
            self.model.set_groups(self.page_num, self.new_groups)
            
            # Publish status message
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Auto-grouped page {self.page_num} into {len(self.new_groups)} groups",
                    level="info"
                ))
            
            return True
        except Exception as e:
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Failed to group: {str(e)}",
                    level="error"
                ))
            return False
    
    def undo(self) -> bool:
        """
        Undo the grouping operation.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.previous_groups is not None:
                self.model.set_groups(self.page_num, self.previous_groups)
            else:
                # Clear groups if there were none before
                self.model.clear_groups(self.page_num)
            
            # Publish status message
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Undid grouping on page {self.page_num}",
                    level="info"
                ))
            
            return True
        except Exception as e:
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Failed to undo: {str(e)}",
                    level="error"
                ))
            return False
    
    def get_description(self) -> str:
        """
        Get command description.
        
        Returns:
            Human-readable description
        """
        return f"Auto-group page {self.page_num}"


class ManualGroupCommand(Command):
    """
    Command to manually group selected words.
    
    Creates a new group from selected items.
    """
    
    def __init__(
        self,
        model: PDFDataModel,
        page_num: int,
        word_indices: List[int],
        event_bus: Optional[EventBus] = None
    ):
        """
        Initialize manual group command.
        
        Args:
            model: Data model
            page_num: Page number
            word_indices: Indices of words to group
            event_bus: Optional event bus
        """
        super().__init__()
        self.model = model
        self.page_num = page_num
        self.word_indices = word_indices
        self.event_bus = event_bus
        
        # Store previous state
        self.previous_groups: Optional[List[List[Dict[str, Any]]]] = None
    
    def execute(self) -> bool:
        """Execute manual grouping."""
        try:
            # Save current state
            self.previous_groups = self.model.get_page_groups(self.page_num)
            
            # Get all words
            words = self.model.get_page_data(self.page_num)
            if not words:
                return False
            
            # Create new group from selected words
            new_group = [words[i] for i in self.word_indices if i < len(words)]
            
            # Get existing groups (or create from all words if none)
            current_groups = self.previous_groups if self.previous_groups else [[w] for w in words]
            
            # Remove selected words from existing groups
            updated_groups = []
            for group in current_groups:
                filtered_group = [w for w in group if w not in new_group]
                if filtered_group:
                    updated_groups.append(filtered_group)
            
            # Add new group
            updated_groups.append(new_group)
            
            # Apply
            self.model.set_groups(self.page_num, updated_groups)
            
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Grouped {len(new_group)} items on page {self.page_num}",
                    level="info"
                ))
            
            return True
        except Exception as e:
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Failed to group: {str(e)}",
                    level="error"
                ))
            return False
    
    def undo(self) -> bool:
        """Undo manual grouping."""
        try:
            if self.previous_groups is not None:
                self.model.set_groups(self.page_num, self.previous_groups)
            else:
                self.model.clear_groups(self.page_num)
            
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Undid manual grouping on page {self.page_num}",
                    level="info"
                ))
            
            return True
        except Exception as e:
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Failed to undo: {str(e)}",
                    level="error"
                ))
            return False
    
    def get_description(self) -> str:
        """Get command description."""
        return f"Manual group {len(self.word_indices)} items on page {self.page_num}"


class UngroupCommand(Command):
    """
    Command to ungroup a group.
    
    Breaks a group back into individual words.
    """
    
    def __init__(
        self,
        model: PDFDataModel,
        page_num: int,
        group_index: int,
        event_bus: Optional[EventBus] = None
    ):
        """
        Initialize ungroup command.
        
        Args:
            model: Data model
            page_num: Page number
            group_index: Index of group to ungroup
            event_bus: Optional event bus
        """
        super().__init__()
        self.model = model
        self.page_num = page_num
        self.group_index = group_index
        self.event_bus = event_bus
        
        # Store previous state
        self.previous_groups: Optional[List[List[Dict[str, Any]]]] = None
    
    def execute(self) -> bool:
        """Execute ungrouping."""
        try:
            # Save current state
            self.previous_groups = self.model.get_page_groups(self.page_num)
            
            if not self.previous_groups or self.group_index >= len(self.previous_groups):
                return False
            
            # Get the group to ungroup
            group_to_ungroup = self.previous_groups[self.group_index]
            
            # Create new groups list without the ungrouped group
            new_groups = [
                g for i, g in enumerate(self.previous_groups)
                if i != self.group_index
            ]
            
            # Add each word as individual group
            for word in group_to_ungroup:
                new_groups.append([word])
            
            # Apply
            self.model.set_groups(self.page_num, new_groups)
            
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Ungrouped {len(group_to_ungroup)} items on page {self.page_num}",
                    level="info"
                ))
            
            return True
        except Exception as e:
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Failed to ungroup: {str(e)}",
                    level="error"
                ))
            return False
    
    def undo(self) -> bool:
        """Undo ungrouping."""
        try:
            if self.previous_groups is not None:
                self.model.set_groups(self.page_num, self.previous_groups)
            
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Undid ungrouping on page {self.page_num}",
                    level="info"
                ))
            
            return True
        except Exception as e:
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Failed to undo: {str(e)}",
                    level="error"
                ))
            return False
    
    def get_description(self) -> str:
        """Get command description."""
        return f"Ungroup on page {self.page_num}"


class ClearGroupsCommand(Command):
    """
    Command to clear all groups on a page.
    
    Removes all grouping, returning to individual words.
    """
    
    def __init__(
        self,
        model: PDFDataModel,
        page_num: int,
        event_bus: Optional[EventBus] = None
    ):
        """
        Initialize clear groups command.
        
        Args:
            model: Data model
            page_num: Page number
            event_bus: Optional event bus
        """
        super().__init__()
        self.model = model
        self.page_num = page_num
        self.event_bus = event_bus
        
        # Store previous state
        self.previous_groups: Optional[List[List[Dict[str, Any]]]] = None
    
    def execute(self) -> bool:
        """Execute clearing groups."""
        try:
            # Save current state
            self.previous_groups = self.model.get_page_groups(self.page_num)
            
            # Clear groups
            self.model.clear_groups(self.page_num)
            
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Cleared groups on page {self.page_num}",
                    level="info"
                ))
            
            return True
        except Exception as e:
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Failed to clear groups: {str(e)}",
                    level="error"
                ))
            return False
    
    def undo(self) -> bool:
        """Undo clearing groups."""
        try:
            if self.previous_groups is not None:
                self.model.set_groups(self.page_num, self.previous_groups)
            
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Restored groups on page {self.page_num}",
                    level="info"
                ))
            
            return True
        except Exception as e:
            if self.event_bus:
                self.event_bus.publish(StatusMessageEvent(
                    message=f"Failed to undo: {str(e)}",
                    level="error"
                ))
            return False
    
    def get_description(self) -> str:
        """Get command description."""
        return f"Clear groups on page {self.page_num}"
