"""Property-based tests for audio processing preservation

**Validates: Requirements 3.6, 3.7**

This test ensures that vocal separation and chroma extraction behavior is preserved after fixes.
Following observation-first methodology: observe behavior on UNFIXED code,
then write property-based tests capturing that behavior.

Requirement 3.6: WHEN audio contains vocals THEN system continues to use vocal separation
                 to improve chord estimation accuracy

Requirement 3.7: WHEN chroma features are extracted THEN system continues to handle
                 silent segments appropriately, treating them as zero vectors
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings
from src.chord_estimation import ChordEstimationModule


@pytest.fixture
def chord_estimator():
    """Create ChordEstimationModule instance"""
    return ChordEstimationModule()


def generate_audio_with_vocals(sample_rate: int = 22050, duration: float = 2.0) -> np.ndarray:
    """
    Generate synthetic audio simulating vocals + accompaniment.
    
    Vocals are simulated with higher frequency content (200-800 Hz range).
    Accompaniment is simulated with lower frequency content (100-400 Hz range).
    
    Args:
        sample_rate: Audio sample rate
        duration: Duration in seconds
        
    Returns:
        Audio signal as numpy array
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Simulate vocal frequencies (higher range)
    vocal_freq1 = 300  # Hz
    vocal_freq2 = 500  # Hz
    vocals = (
        0.4 * np.sin(2 * np.pi * vocal_freq1 * t) +
        0.3 * np.sin(2 * np.pi * vocal_freq2 * t)
    )
    
    # Simulate accompaniment frequencies (lower range)
    accomp_freq1 = 150  # Hz
    accomp_freq2 = 250  # Hz
    accompaniment = (
        0.5 * np.sin(2 * np.pi * accomp_freq1 * t) +
        0.4 * np.sin(2 * np.pi * accomp_freq2 * t)
    )
    
    # Mix vocals and accompaniment
    mixed_audio = vocals + accompaniment
    
    # Normalize to [-1, 1]
    mixed_audio = mixed_audio / np.max(np.abs(mixed_audio))
    
    return mixed_audio


def generate_audio_with_silence(sample_rate: int = 22050, 
                                 sound_duration: float = 1.0,
                                 silence_duration: float = 1.0) -> np.ndarray:
    """
    Generate audio with both sound and silent segments.
    
    Args:
        sample_rate: Audio sample rate
        sound_duration: Duration of sound segment in seconds
        silence_duration: Duration of silent segment in seconds
        
    Returns:
        Audio signal with sound followed by silence
    """
    # Generate sound segment
    t_sound = np.linspace(0, sound_duration, int(sample_rate * sound_duration))
    sound = 0.5 * np.sin(2 * np.pi * 440 * t_sound)  # A4 note
    
    # Generate silent segment
    silence = np.zeros(int(sample_rate * silence_duration))
    
    # Concatenate sound and silence
    audio = np.concatenate([sound, silence])
    
    return audio


# ============================================================================
# OBSERVATION TESTS: Establish baseline behavior on UNFIXED code
# ============================================================================

def test_observe_vocal_separation_output(chord_estimator):
    """
    Observation test: Process audio with vocals and observe vocal separation output.
    This establishes the baseline behavior that we want to preserve.
    
    **Validates: Requirements 3.6**
    """
    audio = generate_audio_with_vocals(duration=2.0)
    sample_rate = 22050
    
    # Perform vocal separation
    separated = chord_estimator.separate_vocals(audio, sample_rate)
    
    # Observe the output characteristics
    print("\n=== Vocal Separation Observation ===")
    print(f"Input audio shape: {audio.shape}")
    print(f"Input audio dtype: {audio.dtype}")
    print(f"Input audio range: [{np.min(audio):.4f}, {np.max(audio):.4f}]")
    print(f"Input audio mean: {np.mean(audio):.4f}")
    print(f"Input audio std: {np.std(audio):.4f}")
    print()
    print(f"Separated audio shape: {separated.shape}")
    print(f"Separated audio dtype: {separated.dtype}")
    print(f"Separated audio range: [{np.min(separated):.4f}, {np.max(separated):.4f}]")
    print(f"Separated audio mean: {np.mean(separated):.4f}")
    print(f"Separated audio std: {np.std(separated):.4f}")
    print()
    
    # Key observations to preserve:
    # 1. Output should be mono (1D array)
    assert separated.ndim == 1, "Separated audio should be mono"
    
    # 2. Output length should match input length
    assert len(separated) == len(audio), "Separated audio length should match input"
    
    # 3. Output should be non-empty
    assert len(separated) > 0, "Separated audio should not be empty"
    
    # 4. Output should contain numeric values (not NaN or Inf)
    assert np.all(np.isfinite(separated)), "Separated audio should contain finite values"
    
    print("✓ Vocal separation produces valid output")


