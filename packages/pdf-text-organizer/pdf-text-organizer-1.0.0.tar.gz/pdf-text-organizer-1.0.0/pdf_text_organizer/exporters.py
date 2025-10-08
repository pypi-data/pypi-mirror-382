"""Export functionality for grouped text."""

import json
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path

from .utils.geometry import get_group_bounds, group_to_text, get_group_statistics


class JSONExporter:
    """Export grouped text to JSON format."""
    
    @staticmethod
    def export(
        filepath: str,
        pages: Dict[int, List[Dict[str, Any]]],
        groups: Dict[int, List[List[Dict[str, Any]]]],
        include_coordinates: bool = True
    ) -> None:
        """
        Export to JSON file.
        
        Args:
            filepath: Output file path
            pages: Page data (words)
            groups: Group data
            include_coordinates: Whether to include coordinate data
        
        Raises:
            IOError: If file cannot be written
        """
        output = {
            'metadata': {
                'source': filepath,
                'page_count': len(pages),
                'total_groups': sum(len(g) for g in groups.values())
            },
            'pages': []
        }
        
        for page_num in sorted(pages.keys()):
            page_groups = groups.get(page_num, [])
            
            page_data = {
                'page_number': page_num,
                'group_count': len(page_groups),
                'groups': []
            }
            
            for group_idx, group in enumerate(page_groups):
                stats = get_group_statistics(group)
                
                group_data = {
                    'group_id': group_idx,
                    'text': stats['text'],
                    'word_count': stats['word_count']
                }
                
                if include_coordinates:
                    group_data['bounds'] = stats['bounds']
                    group_data['center'] = stats['center']
                    group_data['width'] = stats['width']
                    group_data['height'] = stats['height']
                    
                    # Include individual words
                    group_data['words'] = [
                        {
                            'text': w['text'],
                            'x0': w['x0'],
                            'top': w['top'],
                            'x1': w['x1'],
                            'bottom': w['bottom']
                        }
                        for w in group
                    ]
                
                page_data['groups'].append(group_data)
            
            output['pages'].append(page_data)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)


class CSVExporter:
    """Export grouped text to CSV format."""
    
    @staticmethod
    def export(
        filepath: str,
        pages: Dict[int, List[Dict[str, Any]]],
        groups: Dict[int, List[List[Dict[str, Any]]]],
        include_coordinates: bool = True
    ) -> None:
        """
        Export to CSV file.
        
        Args:
            filepath: Output file path
            pages: Page data (words)
            groups: Group data
            include_coordinates: Whether to include coordinate data
        
        Raises:
            IOError: If file cannot be written
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if include_coordinates:
                fieldnames = [
                    'page', 'group_id', 'text', 'word_count',
                    'x0', 'top', 'x1', 'bottom', 'width', 'height'
                ]
            else:
                fieldnames = ['page', 'group_id', 'text', 'word_count']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for page_num in sorted(pages.keys()):
                page_groups = groups.get(page_num, [])
                
                for group_idx, group in enumerate(page_groups):
                    stats = get_group_statistics(group)
                    
                    row = {
                        'page': page_num,
                        'group_id': group_idx,
                        'text': stats['text'],
                        'word_count': stats['word_count']
                    }
                    
                    if include_coordinates:
                        bounds = stats['bounds']
                        row.update({
                            'x0': f"{bounds['x0']:.2f}",
                            'top': f"{bounds['top']:.2f}",
                            'x1': f"{bounds['x1']:.2f}",
                            'bottom': f"{bounds['bottom']:.2f}",
                            'width': f"{stats['width']:.2f}",
                            'height': f"{stats['height']:.2f}"
                        })
                    
                    writer.writerow(row)


class TXTExporter:
    """Export grouped text to plain text format."""
    
    @staticmethod
    def export(
        filepath: str,
        pages: Dict[int, List[Dict[str, Any]]],
        groups: Dict[int, List[List[Dict[str, Any]]]],
        include_coordinates: bool = False
    ) -> None:
        """
        Export to plain text file.
        
        Args:
            filepath: Output file path
            pages: Page data (words)
            groups: Group data
            include_coordinates: Whether to include coordinate data
        
        Raises:
            IOError: If file cannot be written
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("PDF Text Organizer Export\n")
            f.write("=" * 50 + "\n\n")
            
            for page_num in sorted(pages.keys()):
                page_groups = groups.get(page_num, [])
                
                f.write(f"Page {page_num}\n")
                f.write("-" * 50 + "\n\n")
                
                for group_idx, group in enumerate(page_groups):
                    stats = get_group_statistics(group)
                    
                    f.write(f"Group {group_idx + 1}:\n")
                    f.write(f"{stats['text']}\n")
                    
                    if include_coordinates:
                        bounds = stats['bounds']
                        f.write(f"  Words: {stats['word_count']}\n")
                        f.write(f"  Position: ({bounds['x0']:.1f}, {bounds['top']:.1f}) "
                               f"to ({bounds['x1']:.1f}, {bounds['bottom']:.1f})\n")
                        f.write(f"  Size: {stats['width']:.1f} x {stats['height']:.1f}\n")
                    
                    f.write("\n")
                
                f.write("\n")


class MarkdownExporter:
    """Export grouped text to Markdown format."""
    
    @staticmethod
    def export(
        filepath: str,
        pages: Dict[int, List[Dict[str, Any]]],
        groups: Dict[int, List[List[Dict[str, Any]]]],
        include_coordinates: bool = False
    ) -> None:
        """
        Export to Markdown file.
        
        Args:
            filepath: Output file path
            pages: Page data (words)
            groups: Group data
            include_coordinates: Whether to include coordinate data
        
        Raises:
            IOError: If file cannot be written
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# PDF Text Organizer Export\n\n")
            
            # Summary
            total_groups = sum(len(g) for g in groups.values())
            f.write(f"**Pages**: {len(pages)}  \n")
            f.write(f"**Total Groups**: {total_groups}\n\n")
            f.write("---\n\n")
            
            for page_num in sorted(pages.keys()):
                page_groups = groups.get(page_num, [])
                
                f.write(f"## Page {page_num}\n\n")
                f.write(f"*{len(page_groups)} groups*\n\n")
                
                for group_idx, group in enumerate(page_groups):
                    stats = get_group_statistics(group)
                    
                    f.write(f"### Group {group_idx + 1}\n\n")
                    f.write(f"{stats['text']}\n\n")
                    
                    if include_coordinates:
                        bounds = stats['bounds']
                        f.write(f"- **Words**: {stats['word_count']}\n")
                        f.write(f"- **Position**: ({bounds['x0']:.1f}, {bounds['top']:.1f}) "
                               f"to ({bounds['x1']:.1f}, {bounds['bottom']:.1f})\n")
                        f.write(f"- **Size**: {stats['width']:.1f} × {stats['height']:.1f}\n")
                        f.write("\n")
                
                f.write("\n")


def get_exporter(format_type: str):
    """
    Get exporter for specified format.
    
    Args:
        format_type: Export format ('json', 'csv', 'txt', 'md')
    
    Returns:
        Exporter class
    
    Raises:
        ValueError: If format is not supported
    """
    exporters = {
        'json': JSONExporter,
        'csv': CSVExporter,
        'txt': TXTExporter,
        'md': MarkdownExporter,
        'markdown': MarkdownExporter
    }
    
    format_lower = format_type.lower()
    if format_lower not in exporters:
        raise ValueError(f"Unsupported export format: {format_type}")
    
    return exporters[format_lower]
