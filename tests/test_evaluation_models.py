"""Unit tests for evaluation system data models."""

import pytest
from src.evaluation.models import (
    ChordAnnotation,
    EvaluationMetrics,
    BenchmarkResult,
    OptimizationConfig,
    OptimizedParameters,
)


class TestChordAnnotation:
    """Tests for ChordAnnotation validation."""
    
    def test_valid_chord_annotation(self):
        """Test creating a valid ChordAnnotation."""
        annotation = ChordAnnotation(chord="D", position=0, timestamp=1.5)
        assert annotation.chord == "D"
        assert annotation.position == 0
        assert annotation.timestamp == 1.5
    
    def test_chord_annotation_default_timestamp(self):
        """Test ChordAnnotation with default timestamp."""
        annotation = ChordAnnotation(chord="Am", position=5)
        assert annotation.timestamp == 0.0
    
    def test_empty_chord_raises_error(self):
        """Test that empty chord string raises ValueError."""
        with pytest.raises(ValueError, match="chord field must be a non-empty string"):
            ChordAnnotation(chord="", position=0)
    
    def test_negative_position_raises_error(self):
        """Test that negative position raises ValueError."""
        with pytest.raises(ValueError, match="position must be a non-negative integer"):
            ChordAnnotation(chord="D", position=-1)
    
    def test_negative_timestamp_raises_error(self):
        """Test that negative timestamp raises ValueError."""
        with pytest.raises(ValueError, match="timestamp must be a non-negative number"):
            ChordAnnotation(chord="D", position=0, timestamp=-1.0)
    
    def test_non_string_chord_raises_error(self):
        """Test that non-string chord raises ValueError."""
        with pytest.raises(ValueError, match="chord field must be a non-empty string"):
            ChordAnnotation(chord=None, position=0)


class TestEvaluationMetrics:
    """Tests for EvaluationMetrics validation."""
    
    def test_valid_evaluation_metrics(self):
        """Test creating valid EvaluationMetrics."""
        metrics = EvaluationMetrics(
            sequence_accuracy=0.95,
            root_accuracy=0.98,
            quality_accuracy=0.92,
            dtw_distance=0.15,
            exact_match_rate=0.90
        )
        assert metrics.sequence_accuracy == 0.95
        assert metrics.root_accuracy == 0.98
        assert metrics.quality_accuracy == 0.92
        assert metrics.dtw_distance == 0.15
        assert metrics.exact_match_rate == 0.90
    
    def test_perfect_scores(self):
        """Test metrics with perfect scores."""
        metrics = EvaluationMetrics(
            sequence_accuracy=1.0,
            root_accuracy=1.0,
            quality_accuracy=1.0,
            dtw_distance=0.0,
            exact_match_rate=1.0
        )
        assert metrics.sequence_accuracy == 1.0
        assert metrics.dtw_distance == 0.0
    
    def test_sequence_accuracy_above_range_raises_error(self):
        """Test that sequence_accuracy > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="sequence_accuracy must be in range"):
            EvaluationMetrics(
                sequence_accuracy=1.5,
                root_accuracy=0.9,
                quality_accuracy=0.9,
                dtw_distance=0.1,
                exact_match_rate=0.9
            )
    
    def test_root_accuracy_below_range_raises_error(self):
        """Test that root_accuracy < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="root_accuracy must be in range"):
            EvaluationMetrics(
                sequence_accuracy=0.9,
                root_accuracy=-0.1,
                quality_accuracy=0.9,
                dtw_distance=0.1,
                exact_match_rate=0.9
            )
    
    def test_negative_dtw_distance_raises_error(self):
        """Test that negative dtw_distance raises ValueError."""
        with pytest.raises(ValueError, match="dtw_distance must be non-negative"):
            EvaluationMetrics(
                sequence_accuracy=0.9,
                root_accuracy=0.9,
                quality_accuracy=0.9,
                dtw_distance=-0.5,
                exact_match_rate=0.9
            )
    
    def test_quality_accuracy_above_range_raises_error(self):
        """Test that quality_accuracy > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="quality_accuracy must be in range"):
            EvaluationMetrics(
                sequence_accuracy=0.9,
                root_accuracy=0.9,
                quality_accuracy=1.1,
                dtw_distance=0.1,
                exact_match_rate=0.9
            )
    
    def test_exact_match_rate_below_range_raises_error(self):
        """Test that exact_match_rate < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="exact_match_rate must be in range"):
            EvaluationMetrics(
                sequence_accuracy=0.9,
                root_accuracy=0.9,
                quality_accuracy=0.9,
                dtw_distance=0.1,
                exact_match_rate=-0.1
            )