def test_observe_chroma_extraction_with_silence(chord_estimator):
    """
    Observation test: Extract chroma features from audio with silent segments.
    Observe how silent segments are handled (should be zero vectors).
    
    **Validates: Requirements 3.7**
    """
    audio = generate_audio_with_silence(sound_duration=1.0, silence_duration=1.0)
    sample_rate = 22050
    
    # Extract chroma features
    chroma = chord_estimator.extract_chroma(audio, sample_rate)
    
    # Observe the output characteristics
    print("\n=== Chroma Extraction with Silence Observation ===")
    print(f"Input audio shape: {audio.shape}")
    print(f"Input audio has silence: {np.any(np.abs(audio) < 0.01)}")
    print()
    print(f"Chroma shape: {chroma.shape}")
    print(f"Chroma dtype: {chroma.dtype}")
    print(f"Chroma range: [{np.min(chroma):.4f}, {np.max(chroma):.4f}]")
    print(f"Number of frames: {chroma.shape[1]}")
    print()
    
    # Analyze silent frames
    frame_energy = np.sum(chroma, axis=0)
    zero_frames = np.sum(frame_energy == 0)
    non_zero_frames = np.sum(frame_energy > 0)
    
    print(f"Zero frames (silent): {zero_frames}")
    print(f"Non-zero frames (sound): {non_zero_frames}")
    print(f"Percentage of zero frames: {100 * zero_frames / chroma.shape[1]:.1f}%")
    print()
    
    # Key observations to preserve:
    # 1. Chroma should have 12 pitch classes
    assert chroma.shape[0] == 12, "Chroma should have 12 pitch classes"
    
    # 2. Chroma should have multiple time frames
    assert chroma.shape[1] > 0, "Chroma should have time frames"
    
    # 3. All values should be non-negative
    assert np.all(chroma >= 0), "Chroma values should be non-negative"
    
    # 4. Silent segments should produce zero vectors
    # (This is the key behavior from requirement 3.7)
    assert zero_frames > 0, "Should have some zero frames for silent segments"
    
    print("✓ Chroma extraction handles silent segments as zero vectors")


def test_observe_chroma_extraction_all_silence(chord_estimator):
    """
    Observation test: Extract chroma from completely silent audio.
    All frames should be zero vectors.
    
    **Validates: Requirements 3.7**
    """
    sample_rate = 22050
    duration = 1.0
    audio = np.zeros(int(sample_rate * duration))
    
    # Extract chroma features
    chroma = chord_estimator.extract_chroma(audio, sample_rate)
    
    print("\n=== Chroma Extraction from Complete Silence ===")
    print(f"Input: {duration}s of silence")
    print(f"Chroma shape: {chroma.shape}")
    print(f"All frames are zero: {np.allclose(chroma, 0.0)}")
    print()
    
    # Key observation: All frames should be zero for silent audio
    assert np.allclose(chroma, 0.0), "Silent audio should produce all-zero chroma"
    
    print("✓ Complete silence produces all-zero chroma vectors")


# ============================================================================
# PROPERTY-BASED TESTS: Verify preservation across input space
# ============================================================================

@given(
    duration=st.floats(min_value=0.5, max_value=5.0),
    freq1=st.floats(min_value=100, max_value=800),
    freq2=st.floats(min_value=100, max_value=800)
)
@settings(max_examples=20, deadline=None)
def test_vocal_separation_preservation_property(duration, freq1, freq2):
    """
    Property: For all audio inputs with vocals, vocal separation should:
    1. Produce mono output with same length as input
    2. Produce finite numeric values (no NaN or Inf)
    3. Preserve the audio processing pipeline
    
    **Validates: Requirements 3.6**
    
    This property-based test generates random audio with different frequencies
    and durations, verifying that vocal separation behavior is preserved.
    """
    chord_estimator = ChordEstimationModule()
    sample_rate = 22050
    
    # Generate audio with two frequency components
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = (
        0.5 * np.sin(2 * np.pi * freq1 * t) +
        0.5 * np.sin(2 * np.pi * freq2 * t)
    )
    
    # Normalize
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
    
    # Perform vocal separation
    separated = chord_estimator.separate_vocals(audio, sample_rate)
    
    # Property 1: Output should be mono (1D)
    assert separated.ndim == 1, \
        f"Separated audio should be mono, got shape {separated.shape}"
    
    # Property 2: Output length should match input
    assert len(separated) == len(audio), \
        f"Length mismatch: input={len(audio)}, output={len(separated)}"
    
    # Property 3: Output should contain finite values
    assert np.all(np.isfinite(separated)), \
        "Separated audio contains NaN or Inf values"
    
    # Property 4: Output should be non-empty
    assert len(separated) > 0, \
        "Separated audio should not be empty"


