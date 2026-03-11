"""Tests for ChordEstimationModule"""

import pytest
import numpy as np
from src.chord_estimation import ChordEstimationModule
from src.models import ChordQuality


@pytest.fixture
def chord_estimator():
    """Create ChordEstimationModule instance"""
    return ChordEstimationModule()


@pytest.fixture
def sample_audio():
    """Create sample audio data"""
    # Generate 2 seconds of audio at 22050 Hz
    sample_rate = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Simple sine wave (440 Hz - A4)
    audio = np.sin(2 * np.pi * 440 * t)
    
    return audio, sample_rate


def test_chord_estimator_initialization(chord_estimator):
    """Test ChordEstimationModule initialization"""
    # Default is template matching mode (use_chordai=False)
    assert chord_estimator.model_path is not None
    assert chord_estimator.use_chordai is False
    assert chord_estimator.model is None  # No model loaded in template matching mode
    assert chord_estimator.hop_length == 512
    assert chord_estimator.n_fft == 2048


def test_separate_vocals_mono(chord_estimator, sample_audio):
    """Test vocal separation with mono audio"""
    audio, sample_rate = sample_audio
    
    separated = chord_estimator.separate_vocals(audio, sample_rate)
    
    assert separated is not None
    assert separated.ndim == 1  # Should be mono
    assert len(separated) > 0


def test_separate_vocals_stereo(chord_estimator):
    """Test vocal separation with stereo audio"""
    sample_rate = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create stereo audio
    audio_stereo = np.array([
        np.sin(2 * np.pi * 440 * t),
        np.sin(2 * np.pi * 440 * t)
    ])
    
    separated = chord_estimator.separate_vocals(audio_stereo, sample_rate)
    
    assert separated is not None
    assert separated.ndim == 1  # Should be converted to mono


def test_extract_chroma(chord_estimator, sample_audio):
    """Test chroma feature extraction"""
    audio, sample_rate = sample_audio
    
    chroma = chord_estimator.extract_chroma(audio, sample_rate)
    
    assert chroma is not None
    assert chroma.shape[0] == 12  # 12 chroma bins
    assert chroma.shape[1] > 0  # Has time frames
    assert np.all(chroma >= 0)  # All values should be non-negative


def test_extract_chroma_silent_audio(chord_estimator):
    """Test chroma extraction with silent audio"""
    sample_rate = 22050
    duration = 1.0
    
    # Create silent audio
    audio = np.zeros(int(sample_rate * duration))
    
    chroma = chord_estimator.extract_chroma(audio, sample_rate)
    
    assert chroma is not None
    assert chroma.shape[0] == 12
    # Silent frames should have zero chroma
    assert np.allclose(chroma, 0.0)


def test_detect_bass_notes(chord_estimator, sample_audio):
    """Test bass note detection"""
    audio, sample_rate = sample_audio
    
    bass_notes = chord_estimator.detect_bass_notes(audio, sample_rate)
    
    assert isinstance(bass_notes, list)
    # Each entry should be (timestamp, note) tuple
    for timestamp, note in bass_notes:
        assert isinstance(timestamp, float)
        assert isinstance(note, str)
        assert timestamp >= 0


def test_estimate_chords(chord_estimator, sample_audio):
    """Test chord estimation"""
    audio, sample_rate = sample_audio
    
    chords = chord_estimator.estimate_chords(
        audio, 
        sample_rate, 
        use_vocal_separation=False
    )
    
    assert isinstance(chords, list)
    assert len(chords) > 0
    
    # Check chord segment properties
    for chord in chords:
        assert chord.start_time >= 0
        assert chord.end_time > chord.start_time
        assert chord.root in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        assert isinstance(chord.quality, ChordQuality)
        assert 0 <= chord.confidence <= 1


def test_estimate_chords_with_vocal_separation(chord_estimator, sample_audio):
    """Test chord estimation with vocal separation enabled"""
    audio, sample_rate = sample_audio
    
    chords = chord_estimator.estimate_chords(
        audio, 
        sample_rate, 
        use_vocal_separation=True
    )
    
    assert isinstance(chords, list)
    assert len(chords) > 0


def test_chord_segments_non_overlapping(chord_estimator, sample_audio):
    """Test that chord segments don't overlap"""
    audio, sample_rate = sample_audio
    
    chords = chord_estimator.estimate_chords(audio, sample_rate, use_vocal_separation=False)
    
    for i in range(len(chords) - 1):
        assert chords[i].end_time <= chords[i + 1].start_time
