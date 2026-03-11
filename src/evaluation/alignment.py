"""Sequence alignment utilities for the evaluation system.

This module provides functions for aligning predicted and ground truth chord
sequences when they have different lengths. The alignment uses Dynamic Time
Warping (DTW) to find the optimal alignment path that minimizes distortion.

Validates: Requirements 10.1, 10.2, 10.3, 10.4
"""

from typing import List, Tuple
import numpy as np
from src.evaluation.chord_utils import chord_distance


def align_sequences(
    predicted: List[str],
    ground_truth: List[str]
) -> Tuple[List[str], List[str]]:
    """Align predicted and ground truth chord sequences to the same length.
    
    This function uses Dynamic Time Warping (DTW) to find the optimal alignment
    path between two chord sequences of potentially different lengths. The
    alignment minimizes distortion by using the chord_distance function to
    measure similarity between chords.
    
    The function returns two aligned sequences of the same length, where chords
    may be repeated to match the optimal alignment path. The original sequences
    are preserved (not modified).
    
    Args:
        predicted: List of predicted chord names
        ground_truth: List of ground truth chord names
        
    Returns:
        Tuple of (aligned_predicted, aligned_ground_truth) where both lists
        have the same length
        
    Examples:
        >>> align_sequences(["D", "A", "G"], ["D", "A", "Bm7", "G"])
        (["D", "A", "A", "G"], ["D", "A", "Bm7", "G"])
        
        >>> align_sequences(["D", "A"], ["D", "A"])
        (["D", "A"], ["D", "A"])
        
    Validates: Requirements 10.1, 10.2, 10.3, 10.4
    """
    # Handle empty sequences
    if not predicted and not ground_truth:
        return [], []
    if not predicted:
        # If predicted is empty, we can't meaningfully align
        # Return empty for both to indicate no valid comparison
        return [], []
    if not ground_truth:
        # If ground truth is empty, we can't meaningfully align
        # Return empty for both to indicate no valid comparison
        return [], []
    
    # If sequences already have the same length, return copies
    if len(predicted) == len(ground_truth):
        return predicted.copy(), ground_truth.copy()
    
    n = len(predicted)
    m = len(ground_truth)
    
    # Initialize DTW matrix with infinity
    dtw_matrix = np.full((n + 1, m + 1), np.inf)
    dtw_matrix[0, 0] = 0.0
    
    # Fill DTW matrix using dynamic programming
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Calculate cost using chord_distance
            cost = chord_distance(predicted[i-1], ground_truth[j-1])
            
            # Find minimum path: insertion, deletion, or match
            dtw_matrix[i, j] = cost + min(
                dtw_matrix[i-1, j],      # Deletion (skip predicted chord)
                dtw_matrix[i, j-1],      # Insertion (skip ground truth chord)
                dtw_matrix[i-1, j-1]     # Match (align both chords)
            )
    
    # Backtrack to find the optimal alignment path
    aligned_predicted = []
    aligned_ground_truth = []
    
    i, j = n, m
    while i > 0 or j > 0:
        if i == 0:
            # Only ground truth chords left - insert them
            aligned_ground_truth.append(ground_truth[j-1])
            # Repeat the last predicted chord or use the first one
            aligned_predicted.append(predicted[0] if predicted else ground_truth[j-1])
            j -= 1
        elif j == 0:
            # Only predicted chords left - insert them
            aligned_predicted.append(predicted[i-1])
            # Repeat the last ground truth chord or use the first one
            aligned_ground_truth.append(ground_truth[0] if ground_truth else predicted[i-1])
            i -= 1
        else:
            # Find which direction we came from (minimum cost path)
            cost_match = dtw_matrix[i-1, j-1]
            cost_deletion = dtw_matrix[i-1, j]
            cost_insertion = dtw_matrix[i, j-1]
            
            min_cost = min(cost_match, cost_deletion, cost_insertion)
            
            if min_cost == cost_match:
                # Match: align both chords
                aligned_predicted.append(predicted[i-1])
                aligned_ground_truth.append(ground_truth[j-1])
                i -= 1
                j -= 1
            elif min_cost == cost_deletion:
                # Deletion: skip predicted chord (repeat ground truth)
                aligned_predicted.append(predicted[i-1])
                # Repeat the current ground truth chord
                aligned_ground_truth.append(ground_truth[j] if j < m else ground_truth[j-1])
                i -= 1
            else:
                # Insertion: skip ground truth chord (repeat predicted)
                aligned_ground_truth.append(ground_truth[j-1])
                # Repeat the current predicted chord
                aligned_predicted.append(predicted[i] if i < n else predicted[i-1])
                j -= 1
    
    # Reverse the sequences (we built them backwards)
    aligned_predicted.reverse()
    aligned_ground_truth.reverse()
    
    return aligned_predicted, aligned_ground_truth
