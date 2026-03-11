"""Tests for ChordEstimationModule ChordAI initialization (Task 6.1)

These tests verify that the ChordEstimationModule correctly initializes
with the ChordAI model, including dependency verification and error handling.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.chord_estimation import ChordEstimationModule


class TestChordAIInitialization:
    """Test ChordAI model initialization in ChordEstimationModule"""
    
    def test_dependency_verification_missing_tensorflow(self):
        """Test that missing TensorFlow dependency raises ImportError"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies') as mock_verify:
            mock_verify.side_effect = ImportError(
                "Required dependencies not found: tensorflow>=2.0. "
                "Please install with: pip install tensorflow>=2.0"
            )
            
            with pytest.raises(ImportError) as exc_info:
                ChordEstimationModule(use_chordai=True)
            
            assert "tensorflow>=2.0" in str(exc_info.value)
            assert "pip install" in str(exc_info.value)
    
    def test_model_path_default(self):
        """Test that default model path is set correctly"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine'):
                    # Setup mock
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    estimator = ChordEstimationModule(use_chordai=True)
                    
                    assert estimator.model_path == Path("models/chordai")
    
    def test_model_path_custom(self):
        """Test that custom model path is used when provided"""
        custom_path = Path("/custom/model/path")
        
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine'):
                    # Setup mock
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    estimator = ChordEstimationModule(model_path=custom_path, use_chordai=True)
                    
                    assert estimator.model_path == custom_path
                    mock_loader_class.assert_called_once_with(custom_path)
    
    def test_chordai_loader_initialization(self):
        """Test that ChordAIModelLoader is initialized with correct path"""
        model_path = Path("test/model/path")
        
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine'):
                    # Setup mock
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    estimator = ChordEstimationModule(model_path=model_path, use_chordai=True)
                    
                    # Verify loader was created with correct path
                    mock_loader_class.assert_called_once_with(model_path)
                    assert estimator.chordai_loader == mock_loader
    
    def test_model_loading(self):
        """Test that model is loaded using ChordAIModelLoader"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine'):
                    # Setup mock
                    mock_model = Mock()
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = mock_model
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    estimator = ChordEstimationModule(use_chordai=True)
                    
                    # Verify model was loaded
                    mock_loader.load_model.assert_called_once()
                    assert estimator.model == mock_model
    
    def test_model_validation(self):
        """Test that loaded model is validated"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine'):
                    # Setup mock
                    mock_model = Mock()
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = mock_model
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    estimator = ChordEstimationModule(use_chordai=True)
                    
                    # Verify validation was called
                    mock_loader.validate_model.assert_called_once_with(mock_model)
    
    def test_model_validation_failure(self):
        """Test that invalid model raises ValueError"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                # Setup mock with validation failure
                mock_model = Mock()
                mock_loader = Mock()
                mock_loader.load_model.return_value = mock_model
                mock_loader.validate_model.return_value = False
                mock_loader_class.return_value = mock_loader
                
                with pytest.raises(ValueError) as exc_info:
                    ChordEstimationModule(use_chordai=True)
                
                assert "Invalid model architecture" in str(exc_info.value)
    
    def test_inference_engine_initialization(self):
        """Test that ChordAIInferenceEngine is initialized with loaded model"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine') as mock_engine_class:
                    # Setup mocks
                    mock_model = Mock()
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = mock_model
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    mock_engine = Mock()
                    mock_engine_class.return_value = mock_engine
                    
                    estimator = ChordEstimationModule(use_chordai=True)
                    
                    # Verify inference engine was created with model
                    mock_engine_class.assert_called_once_with(mock_model)
                    assert estimator.inference_engine == mock_engine
    
    def test_file_not_found_error_handling(self):
        """Test that FileNotFoundError from model loading is properly handled"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                # Setup mock to raise FileNotFoundError
                mock_loader = Mock()
                mock_loader.load_model.side_effect = FileNotFoundError(
                    "ChordAI model weights not found at models/chordai"
                )
                mock_loader_class.return_value = mock_loader
                
                with pytest.raises(FileNotFoundError) as exc_info:
                    ChordEstimationModule(use_chordai=True)
                
                assert "model weights not found" in str(exc_info.value).lower()
    
    def test_runtime_error_handling(self):
        """Test that RuntimeError from model loading is properly handled"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                # Setup mock to raise RuntimeError
                mock_loader = Mock()
                mock_loader.load_model.side_effect = RuntimeError(
                    "Failed to load ChordAI model: corrupted file"
                )
                mock_loader_class.return_value = mock_loader
                
                with pytest.raises(RuntimeError) as exc_info:
                    ChordEstimationModule(use_chordai=True)
                
                assert "Failed to load ChordAI model" in str(exc_info.value)
    
    def test_parameters_preserved(self):
        """Test that chord recognition parameters are preserved"""
        with patch('src.chord_estimation.ChordEstimationModule._verify_dependencies'):
            with patch('src.chordai_loader.ChordAIModelLoader') as mock_loader_class:
                with patch('src.chordai_inference.ChordAIInferenceEngine'):
                    # Setup mock
                    mock_loader = Mock()
                    mock_loader.load_model.return_value = Mock()
                    mock_loader.validate_model.return_value = True
                    mock_loader_class.return_value = mock_loader
                    
                    estimator = ChordEstimationModule(use_chordai=True)
                    
                    # Verify parameters are set correctly
                    assert estimator.hop_length == 512
                    assert estimator.n_fft == 2048
                    assert estimator.frame_duration == 0.5


class TestDependencyVerification:
    """Test dependency verification logic"""
    
    def test_verify_dependencies_tensorflow_missing(self):
        """Test that ImportError is raised when TensorFlow is missing"""
        # Create a minimal instance to test _verify_dependencies
        with patch.object(ChordEstimationModule, '__init__', lambda x, model_path=None: None):
            estimator = ChordEstimationModule()
            
            # Manually set up the method we want to test
            estimator._verify_dependencies = ChordEstimationModule._verify_dependencies.__get__(estimator)
            
            with patch('builtins.__import__') as mock_import:
                def import_side_effect(name, *args, **kwargs):
                    if name == 'tensorflow':
                        raise ImportError("No module named 'tensorflow'")
                    return Mock()
                
                mock_import.side_effect = import_side_effect
                
                with pytest.raises(ImportError) as exc_info:
                    estimator._verify_dependencies()
                
                assert "tensorflow>=2.0" in str(exc_info.value)
                assert "pip install" in str(exc_info.value)
