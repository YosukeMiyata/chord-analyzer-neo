"""ChordAI Model Loader

This module provides functionality to load and validate the ChordAI pre-trained
machine learning model for chord recognition.

The ChordAI model uses TensorFlow SavedModel format and recognizes 529 chord classes
across all 12 chromatic roots.
"""

from pathlib import Path
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class ChordAIModelLoader:
    """Loads and validates ChordAI pre-trained model
    
    The ChordAI model is stored in TensorFlow SavedModel format with the following structure:
    - saved_model.pb: Model architecture and graph definition
    - variables/: Directory containing trained weights
    
    Attributes:
        model_path: Path to the ChordAI model directory
    """
    
    def __init__(self, model_path: Path):
        """Initialize loader with path to model weights
        
        Args:
            model_path: Path to the directory containing ChordAI model files
                       (should contain saved_model.pb and variables/ directory)
        """
        self.model_path = Path(model_path)
        logger.info(f"Initialized ChordAIModelLoader with path: {self.model_path}")
    
    def load_model(self) -> Any:
        """Load model weights and return inference-ready model
        
        Returns:
            Loaded TensorFlow model object ready for inference
            
        Raises:
            FileNotFoundError: If model weights file not found at specified path
            RuntimeError: If model loading fails due to corruption or incompatibility
            ImportError: If TensorFlow is not installed
        """
        # Check if TensorFlow is available
        try:
            import tensorflow as tf
        except ImportError as e:
            raise ImportError(
                "Required dependency not found: tensorflow. "
                "Please install with: pip install tensorflow>=2.0.0"
            ) from e
        
        # Verify model path exists
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"ChordAI model weights not found at {self.model_path}. "
                "Please ensure the model file exists."
            )
        
        # Check for required model files
        saved_model_pb = self.model_path / "saved_model.pb"
        variables_dir = self.model_path / "variables"
        
        if not saved_model_pb.exists():
            raise FileNotFoundError(
                f"Model architecture file not found: {saved_model_pb}. "
                "The ChordAI model requires saved_model.pb file."
            )
        
        if not variables_dir.exists() or not variables_dir.is_dir():
            raise FileNotFoundError(
                f"Model weights directory not found: {variables_dir}. "
                "The ChordAI model requires a variables/ directory with trained weights."
            )
        
        # Attempt to load the model
        try:
            logger.info(f"Loading ChordAI model from {self.model_path}")
            model = tf.saved_model.load(str(self.model_path))
            logger.info("ChordAI model loaded successfully")
            return model
        except Exception as e:
            raise RuntimeError(
                f"Failed to load ChordAI model: {str(e)}. "
                "The model file may be corrupted or incompatible with the installed TensorFlow version."
            ) from e
    
    def validate_model(self, model: Any) -> bool:
        """Validate model architecture matches ChordAI specification
        
        Verifies that the loaded model has the expected structure for ChordAI:
        - Has a serving signature for inference
        - Has expected input/output tensors
        
        Args:
            model: Loaded TensorFlow model object
            
        Returns:
            True if model is valid ChordAI model, False otherwise
        """
        try:
            # Check if model has signatures
            if not hasattr(model, 'signatures'):
                logger.error("Model does not have signatures attribute")
                return False
            
            # Get available signatures
            signatures = model.signatures
            if not signatures:
                logger.error("Model has no available signatures")
                return False
            
            # Check for serving_default signature (standard TensorFlow serving signature)
            if 'serving_default' not in signatures:
                logger.warning(
                    f"Model does not have 'serving_default' signature. "
                    f"Available signatures: {list(signatures.keys())}"
                )
                # If serving_default is not available, check if there's at least one signature
                if len(signatures) == 0:
                    logger.error("No valid signatures found in model")
                    return False
            
            # Get the inference function
            if 'serving_default' in signatures:
                infer_fn = signatures['serving_default']
            else:
                # Use the first available signature
                infer_fn = list(signatures.values())[0]
            
            # Validate that the signature has inputs and outputs
            if not hasattr(infer_fn, 'structured_input_signature'):
                logger.error("Inference function does not have structured_input_signature")
                return False
            
            if not hasattr(infer_fn, 'structured_outputs'):
                logger.error("Inference function does not have structured_outputs")
                return False
            
            logger.info("Model validation passed: ChordAI model structure is valid")
            return True
            
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            return False
