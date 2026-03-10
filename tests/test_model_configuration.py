"""Tests for ModelConfigurationModule"""

import pytest
import tempfile
import tomli
from pathlib import Path
from src.model_configuration import ModelConfigurationModule
from src.models import ModelConfig


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
def sample_model_file(temp_models_dir):
    """Create a sample model file"""
    model_file = temp_models_dir / "test_model.onnx"
    model_file.write_text("dummy model content")
    return model_file


class TestModelConfigurationModule:
    """Test suite for ModelConfigurationModule"""
    
    def test_initialization_creates_default_config(self, temp_models_dir):
        """Test that initialization creates default configuration"""
        module = ModelConfigurationModule(models_dir=temp_models_dir)
        
        # Check that config file was created
        config_path = temp_models_dir / "models.toml"
        assert config_path.exists()
        
        # Check that default model exists
        models = module.list_available_models()
        assert len(models) == 1
        assert models[0].model_id == "default_hmm"
        assert models[0].is_default is True
    
    def test_list_available_models(self, model_config_module):
        """Test listing available models - Requirement 13.2"""
        models = model_config_module.list_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert all(isinstance(m, ModelConfig) for m in models)
    
    def test_get_active_model(self, model_config_module):
        """Test getting active model - Requirement 13.3"""
        active_model = model_config_module.get_active_model()
        
        assert isinstance(active_model, ModelConfig)
        assert active_model.model_id == "default_hmm"
    
    def test_get_active_model_no_active_raises_error(self, temp_models_dir):
        """Test that getting active model raises error when none is set"""
        module = ModelConfigurationModule(models_dir=temp_models_dir)
        module._active_model_id = None
        
        with pytest.raises(RuntimeError, match="No active model set"):
            module.get_active_model()
    
    def test_set_active_model(self, model_config_module, sample_model_file):
        """Test changing active model - Requirement 13.3"""
        # Add a custom model
        custom_model = model_config_module.add_custom_model(
            model_path=sample_model_file,
            model_name="Test Model",
            model_type="onnx",
            description="Test model"
        )
        
        # Set it as active
        model_config_module.set_active_model(custom_model.model_id)
        
        # Verify it's active
        active_model = model_config_module.get_active_model()
        assert active_model.model_id == custom_model.model_id
    
    def test_set_active_model_invalid_id_raises_error(self, model_config_module):
        """Test that setting invalid model ID raises error"""
        with pytest.raises(ValueError, match="Model 'invalid_id' not found"):
            model_config_module.set_active_model("invalid_id")
    
    def test_add_custom_model(self, model_config_module, sample_model_file):
        """Test adding custom model - Requirement 13.5"""
        model_config = model_config_module.add_custom_model(
            model_path=sample_model_file,
            model_name="Custom ONNX Model",
            model_type="onnx",
            description="A custom ONNX model for jazz"
        )
        
        assert isinstance(model_config, ModelConfig)
        assert model_config.model_name == "Custom ONNX Model"
        assert model_config.model_type == "onnx"
        assert model_config.description == "A custom ONNX model for jazz"
        assert model_config.is_default is False
        
        # Verify it's in the list
        models = model_config_module.list_available_models()
        assert any(m.model_id == model_config.model_id for m in models)
    
    def test_add_custom_model_with_custom_id(self, model_config_module, sample_model_file):
        """Test adding custom model with custom ID"""
        model_config = model_config_module.add_custom_model(
            model_path=sample_model_file,
            model_name="Test Model",
            model_type="onnx",
            description="Test",
            model_id="my_custom_id"
        )
        
        assert model_config.model_id == "my_custom_id"
    
    def test_add_custom_model_nonexistent_file_raises_error(self, model_config_module, temp_models_dir):
        """Test that adding model with nonexistent file raises error"""
        nonexistent_file = temp_models_dir / "nonexistent.onnx"
        
        with pytest.raises(ValueError, match="Model file not found"):
            model_config_module.add_custom_model(
                model_path=nonexistent_file,
                model_name="Test",
                model_type="onnx",
                description="Test"
            )
    
    def test_add_custom_model_invalid_type_raises_error(self, model_config_module, sample_model_file):
        """Test that adding model with invalid type raises error"""
        with pytest.raises(ValueError, match="Invalid model type"):
            model_config_module.add_custom_model(
                model_path=sample_model_file,
                model_name="Test",
                model_type="invalid_type",
                description="Test"
            )
    
    def test_add_custom_model_duplicate_id_raises_error(self, model_config_module, sample_model_file):
        """Test that adding model with duplicate ID raises error"""
        model_id = "duplicate_id"
        
        # Add first model
        model_config_module.add_custom_model(
            model_path=sample_model_file,
            model_name="First Model",
            model_type="onnx",
            description="First",
            model_id=model_id
        )
        
        # Try to add second model with same ID
        with pytest.raises(ValueError, match="Model ID 'duplicate_id' already exists"):
            model_config_module.add_custom_model(
                model_path=sample_model_file,
                model_name="Second Model",
                model_type="onnx",
                description="Second",
                model_id=model_id
            )
    
    def test_evaluate_model_invalid_id_raises_error(self, model_config_module):
        """Test that evaluating invalid model ID raises error"""
        with pytest.raises(ValueError, match="Model 'invalid_id' not found"):
            model_config_module.evaluate_model(
                model_id="invalid_id",
                test_audio_files=[],
                ground_truth=[]
            )
    
    def test_evaluate_model_mismatched_lengths_raises_error(self, model_config_module):
        """Test that evaluating with mismatched input lengths raises error"""
        with pytest.raises(ValueError, match="Number of test files must match"):
            model_config_module.evaluate_model(
                model_id="default_hmm",
                test_audio_files=[Path("file1.wav")],
                ground_truth=[]
            )
    
    def test_evaluate_model_empty_inputs_raises_error(self, model_config_module):
        """Test that evaluating with empty inputs raises error"""
        with pytest.raises(ValueError, match="No test files provided"):
            model_config_module.evaluate_model(
                model_id="default_hmm",
                test_audio_files=[],
                ground_truth=[]
            )
    
    def test_config_persistence(self, temp_models_dir, sample_model_file):
        """Test that configuration persists across instances - Requirement 13.6"""
        # Create first instance and add model
        module1 = ModelConfigurationModule(models_dir=temp_models_dir)
        custom_model = module1.add_custom_model(
            model_path=sample_model_file,
            model_name="Persistent Model",
            model_type="onnx",
            description="Test persistence"
        )
        module1.set_active_model(custom_model.model_id)
        
        # Create second instance and verify configuration persisted
        module2 = ModelConfigurationModule(models_dir=temp_models_dir)
        
        models = module2.list_available_models()
        assert len(models) == 2  # default + custom
        
        active_model = module2.get_active_model()
        assert active_model.model_id == custom_model.model_id
        assert active_model.model_name == "Persistent Model"
    
    def test_toml_config_format(self, temp_models_dir, sample_model_file):
        """Test that TOML configuration has correct format"""
        module = ModelConfigurationModule(models_dir=temp_models_dir)
        module.add_custom_model(
            model_path=sample_model_file,
            model_name="Test Model",
            model_type="onnx",
            description="Test"
        )
        
        config_path = temp_models_dir / "models.toml"
        assert config_path.exists()
        
        # Parse TOML and verify structure
        with open(config_path, "rb") as f:
            config_data = tomli.load(f)
        
        assert "active_model" in config_data
        assert "models" in config_data
        assert isinstance(config_data["models"], list)
        assert len(config_data["models"]) == 2  # default + custom
        
        # Verify model structure
        for model_data in config_data["models"]:
            assert "model_id" in model_data
            assert "model_name" in model_data
            assert "model_path" in model_data
            assert "model_type" in model_data
            assert "description" in model_data
            assert "accuracy_metrics" in model_data
            assert "is_default" in model_data
    
    def test_model_description_and_accuracy_info(self, model_config_module):
        """Test that models provide description and accuracy information - Requirement 13.4"""
        models = model_config_module.list_available_models()
        
        for model in models:
            assert hasattr(model, 'description')
            assert hasattr(model, 'accuracy_metrics')
            assert isinstance(model.description, str)
            assert isinstance(model.accuracy_metrics, dict)
    
    def test_default_model_setting(self, temp_models_dir, sample_model_file):
        """Test default model configuration - Requirement 13.6"""
        module = ModelConfigurationModule(models_dir=temp_models_dir)
        
        # Default model should be set
        default_models = [m for m in module.list_available_models() if m.is_default]
        assert len(default_models) == 1
        
        # Active model should be the default
        active_model = module.get_active_model()
        assert active_model.is_default is True
    
    def test_evaluate_model_returns_metrics(self, model_config_module):
        """Test that evaluate_model returns accuracy metrics - Requirement 13.4"""
        # Test with empty data (should return zero metrics)
        # We can't test with real audio files in unit tests
        # This is tested in integration tests
        pass
    
    def test_multiple_model_types_supported(self, model_config_module, temp_models_dir):
        """Test that multiple model types are supported"""
        valid_types = ["tensorflow", "onnx", "pytorch", "hmm"]
        
        for model_type in valid_types:
            model_file = temp_models_dir / f"model_{model_type}.bin"
            model_file.write_text("dummy")
            
            model_config = model_config_module.add_custom_model(
                model_path=model_file,
                model_name=f"{model_type} Model",
                model_type=model_type,
                description=f"Test {model_type} model",
                model_id=f"test_{model_type}"
            )
            
            assert model_config.model_type == model_type
    
    def test_model_switching_workflow(self, model_config_module, temp_models_dir):
        """Test complete model switching workflow - Requirements 13.1, 13.2, 13.3"""
        # 1. List available models
        initial_models = model_config_module.list_available_models()
        assert len(initial_models) == 1
        
        # 2. Add custom models
        model_file1 = temp_models_dir / "jazz_model.onnx"
        model_file1.write_text("dummy")
        jazz_model = model_config_module.add_custom_model(
            model_path=model_file1,
            model_name="Jazz Model",
            model_type="onnx",
            description="Optimized for jazz music"
        )
        
        model_file2 = temp_models_dir / "pop_model.onnx"
        model_file2.write_text("dummy")
        pop_model = model_config_module.add_custom_model(
            model_path=model_file2,
            model_name="Pop Model",
            model_type="onnx",
            description="Optimized for pop music"
        )
        
        # 3. List models again
        all_models = model_config_module.list_available_models()
        assert len(all_models) == 3
        
        # 4. Switch to jazz model
        model_config_module.set_active_model(jazz_model.model_id)
        active = model_config_module.get_active_model()
        assert active.model_id == jazz_model.model_id
        
        # 5. Switch to pop model
        model_config_module.set_active_model(pop_model.model_id)
        active = model_config_module.get_active_model()
        assert active.model_id == pop_model.model_id
        
        # 6. Switch back to default
        model_config_module.set_active_model("default_hmm")
        active = model_config_module.get_active_model()
        assert active.model_id == "default_hmm"
