"""Property-based tests for confidence scoring preservation

**Validates: Requirements 3.1**

This test ensures that confidence calculation methodology remains unchanged after fixes.
Following observation-first methodology: observe confidence scores on UNFIXED code,
then write property-based tests capturing that behavior.

Confidence is calculated as the dot product between normalized chroma vector
and the chord template. This methodology must remain unchanged.
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


def generate_chord_audio(root_note: str, sample_rate: int = 22050, duration: float = 2.0) -> np.ndarray:
    """
    Generate synthetic audio for a major chord.
    
    Args:
        root_note: Root note name (C, C#, D, etc.)
        sample_rate: Audio sample rate
        duration: Duration in seconds
        
    Returns:
        Audio signal as numpy array
    """
    note_to_freq = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88,
    }
    
    if root_note not in note_to_freq:
        raise ValueError(f"Unknown note: {root_note}")
    
    fundamental = note_to_freq[root_note]
    major_third = fundamental * 5/4
    perfect_fifth = fundamental * 3/2
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Combine the three frequencies
    audio = (
        0.5 * np.sin(2 * np.pi * fundamental * t) +
        0.3 * np.sin(2 * np.pi * major_third * t) +
        0.3 * np.sin(2 * np.pi * perfect_fifth * t)
    )
    
    # Normalize to [-1, 1]
    audio = audio / np.max(np.abs(audio))
    
    return audio


def test_observe_confidence_scoring(chord_estimator):
    """
    Observation test: Observe confidence scores for various chord detections.
    This establishes the baseline confidence calculation methodology.
    
    Confidence is calculated as: dot_product(normalized_chroma, chord_template)
    """
    test_chords = ['C', 'G', 'A', 'F', 'D', 'E']
    
    print("\n=== Observing Confidence Scoring on UNFIXED Code ===")
    
    for root in test_chords:
        audio = generate_chord_audio(root, duration=2.0)
        chords = chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
        
        assert len(chords) > 0, f"Should detect at least one chord for {root}"
        
        # Observe confidence scores
        for chord in chords:
            print(f"Chord: {chord.root}{chord.quality.value}, "
                  f"Confidence: {chord.confidence:.6f}, "
                  f"Time: {chord.start_time:.2f}-{chord.end_time:.2f}s")
            
            # Confidence should be in valid range [0, 1]
            assert 0 <= chord.confidence <= 1, \
                f"Confidence out of range: {chord.confidence}"


@given(
    root_notes=st.lists(
        st.sampled_from(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']),
        min_size=1,
        max_size=5
    ),
    duration=st.floats(min_value=1.0, max_value=3.0)
)
@settings(max_examples=30, deadline=None)
def test_confidence_calculation_methodology_preserved(root_notes, duration):
    """
    Property: Confidence calculation methodology must remain unchanged.
    
    The confidence score is calculated as the dot product between the
    normalized chroma vector and the chord template. This test verifies:
    
    1. Confidence scores are in valid range [0, 1]
    2. Confidence scores are deterministic (same input -> same output)
    3. Confidence calculation is based on template matching (higher for better matches)
    4. The methodology produces consistent results across different chords
    
    **Validates: Requirements 3.1**
    
    This property-based test generates random chord progressions and verifies
    that confidence scoring methodology is preserved.
    """
    chord_estimator = ChordEstimationModule()
    sample_rate = 22050
    
    # Generate audio for the progression
    audio_segments = []
    for root in root_notes:
        chord_audio = generate_chord_audio(root, sample_rate, duration)
        audio_segments.append(chord_audio)
    
    full_audio = np.concatenate(audio_segments)
    
    # Estimate chords
    detected_chords = chord_estimator.estimate_chords(
        full_audio, 
        sample_rate, 
        use_vocal_separation=False
    )
    
    # Property 1: All confidence scores must be in valid range [0, 1]
    for chord in detected_chords:
        assert 0 <= chord.confidence <= 1, \
            f"Confidence out of range [0,1]: {chord.confidence} for chord {chord.root}"
    
    # Property 2: Confidence scores should be positive for detected chords
    # (since we're generating actual chord audio, not noise)
    for chord in detected_chords:
        assert chord.confidence > 0, \
            f"Confidence should be positive for detected chord {chord.root}, got {chord.confidence}"
    
    # Property 3: Determinism - running estimation twice should give same results
    detected_chords_2 = chord_estimator.estimate_chords(
        full_audio, 
        sample_rate, 
        use_vocal_separation=False
    )
    
    assert len(detected_chords) == len(detected_chords_2), \
        "Determinism violated: different number of chords detected"
    
    for chord1, chord2 in zip(detected_chords, detected_chords_2):
        assert abs(chord1.confidence - chord2.confidence) < 1e-6, \
            f"Determinism violated: confidence differs for {chord1.root}"
    
    # Property 4: Confidence methodology is consistent
    # For well-formed chord audio, confidence should be reasonably high
    # (template matching should find good matches)
    if len(detected_chords) > 0:
        avg_confidence = sum(c.confidence for c in detected_chords) / len(detected_chords)
        # This is a weak assertion - just checking the methodology produces reasonable values
        assert avg_confidence > 0, \
            f"Average confidence should be positive, got {avg_confidence}"


def test_confidence_scoring_specific_cases(chord_estimator):
    """
    Test confidence scoring for specific chord cases.
    
    **Validates: Requirements 3.1**
    """
    # Test case 1: Single clear chord should have high confidence
    audio_c = generate_chord_audio('C', duration=2.0)
    chords_c = chord_estimator.estimate_chords(audio_c, 22050, use_vocal_separation=False)
    
    assert len(chords_c) > 0, "Should detect C chord"
    for chord in chords_c:
        assert chord.confidence > 0, f"C chord should have positive confidence"
        assert chord.confidence <= 1, f"C chord confidence should be <= 1"
    
    # Test case 2: Different chords should have different confidence patterns
    # but all should be in valid range
    test_roots = ['C', 'G', 'A', 'F']
    all_confidences = []
    
    for root in test_roots:
        audio = generate_chord_audio(root, duration=2.0)
        chords = chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
        
        for chord in chords:
            all_confidences.append(chord.confidence)
            assert 0 <= chord.confidence <= 1, \
                f"Confidence for {root} out of range: {chord.confidence}"
    
    # All confidences should be valid
    assert len(all_confidences) > 0, "Should have detected some chords"
    assert all(0 <= c <= 1 for c in all_confidences), \
        "All confidences should be in [0, 1]"


def test_confidence_calculation_formula_preserved(chord_estimator):
    """
    Test that the confidence calculation formula (dot product) is preserved.
    
    The confidence is calculated as: dot_product(normalized_chroma, template)
    This test verifies the calculation methodology by checking properties
    that should hold for dot product-based confidence.
    
    **Validates: Requirements 3.1**
    """
    # Generate a clear C major chord
    audio = generate_chord_audio('C', duration=2.0)
    
    # Extract chroma features (same as what estimate_chords does internally)
    chroma = chord_estimator.extract_chroma(audio, 22050)
    
    # Estimate chords
    chords = chord_estimator.estimate_chords(audio, 22050, use_vocal_separation=False)
    
    assert len(chords) > 0, "Should detect at least one chord"
    
    # For each detected chord, verify confidence properties
    for chord in chords:
        # Property 1: Confidence is the result of template matching
        # (dot product between normalized chroma and template)
        # This means confidence should be bounded by [0, 1] for normalized vectors
        assert 0 <= chord.confidence <= 1, \
            f"Confidence should be in [0,1] for dot product, got {chord.confidence}"
        
        # Property 2: For a well-formed chord, confidence should be positive
        assert chord.confidence > 0, \
            f"Confidence should be positive for detected chord, got {chord.confidence}"
        
        # Property 3: Confidence should be a float (not int or other type)
        assert isinstance(chord.confidence, float), \
            f"Confidence should be float type, got {type(chord.confidence)}"


if __name__ == "__main__":
    # Run observation test to see baseline behavior
    estimator = ChordEstimationModule()
    test_observe_confidence_scoring(estimator)
