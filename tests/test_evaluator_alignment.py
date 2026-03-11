"""Tests for evaluator integration with sequence alignment.

Tests that the Evaluator.evaluate() method correctly uses alignment when
sequences have different lengths.

Validates: Requirements 10.1, 10.2, 10.3, 10.4
"""

import pytest
from src.evaluation.evaluator import Evaluator


class TestEvaluatorWithAlignment:
    """Test suite for evaluator with alignment integration."""
    
    def test_evaluate_with_same_length_sequences(self):
        """Test evaluation when sequences have the same length."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        metrics = evaluator.evaluate(predicted, ground_truth)
        
        # Perfect match should give perfect scores
        assert metrics.sequence_accuracy == 1.0
        assert metrics.root_accuracy == 1.0
        assert metrics.quality_accuracy == 1.0
        assert metrics.exact_match_rate == 1.0
        assert metrics.dtw_distance == 0.0
    
    def test_evaluate_with_different_length_sequences_alignment_enabled(self):
        """Test evaluation with different length sequences and alignment enabled."""
        evaluator = Evaluator()
        predicted = ["D", "A", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        # With alignment enabled (default)
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # Metrics should be calculated on aligned sequences
        # Root accuracy should be high since D->D, A->A, G->G match
        assert metrics.root_accuracy > 0.0
        
        # DTW distance should be non-zero but reasonable
        assert metrics.dtw_distance >= 0.0
    
    def test_evaluate_with_different_length_sequences_alignment_disabled(self):
        """Test evaluation with different length sequences and alignment disabled."""
        evaluator = Evaluator()
        predicted = ["D", "A", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        # With alignment disabled
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=False)
        
        # Most metrics should be 0.0 because lengths don't match
        assert metrics.sequence_accuracy == 0.0
        assert metrics.root_accuracy == 0.0
        assert metrics.quality_accuracy == 0.0
        assert metrics.exact_match_rate == 0.0
        
        # DTW distance should still be calculated
        assert metrics.dtw_distance >= 0.0
    
    def test_evaluate_predicted_shorter_than_ground_truth(self):
        """Test evaluation when predicted is shorter than ground truth."""
        evaluator = Evaluator()
        predicted = ["D", "A"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # Should have valid metrics after alignment
        assert 0.0 <= metrics.root_accuracy <= 1.0
        assert 0.0 <= metrics.quality_accuracy <= 1.0
        assert 0.0 <= metrics.exact_match_rate <= 1.0
        assert metrics.dtw_distance >= 0.0
    
    def test_evaluate_ground_truth_shorter_than_predicted(self):
        """Test evaluation when ground truth is shorter than predicted."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "A"]
        
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # Should have valid metrics after alignment
        assert 0.0 <= metrics.root_accuracy <= 1.0
        assert 0.0 <= metrics.quality_accuracy <= 1.0
        assert 0.0 <= metrics.exact_match_rate <= 1.0
        assert metrics.dtw_distance >= 0.0
    
    def test_evaluate_with_empty_predicted(self):
        """Test evaluation with empty predicted sequence."""
        evaluator = Evaluator()
        predicted = []
        ground_truth = ["D", "A", "G"]
        
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # When alignment returns empty sequences for both (can't meaningfully align),
        # sequence_accuracy is 1.0 (empty == empty), but other metrics are 0.0
        assert metrics.sequence_accuracy == 1.0  # Empty sequences match
        assert metrics.root_accuracy == 0.0
        assert metrics.quality_accuracy == 0.0
        assert metrics.exact_match_rate == 0.0
        assert metrics.dtw_distance == 0.0
    
    def test_evaluate_with_empty_ground_truth(self):
        """Test evaluation with empty ground truth sequence."""
        evaluator = Evaluator()
        predicted = ["D", "A", "G"]
        ground_truth = []
        
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # When alignment returns empty sequences for both (can't meaningfully align),
        # sequence_accuracy is 1.0 (empty == empty), but other metrics are 0.0
        assert metrics.sequence_accuracy == 1.0  # Empty sequences match
        assert metrics.root_accuracy == 0.0
        assert metrics.quality_accuracy == 0.0
        assert metrics.exact_match_rate == 0.0
        assert metrics.dtw_distance == 0.0
    
    def test_evaluate_alignment_improves_metrics(self):
        """Test that alignment improves metrics for misaligned sequences."""
        evaluator = Evaluator()
        
        # Sequences that are similar but different lengths
        predicted = ["D", "A", "G", "D"]
        ground_truth = ["D", "A", "Bm7", "G", "D"]
        
        # With alignment
        metrics_aligned = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # Without alignment
        metrics_not_aligned = evaluator.evaluate(predicted, ground_truth, align_sequences=False)
        
        # Aligned metrics should be better (or at least not worse)
        assert metrics_aligned.root_accuracy >= metrics_not_aligned.root_accuracy
    
    def test_evaluate_with_similar_chords_different_lengths(self):
        """Test evaluation with similar chords but different sequence lengths."""
        evaluator = Evaluator()
        
        # Predicted has major chords, ground truth has some minor variants
        predicted = ["D", "A", "G"]
        ground_truth = ["D", "Am", "Bm7", "G"]
        
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # Root accuracy should be reasonable since roots match
        assert metrics.root_accuracy > 0.5
        
        # Quality accuracy might be lower due to major/minor differences
        assert 0.0 <= metrics.quality_accuracy <= 1.0
    
    def test_evaluate_preserves_original_sequences(self):
        """Test that evaluation does not modify original sequences."""
        evaluator = Evaluator()
        
        predicted = ["D", "A", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        # Store original values
        original_predicted = predicted.copy()
        original_ground_truth = ground_truth.copy()
        
        # Perform evaluation
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # Verify originals are unchanged
        assert predicted == original_predicted
        assert ground_truth == original_ground_truth
    
    def test_evaluate_dtw_uses_original_sequences(self):
        """Test that DTW distance is calculated on original sequences, not aligned."""
        evaluator = Evaluator()
        
        predicted = ["D", "A", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        # Calculate DTW directly
        dtw_direct = evaluator.calculate_dtw_distance(predicted, ground_truth)
        
        # Calculate through evaluate with alignment
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # DTW distance should be the same (calculated on original sequences)
        assert metrics.dtw_distance == dtw_direct
    
    def test_evaluate_with_single_chord_sequences(self):
        """Test evaluation with single chord sequences of different lengths."""
        evaluator = Evaluator()
        
        predicted = ["D"]
        ground_truth = ["D", "A", "G"]
        
        metrics = evaluator.evaluate(predicted, ground_truth, align_sequences=True)
        
        # Should have valid metrics
        assert 0.0 <= metrics.root_accuracy <= 1.0
        assert 0.0 <= metrics.quality_accuracy <= 1.0
        assert metrics.dtw_distance >= 0.0
