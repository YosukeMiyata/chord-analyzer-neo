"""Tests for AudioProcessingEngine"""

import pytest
import numpy as np
from pathlib import Path
from src.audio_engine import AudioProcessingEngine


@pytest.fixture
def audio_engine():
    """Create AudioProcessingEngine instance"""
    return AudioProcessingEngine()


def test_audio_engine_initialization(audio_engine):
    """Test AudioProcessingEngine initialization"""
    assert audio_engine.audio_data is None
    assert audio_engine.sample_rate is None
    assert audio_engine.duration is None
    assert audio_engine.channels is None
    assert audio_engine.current_position == 0.0
    assert audio_engine.volume == 1.0
    assert audio_engine.is_playing is False


def test_load_nonexistent_file(audio_engine):
    """Test loading a non-existent file raises FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        audio_engine.load_audio_file(Path("nonexistent.wav"))


def test_load_unsupported_format(audio_engine, tmp_path):
    """Test loading unsupported format raises ValueError"""
    # Create a dummy file with unsupported extension
    unsupported_file = tmp_path / "test.txt"
    unsupported_file.write_text("dummy content")
    
    with pytest.raises(ValueError, match="Unsupported audio format"):
        audio_engine.load_audio_file(unsupported_file)


def test_get_audio_info_without_loading(audio_engine):
    """Test getting audio info without loading file raises RuntimeError"""
    with pytest.raises(RuntimeError, match="No audio file loaded"):
        audio_engine.get_audio_info()


def test_play_without_loading(audio_engine):
    """Test playing without loading file raises RuntimeError"""
    with pytest.raises(RuntimeError, match="No audio file loaded"):
        audio_engine.play()


def test_pause_when_not_playing(audio_engine):
    """Test pausing when not playing (should not raise error)"""
    audio_engine.pause()  # Should not raise


def test_stop(audio_engine):
    """Test stop resets position"""
    audio_engine.current_position = 10.0
    audio_engine.is_playing = True
    audio_engine.is_paused = True
    
    audio_engine.stop()
    
    assert audio_engine.current_position == 0.0
    assert audio_engine.is_playing is False
    assert audio_engine.is_paused is False


def test_seek_without_loading(audio_engine):
    """Test seeking without loading file raises RuntimeError"""
    with pytest.raises(RuntimeError, match="No audio file loaded"):
        audio_engine.seek(5.0)


def test_set_volume_valid(audio_engine):
    """Test setting valid volume"""
    audio_engine.set_volume(0.5)
    assert audio_engine.volume == 0.5
    
    audio_engine.set_volume(0.0)
    assert audio_engine.volume == 0.0
    
    audio_engine.set_volume(1.0)
    assert audio_engine.volume == 1.0


def test_set_volume_invalid(audio_engine):
    """Test setting invalid volume raises ValueError"""
    with pytest.raises(ValueError, match="Volume must be between 0.0 and 1.0"):
        audio_engine.set_volume(-0.1)
    
    with pytest.raises(ValueError, match="Volume must be between 0.0 and 1.0"):
        audio_engine.set_volume(1.1)


def test_get_current_position(audio_engine):
    """Test getting current position"""
    assert audio_engine.get_current_position() == 0.0
    
    audio_engine.current_position = 5.5
    assert audio_engine.get_current_position() == 5.5


def test_supported_formats():
    """Test supported audio formats"""
    expected_formats = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    assert AudioProcessingEngine.SUPPORTED_FORMATS == expected_formats
