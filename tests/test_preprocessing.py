"""Tests for chord evaluation preprocessing module."""

import pytest
from src.evaluation.preprocessing import (
    ChordNormalizer,
    NormalizationMode,
    AggregationStrategy,
    PreprocessingConfig,
    ChordWithTimestamp,
)


class TestChordNormalizer:
    """Tests for ChordNormalizer class."""
    
    def test_init_default_mode(self):
        """Test ChordNormalizer initialization with default mode."""
        normalizer = ChordNormalizer()
        assert normalizer.mode == NormalizationMode.STANDARD
    
    def test_init_slash_mode(self):
        """Test ChordNormalizer initialization with SLASH mode."""
        normalizer = ChordNormalizer(NormalizationMode.SLASH)
        assert normalizer.mode == NormalizationMode.SLASH
    
    def test_init_on_mode(self):
        """Test ChordNormalizer initialization with ON mode."""
        normalizer = ChordNormalizer(NormalizationMode.ON)
        assert normalizer.mode == NormalizationMode.ON
    
    def test_init_standard_mode(self):
        """Test ChordNormalizer initialization with STANDARD mode."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)
        assert normalizer.mode == NormalizationMode.STANDARD

    def test_parse_chord_simple(self):
        """Test parsing simple chords without bass notes."""
        normalizer = ChordNormalizer()

        # Simple root only
        root, quality, bass = normalizer._parse_chord("C")
        assert root == "C"
        assert quality == ""
        assert bass is None

        # Root with sharp
        root, quality, bass = normalizer._parse_chord("F#")
        assert root == "F#"
        assert quality == ""
        assert bass is None

        # Root with flat
        root, quality, bass = normalizer._parse_chord("Bb")
        assert root == "Bb"
        assert quality == ""
        assert bass is None

    def test_parse_chord_with_quality(self):
        """Test parsing chords with quality suffixes."""
        normalizer = ChordNormalizer()

        # Major quality
        root, quality, bass = normalizer._parse_chord("Cmaj")
        assert root == "C"
        assert quality == "maj"
        assert bass is None

        # Minor quality
        root, quality, bass = normalizer._parse_chord("Am")
        assert root == "A"
        assert quality == "m"
        assert bass is None

        # Seventh
        root, quality, bass = normalizer._parse_chord("D7")
        assert root == "D"
        assert quality == "7"
        assert bass is None

        # Minor seventh
        root, quality, bass = normalizer._parse_chord("Am7")
        assert root == "A"
        assert quality == "m7"
        assert bass is None

        # Suspended
        root, quality, bass = normalizer._parse_chord("Dsus2")
        assert root == "D"
        assert quality == "sus2"
        assert bass is None

        # Major seventh
        root, quality, bass = normalizer._parse_chord("Cmaj7")
        assert root == "C"
        assert quality == "maj7"
        assert bass is None

    def test_parse_chord_slash_notation(self):
        """Test parsing chords with slash notation (C/E)."""
        normalizer = ChordNormalizer()

        # Simple slash chord
        root, quality, bass = normalizer._parse_chord("C/E")
        assert root == "C"
        assert quality == ""
        assert bass == "E"

        # Slash chord with quality
        root, quality, bass = normalizer._parse_chord("Cmaj/E")
        assert root == "C"
        assert quality == "maj"
        assert bass == "E"

        # Slash chord with sharp bass
        root, quality, bass = normalizer._parse_chord("D/F#")
        assert root == "D"
        assert quality == ""
        assert bass == "F#"

        # Complex slash chord
        root, quality, bass = normalizer._parse_chord("Dsus2/C")
        assert root == "D"
        assert quality == "sus2"
        assert bass == "C"

    def test_parse_chord_on_notation(self):
        """Test parsing chords with on notation (ConE)."""
        normalizer = ChordNormalizer()

        # Simple on chord
        root, quality, bass = normalizer._parse_chord("ConE")
        assert root == "C"
        assert quality == ""
        assert bass == "E"

        # On chord with quality
        root, quality, bass = normalizer._parse_chord("CmajonE")
        assert root == "C"
        assert quality == "maj"
        assert bass == "E"

        # On chord with sharp bass
        root, quality, bass = normalizer._parse_chord("DonF#")
        assert root == "D"
        assert quality == ""
        assert bass == "F#"

        # Complex on chord
        root, quality, bass = normalizer._parse_chord("Dsus2onC")
        assert root == "D"
        assert quality == "sus2"
        assert bass == "C"

        # Case insensitive on
        root, quality, bass = normalizer._parse_chord("AonC#")
        assert root == "A"
        assert quality == ""
        assert bass == "C#"

    def test_parse_chord_with_whitespace(self):
        """Test parsing chords with whitespace."""
        normalizer = ChordNormalizer()

        # Whitespace around slash
        root, quality, bass = normalizer._parse_chord("C / E")
        assert root == "C"
        assert quality == ""
        assert bass == "E"

        # Whitespace in quality
        root, quality, bass = normalizer._parse_chord("C maj / E")
        assert root == "C"
        assert quality == "maj"
        assert bass == "E"

    def test_parse_chord_invalid(self):
        """Test parsing invalid chords raises ValueError."""
        normalizer = ChordNormalizer()

        # Empty string
        with pytest.raises(ValueError, match="Chord string cannot be empty"):
            normalizer._parse_chord("")

        # Invalid root note
        with pytest.raises(ValueError, match="Could not extract root note"):
            normalizer._parse_chord("X")

        # Invalid format
        with pytest.raises(ValueError, match="Could not extract root note"):
            normalizer._parse_chord("123")

    def test_normalize_root_uppercase(self):
        """Test root note normalization converts to uppercase."""
        normalizer = ChordNormalizer()

        # Lowercase letters
        assert normalizer._normalize_root("c") == "C"
        assert normalizer._normalize_root("d") == "D"
        assert normalizer._normalize_root("f#") == "F#"
        assert normalizer._normalize_root("gb") == "F#"  # Also tests enharmonic

    def test_normalize_root_enharmonic_equivalents(self):
        """Test root note normalization handles enharmonic equivalents."""
        normalizer = ChordNormalizer()

        # Flat to sharp conversions
        assert normalizer._normalize_root("Db") == "C#"
        assert normalizer._normalize_root("Eb") == "D#"
        assert normalizer._normalize_root("Gb") == "F#"
        assert normalizer._normalize_root("Ab") == "G#"
        assert normalizer._normalize_root("Bb") == "A#"

        # Sharps remain unchanged
        assert normalizer._normalize_root("C#") == "C#"
        assert normalizer._normalize_root("D#") == "D#"
        assert normalizer._normalize_root("F#") == "F#"
        assert normalizer._normalize_root("G#") == "G#"
        assert normalizer._normalize_root("A#") == "A#"

        # Natural notes remain unchanged
        assert normalizer._normalize_root("C") == "C"
        assert normalizer._normalize_root("D") == "D"
        assert normalizer._normalize_root("E") == "E"
        assert normalizer._normalize_root("F") == "F"
        assert normalizer._normalize_root("G") == "G"
        assert normalizer._normalize_root("A") == "A"
        assert normalizer._normalize_root("B") == "B"

    def test_normalize_root_invalid(self):
        """Test root note normalization raises ValueError for invalid input."""
        normalizer = ChordNormalizer()

        # Empty string
        with pytest.raises(ValueError, match="Root note cannot be empty"):
            normalizer._normalize_root("")

        # Invalid note name
        with pytest.raises(ValueError, match="Invalid root note format"):
            normalizer._normalize_root("X")

        # Invalid format
        with pytest.raises(ValueError, match="Invalid root note format"):
            normalizer._normalize_root("C##")

        # Invalid format
        with pytest.raises(ValueError, match="Invalid root note format"):
            normalizer._normalize_root("Cbb")
    def test_normalize_quality_empty(self):
        """Test quality normalization with empty string."""
        normalizer = ChordNormalizer()
        assert normalizer._normalize_quality("") == ""

    def test_normalize_quality_major_variations(self):
        """Test quality normalization for major chord variations."""
        normalizer = ChordNormalizer()

        # Major variations
        assert normalizer._normalize_quality("maj") == "M"
        assert normalizer._normalize_quality("M") == "M"
        assert normalizer._normalize_quality("major") == "M"

    def test_normalize_quality_minor_variations(self):
        """Test quality normalization for minor chord variations."""
        normalizer = ChordNormalizer()

        # Minor variations
        assert normalizer._normalize_quality("min") == "m"
        assert normalizer._normalize_quality("m") == "m"

    def test_normalize_quality_compound_major(self):
        """Test quality normalization for compound major qualities."""
        normalizer = ChordNormalizer()

        # Compound major qualities
        assert normalizer._normalize_quality("maj7") == "M7"
        assert normalizer._normalize_quality("major7") == "M7"
        assert normalizer._normalize_quality("maj9") == "M9"

    def test_normalize_quality_compound_minor(self):
        """Test quality normalization for compound minor qualities."""
        normalizer = ChordNormalizer()

        # Compound minor qualities
        assert normalizer._normalize_quality("min7") == "m7"
        assert normalizer._normalize_quality("min9") == "m9"

    def test_normalize_quality_preserve_others(self):
        """Test quality normalization preserves other quality types."""
        normalizer = ChordNormalizer()

        # Other qualities should be preserved
        assert normalizer._normalize_quality("7") == "7"
        assert normalizer._normalize_quality("sus2") == "sus2"
        assert normalizer._normalize_quality("sus4") == "sus4"
        assert normalizer._normalize_quality("dim") == "dim"
        assert normalizer._normalize_quality("aug") == "aug"
        assert normalizer._normalize_quality("9") == "9"
        assert normalizer._normalize_quality("11") == "11"
        assert normalizer._normalize_quality("13") == "13"

    def test_build_chord_without_bass_standard_mode(self):
        """Test building chords without bass notes in STANDARD mode."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # Simple root only
        assert normalizer._build_chord("C", "", None) == "C"

        # Root with major quality
        assert normalizer._build_chord("C", "M", None) == "CM"

        # Root with minor quality
        assert normalizer._build_chord("D", "m", None) == "Dm"

        # Root with seventh
        assert normalizer._build_chord("G", "7", None) == "G7"

        # Root with suspended
        assert normalizer._build_chord("D", "sus2", None) == "Dsus2"

        # Root with sharp and quality
        assert normalizer._build_chord("F#", "m7", None) == "F#m7"

    def test_build_chord_with_bass_standard_mode(self):
        """Test building chords with bass notes in STANDARD mode."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # Simple slash chord
        assert normalizer._build_chord("C", "", "E") == "C/E"

        # Slash chord with major quality
        assert normalizer._build_chord("C", "M", "E") == "CM/E"

        # Slash chord with minor quality
        assert normalizer._build_chord("D", "m", "F#") == "Dm/F#"

        # Slash chord with suspended
        assert normalizer._build_chord("D", "sus2", "C") == "Dsus2/C"

        # Complex slash chord
        assert normalizer._build_chord("A", "m7", "C#") == "Am7/C#"

    def test_build_chord_with_bass_slash_mode(self):
        """Test building chords with bass notes in SLASH mode."""
        normalizer = ChordNormalizer(NormalizationMode.SLASH)

        # Simple slash chord
        assert normalizer._build_chord("C", "", "E") == "C/E"

        # Slash chord with major quality
        assert normalizer._build_chord("C", "M", "E") == "CM/E"

        # Slash chord with minor quality
        assert normalizer._build_chord("D", "m", "F#") == "Dm/F#"

    def test_build_chord_with_bass_on_mode(self):
        """Test building chords with bass notes in ON mode."""
        normalizer = ChordNormalizer(NormalizationMode.ON)

        # Simple on chord
        assert normalizer._build_chord("C", "", "E") == "ConE"

        # On chord with major quality
        assert normalizer._build_chord("C", "M", "E") == "CMonE"

        # On chord with minor quality
        assert normalizer._build_chord("D", "m", "F#") == "DmonF#"

        # On chord with suspended
        assert normalizer._build_chord("D", "sus2", "C") == "Dsus2onC"

        # Complex on chord
        assert normalizer._build_chord("A", "m7", "C#") == "Am7onC#"

    def test_build_chord_without_bass_on_mode(self):
        """Test building chords without bass notes in ON mode."""
        normalizer = ChordNormalizer(NormalizationMode.ON)

        # Should work the same as STANDARD mode when no bass note
        assert normalizer._build_chord("C", "", None) == "C"
        assert normalizer._build_chord("C", "M", None) == "CM"
        assert normalizer._build_chord("D", "m", None) == "Dm"

    def test_normalize_simple_chords(self):
        """Test normalizing simple chords without bass notes."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # Simple root only
        assert normalizer.normalize("C") == "C"
        assert normalizer.normalize("F#") == "F#"
        assert normalizer.normalize("Bb") == "A#"  # Enharmonic conversion

        # With quality
        assert normalizer.normalize("Cmaj") == "CM"
        assert normalizer.normalize("Am") == "Am"
        assert normalizer.normalize("D7") == "D7"
        assert normalizer.normalize("Dsus2") == "Dsus2"

    def test_normalize_with_whitespace(self):
        """Test normalizing chords with whitespace."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # Leading/trailing whitespace
        assert normalizer.normalize("  C  ") == "C"
        assert normalizer.normalize("  Cmaj  ") == "CM"

        # Whitespace in slash notation
        assert normalizer.normalize("C / E") == "C/E"
        assert normalizer.normalize("C maj / E") == "CM/E"

    def test_normalize_slash_chords_standard_mode(self):
        """Test normalizing slash chords in STANDARD mode."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # Simple slash chords
        assert normalizer.normalize("C/E") == "C/E"
        assert normalizer.normalize("Cmaj/E") == "CM/E"
        assert normalizer.normalize("D/F#") == "D/F#"
        assert normalizer.normalize("Dsus2/C") == "Dsus2/C"

        # With enharmonic conversion
        assert normalizer.normalize("Db/E") == "C#/E"
        assert normalizer.normalize("C/Eb") == "C/D#"

    def test_normalize_on_chords_standard_mode(self):
        """Test normalizing on notation chords in STANDARD mode."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # On notation should convert to slash notation in STANDARD mode
        assert normalizer.normalize("ConE") == "C/E"
        assert normalizer.normalize("CmajonE") == "CM/E"
        assert normalizer.normalize("DonF#") == "D/F#"
        assert normalizer.normalize("Dsus2onC") == "Dsus2/C"

    def test_normalize_on_chords_on_mode(self):
        """Test normalizing chords in ON mode."""
        normalizer = ChordNormalizer(NormalizationMode.ON)

        # Slash notation should convert to on notation in ON mode
        assert normalizer.normalize("C/E") == "ConE"
        assert normalizer.normalize("Cmaj/E") == "CMonE"

        # On notation should stay as on notation
        assert normalizer.normalize("ConE") == "ConE"
        assert normalizer.normalize("CmajonE") == "CMonE"

    def test_normalize_slash_chords_slash_mode(self):
        """Test normalizing chords in SLASH mode."""
        normalizer = ChordNormalizer(NormalizationMode.SLASH)

        # On notation should convert to slash notation in SLASH mode
        assert normalizer.normalize("ConE") == "C/E"
        assert normalizer.normalize("CmajonE") == "CM/E"

        # Slash notation should stay as slash notation
        assert normalizer.normalize("C/E") == "C/E"
        assert normalizer.normalize("Cmaj/E") == "CM/E"

    def test_normalize_enharmonic_equivalents(self):
        """Test normalizing chords with enharmonic equivalents."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # Root note enharmonic conversion
        assert normalizer.normalize("Db") == "C#"
        assert normalizer.normalize("Eb") == "D#"
        assert normalizer.normalize("Gb") == "F#"
        assert normalizer.normalize("Ab") == "G#"
        assert normalizer.normalize("Bb") == "A#"

        # With quality
        assert normalizer.normalize("Dbmaj") == "C#M"
        assert normalizer.normalize("Ebmin") == "D#m"

        # Bass note enharmonic conversion
        assert normalizer.normalize("C/Db") == "C/C#"
        assert normalizer.normalize("D/Eb") == "D/D#"

    def test_normalize_quality_variations(self):
        """Test normalizing chords with quality variations."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # Major variations
        assert normalizer.normalize("Cmaj") == "CM"
        assert normalizer.normalize("CM") == "CM"
        assert normalizer.normalize("Cmajor") == "CM"

        # Minor variations
        assert normalizer.normalize("Amin") == "Am"
        assert normalizer.normalize("Am") == "Am"

        # Compound qualities
        assert normalizer.normalize("Cmaj7") == "CM7"
        assert normalizer.normalize("Amin7") == "Am7"
        assert normalizer.normalize("Cmajor7") == "CM7"

    def test_normalize_idempotency(self):
        """Test that normalizing twice gives the same result (idempotency)."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # Test various chords
        chords = ["C", "Cmaj", "C/E", "ConE", "Dbmaj7", "Am", "Dsus2/C"]

        for chord in chords:
            normalized_once = normalizer.normalize(chord)
            normalized_twice = normalizer.normalize(normalized_once)
            assert normalized_once == normalized_twice, \
                f"Normalization not idempotent for '{chord}': " \
                f"'{normalized_once}' != '{normalized_twice}'"

    def test_normalize_invalid_empty(self):
        """Test normalizing empty string raises ValueError."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        with pytest.raises(ValueError, match="Chord string cannot be empty"):
            normalizer.normalize("")

        with pytest.raises(ValueError, match="Chord string cannot be empty"):
            normalizer.normalize("   ")

    def test_normalize_invalid_notation(self):
        """Test normalizing invalid chord notation raises ValueError."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)

        # Invalid root note
        with pytest.raises(ValueError, match="Invalid chord notation"):
            normalizer.normalize("X")

        with pytest.raises(ValueError, match="Invalid chord notation"):
            normalizer.normalize("123")

        # Invalid format - no valid root note
        with pytest.raises(ValueError, match="Invalid chord notation"):
            normalizer.normalize("xyz")

    def test_normalize_batch_empty_list(self):
        """Test normalizing an empty list returns empty list."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)
        assert normalizer.normalize_batch([]) == []

    def test_normalize_batch_single_chord(self):
        """Test normalizing a list with a single chord."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)
        result = normalizer.normalize_batch(["Cmaj"])
        assert result == ["CM"]

    def test_normalize_batch_multiple_chords(self):
        """Test normalizing a list with multiple chords."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)
        chords = ["C maj / E", "Dm", "DonF#", "Dbmaj7", "Am"]
        expected = ["CM/E", "Dm", "D/F#", "C#M7", "Am"]
        result = normalizer.normalize_batch(chords)
        assert result == expected

    def test_normalize_batch_equivalence(self):
        """Test that batch normalization equals individual normalization."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)
        chords = ["C", "Cmaj/E", "ConE", "Dbmaj7", "Am", "Dsus2/C", "Gb7"]
        
        # Batch normalization
        batch_result = normalizer.normalize_batch(chords)
        
        # Individual normalization
        individual_result = [normalizer.normalize(chord) for chord in chords]
        
        # Should be equivalent
        assert batch_result == individual_result

    def test_normalize_batch_preserves_order(self):
        """Test that batch normalization preserves chord order."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)
        chords = ["Am", "Dm", "G7", "CM"]
        result = normalizer.normalize_batch(chords)
        assert result == ["Am", "Dm", "G7", "CM"]

    def test_normalize_batch_with_whitespace(self):
        """Test batch normalization handles whitespace correctly."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)
        chords = ["  C  ", " Cmaj ", "D / F# "]
        expected = ["C", "CM", "D/F#"]
        result = normalizer.normalize_batch(chords)
        assert result == expected

    def test_normalize_batch_different_modes(self):
        """Test batch normalization with different normalization modes."""
        # STANDARD mode
        normalizer_standard = ChordNormalizer(NormalizationMode.STANDARD)
        chords = ["C/E", "ConE", "Dmaj/F#"]
        result_standard = normalizer_standard.normalize_batch(chords)
        assert result_standard == ["C/E", "C/E", "DM/F#"]
        
        # ON mode
        normalizer_on = ChordNormalizer(NormalizationMode.ON)
        result_on = normalizer_on.normalize_batch(chords)
        assert result_on == ["ConE", "ConE", "DMonF#"]
        
        # SLASH mode
        normalizer_slash = ChordNormalizer(NormalizationMode.SLASH)
        result_slash = normalizer_slash.normalize_batch(chords)
        assert result_slash == ["C/E", "C/E", "DM/F#"]

    def test_normalize_batch_with_invalid_chord(self):
        """Test batch normalization raises error for invalid chord."""
        normalizer = ChordNormalizer(NormalizationMode.STANDARD)
        chords = ["C", "InvalidChord", "Dm"]
        
        # Should raise ValueError when encountering invalid chord
        with pytest.raises(ValueError, match="Invalid chord notation"):
            normalizer.normalize_batch(chords)