@given(
    sound_duration=st.floats(min_value=0.5, max_value=3.0),
    silence_duration=st.floats(min_value=0.5, max_value=3.0),
    frequency=st.floats(min_value=100, max_value=1000)
)
@settings(max_examples=20, deadline=None)
def test_chroma_silent_segments_preservation_property(sound_duration, silence_duration, frequency):
    """
    Property: For all audio inputs with silent segments, chroma extraction should:
    1. Produce 12-dimensional chroma vectors
    2. Handle silent segments as zero vectors
    3. Produce non-negative values
    4. Preserve the chroma extraction pipeline
    
    **Validates: Requirements 3.7**
    
    This property-based test generates random audio with varying amounts of
    sound and silence, verifying that silent segment handling is preserved.
    """
    chord_estimator = ChordEstimationModule()
    sample_rate = 22050
    
    # Generate sound segment
    t_sound = np.linspace(0, sound_duration, int(sample_rate * sound_duration))
    sound = 0.5 * np.sin(2 * np.pi * frequency * t_sound)
    
    # Generate silent segment
    silence = np.zeros(int(sample_rate * silence_duration))
    
    # Concatenate
    audio = np.concatenate([sound, silence])
    
    # Extract chroma
    chroma = chord_estimator.extract_chroma(audio, sample_rate)
    
    # Property 1: Should have 12 pitch classes
    assert chroma.shape[0] == 12, \
        f"Chroma should have 12 pitch classes, got {chroma.shape[0]}"
    
    # Property 2: Should have time frames
    assert chroma.shape[1] > 0, \
        "Chroma should have at least one time frame"
    
    # Property 3: All values should be non-negative
    assert np.all(chroma >= 0), \
        f"Chroma should be non-negative, got min={np.min(chroma)}"
    
    # Property 4: Should have some zero frames (for silent segments)
    frame_energy = np.sum(chroma, axis=0)
    zero_frames = np.sum(frame_energy == 0)
    
    # Since we have silence in the audio, we expect some zero frames
    # (unless the silence is very short and gets smoothed out)
    if silence_duration > 0.5:  # Only check for longer silence periods
        assert zero_frames > 0, \
            "Should have zero frames for silent segments"


@given(
    duration=st.floats(min_value=0.5, max_value=3.0)
)
@settings(max_examples=20, deadline=None)
def test_chroma_complete_silence_preservation_property(duration):
    """
    Property: For all completely silent audio, chroma extraction should:
    1. Produce all-zero chroma vectors
    2. Maintain 12-dimensional structure
    
    **Validates: Requirements 3.7**
    
    This property-based test verifies that complete silence is consistently
    handled as zero vectors across different durations.
    """
    chord_estimator = ChordEstimationModule()
    sample_rate = 22050
    
    # Generate silent audio
    audio = np.zeros(int(sample_rate * duration))
    
    # Extract chroma
    chroma = chord_estimator.extract_chroma(audio, sample_rate)
    
    # Property 1: Should have 12 pitch classes
    assert chroma.shape[0] == 12, \
        f"Chroma should have 12 pitch classes, got {chroma.shape[0]}"
    
    # Property 2: All frames should be zero for silent audio
    assert np.allclose(chroma, 0.0), \
        f"Silent audio should produce all-zero chroma, got max={np.max(chroma)}"


def test_vocal_separation_stereo_to_mono_conversion(chord_estimator):
    """
    Test that stereo audio is properly converted to mono during vocal separation.
    This is part of the preservation requirement.
    
    **Validates: Requirements 3.6**
    """
    sample_rate = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create stereo audio (2 channels)
    audio_stereo = np.array([
        np.sin(2 * np.pi * 440 * t),  # Left channel
        np.sin(2 * np.pi * 880 * t)   # Right channel (different frequency)
    ])
    
    # Perform vocal separation
    separated = chord_estimator.separate_vocals(audio_stereo, sample_rate)
    
    # Should be converted to mono
    assert separated.ndim == 1, "Stereo input should be converted to mono"
    assert len(separated) > 0, "Output should not be empty"
    assert np.all(np.isfinite(separated)), "Output should contain finite values"


def test_chroma_extraction_stereo_to_mono_conversion(chord_estimator):
    """
    Test that stereo audio is properly converted to mono during chroma extraction.
    This is part of the preservation requirement.
    
    **Validates: Requirements 3.7**
    """
    sample_rate = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create stereo audio (2 channels)
    audio_stereo = np.array([
        np.sin(2 * np.pi * 440 * t),  # Left channel
        np.sin(2 * np.pi * 880 * t)   # Right channel
    ])
    
    # Extract chroma
    chroma = chord_estimator.extract_chroma(audio_stereo, sample_rate)
    
    # Should produce valid chroma features
    assert chroma.shape[0] == 12, "Should have 12 pitch classes"
    assert chroma.shape[1] > 0, "Should have time frames"
    assert np.all(chroma >= 0), "Chroma should be non-negative"
