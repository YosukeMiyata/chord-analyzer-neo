"""Integration test for analyze_audio() method"""

import pytest
import numpy as np
from pathlib import Path
import librosa

from src.audio_engine import AudioProcessingEngine
from src.models import AudioAnalysisResult


@pytest.fixture
def test_audio_file(tmp_path):
    """Create a simple test audio file"""
    # Generate a simple sine wave (440 Hz, 2 seconds)
    sample_rate = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    
    # Save as WAV file
    audio_file = tmp_path / "test_audio.wav"
    import soundfile as sf
    sf.write(str(audio_file), audio, sample_rate)
    
    return audio_file


@pytest.fixture
def audio_engine(tmp_path):
    """Create AudioProcessingEngine with test cache directory"""
    cache_dir = tmp_path / "cache"
    return AudioProcessingEngine(cache_dir=cache_dir)


def test_analyze_audio_full_pipeline(audio_engine, test_audio_file, monkeypatch):
    """Test full analyze_audio pipeline with real audio"""
    # Mock lyrics transcription to avoid downloading Whisper model
    from src.lyrics_transcription import LyricsTranscriptionModule
    
    def mock_transcribe(self, audio, sample_rate, language="ja"):
        return []  # Return empty lyrics
    
    monkeypatch.setattr(LyricsTranscriptionModule, 'transcribe', mock_transcribe)
    
    # Load audio file
    audio_engine.load_audio_file(test_audio_file)
    
    # Perform analysis
    result = audio_engine.analyze_audio(use_cache=False)
    
    # Verify result structure
    assert isinstance(result, AudioAnalysisResult)
    assert isinstance(result.chord_progression, list)
    assert isinstance(result.lyrics, list)
    assert isinstance(result.tempo, float)
    assert isinstance(result.key, str)
    assert isinstance(result.time_signature, tuple)
    assert len(result.time_signature) == 2
    
    # Verify tempo is reasonable (or 0 if detection failed on short audio)
    assert result.tempo >= 0
    if result.tempo > 0:
        assert result.tempo < 300  # Reasonable BPM range
    
    # Verify key is valid
    assert len(result.key) > 0
    
    # Verify time signature is valid
    assert result.time_signature[0] > 0
    assert result.time_signature[1] > 0


def test_analyze_audio_with_cache_integration(audio_engine, test_audio_file, monkeypatch):
    """Test analyze_audio with cache integration"""
    # Mock lyrics transcription to avoid downloading Whisper model
    from src.lyrics_transcription import LyricsTranscriptionModule
    
    def mock_transcribe(self, audio, sample_rate, language="ja"):
        return []  # Return empty lyrics
    
    monkeypatch.setattr(LyricsTranscriptionModule, 'transcribe', mock_transcribe)
    
    # Load audio file
    audio_engine.load_audio_file(test_audio_file)
    
    # First analysis (no cache)
    result1 = audio_engine.analyze_audio(use_cache=True)
    
    # Verify cache was created
    assert audio_engine.cache_manager.has_cache(test_audio_file)
    
    # Second analysis (should use cache)
    result2 = audio_engine.analyze_audio(use_cache=True)
    
    # Results should be identical
    assert result1.tempo == result2.tempo
    assert result1.key == result2.key
    assert result1.time_signature == result2.time_signature
    assert len(result1.chord_progression) == len(result2.chord_progression)
    assert len(result1.lyrics) == len(result2.lyrics)


def test_analyze_audio_cache_bypass(audio_engine, test_audio_file, monkeypatch):
    """Test analyze_audio bypasses cache when use_cache=False"""
    # Mock lyrics transcription to avoid downloading Whisper model
    from src.lyrics_transcription import LyricsTranscriptionModule
    
    def mock_transcribe(self, audio, sample_rate, language="ja"):
        return []  # Return empty lyrics
    
    monkeypatch.setattr(LyricsTranscriptionModule, 'transcribe', mock_transcribe)
    
    # Load audio file
    audio_engine.load_audio_file(test_audio_file)
    
    # First analysis with cache
    result1 = audio_engine.analyze_audio(use_cache=True)
    
    # Verify cache exists
    assert audio_engine.cache_manager.has_cache(test_audio_file)
    
    # Second analysis bypassing cache
    result2 = audio_engine.analyze_audio(use_cache=False)
    
    # Both should succeed (results may vary slightly due to randomness in algorithms)
    assert isinstance(result1, AudioAnalysisResult)
    assert isinstance(result2, AudioAnalysisResult)
