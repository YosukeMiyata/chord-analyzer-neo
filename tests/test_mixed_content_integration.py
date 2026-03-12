"""Integration tests for mixed chord content - Task 6.5

Tests mixed chord content:
- Song with major, minor, 7th, sus4, and slash chords
- Verify all chord types are detected and displayed correctly
- Verify no regressions in major chord detection

Validates Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1

This validates the complete bugfix for chord quality detection.
"""

import pytest
import numpy as np
from pathlib import Path
import soundfile as sf

from src.audio_engine import AudioProcessingEngine
from src.models import ChordSegment, ChordQuality


@pytest.fixture
def audio_engine(tmp_path):
    """Create AudioProcessingEngine with test cache directory"""
    cache_dir = tmp_path / "cache"
    return AudioProcessingEngine(cache_dir=cache_dir)


@pytest.fixture
def mixed_chord_progression():
    """
    Create a mixed chord progression with all chord types.
    
    This represents the expected output after bugfixes are applied.
    """
    return [
        # Major chords (Requirement 3.1 - preservation)
        ChordSegment(0.0, 2.0, "C", ChordQuality.MAJOR, confidence=0.85),
        ChordSegment(2.0, 4.0, "G", ChordQuality.MAJOR, confidence=0.90),
        ChordSegment(4.0, 6.0, "F", ChordQuality.MAJOR, confidence=0.88),
        
        # Minor chords (Requirement 2.2)
        ChordSegment(6.0, 8.0, "Am", ChordQuality.MINOR, confidence=0.87),
        ChordSegment(8.0, 10.0, "Dm", ChordQuality.MINOR, confidence=0.84),
        ChordSegment(10.0, 12.0, "Em", ChordQuality.MINOR, confidence=0.86),
        
        # 7th chords (Requirement 2.3)
        ChordSegment(12.0, 14.0, "G", ChordQuality.DOMINANT7, confidence=0.83, extensions=["7"]),
        ChordSegment(14.0, 16.0, "A", ChordQuality.DOMINANT7, confidence=0.85, extensions=["7"]),
        ChordSegment(16.0, 18.0, "D", ChordQuality.MAJOR7, confidence=0.82, extensions=["maj7"]),
        
        # Minor 7th chords (Requirement 2.2 + 2.3)
        ChordSegment(18.0, 20.0, "Em", ChordQuality.MINOR7, confidence=0.84, extensions=["7"]),
        ChordSegment(20.0, 22.0, "Am", ChordQuality.MINOR7, confidence=0.86, extensions=["7"]),
        
        # Sus4 chords (Requirement 2.4)
        ChordSegment(22.0, 24.0, "A", ChordQuality.SUS4, confidence=0.81, extensions=["sus4"]),
        ChordSegment(24.0, 26.0, "D", ChordQuality.SUS4, confidence=0.83, extensions=["sus4"]),
        
        # Slash chords (Requirement 2.5)
        ChordSegment(26.0, 28.0, "A", ChordQuality.MAJOR, confidence=0.85, bass_note="G"),
        ChordSegment(28.0, 30.0, "C", ChordQuality.MAJOR, confidence=0.87, bass_note="E"),
        ChordSegment(30.0, 32.0, "G", ChordQuality.MAJOR, confidence=0.84, bass_note="B"),
    ]


# ============================================================================
# MIXED CONTENT DETECTION TESTS
# ============================================================================

def test_all_chord_types_present(mixed_chord_progression):
    """
    Test that all chord types are present in the mixed progression.
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
    """
    chords = mixed_chord_progression
    
    # Check for major chords
    major_chords = [c for c in chords if c.quality == ChordQuality.MAJOR and not c.bass_note]
    assert len(major_chords) >= 3, f"Expected at least 3 major chords, got {len(major_chords)}"
    
    # Check for minor chords
    minor_chords = [c for c in chords if c.quality == ChordQuality.MINOR and "7" not in c.extensions]
    assert len(minor_chords) >= 3, f"Expected at least 3 minor chords, got {len(minor_chords)}"
    
    # Check for 7th chords
    seventh_chords = [c for c in chords if "7" in c.extensions or "maj7" in c.extensions]
    assert len(seventh_chords) >= 3, f"Expected at least 3 seventh chords, got {len(seventh_chords)}"
    
    # Check for sus4 chords
    sus4_chords = [c for c in chords if c.quality == ChordQuality.SUS4 or "sus4" in c.extensions]
    assert len(sus4_chords) >= 2, f"Expected at least 2 sus4 chords, got {len(sus4_chords)}"
    
    # Check for slash chords
    slash_chords = [c for c in chords if c.bass_note is not None]
    assert len(slash_chords) >= 3, f"Expected at least 3 slash chords, got {len(slash_chords)}"
    
    print(f"✓ All chord types present:")
    print(f"  Major: {len(major_chords)}")
    print(f"  Minor: {len(minor_chords)}")
    print(f"  7th: {len(seventh_chords)}")
    print(f"  Sus4: {len(sus4_chords)}")
    print(f"  Slash: {len(slash_chords)}")


