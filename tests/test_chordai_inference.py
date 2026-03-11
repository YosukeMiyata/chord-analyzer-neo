"""Unit tests for ChordAI Inference Engine"""

import pytest
import numpy as np
from pathlib import Path

from src.chordai_inference import ChordAIInferenceEngine
from src.chordai_models import ChordPrediction
from src.chordai_loader import ChordAIModelLoader


class TestChordAIInferenceEngine:
    """Test suite for ChordAIInferenceEngine"""
    
    @pytest.fixture
    def real_model(self):
        """Load the actual ChordAI model"""
        model_path = Path("models/chordai")
        loader = ChordAIModelLoader(model_path)
        return loader.load_model()
    
    @pytest.fixture
    def inference_engine(self, real_model):
        """Create an inference engine with real model"""
        return ChordAIInferenceEngine(real_model)
    
    def test_init_with_serving_default_signature(self, real_model):
        """Test initialization with serving_default signature"""
        engine = ChordAIInferenceEngine(real_model)
        assert engine.model == real_model
        assert hasattr(engine, 'infer_fn')
    
    def test_predict_chords_with_valid_input(self, inference_engine):
        """Test predict_chords with valid audio input"""
        # Create valid audio (1 second at 22050 Hz)
        audio = np.random.rand(22050).astype(np.float32)
        sample_rate = 22050
        
        predictions = inference_engine.predict_chords(audio, sample_rate)
        
        # Verify output format
        assert isinstance(predictions, list)
        assert len(predictions) > 0
        assert all(isinstance(p, ChordPrediction) for p in predictions)
    
    def test_predict_chords_output_format(self, inference_engine):
        """Test that predictions have correct ChordPrediction format"""
        audio = np.random.rand(22050).astype(np.float32)
        sample_rate = 22050
        
        predictions = inference_engine.predict_chords(audio, sample_rate)
        
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
        audio = np.random.rand(44100).astype(np.float32)  # 2 seconds
        sample_rate = 22050
        frame_duration = 0.5
        
        predictions = inference_engine.predict_chords(
            audio, sample_rate, frame_duration
        )
        
        # Verify timing (should have multiple predictions)
        assert len(predictions) > 0
        for i, pred in enumerate(predictions):
            expected_start = i * frame_duration
            expected_end = (i + 1) * frame_duration
            assert pred.start_time == pytest.approx(expected_start)
            assert pred.end_time == pytest.approx(expected_end)
    
    def test_predict_chords_empty_audio(self, inference_engine):
        """Test handling of empty audio"""
        audio = np.array([]).astype(np.float32)
        sample_rate = 22050
        
        # Empty audio should still process but may return empty or minimal predictions
        predictions = inference_engine.predict_chords(audio, sample_rate)
        assert isinstance(predictions, list)
    
    def test_predict_chords_short_audio(self, inference_engine):
        """Test handling of very short audio"""
        audio = np.random.rand(1000).astype(np.float32)  # ~0.045 seconds
        sample_rate = 22050
        
        predictions = inference_engine.predict_chords(audio, sample_rate)
        assert isinstance(predictions, list)
        # Short audio may produce minimal predictions
    
    def test_predict_chords_custom_frame_duration(self, inference_engine):
        """Test predict_chords with custom frame duration"""
        audio = np.random.rand(66150).astype(np.float32)  # 3 seconds
        sample_rate = 22050
        frame_duration = 1.0  # 1 second per frame
        
        predictions = inference_engine.predict_chords(
            audio, sample_rate, frame_duration
        )
        
        assert len(predictions) > 0
        # Verify frame duration is applied
        if len(predictions) >= 2:
            assert predictions[1].start_time == pytest.approx(1.0)
            assert predictions[1].end_time == pytest.approx(2.0)
