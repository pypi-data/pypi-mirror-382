"""Tests for geometry utilities."""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Main')))

from pdf_text_organizer.utils.geometry import (
    euclidean_distance,
    get_word_center,
    auto_group_words,
    get_group_bounds,
    group_to_text,
    merge_groups,
    split_group,
    get_group_statistics
)


class TestEuclideanDistance:
    """Tests for euclidean_distance function."""
    
    def test_distance_same_point(self):
        """Test distance between same point is zero."""
        word1 = {'x0': 10, 'top': 20, 'x1': 30, 'bottom': 40}
        word2 = {'x0': 10, 'top': 20, 'x1': 30, 'bottom': 40}
        
        distance = euclidean_distance(word1, word2)
        
        assert distance == 0.0
    
    def test_distance_horizontal(self):
        """Test distance between horizontally separated words."""
        word1 = {'x0': 0, 'top': 0, 'x1': 10, 'bottom': 10}
        word2 = {'x0': 30, 'top': 0, 'x1': 40, 'bottom': 10}
        
        distance = euclidean_distance(word1, word2)
        
        # Centers are at (5, 5) and (35, 5), distance = 30
        assert distance == 30.0
    
    def test_distance_vertical(self):
        """Test distance between vertically separated words."""
        word1 = {'x0': 0, 'top': 0, 'x1': 10, 'bottom': 10}
        word2 = {'x0': 0, 'top': 40, 'x1': 10, 'bottom': 50}
        
        distance = euclidean_distance(word1, word2)
        
        # Centers are at (5, 5) and (5, 45), distance = 40
        assert distance == 40.0


class TestGetWordCenter:
    """Tests for get_word_center function."""
    
    def test_center_calculation(self):
        """Test center point calculation."""
        word = {'x0': 10, 'top': 20, 'x1': 30, 'bottom': 40}
        
        center = get_word_center(word)
        
        assert center == (20.0, 30.0)


