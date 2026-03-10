"""Audio Processing Engine - Core audio file handling and analysis orchestration"""

import librosa
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import logging

from src.models import AudioAnalysisResult

logger = logging.getLogger(__name__)


class AudioProcessingEngine:
    """Main audio processing engine for chord analysis"""
    
    SUPPORTED_FORMATS = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    def __init__(self):
        self.audio_data: Optional[np.ndarray] = None
        self.sample_rate: Optional[int] = None
        self.duration: Optional[float] = None
        self.channels: Optional[int] = None
        self.current_position: float = 0.0
        self.volume: float = 1.0
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.current_file_path: Optional[Path] = None
    
    def load_audio_file(self, filepath: Path) -> bool:
        """
        Load an audio file and extract basic information
        
        Args:
            filepath: Path to the audio file
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        # Validate file exists
        if not filepath.exists():
            logger.error(f"Audio file not found: {filepath}")
            raise FileNotFoundError(f"Audio file not found: {filepath}")
        
        # Validate file format
        if filepath.suffix.lower() not in self.SUPPORTED_FORMATS:
            logger.error(f"Unsupported audio format: {filepath.suffix}")
            raise ValueError(
                f"Unsupported audio format: {filepath.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        try:
            # Load audio file using librosa
            logger.info(f"Loading audio file: {filepath}")
            audio_data, sample_rate = librosa.load(
                str(filepath),
                sr=None,  # Preserve original sample rate
                mono=False  # Preserve stereo if present
            )
            
            # Store audio information
            self.audio_data = audio_data
            self.sample_rate = sample_rate
            
            # Calculate duration
            if audio_data.ndim == 1:
                self.duration = len(audio_data) / sample_rate
                self.channels = 1
            else:
                self.duration = audio_data.shape[1] / sample_rate
                self.channels = audio_data.shape[0]
            
            self.current_file_path = filepath
            self.current_position = 0.0
            
            logger.info(
                f"Audio loaded successfully: "
                f"duration={self.duration:.2f}s, "
                f"sample_rate={self.sample_rate}Hz, "
                f"channels={self.channels}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load audio file: {e}")
            # Reset state on error
            self.audio_data = None
            self.sample_rate = None
            self.duration = None
            self.channels = None
            self.current_file_path = None
            raise
    
    def get_audio_info(self) -> dict:
        """
        Get basic information about the loaded audio file
        
        Returns:
            Dictionary containing sample_rate, duration, and channels
        """
        if self.audio_data is None:
            raise RuntimeError("No audio file loaded")
        
        return {
            'sample_rate': self.sample_rate,
            'duration': self.duration,
            'channels': self.channels,
            'filepath': str(self.current_file_path) if self.current_file_path else None
        }
    
    def analyze_audio(self, use_cache: bool = True) -> AudioAnalysisResult:
        """
        Perform complete audio analysis (chords, lyrics, tempo, key)
        
        Args:
            use_cache: Whether to use cached results if available
            
        Returns:
            AudioAnalysisResult containing all analysis data
        """
        if self.audio_data is None:
            raise RuntimeError("No audio file loaded")
        
        # TODO: Implement full analysis pipeline
        # This will be implemented in later tasks
        raise NotImplementedError("Full analysis not yet implemented")
    
    def play(self) -> None:
        """Start audio playback"""
        if self.audio_data is None:
            raise RuntimeError("No audio file loaded")
        
        self.is_playing = True
        self.is_paused = False
        logger.info("Audio playback started")
    
    def pause(self) -> None:
        """Pause audio playback at current position"""
        if not self.is_playing:
            logger.warning("Cannot pause: audio is not playing")
            return
        
        self.is_playing = False
        self.is_paused = True
        logger.info(f"Audio playback paused at {self.current_position:.2f}s")
    
    def stop(self) -> None:
        """Stop audio playback and reset position"""
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0.0
        logger.info("Audio playback stopped")
    
    def seek(self, position_seconds: float) -> None:
        """
        Change playback position
        
        Args:
            position_seconds: Target position in seconds
        """
        if self.audio_data is None:
            raise RuntimeError("No audio file loaded")
        
        if position_seconds < 0 or position_seconds > self.duration:
            raise ValueError(
                f"Invalid seek position: {position_seconds}. "
                f"Must be between 0 and {self.duration}"
            )
        
        self.current_position = position_seconds
        logger.info(f"Seeked to {position_seconds:.2f}s")
    
    def set_volume(self, volume: float) -> None:
        """
        Set playback volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if volume < 0.0 or volume > 1.0:
            raise ValueError(f"Volume must be between 0.0 and 1.0, got {volume}")
        
        self.volume = volume
        logger.info(f"Volume set to {volume:.2f}")
    
    def get_current_position(self) -> float:
        """
        Get current playback position in seconds
        
        Returns:
            Current position in seconds
        """
        return self.current_position
