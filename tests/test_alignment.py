"""Unit tests for sequence alignment functionality.

Tests the align_sequences function which uses DTW to align predicted and
ground truth chord sequences to the same length.

Validates: Requirements 10.1, 10.2, 10.3, 10.4
"""

import pytest
from src.evaluation.alignment import align_sequences


class TestAlignSequences:
    """Test suite for align_sequences function."""
    
    def test_same_length_sequences(self):
        """Test alignment when sequences already have the same length."""
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Should return copies of the original sequences
        assert aligned_pred == predicted
        assert aligned_gt == ground_truth
        assert len(aligned_pred) == len(aligned_gt)
        
        # Verify original sequences are not modified
        assert predicted == ["D", "A", "Bm7", "G"]
        assert ground_truth == ["D", "A", "Bm7", "G"]
    
    def test_predicted_shorter_than_ground_truth(self):
        """Test alignment when predicted sequence is shorter."""
        predicted = ["D", "A", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Both aligned sequences should have the same length
        assert len(aligned_pred) == len(aligned_gt)
        
        # Aligned sequences should be at least as long as the longer input
        assert len(aligned_pred) >= len(ground_truth)
        
        # Original sequences should be preserved
        assert predicted == ["D", "A", "G"]
        assert ground_truth == ["D", "A", "Bm7", "G"]
    
    def test_ground_truth_shorter_than_predicted(self):
        """Test alignment when ground truth sequence is shorter."""
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "A", "G"]
        
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Both aligned sequences should have the same length
        assert len(aligned_pred) == len(aligned_gt)
        
        # Aligned sequences should be at least as long as the longer input
        assert len(aligned_pred) >= len(predicted)
        
        # Original sequences should be preserved
        assert predicted == ["D", "A", "Bm7", "G"]
        assert ground_truth == ["D", "A", "G"]
    
    def test_empty_sequences(self):
        """Test alignment with empty sequences."""
        # Both empty
        aligned_pred, aligned_gt = align_sequences([], [])
        assert aligned_pred == []
        assert aligned_gt == []
        
        # Only predicted empty - should return empty for both
        ground_truth = ["D", "A", "G"]
        aligned_pred, aligned_gt = align_sequences([], ground_truth)
        assert aligned_pred == []
        assert aligned_gt == []
        
        # Only ground truth empty - should return empty for both
        predicted = ["D", "A", "G"]
        aligned_pred, aligned_gt = align_sequences(predicted, [])
        assert aligned_pred == []
        assert aligned_gt == []
    
    def test_single_chord_sequences(self):
        """Test alignment with single chord sequences."""
        predicted = ["D"]
        ground_truth = ["D", "A", "G"]
        
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Both should have the same length
        assert len(aligned_pred) == len(aligned_gt)
        
        # Original sequences preserved
        assert predicted == ["D"]
        assert ground_truth == ["D", "A", "G"]
    
    def test_alignment_minimizes_distortion(self):
        """Test that alignment minimizes distortion using chord similarity."""
        # Predicted has a repeated chord that should align well
        predicted = ["D", "D", "A", "G"]
        ground_truth = ["D", "A", "G"]
        
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Both should have the same length
        assert len(aligned_pred) == len(aligned_gt)
        
        # The alignment should preserve the chord sequence structure
        # (exact alignment depends on DTW algorithm, but length must match)
        assert len(aligned_pred) >= max(len(predicted), len(ground_truth))
    
    def test_alignment_with_similar_chords(self):
        """Test alignment with chords that have same root but different quality."""
        predicted = ["D", "Am", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Both should have the same length
        assert len(aligned_pred) == len(aligned_gt)
        
        # Original sequences preserved
        assert predicted == ["D", "Am", "G"]
        assert ground_truth == ["D", "A", "Bm7", "G"]
    
    def test_alignment_with_completely_different_chords(self):
        """Test alignment with completely different chord sequences."""
        predicted = ["C", "F", "G"]
        ground_truth = ["D", "A", "Bm7", "E"]
        
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Both should have the same length
        assert len(aligned_pred) == len(aligned_gt)
        
        # Original sequences preserved
        assert predicted == ["C", "F", "G"]
        assert ground_truth == ["D", "A", "Bm7", "E"]
    
    def test_alignment_preserves_original_sequences(self):
        """Test that alignment does not modify original sequences."""
        predicted = ["D", "A", "G"]
        ground_truth = ["D", "A", "Bm7", "G", "D"]
        
        # Store original values
        original_predicted = predicted.copy()
        original_ground_truth = ground_truth.copy()
        
        # Perform alignment
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Verify originals are unchanged
        assert predicted == original_predicted
        assert ground_truth == original_ground_truth
        
        # Verify aligned sequences are different objects
        assert aligned_pred is not predicted
        assert aligned_gt is not ground_truth
    
    def test_alignment_result_length_property(self):
        """Test that aligned sequences always have the same length."""
        test_cases = [
            (["D"], ["D", "A", "G"]),
            (["D", "A"], ["D"]),
            (["D", "A", "G"], ["D", "A", "Bm7", "G", "D"]),
            (["C", "F", "G", "Am"], ["D", "A"]),
            (["D", "A", "Bm7", "G", "D", "A"], ["D", "G"]),
        ]
        
        for predicted, ground_truth in test_cases:
            aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
            assert len(aligned_pred) == len(aligned_gt), \
                f"Aligned sequences have different lengths for input: {predicted}, {ground_truth}"
    
    def test_alignment_with_slash_chords(self):
        """Test alignment with slash chords."""
        predicted = ["D", "AonC#", "Bm7", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Both should have the same length
        assert len(aligned_pred) == len(aligned_gt)
        
        # Original sequences preserved
        assert predicted == ["D", "AonC#", "Bm7", "G"]
        assert ground_truth == ["D", "A", "Bm7", "G"]
    
    def test_alignment_with_complex_qualities(self):
        """Test alignment with various chord qualities."""
        predicted = ["Cmaj7", "Dm7", "G7", "Cmaj7"]
        ground_truth = ["C", "Dm7", "G7"]
        
        aligned_pred, aligned_gt = align_sequences(predicted, ground_truth)
        
        # Both should have the same length
        assert len(aligned_pred) == len(aligned_gt)
        
        # Original sequences preserved
        assert predicted == ["Cmaj7", "Dm7", "G7", "Cmaj7"]
        assert ground_truth == ["C", "Dm7", "G7"]
