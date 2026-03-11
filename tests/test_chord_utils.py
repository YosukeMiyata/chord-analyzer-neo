"""Unit tests for chord utility functions.

Tests the extract_root function for various chord formats.
Validates: Requirements 3.1, 3.2, 3.3, 3.4
"""

import pytest
from src.evaluation.chord_utils import extract_root, identify_quality


class TestExtractRoot:
    """Tests for extract_root function."""
    
    # Requirement 3.1: Simple chords
    def test_simple_major_chord(self):
        """Test extracting root from simple major chord."""
        assert extract_root("D") == "D"
        assert extract_root("C") == "C"
        assert extract_root("G") == "G"
        assert extract_root("A") == "A"
        assert extract_root("E") == "E"
        assert extract_root("F") == "F"
        assert extract_root("B") == "B"
    
    def test_simple_minor_chord(self):
        """Test extracting root from simple minor chord."""
        assert extract_root("Am") == "A"
        assert extract_root("Dm") == "D"
        assert extract_root("Em") == "E"
        assert extract_root("Bm") == "B"
        assert extract_root("Cm") == "C"
        assert extract_root("Fm") == "F"
        assert extract_root("Gm") == "G"
    
    # Requirement 3.2: Slash chords
    def test_slash_chord_with_on(self):
        """Test extracting root from slash chord with 'on' notation."""
        assert extract_root("AonC#") == "A"
        assert extract_root("DonF#") == "D"
        assert extract_root("ConE") == "C"
        assert extract_root("GonB") == "G"
    
    def test_slash_chord_with_forward_slash(self):
        """Test extracting root from slash chord with '/' notation."""
        assert extract_root("D/F#") == "D"
        assert extract_root("C/E") == "C"
        assert extract_root("G/B") == "G"
        assert extract_root("A/C#") == "A"
    
    # Requirement 3.3: Chords with quality suffix
    def test_chord_with_seventh(self):
        """Test extracting root from seventh chords."""
        assert extract_root("Bm7") == "B"
        assert extract_root("D7") == "D"
        assert extract_root("Am7") == "A"
        assert extract_root("E7") == "E"
        assert extract_root("G7") == "G"
    
    def test_chord_with_major_seventh(self):
        """Test extracting root from major seventh chords."""
        assert extract_root("Cmaj7") == "C"
        assert extract_root("Dmaj7") == "D"
        assert extract_root("Gmaj7") == "G"
        assert extract_root("Amaj7") == "A"
    
    def test_chord_with_complex_suffix(self):
        """Test extracting root from chords with complex suffixes."""
        assert extract_root("F#m7b5") == "F#"
        assert extract_root("Bb9") == "Bb"
        assert extract_root("Dm9") == "D"
        assert extract_root("Cadd9") == "C"
        assert extract_root("Gsus4") == "G"
        assert extract_root("Asus2") == "A"
    
    # Requirement 3.4: Sharp and flat accidentals
    def test_sharp_accidentals(self):
        """Test extracting root with sharp accidentals."""
        assert extract_root("F#") == "F#"
        assert extract_root("C#") == "C#"
        assert extract_root("G#") == "G#"
        assert extract_root("D#") == "D#"
        assert extract_root("A#") == "A#"
        assert extract_root("F#m") == "F#"
        assert extract_root("C#m7") == "C#"
        assert extract_root("G#maj7") == "G#"
    
    def test_flat_accidentals(self):
        """Test extracting root with flat accidentals."""
        assert extract_root("Bb") == "Bb"
        assert extract_root("Eb") == "Eb"
        assert extract_root("Ab") == "Ab"
        assert extract_root("Db") == "Db"
        assert extract_root("Gb") == "Gb"
        assert extract_root("Bbm") == "Bb"
        assert extract_root("Ebm7") == "Eb"
        assert extract_root("Abmaj7") == "Ab"
    
    # Combined requirements: Complex cases
    def test_slash_chord_with_accidentals_and_suffix(self):
        """Test extracting root from complex slash chords."""
        assert extract_root("F#m7/A") == "F#"
        assert extract_root("Bbmaj7onD") == "Bb"
        assert extract_root("C#m7b5/E") == "C#"
    
    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        assert extract_root(" D ") == "D"
        assert extract_root("  Am  ") == "A"
        assert extract_root(" F#m7 ") == "F#"
    
    # Error cases
    def test_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="chord must be a non-empty string"):
            extract_root("")
    
    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="chord cannot be empty after stripping whitespace"):
            extract_root("   ")
    
    def test_none_raises_error(self):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError, match="chord must be a non-empty string"):
            extract_root(None)
    
    def test_invalid_chord_raises_error(self):
        """Test that invalid chord format raises ValueError."""
        with pytest.raises(ValueError, match="Could not extract root note from chord"):
            extract_root("123")
        with pytest.raises(ValueError, match="Could not extract root note from chord"):
            extract_root("xyz")
        with pytest.raises(ValueError, match="Could not extract root note from chord"):
            extract_root("@#$")
    
    def test_lowercase_chord_raises_error(self):
        """Test that lowercase chord letters raise ValueError."""
        with pytest.raises(ValueError, match="Could not extract root note from chord"):
            extract_root("d")
        with pytest.raises(ValueError, match="Could not extract root note from chord"):
            extract_root("am")



