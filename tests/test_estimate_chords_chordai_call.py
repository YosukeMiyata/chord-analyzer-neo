"""Test that estimate_chords calls _chordai_recognition (Task 6.3)

This test verifies that:
- estimate_chords calls _chordai_recognition instead of _simple_chord_recognition
- Chroma features are passed unchanged to _chordai_recognition
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.chord_estimation import ChordEstimationModule
from src.models import ChordSegment, ChordQuality


class TestEstimateChordsChordAICall:
    """Test that estimate_chords uses ChordAI recognition"""
    
    def test_estimate_chords_calls_chordai_recognition(self):
        """Test that estimate_chords calls _chordai_recognition instead of _simple_chord_recognition"""
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
                    
                    estimator = ChordEstimationModule(use_chordai=True)
                    
                    # Mock the _chordai_recognition method to track calls
                    with patch.object(estimator, '_chordai_recognition', return_value=[]) as mock_chordai:
                        # Create test audio
                        audio = np.random.rand(22050)  # 1 second of audio
                        sample_rate = 22050
                        
                        # Call estimate_chords
                        result = estimator.estimate_chords(audio, sample_rate, use_vocal_separation=False)
                        
                        # Verify _chordai_recognition was called
                        assert mock_chordai.called, "_chordai_recognition should be called"
                        assert mock_chordai.call_count == 1, "_chordai_recognition should be called exactly once"
    
    def test_estimate_chords_passes_chroma_to_chordai(self):
        """Test that estimate_chords passes audio unchanged to _chordai_recognition"""
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
                    
                    estimator = ChordEstimationModule(use_chordai=True)
                    
                    # Mock the _chordai_recognition method to capture arguments
                    captured_audio = None
                    captured_sr = None
                    
                    def capture_args(audio, sample_rate):
                        nonlocal captured_audio, captured_sr
                        captured_audio = audio
                        captured_sr = sample_rate
                        return []
                    
                    with patch.object(estimator, '_chordai_recognition', side_effect=capture_args):
                        # Create test audio
                        audio = np.random.rand(22050)  # 1 second of audio
                        sample_rate = 22050
                        
                        # Call estimate_chords
                        estimator.estimate_chords(audio, sample_rate, use_vocal_separation=False)
                        
                        # Verify audio was passed
                        assert captured_audio is not None, "Audio should be passed to _chordai_recognition"
                        assert captured_sr == sample_rate, "Sample rate should be passed unchanged"
                        
                        # Verify audio has correct shape (1D array)
                        assert captured_audio.ndim == 1, "Audio should be 1D array"
    
    def test_estimate_chords_does_not_call_simple_chord_recognition(self):
        """Test that estimate_chords does NOT call _simple_chord_recognition when using ChordAI"""
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
                    
                    estimator = ChordEstimationModule(use_chordai=True)
                    
                    # Check if _simple_chord_recognition method exists
                    has_simple_method = hasattr(estimator, '_simple_chord_recognition')
                    
                    if has_simple_method:
                        # If it exists, mock it to track calls
                        with patch.object(estimator, '_simple_chord_recognition', return_value=[]) as mock_simple:
                            with patch.object(estimator, '_chordai_recognition', return_value=[]):
                                # Create test audio
                                audio = np.random.rand(22050)
                                sample_rate = 22050
                                
                                # Call estimate_chords
                                estimator.estimate_chords(audio, sample_rate, use_vocal_separation=False)
                                
                                # Verify _simple_chord_recognition was NOT called
                                assert not mock_simple.called, "_simple_chord_recognition should NOT be called"
    
    def test_estimate_chords_integration_with_chordai(self):
        """Integration test: estimate_chords with ChordAI returns expected format"""
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
                    
                    estimator = ChordEstimationModule(use_chordai=True)
                    
                    # Mock _chordai_recognition to return sample chord segments
                    sample_segments = [
                        ChordSegment(
                            start_time=0.0,
                            end_time=0.5,
                            root="C",
                            quality=ChordQuality.MAJOR,
                            bass_note=None,
                            extensions=[],
                            confidence=0.95
                        ),
                        ChordSegment(
                            start_time=0.5,
                            end_time=1.0,
                            root="G",
                            quality=ChordQuality.MAJOR,
                            bass_note=None,
                            extensions=[],
                            confidence=0.90
                        )
                    ]
                    
                    with patch.object(estimator, '_chordai_recognition', return_value=sample_segments):
                        # Create test audio
                        audio = np.random.rand(22050)
                        sample_rate = 22050
                        
                        # Call estimate_chords
                        result = estimator.estimate_chords(audio, sample_rate, use_vocal_separation=False)
                        
                        # Verify result format
                        assert isinstance(result, list), "Result should be a list"
                        assert len(result) == 2, "Should return 2 chord segments"
                        assert all(isinstance(seg, ChordSegment) for seg in result), "All items should be ChordSegment"
                        
                        # Verify chord data
                        assert result[0].root == "C"
                        assert result[0].quality == ChordQuality.MAJOR
                        assert result[1].root == "G"
                        assert result[1].quality == ChordQuality.MAJOR
