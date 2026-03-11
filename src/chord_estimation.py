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
        
        # Step 3: Chord recognition
        # TODO: Implement full chord recognition with ML model
        # For now, use a simple template matching approach
        chord_progression = self._simple_chord_recognition(chroma, sample_rate)
        
        # Step 4: Detect bass notes for slash chords
        bass_notes = self.detect_bass_notes(audio, sample_rate)
        
        # Step 5: Match bass notes to chord segments
        for chord_segment in chord_progression:
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
                    logger.debug(f"Slash chord detected: {chord_segment.root}/{bass_note_name} at {chord_segment.start_time:.2f}s")
        
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
        # Define chord templates (major, minor, dominant 7th, major 7th, sus4, diminished)
        chord_templates = {
            # Major triads (root, major 3rd, perfect 5th)
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
            
            # Minor triads (root, minor 3rd, perfect 5th)
            'Cm': np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]),
            'C#m': np.array([0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]),
            'Dm': np.array([0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0]),
            'D#m': np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]),
            'Em': np.array([0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1]),
            'Fm': np.array([1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0]),
            'F#m': np.array([0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0]),
            'Gm': np.array([0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0]),
            'G#m': np.array([0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1]),
            'Am': np.array([1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0]),
            'A#m': np.array([0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]),
            'Bm': np.array([0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1]),
            
            # Dominant 7th (root, major 3rd, perfect 5th, minor 7th)
            'C7': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]),
            'C#7': np.array([0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1]),
            'D7': np.array([1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0]),
            'D#7': np.array([0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0]),
            'E7': np.array([0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]),
            'F7': np.array([1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0]),
            'F#7': np.array([0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0]),
            'G7': np.array([0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1]),
            'G#7': np.array([1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0]),
            'A7': np.array([0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0]),
            'A#7': np.array([0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0]),
            'B7': np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1]),
            
            # Major 7th (root, major 3rd, perfect 5th, major 7th)
            'Cmaj7': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1]),
            'C#maj7': np.array([1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0]),
            'Dmaj7': np.array([0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0]),
            'D#maj7': np.array([0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0]),
            'Emaj7': np.array([0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1]),
            'Fmaj7': np.array([1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0]),
            'F#maj7': np.array([0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0]),
            'Gmaj7': np.array([0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1]),
            'G#maj7': np.array([1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0]),
            'Amaj7': np.array([0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0]),
            'A#maj7': np.array([0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0]),
            'Bmaj7': np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1]),
            
            # Sus4 (root, perfect 4th, perfect 5th)
            'Csus4': np.array([1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0]),
            'C#sus4': np.array([0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0]),
            'Dsus4': np.array([0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0]),
            'D#sus4': np.array([0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0]),
            'Esus4': np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1]),
            'Fsus4': np.array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]),
            'F#sus4': np.array([0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]),
            'Gsus4': np.array([1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0]),
            'G#sus4': np.array([0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0]),
            'Asus4': np.array([0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0]),
            'A#sus4': np.array([0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0]),
            'Bsus4': np.array([0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1]),
            
            # Diminished (root, minor 3rd, diminished 5th)
            'Cdim': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]),
            'C#dim': np.array([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]),
            'Ddim': np.array([0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0]),
            'D#dim': np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]),
            'Edim': np.array([0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]),
            'Fdim': np.array([0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1]),
            'F#dim': np.array([1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0]),
            'Gdim': np.array([0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]),
            'G#dim': np.array([0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1]),
            'Adim': np.array([1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0]),
            'A#dim': np.array([0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]),
            'Bdim': np.array([0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1]),
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
            
            # Check if the best match is a 7th chord and verify the 7th note is actually present
            if best_chord != 'N' and ('7' in best_chord or 'maj7' in best_chord):
                # Map root notes to their positions in the chroma vector
                note_to_index = {
                    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
                }
                
                # Extract root from chord name
                root_note = best_chord.replace('maj7', '').replace('7', '').replace('m', '').replace('sus4', '').replace('dim', '')
                
                if root_note in note_to_index:
                    root_index = note_to_index[root_note]
                    
                    # Calculate 7th note position
                    if 'maj7' in best_chord:
                        # Major 7th is 11 semitones above root
                        seventh_index = (root_index + 11) % 12
                    else:
                        # Dominant 7th is 10 semitones above root
                        seventh_index = (root_index + 10) % 12
                    
                    # Check if the 7th note has significant energy (threshold: 0.15)
                    seventh_energy = segment_chroma[seventh_index]
                    
                    if seventh_energy < 0.15:
                        # 7th note is weak, fall back to the corresponding triad
                        if 'maj7' in best_chord:
                            # Replace maj7 with plain major triad
                            best_chord = root_note
                        elif best_chord.endswith('7') and 'm' not in best_chord:
                            # Replace dominant 7 with plain major triad
                            best_chord = root_note
                        # Note: We don't modify minor 7th chords (Cm7) as they're not in the templates
            
            # Create chord segment
            start_time = librosa.frames_to_time(i, sr=sample_rate, hop_length=self.hop_length)
            end_time = librosa.frames_to_time(end_frame, sr=sample_rate, hop_length=self.hop_length)
            
            # Determine quality from template name
            quality = self._extract_quality_from_template_name(best_chord)
            
            # Extract root note from template name
            root = self._extract_root_from_template_name(best_chord)
            
            # Detect extensions (7th, 9th, 11th, 13th, sus4)
            extensions = self._detect_extensions(segment_chroma, root, quality)
            
            if best_chord != 'N':
                chord_segment = ChordSegment(
                    start_time=start_time,
                    end_time=end_time,
                    root=root,
                    quality=quality,
                    extensions=extensions,
                    confidence=float(best_score)
                )
                chord_segments.append(chord_segment)
        
        return chord_segments
    
    def _detect_extensions(self, chroma: np.ndarray, root: str, quality: ChordQuality) -> List[str]:
            """
            Detect chord extensions (7th, 9th, 11th, 13th) and alterations (sus4)

            Args:
                chroma: Normalized chroma vector for the segment
                root: Root note of the chord
                quality: Chord quality (to avoid redundant extension detection)

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

            # Threshold for detecting extensions
            extension_threshold = 0.15

            # Detect 7th intervals (only if not already in quality)
            # Minor 7th = 10 semitones from root
            # Major 7th = 11 semitones from root
            minor_seventh_index = (root_index + 10) % 12
            major_seventh_index = (root_index + 11) % 12

            # Only add 7th to extensions if it's not already represented by the quality
            if quality not in [ChordQuality.DOMINANT7, ChordQuality.MAJOR7, ChordQuality.MINOR7]:
                if chroma[minor_seventh_index] > extension_threshold:
                    extensions.append('7')
                elif chroma[major_seventh_index] > extension_threshold:
                    extensions.append('maj7')

            # Detect sus4 (only if not already in quality)
            # Perfect 4th = 5 semitones from root
            # Check if 3rd is absent and 4th is present
            major_third_index = (root_index + 4) % 12
            minor_third_index = (root_index + 3) % 12
            fourth_index = (root_index + 5) % 12

            if quality not in [ChordQuality.SUS4, ChordQuality.SUS2]:
                # Sus4 is when 4th is present and 3rd is weak/absent
                has_fourth = chroma[fourth_index] > extension_threshold
                has_third = (chroma[major_third_index] > extension_threshold or 
                            chroma[minor_third_index] > extension_threshold)

                if has_fourth and not has_third:
                    extensions.append('sus4')

            # Extension intervals from root
            # 9th = 2 semitones (whole step above octave)
            # 11th = 5 semitones (perfect fourth above octave)
            # 13th = 9 semitones (major sixth above octave)
            ninth_index = (root_index + 2) % 12
            eleventh_index = (root_index + 5) % 12
            thirteenth_index = (root_index + 9) % 12

            if chroma[ninth_index] > extension_threshold:
                extensions.append('9')

            if chroma[eleventh_index] > extension_threshold:
                # Only add 11th if we didn't already add sus4 (both use index 5)
                # and if the quality is not SUS4 (to avoid redundancy)
                if 'sus4' not in extensions and quality not in [ChordQuality.SUS4, ChordQuality.SUS2]:
                    extensions.append('11')

            if chroma[thirteenth_index] > extension_threshold:
                extensions.append('13')

            return extensions
    def _extract_quality_from_template_name(self, chord_name: str) -> ChordQuality:
        """
        Extract chord quality from template name

        Args:
            chord_name: Template name (e.g., 'C', 'Cm', 'C7', 'Cmaj7', 'Csus4', 'Cdim')

        Returns:
            ChordQuality enum value
        """
        # Handle 'N' (no chord) case
        if chord_name == 'N':
            return ChordQuality.MAJOR

        # Check for specific quality patterns in the template name
        if 'maj7' in chord_name:
            return ChordQuality.MAJOR7
        elif chord_name.endswith('7'):
            return ChordQuality.DOMINANT7
        elif chord_name.endswith('m'):
            return ChordQuality.MINOR
        elif 'sus4' in chord_name:
            return ChordQuality.SUS4
        elif 'dim' in chord_name:
            return ChordQuality.DIMINISHED
        else:
            # Default to major for simple root names (C, D, E, etc.)
            return ChordQuality.MAJOR
    def _extract_root_from_template_name(self, chord_name: str) -> str:
        """
        Extract root note from template name

        Args:
            chord_name: Template name (e.g., 'C', 'Cm', 'C7', 'Cmaj7', 'Csus4', 'Cdim')

        Returns:
            Root note (e.g., 'C', 'C#', 'D')
        """
        # Handle 'N' (no chord) case
        if chord_name == 'N':
            return 'N'

        # Extract root note by removing quality suffixes
        # Check for two-character roots first (C#, D#, F#, G#, A#)
        if len(chord_name) >= 2 and chord_name[1] == '#':
            return chord_name[:2]
        else:
            # Single character root (C, D, E, F, G, A, B)
            return chord_name[0]


