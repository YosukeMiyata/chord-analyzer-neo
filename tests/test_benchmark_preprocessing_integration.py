"""Integration tests for BenchmarkTool preprocessing functionality.

This module tests:
- Setting preprocessing pipeline
- Preprocessing application during benchmark execution
- Temporary preprocessing override

Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from src.evaluation.benchmark import BenchmarkTool
from src.evaluation.preprocessing import (
    PreprocessingPipeline,
    PreprocessingConfig,
    NormalizationMode,
    AggregationStrategy
)


class TestBenchmarkToolPreprocessingIntegration:
    """Test preprocessing integration with BenchmarkTool."""
    
    def test_set_preprocessing_pipeline(self):
        """Test setting preprocessing pipeline on BenchmarkTool.
        
        Validates: Requirement 4.1
        """
        tool = BenchmarkTool()
        
        # Initially, no pipeline should be set
        assert tool.preprocessing_pipeline is None
        
        # Create and set a pipeline
        config = PreprocessingConfig(
            enable_normalization=True,
            enable_aggregation=True
        )
        pipeline = PreprocessingPipeline(config)
        
        tool.set_preprocessing_pipeline(pipeline)
        
        # Verify pipeline is set
        assert tool.preprocessing_pipeline is pipeline
    
    def test_set_preprocessing_pipeline_to_none(self):
        """Test disabling preprocessing by setting pipeline to None.
        
        Validates: Requirement 4.1, 4.3
        """
        tool = BenchmarkTool()
        
        # Set a pipeline first
        config = PreprocessingConfig()
        pipeline = PreprocessingPipeline(config)
        tool.set_preprocessing_pipeline(pipeline)
        
        # Now disable it
        tool.set_preprocessing_pipeline(None)
        
        # Verify pipeline is disabled
        assert tool.preprocessing_pipeline is None
    
    def test_no_preprocessing_by_default(self):
        """Test that preprocessing is disabled by default.
        
        Validates: Requirement 4.3
        """
        tool = BenchmarkTool()
        
        # Verify no preprocessing pipeline is set by default
        assert tool.preprocessing_pipeline is None
    
    def test_run_benchmark_with_preprocessing_override_disable(self, tmp_path):
        """Test temporarily disabling preprocessing for a benchmark run.
        
        Validates: Requirement 4.4
        """
        tool = BenchmarkTool()
        
        # Set up a preprocessing pipeline
        config = PreprocessingConfig()
        pipeline = PreprocessingPipeline(config)
        tool.set_preprocessing_pipeline(pipeline)
        
        # Create empty test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Mock discover_file_pairs to return empty list
        with patch.object(tool, 'discover_file_pairs', return_value=[]):
            # Run benchmark with preprocessing disabled
            results = tool.run_benchmark(audio_dir, gt_dir, enable_preprocessing=False)
        
        # Verify pipeline is still set after the run (restored)
        assert tool.preprocessing_pipeline is pipeline
    
    def test_run_benchmark_with_preprocessing_override_enable(self, tmp_path):
        """Test temporarily enabling preprocessing for a benchmark run.
        
        Validates: Requirement 4.4
        """
        tool = BenchmarkTool()
        
        # Don't set a pipeline initially
        assert tool.preprocessing_pipeline is None
        
        # Create empty test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Mock discover_file_pairs to return empty list
        with patch.object(tool, 'discover_file_pairs', return_value=[]):
            # Run benchmark with preprocessing enabled (should log warning)
            results = tool.run_benchmark(audio_dir, gt_dir, enable_preprocessing=True)
        
        # Verify pipeline is still None after the run (restored)
        assert tool.preprocessing_pipeline is None
    
    def test_run_benchmark_respects_pipeline_configuration(self, tmp_path):
        """Test that run_benchmark uses configured pipeline when no override is provided.
        
        Validates: Requirement 4.2, 4.3
        """
        tool = BenchmarkTool()
        
        # Set up a preprocessing pipeline
        config = PreprocessingConfig()
        pipeline = PreprocessingPipeline(config)
        tool.set_preprocessing_pipeline(pipeline)
        
        # Create empty test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Mock discover_file_pairs to return empty list
        with patch.object(tool, 'discover_file_pairs', return_value=[]):
            # Run benchmark without override (should use configured pipeline)
            results = tool.run_benchmark(audio_dir, gt_dir)
        
        # Verify pipeline is still set
        assert tool.preprocessing_pipeline is pipeline


class TestBenchmarkToolPreprocessingApplication:
    """Test that preprocessing is actually applied during song processing."""
    
    @patch('src.audio_engine.AudioProcessingEngine')
    def test_preprocessing_applied_in_process_single_song(self, mock_audio_engine_class, tmp_path):
        """Test that preprocessing is applied when processing a single song.
        
        Validates: Requirement 4.2, 4.5
        """
        # Create test files
        audio_file = tmp_path / "test.mp3"
        gt_file = tmp_path / "test.txt"
        audio_file.touch()
        gt_file.write_text("[C][D]")  # Use bracketed chord format
        
        # Set up BenchmarkTool with preprocessing
        tool = BenchmarkTool()
        config = PreprocessingConfig(
            enable_normalization=True,
            enable_aggregation=False  # Disable aggregation for simpler test
        )
        pipeline = PreprocessingPipeline(config)
        tool.set_preprocessing_pipeline(pipeline)
        
        # Mock audio engine to return predicted chords
        mock_engine = MagicMock()
        mock_audio_engine_class.return_value = mock_engine
        
        # Create mock chord segments
        mock_segment1 = Mock()
        mock_segment1.__str__ = Mock(return_value="C maj")
        mock_segment1.start_time = 0.0
        
        mock_segment2 = Mock()
        mock_segment2.__str__ = Mock(return_value="D min")
        mock_segment2.start_time = 1.0
        
        # Mock analysis result
        mock_result = Mock()
        mock_result.chord_progression = [mock_segment1, mock_segment2]
        mock_engine.analyze_audio.return_value = mock_result
        
        # Process the song
        result = tool.process_single_song(audio_file, gt_file)
        
        # Verify preprocessing was applied (chords should be normalized)
        # "C maj" should become "CM", "D min" should become "Dm"
        assert "CM" in result.predicted_chords or "C" in result.predicted_chords
        assert "Dm" in result.predicted_chords or "D" in result.predicted_chords
    
    @patch('src.audio_engine.AudioProcessingEngine')
    def test_no_preprocessing_when_pipeline_not_set(self, mock_audio_engine_class, tmp_path):
        """Test that no preprocessing is applied when pipeline is not set.
        
        Validates: Requirement 4.3
        """
        # Create test files
        audio_file = tmp_path / "test.mp3"
        gt_file = tmp_path / "test.txt"
        audio_file.touch()
        gt_file.write_text("[C][D]")  # Use bracketed chord format
        
        # Set up BenchmarkTool WITHOUT preprocessing
        tool = BenchmarkTool()
        assert tool.preprocessing_pipeline is None
        
        # Mock audio engine to return predicted chords
        mock_engine = MagicMock()
        mock_audio_engine_class.return_value = mock_engine
        
        # Create mock chord segments
        mock_segment1 = Mock()
        mock_segment1.__str__ = Mock(return_value="C maj")
        mock_segment1.start_time = 0.0
        
        mock_segment2 = Mock()
        mock_segment2.__str__ = Mock(return_value="D min")
        mock_segment2.start_time = 1.0
        
        # Mock analysis result
        mock_result = Mock()
        mock_result.chord_progression = [mock_segment1, mock_segment2]
        mock_engine.analyze_audio.return_value = mock_result
        
        # Process the song
        result = tool.process_single_song(audio_file, gt_file)
        
        # Verify no preprocessing was applied (chords should be unchanged)
        assert "C maj" in result.predicted_chords
        assert "D min" in result.predicted_chords


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
