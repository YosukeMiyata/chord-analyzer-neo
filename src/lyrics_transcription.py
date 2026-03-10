"""Lyrics Transcription Module - Automatic lyrics transcription using Whisper"""

import whisper
import numpy as np
from typing import List, Tuple, Optional
import logging

from src.models import LyricSegment, ChordSegment

logger = logging.getLogger(__name__)


class LyricsTranscriptionModule:
    """Module for transcribing lyrics from audio using Whisper"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model for lyrics transcription
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        
        logger.info(f"LyricsTranscriptionModule initialized with model size: {model_size}")
    
    def _load_model(self):
        """Lazy load Whisper model"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
    
    def transcribe(
        self,
        audio: np.ndarray,
        sample_rate: int,
        language: str = "ja"
    ) -> List[LyricSegment]:
        """
        Transcribe lyrics from audio with timestamps
        
        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate of the audio
            language: Language code (ja, en, etc.)
            
        Returns:
            List of LyricSegment objects with timestamps
        """
        self._load_model()
        
        logger.info(f"Starting lyrics transcription (language: {language})")
        
        # Ensure audio is mono
        if audio.ndim > 1:
            audio = np.mean(audio, axis=0)
        
        # Whisper expects float32 audio normalized to [-1, 1]
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        # Normalize if needed
        if np.abs(audio).max() > 1.0:
            audio = audio / np.abs(audio).max()
        
        try:
            # Transcribe with word-level timestamps
            result = self.model.transcribe(
                audio,
                language=language,
                word_timestamps=True,
                verbose=False
            )
            
            # Extract lyric segments
            lyric_segments = []
            
            if 'segments' in result:
                for segment in result['segments']:
                    # Create lyric segment
                    lyric_segment = LyricSegment(
                        start_time=segment['start'],
                        end_time=segment['end'],
                        text=segment['text'].strip(),
                        confidence=segment.get('no_speech_prob', 0.0)
                    )
                    lyric_segments.append(lyric_segment)
            
            logger.info(f"Transcription completed: {len(lyric_segments)} segments")
            
            # Return empty list if no lyrics detected
            if not lyric_segments:
                logger.info("No lyrics detected in audio")
                return []
            
            return lyric_segments
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Lyrics transcription failed: {e}")
    
    def align_lyrics_with_chords(
        self,
        lyrics: List[LyricSegment],
        chords: List[ChordSegment]
    ) -> List[Tuple[LyricSegment, List[ChordSegment]]]:
        """
        Align lyrics with chords based on time overlap
        
        Args:
            lyrics: List of lyric segments
            chords: List of chord segments
            
        Returns:
            List of (lyric, associated_chords) tuples
        """
        logger.info("Aligning lyrics with chords")
        
        aligned = []
        
        for lyric in lyrics:
            # Find all chords that overlap with this lyric segment
            overlapping_chords = []
            
            for chord in chords:
                # Check if time ranges overlap
                if self._time_ranges_overlap(
                    lyric.start_time, lyric.end_time,
                    chord.start_time, chord.end_time
                ):
                    overlapping_chords.append(chord)
            
            # Add to aligned list (even if no chords found)
            aligned.append((lyric, overlapping_chords))
        
        logger.info(f"Alignment completed: {len(aligned)} lyric-chord pairs")
        
        return aligned
    
    def _time_ranges_overlap(
        self,
        start1: float,
        end1: float,
        start2: float,
        end2: float
    ) -> bool:
        """
        Check if two time ranges overlap
        
        Args:
            start1, end1: First time range
            start2, end2: Second time range
            
        Returns:
            True if ranges overlap, False otherwise
        """
        # Ranges overlap if one starts before the other ends
        return start1 < end2 and start2 < end1
