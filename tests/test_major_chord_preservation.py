"""Property-based tests for major chord preservation

**Validates: Requirements 3.1**

This test ensures that major chord detection accuracy is preserved after fixes.
Following observation-first methodology: observe behavior on UNFIXED code,
then write property-based tests capturing that behavior.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings
from src.chord_estimation import ChordEstimationModule
from src.models import ChordQuality


@pytest.fixture
def chord_estimator():
    """Create ChordEstimationModule instance"""
    return ChordEstimationModule()


def generate_major_chord_audio(root_note: str, sample_rate: int = 22050, duration: float = 2.0) -> np.ndarray:
    """
    Generate synthetic audio for a major chord.
    
    A major chord consists of:
    - Root note (fundamental frequency)
    - Major third (frequency * 5/4)
    - Perfect fifth (frequency * 3/2)
    
    Args:
        root_note: Root note name (C, C#, D, etc.)
        sample_rate: Audio sample rate
        duration: Duration in seconds
        
    Returns:
        Audio signal as numpy array
    """
    # Map note names to frequencies (A4 = 440 Hz as reference)
    note_to_freq = {
        'C': 261.63,   # C4
        'C#': 277.18,
        'D': 293.66,
        'D#': 311.13,
        'E': 329.63,
        'F': 349.23,
        'F#': 369.99,
        'G': 392.00,
        'G#': 415.30,
        'A': 440.00,
        'A#': 466.16,
        'B': 493.88,
    }
    
    if root_note not in note_to_freq:
        raise ValueError(f"Unknown note: {root_note}")
    
    fundamental = note_to_freq[root_note]
    major_third = fundamental * 5/4
    perfect_fifth = fundamental * 3/2
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Combine the three frequencies with different amplitudes
    audio = (
        0.5 * np.sin(2 * np.pi * fundamental * t) +
        0.3 * np.sin(2 * np.pi * major_third * t) +
        0.3 * np.sin(2 * np.pi * perfect_fifth * t)
    )
    
    # Normalize to [-1, 1]
    audio = audio / np.max(np.abs(audio))
    
    return audio


# First, let's observe the baseline behavior with a simple unit test
def test_observe_major_chord_detection(chord_estimator):
    """
    Observation test: Process audio with major chords and observe behavior.
    This establishes the baseline that we want to preserve.
    """
    major_chords = ['C', 'G', 'A', 'F']
    
    for root in major_chords:
        audio = generate_major_chord_audio(root, duration=2.0)
        chords = chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
        
        # Observe what the current system detects
        assert len(chords) > 0, f"Should detect at least one chord for {root}"
        
        # Check that detected chords are major quality
        for chord in chords:
            assert chord.quality.value == "maj", \
                f"Expected MAJOR quality for {root} chord, got {chord.quality}"
            
        # Log the detection for observation
        print(f"\nObserved detection for {root} major chord:")
        for chord in chords:
            print(f"  - Root: {chord.root}, Quality: {chord.quality}, "
                  f"Confidence: {chord.confidence:.3f}, "
                  f"Time: {chord.start_time:.2f}-{chord.end_time:.2f}s")


# Property-based test: For all major-only chord progressions,
# detection accuracy matches original behavior
@given(
    root_notes=st.lists(
        st.sampled_from(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']),
        min_size=1,
        max_size=4
    )
)
@settings(max_examples=20, deadline=None)
def test_major_chord_preservation_property(root_notes):
    """
    Property: For all major-only chord progressions, the system should:
    1. Detect chords with MAJOR quality
    2. Maintain consistent confidence scoring
    3. Produce non-overlapping segments
    
    **Validates: Requirements 3.1**
    
    This property-based test generates random major chord progressions
    and verifies that the baseline behavior is preserved.
    """
    chord_estimator = ChordEstimationModule()
    
    # Generate audio for each chord in the progression
    sample_rate = 22050
    chord_duration = 2.0
    
    # Create a progression by concatenating chord audio
    audio_segments = []
    for root in root_notes:
        chord_audio = generate_major_chord_audio(root, sample_rate, chord_duration)
        audio_segments.append(chord_audio)
    
    # Concatenate all segments
    full_audio = np.concatenate(audio_segments)
    
    # Estimate chords
    detected_chords = chord_estimator.estimate_chords(
        full_audio, 
        sample_rate, 
        use_vocal_separation=False
    )
    
    # Property 1: All detected chords should have MAJOR quality
    for chord in detected_chords:
        assert chord.quality.value == "maj", \
            f"Expected MAJOR quality, got {chord.quality} for chord {chord.root}"
    
    # Property 2: Confidence scores should be reasonable (> 0)
    for chord in detected_chords:
        assert chord.confidence > 0, \
            f"Confidence should be positive, got {chord.confidence}"
    
    # Property 3: Segments should be non-overlapping
    for i in range(len(detected_chords) - 1):
        assert detected_chords[i].end_time <= detected_chords[i + 1].start_time, \
            f"Overlapping segments detected: {detected_chords[i]} and {detected_chords[i + 1]}"
    
    # Property 4: Should detect at least some chords (not empty)
    assert len(detected_chords) > 0, \
        "Should detect at least one chord in the progression"


def test_major_chord_specific_roots(chord_estimator):
    """
    Test specific major chord roots mentioned in the task: C, G, A, F
    
    **Validates: Requirements 3.1**
    """
    test_chords = ['C', 'G', 'A', 'F']
    
    for root in test_chords:
        audio = generate_major_chord_audio(root, duration=2.0)
        chords = chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
        
        # Should detect at least one chord
        assert len(chords) > 0, f"Should detect chord for {root}"
        
        # All detected chords should be major quality
        for chord in chords:
            assert chord.quality.value == "maj", \
                f"Expected MAJOR quality for {root}, got {chord.quality}"
            
        # Should have reasonable confidence
        for chord in chords:
            assert chord.confidence > 0, \
                f"Confidence should be positive for {root}"
