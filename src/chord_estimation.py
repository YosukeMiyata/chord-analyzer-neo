"""Chord Estimation Module - Audio chord recognition and analysis"""

import librosa
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
import logging

from src.models import ChordSegment, ChordQuality

logger = logging.getLogger(__name__)


class ChordEstimationModule:
    """Module for estimating chord progressions from audio"""
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize chord estimation module with ChordAI model

        Args:
            model_path: Path to ChordAI pre-trained model directory.
                       If None, uses default path 'models/chordai'

        Raises:
            ImportError: If required dependencies (tensorflow) are not installed
            FileNotFoundError: If model weights not found at specified path
            RuntimeError: If model loading or validation fails
        """
        # Set model path with default
        if model_path is None:
            model_path = Path("models/chordai")
        self.model_path = model_path

        # Chord recognition parameters
        self.hop_length = 512
        self.n_fft = 2048
        self.frame_duration = 0.5  # seconds per chord segment

        # Verify dependencies at initialization
        self._verify_dependencies()

        # Load ChordAI model
        try:
            from src.chordai_loader import ChordAIModelLoader
            from src.chordai_inference import ChordAIInferenceEngine

            logger.info(f"Loading ChordAI model from {self.model_path}")

            # Initialize model loader
            self.chordai_loader = ChordAIModelLoader(self.model_path)

            # Load the model
            self.model = self.chordai_loader.load_model()

            # Validate model architecture
            if not self.chordai_loader.validate_model(self.model):
                raise ValueError(
                    f"Invalid model architecture. Expected ChordAI model but got incompatible model."
                )

            # Initialize inference engine
            self.inference_engine = ChordAIInferenceEngine(self.model)

            logger.info("ChordEstimationModule initialized with ChordAI model")

        except ImportError as e:
            logger.error(f"Failed to import ChordAI components: {e}")
            raise
        except (FileNotFoundError, RuntimeError, ValueError) as e:
            logger.error(f"Failed to load ChordAI model: {e}")
            raise

    def _verify_dependencies(self):
        """Verify that all required dependencies are installed

        Raises:
            ImportError: If required dependencies are missing with installation instructions
        """
        missing_deps = []

        # Check for TensorFlow
        try:
            import tensorflow as tf
            # Verify version is compatible (>= 2.0)
            tf_version = tf.__version__
            major_version = int(tf_version.split('.')[0])
            if major_version < 2:
                missing_deps.append(
                    f"tensorflow>={2}.0 (found incompatible version {tf_version})"
                )
        except ImportError:
            missing_deps.append("tensorflow>=2.0")

        # Check for numpy (should already be present)
        try:
            import numpy
        except ImportError:
            missing_deps.append("numpy")

        # Check for librosa (should already be present)
        try:
            import librosa
        except ImportError:
            missing_deps.append("librosa")

        if missing_deps:
            deps_list = ", ".join(missing_deps)
            raise ImportError(
                f"Required dependencies not found: {deps_list}. "
                f"Please install with: pip install {' '.join(missing_deps)}"
            )
    
    def separate_vocals(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Separate vocals from audio using source separation
        
        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            Audio with vocals removed (accompaniment only)
            
        Raises:
            RuntimeError: If vocal separation fails
        """
        try:
            logger.info("Starting vocal separation")
            
            # For now, we'll use a simple approach
            # In production, this would use demucs or spleeter
            # TODO: Integrate demucs for high-quality vocal separation
            
            # Ensure audio is mono
            if audio.ndim > 1:
                audio = librosa.to_mono(audio)
            
            # Verify sample rate is preserved
            original_sr = sample_rate
            
            # Simple harmonic-percussive separation as placeholder
            # This separates harmonic (tonal) from percussive components
            harmonic, percussive = librosa.effects.hpss(audio)
            
            # Use harmonic component (approximates accompaniment)
            separated_audio = harmonic
            
            logger.info(
                f"Vocal separation completed. "
                f"Original SR: {original_sr}, Output SR: {sample_rate}"
            )
            
            return separated_audio
            
        except Exception as e:
            logger.error(f"Vocal separation failed: {e}")
            raise RuntimeError(f"Vocal separation failed: {e}")
    
    def extract_chroma(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Extract chroma features from audio
        
        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            12-dimensional chroma vectors over time (shape: [12, n_frames])
        """
        logger.info("Extracting chroma features")
        
        # Ensure audio is mono
        if audio.ndim > 1:
            audio = librosa.to_mono(audio)
        
        # Extract chroma features using CQT (Constant-Q Transform)
        chroma = librosa.feature.chroma_cqt(
            y=audio,
            sr=sample_rate,
            hop_length=self.hop_length,
            n_chroma=12
        )
        
        # Handle silent regions (set to zero vector)
        rms = librosa.feature.rms(y=audio, hop_length=self.hop_length)[0]
        silence_threshold = 0.01
        silent_frames = rms < silence_threshold
        chroma[:, silent_frames] = 0.0
        
        logger.info(f"Chroma features extracted: shape={chroma.shape}")
        
        return chroma
    
    def detect_bass_notes(
        self, 
        audio: np.ndarray, 
        sample_rate: int
    ) -> List[Tuple[float, str]]:
        """
        Detect bass notes for slash chord identification
        
        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            List of (timestamp, note) tuples
        """
        logger.info("Detecting bass notes")
        
        # Ensure audio is mono
        if audio.ndim > 1:
            audio = librosa.to_mono(audio)
        
        # Extract pitch using piptrack with wider frequency range
        # Use a wider range to capture bass notes in various octaves
        pitches, magnitudes = librosa.piptrack(
            y=audio,
            sr=sample_rate,
            hop_length=self.hop_length,
            fmin=librosa.note_to_hz('C1'),  # Wider range from C1
            fmax=librosa.note_to_hz('C6')   # to C6 to capture all bass notes
        )
        
        bass_notes = []
        
        # Extract dominant pitch at each frame, focusing on lower frequencies
        for t in range(pitches.shape[1]):
            # Get all pitches with significant magnitude
            frame_magnitudes = magnitudes[:, t]
            frame_pitches = pitches[:, t]
            
            # Find pitches with magnitude above threshold
            threshold = frame_magnitudes.max() * 0.1 if frame_magnitudes.max() > 0 else 0
            significant_indices = np.where(frame_magnitudes > threshold)[0]
            
            if len(significant_indices) > 0:
                # Among significant pitches, find the lowest one (bass note)
                significant_pitches = frame_pitches[significant_indices]
                significant_pitches = significant_pitches[significant_pitches > 0]
                
                if len(significant_pitches) > 0:
                    # Take the lowest pitch as the bass note
                    bass_pitch = significant_pitches.min()
                    
                    # Convert Hz to note name
                    note = librosa.hz_to_note(bass_pitch)
                    timestamp = librosa.frames_to_time(t, sr=sample_rate, hop_length=self.hop_length)
                    bass_notes.append((timestamp, note))
        
        logger.info(f"Detected {len(bass_notes)} bass note events")
        
        return bass_notes
    
    def estimate_chords(
        self,
        audio: np.ndarray,
        sample_rate: int,
        use_vocal_separation: bool = True
    ) -> List[ChordSegment]:
        """
        Estimate chord progression from audio
        
        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate of the audio
            use_vocal_separation: Whether to remove vocals before analysis
            
        Returns:
            List of ChordSegment objects
        """
        logger.info("Starting chord estimation")
        
        # Step 1: Vocal separation (optional)
        if use_vocal_separation:
            audio = self.separate_vocals(audio, sample_rate)
        
        # Step 2: Extract chroma features
        chroma = self.extract_chroma(audio, sample_rate)
        
        # Step 3: Chord recognition using ChordAI model
        chord_progression = self._chordai_recognition(chroma, sample_rate)
        
        # Step 4: Detect bass notes for slash chords
        bass_notes = self.detect_bass_notes(audio, sample_rate)
        
        # Step 5: Match bass notes to chord segments
        for chord_segment in chord_progression:
            # If ChordAI already provided a bass note, preserve it
            if chord_segment.bass_note is not None:
                # Handle root position chords: if bass_note matches root, clear it
                if chord_segment.bass_note == chord_segment.root:
                    chord_segment.bass_note = None
                    logger.debug(f"Root position chord detected: {chord_segment.root} at {chord_segment.start_time:.2f}s")
                else:
                    logger.debug(f"ChordAI bass note preserved: {chord_segment.root}/{chord_segment.bass_note} at {chord_segment.start_time:.2f}s")
                continue
            
            # Only use detected bass notes if ChordAI didn't provide one
            # Find bass notes that occur during this chord segment
            segment_bass_notes = [
                note for timestamp, note in bass_notes
                if chord_segment.start_time <= timestamp < chord_segment.end_time
            ]
            
            if segment_bass_notes:
                # Use the most common bass note in this segment
                from collections import Counter
                most_common_bass = Counter(segment_bass_notes).most_common(1)[0][0]
                
                # Extract just the note name without octave (e.g., "C2" -> "C")
                bass_note_name = most_common_bass[:-1] if most_common_bass[-1].isdigit() else most_common_bass
                
                # Only set bass_note if it differs from the chord root
                if bass_note_name != chord_segment.root:
                    chord_segment.bass_note = bass_note_name
                    logger.debug(f"Detected bass note applied: {chord_segment.root}/{bass_note_name} at {chord_segment.start_time:.2f}s")
        
        logger.info(f"Chord estimation completed: {len(chord_progression)} segments")
        
        return chord_progression

    def _chordai_recognition(
        self,
        chroma: np.ndarray,
        sample_rate: int
    ) -> List[ChordSegment]:
        """ChordAI-based chord recognition

        Uses the ChordAI pre-trained model to recognize chords from chroma features.
        The method passes chroma features to the inference engine, receives ChordPrediction
        objects, and maps them to ChordSegment objects using the ChordAIOutputMapper.

        Args:
            chroma: Chroma features as numpy array with shape (12, n_frames)
                   where 12 represents the pitch classes and n_frames is the
                   number of time frames
            sample_rate: Audio sample rate in Hz (e.g., 22050, 44100)

        Returns:
            List of ChordSegment objects with timing, root, quality, bass_note,
            and confidence information

        Raises:
            RuntimeError: If ChordAI model inference fails
        """
        from src.chordai_mapper import ChordAIOutputMapper

        logger.info("Running ChordAI-based chord recognition")

        try:
            # Call inference engine with chroma features
            predictions = self.inference_engine.predict_chords(
                chroma=chroma,
                sample_rate=sample_rate,
                frame_duration=self.frame_duration
            )

            # Map ChordPrediction objects to ChordSegment objects
            chord_segments = []
            for prediction in predictions:
                segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
                chord_segments.append(segment)

            logger.info(f"ChordAI recognition completed: {len(chord_segments)} segments")
            return chord_segments

        except Exception as e:
            raise RuntimeError(
                f"ChordAI recognition failed: {str(e)}"
            ) from e

    
    


