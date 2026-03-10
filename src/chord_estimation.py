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
        Initialize chord estimation module
        
        Args:
            model_path: Optional path to pre-trained model
        """
        self.model_path = model_path
        self.model = None
        
        # Chord recognition parameters
        self.hop_length = 512
        self.n_fft = 2048
        self.frame_duration = 0.5  # seconds per chord segment
        
        logger.info("ChordEstimationModule initialized")
    
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
        
        # Extract low-frequency content
        # Apply high-pass filter to isolate bass frequencies (20-250 Hz)
        bass_audio = librosa.effects.preemphasis(audio, coef=0.97)
        
        # Extract pitch using piptrack
        pitches, magnitudes = librosa.piptrack(
            y=bass_audio,
            sr=sample_rate,
            hop_length=self.hop_length,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C4')
        )
        
        bass_notes = []
        
        # Extract dominant pitch at each frame
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            
            if pitch > 0:
                # Convert Hz to note name
                note = librosa.hz_to_note(pitch)
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
        
        # Step 3: Chord recognition
        # TODO: Implement full chord recognition with ML model
        # For now, use a simple template matching approach
        chord_progression = self._simple_chord_recognition(chroma, sample_rate)
        
        logger.info(f"Chord estimation completed: {len(chord_progression)} segments")
        
        return chord_progression
    
    def _simple_chord_recognition(
        self,
        chroma: np.ndarray,
        sample_rate: int
    ) -> List[ChordSegment]:
        """
        Simple chord recognition using template matching
        
        This is a placeholder implementation. In production, this would use
        a trained ML model (HMM, CNN, or transformer-based).
        
        Args:
            chroma: Chroma features (12 x n_frames)
            sample_rate: Sample rate
            
        Returns:
            List of ChordSegment objects
        """
        # Define chord templates (major and minor triads)
        chord_templates = {
            'C': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]),
            'C#': np.array([0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0]),
            'D': np.array([0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0]),
            'D#': np.array([0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0]),
            'E': np.array([0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1]),
            'F': np.array([1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]),
            'F#': np.array([0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0]),
            'G': np.array([0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1]),
            'G#': np.array([1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0]),
            'A': np.array([0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0]),
            'A#': np.array([0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0]),
            'B': np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1]),
        }
        
        chord_segments = []
        n_frames = chroma.shape[1]
        
        # Process in segments
        frames_per_segment = int(self.frame_duration * sample_rate / self.hop_length)
        
        for i in range(0, n_frames, frames_per_segment):
            end_frame = min(i + frames_per_segment, n_frames)
            segment_chroma = chroma[:, i:end_frame].mean(axis=1)
            
            # Normalize
            if segment_chroma.sum() > 0:
                segment_chroma = segment_chroma / segment_chroma.sum()
            
            # Find best matching chord
            best_chord = 'N'  # No chord
            best_score = 0.0
            
            for chord_name, template in chord_templates.items():
                score = np.dot(segment_chroma, template)
                if score > best_score:
                    best_score = score
                    best_chord = chord_name
            
            # Create chord segment
            start_time = librosa.frames_to_time(i, sr=sample_rate, hop_length=self.hop_length)
            end_time = librosa.frames_to_time(end_frame, sr=sample_rate, hop_length=self.hop_length)
            
            # Determine quality (simplified - always major for now)
            quality = ChordQuality.MAJOR if best_chord != 'N' else ChordQuality.MAJOR
            
            # Detect extensions (9th, 11th, 13th)
            extensions = self._detect_extensions(segment_chroma, best_chord)
            
            if best_chord != 'N':
                chord_segment = ChordSegment(
                    start_time=start_time,
                    end_time=end_time,
                    root=best_chord,
                    quality=quality,
                    extensions=extensions,
                    confidence=float(best_score)
                )
                chord_segments.append(chord_segment)
        
        return chord_segments
    
    def _detect_extensions(self, chroma: np.ndarray, root: str) -> List[str]:
        """
        Detect chord extensions (9th, 11th, 13th)
        
        Args:
            chroma: Normalized chroma vector for the segment
            root: Root note of the chord
            
        Returns:
            List of detected extensions
        """
        extensions = []
        
        # Map root notes to chroma indices
        note_to_index = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        
        if root not in note_to_index:
            return extensions
        
        root_index = note_to_index[root]
        
        # Extension intervals from root
        # 9th = 2 semitones (whole step above octave)
        # 11th = 5 semitones (perfect fourth above octave)
        # 13th = 9 semitones (major sixth above octave)
        ninth_index = (root_index + 2) % 12
        eleventh_index = (root_index + 5) % 12
        thirteenth_index = (root_index + 9) % 12
        
        # Threshold for detecting extensions
        extension_threshold = 0.15
        
        if chroma[ninth_index] > extension_threshold:
            extensions.append('9')
        
        if chroma[eleventh_index] > extension_threshold:
            extensions.append('11')
        
        if chroma[thirteenth_index] > extension_threshold:
            extensions.append('13')
        
        return extensions