class TestBenchmarkResult:
    """Tests for BenchmarkResult validation."""
    
    def test_valid_benchmark_result(self):
        """Test creating a valid BenchmarkResult."""
        metrics = EvaluationMetrics(
            sequence_accuracy=0.95,
            root_accuracy=0.98,
            quality_accuracy=0.92,
            dtw_distance=0.15,
            exact_match_rate=0.90
        )
        result = BenchmarkResult(
            song_name="test_song",
            metrics=metrics,
            predicted_chords=["D", "A", "Bm"],
            ground_truth_chords=["D", "A", "Bm7"],
            processing_time=2.5
        )
        assert result.song_name == "test_song"
        assert result.metrics == metrics
        assert len(result.predicted_chords) == 3
        assert len(result.ground_truth_chords) == 3
        assert result.processing_time == 2.5
    
    def test_benchmark_result_default_processing_time(self):
        """Test BenchmarkResult with default processing_time."""
        metrics = EvaluationMetrics(
            sequence_accuracy=0.95,
            root_accuracy=0.98,
            quality_accuracy=0.92,
            dtw_distance=0.15,
            exact_match_rate=0.90
        )
        result = BenchmarkResult(
            song_name="test_song",
            metrics=metrics,
            predicted_chords=["D"],
            ground_truth_chords=["D"]
        )
        assert result.processing_time == 0.0
    
    def test_empty_song_name_raises_error(self):
        """Test that empty song_name raises ValueError."""
        metrics = EvaluationMetrics(
            sequence_accuracy=0.95,
            root_accuracy=0.98,
            quality_accuracy=0.92,
            dtw_distance=0.15,
            exact_match_rate=0.90
        )
        with pytest.raises(ValueError, match="song_name must be a non-empty string"):
            BenchmarkResult(
                song_name="",
                metrics=metrics,
                predicted_chords=["D"],
                ground_truth_chords=["D"]
            )
    
    def test_empty_predicted_chords_raises_error(self):
        """Test that empty predicted_chords raises ValueError."""
        metrics = EvaluationMetrics(
            sequence_accuracy=0.95,
            root_accuracy=0.98,
            quality_accuracy=0.92,
            dtw_distance=0.15,
            exact_match_rate=0.90
        )
        with pytest.raises(ValueError, match="predicted_chords must be a non-empty list"):
            BenchmarkResult(
                song_name="test_song",
                metrics=metrics,
                predicted_chords=[],
                ground_truth_chords=["D"]
            )
    
    def test_empty_ground_truth_chords_raises_error(self):
        """Test that empty ground_truth_chords raises ValueError."""
        metrics = EvaluationMetrics(
            sequence_accuracy=0.95,
            root_accuracy=0.98,
            quality_accuracy=0.92,
            dtw_distance=0.15,
            exact_match_rate=0.90
        )
        with pytest.raises(ValueError, match="ground_truth_chords must be a non-empty list"):
            BenchmarkResult(
                song_name="test_song",
                metrics=metrics,
                predicted_chords=["D"],
                ground_truth_chords=[]
            )
    
    def test_negative_processing_time_raises_error(self):
        """Test that negative processing_time raises ValueError."""
        metrics = EvaluationMetrics(
            sequence_accuracy=0.95,
            root_accuracy=0.98,
            quality_accuracy=0.92,
            dtw_distance=0.15,
            exact_match_rate=0.90
        )
        with pytest.raises(ValueError, match="processing_time must be a non-negative number"):
            BenchmarkResult(
                song_name="test_song",
                metrics=metrics,
                predicted_chords=["D"],
                ground_truth_chords=["D"],
                processing_time=-1.0
            )


class TestOptimizationConfig:
    """Tests for OptimizationConfig validation."""
    
    def test_valid_optimization_config(self):
        """Test creating a valid OptimizationConfig."""
        config = OptimizationConfig(
            penalty_range=(0.0, 0.3),
            grouping_threshold_range=(1.0, 2.0),
            optimization_metric="root_accuracy"
        )
        assert config.penalty_range == (0.0, 0.3)
        assert config.grouping_threshold_range == (1.0, 2.0)
        assert config.optimization_metric == "root_accuracy"
    
    def test_invalid_penalty_range_raises_error(self):
        """Test that invalid penalty_range raises ValueError."""
        with pytest.raises(ValueError, match="penalty_range min must be <= max"):
            OptimizationConfig(
                penalty_range=(0.5, 0.1),
                grouping_threshold_range=(1.0, 2.0),
                optimization_metric="root_accuracy"
            )
    
    def test_invalid_grouping_threshold_range_raises_error(self):
        """Test that invalid grouping_threshold_range raises ValueError."""
        with pytest.raises(ValueError, match="grouping_threshold_range min must be <= max"):
            OptimizationConfig(
                penalty_range=(0.0, 0.3),
                grouping_threshold_range=(2.0, 1.0),
                optimization_metric="root_accuracy"
            )
    
    def test_empty_optimization_metric_raises_error(self):
        """Test that empty optimization_metric raises ValueError."""
        with pytest.raises(ValueError, match="optimization_metric must be a non-empty string"):
            OptimizationConfig(
                penalty_range=(0.0, 0.3),
                grouping_threshold_range=(1.0, 2.0),
                optimization_metric=""
            )


class TestOptimizedParameters:
    """Tests for OptimizedParameters validation."""
    
    def test_valid_optimized_parameters(self):
        """Test creating valid OptimizedParameters."""
        params = OptimizedParameters(
            maj7_penalty=0.15,
            grouping_threshold=1.5,
            achieved_metric=0.95
        )
        assert params.maj7_penalty == 0.15
        assert params.grouping_threshold == 1.5
        assert params.achieved_metric == 0.95
    
    def test_non_numeric_maj7_penalty_raises_error(self):
        """Test that non-numeric maj7_penalty raises ValueError."""
        with pytest.raises(ValueError, match="maj7_penalty must be a number"):
            OptimizedParameters(
                maj7_penalty="invalid",
                grouping_threshold=1.5,
                achieved_metric=0.95
            )
    
    def test_non_numeric_grouping_threshold_raises_error(self):
        """Test that non-numeric grouping_threshold raises ValueError."""
        with pytest.raises(ValueError, match="grouping_threshold must be a number"):
            OptimizedParameters(
                maj7_penalty=0.15,
                grouping_threshold="invalid",
                achieved_metric=0.95
            )
    
    def test_non_numeric_achieved_metric_raises_error(self):
        """Test that non-numeric achieved_metric raises ValueError."""
        with pytest.raises(ValueError, match="achieved_metric must be a number"):
            OptimizedParameters(
                maj7_penalty=0.15,
                grouping_threshold=1.5,
                achieved_metric="invalid"
            )