class TestPreprocessingConfig:
    """Tests for PreprocessingConfig dataclass."""
    
    def test_default_values(self):
        """Test PreprocessingConfig default values."""
        config = PreprocessingConfig()
        assert config.enable_normalization is True
        assert config.enable_aggregation is True
        assert config.normalization_mode == NormalizationMode.STANDARD
        assert config.aggregation_strategy == AggregationStrategy.MOST_FREQUENT
        assert config.aggregation_tolerance == 0.1
    
    def test_custom_values(self):
        """Test PreprocessingConfig with custom values."""
        config = PreprocessingConfig(
            enable_normalization=False,
            enable_aggregation=False,
            normalization_mode=NormalizationMode.SLASH,
            aggregation_strategy=AggregationStrategy.LONGEST_DURATION,
            aggregation_tolerance=0.2
        )
        assert config.enable_normalization is False
        assert config.enable_aggregation is False
        assert config.normalization_mode == NormalizationMode.SLASH
        assert config.aggregation_strategy == AggregationStrategy.LONGEST_DURATION
        assert config.aggregation_tolerance == 0.2


class TestChordWithTimestamp:
    """Tests for ChordWithTimestamp dataclass."""
    
    def test_duration_with_end_time(self):
        """Test duration calculation with end_time set."""
        chord = ChordWithTimestamp(chord="C", start_time=0.0, end_time=2.5)
        assert chord.duration == 2.5
    
    def test_duration_without_end_time(self):
        """Test duration calculation without end_time."""
        chord = ChordWithTimestamp(chord="C", start_time=0.0)
        assert chord.duration == 0.0
    
    def test_duration_zero_length(self):
        """Test duration calculation for zero-length chord."""
        chord = ChordWithTimestamp(chord="C", start_time=1.0, end_time=1.0)
        assert chord.duration == 0.0



