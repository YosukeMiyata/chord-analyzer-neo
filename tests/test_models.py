"""Tests for core data models"""

import pytest
from src.models import ChordSegment, ChordQuality, LyricSegment, AudioAnalysisResult


def test_chord_segment_creation():
    """Test ChordSegment creation"""
    chord = ChordSegment(
        start_time=0.0,
        end_time=2.0,
        root="C",
        quality=ChordQuality.MAJOR,
        confidence=0.9
    )
    assert chord.start_time == 0.0
    assert chord.end_time == 2.0
    assert chord.root == "C"
    assert chord.quality == ChordQuality.MAJOR
    assert chord.confidence == 0.9


def test_chord_segment_string_representation():
    """Test ChordSegment string representation"""
    chord = ChordSegment(
        start_time=0.0,
        end_time=2.0,
        root="C",
        quality=ChordQuality.MAJOR7
    )
    assert str(chord) == "Cmaj7"


def test_chord_segment_with_bass_note():
    """Test ChordSegment with slash chord"""
    chord = ChordSegment(
        start_time=0.0,
        end_time=2.0,
        root="C",
        quality=ChordQuality.MAJOR,
        bass_note="G"
    )
    assert str(chord) == "Cmaj/G"


def test_lyric_segment_creation():
    """Test LyricSegment creation"""
    lyric = LyricSegment(
        start_time=0.0,
        end_time=2.0,
        text="Hello world",
        confidence=0.95
    )
    assert lyric.start_time == 0.0
    assert lyric.end_time == 2.0
    assert lyric.text == "Hello world"
    assert lyric.confidence == 0.95
