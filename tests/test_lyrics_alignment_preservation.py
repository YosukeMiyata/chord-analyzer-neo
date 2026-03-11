"""Property-based tests for lyrics-chord alignment preservation

**Validates: Requirements 3.5**

This test ensures that lyrics-chord time alignment behavior is preserved after fixes.
Following observation-first methodology: observe behavior on UNFIXED code,
then write property-based tests capturing that behavior.

Requirement 3.5: WHEN lyrics segments have associated chords THEN system continues to
                 correctly display the time-based correspondence between lyrics and chords
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings
from src.lyrics_transcription import LyricsTranscriptionModule
from src.models import LyricSegment, ChordSegment, ChordQuality


@pytest.fixture
def lyrics_module():
    """Create LyricsTranscriptionModule instance"""
    return LyricsTranscriptionModule(model_size="tiny")


def create_test_lyrics(num_segments: int = 3, segment_duration: float = 2.0) -> list[LyricSegment]:
    """
    Create test lyric segments with sequential timing.
    
    Args:
        num_segments: Number of lyric segments to create
        segment_duration: Duration of each segment in seconds
        
    Returns:
        List of LyricSegment objects
    """
    lyrics = []
    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration
        text = f"Lyric segment {i + 1}"
        confidence = 0.9
        lyrics.append(LyricSegment(start_time, end_time, text, confidence))
    return lyrics


def create_test_chords(num_chords: int = 6, chord_duration: float = 1.0) -> list[ChordSegment]:
    """
    Create test chord segments with sequential timing.
    
    Args:
        num_chords: Number of chord segments to create
        chord_duration: Duration of each chord in seconds
        
    Returns:
        List of ChordSegment objects
    """
    chord_roots = ["C", "G", "Am", "F", "Dm", "Em"]
    chord_qualities = [ChordQuality.MAJOR, ChordQuality.MAJOR, ChordQuality.MINOR, 
                       ChordQuality.MAJOR, ChordQuality.MINOR, ChordQuality.MINOR]
    
    chords = []
    for i in range(num_chords):
        start_time = i * chord_duration
        end_time = (i + 1) * chord_duration
        root = chord_roots[i % len(chord_roots)]
        quality = chord_qualities[i % len(chord_qualities)]
        chords.append(ChordSegment(start_time, end_time, root, quality, confidence=0.85))
    return chords


# ============================================================================
# OBSERVATION TESTS: Establish baseline behavior on UNFIXED code
# ============================================================================

def test_observe_lyrics_chord_alignment_basic(lyrics_module):
    """
    Observation test: Align lyrics with chords and observe the time-based correspondence.
    This establishes the baseline behavior that we want to preserve.
    
    **Validates: Requirements 3.5**
    """
    # Create test data: 3 lyrics (0-2s, 2-4s, 4-6s) and 6 chords (0-1s, 1-2s, 2-3s, 3-4s, 4-5s, 5-6s)
    lyrics = create_test_lyrics(num_segments=3, segment_duration=2.0)
    chords = create_test_chords(num_chords=6, chord_duration=1.0)
    
    # Perform alignment
    aligned = lyrics_module.align_lyrics_with_chords(lyrics, chords)
    
    # Observe the output characteristics
    print("\n=== Lyrics-Chord Alignment Observation ===")
    print(f"Number of lyrics: {len(lyrics)}")
    print(f"Number of chords: {len(chords)}")
    print(f"Number of aligned pairs: {len(aligned)}")
    print()
    
    for i, (lyric, associated_chords) in enumerate(aligned):
        print(f"Lyric {i + 1}: '{lyric.text}' ({lyric.start_time:.1f}s - {lyric.end_time:.1f}s)")
        print(f"  Associated chords: {len(associated_chords)}")
        for chord in associated_chords:
            print(f"    - {chord.root} ({chord.start_time:.1f}s - {chord.end_time:.1f}s)")
        print()
    
    # Key observations to preserve:
    # 1. Number of aligned pairs should equal number of lyrics
    assert len(aligned) == len(lyrics), \
        "Number of aligned pairs should match number of lyrics"
    
    # 2. Each lyric should have associated chords based on time overlap
    # Lyric 1 (0-2s) should overlap with chords 1 and 2 (0-1s, 1-2s)
    lyric1, chords1 = aligned[0]
    assert len(chords1) == 2, f"Lyric 1 should have 2 chords, got {len(chords1)}"
    assert chords1[0].root == "C", f"First chord should be C, got {chords1[0].root}"
    assert chords1[1].root == "G", f"Second chord should be G, got {chords1[1].root}"
    
    # Lyric 2 (2-4s) should overlap with chords 3 and 4 (2-3s, 3-4s)
    lyric2, chords2 = aligned[1]
    assert len(chords2) == 2, f"Lyric 2 should have 2 chords, got {len(chords2)}"
    assert chords2[0].root == "Am", f"First chord should be Am, got {chords2[0].root}"
    assert chords2[1].root == "F", f"Second chord should be F, got {chords2[1].root}"
    
    # Lyric 3 (4-6s) should overlap with chords 5 and 6 (4-5s, 5-6s)
    lyric3, chords3 = aligned[2]
    assert len(chords3) == 2, f"Lyric 3 should have 2 chords, got {len(chords3)}"
    assert chords3[0].root == "Dm", f"First chord should be Dm, got {chords3[0].root}"
    assert chords3[1].root == "Em", f"Second chord should be Em, got {chords3[1].root}"
    
    print("✓ Lyrics-chord alignment preserves time-based correspondence")


def test_observe_lyrics_chord_alignment_partial_overlap(lyrics_module):
    """
    Observation test: Test alignment with partial time overlap between lyrics and chords.
    
    **Validates: Requirements 3.5**
    """
    # Create lyrics with partial overlap
    lyrics = [
        LyricSegment(0.5, 2.5, "Partial overlap lyric 1", 0.9),
        LyricSegment(3.0, 5.0, "Partial overlap lyric 2", 0.9)
    ]
    
    # Create chords
    chords = [
        ChordSegment(0.0, 1.0, "C", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(1.0, 2.0, "G", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(2.0, 3.0, "Am", ChordQuality.MINOR, confidence=0.85),
        ChordSegment(3.0, 4.0, "F", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(4.0, 5.0, "Dm", ChordQuality.MINOR, confidence=0.85)
    ]
    
    # Perform alignment
    aligned = lyrics_module.align_lyrics_with_chords(lyrics, chords)
    
    print("\n=== Partial Overlap Alignment Observation ===")
    for i, (lyric, associated_chords) in enumerate(aligned):
        print(f"Lyric {i + 1}: '{lyric.text}' ({lyric.start_time:.1f}s - {lyric.end_time:.1f}s)")
        print(f"  Associated chords: {len(associated_chords)}")
        for chord in associated_chords:
            print(f"    - {chord.root} ({chord.start_time:.1f}s - {chord.end_time:.1f}s)")
        print()
    
    # Key observation: Partial overlaps should be detected
    # Lyric 1 (0.5-2.5s) should overlap with chords at 0-1s, 1-2s, and 2-3s
    lyric1, chords1 = aligned[0]
    assert len(chords1) == 3, f"Lyric 1 should have 3 overlapping chords, got {len(chords1)}"
    
    # Lyric 2 (3.0-5.0s) should overlap with chords at 3-4s and 4-5s
    lyric2, chords2 = aligned[1]
    assert len(chords2) == 2, f"Lyric 2 should have 2 overlapping chords, got {len(chords2)}"
    
    print("✓ Partial overlap detection works correctly")


def test_observe_lyrics_chord_alignment_no_overlap(lyrics_module):
    """
    Observation test: Test alignment when lyrics and chords don't overlap.
    
    **Validates: Requirements 3.5**
    """
    # Create non-overlapping lyrics and chords
    lyrics = [
        LyricSegment(5.0, 7.0, "Late lyric", 0.9)
    ]
    
    chords = [
        ChordSegment(0.0, 1.0, "C", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(1.0, 2.0, "G", ChordQuality.MAJOR, confidence=0.85)
    ]
    
    # Perform alignment
    aligned = lyrics_module.align_lyrics_with_chords(lyrics, chords)
    
    print("\n=== No Overlap Alignment Observation ===")
    lyric, associated_chords = aligned[0]
    print(f"Lyric: '{lyric.text}' ({lyric.start_time:.1f}s - {lyric.end_time:.1f}s)")
    print(f"Associated chords: {len(associated_chords)}")
    print()
    
    # Key observation: No overlap should result in empty chord list
    assert len(associated_chords) == 0, \
        f"Non-overlapping lyric should have 0 chords, got {len(associated_chords)}"
    
    print("✓ Non-overlapping lyrics correctly have no associated chords")


def test_observe_lyrics_chord_alignment_empty_inputs(lyrics_module):
    """
    Observation test: Test alignment with empty inputs.
    
    **Validates: Requirements 3.5**
    """
    # Test with empty lyrics
    aligned_empty_lyrics = lyrics_module.align_lyrics_with_chords([], create_test_chords())
    assert len(aligned_empty_lyrics) == 0, "Empty lyrics should produce empty alignment"
    
    # Test with empty chords
    aligned_empty_chords = lyrics_module.align_lyrics_with_chords(create_test_lyrics(), [])
    assert len(aligned_empty_chords) == len(create_test_lyrics()), \
        "Empty chords should still produce alignment pairs (with empty chord lists)"
    
    for lyric, chords in aligned_empty_chords:
        assert len(chords) == 0, "Each lyric should have empty chord list"
    
    print("\n=== Empty Input Handling ===")
    print("✓ Empty lyrics produce empty alignment")
    print("✓ Empty chords produce alignment with empty chord lists")


# ============================================================================
# PROPERTY-BASED TESTS: Verify preservation across input space
# ============================================================================

@given(
    num_lyrics=st.integers(min_value=1, max_value=10),
    num_chords=st.integers(min_value=1, max_value=20),
    lyric_duration=st.floats(min_value=1.0, max_value=5.0),
    chord_duration=st.floats(min_value=0.5, max_value=3.0)
)
@settings(max_examples=30, deadline=None)
def test_lyrics_chord_alignment_preservation_property(num_lyrics, num_chords, 
                                                       lyric_duration, chord_duration):
    """
    Property: For all combinations of lyrics and chords, alignment should:
    1. Produce exactly one alignment pair per lyric
    2. Associate chords based on time overlap
    3. Preserve the time-based correspondence logic
    4. Handle all edge cases consistently
    
    **Validates: Requirements 3.5**
    
    This property-based test generates random combinations of lyrics and chords
    with varying counts and durations, verifying that alignment behavior is preserved.
    """
    lyrics_module = LyricsTranscriptionModule(model_size="tiny")
    
    # Generate lyrics
    lyrics = create_test_lyrics(num_segments=num_lyrics, segment_duration=lyric_duration)
    
    # Generate chords
    chords = create_test_chords(num_chords=num_chords, chord_duration=chord_duration)
    
    # Perform alignment
    aligned = lyrics_module.align_lyrics_with_chords(lyrics, chords)
    
    # Property 1: Number of aligned pairs equals number of lyrics
    assert len(aligned) == len(lyrics), \
        f"Alignment count mismatch: expected {len(lyrics)}, got {len(aligned)}"
    
    # Property 2: Each aligned pair contains a lyric and a list of chords
    for lyric, associated_chords in aligned:
        assert isinstance(lyric, LyricSegment), \
            f"Expected LyricSegment, got {type(lyric)}"
        assert isinstance(associated_chords, list), \
            f"Expected list of chords, got {type(associated_chords)}"
        
        # Property 3: All associated chords should actually overlap with the lyric
        for chord in associated_chords:
            assert isinstance(chord, ChordSegment), \
                f"Expected ChordSegment, got {type(chord)}"
            
            # Verify time overlap
            overlaps = (lyric.start_time < chord.end_time and 
                       chord.start_time < lyric.end_time)
            assert overlaps, \
                f"Chord {chord.root} ({chord.start_time}-{chord.end_time}) " \
                f"doesn't overlap with lyric ({lyric.start_time}-{lyric.end_time})"
    
    # Property 4: No chord should be associated with a lyric if they don't overlap
    for lyric, associated_chords in aligned:
        for chord in chords:
            overlaps = (lyric.start_time < chord.end_time and 
                       chord.start_time < lyric.end_time)
            is_associated = chord in associated_chords
            
            # If they overlap, chord should be associated; if not, it shouldn't be
            assert overlaps == is_associated, \
                f"Overlap mismatch for lyric ({lyric.start_time}-{lyric.end_time}) " \
                f"and chord {chord.root} ({chord.start_time}-{chord.end_time})"


@given(
    offset=st.floats(min_value=0.0, max_value=2.0),
    lyric_duration=st.floats(min_value=1.0, max_value=3.0),
    chord_duration=st.floats(min_value=0.5, max_value=2.0)
)
@settings(max_examples=30, deadline=None)
def test_lyrics_chord_alignment_time_offset_property(offset, lyric_duration, chord_duration):
    """
    Property: Alignment should correctly handle various time offsets between
    lyrics and chords, preserving the overlap detection logic.
    
    **Validates: Requirements 3.5**
    
    This test verifies that time-based correspondence is preserved regardless
    of the relative timing between lyrics and chords.
    """
    lyrics_module = LyricsTranscriptionModule(model_size="tiny")
    
    # Create a single lyric starting at offset
    lyrics = [LyricSegment(offset, offset + lyric_duration, "Test lyric", 0.9)]
    
    # Create chords before, during, and after the lyric
    chords = [
        ChordSegment(0.0, chord_duration, "C", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(offset + 0.5, offset + 0.5 + chord_duration, "G", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(offset + lyric_duration + 1.0, offset + lyric_duration + 1.0 + chord_duration, 
                    "Am", ChordQuality.MINOR, confidence=0.85)
    ]
    
    # Perform alignment
    aligned = lyrics_module.align_lyrics_with_chords(lyrics, chords)
    
    # Property: Only chords that overlap with the lyric should be associated
    lyric, associated_chords = aligned[0]
    
    for chord in associated_chords:
        # Verify overlap
        overlaps = (lyric.start_time < chord.end_time and 
                   chord.start_time < lyric.end_time)
        assert overlaps, \
            f"Associated chord {chord.root} doesn't overlap with lyric"
    
    # Verify that non-overlapping chords are not associated
    for chord in chords:
        overlaps = (lyric.start_time < chord.end_time and 
                   chord.start_time < lyric.end_time)
        is_associated = chord in associated_chords
        
        assert overlaps == is_associated, \
            f"Chord {chord.root} association doesn't match overlap status"


def test_lyrics_chord_alignment_preserves_order(lyrics_module):
    """
    Test that alignment preserves the order of lyrics and chords.
    
    **Validates: Requirements 3.5**
    """
    # Create lyrics and chords in specific order
    lyrics = [
        LyricSegment(0.0, 2.0, "First", 0.9),
        LyricSegment(2.0, 4.0, "Second", 0.9),
        LyricSegment(4.0, 6.0, "Third", 0.9)
    ]
    
    chords = [
        ChordSegment(0.0, 2.0, "C", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(2.0, 4.0, "G", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(4.0, 6.0, "Am", ChordQuality.MINOR, confidence=0.85)
    ]
    
    # Perform alignment
    aligned = lyrics_module.align_lyrics_with_chords(lyrics, chords)
    
    # Verify order is preserved
    assert aligned[0][0].text == "First", "First lyric should be first"
    assert aligned[1][0].text == "Second", "Second lyric should be second"
    assert aligned[2][0].text == "Third", "Third lyric should be third"
    
    # Verify chord order within each alignment
    assert aligned[0][1][0].root == "C", "First chord should be C"
    assert aligned[1][1][0].root == "G", "Second chord should be G"
    assert aligned[2][1][0].root == "Am", "Third chord should be Am"
    
    print("\n=== Order Preservation ===")
    print("✓ Lyrics order preserved")
    print("✓ Chord order preserved within alignments")


def test_lyrics_chord_alignment_with_mixed_qualities(lyrics_module):
    """
    Test that alignment works correctly with chords of different qualities
    (major, minor, etc.) after the chord quality fix.
    
    **Validates: Requirements 3.5**
    """
    lyrics = [
        LyricSegment(0.0, 4.0, "Long lyric spanning multiple chords", 0.9)
    ]
    
    # Mix of different chord qualities
    chords = [
        ChordSegment(0.0, 1.0, "C", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(1.0, 2.0, "Em", ChordQuality.MINOR, confidence=0.85),
        ChordSegment(2.0, 3.0, "A7", ChordQuality.MAJOR, confidence=0.85, extensions=["7"]),
        ChordSegment(3.0, 4.0, "Dm", ChordQuality.MINOR, confidence=0.85)
    ]
    
    # Perform alignment
    aligned = lyrics_module.align_lyrics_with_chords(lyrics, chords)
    
    # Verify all chords are associated (they all overlap with the lyric)
    lyric, associated_chords = aligned[0]
    assert len(associated_chords) == 4, \
        f"Should have 4 associated chords, got {len(associated_chords)}"
    
    # Verify chord qualities are preserved in alignment
    assert associated_chords[0].quality == ChordQuality.MAJOR
    assert associated_chords[1].quality == ChordQuality.MINOR
    assert associated_chords[2].quality == ChordQuality.MAJOR
    assert associated_chords[3].quality == ChordQuality.MINOR
    
    print("\n=== Mixed Chord Qualities ===")
    print("✓ Alignment works with major chords")
    print("✓ Alignment works with minor chords")
    print("✓ Alignment works with 7th chords")
    print("✓ Chord quality information preserved in alignment")