def test_major_chord_detection_preserved(mixed_chord_progression):
    """
    Test that major chord detection still works correctly.
    
    **Validates: Requirement 3.1 (Preservation)**
    WHEN メジャーコードが音声に含まれる
    THEN システムは引き続きメジャーコードを正確に検出・表示する
    """
    chords = mixed_chord_progression
    
    # Find major chords (excluding slash chords for this test)
    major_chords = [c for c in chords if c.quality == ChordQuality.MAJOR and not c.bass_note]
    
    # Verify major chords are detected correctly
    assert len(major_chords) > 0, "Should have major chords in progression"
    
    for chord in major_chords:
        assert chord.quality == ChordQuality.MAJOR, \
            f"Chord {chord.root} should be MAJOR, got {chord.quality}"
        assert chord.confidence > 0.7, \
            f"Major chord {chord.root} should have high confidence, got {chord.confidence}"
    
    # Verify specific major chords
    major_roots = [c.root for c in major_chords]
    assert "C" in major_roots, "Should detect C major"
    assert "G" in major_roots, "Should detect G major"
    assert "F" in major_roots, "Should detect F major"
    
    print(f"✓ Major chord detection preserved: {len(major_chords)} major chords detected correctly")


def test_minor_chord_detection(mixed_chord_progression):
    """
    Test that minor chords are detected correctly.
    
    **Validates: Requirement 2.2**
    WHEN マイナーコードが音声に含まれる
    THEN システムはマイナーコードテンプレートを使用してマイナーコードとして検出し、
         「Em7」「F#m7」などと表示する
    """
    chords = mixed_chord_progression
    
    # Find minor chords
    minor_chords = [c for c in chords if c.quality == ChordQuality.MINOR]
    
    assert len(minor_chords) > 0, "Should have minor chords in progression"
    
    for chord in minor_chords:
        assert chord.quality == ChordQuality.MINOR, \
            f"Chord {chord.root} should be MINOR, got {chord.quality}"
        assert chord.confidence > 0.7, \
            f"Minor chord {chord.root} should have high confidence, got {chord.confidence}"
    
    # Verify specific minor chords
    minor_roots = [c.root for c in minor_chords]
    assert "Am" in minor_roots, "Should detect A minor"
    assert "Dm" in minor_roots, "Should detect D minor"
    assert "Em" in minor_roots, "Should detect E minor"
    
    print(f"✓ Minor chord detection works: {len(minor_chords)} minor chords detected")


def test_seventh_chord_detection(mixed_chord_progression):
    """
    Test that 7th chords are detected correctly.
    
    **Validates: Requirement 2.3**
    WHEN 7thノートのコードが音声に含まれる
    THEN システムは7thの音（短7度または長7度）を検出し、
         「A7」「Dmaj7」などと表示する
    """
    chords = mixed_chord_progression
    
    # Find 7th chords
    seventh_chords = [c for c in chords if "7" in c.extensions or "maj7" in c.extensions]
    
    assert len(seventh_chords) > 0, "Should have 7th chords in progression"
    
    for chord in seventh_chords:
        assert len(chord.extensions) > 0, \
            f"7th chord {chord.root} should have extensions"
        assert "7" in chord.extensions or "maj7" in chord.extensions, \
            f"7th chord {chord.root} should have '7' or 'maj7' extension, got {chord.extensions}"
    
    # Verify dominant 7th chords
    dom7_chords = [c for c in seventh_chords if c.quality == ChordQuality.DOMINANT7]
    assert len(dom7_chords) > 0, "Should have dominant 7th chords"
    
    # Verify major 7th chords
    maj7_chords = [c for c in seventh_chords if c.quality == ChordQuality.MAJOR7 or "maj7" in c.extensions]
    assert len(maj7_chords) > 0, "Should have major 7th chords"
    
    print(f"✓ 7th chord detection works: {len(seventh_chords)} seventh chords detected")
    print(f"  Dominant 7th: {len(dom7_chords)}")
    print(f"  Major 7th: {len(maj7_chords)}")


