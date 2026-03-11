"""Unit tests for the Evaluator class."""

import pytest
from src.evaluation.evaluator import Evaluator


class TestSequenceMatch:
    """Tests for the sequence_match method."""
    
    def test_exact_match_returns_one(self):
        """Test that exact sequence match returns 1.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        result = evaluator.sequence_match(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_different_chord_returns_zero(self):
        """Test that different chord in sequence returns 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "AonC#", "Bm7", "G"]
        
        result = evaluator.sequence_match(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_different_length_returns_zero(self):
        """Test that sequences of different lengths return 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        result = evaluator.sequence_match(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_empty_sequences_returns_one(self):
        """Test that two empty sequences return 1.0."""
        evaluator = Evaluator()
        predicted = []
        ground_truth = []
        
        result = evaluator.sequence_match(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_single_chord_match(self):
        """Test that single chord sequences match correctly."""
        evaluator = Evaluator()
        predicted = ["D"]
        ground_truth = ["D"]
        
        result = evaluator.sequence_match(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_single_chord_mismatch(self):
        """Test that single chord sequences mismatch correctly."""
        evaluator = Evaluator()
        predicted = ["D"]
        ground_truth = ["A"]
        
        result = evaluator.sequence_match(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_different_order_returns_zero(self):
        """Test that same chords in different order return 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["A", "D", "G", "Bm7"]
        
        result = evaluator.sequence_match(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_complex_chords_exact_match(self):
        """Test exact match with complex chord names."""
        evaluator = Evaluator()
        predicted = ["Cmaj7", "AonC#", "Dm7", "G7"]
        ground_truth = ["Cmaj7", "AonC#", "Dm7", "G7"]
        
        result = evaluator.sequence_match(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_case_sensitive_comparison(self):
        """Test that chord comparison is case-sensitive."""
        evaluator = Evaluator()
        predicted = ["D", "a", "Bm7"]
        ground_truth = ["D", "A", "Bm7"]
        
        result = evaluator.sequence_match(predicted, ground_truth)
        
        assert result == 0.0



class TestRootAccuracy:
    """Tests for the root_accuracy method."""
    
    def test_all_roots_match(self):
        """Test that all matching root notes returns 1.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "AonC#", "Bm7", "G"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_no_roots_match(self):
        """Test that no matching root notes returns 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["C", "F", "Em", "Am"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_partial_root_match(self):
        """Test that partial matching returns correct percentage."""
        evaluator = Evaluator()
        predicted = ["D", "A"]
        ground_truth = ["D", "F"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 0.5
    
    def test_slash_chords_root_extraction(self):
        """Test that slash chords extract root correctly."""
        evaluator = Evaluator()
        predicted = ["AonC#", "D/F#", "G/B"]
        ground_truth = ["A", "D", "G"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_complex_chords_root_match(self):
        """Test root matching with complex chord suffixes."""
        evaluator = Evaluator()
        predicted = ["Cmaj7", "Dm7", "G7", "Am"]
        ground_truth = ["C", "Dm", "G", "Am7"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_accidentals_in_roots(self):
        """Test root matching with sharp and flat accidentals."""
        evaluator = Evaluator()
        predicted = ["F#", "Bb", "C#m", "Ebmaj7"]
        ground_truth = ["F#m7", "Bb7", "C#", "Eb"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_different_length_returns_zero(self):
        """Test that sequences of different lengths return 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_empty_predicted_returns_zero(self):
        """Test that empty predicted sequence returns 0.0."""
        evaluator = Evaluator()
        predicted = []
        ground_truth = ["D", "A", "Bm7", "G"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_empty_ground_truth_returns_zero(self):
        """Test that empty ground truth sequence returns 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = []
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_both_empty_returns_zero(self):
        """Test that both empty sequences return 0.0."""
        evaluator = Evaluator()
        predicted = []
        ground_truth = []
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_single_chord_match(self):
        """Test single chord with matching root."""
        evaluator = Evaluator()
        predicted = ["D"]
        ground_truth = ["Dmaj7"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_single_chord_mismatch(self):
        """Test single chord with different root."""
        evaluator = Evaluator()
        predicted = ["D"]
        ground_truth = ["A"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_mixed_match_percentage(self):
        """Test accuracy calculation with mixed matches."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G", "C"]
        ground_truth = ["D", "F", "Bm", "A", "C"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        # D matches D, A doesn't match F, B matches B, G doesn't match A, C matches C
        # 3 out of 5 = 0.6
        assert result == 0.6
    
    def test_invalid_chord_handled_gracefully(self):
        """Test that invalid chords are handled without crashing."""
        evaluator = Evaluator()
        # If one chord is invalid, it should be counted as a mismatch
        predicted = ["D", "INVALID", "G"]
        ground_truth = ["D", "A", "G"]
        
        result = evaluator.root_accuracy(predicted, ground_truth)
        
        # D matches, INVALID doesn't match (can't extract root), G matches
        # 2 out of 3 = 0.666...
        assert result == pytest.approx(0.6666666666666666)


class TestQualityAccuracy:
    """Tests for the quality_accuracy method."""
    
    def test_all_qualities_match(self):
        """Test that all matching qualities returns 1.0."""
        evaluator = Evaluator()
        predicted = ["D", "Am", "D7", "Cmaj7"]
        ground_truth = ["D", "Am", "D7", "Cmaj7"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_no_qualities_match(self):
        """Test that no matching qualities returns 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "Am"]
        ground_truth = ["Dm", "A"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_partial_quality_match(self):
        """Test that partial matching returns correct percentage."""
        evaluator = Evaluator()
        predicted = ["D", "Am", "D7"]
        ground_truth = ["Dm", "Am", "D7"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # Am matches Am (minor), D7 matches D7 (seventh), D doesn't match Dm
        # 2 out of 3 = 0.6666...
        assert result == pytest.approx(0.6666666666666666)
    
    def test_same_root_different_quality(self):
        """Test chords with same root but different qualities."""
        evaluator = Evaluator()
        predicted = ["D", "Am", "D7", "Cmaj7"]
        ground_truth = ["Dmaj7", "Am7", "D7", "C"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # D (major) vs Dmaj7 (major_seventh): no match
        # Am (minor) vs Am7 (minor_seventh): no match
        # D7 (seventh) vs D7 (seventh): match
        # Cmaj7 (major_seventh) vs C (major): no match
        # 1 out of 4 = 0.25
        assert result == 0.25
    
    def test_major_vs_minor_quality(self):
        """Test distinguishing between major and minor qualities."""
        evaluator = Evaluator()
        predicted = ["D", "A", "G", "C"]
        ground_truth = ["Dm", "Am", "Gm", "Cm"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # All are major vs minor, no matches
        assert result == 0.0
    
    def test_seventh_vs_major_seventh(self):
        """Test distinguishing between seventh and major seventh."""
        evaluator = Evaluator()
        predicted = ["D7", "A7", "G7"]
        ground_truth = ["Dmaj7", "Amaj7", "Gmaj7"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # All are seventh vs major_seventh, no matches
        assert result == 0.0
    
    def test_minor_seventh_matching(self):
        """Test matching minor seventh chords."""
        evaluator = Evaluator()
        predicted = ["Bm7", "Am7", "Dm7"]
        ground_truth = ["Bm7", "Am7", "Dm7"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_complex_quality_variations(self):
        """Test various quality combinations."""
        evaluator = Evaluator()
        predicted = ["D", "Am", "G7", "Cmaj7", "Bm7"]
        ground_truth = ["D", "A", "G", "C", "Bm"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # D (major) vs D (major): match
        # Am (minor) vs A (major): no match
        # G7 (seventh) vs G (major): no match
        # Cmaj7 (major_seventh) vs C (major): no match
        # Bm7 (minor_seventh) vs Bm (minor): no match
        # 1 out of 5 = 0.2
        assert result == 0.2
    
    def test_slash_chords_quality_comparison(self):
        """Test quality comparison with slash chords."""
        evaluator = Evaluator()
        predicted = ["D/F#", "Am/C", "G7/B"]
        ground_truth = ["D", "Am", "G7"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # All qualities should match (slash doesn't affect quality)
        assert result == 1.0
    
    def test_different_length_returns_zero(self):
        """Test that sequences of different lengths return 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "Am", "D7"]
        ground_truth = ["D", "Am", "D7", "Cmaj7"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_empty_predicted_returns_zero(self):
        """Test that empty predicted sequence returns 0.0."""
        evaluator = Evaluator()
        predicted = []
        ground_truth = ["D", "Am", "D7"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_empty_ground_truth_returns_zero(self):
        """Test that empty ground truth sequence returns 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "Am", "D7"]
        ground_truth = []
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_both_empty_returns_zero(self):
        """Test that both empty sequences return 0.0."""
        evaluator = Evaluator()
        predicted = []
        ground_truth = []
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_single_chord_match(self):
        """Test single chord with matching quality."""
        evaluator = Evaluator()
        predicted = ["D"]
        ground_truth = ["G"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # Both are major quality
        assert result == 1.0
    
    def test_single_chord_mismatch(self):
        """Test single chord with different quality."""
        evaluator = Evaluator()
        predicted = ["D"]
        ground_truth = ["Dm"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # D is major, Dm is minor
        assert result == 0.0
    
    def test_suspended_and_augmented_qualities(self):
        """Test less common chord qualities."""
        evaluator = Evaluator()
        predicted = ["Dsus4", "Caug", "Bdim"]
        ground_truth = ["Dsus4", "Caug", "Bdim"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_mixed_quality_accuracy(self):
        """Test accuracy calculation with various quality matches."""
        evaluator = Evaluator()
        predicted = ["D", "Am", "G7", "Cmaj7", "Bm7", "Fsus4"]
        ground_truth = ["D", "Am7", "G7", "C", "Bm7", "Fsus4"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # D (major) vs D (major): match
        # Am (minor) vs Am7 (minor_seventh): no match
        # G7 (seventh) vs G7 (seventh): match
        # Cmaj7 (major_seventh) vs C (major): no match
        # Bm7 (minor_seventh) vs Bm7 (minor_seventh): match
        # Fsus4 (suspended) vs Fsus4 (suspended): match
        # 4 out of 6 = 0.6666...
        assert result == pytest.approx(0.6666666666666666)
    
    def test_invalid_chord_handled_gracefully(self):
        """Test that invalid chords are handled without crashing."""
        evaluator = Evaluator()
        # If one chord is invalid, it should be counted as a mismatch
        predicted = ["D", "INVALID", "Am"]
        ground_truth = ["D", "Am", "Am"]
        
        result = evaluator.quality_accuracy(predicted, ground_truth)
        
        # D matches D (both major), INVALID doesn't match (can't identify quality), Am matches Am (both minor)
        # 2 out of 3 = 0.6666...
        assert result == pytest.approx(0.6666666666666666)



class TestExactMatchRate:
    """Tests for the exact_match_rate method."""
    
    def test_all_chords_match(self):
        """Test that all matching chords returns 1.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_no_chords_match(self):
        """Test that no matching chords returns 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["C", "F", "Em", "Am"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_partial_match_three_out_of_four(self):
        """Test partial match rate calculation (3 out of 4)."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "AonC#", "Bm7", "G"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        # D matches, A doesn't match AonC#, Bm7 matches, G matches
        # 3 out of 4 = 0.75
        assert result == 0.75
    
    def test_partial_match_one_out_of_two(self):
        """Test partial match rate calculation (1 out of 2)."""
        evaluator = Evaluator()
        predicted = ["D", "A"]
        ground_truth = ["D", "F"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        # D matches, A doesn't match F
        # 1 out of 2 = 0.5
        assert result == 0.5
    
    def test_single_chord_match(self):
        """Test single chord exact match."""
        evaluator = Evaluator()
        predicted = ["D"]
        ground_truth = ["D"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_single_chord_mismatch(self):
        """Test single chord mismatch."""
        evaluator = Evaluator()
        predicted = ["D"]
        ground_truth = ["A"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_complex_chords_exact_match(self):
        """Test exact match with complex chord names."""
        evaluator = Evaluator()
        predicted = ["Cmaj7", "AonC#", "Dm7", "G7"]
        ground_truth = ["Cmaj7", "AonC#", "Dm7", "G7"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        assert result == 1.0
    
    def test_complex_chords_partial_match(self):
        """Test partial match with complex chord names."""
        evaluator = Evaluator()
        predicted = ["Cmaj7", "A", "Dm7", "G7"]
        ground_truth = ["Cmaj7", "AonC#", "Dm7", "G"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        # Cmaj7 matches, A doesn't match AonC#, Dm7 matches, G7 doesn't match G
        # 2 out of 4 = 0.5
        assert result == 0.5
    
    def test_case_sensitive_comparison(self):
        """Test that chord comparison is case-sensitive."""
        evaluator = Evaluator()
        predicted = ["D", "a", "Bm7"]
        ground_truth = ["D", "A", "Bm7"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        # D matches, a doesn't match A (case-sensitive), Bm7 matches
        # 2 out of 3 = 0.6666...
        assert result == pytest.approx(0.6666666666666666)
    
    def test_different_length_returns_zero(self):
        """Test that sequences of different lengths return 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7"]
        ground_truth = ["D", "A", "Bm7", "G"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_empty_predicted_returns_zero(self):
        """Test that empty predicted sequence returns 0.0."""
        evaluator = Evaluator()
        predicted = []
        ground_truth = ["D", "A", "Bm7", "G"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_empty_ground_truth_returns_zero(self):
        """Test that empty ground truth sequence returns 0.0."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = []
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_both_empty_returns_zero(self):
        """Test that both empty sequences return 0.0."""
        evaluator = Evaluator()
        predicted = []
        ground_truth = []
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        assert result == 0.0
    
    def test_same_root_different_quality_no_match(self):
        """Test that same root with different quality doesn't match."""
        evaluator = Evaluator()
        predicted = ["D", "Am", "G7"]
        ground_truth = ["Dmaj7", "Am7", "G"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        # None of the chords match exactly (different qualities)
        assert result == 0.0
    
    def test_slash_chords_must_match_exactly(self):
        """Test that slash chords must match exactly."""
        evaluator = Evaluator()
        predicted = ["D/F#", "A", "G/B"]
        ground_truth = ["D", "AonC#", "G"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        # None match exactly (slash notation differs)
        assert result == 0.0
    
    def test_mixed_match_percentage(self):
        """Test accuracy calculation with various matches."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G", "C", "F"]
        ground_truth = ["D", "F", "Bm7", "A", "C", "F#"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        # D matches, A doesn't match F, Bm7 matches, G doesn't match A, C matches, F doesn't match F#
        # 3 out of 6 = 0.5
        assert result == 0.5
    
    def test_accidentals_must_match_exactly(self):
        """Test that accidentals must match exactly."""
        evaluator = Evaluator()
        predicted = ["F#", "Bb", "C#m"]
        ground_truth = ["F", "B", "Cm"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        # None match exactly (accidentals differ)
        assert result == 0.0
    
    def test_long_sequence_partial_match(self):
        """Test match rate calculation with longer sequence."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G", "D", "A", "Bm7", "G", "Em", "A"]
        ground_truth = ["D", "A", "Bm7", "G", "D", "AonC#", "Bm7", "G", "Em", "A7"]
        
        result = evaluator.exact_match_rate(predicted, ground_truth)
        
        # Matches: D, A, Bm7, G, D, Bm7, G, Em (8 out of 10)
        # 8 out of 10 = 0.8
        assert result == 0.8
    
    def test_difference_from_sequence_match(self):
        """Test that exact_match_rate differs from sequence_match behavior."""
        evaluator = Evaluator()
        predicted = ["D", "A", "Bm7", "G"]
        ground_truth = ["D", "AonC#", "Bm7", "G"]
        
        # sequence_match should return 0.0 (not all match)
        sequence_result = evaluator.sequence_match(predicted, ground_truth)
        assert sequence_result == 0.0
        
        # exact_match_rate should return 0.75 (3 out of 4 match)
        exact_match_result = evaluator.exact_match_rate(predicted, ground_truth)
        assert exact_match_result == 0.75
