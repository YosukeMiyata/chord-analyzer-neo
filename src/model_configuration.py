"""Model configuration and management module"""

import json
import tomli
import tomli_w
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.models import ModelConfig


class ModelConfigurationModule:
    """Manages multiple chord estimation models and their configurations"""
    
    def __init__(self, models_dir: Path, config_path: Optional[Path] = None):
        """
        Initialize model configuration module
        
        Args:
            models_dir: Directory containing model files
            config_path: Path to TOML configuration file (default: models_dir/models.toml)
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_path = Path(config_path) if config_path else self.models_dir / "models.toml"
        self._models: Dict[str, ModelConfig] = {}
        self._active_model_id: Optional[str] = None
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load model configurations from TOML file"""
        if not self.config_path.exists():
            # Create default configuration
            self._create_default_config()
            return
        
        try:
            with open(self.config_path, "rb") as f:
                config_data = tomli.load(f)
            
            # Load active model ID
            self._active_model_id = config_data.get("active_model")
            
            # Load model configurations
            models_data = config_data.get("models", [])
            for model_data in models_data:
                model_config = ModelConfig(
                    model_id=model_data["model_id"],
                    model_name=model_data["model_name"],
                    model_path=model_data["model_path"],
                    model_type=model_data["model_type"],
                    description=model_data.get("description", ""),
                    accuracy_metrics=model_data.get("accuracy_metrics", {}),
                    is_default=model_data.get("is_default", False)
                )
                self._models[model_config.model_id] = model_config
            
            # Set active model to default if not set
            if not self._active_model_id:
                default_models = [m for m in self._models.values() if m.is_default]
                if default_models:
                    self._active_model_id = default_models[0].model_id
                elif self._models:
                    self._active_model_id = list(self._models.keys())[0]
        
        except Exception as e:
            raise RuntimeError(f"Failed to load model configuration: {e}")
    
    def _save_config(self) -> None:
        """Save model configurations to TOML file"""
        config_data = {
            "active_model": self._active_model_id,
            "models": [
                {
                    "model_id": model.model_id,
                    "model_name": model.model_name,
                    "model_path": model.model_path,
                    "model_type": model.model_type,
                    "description": model.description,
                    "accuracy_metrics": model.accuracy_metrics,
                    "is_default": model.is_default
                }
                for model in self._models.values()
            ]
        }
        
        try:
            with open(self.config_path, "wb") as f:
                tomli_w.dump(config_data, f)
        except Exception as e:
            raise RuntimeError(f"Failed to save model configuration: {e}")
    
    def _create_default_config(self) -> None:
        """Create default model configuration"""
        default_model = ModelConfig(
            model_id="default_hmm",
            model_name="Default HMM Model",
            model_path="builtin",
            model_type="hmm",
            description="Built-in HMM-based chord estimation model",
            accuracy_metrics={"accuracy": 0.75, "f1_score": 0.72},
            is_default=True
        )
        
        self._models[default_model.model_id] = default_model
        self._active_model_id = default_model.model_id
        self._save_config()
    
    def list_available_models(self) -> List[ModelConfig]:
        """
        List all available models
        
        Returns:
            List of ModelConfig objects
        """
        return list(self._models.values())
    
    def get_active_model(self) -> ModelConfig:
        """
        Get currently active model
        
        Returns:
            Active ModelConfig object
        
        Raises:
            RuntimeError: If no active model is set
        """
        if not self._active_model_id or self._active_model_id not in self._models:
            raise RuntimeError("No active model set")
        
        return self._models[self._active_model_id]
    
    def set_active_model(self, model_id: str) -> None:
        """
        Change active model
        
        Args:
            model_id: ID of the model to activate
        
        Raises:
            ValueError: If model_id does not exist
        """
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' not found")
        
        self._active_model_id = model_id
        self._save_config()
    
    def add_custom_model(
        self,
        model_path: Path,
        model_name: str,
        model_type: str,
        description: str,
        model_id: Optional[str] = None
    ) -> ModelConfig:
        """
        Add custom model
        
        Args:
            model_path: Path to model file
            model_name: Display name for the model
            model_type: Type of model ("tensorflow", "onnx", "pytorch", "hmm")
            description: Model description
            model_id: Optional custom model ID (auto-generated if not provided)
        
        Returns:
            Created ModelConfig object
        
        Raises:
            ValueError: If model_path does not exist or model_type is invalid
        """
        model_path = Path(model_path)
        
        # Validate model path
        if not model_path.exists():
            raise ValueError(f"Model file not found: {model_path}")
        
        # Validate model type
        valid_types = ["tensorflow", "onnx", "pytorch", "hmm"]
        if model_type not in valid_types:
            raise ValueError(f"Invalid model type. Must be one of: {valid_types}")
        
        # Generate model ID if not provided
        if not model_id:
            model_id = f"custom_{model_name.lower().replace(' ', '_')}"
        
        # Check for duplicate model ID
        if model_id in self._models:
            raise ValueError(f"Model ID '{model_id}' already exists")
        
        # Create model config
        model_config = ModelConfig(
            model_id=model_id,
            model_name=model_name,
            model_path=str(model_path),
            model_type=model_type,
            description=description,
            accuracy_metrics={},
            is_default=False
        )
        
        self._models[model_id] = model_config
        self._save_config()
        
        return model_config
    
    def evaluate_model(
        self,
        model_id: str,
        test_audio_files: List[Path],
        ground_truth: List[List[Any]]
    ) -> Dict[str, float]:
        """
        Evaluate model accuracy
        
        Args:
            model_id: ID of the model to evaluate
            test_audio_files: List of test audio file paths
            ground_truth: List of ground truth chord progressions
        
        Returns:
            Dictionary of accuracy metrics (accuracy, precision, recall, f1_score)
        
        Raises:
            ValueError: If model_id does not exist or input lengths don't match
        """
        if model_id not in self._models:
            raise ValueError(f"Model '{model_id}' not found")
        
        if len(test_audio_files) != len(ground_truth):
            raise ValueError("Number of test files must match number of ground truth labels")
        
        if not test_audio_files:
            raise ValueError("No test files provided")
        
        # Initialize counters
        total_segments = 0
        correct_predictions = 0
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        # Import here to avoid circular dependency
        from audio_engine import AudioProcessingEngine
        from chord_estimation import ChordEstimationModule
        
        # Get model config
        model_config = self._models[model_id]
        
        # Create chord estimator with the specified model
        chord_estimator = ChordEstimationModule(
            model_path=Path(model_config.model_path) if model_config.model_path != "builtin" else None
        )
        
        # Evaluate each test file
        for audio_file, truth_chords in zip(test_audio_files, ground_truth):
            try:
                # Load audio
                import librosa
                audio, sr = librosa.load(str(audio_file), sr=22050, mono=True)
                
                # Estimate chords
                predicted_chords = chord_estimator.estimate_chords(
                    audio, sr, use_vocal_separation=False
                )
                
                # Compare predictions with ground truth
                # Simple segment-by-segment comparison
                min_len = min(len(predicted_chords), len(truth_chords))
                total_segments += min_len
                
                for pred, truth in zip(predicted_chords[:min_len], truth_chords[:min_len]):
                    # Check if root and quality match
                    if hasattr(truth, 'root') and hasattr(truth, 'quality'):
                        if pred.root == truth.root and pred.quality == truth.quality:
                            correct_predictions += 1
                            true_positives += 1
                        else:
                            false_positives += 1
                            false_negatives += 1
                    
            except Exception as e:
                print(f"Warning: Failed to evaluate {audio_file}: {e}")
                continue
        
        # Calculate metrics
        if total_segments == 0:
            return {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0
            }
        
        accuracy = correct_predictions / total_segments if total_segments > 0 else 0.0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        metrics = {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1_score, 4)
        }
        
        # Update model's accuracy metrics
        self._models[model_id].accuracy_metrics = metrics
        self._save_config()
        
        return metrics
