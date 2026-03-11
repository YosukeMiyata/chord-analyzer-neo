"""ChordAI Inference Engine

This module provides functionality to run inference on audio features using the
ChordAI pre-trained model.

The ChordAI model outputs predictions for 529 chord classes across all 12 chromatic roots.
"""

import numpy as np
from typing import Any, List
import logging

from src.chordai_models import ChordPrediction

logger = logging.getLogger(__name__)


class ChordAIInferenceEngine:
    """Runs inference on chroma features using ChordAI model
    
    The inference engine processes chroma features (12-dimensional pitch class vectors)
    through the loaded ChordAI model to generate chord predictions with timing,
    root note, quality, bass note, and confidence information.
    
    Attributes:
        model: Loaded TensorFlow ChordAI model
    """
    
    def __init__(self, model: Any):
        """Initialize inference engine with loaded model
        
        Args:
            model: Loaded TensorFlow model object from ChordAIModelLoader
        """
        self.model = model
        
        # Get the inference function from model signatures
        if hasattr(model, 'signatures'):
            if 'serving_default' in model.signatures:
                self.infer_fn = model.signatures['serving_default']
            elif len(model.signatures) > 0:
                # Use the first available signature
                self.infer_fn = list(model.signatures.values())[0]
            else:
                raise ValueError("Model does not have valid signatures for inference")
        else:
            raise ValueError("Model does not have valid signatures for inference")
        
        logger.info("ChordAIInferenceEngine initialized")
    
    def predict_chords(
        self,
        audio: np.ndarray,
        sample_rate: int,
        frame_duration: float = 0.5
    ) -> List[ChordPrediction]:
        """Run inference on audio using CQT features
        
        Processes audio through CQT feature extraction and the ChordAI model 
        to generate chord predictions.
        
        Args:
            audio: Audio data as numpy array (mono)
            sample_rate: Audio sample rate in Hz (e.g., 22050, 44100)
            frame_duration: Duration of each chord segment in seconds (default: 0.5)
            
        Returns:
            List of ChordPrediction objects with timing, root, quality, bass_note,
            and confidence information
            
        Raises:
            ValueError: If audio has invalid shape
            RuntimeError: If model inference fails
        """
        import librosa
        
        # Validate input
        if audio.ndim > 1:
            audio = librosa.to_mono(audio)
        
        logger.info(f"Running ChordAI inference on audio (length: {len(audio)} samples)")
        
        try:
            # Extract CQT features (252 bins, 36 bins/octave * 7 octaves)
            # This matches the model's expected input format
            cqt = librosa.cqt(
                y=audio,
                sr=sample_rate,
                hop_length=512,
                n_bins=252,
                bins_per_octave=36
            )
            
            # CQT is complex-valued, convert to magnitude and phase
            cqt_mag = np.abs(cqt)  # Magnitude
            cqt_phase = np.angle(cqt)  # Phase
            
            # Transpose to (n_frames, 252) and normalize
            cqt_mag = cqt_mag.T
            cqt_phase = cqt_phase.T
            
            # Normalize magnitude to [0, 1] range
            cqt_mag = cqt_mag / (np.max(cqt_mag) + 1e-8)
            
            # Normalize phase to [-1, 1] range
            cqt_phase = cqt_phase / np.pi
            
            # Process through model
            predictions = self._run_inference_batch(cqt_mag, cqt_phase, frame_duration)
            
            logger.info(f"Generated {len(predictions)} chord predictions")
            return predictions
            
        except Exception as e:
            raise RuntimeError(
                f"ChordAI inference failed: {str(e)}. "
                f"Audio shape: {audio.shape}"
            ) from e
    
    def _run_inference_batch(
        self,
        chroma: np.ndarray,
        frame_duration: float
    ) -> List[ChordPrediction]:
        """Run inference on a batch of chroma frames
        
        Converts chroma features to CQT format expected by the model,
        runs inference, and parses the output into ChordPrediction objects.
        
        Args:
            chroma: Chroma features (12, n_frames)
            frame_duration: Duration per frame in seconds
            
        Returns:
            List of ChordPrediction objects
        """
        import tensorflow as tf
        import json
        from pathlib import Path
        
        # Load chord index mapping
        index_path = Path(__file__).parent.parent / "models" / "chordai" / "index.json"
        if not index_path.exists():
            raise FileNotFoundError(
                f"Chord index file not found at {index_path}. "
                "Please ensure index.json is in the models/chordai directory."
            )
        
        with open(index_path, 'r') as f:
            chord_index = json.load(f)
        
        # Convert chroma to CQT-like features
        # The model expects (batch, time, 252, 2) where:
        # - 252 is the number of frequency bins (CQT with 36 bins/octave * 7 octaves)
        # - 2 channels (magnitude and phase, or real/imaginary)
        # 
        # For now, we'll create a simplified mapping from chroma (12 bins) to CQT (252 bins)
        # by repeating and interpolating the chroma features
        cqt_features = self._chroma_to_cqt_features(chroma)
        
        # Pad or chunk the time dimension to multiples of 256 (model requirement)
        n_frames = cqt_features.shape[0]
        chunk_size = 256
        
        # Pad to nearest multiple of chunk_size
        if n_frames % chunk_size != 0:
            pad_frames = chunk_size - (n_frames % chunk_size)
            cqt_features = np.pad(
                cqt_features,
                ((0, pad_frames), (0, 0), (0, 0)),
                mode='edge'
            )
        
        # Add batch dimension: (time, 252, 2) -> (1, time, 252, 2)
        input_tensor = tf.constant(cqt_features[np.newaxis, :, :, :], dtype=tf.float32)
        
        # Run inference
        output = self.infer_fn(input_1=input_tensor)
        
        # Extract chord predictions from output
        # The key output is 'ccf_1' with shape (batch, time, 529)
        chord_logits = output['ccf_1'].numpy()[0]  # Remove batch dimension: (time, 529)
        
        # Trim back to original length
        chord_logits = chord_logits[:n_frames]
        
        # Apply softmax to convert logits to probabilities
        # Using scipy for numerical stability
        from scipy.special import softmax
        chord_probs = softmax(chord_logits, axis=1)
        
        # Convert predictions to ChordPrediction objects
        predictions = []
        for i in range(n_frames):
            start_time = i * frame_duration
            end_time = (i + 1) * frame_duration
            
            # Get the predicted chord class (highest probability)
            chord_idx = np.argmax(chord_probs[i])
            confidence = float(chord_probs[i, chord_idx])
            
            # Map index to chord label
            chord_label = chord_index[str(chord_idx)]
            
            # Parse chord label into root, quality, and bass_note
            root, quality, bass_note = self._parse_chord_label(chord_label)
            
            prediction = ChordPrediction(
                start_time=start_time,
                end_time=end_time,
                root=root,
                quality=quality,
                bass_note=bass_note,
                confidence=confidence
            )
            predictions.append(prediction)
        
        return predictions
    
    def _chroma_to_cqt_features(self, chroma: np.ndarray) -> np.ndarray:
        """Convert chroma features to CQT-like features expected by the model
        
        Args:
            chroma: Chroma features with shape (12, n_frames)
            
        Returns:
            CQT-like features with shape (n_frames, 252, 2)
        """
        # Transpose to (n_frames, 12)
        chroma_t = chroma.T
        n_frames = chroma_t.shape[0]
        
        # Expand chroma (12 bins) to CQT (252 bins) by repeating
        # 252 / 12 = 21, so repeat each chroma bin 21 times
        cqt_expanded = np.repeat(chroma_t, 21, axis=1)  # (n_frames, 252)
        
        # Create 2-channel representation (magnitude and phase)
        # For simplicity, use the chroma values as magnitude and zeros as phase
        cqt_features = np.stack([cqt_expanded, np.zeros_like(cqt_expanded)], axis=-1)
        
        return cqt_features  # (n_frames, 252, 2)
    
    def _parse_chord_label(self, chord_label: str) -> tuple:
        """Parse chord label into root, quality, and bass_note
        
        Args:
            chord_label: Chord label string (e.g., "CM7", "Am", "N.C.", "G/B")
            
        Returns:
            Tuple of (root, quality, bass_note)
        """
        # Handle "N.C." (no chord) - skip these predictions
        # We'll filter them out later, but for now return a placeholder
        if chord_label == "N.C.":
            return ("C", "N.C.", None)  # Use C as placeholder root
        
        # Handle slash chords (e.g., "C/E")
        if "/" in chord_label:
            chord_part, bass_note = chord_label.split("/")
            root, quality = self._parse_chord_part(chord_part)
            return (root, quality, bass_note)
        
        # Parse regular chord
        root, quality = self._parse_chord_part(chord_label)
        return (root, quality, None)
    
    def _parse_chord_part(self, chord_part: str) -> tuple:
        """Parse chord part (without bass note) into root and quality
        
        Args:
            chord_part: Chord string without bass note (e.g., "CM7", "Am", "C5")
            
        Returns:
            Tuple of (root, quality)
        """
        # Extract root note (1-2 characters: C, Db, etc.)
        if len(chord_part) >= 2 and chord_part[1] in ['b', '#']:
            root = chord_part[:2]
            quality_str = chord_part[2:]
        else:
            root = chord_part[0]
            quality_str = chord_part[1:]
        
        # Map quality string to standardized format
        # If no quality specified, it's major
        if not quality_str:
            quality = "maj"
        elif quality_str == "m":
            quality = "min"
        elif quality_str == "5":
            quality = "5"  # Power chord
        elif quality_str == "dim":
            quality = "dim"
        elif quality_str == "aug":
            quality = "aug"
        elif quality_str.startswith("sus"):
            quality = quality_str  # sus4, sus2
        else:
            # Keep complex qualities as-is (7, M7, m7, etc.)
            quality = quality_str
        
        return (root, quality)