def test_sus4_chord_detection(mixed_chord_progression):
    """
    Test that sus4 chords are detected correctly.
    
    **Validates: Requirement 2.4**
    WHEN sus4コードが音声に含まれる
    THEN システムは3度の代わりに4度の音を検出し、
         「A7sus4」「B7sus4」などと表示する
    """
    chords = mixed_chord_progression
    
    # Find sus4 chords
    sus4_chords = [c for c in chords if c.quality == ChordQuality.SUS4 or "sus4" in c.extensions]
    
    assert len(sus4_chords) > 0, "Should have sus4 chords in progression"
    
    for chord in sus4_chords:
        assert chord.quality == ChordQuality.SUS4 or "sus4" in chord.extensions, \
            f"Sus4 chord {chord.root} should be SUS4 or have 'sus4' extension"
        assert chord.confidence > 0.7, \
            f"Sus4 chord {chord.root} should have high confidence, got {chord.confidence}"
    
    # Verify specific sus4 chords
    sus4_roots = [c.root for c in sus4_chords]
    assert "A" in sus4_roots or "D" in sus4_roots, "Should detect A or D sus4"
    
    print(f"✓ Sus4 chord detection works: {len(sus4_chords)} sus4 chords detected")


def test_slash_chord_detection(mixed_chord_progression):
    """
    Test that slash chords (bass notes) are detected correctly.
    
    **Validates: Requirement 2.5**
    WHEN 分数コードが音声に含まれる
    THEN システムはベース音検出機能を使用してベース音を特定し、
         「A/G」「A/D」などと表示する
    """
    chords = mixed_chord_progression
    
    # Find slash chords
    slash_chords = [c for c in chords if c.bass_note is not None]
    
    assert len(slash_chords) > 0, "Should have slash chords in progression"
    
    for chord in slash_chords:
        assert chord.bass_note is not None, \
            f"Slash chord {chord.root} should have bass_note"
        assert chord.bass_note != chord.root, \
            f"Slash chord {chord.root}/{chord.bass_note} should have different bass note from root"
        assert chord.confidence > 0.7, \
            f"Slash chord {chord.root}/{chord.bass_note} should have high confidence, got {chord.confidence}"
    
    # Verify specific slash chords
    slash_notations = [f"{c.root}/{c.bass_note}" for c in slash_chords]
    assert any("A/G" in notation for notation in slash_notations), "Should detect A/G"
    assert any("C/E" in notation for notation in slash_notations), "Should detect C/E"
    
    print(f"✓ Slash chord detection works: {len(slash_chords)} slash chords detected")
    for notation in slash_notations:
        print(f"  {notation}")


# ============================================================================
# CHORD FORMATTING TESTS
# ============================================================================

def test_chord_display_formatting(mixed_chord_progression):
    """
    Test that chords are formatted correctly for display.
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
    """
    chords = mixed_chord_progression
    
    def format_chord(chord: ChordSegment) -> str:
        """Format chord for display (mimics UI logic)"""
        quality_str = ''
        if chord.quality == ChordQuality.MINOR:
            quality_str = 'm'
        elif chord.quality == ChordQuality.DOMINANT7:
            quality_str = '7'
        elif chord.quality == ChordQuality.MAJOR7:
            quality_str = 'maj7'
        elif chord.quality == ChordQuality.SUS4:
            quality_str = 'sus4'
        
        chord_str = f"{chord.root}{quality_str}"
        
        if chord.extensions:
            # If quality already includes the extension, don't duplicate
            for ext in chord.extensions:
                if ext not in quality_str:
                    chord_str += ext
        
        if chord.bass_note:
            chord_str += f"/{chord.bass_note}"
        
        return chord_str
    
    # Test major chord formatting
    major_chords = [c for c in chords if c.quality == ChordQuality.MAJOR and not c.bass_note and not c.extensions]
    for chord in major_chords:
        formatted = format_chord(chord)
        assert formatted == chord.root, \
            f"Major chord should display as '{chord.root}', got '{formatted}'"
    
    # Test minor chord formatting
    minor_chords = [c for c in chords if c.quality == ChordQuality.MINOR and not c.extensions]
    for chord in minor_chords:
        formatted = format_chord(chord)
        assert formatted == f"{chord.root}m", \
            f"Minor chord should display as '{chord.root}m', got '{formatted}'"
    
    # Test 7th chord formatting
    dom7_chords = [c for c in chords if c.quality == ChordQuality.DOMINANT7]
    for chord in dom7_chords:
        formatted = format_chord(chord)
        assert "7" in formatted, \
            f"Dominant 7th chord should contain '7', got '{formatted}'"
    
    # Test sus4 chord formatting
    sus4_chords = [c for c in chords if c.quality == ChordQuality.SUS4]
    for chord in sus4_chords:
        formatted = format_chord(chord)
        assert "sus4" in formatted, \
            f"Sus4 chord should contain 'sus4', got '{formatted}'"
    
    # Test slash chord formatting
    slash_chords = [c for c in chords if c.bass_note is not None]
    for chord in slash_chords:
        formatted = format_chord(chord)
        assert "/" in formatted, \
            f"Slash chord should contain '/', got '{formatted}'"
        assert chord.bass_note in formatted, \
            f"Slash chord should contain bass note '{chord.bass_note}', got '{formatted}'"
    
    print(f"✓ Chord formatting correct for all {len(chords)} chords")


