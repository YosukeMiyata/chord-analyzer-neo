"""Tests for _chordai_recognition method (Task 6.2)

These tests verify that the _chordai_recognition method correctly:
- Accepts audio and sample_rate parameters
- Calls inference_engine.predict_chords with audio
- Maps ChordPrediction objects to ChordSegment objects
- Returns list of ChordSegment objects
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.chord_estimation import ChordEstimationModule
from src.chordai_models import ChordPrediction
from src.models import ChordSegment, ChordQuality


class TestChordAIRecognitionMethod:
    """Test _chordai_recognition method in ChordEstimationModule"""
    
    def test_chordai_recognition_accepts_parameters(self):
        """Test that _chordai_recognition accepts audio and sample_rate parameters"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine') as mock_engine_class:
                    # Setup mocks
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    mock_engine = Mock()
                    mock_engine.predict_chords.return_value = []
                    mock_engine_class.return_value = mock_engine
                    
                    estimator = ChordEstimationModule()
                    
                    # Create test audio
                    audio = np.random.rand(22050)
                    sample_rate = 22050
                    
                    # Call method
                    result = estimator._chordai_recognition(audio, sample_rate)
                    
                    # Verify it returns a list
                    assert isinstance(result, list)
    
    def test_chordai_recognition_calls_inference_engine(self):
        """Test that _chordai_recognition calls inference_engine.predict_chords"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine') as mock_engine_class:
                    # Setup mocks
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    mock_engine = Mock()
                    mock_engine.predict_chords.return_value = []
                    mock_engine_class.return_value = mock_engine
                    
                    estimator = ChordEstimationModule()
                    
                    # Create test audio
                    audio = np.random.rand(22050)
                    sample_rate = 22050
                    
                    # Call method
                    estimator._chordai_recognition(audio, sample_rate)
                    
                    # Verify inference engine was called with correct parameters
                    mock_engine.predict_chords.assert_called_once_with(
                        audio=audio,
                        sample_rate=sample_rate,
                        frame_duration=estimator.frame_duration
                    )
    
    def test_chordai_recognition_passes_chroma_unchanged(self):
        """Test that audio is passed unchanged to inference engine"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine') as mock_engine_class:
                    # Setup mocks
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    mock_engine = Mock()
                    mock_engine.predict_chords.return_value = []
                    mock_engine_class.return_value = mock_engine
                    
                    estimator = ChordEstimationModule()
                    
                    # Create test audio with specific values
                    audio = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
                    sample_rate = 22050
                    
                    # Call method
                    estimator._chordai_recognition(audio, sample_rate)
                    
                    # Verify audio was passed unchanged
                    call_args = mock_engine.predict_chords.call_args
                    passed_audio = call_args.kwargs['audio']
                    np.testing.assert_array_equal(passed_audio, audio)
    
    def test_chordai_recognition_maps_predictions_to_segments(self):
        """Test that ChordPrediction objects are mapped to ChordSegment objects"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine') as mock_engine_class:
                    # Setup mocks
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    # Create mock predictions
                    predictions = [
                        ChordPrediction(0.0, 0.5, "C", "maj", None, 0.95),
                        ChordPrediction(0.5, 1.0, "G", "maj", None, 0.90),
                        ChordPrediction(1.0, 1.5, "Am", "min", None, 0.85)
                    ]
                    
                    mock_engine = Mock()
                    mock_engine.predict_chords.return_value = predictions
                    mock_engine_class.return_value = mock_engine
                    
                    estimator = ChordEstimationModule()
                    
                    # Create test audio
                    audio = np.random.rand(22050)
                    sample_rate = 22050
                    
                    # Call method
                    result = estimator._chordai_recognition(audio, sample_rate)
                    
                    # Verify result is a list of ChordSegment objects
                    assert isinstance(result, list)
                    assert len(result) == 3
                    assert all(isinstance(seg, ChordSegment) for seg in result)
    
    def test_chordai_recognition_returns_chord_segments(self):
        """Test that _chordai_recognition returns list of ChordSegment objects"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine') as mock_engine_class:
                    # Setup mocks
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    # Create mock predictions
                    predictions = [
                        ChordPrediction(0.0, 0.5, "C", "maj", None, 0.95),
                        ChordPrediction(0.5, 1.0, "D", "min", None, 0.90)
                    ]
                    
                    mock_engine = Mock()
                    mock_engine.predict_chords.return_value = predictions
                    mock_engine_class.return_value = mock_engine
                    
                    estimator = ChordEstimationModule()
                    
                    # Create test audio
                    audio = np.random.rand(22050)
                    sample_rate = 22050
                    
                    # Call method
                    result = estimator._chordai_recognition(audio, sample_rate)
                    
                    # Verify result structure
                    assert len(result) == 2
                    
                    # Check first segment
                    assert result[0].start_time == 0.0
                    assert result[0].end_time == 0.5
                    assert result[0].root == "C"
                    assert result[0].quality == ChordQuality.MAJOR
                    assert result[0].confidence == 0.95
                    
                    # Check second segment
                    assert result[1].start_time == 0.5
                    assert result[1].end_time == 1.0
                    assert result[1].root == "D"
                    assert result[1].quality == ChordQuality.MINOR
                    assert result[1].confidence == 0.90
    
    def test_chordai_recognition_handles_bass_notes(self):
        """Test that bass notes from predictions are preserved in ChordSegment"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine') as mock_engine_class:
                    # Setup mocks
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    # Create mock predictions with bass notes
                    predictions = [
                        ChordPrediction(0.0, 0.5, "C", "maj", "G", 0.95),  # C/G
                        ChordPrediction(0.5, 1.0, "D", "min", None, 0.90)  # Dm (no bass)
                    ]
                    
                    mock_engine = Mock()
                    mock_engine.predict_chords.return_value = predictions
                    mock_engine_class.return_value = mock_engine
                    
                    estimator = ChordEstimationModule()
                    
                    # Create test audio
                    audio = np.random.rand(22050)
                    sample_rate = 22050
                    
                    # Call method
                    result = estimator._chordai_recognition(audio, sample_rate)
                    
                    # Verify bass notes are preserved
                    assert result[0].bass_note == "G"
                    assert result[1].bass_note is None
    
    def test_chordai_recognition_raises_runtime_error_on_failure(self):
        """Test that RuntimeError is raised when inference fails"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine') as mock_engine_class:
                    # Setup mocks
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    # Make inference engine raise an exception
                    mock_engine = Mock()
                    mock_engine.predict_chords.side_effect = ValueError("Invalid input shape")
                    mock_engine_class.return_value = mock_engine
                    
                    estimator = ChordEstimationModule()
                    
                    # Create test audio
                    audio = np.random.rand(22050)
                    sample_rate = 22050
                    
                    # Call method and expect RuntimeError
                    with pytest.raises(RuntimeError) as exc_info:
                        estimator._chordai_recognition(audio, sample_rate)
                    
                    assert "ChordAI recognition failed" in str(exc_info.value)
    
    def test_chordai_recognition_empty_predictions(self):
        """Test that _chordai_recognition handles empty predictions list"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine') as mock_engine_class:
                    # Setup mocks
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    # Return empty predictions
                    mock_engine = Mock()
                    mock_engine.predict_chords.return_value = []
                    mock_engine_class.return_value = mock_engine
                    
                    estimator = ChordEstimationModule()
                    
                    # Create test audio
                    audio = np.random.rand(22050)
                    sample_rate = 22050
                    
                    # Call method
                    result = estimator._chordai_recognition(audio, sample_rate)
                    
                    # Verify empty list is returned
                    assert isinstance(result, list)
                    assert len(result) == 0
