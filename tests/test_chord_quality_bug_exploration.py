"""Bug Condition Exploration Tests for Chord Quality Detection

These tests are designed to FAIL on unfixed code to surface counterexamples
that demonstrate the chord quality detection bugs. The goal is to confirm
the root cause analysis before implementing fixes.

EXPECTED OUTCOME: All tests FAIL on unfixed code
- Em7 detected as "E" (major) instead of "Em7"
- A7 detected as "A" (major) instead of "A7"
- A7sus4 detected as "A" (major) instead of "A7sus4"
- A/G detected as "A" instead of "A/G"

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
"""

import pytest
import numpy as np
from src.chord_estimation import ChordEstimationModule
from src.models import ChordQuality


@pytest.fixture
def chord_estimator():
    """Create ChordEstimationModule instance"""
    return ChordEstimationModule()


def generate_chord_audio(root_freq: float, intervals: list, sample_rate: int = 22050, duration: float = 2.0) -> np.ndarray:
    """
    Generate synthetic audio for a chord with specified intervals
    
    Args:
        root_freq: Frequency of the root note in Hz
        intervals: List of semitone intervals from root (e.g., [0, 4, 7] for major triad)
        sample_rate: Sample rate in Hz
        duration: Duration in seconds
        
    Returns:
        Audio signal as numpy array
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)
    
    # Add each note in the chord
    for interval in intervals:
        freq = root_freq * (2 ** (interval / 12))
        audio += np.sin(2 * np.pi * freq * t)
    
    # Normalize
    audio = audio / len(intervals)
    
    return audio


def test_minor_seventh_chord_detection(chord_estimator):
    """
    Test that Em7 chord is detected with minor quality (not major)
    
    Em7 = E + G + B + D
    Intervals from E: [0, 3, 7, 10] (root, minor 3rd, perfect 5th, minor 7th)
    
    EXPECTED ON UNFIXED CODE: Fails - detects as major quality
    EXPECTED ON FIXED CODE: Passes - detects as minor quality with 7th
    """
    # E4 = 329.63 Hz
    e_freq = 329.63
    
    # Em7 intervals: root, minor 3rd, perfect 5th, minor 7th
    em7_intervals = [0, 3, 7, 10]
    
    audio = generate_chord_audio(e_freq, em7_intervals, duration=1.0)
    
    chords = chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    assert len(chords) > 0, "No chords detected"
    
    # Check that at least one chord has minor quality (not all major)
    # The bug is that ALL chords are detected as MAJOR
    all_major = all(chord.quality == ChordQuality.MAJOR for chord in chords)
    
    assert not all_major, \
        f"Counterexample: Minor chord detected as MAJOR. All chords: {[str(c) for c in chords]}"


def test_dominant_seventh_chord_detection(chord_estimator):
    """
    Test that A7 chord is detected with 7th extension (not plain major)
    
    A7 = A + C# + E + G
    Intervals from A: [0, 4, 7, 10] (root, major 3rd, perfect 5th, minor 7th)
    
    EXPECTED ON UNFIXED CODE: Fails - detects as "A" major without 7th
    EXPECTED ON FIXED CODE: Passes - detects as "A7" with DOMINANT7 quality or 7th extension
    """
    # A4 = 440 Hz
    a_freq = 440.0
    
    # A7 intervals: root, major 3rd, perfect 5th, minor 7th
    a7_intervals = [0, 4, 7, 10]
    
    audio = generate_chord_audio(a_freq, a7_intervals, duration=1.0)
    
    chords = chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    assert len(chords) > 0, "No chords detected"
    
    # Check first chord (should be A7)
    chord = chords[0]
    
    # Root should be A
    assert chord.root == 'A', f"Expected root 'A', got '{chord.root}'"
    
    # Quality should be DOMINANT7 or have 7th extension
    has_seventh = chord.quality == ChordQuality.DOMINANT7 or '7' in chord.extensions
    assert has_seventh, \
        f"Expected dominant 7th quality or 7th extension, got quality={chord.quality}, extensions={chord.extensions}. " \
        f"Counterexample: A7 detected as {chord}"


def test_sus4_chord_detection(chord_estimator):
    """
    Test that sus4 chord is detected with sus4 quality (not plain major)
    
    Asus4 = A + D + E
    Intervals from A: [0, 5, 7] (root, perfect 4th, perfect 5th)
    
    EXPECTED ON UNFIXED CODE: Fails - detects as major quality
    EXPECTED ON FIXED CODE: Passes - detects with SUS4 quality or sus4 extension
    """
    # A4 = 440 Hz
    a_freq = 440.0
    
    # Asus4 intervals: root, perfect 4th (sus4), perfect 5th
    asus4_intervals = [0, 5, 7]
    
    audio = generate_chord_audio(a_freq, asus4_intervals, duration=1.0)
    
    chords = chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    assert len(chords) > 0, "No chords detected"
    
    # Check that at least one chord has sus4 quality (not all major)
    # The bug is that ALL chords are detected as MAJOR
    all_major = all(chord.quality == ChordQuality.MAJOR for chord in chords)
    
    assert not all_major, \
        f"Counterexample: Sus4 chord detected as MAJOR. All chords: {[str(c) for c in chords]}"


def test_slash_chord_detection(chord_estimator):
    """
    Test that A/G slash chord is detected with bass note (not just "A")
    
    A/G = A major triad with G bass note
    A triad: A + C# + E (intervals [0, 4, 7])
    Bass: G (2 semitones below A)
    
    EXPECTED ON UNFIXED CODE: Fails - detects as "A" without bass note
    EXPECTED ON FIXED CODE: Passes - detects as "A/G" with bass_note='G'
    """
    # A4 = 440 Hz
    a_freq = 440.0
    
    # A major triad intervals
    a_major_intervals = [0, 4, 7]
    
    # Add G bass note (2 semitones below A, or -2 semitones)
    # G is 2 semitones below A
    a_with_g_bass = [-2] + a_major_intervals
    
    audio = generate_chord_audio(a_freq, a_with_g_bass, duration=1.0)
    
    chords = chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    assert len(chords) > 0, "No chords detected"
    
    # Check first chord (should be A/G)
    chord = chords[0]
    
    # Root should be A
    assert chord.root == 'A', f"Expected root 'A', got '{chord.root}'"
    
    # Bass note should be detected (not None)
    assert chord.bass_note is not None, \
        f"Expected bass note to be detected. Counterexample: A/G detected as {chord} (bass_note=None)"
    
    # Bass note should be G
    assert chord.bass_note == 'G', \
        f"Expected bass note 'G', got '{chord.bass_note}'. Counterexample: A/G detected as {chord}"
