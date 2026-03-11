"""Tests for ChordAIModelLoader

Tests cover:
- Successful model loading with valid files
- Error handling for missing model files
- Error handling for corrupted model files
- Model architecture validation
- Dependency verification
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.chordai_loader import ChordAIModelLoader


@pytest.fixture
def temp_model_dir():
    """Create temporary model directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def valid_model_dir(temp_model_dir):
    """Create a valid model directory structure"""
    # Create saved_model.pb
    saved_model_pb = temp_model_dir / "saved_model.pb"
    saved_model_pb.write_bytes(b"dummy model content")
    
    # Create variables directory
    variables_dir = temp_model_dir / "variables"
    variables_dir.mkdir()
    
    # Create variable files
    (variables_dir / "variables.data-00000-of-00001").write_bytes(b"dummy weights")
    (variables_dir / "variables.index").write_bytes(b"dummy index")
    
    return temp_model_dir


@pytest.fixture
def mock_tensorflow():
    """Mock TensorFlow module"""
    with patch.dict('sys.modules', {'tensorflow': MagicMock()}):
        import sys
        tf_mock = sys.modules['tensorflow']
        yield tf_mock


class TestChordAIModelLoader:
    """Test suite for ChordAIModelLoader"""
    
    def test_initialization(self, temp_model_dir):
        """Test ChordAIModelLoader initialization"""
        loader = ChordAIModelLoader(temp_model_dir)
        
        assert loader.model_path == temp_model_dir
        assert isinstance(loader.model_path, Path)
    
    def test_initialization_converts_string_to_path(self):
        """Test that string paths are converted to Path objects"""
        loader = ChordAIModelLoader("/path/to/model")
        
        assert isinstance(loader.model_path, Path)
        assert str(loader.model_path) == "/path/to/model"
    
    def test_load_model_missing_tensorflow_raises_import_error(self, valid_model_dir):
        """Test that missing TensorFlow raises ImportError with helpful message
        
        Requirements: 1.2, 6.2, 6.3
        """
        loader = ChordAIModelLoader(valid_model_dir)
        
        with patch.dict('sys.modules', {'tensorflow': None}):
            with pytest.raises(ImportError) as exc_info:
                loader.load_model()
            
            error_msg = str(exc_info.value)
            assert "tensorflow" in error_msg.lower()
            assert "pip install tensorflow>=2.0.0" in error_msg
    
    def test_load_model_nonexistent_directory_raises_file_not_found(self, temp_model_dir):
        """Test that nonexistent model directory raises FileNotFoundError
        
        Requirements: 1.2
        """
        nonexistent_dir = temp_model_dir / "nonexistent"
        loader = ChordAIModelLoader(nonexistent_dir)
        
        with patch.dict('sys.modules', {'tensorflow': MagicMock()}):
            with pytest.raises(FileNotFoundError) as exc_info:
                loader.load_model()
            
            error_msg = str(exc_info.value)
            assert str(nonexistent_dir) in error_msg
            assert "not found" in error_msg.lower()
    
    def test_load_model_missing_saved_model_pb_raises_file_not_found(self, temp_model_dir):
        """Test that missing saved_model.pb raises FileNotFoundError
        
        Requirements: 1.2
        """
        # Create directory but no saved_model.pb
        loader = ChordAIModelLoader(temp_model_dir)
        
        with patch.dict('sys.modules', {'tensorflow': MagicMock()}):
            with pytest.raises(FileNotFoundError) as exc_info:
                loader.load_model()
            
            error_msg = str(exc_info.value)
            assert "saved_model.pb" in error_msg
            assert "not found" in error_msg.lower()
    
    def test_load_model_missing_variables_directory_raises_file_not_found(self, temp_model_dir):
        """Test that missing variables directory raises FileNotFoundError
        
        Requirements: 1.2
        """
        # Create saved_model.pb but no variables directory
        saved_model_pb = temp_model_dir / "saved_model.pb"
        saved_model_pb.write_bytes(b"dummy")
        
        loader = ChordAIModelLoader(temp_model_dir)
        
        with patch.dict('sys.modules', {'tensorflow': MagicMock()}):
            with pytest.raises(FileNotFoundError) as exc_info:
                loader.load_model()
            
            error_msg = str(exc_info.value)
            assert "variables" in error_msg.lower()
            assert "not found" in error_msg.lower()
    
    def test_load_model_corrupted_file_raises_runtime_error(self, valid_model_dir, mock_tensorflow):
        """Test that corrupted model file raises RuntimeError
        
        Requirements: 1.2
        """
        loader = ChordAIModelLoader(valid_model_dir)
        
        # Mock TensorFlow to raise an exception when loading
        mock_tensorflow.saved_model.load.side_effect = Exception("Corrupted model file")
        
        with pytest.raises(RuntimeError) as exc_info:
            loader.load_model()
        
        error_msg = str(exc_info.value)
        assert "failed to load" in error_msg.lower()
        assert "corrupted" in error_msg.lower()
    
    def test_load_model_success(self, valid_model_dir, mock_tensorflow):
        """Test successful model loading
        
        Requirements: 1.1
        """
        loader = ChordAIModelLoader(valid_model_dir)
        
        # Mock successful model loading
        mock_model = Mock()
        mock_tensorflow.saved_model.load.return_value = mock_model
        
        result = loader.load_model()
        
        assert result == mock_model
        mock_tensorflow.saved_model.load.assert_called_once_with(str(valid_model_dir))
    
    def test_validate_model_no_signatures_returns_false(self):
        """Test that model without signatures fails validation
        
        Requirements: 1.4
        """
        loader = ChordAIModelLoader(Path("/dummy"))
        
        # Create mock model without signatures
        mock_model = Mock(spec=[])  # No attributes
        
        result = loader.validate_model(mock_model)
        
        assert result is False
    
    def test_validate_model_empty_signatures_returns_false(self):
        """Test that model with empty signatures fails validation
        
        Requirements: 1.4
        """
        loader = ChordAIModelLoader(Path("/dummy"))
        
        # Create mock model with empty signatures
        mock_model = Mock()
        mock_model.signatures = {}
        
        result = loader.validate_model(mock_model)
        
        assert result is False
    
    def test_validate_model_no_serving_default_uses_first_signature(self):
        """Test that model without serving_default uses first available signature
        
        Requirements: 1.4
        """
        loader = ChordAIModelLoader(Path("/dummy"))
        
        # Create mock inference function
        mock_infer_fn = Mock()
        mock_infer_fn.structured_input_signature = Mock()
        mock_infer_fn.structured_outputs = Mock()
        
        # Create mock model with custom signature
        mock_model = Mock()
        mock_model.signatures = {'custom_signature': mock_infer_fn}
        
        result = loader.validate_model(mock_model)
        
        assert result is True
    
    def test_validate_model_missing_input_signature_returns_false(self):
        """Test that model without input signature fails validation
        
        Requirements: 1.4
        """
        loader = ChordAIModelLoader(Path("/dummy"))
        
        # Create mock inference function without input signature
        mock_infer_fn = Mock(spec=['structured_outputs'])
        mock_infer_fn.structured_outputs = Mock()
        
        # Create mock model
        mock_model = Mock()
        mock_model.signatures = {'serving_default': mock_infer_fn}
        
        result = loader.validate_model(mock_model)
        
        assert result is False
    
    def test_validate_model_missing_outputs_returns_false(self):
        """Test that model without outputs fails validation
        
        Requirements: 1.4
        """
        loader = ChordAIModelLoader(Path("/dummy"))
        
        # Create mock inference function without outputs
        mock_infer_fn = Mock(spec=['structured_input_signature'])
        mock_infer_fn.structured_input_signature = Mock()
        
        # Create mock model
        mock_model = Mock()
        mock_model.signatures = {'serving_default': mock_infer_fn}
        
        result = loader.validate_model(mock_model)
        
        assert result is False
    
    def test_validate_model_success_with_serving_default(self):
        """Test successful validation with serving_default signature
        
        Requirements: 1.4
        """
        loader = ChordAIModelLoader(Path("/dummy"))
        
        # Create mock inference function with all required attributes
        mock_infer_fn = Mock()
        mock_infer_fn.structured_input_signature = Mock()
        mock_infer_fn.structured_outputs = Mock()
        
        # Create mock model
        mock_model = Mock()
        mock_model.signatures = {'serving_default': mock_infer_fn}
        
        result = loader.validate_model(mock_model)
        
        assert result is True
    
    def test_validate_model_exception_returns_false(self):
        """Test that validation exceptions are caught and return False
        
        Requirements: 1.4
        """
        loader = ChordAIModelLoader(Path("/dummy"))
        
        # Create mock model that raises exception
        mock_model = Mock()
        mock_model.signatures = Mock(side_effect=Exception("Unexpected error"))
        
        result = loader.validate_model(mock_model)
        
        assert result is False
    
    def test_load_and_validate_workflow(self, valid_model_dir, mock_tensorflow):
        """Test complete load and validate workflow
        
        Requirements: 1.1, 1.4
        """
        loader = ChordAIModelLoader(valid_model_dir)
        
        # Create mock model with valid structure
        mock_infer_fn = Mock()
        mock_infer_fn.structured_input_signature = Mock()
        mock_infer_fn.structured_outputs = Mock()
        
        mock_model = Mock()
        mock_model.signatures = {'serving_default': mock_infer_fn}
        
        mock_tensorflow.saved_model.load.return_value = mock_model
        
        # Load model
        loaded_model = loader.load_model()
        assert loaded_model == mock_model
        
        # Validate model
        is_valid = loader.validate_model(loaded_model)
        assert is_valid is True
    
    def test_error_messages_are_descriptive(self, temp_model_dir):
        """Test that all error messages are descriptive and helpful
        
        Requirements: 1.2
        """
        loader = ChordAIModelLoader(temp_model_dir)
        
        # Test missing directory error message
        with patch.dict('sys.modules', {'tensorflow': MagicMock()}):
            try:
                loader.load_model()
            except FileNotFoundError as e:
                assert "not found" in str(e).lower()
                assert str(temp_model_dir) in str(e)
    
    def test_multiple_loaders_independent(self):
        """Test that multiple loader instances are independent"""
        path1 = Path("/path/to/model1")
        path2 = Path("/path/to/model2")
        
        loader1 = ChordAIModelLoader(path1)
        loader2 = ChordAIModelLoader(path2)
        
        assert loader1.model_path != loader2.model_path
        assert loader1.model_path == path1
        assert loader2.model_path == path2