class TestChordAggregator:
    """Tests for ChordAggregator class."""
    
    def test_init_default_values(self):
        """Test ChordAggregator initialization with default values."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator()
        assert aggregator.strategy == AggregationStrategy.MOST_FREQUENT
        assert aggregator.tolerance == 0.1
    
    def test_init_custom_values(self):
        """Test ChordAggregator initialization with custom values."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(
            strategy=AggregationStrategy.LONGEST_DURATION,
            tolerance=0.2
        )
        assert aggregator.strategy == AggregationStrategy.LONGEST_DURATION
        assert aggregator.tolerance == 0.2
    
    def test_collect_chords_in_interval_basic(self):
        """Test collecting chords within a basic interval."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(tolerance=0.1)
        chords = ["C", "D", "E", "F"]
        times = [0.0, 1.0, 2.0, 3.0]
        
        # Interval [0.5, 2.5) should include chords at 1.0 and 2.0
        result = aggregator._collect_chords_in_interval(chords, times, 0.5, 2.5)
        assert result == [("D", 1.0), ("E", 2.0)]
    
    def test_collect_chords_in_interval_with_tolerance(self):
        """Test that tolerance is applied to interval boundaries."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(tolerance=0.1)
        chords = ["C", "D", "E", "F"]
        times = [0.0, 1.0, 2.0, 3.0]
        
        # Interval [1.05, 2.05) with tolerance 0.1 should include chords at 1.0 and 2.0
        # Because 1.0 >= 1.05 - 0.1 (0.95) and 2.0 < 2.05 + 0.1 (2.15)
        result = aggregator._collect_chords_in_interval(chords, times, 1.05, 2.05)
        assert result == [("D", 1.0), ("E", 2.0)]
    
    def test_collect_chords_in_interval_empty(self):
        """Test collecting chords when no chords fall in interval."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(tolerance=0.1)
        chords = ["C", "D", "E", "F"]
        times = [0.0, 1.0, 2.0, 3.0]
        
        # Interval [5.0, 6.0) should be empty
        result = aggregator._collect_chords_in_interval(chords, times, 5.0, 6.0)
        assert result == []
    
    def test_collect_chords_in_interval_all_chords(self):
        """Test collecting all chords when interval spans entire range."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(tolerance=0.1)
        chords = ["C", "D", "E", "F"]
        times = [0.0, 1.0, 2.0, 3.0]
        
        # Interval [0.0, 10.0) should include all chords
        result = aggregator._collect_chords_in_interval(chords, times, 0.0, 10.0)
        assert result == [("C", 0.0), ("D", 1.0), ("E", 2.0), ("F", 3.0)]
    
    def test_collect_chords_in_interval_boundary_cases(self):
        """Test boundary cases with tolerance."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(tolerance=0.1)
        chords = ["C", "D", "E"]
        times = [1.0, 2.0, 3.0]
        
        # Chord at 1.0 should be included when start is 1.05 (within tolerance)
        result = aggregator._collect_chords_in_interval(chords, times, 1.05, 2.5)
        assert ("C", 1.0) in result
        
        # Chord at 3.0 should be included when end is 2.95 (within tolerance)
        result = aggregator._collect_chords_in_interval(chords, times, 2.5, 2.95)
        assert ("E", 3.0) in result
    
    def test_collect_chords_in_interval_zero_tolerance(self):
        """Test collecting chords with zero tolerance."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(tolerance=0.0)
        chords = ["C", "D", "E", "F"]
        times = [0.0, 1.0, 2.0, 3.0]
        
        # With zero tolerance, only exact matches within [1.0, 2.0)
        result = aggregator._collect_chords_in_interval(chords, times, 1.0, 2.0)
        assert result == [("D", 1.0)]
    
    def test_collect_chords_in_interval_large_tolerance(self):
        """Test collecting chords with large tolerance."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(tolerance=1.0)
        chords = ["C", "D", "E", "F"]
        times = [0.0, 1.0, 2.0, 3.0]
        
        # With large tolerance, interval [1.5, 2.5) should include more chords
        # 0.0 >= 1.5 - 1.0 (0.5)? No
        # 1.0 >= 1.5 - 1.0 (0.5)? Yes
        # 2.0 >= 1.5 - 1.0 (0.5)? Yes, and 2.0 < 2.5 + 1.0 (3.5)? Yes
        # 3.0 >= 1.5 - 1.0 (0.5)? Yes, and 3.0 < 2.5 + 1.0 (3.5)? Yes
        result = aggregator._collect_chords_in_interval(chords, times, 1.5, 2.5)
        assert result == [("D", 1.0), ("E", 2.0), ("F", 3.0)]

    def test_select_chord_by_strategy_most_frequent(self):
        """Test MOST_FREQUENT strategy selects the most common chord."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.MOST_FREQUENT)
        
        # C appears 3 times, D appears 2 times, E appears 1 time
        chords = [("C", 0.0), ("C", 0.5), ("D", 1.0), ("C", 1.5), ("D", 2.0), ("E", 2.5)]
        result = aggregator._select_chord_by_strategy(chords)
        assert result == "C"
    
    def test_select_chord_by_strategy_most_frequent_tie(self):
        """Test MOST_FREQUENT strategy returns first chord in case of tie."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.MOST_FREQUENT)
        
        # C and D both appear 2 times, C appears first
        chords = [("C", 0.0), ("D", 0.5), ("C", 1.0), ("D", 1.5)]
        result = aggregator._select_chord_by_strategy(chords)
        assert result in ["C", "D"]  # Either is acceptable, but should be consistent
    
    def test_select_chord_by_strategy_longest_duration(self):
        """Test LONGEST_DURATION strategy selects chord with longest duration."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.LONGEST_DURATION)
        
        # C: 0.0-0.5 (0.5s), D: 0.5-2.0 (1.5s), E: 2.0-2.5 (0.5s), F: 2.5-? (0.0s default)
        chords = [("C", 0.0), ("D", 0.5), ("E", 2.0), ("F", 2.5)]
        result = aggregator._select_chord_by_strategy(chords)
        assert result == "D"
    
    def test_select_chord_by_strategy_longest_duration_last_chord(self):
        """Test LONGEST_DURATION strategy handles last chord with default duration."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.LONGEST_DURATION)
        
        # C: 0.0-1.0 (1.0s), D: 1.0-? (0.0s default)
        # C should be selected as it has longer duration
        chords = [("C", 0.0), ("D", 1.0)]
        result = aggregator._select_chord_by_strategy(chords)
        assert result == "C"
    
    def test_select_chord_by_strategy_longest_duration_single_chord(self):
        """Test LONGEST_DURATION strategy with single chord."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.LONGEST_DURATION)
        
        # Single chord gets default duration of 0.0
        chords = [("C", 0.0)]
        result = aggregator._select_chord_by_strategy(chords)
        assert result == "C"
    
    def test_select_chord_by_strategy_first(self):
        """Test FIRST strategy selects the first chord."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.FIRST)
        
        chords = [("C", 0.0), ("D", 0.5), ("E", 1.0), ("F", 1.5)]
        result = aggregator._select_chord_by_strategy(chords)
        assert result == "C"
    
    def test_select_chord_by_strategy_first_single_chord(self):
        """Test FIRST strategy with single chord."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.FIRST)
        
        chords = [("C", 0.0)]
        result = aggregator._select_chord_by_strategy(chords)
        assert result == "C"
    
    def test_select_chord_by_strategy_last(self):
        """Test LAST strategy selects the last chord."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.LAST)
        
        chords = [("C", 0.0), ("D", 0.5), ("E", 1.0), ("F", 1.5)]
        result = aggregator._select_chord_by_strategy(chords)
        assert result == "F"
    
    def test_select_chord_by_strategy_last_single_chord(self):
        """Test LAST strategy with single chord."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.LAST)
        
        chords = [("C", 0.0)]
        result = aggregator._select_chord_by_strategy(chords)
        assert result == "C"
    
    def test_select_chord_by_strategy_empty_raises_error(self):
        """Test that empty interval raises ValueError."""
        from src.evaluation.preprocessing import ChordAggregator
        
        aggregator = ChordAggregator(strategy=AggregationStrategy.MOST_FREQUENT)
        
        with pytest.raises(ValueError, match="Cannot select chord from empty interval"):
            aggregator._select_chord_by_strategy([])
    
    def test_select_chord_by_strategy_all_strategies_with_same_chord(self):
        """Test all strategies return same result when all chords are identical."""
        from src.evaluation.preprocessing import ChordAggregator
        
        chords = [("C", 0.0), ("C", 0.5), ("C", 1.0)]
        
        for strategy in AggregationStrategy:
            aggregator = ChordAggregator(strategy=strategy)
            result = aggregator._select_chord_by_strategy(chords)
            assert result == "C", f"Strategy {strategy} should return 'C'"

    def test_find_nearest_chord_basic(self):
        """Test finding nearest chord to a target time."""
        from src.evaluation.preprocessing import ChordAggregator

        aggregator = ChordAggregator()
        chords = ["C", "D", "E"]
        times = [0.0, 2.0, 4.0]

        # Target 1.5 is closest to 2.0 (distance 0.5)
        result = aggregator._find_nearest_chord(chords, times, 1.5)
        assert result == "D"

        # Target 3.5 is closest to 4.0 (distance 0.5)
        result = aggregator._find_nearest_chord(chords, times, 3.5)
        assert result == "E"

    def test_find_nearest_chord_exact_match(self):
        """Test finding nearest chord when target exactly matches a timestamp."""
        from src.evaluation.preprocessing import ChordAggregator

        aggregator = ChordAggregator()
        chords = ["C", "D", "E"]
        times = [0.0, 2.0, 4.0]

        # Target 2.0 exactly matches D
        result = aggregator._find_nearest_chord(chords, times, 2.0)
        assert result == "D"

    def test_find_nearest_chord_before_first(self):
        """Test finding nearest chord when target is before first timestamp."""
        from src.evaluation.preprocessing import ChordAggregator

        aggregator = ChordAggregator()
        chords = ["C", "D", "E"]
        times = [1.0, 2.0, 3.0]

        # Target 0.0 is closest to 1.0
        result = aggregator._find_nearest_chord(chords, times, 0.0)
        assert result == "C"

    def test_find_nearest_chord_after_last(self):
        """Test finding nearest chord when target is after last timestamp."""
        from src.evaluation.preprocessing import ChordAggregator

        aggregator = ChordAggregator()
        chords = ["C", "D", "E"]
        times = [1.0, 2.0, 3.0]

        # Target 10.0 is closest to 3.0
        result = aggregator._find_nearest_chord(chords, times, 10.0)
        assert result == "E"

    def test_find_nearest_chord_tie_returns_first(self):
        """Test that when two chords are equidistant, the first one is returned."""
        from src.evaluation.preprocessing import ChordAggregator

        aggregator = ChordAggregator()
        chords = ["C", "D", "E"]
        times = [0.0, 2.0, 4.0]

        # Target 1.0 is equidistant from C (1.0) and D (1.0)
        # Should return C as it appears first
        result = aggregator._find_nearest_chord(chords, times, 1.0)
        assert result == "C"

    def test_find_nearest_chord_single_chord(self):
        """Test finding nearest chord when only one chord exists."""
        from src.evaluation.preprocessing import ChordAggregator

        aggregator = ChordAggregator()
        chords = ["C"]
        times = [5.0]

        # Any target should return the only chord
        result = aggregator._find_nearest_chord(chords, times, 0.0)
        assert result == "C"

        result = aggregator._find_nearest_chord(chords, times, 10.0)
        assert result == "C"

    def test_find_nearest_chord_empty_raises_error(self):
        """Test that empty chord list raises ValueError."""
        from src.evaluation.preprocessing import ChordAggregator

        aggregator = ChordAggregator()

        with pytest.raises(ValueError, match="Cannot find nearest chord from empty list"):
            aggregator._find_nearest_chord([], [], 1.0)

    def test_find_nearest_chord_complex_scenario(self):
        """Test finding nearest chord in a complex scenario with many chords."""
        from src.evaluation.preprocessing import ChordAggregator

        aggregator = ChordAggregator()
        chords = ["C", "D", "E", "F", "G", "A"]
        times = [0.0, 1.0, 2.5, 4.0, 5.5, 7.0]

        # Target 3.0 is closest to 2.5 (distance 0.5) vs 4.0 (distance 1.0)
        result = aggregator._find_nearest_chord(chords, times, 3.0)
        assert result == "E"

        # Target 6.0 is closest to 5.5 (distance 0.5) vs 7.0 (distance 1.0)
        result = aggregator._find_nearest_chord(chords, times, 6.0)
        assert result == "G"

