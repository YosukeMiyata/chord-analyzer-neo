"""Unit tests for ChordAI Inference Engine"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock

from src.chordai_inference import ChordAIInferenceEngine
from src.chordai_models import ChordPrediction


class TestChordAIInferenceEngine:
    """Test suite for ChordAIInferenceEngine"""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock TensorFlow model"""
        model = Mock()
        model.signatures = {
            'serving_default': Mock()
        }
        return model
    
    @pytest.fixture
    def inference_engine(self, mock_model):
        """Create an inference engine with mock model"""
        return ChordAIInferenceEngine(mock_model)
    
    def test_init_with_serving_default_signature(self, mock_model):
        """Test initialization with serving_default signature"""
        engine = ChordAIInferenceEngine(mock_model)
        assert engine.model == mock_model
        assert engine.infer_fn == mock_model.signatures['serving_default']
    
    def test_init_with_alternative_signature(self):
        """Test initialization when serving_default is not available"""
        model = Mock()
        custom_signature = Mock()
        model.signatures = {'custom_signature': custom_signature}
        
        engine = ChordAIInferenceEngine(model)
        assert engine.infer_fn == custom_signature
    
    def test_init_without_signatures_raises_error(self):
        """Test that initialization fails if model has no signatures"""
        model = Mock()
        model.signatures = {}
        
        with pytest.raises(ValueError, match="Model does not have valid signatures"):
            ChordAIInferenceEngine(model)
    
    def test_predict_chords_with_valid_input(self, inference_engine):
        """Test predict_chords with valid chroma input"""
        # Create valid chroma features (12 pitch classes, 10 frames)
        chroma = np.random.rand(12, 10)
        sample_rate = 22050
        
        predictions = inference_engine.predict_chords(chroma, sample_rate)
        
        # Verify output format
        assert isinstance(predictions, list)
        assert len(predictions) > 0
        assert all(isinstance(p, ChordPrediction) for p in predictions)
    
    def test_predict_chords_output_format(self, inference_engine):
        """Test that predictions have correct ChordPrediction format"""
        chroma = np.random.rand(12, 5)
        sample_rate = 22050
        
        predictions = inference_engine.predict_chords(chroma, sample_rate)
        
        for pred in predictions:
            assert hasattr(pred, 'start_time')
            assert hasattr(pred, 'end_time')
            assert hasattr(pred, 'root')
            assert hasattr(pred, 'quality')
            assert hasattr(pred, 'bass_note')
            assert hasattr(pred, 'confidence')
            assert isinstance(pred.start_time, float)
            assert isinstance(pred.end_time, float)
            assert isinstance(pred.root, str)
            assert isinstance(pred.quality, str)
            assert pred.confidence >= 0.0 and pred.confidence <= 1.0
    
    def test_predict_chords_timing_information(self, inference_engine):
        """Test that predictions have correct timing information"""
        chroma = np.random.rand(12, 4)
        sample_rate = 22050
        frame_duration = 0.5
        
        predictions = inference_engine.predict_chords(
            chroma, sample_rate, frame_duration
        )
        
        # Verify timing
        assert len(predictions) == 4
        for i, pred in enumerate(predictions):
            expected_start = i * frame_duration
            expected_end = (i + 1) * frame_duration
            assert pred.start_time == pytest.approx(expected_start)
            assert pred.end_time == pytest.approx(expected_end)
    
    def test_predict_chords_invalid_shape_1d(self, inference_engine):
        """Test error handling for 1D chroma input"""
        chroma = np.random.rand(12)  # 1D instead of 2D
        sample_rate = 22050
        
        with pytest.raises(ValueError, match="must be 2-dimensional"):
            inference_engine.predict_chords(chroma, sample_rate)
    
    def test_predict_chords_invalid_shape_3d(self, inference_engine):
        """Test error handling for 3D chroma input"""
        chroma = np.random.rand(12, 10, 5)  # 3D instead of 2D
        sample_rate = 22050
        
        with pytest.raises(ValueError, match="must be 2-dimensional"):
            inference_engine.predict_chords(chroma, sample_rate)
    
    def test_predict_chords_invalid_pitch_classes(self, inference_engine):
        """Test error handling for wrong number of pitch classes"""
        chroma = np.random.rand(24, 10)  # 24 instead of 12 pitch classes
        sample_rate = 22050
        
        with pytest.raises(ValueError, match="must have 12 pitch classes"):
            inference_engine.predict_chords(chroma, sample_rate)
    
    def test_predict_chords_empty_frames(self, inference_engine):
        """Test handling of chroma with zero frames"""
        chroma = np.random.rand(12, 0)  # No frames
        sample_rate = 22050
        
        predictions = inference_engine.predict_chords(chroma, sample_rate)
        assert isinstance(predictions, list)
        assert len(predictions) == 0
    
    def test_predict_chords_single_frame(self, inference_engine):
        """Test handling of single chroma frame"""
        chroma = np.random.rand(12, 1)
        sample_rate = 22050
        
        predictions = inference_engine.predict_chords(chroma, sample_rate)
        assert len(predictions) == 1
        assert predictions[0].start_time == 0.0
        assert predictions[0].end_time == 0.5
    
    def test_predict_chords_custom_frame_duration(self, inference_engine):
        """Test predict_chords with custom frame duration"""
        chroma = np.random.rand(12, 3)
        sample_rate = 22050
        frame_duration = 1.0  # 1 second per frame
        
        predictions = inference_engine.predict_chords(
            chroma, sample_rate, frame_duration
        )
        
        assert len(predictions) == 3
        assert predictions[0].end_time == 1.0
        assert predictions[1].start_time == 1.0
        assert predictions[1].end_time == 2.0
        assert predictions[2].start_time == 2.0
        assert predictions[2].end_time == 3.0
