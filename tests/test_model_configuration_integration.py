"""Integration tests for ModelConfigurationModule with ChordEstimationModule"""

import pytest
import tempfile
import numpy as np
from pathlib import Path
from src.model_configuration import ModelConfigurationModule
from src.chord_estimation import ChordEstimationModule


@pytest.fixture
def temp_models_dir():
    """Create temporary models directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def model_config_module(temp_models_dir):
    """Create ModelConfigurationModule instance"""
    return ModelConfigurationModule(models_dir=temp_models_dir)


@pytest.fixture
def sample_audio():
    """Generate sample audio data"""
    # Generate 2 seconds of audio at 22050 Hz
    duration = 2.0
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Simple sine wave at 440 Hz (A4)
    audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    return audio, sample_rate


class TestModelConfigurationIntegration:
    """Integration tests for model configuration with chord estimation"""
    
    def test_default_model_with_chord_estimation(self, model_config_module, sample_audio):
        """Test that default model can be used with chord estimation"""
        audio, sr = sample_audio
        
        # Get active model
        active_model = model_config_module.get_active_model()
        assert active_model.model_id == "default_hmm"
        
        # Create chord estimator (uses default/builtin model)
        chord_estimator = ChordEstimationModule()
        
        # Estimate chords (should not raise error)
        chords = chord_estimator.estimate_chords(audio, sr, use_vocal_separation=False)
        
        # Verify we get some result
        assert isinstance(chords, list)
    
    def test_model_switching_affects_estimation(self, model_config_module, temp_models_dir):
        """Test that switching models is reflected in configuration"""
        # Add a custom model
        model_file = temp_models_dir / "custom_model.onnx"
        model_file.write_text("dummy model")
        
        custom_model = model_config_module.add_custom_model(
            model_path=model_file,
            model_name="Custom Model",
            model_type="onnx",
            description="Custom test model"
        )
        
        # Switch to custom model
        model_config_module.set_active_model(custom_model.model_id)
        
        # Verify active model changed
        active_model = model_config_module.get_active_model()
        assert active_model.model_id == custom_model.model_id
        assert active_model.model_path == str(model_file)
    
    def test_list_models_includes_metadata(self, model_config_module, temp_models_dir):
        """Test that listed models include all necessary metadata for UI display"""
        # Add multiple models
        for i in range(3):
            model_file = temp_models_dir / f"model_{i}.onnx"
            model_file.write_text("dummy")
            
            model_config_module.add_custom_model(
                model_path=model_file,
                model_name=f"Model {i}",
                model_type="onnx",
                description=f"Test model {i} for genre X"
            )
        
        # List all models
        models = model_config_module.list_available_models()
        assert len(models) == 4  # 3 custom + 1 default
        
        # Verify each model has required metadata
        for model in models:
            assert model.model_id
            assert model.model_name
            assert model.model_path
            assert model.model_type
            assert model.description
            assert isinstance(model.accuracy_metrics, dict)
            assert isinstance(model.is_default, bool)
    
    def test_model_configuration_persistence_across_sessions(self, temp_models_dir):
        """Test that model configuration persists and can be reloaded"""
        # Session 1: Create and configure models
        module1 = ModelConfigurationModule(models_dir=temp_models_dir)
        
        model_file = temp_models_dir / "persistent_model.onnx"
        model_file.write_text("dummy")
        
        custom_model = module1.add_custom_model(
            model_path=model_file,
            model_name="Persistent Model",
            model_type="onnx",
            description="Should persist across sessions"
        )
        
        module1.set_active_model(custom_model.model_id)
        
        # Session 2: Reload configuration
        module2 = ModelConfigurationModule(models_dir=temp_models_dir)
        
        # Verify configuration persisted
        active_model = module2.get_active_model()
        assert active_model.model_id == custom_model.model_id
        assert active_model.model_name == "Persistent Model"
        
        models = module2.list_available_models()
        assert len(models) == 2  # default + custom
    
    def test_evaluate_model_with_empty_data(self, model_config_module):
        """Test model evaluation handles edge cases gracefully"""
        # This should raise an error for empty test data
        with pytest.raises(ValueError, match="No test files provided"):
            model_config_module.evaluate_model(
                model_id="default_hmm",
                test_audio_files=[],
                ground_truth=[]
            )
    
    def test_model_types_validation(self, model_config_module, temp_models_dir):
        """Test that only valid model types are accepted"""
        model_file = temp_models_dir / "test.bin"
        model_file.write_text("dummy")
        
        # Valid types should work
        valid_types = ["tensorflow", "onnx", "pytorch", "hmm"]
        for model_type in valid_types:
            model = model_config_module.add_custom_model(
                model_path=model_file,
                model_name=f"Test {model_type}",
                model_type=model_type,
                description="Test",
                model_id=f"test_{model_type}"
            )
            assert model.model_type == model_type
        
        # Invalid type should raise error
        with pytest.raises(ValueError, match="Invalid model type"):
            model_config_module.add_custom_model(
                model_path=model_file,
                model_name="Invalid",
                model_type="invalid_type",
                description="Test",
                model_id="test_invalid"
            )
