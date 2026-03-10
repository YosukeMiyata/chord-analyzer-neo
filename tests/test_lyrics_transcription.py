"""Tests for LyricsTranscriptionModule"""

import pytest
import numpy as np
from src.lyrics_transcription import LyricsTranscriptionModule
from src.models import LyricSegment, ChordSegment, ChordQuality


@pytest.fixture
def lyrics_module():
    """Create LyricsTranscriptionModule instance"""
    return LyricsTranscriptionModule(model_size="tiny")


@pytest.fixture
def sample_lyrics():
    """Create sample lyric segments"""
    return [
        LyricSegment(0.0, 2.0, "Hello world", 0.95),
        LyricSegment(2.0, 4.0, "This is a test", 0.90),
        LyricSegment(4.0, 6.0, "Testing lyrics", 0.85)
    ]


@pytest.fixture
def sample_chords():
    """Create sample chord segments"""
    return [
        ChordSegment(0.0, 2.0, "C", ChordQuality.MAJOR, confidence=0.9),
        ChordSegment(2.0, 4.0, "G", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(4.0, 6.0, "Am", ChordQuality.MINOR, confidence=0.88)
    ]


def test_lyrics_module_initialization(lyrics_module):
    """Test LyricsTranscriptionModule initialization"""
    assert lyrics_module.model_size == "tiny"
    assert lyrics_module.model is None  # Lazy loading


def test_time_ranges_overlap(lyrics_module):
    """Test time range overlap detection"""
    # Overlapping ranges
    assert lyrics_module._time_ranges_overlap(0.0, 2.0, 1.0, 3.0) is True
    assert lyrics_module._time_ranges_overlap(1.0, 3.0, 0.0, 2.0) is True
    assert lyrics_module._time_ranges_overlap(0.0, 4.0, 1.0, 3.0) is True
    
    # Non-overlapping ranges
    assert lyrics_module._time_ranges_overlap(0.0, 1.0, 2.0, 3.0) is False
    assert lyrics_module._time_ranges_overlap(2.0, 3.0, 0.0, 1.0) is False
    
    # Adjacent ranges (no overlap)
    assert lyrics_module._time_ranges_overlap(0.0, 1.0, 1.0, 2.0) is False


def test_align_lyrics_with_chords(lyrics_module, sample_lyrics, sample_chords):
    """Test lyrics and chords alignment"""
    aligned = lyrics_module.align_lyrics_with_chords(sample_lyrics, sample_chords)
    
    assert len(aligned) == len(sample_lyrics)
    
    # Check first alignment
    lyric, chords = aligned[0]
    assert lyric.text == "Hello world"
    assert len(chords) == 1
    assert chords[0].root == "C"
    
    # Check second alignment
    lyric, chords = aligned[1]
    assert lyric.text == "This is a test"
    assert len(chords) == 1
    assert chords[0].root == "G"


def test_align_lyrics_with_no_chords(lyrics_module, sample_lyrics):
    """Test alignment when no chords are present"""
    aligned = lyrics_module.align_lyrics_with_chords(sample_lyrics, [])
    
    assert len(aligned) == len(sample_lyrics)
    
    # All lyrics should have empty chord lists
    for lyric, chords in aligned:
        assert isinstance(lyric, LyricSegment)
        assert chords == []


def test_align_empty_lyrics(lyrics_module, sample_chords):
    """Test alignment with empty lyrics"""
    aligned = lyrics_module.align_lyrics_with_chords([], sample_chords)
    
    assert aligned == []


def test_align_lyrics_with_multiple_chords(lyrics_module):
    """Test alignment when lyric spans multiple chords"""
    lyrics = [LyricSegment(0.0, 4.0, "Long lyric segment", 0.9)]
    chords = [
        ChordSegment(0.0, 2.0, "C", ChordQuality.MAJOR, confidence=0.9),
        ChordSegment(2.0, 4.0, "G", ChordQuality.MAJOR, confidence=0.85)
    ]
    
    aligned = lyrics_module.align_lyrics_with_chords(lyrics, chords)
    
    assert len(aligned) == 1
    lyric, associated_chords = aligned[0]
    assert len(associated_chords) == 2
    assert associated_chords[0].root == "C"
    assert associated_chords[1].root == "G"


def test_align_partial_overlap(lyrics_module):
    """Test alignment with partial time overlap"""
    lyrics = [LyricSegment(1.0, 3.0, "Partial overlap", 0.9)]
    chords = [
        ChordSegment(0.0, 2.0, "C", ChordQuality.MAJOR, confidence=0.9),
        ChordSegment(2.0, 4.0, "G", ChordQuality.MAJOR, confidence=0.85)
    ]
    
    aligned = lyrics_module.align_lyrics_with_chords(lyrics, chords)
    
    assert len(aligned) == 1
    lyric, associated_chords = aligned[0]
    # Should overlap with both chords
    assert len(associated_chords) == 2