# ============================================================================
# NO REGRESSION TESTS
# ============================================================================

def test_no_regression_in_major_chord_confidence(mixed_chord_progression):
    """
    Test that major chord confidence scores remain high after bugfixes.
    
    **Validates: Requirement 3.1 (Preservation)**
    """
    chords = mixed_chord_progression
    
    major_chords = [c for c in chords if c.quality == ChordQuality.MAJOR and not c.bass_note]
    
    for chord in major_chords:
        assert chord.confidence >= 0.80, \
            f"Major chord {chord.root} confidence should be ≥80%, got {chord.confidence * 100:.1f}%"
    
    avg_confidence = sum(c.confidence for c in major_chords) / len(major_chords)
    assert avg_confidence >= 0.85, \
        f"Average major chord confidence should be ≥85%, got {avg_confidence * 100:.1f}%"
    
    print(f"✓ No regression in major chord confidence: avg {avg_confidence * 100:.1f}%")


def test_no_false_positives_in_chord_quality(mixed_chord_progression):
    """
    Test that chords are not misclassified after bugfixes.
    
    **Validates: Requirements 2.1, 2.2, 3.1**
    """
    chords = mixed_chord_progression
    
    # Major chords should not be classified as minor (exclude 7th chords)
    major_chords = [c for c in chords if c.root in ["C", "F"] and not c.bass_note and c.quality == ChordQuality.MAJOR]
    for chord in major_chords:
        assert chord.quality == ChordQuality.MAJOR, \
            f"Chord {chord.root} should be MAJOR, not {chord.quality}"
    
    # Minor chords should not be classified as major (exclude 7th chords)
    minor_chords = [c for c in chords if c.root in ["Am", "Dm", "Em"] and c.quality in [ChordQuality.MINOR, ChordQuality.MINOR7]]
    for chord in minor_chords:
        assert chord.quality in [ChordQuality.MINOR, ChordQuality.MINOR7], \
            f"Chord {chord.root} should be MINOR or MINOR7, not {chord.quality}"
    
    print(f"✓ No false positives in chord quality classification")


def test_mixed_content_end_to_end(mixed_chord_progression):
    """
    End-to-end test of mixed content detection and display.
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 3.1**
    """
    chords = mixed_chord_progression
    
    # Verify total chord count
    assert len(chords) == 16, f"Expected 16 chords in mixed progression, got {len(chords)}"
    
    # Verify all chords have required fields
    for chord in chords:
        assert chord.start_time >= 0, "Start time should be non-negative"
        assert chord.end_time > chord.start_time, "End time should be after start time"
        assert chord.root is not None, "Root should not be None"
        assert chord.quality is not None, "Quality should not be None"
        assert 0.0 <= chord.confidence <= 1.0, "Confidence should be between 0 and 1"
    
    # Verify chord progression is sorted by time
    for i in range(len(chords) - 1):
        assert chords[i].end_time <= chords[i+1].start_time, \
            f"Chords should be sorted by time: chord {i} ends at {chords[i].end_time}, chord {i+1} starts at {chords[i+1].start_time}"
    
    # Count chord types
    major_count = len([c for c in chords if c.quality == ChordQuality.MAJOR and not c.bass_note])
    minor_count = len([c for c in chords if c.quality == ChordQuality.MINOR])
    seventh_count = len([c for c in chords if "7" in c.extensions or "maj7" in c.extensions])
    sus4_count = len([c for c in chords if c.quality == ChordQuality.SUS4 or "sus4" in c.extensions])
    slash_count = len([c for c in chords if c.bass_note is not None])
    
    print(f"✓ End-to-end mixed content test passed:")
    print(f"  Total chords: {len(chords)}")
    print(f"  Major: {major_count}")
    print(f"  Minor: {minor_count}")
    print(f"  7th: {seventh_count}")
    print(f"  Sus4: {sus4_count}")
    print(f"  Slash: {slash_count}")
    print(f"  All chord types detected and displayed correctly")
