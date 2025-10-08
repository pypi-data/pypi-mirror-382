"""Spatial grouping algorithms for text organization."""

from typing import List, Dict, Any, Tuple
from math import sqrt


def euclidean_distance(word1: Dict[str, Any], word2: Dict[str, Any]) -> float:
    """
    Calculate Euclidean distance between centers of two words.
    
    Args:
        word1: First word dictionary with x0, top, x1, bottom
        word2: Second word dictionary with x0, top, x1, bottom
    
    Returns:
        Euclidean distance between word centers
    """
    x1 = (word1['x0'] + word1['x1']) / 2
    y1 = (word1['top'] + word1['bottom']) / 2
    x2 = (word2['x0'] + word2['x1']) / 2
    y2 = (word2['top'] + word2['bottom']) / 2
    
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def get_word_center(word: Dict[str, Any]) -> Tuple[float, float]:
    """
    Get the center point of a word.
    
    Args:
        word: Word dictionary with x0, top, x1, bottom
    
    Returns:
        Tuple of (x, y) coordinates
    """
    x = (word['x0'] + word['x1']) / 2
    y = (word['top'] + word['bottom']) / 2
    return (x, y)


def auto_group_words(
    words: List[Dict[str, Any]],
    y_threshold: float = 20.0,
    dist_threshold: float = 50.0
) -> List[List[Dict[str, Any]]]:
    """
    Automatically group words by spatial proximity.
    
    Algorithm:
    1. Sort words by y-coordinate (top-down), then x-coordinate (left-right)
    2. Group consecutive words if y-distance < y_threshold (same line)
    3. Further cluster lines if vertical distance < dist_threshold (nearby blocks)
    
    Args:
        words: List of word dictionaries with coordinates
        y_threshold: Maximum y-distance for same-line grouping (default: 20)
        dist_threshold: Maximum vertical distance for block clustering (default: 50)
    
    Returns:
        List of groups, where each group is a list of words
    
    Example:
        >>> words = [
        ...     {'text': 'Hello', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
        ...     {'text': 'World', 'x0': 60, 'top': 20, 'x1': 100, 'bottom': 30}
        ... ]
        >>> groups = auto_group_words(words, y_threshold=15)
        >>> len(groups)
        1
        >>> len(groups[0])
        2
    """
    if not words:
        return []
    
    # Sort words: top-down (negative top for descending), left-right
    sorted_words = sorted(words, key=lambda w: (w['top'], w['x0']))
    
    # Phase 1: Group by lines (y-proximity)
    lines: List[List[Dict[str, Any]]] = []
    current_line = [sorted_words[0]]
    
    for word in sorted_words[1:]:
        prev_word = current_line[-1]
        y_distance = abs(word['top'] - prev_word['top'])
        
        if y_distance < y_threshold:
            # Same line
            current_line.append(word)
        else:
            # New line
            lines.append(current_line)
            current_line = [word]
    
    if current_line:
        lines.append(current_line)
    
    # Phase 2: Cluster lines into blocks (vertical distance-based)
    if not lines:
        return []
    
    blocks: List[List[List[Dict[str, Any]]]] = [[lines[0]]]
    
    for line in lines[1:]:
        # Check vertical distance to last block's last line
        last_block = blocks[-1]
        last_line = last_block[-1]
        
        # Calculate vertical distance between line bottoms/tops
        last_line_bottom = max(w['bottom'] for w in last_line)
        current_line_top = min(w['top'] for w in line)
        
        vertical_gap = current_line_top - last_line_bottom
        
        if vertical_gap < dist_threshold:
            # Add to current block
            last_block.append(line)
        else:
            # Start new block
            blocks.append([line])
    
    # Flatten blocks (each block is list of lines, flatten to list of words)
    flattened_groups: List[List[Dict[str, Any]]] = []
    for block in blocks:
        flat_group: List[Dict[str, Any]] = []
        for line in block:
            flat_group.extend(line)
        flattened_groups.append(flat_group)
    
    return flattened_groups


def get_group_bounds(group: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate bounding box for a group of words.
    
    Args:
        group: List of word dictionaries
    
    Returns:
        Dictionary with x0, top, x1, bottom coordinates
    
    Example:
        >>> words = [
        ...     {'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
        ...     {'x0': 60, 'top': 20, 'x1': 100, 'bottom': 30}
        ... ]
        >>> bounds = get_group_bounds(words)
        >>> bounds['x0']
        10
        >>> bounds['x1']
        100
    """
    if not group:
        return {'x0': 0, 'top': 0, 'x1': 0, 'bottom': 0}
    
    x0 = min(w['x0'] for w in group)
    top = min(w['top'] for w in group)
    x1 = max(w['x1'] for w in group)
    bottom = max(w['bottom'] for w in group)
    
    return {'x0': x0, 'top': top, 'x1': x1, 'bottom': bottom}


def group_to_text(group: List[Dict[str, Any]]) -> str:
    """
    Convert a group of words to a single text string.
    
    Sorts words by reading order (top-down, left-right) before joining.
    
    Args:
        group: List of word dictionaries
    
    Returns:
        Concatenated text string
    
    Example:
        >>> words = [
        ...     {'text': 'World', 'x0': 60, 'top': 20, 'x1': 100, 'bottom': 30},
        ...     {'text': 'Hello', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30}
        ... ]
        >>> group_to_text(words)
        'Hello World'
    """
    if not group:
        return ""
    
    # Sort by reading order within group
    sorted_group = sorted(group, key=lambda w: (w['top'], w['x0']))
    return ' '.join(w['text'] for w in sorted_group)


def merge_groups(
    group1: List[Dict[str, Any]],
    group2: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Merge two groups into one.
    
    Args:
        group1: First group
        group2: Second group
    
    Returns:
        Combined group
    """
    return group1 + group2


def split_group(
    group: List[Dict[str, Any]],
    split_index: int
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Split a group at a specific index.
    
    Args:
        group: Group to split
        split_index: Index to split at
    
    Returns:
        Tuple of (first_group, second_group)
    """
    if split_index < 0 or split_index >= len(group):
        return (group, [])
    
    return (group[:split_index], group[split_index:])


def get_group_statistics(group: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for a group.
    
    Args:
        group: List of word dictionaries
    
    Returns:
        Dictionary with statistics (word_count, bounds, center, text)
    """
    if not group:
        return {
            'word_count': 0,
            'bounds': {'x0': 0, 'top': 0, 'x1': 0, 'bottom': 0},
            'center': (0, 0),
            'text': ''
        }
    
    bounds = get_group_bounds(group)
    center_x = (bounds['x0'] + bounds['x1']) / 2
    center_y = (bounds['top'] + bounds['bottom']) / 2
    
    return {
        'word_count': len(group),
        'bounds': bounds,
        'center': (center_x, center_y),
        'text': group_to_text(group),
        'width': bounds['x1'] - bounds['x0'],
        'height': bounds['bottom'] - bounds['top']
    }