class TestAutoGroupWords:
    """Tests for auto_group_words function."""
    
    def test_empty_list(self):
        """Test grouping empty list returns empty."""
        groups = auto_group_words([])
        
        assert groups == []
    
    def test_single_word(self):
        """Test grouping single word."""
        words = [{'text': 'test', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30}]
        
        groups = auto_group_words(words)
        
        assert len(groups) == 1
        assert len(groups[0]) == 1
        assert groups[0][0]['text'] == 'test'
    
    def test_same_line_grouping(self):
        """Test words on same line are grouped together."""
        words = [
            {'text': 'Hello', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
            {'text': 'World', 'x0': 60, 'top': 22, 'x1': 100, 'bottom': 32}
        ]
        
        groups = auto_group_words(words, y_threshold=15)
        
        assert len(groups) == 1
        assert len(groups[0]) == 2
    
    def test_different_lines_separate_groups(self):
        """Test words on different lines create separate groups."""
        words = [
            {'text': 'Line1', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
            {'text': 'Line2', 'x0': 10, 'top': 100, 'x1': 50, 'bottom': 110}
        ]
        
        groups = auto_group_words(words, y_threshold=15, dist_threshold=50)
        
        assert len(groups) == 2
    
    def test_nearby_lines_same_block(self):
        """Test nearby lines are grouped into same block."""
        words = [
            {'text': 'Line1', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
            {'text': 'Line2', 'x0': 10, 'top': 35, 'x1': 50, 'bottom': 45}
        ]
        
        groups = auto_group_words(words, y_threshold=5, dist_threshold=20)
        
        # Two lines but close together, should be one block
        assert len(groups) == 1
        assert len(groups[0]) == 2
    
    def test_sorting_by_position(self):
        """Test words are sorted by position."""
        words = [
            {'text': 'Third', 'x0': 10, 'top': 60, 'x1': 50, 'bottom': 70},
            {'text': 'First', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
            {'text': 'Second', 'x0': 10, 'top': 40, 'x1': 50, 'bottom': 50}
        ]
        
        groups = auto_group_words(words, y_threshold=5, dist_threshold=100)
        
        # All should be in one group, sorted by top position
        assert len(groups) == 1
        assert groups[0][0]['text'] == 'First'
        assert groups[0][1]['text'] == 'Second'
        assert groups[0][2]['text'] == 'Third'


class TestGetGroupBounds:
    """Tests for get_group_bounds function."""
    
    def test_empty_group(self):
        """Test bounds of empty group."""
        bounds = get_group_bounds([])
        
        assert bounds == {'x0': 0, 'top': 0, 'x1': 0, 'bottom': 0}
    
    def test_single_word_bounds(self):
        """Test bounds of single word."""
        words = [{'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30}]
        
        bounds = get_group_bounds(words)
        
        assert bounds['x0'] == 10
        assert bounds['top'] == 20
        assert bounds['x1'] == 50
        assert bounds['bottom'] == 30
    
    def test_multiple_words_bounds(self):
        """Test bounds encompass all words."""
        words = [
            {'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30},
            {'x0': 60, 'top': 25, 'x1': 100, 'bottom': 35},
            {'x0': 5, 'top': 40, 'x1': 45, 'bottom': 50}
        ]
        
        bounds = get_group_bounds(words)
        
        assert bounds['x0'] == 5  # Minimum x0
        assert bounds['top'] == 20  # Minimum top
        assert bounds['x1'] == 100  # Maximum x1
        assert bounds['bottom'] == 50  # Maximum bottom


class TestGroupToText:
    """Tests for group_to_text function."""
    
    def test_empty_group(self):
        """Test text of empty group."""
        text = group_to_text([])
        
        assert text == ""
    
    def test_single_word(self):
        """Test text of single word."""
        words = [{'text': 'Hello', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30}]
        
        text = group_to_text(words)
        
        assert text == "Hello"
    
    def test_multiple_words_sorted(self):
        """Test words are sorted by reading order."""
        words = [
            {'text': 'World', 'x0': 60, 'top': 20, 'x1': 100, 'bottom': 30},
            {'text': 'Hello', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30}
        ]
        
        text = group_to_text(words)
        
        assert text == "Hello World"
    
    def test_multiline_text(self):
        """Test text from multiple lines."""
        words = [
            {'text': 'Line2', 'x0': 10, 'top': 40, 'x1': 50, 'bottom': 50},
            {'text': 'Line1', 'x0': 10, 'top': 20, 'x1': 50, 'bottom': 30}
        ]
        
        text = group_to_text(words)
        
        assert text == "Line1 Line2"


class TestMergeGroups:
    """Tests for merge_groups function."""
    
    def test_merge_two_groups(self):
        """Test merging two groups."""
        group1 = [{'text': 'A'}, {'text': 'B'}]
        group2 = [{'text': 'C'}, {'text': 'D'}]
        
        merged = merge_groups(group1, group2)
        
        assert len(merged) == 4
        assert merged[0]['text'] == 'A'
        assert merged[3]['text'] == 'D'


class TestSplitGroup:
    """Tests for split_group function."""
    
    def test_split_at_middle(self):
        """Test splitting group in middle."""
        group = [{'text': 'A'}, {'text': 'B'}, {'text': 'C'}, {'text': 'D'}]
        
        first, second = split_group(group, 2)
        
        assert len(first) == 2
        assert len(second) == 2
        assert first[0]['text'] == 'A'
        assert second[0]['text'] == 'C'
    
    def test_split_at_invalid_index(self):
        """Test splitting at invalid index."""
        group = [{'text': 'A'}, {'text': 'B'}]
        
        first, second = split_group(group, 10)
        
        assert first == group
        assert second == []


class TestGetGroupStatistics:
    """Tests for get_group_statistics function."""
    
    def test_empty_group_stats(self):
        """Test statistics of empty group."""
        stats = get_group_statistics([])
        
        assert stats['word_count'] == 0
        assert stats['center'] == (0, 0)
    
    def test_group_stats(self):
        """Test statistics calculation."""
        words = [
            {'text': 'Hello', 'x0': 0, 'top': 0, 'x1': 40, 'bottom': 10},
            {'text': 'World', 'x0': 50, 'top': 0, 'x1': 90, 'bottom': 10}
        ]
        
        stats = get_group_statistics(words)
        
        assert stats['word_count'] == 2
        assert stats['text'] == "Hello World"
        assert stats['width'] == 90  # 90 - 0
        assert stats['height'] == 10  # 10 - 0
        assert stats['center'] == (45.0, 5.0)  # Center of bounding box
