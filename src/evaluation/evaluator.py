"""Evaluator for chord recognition accuracy metrics.

This module provides the Evaluator class for calculating various accuracy metrics
by comparing predicted chord sequences against ground truth sequences.
"""

from typing import List
from src.evaluation.models import EvaluationMetrics


class Evaluator:
    """Evaluator for chord recognition accuracy.
    
    Calculates multiple evaluation metrics including sequence accuracy,
    root accuracy, quality accuracy, DTW distance, and exact match rate.
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
    """
    
    def sequence_match(
        self,
        predicted: List[str],
        ground_truth: List[str]
    ) -> float:
        """Calculate sequence matching accuracy.
        
        Compares two chord sequences for exact matching. Returns 1.0 if the
        sequences match exactly in order and content, 0.0 otherwise.
        
        Args:
            predicted: List of predicted chord names
            ground_truth: List of ground truth chord names
        
        Returns:
            float: 1.0 if sequences match exactly, 0.0 otherwise
        
        Validates: Requirements 2.1
        
        Examples:
            >>> evaluator = Evaluator()
            >>> evaluator.sequence_match(["D", "A", "Bm7", "G"], ["D", "A", "Bm7", "G"])
            1.0
            >>> evaluator.sequence_match(["D", "A", "Bm7", "G"], ["D", "AonC#", "Bm7", "G"])
            0.0
        """
        # Check if sequences have the same length
        if len(predicted) != len(ground_truth):
            return 0.0
        
        # Check if all chords match exactly
        if predicted == ground_truth:
            return 1.0
        
        return 0.0


    def root_accuracy(
        self,
        predicted: List[str],
        ground_truth: List[str]
    ) -> float:
        """Calculate root note accuracy.

        Compares root notes between predicted and ground truth chord sequences.
        Uses the extract_root utility to extract root notes from each chord,
        then calculates the percentage of matching root notes.

        Args:
            predicted: List of predicted chord names
            ground_truth: List of ground truth chord names

        Returns:
            float: Accuracy in range [0.0, 1.0] representing the percentage
                   of matching root notes

        Validates: Requirements 2.2, 3.1, 3.2, 3.3, 3.4

        Examples:
            >>> evaluator = Evaluator()
            >>> evaluator.root_accuracy(["D", "A", "Bm7", "G"], ["D", "AonC#", "Bm7", "G"])
            1.0
            >>> evaluator.root_accuracy(["D", "A", "Bm7", "G"], ["C", "F", "Em", "Am"])
            0.0
            >>> evaluator.root_accuracy(["D", "A"], ["D", "F"])
            0.5
        """
        from src.evaluation.chord_utils import extract_root

        # Handle empty sequences
        if not predicted or not ground_truth:
            return 0.0

        # Sequences must have the same length for comparison
        if len(predicted) != len(ground_truth):
            return 0.0

        # Count matching root notes
        matches = 0
        for pred_chord, gt_chord in zip(predicted, ground_truth):
            try:
                pred_root = extract_root(pred_chord)
                gt_root = extract_root(gt_chord)

                if pred_root == gt_root:
                    matches += 1
            except ValueError:
                # If we can't extract root from either chord, count as mismatch
                continue

        # Calculate accuracy as percentage of matches
        accuracy = matches / len(predicted)
        return accuracy

    def quality_accuracy(
        self,
        predicted: List[str],
        ground_truth: List[str]
    ) -> float:
        """Calculate chord quality accuracy.

        Compares chord qualities between predicted and ground truth chord sequences.
        Uses the identify_quality utility to identify the quality of each chord,
        then calculates the percentage of matching qualities.

        Args:
            predicted: List of predicted chord names
            ground_truth: List of ground truth chord names

        Returns:
            float: Accuracy in range [0.0, 1.0] representing the percentage
                   of matching chord qualities

        Validates: Requirements 2.3, 4.1, 4.2, 4.3, 4.4

        Examples:
            >>> evaluator = Evaluator()
            >>> evaluator.quality_accuracy(["D", "Am", "D7", "Cmaj7"], ["D", "Am", "D7", "Cmaj7"])
            1.0
            >>> evaluator.quality_accuracy(["D", "Am"], ["Dm", "A"])
            0.0
            >>> evaluator.quality_accuracy(["D", "Am", "D7"], ["Dm", "Am", "D7"])
            0.6666666666666666
        """
        from src.evaluation.chord_utils import identify_quality

        # Handle empty sequences
        if not predicted or not ground_truth:
            return 0.0

        # Sequences must have the same length for comparison
        if len(predicted) != len(ground_truth):
            return 0.0

        # Count matching qualities
        matches = 0
        for pred_chord, gt_chord in zip(predicted, ground_truth):
            try:
                pred_quality = identify_quality(pred_chord)
                gt_quality = identify_quality(gt_chord)

                if pred_quality == gt_quality:
                    matches += 1
            except ValueError:
                # If we can't identify quality from either chord, count as mismatch
                continue

        # Calculate accuracy as percentage of matches
        accuracy = matches / len(predicted)
        return accuracy

    def exact_match_rate(
        self,
        predicted: List[str],
        ground_truth: List[str]
    ) -> float:
        """Calculate exact match rate.

        Counts the number of exact chord matches between predicted and ground truth
        sequences, then calculates the match rate as a percentage. This is different
        from sequence_match which requires ALL chords to match - exact_match_rate
        calculates the percentage of individual chords that match exactly.

        Args:
            predicted: List of predicted chord names
            ground_truth: List of ground truth chord names

        Returns:
            float: Match rate in range [0.0, 1.0] representing the percentage
                   of exact chord matches

        Validates: Requirements 2.5

        Examples:
            >>> evaluator = Evaluator()
            >>> evaluator.exact_match_rate(["D", "A", "Bm7", "G"], ["D", "AonC#", "Bm7", "G"])
            0.75
            >>> evaluator.exact_match_rate(["D", "A", "Bm7", "G"], ["D", "A", "Bm7", "G"])
            1.0
            >>> evaluator.exact_match_rate(["D", "A"], ["C", "F"])
            0.0
        """
        # Handle empty sequences
        if not predicted or not ground_truth:
            return 0.0

        # Sequences must have the same length for comparison
        if len(predicted) != len(ground_truth):
            return 0.0

        # Count exact matches
        matches = 0
        for pred_chord, gt_chord in zip(predicted, ground_truth):
            if pred_chord == gt_chord:
                matches += 1

        # Calculate match rate as percentage of matches
        match_rate = matches / len(predicted)
        return match_rate



