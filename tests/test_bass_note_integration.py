"""Unit tests for bass note integration logic in estimate_chords method

Tests verify that:
1. ChordAI bass_note predictions are preserved
2. Detected bass notes only override when ChordAI didn't provide one
3. Root position chords (bass_note == root) are handled correctly
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.chord_estimation import ChordEstimationModule
from src.models import ChordSegment, ChordQuality


@pytest.fixture
def mock_chord_estimator():
    """Create a mocked ChordEstimationModule that bypasses initialization"""
    with patch.object(ChordEstimationModule, '_verify_dependencies'):
        with patch.object(ChordEstimationModule, '__init__', lambda x, model_path=None, use_chordai=False: None):
            estimator = ChordEstimationModule()
            estimator.hop_length = 512
            estimator.n_fft = 2048
            estimator.frame_duration = 0.5
            estimator.use_chordai = True  # Set use_chordai for these tests
            return estimator


def test_chordai_bass_note_preserved(mock_chord_estimator):
    """Test that ChordAI bass_note predictions are preserved"""
    # Mock the methods
    mock_chord_estimator.separate_vocals = Mock(return_value=np.zeros(1000))
    mock_chord_estimator.extract_chroma = Mock(return_value=np.zeros((12, 10)))
    
    # ChordAI provides bass_note = "E" for a C/E chord
    chordai_segment = ChordSegment(
        start_time=0.0,
        end_time=2.0,
        root="C",
        quality=ChordQuality.MAJOR,
        bass_note="E",  # ChordAI provided this
        confidence=0.95
    )
    mock_chord_estimator._chordai_recognition = Mock(return_value=[chordai_segment])
    
    # detect_bass_notes returns different bass note
    mock_chord_estimator.detect_bass_notes = Mock(return_value=[(1.0, "G2")])
    
    # Run estimate_chords
    audio = np.zeros(1000)
    result = mock_chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    # Verify ChordAI bass_note is preserved (not overridden by detected "G")
    assert len(result) == 1
    assert result[0].bass_note == "E"
    assert result[0].root == "C"


def test_detected_bass_note_applied_when_chordai_none(mock_chord_estimator):
    """Test that detected bass notes are applied when ChordAI didn't provide one"""
    # Mock the methods
    mock_chord_estimator.separate_vocals = Mock(return_value=np.zeros(1000))
    mock_chord_estimator.extract_chroma = Mock(return_value=np.zeros((12, 10)))
    
    # ChordAI doesn't provide bass_note
    chordai_segment = ChordSegment(
        start_time=0.0,
        end_time=2.0,
        root="C",
        quality=ChordQuality.MAJOR,
        bass_note=None,  # ChordAI didn't provide this
        confidence=0.95
    )
    mock_chord_estimator._chordai_recognition = Mock(return_value=[chordai_segment])
    
    # detect_bass_notes returns bass note "E"
    mock_chord_estimator.detect_bass_notes = Mock(return_value=[(1.0, "E2")])
    
    # Run estimate_chords
    audio = np.zeros(1000)
    result = mock_chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    # Verify detected bass_note is applied
    assert len(result) == 1
    assert result[0].bass_note == "E"
    assert result[0].root == "C"


def test_root_position_chord_bass_note_cleared(mock_chord_estimator):
    """Test that root position chords (bass_note == root) have bass_note cleared"""
    # Mock the methods
    mock_chord_estimator.separate_vocals = Mock(return_value=np.zeros(1000))
    mock_chord_estimator.extract_chroma = Mock(return_value=np.zeros((12, 10)))
    
    # ChordAI provides bass_note = "C" which matches root (root position)
    chordai_segment = ChordSegment(
        start_time=0.0,
        end_time=2.0,
        root="C",
        quality=ChordQuality.MAJOR,
        bass_note="C",  # Matches root - should be cleared
        confidence=0.95
    )
    mock_chord_estimator._chordai_recognition = Mock(return_value=[chordai_segment])
    
    # detect_bass_notes returns empty
    mock_chord_estimator.detect_bass_notes = Mock(return_value=[])
    
    # Run estimate_chords
    audio = np.zeros(1000)
    result = mock_chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    # Verify bass_note is cleared for root position chord
    assert len(result) == 1
    assert result[0].bass_note is None
    assert result[0].root == "C"


def test_detected_bass_note_not_applied_when_matches_root(mock_chord_estimator):
    """Test that detected bass notes matching root are not applied"""
    # Mock the methods
    mock_chord_estimator.separate_vocals = Mock(return_value=np.zeros(1000))
    mock_chord_estimator.extract_chroma = Mock(return_value=np.zeros((12, 10)))
    
    # ChordAI doesn't provide bass_note
    chordai_segment = ChordSegment(
        start_time=0.0,
        end_time=2.0,
        root="C",
        quality=ChordQuality.MAJOR,
        bass_note=None,
        confidence=0.95
    )
    mock_chord_estimator._chordai_recognition = Mock(return_value=[chordai_segment])
    
    # detect_bass_notes returns bass note "C" which matches root
    mock_chord_estimator.detect_bass_notes = Mock(return_value=[(1.0, "C2")])
    
    # Run estimate_chords
    audio = np.zeros(1000)
    result = mock_chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    # Verify bass_note is not set when it matches root
    assert len(result) == 1
    assert result[0].bass_note is None
    assert result[0].root == "C"


def test_multiple_segments_mixed_bass_notes(mock_chord_estimator):
    """Test handling of multiple segments with mixed bass note scenarios"""
    # Mock the methods
    mock_chord_estimator.separate_vocals = Mock(return_value=np.zeros(1000))
    mock_chord_estimator.extract_chroma = Mock(return_value=np.zeros((12, 10)))
    
    # Multiple segments with different bass note scenarios
    segments = [
        # Segment 1: ChordAI provides bass_note
        ChordSegment(0.0, 2.0, "C", ChordQuality.MAJOR, bass_note="E", confidence=0.95),
        # Segment 2: ChordAI doesn't provide bass_note
        ChordSegment(2.0, 4.0, "F", ChordQuality.MAJOR, bass_note=None, confidence=0.90),
        # Segment 3: ChordAI provides root position (bass_note == root)
        ChordSegment(4.0, 6.0, "G", ChordQuality.MAJOR, bass_note="G", confidence=0.92),
    ]
    mock_chord_estimator._chordai_recognition = Mock(return_value=segments)
    
    # detect_bass_notes returns bass notes for all segments
    mock_chord_estimator.detect_bass_notes = Mock(return_value=[
        (1.0, "G2"),  # During segment 1 - should be ignored (ChordAI provided E)
        (3.0, "A2"),  # During segment 2 - should be applied (ChordAI didn't provide)
        (5.0, "G2"),  # During segment 3 - root position, should stay None
    ])
    
    # Run estimate_chords
    audio = np.zeros(1000)
    result = mock_chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    # Verify each segment
    assert len(result) == 3
    
    # Segment 1: ChordAI bass_note preserved
    assert result[0].root == "C"
    assert result[0].bass_note == "E"
    
    # Segment 2: Detected bass_note applied
    assert result[1].root == "F"
    assert result[1].bass_note == "A"
    
    # Segment 3: Root position, bass_note cleared
    assert result[2].root == "G"
    assert result[2].bass_note is None