class TestIdentifyQuality:
    """Tests for identify_quality function."""
    
    # Requirement 4.1: Major chords
    def test_simple_major_chord(self):
        """Test identifying major quality from simple chords."""
        assert identify_quality("D") == "major"
        assert identify_quality("C") == "major"
        assert identify_quality("G") == "major"
        assert identify_quality("A") == "major"
        assert identify_quality("E") == "major"
        assert identify_quality("F") == "major"
        assert identify_quality("B") == "major"
    
    def test_major_chord_with_accidentals(self):
        """Test identifying major quality with accidentals."""
        assert identify_quality("F#") == "major"
        assert identify_quality("Bb") == "major"
        assert identify_quality("C#") == "major"
        assert identify_quality("Eb") == "major"
    
    def test_major_chord_with_extensions(self):
        """Test identifying major quality with extensions."""
        assert identify_quality("Cadd9") == "major"
        assert identify_quality("Dadd11") == "major"
        assert identify_quality("G6") == "major"
        assert identify_quality("A9") == "major"
    
    # Requirement 4.2: Minor chords
    def test_minor_chord_with_m(self):
        """Test identifying minor quality with 'm' suffix."""
        assert identify_quality("Am") == "minor"
        assert identify_quality("Dm") == "minor"
        assert identify_quality("Em") == "minor"
        assert identify_quality("Bm") == "minor"
        assert identify_quality("Cm") == "minor"
        assert identify_quality("Fm") == "minor"
        assert identify_quality("Gm") == "minor"
    
    def test_minor_chord_with_min(self):
        """Test identifying minor quality with 'min' suffix."""
        assert identify_quality("Amin") == "minor"
        assert identify_quality("Dmin") == "minor"
        assert identify_quality("Emin") == "minor"
    
    def test_minor_chord_with_accidentals(self):
        """Test identifying minor quality with accidentals."""
        assert identify_quality("F#m") == "minor"
        assert identify_quality("Bbm") == "minor"
        assert identify_quality("C#m") == "minor"
        assert identify_quality("Ebm") == "minor"
    
    # Requirement 4.3: Seventh chords
    def test_dominant_seventh(self):
        """Test identifying seventh quality (dominant seventh)."""
        assert identify_quality("D7") == "seventh"
        assert identify_quality("A7") == "seventh"
        assert identify_quality("E7") == "seventh"
        assert identify_quality("G7") == "seventh"
        assert identify_quality("C7") == "seventh"
    
    def test_seventh_with_accidentals(self):
        """Test identifying seventh quality with accidentals."""
        assert identify_quality("F#7") == "seventh"
        assert identify_quality("Bb7") == "seventh"
        assert identify_quality("C#7") == "seventh"
    
    def test_seventh_with_extensions(self):
        """Test identifying seventh quality with extensions."""
        assert identify_quality("D7b9") == "seventh"
        assert identify_quality("G7#5") == "seventh"
        assert identify_quality("A7sus4") == "seventh"
    
    # Requirement 4.4: Major seventh chords
    def test_major_seventh_with_maj7(self):
        """Test identifying major seventh quality with 'maj7' suffix."""
        assert identify_quality("Cmaj7") == "major_seventh"
        assert identify_quality("Dmaj7") == "major_seventh"
        assert identify_quality("Gmaj7") == "major_seventh"
        assert identify_quality("Amaj7") == "major_seventh"
        assert identify_quality("Fmaj7") == "major_seventh"
    
    def test_major_seventh_with_M7(self):
        """Test identifying major seventh quality with 'M7' suffix."""
        assert identify_quality("CM7") == "major_seventh"
        assert identify_quality("DM7") == "major_seventh"
        assert identify_quality("GM7") == "major_seventh"
    
    def test_major_seventh_with_accidentals(self):
        """Test identifying major seventh quality with accidentals."""
        assert identify_quality("F#maj7") == "major_seventh"
        assert identify_quality("Bbmaj7") == "major_seventh"
        assert identify_quality("C#M7") == "major_seventh"
    
    # Requirement 4.5: Minor seventh chords
    def test_minor_seventh(self):
        """Test identifying minor seventh quality."""
        assert identify_quality("Bm7") == "minor_seventh"
        assert identify_quality("Am7") == "minor_seventh"
        assert identify_quality("Dm7") == "minor_seventh"
        assert identify_quality("Em7") == "minor_seventh"
        assert identify_quality("Cm7") == "minor_seventh"
    
    def test_minor_seventh_with_min7(self):
        """Test identifying minor seventh quality with 'min7' suffix."""
        assert identify_quality("Amin7") == "minor_seventh"
        assert identify_quality("Dmin7") == "minor_seventh"
    
    def test_minor_seventh_with_extensions(self):
        """Test identifying minor seventh quality with extensions."""
        assert identify_quality("F#m7b5") == "minor_seventh"
        assert identify_quality("Bm7b5") == "minor_seventh"
        assert identify_quality("Am7b9") == "minor_seventh"
    
    def test_minor_seventh_with_accidentals(self):
        """Test identifying minor seventh quality with accidentals."""
        assert identify_quality("F#m7") == "minor_seventh"
        assert identify_quality("Bbm7") == "minor_seventh"
        assert identify_quality("C#m7") == "minor_seventh"
    
    # Additional qualities
    def test_suspended_chords(self):
        """Test identifying suspended quality."""
        assert identify_quality("Gsus4") == "suspended"
        assert identify_quality("Dsus2") == "suspended"
        assert identify_quality("Asus4") == "suspended"
        assert identify_quality("Csus2") == "suspended"
    
    def test_augmented_chords(self):
        """Test identifying augmented quality."""
        assert identify_quality("Caug") == "augmented"
        assert identify_quality("Daug") == "augmented"
        assert identify_quality("C+") == "augmented"
        assert identify_quality("D+") == "augmented"
    
    def test_diminished_chords(self):
        """Test identifying diminished quality."""
        assert identify_quality("Cdim") == "diminished"
        assert identify_quality("Ddim") == "diminished"
        assert identify_quality("Bdim7") == "diminished"
    
    # Slash chords
    def test_slash_chord_quality(self):
        """Test identifying quality from slash chords."""
        assert identify_quality("D/F#") == "major"
        assert identify_quality("Am/C") == "minor"
        assert identify_quality("D7/F#") == "seventh"
        assert identify_quality("Cmaj7/E") == "major_seventh"
        assert identify_quality("Bm7/D") == "minor_seventh"
        assert identify_quality("AonC#") == "major"
        assert identify_quality("DmonF") == "minor"
    
    # Error cases
    def test_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="chord must be a non-empty string"):
            identify_quality("")
    
    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="chord cannot be empty after stripping whitespace"):
            identify_quality("   ")
    
    def test_none_raises_error(self):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError, match="chord must be a non-empty string"):
            identify_quality(None)
    
    def test_invalid_chord_raises_error(self):
        """Test that invalid chord format raises ValueError."""
        with pytest.raises(ValueError, match="Could not extract root note from chord"):
            identify_quality("123")
        with pytest.raises(ValueError, match="Could not extract root note from chord"):
            identify_quality("xyz")
        with pytest.raises(ValueError, match="Could not extract root note from chord"):
            identify_quality("@#$")
    
    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        assert identify_quality(" D ") == "major"
        assert identify_quality("  Am  ") == "minor"
        assert identify_quality(" D7 ") == "seventh"
        assert identify_quality(" Cmaj7 ") == "major_seventh"
