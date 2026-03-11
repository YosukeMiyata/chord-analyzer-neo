"""Data models for the evaluation system with validation logic."""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ChordAnnotation:
    """Chord annotation with position information.
    
    Attributes:
        chord: Chord name (e.g., "D", "AonC#", "Bm7")
        position: Character position or bar number (non-negative)
        timestamp: Optional time in seconds (non-negative)
    
    Validates: Requirements 13.1, 13.2
    """
    chord: str
    position: int
    timestamp: float = 0.0
    
    def __post_init__(self):
        """Validate ChordAnnotation fields."""
        if not self.chord or not isinstance(self.chord, str):
            raise ValueError("chord field must be a non-empty string")
        
        if not isinstance(self.position, int) or self.position < 0:
            raise ValueError("position must be a non-negative integer")
        
        if not isinstance(self.timestamp, (int, float)) or self.timestamp < 0:
            raise ValueError("timestamp must be a non-negative number")


@dataclass
class EvaluationMetrics:
    """Evaluation metrics for chord recognition accuracy.
    
    Attributes:
        sequence_accuracy: Exact sequence match rate (0.0 to 1.0)
        root_accuracy: Root note accuracy (0.0 to 1.0)
        quality_accuracy: Chord quality accuracy (0.0 to 1.0)
        dtw_distance: Dynamic Time Warping distance (non-negative)
        exact_match_rate: Exact chord match rate (0.0 to 1.0)
    
    Validates: Requirements 13.3, 13.4
    """
    sequence_accuracy: float
    root_accuracy: float
    quality_accuracy: float
    dtw_distance: float
    exact_match_rate: float
    
    def __post_init__(self):
        """Validate EvaluationMetrics fields."""
        accuracy_fields = [
            ("sequence_accuracy", self.sequence_accuracy),
            ("root_accuracy", self.root_accuracy),
            ("quality_accuracy", self.quality_accuracy),
            ("exact_match_rate", self.exact_match_rate),
        ]
        
        for field_name, value in accuracy_fields:
            if not isinstance(value, (int, float)):
                raise ValueError(f"{field_name} must be a number")
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{field_name} must be in range [0.0, 1.0], got {value}")
        
        if not isinstance(self.dtw_distance, (int, float)):
            raise ValueError("dtw_distance must be a number")
        if self.dtw_distance < 0:
            raise ValueError(f"dtw_distance must be non-negative, got {self.dtw_distance}")


@dataclass
class BenchmarkResult:
    """Result of benchmarking a single song.
    
    Attributes:
        song_name: Name of the song (non-empty)
        metrics: Evaluation metrics for the song
        predicted_chords: List of predicted chords (non-empty)
        ground_truth_chords: List of ground truth chords (non-empty)
        processing_time: Time taken to process in seconds (non-negative)
    
    Validates: Requirements 13.5
    """
    song_name: str
    metrics: EvaluationMetrics
    predicted_chords: List[str]
    ground_truth_chords: List[str]
    processing_time: float = 0.0
    
    def __post_init__(self):
        """Validate BenchmarkResult fields."""
        if not self.song_name or not isinstance(self.song_name, str):
            raise ValueError("song_name must be a non-empty string")
        
        if not isinstance(self.metrics, EvaluationMetrics):
            raise ValueError("metrics must be an EvaluationMetrics instance")
        
        if not isinstance(self.predicted_chords, list) or len(self.predicted_chords) == 0:
            raise ValueError("predicted_chords must be a non-empty list")
        
        if not isinstance(self.ground_truth_chords, list) or len(self.ground_truth_chords) == 0:
            raise ValueError("ground_truth_chords must be a non-empty list")
        
        if not isinstance(self.processing_time, (int, float)) or self.processing_time < 0:
            raise ValueError("processing_time must be a non-negative number")


@dataclass
class OptimizationConfig:
    """Configuration for parameter optimization.
    
    Attributes:
        penalty_range: Tuple of (min, max) for penalty parameter
        grouping_threshold_range: Tuple of (min, max) for grouping threshold
        optimization_metric: Name of metric to optimize (e.g., 'root_accuracy')
    """
    penalty_range: Tuple[float, float]
    grouping_threshold_range: Tuple[float, float]
    optimization_metric: str
    
    def __post_init__(self):
        """Validate OptimizationConfig fields."""
        if not isinstance(self.penalty_range, tuple) or len(self.penalty_range) != 2:
            raise ValueError("penalty_range must be a tuple of (min, max)")
        
        if self.penalty_range[0] > self.penalty_range[1]:
            raise ValueError("penalty_range min must be <= max")
        
        if not isinstance(self.grouping_threshold_range, tuple) or len(self.grouping_threshold_range) != 2:
            raise ValueError("grouping_threshold_range must be a tuple of (min, max)")
        
        if self.grouping_threshold_range[0] > self.grouping_threshold_range[1]:
            raise ValueError("grouping_threshold_range min must be <= max")
        
        if not self.optimization_metric or not isinstance(self.optimization_metric, str):
            raise ValueError("optimization_metric must be a non-empty string")


@dataclass
class OptimizedParameters:
    """Result of parameter optimization.
    
    Attributes:
        maj7_penalty: Optimized penalty value for maj7 chords
        grouping_threshold: Optimized grouping threshold
        achieved_metric: Metric value achieved with optimized parameters
    """
    maj7_penalty: float
    grouping_threshold: float
    achieved_metric: float
    
    def __post_init__(self):
        """Validate OptimizedParameters fields."""
        if not isinstance(self.maj7_penalty, (int, float)):
            raise ValueError("maj7_penalty must be a number")
        
        if not isinstance(self.grouping_threshold, (int, float)):
            raise ValueError("grouping_threshold must be a number")
        
        if not isinstance(self.achieved_metric, (int, float)):
            raise ValueError("achieved_metric must be a number")
