"""Unit tests for ground truth parser.

Tests format detection and parsing functionality for three formats:
- chord-only: [D][AonC#][Bm7]
- lyrics-with-chords: 涙[D]があふれ[AonC#]る
- lyrics-only: Plain text without chords
"""

import pytest
from src.evaluation.parser import GroundTruthParser
from src.evaluation.models import ChordAnnotation


class TestFormatDetection:
    """Test format detection functionality."""
    
    def test_detect_chord_only_format(self):
        """Test detection of chord-only format."""
        parser = GroundTruthParser()
        
        # Simple chord-only format
        content = "[D][AonC#][Bm7]"
        assert parser.detect_format(content) == 'chord_only'
        
        # Chord-only with whitespace
        content = "[D] [AonC#] [Bm7]"
        assert parser.detect_format(content) == 'chord_only'
        
        # Chord-only with newlines
        content = "[D]\n[AonC#]\n[Bm7]"
        assert parser.detect_format(content) == 'chord_only'
    
    def test_detect_lyrics_with_chords_format(self):
        """Test detection of lyrics-with-chords format."""
        parser = GroundTruthParser()
        
        # Japanese lyrics with chords
        content = "涙[D]があふれ[AonC#]る"
        assert parser.detect_format(content) == 'lyrics_with_chords'
        
        # English lyrics with chords
        content = "Hello [G]world [C]today"
        assert parser.detect_format(content) == 'lyrics_with_chords'
        
        # Lyrics with chords and newlines
        content = "First line [D]here\nSecond line [G]there"
        assert parser.detect_format(content) == 'lyrics_with_chords'
    
    def test_detect_lyrics_only_format(self):
        """Test detection of lyrics-only format."""
        parser = GroundTruthParser()
        
        # Simple lyrics without chords
        content = "This is just plain text"
        assert parser.detect_format(content) == 'lyrics_only'
        
        # Japanese lyrics without chords
        content = "涙があふれる"
        assert parser.detect_format(content) == 'lyrics_only'
        
        # Multi-line lyrics without chords
        content = "First line\nSecond line\nThird line"
        assert parser.detect_format(content) == 'lyrics_only'
    
    def test_detect_format_with_empty_brackets(self):
        """Test format detection with empty brackets."""
        parser = GroundTruthParser()
        
        # Empty brackets should still be detected as chord format
        content = "[D][][Bm7]"
        assert parser.detect_format(content) == 'chord_only'
        
        # Empty brackets with text
        content = "Hello []world [D]today"
        assert parser.detect_format(content) == 'lyrics_with_chords'
    
    def test_detect_format_edge_cases(self):
        """Test format detection edge cases."""
        parser = GroundTruthParser()
        
        # Single chord
        content = "[D]"
        assert parser.detect_format(content) == 'chord_only'
        
        # Single word with chord
        content = "word[D]"
        assert parser.detect_format(content) == 'lyrics_with_chords'
        
        # Chord at start of lyrics
        content = "[D]Hello world"
        assert parser.detect_format(content) == 'lyrics_with_chords'
        
        # Chord at end of lyrics
        content = "Hello world[D]"
        assert parser.detect_format(content) == 'lyrics_with_chords'
    
    def test_detect_format_invalid_input(self):
        """Test format detection with invalid input."""
        parser = GroundTruthParser()
        
        # Empty string
        with pytest.raises(ValueError, match="content must be a non-empty string"):
            parser.detect_format("")
        
        # Whitespace only
        with pytest.raises(ValueError, match="content cannot be empty after stripping"):
            parser.detect_format("   \n\t  ")
        
        # None input
        with pytest.raises(ValueError, match="content must be a non-empty string"):
            parser.detect_format(None)



class TestChordOnlyParsing:
    """Test chord-only format parsing functionality."""
    
    def test_parse_simple_chord_sequence(self):
        """Test parsing simple chord sequence."""
        parser = GroundTruthParser()
        content = "[D][AonC#][Bm7]"
        
        annotations = parser.parse_chord_only_format(content)
        
        assert len(annotations) == 3
        assert annotations[0].chord == "D"
        assert annotations[0].position == 0
        assert annotations[1].chord == "AonC#"
        assert annotations[1].position == 1
        assert annotations[2].chord == "Bm7"
        assert annotations[2].position == 2
    
    def test_parse_chord_sequence_with_whitespace(self):
        """Test parsing chord sequence with whitespace between brackets."""
        parser = GroundTruthParser()
        content = "[D] [AonC#] [Bm7]"
        
        annotations = parser.parse_chord_only_format(content)
        
        assert len(annotations) == 3
        assert annotations[0].chord == "D"
        assert annotations[0].position == 0
        assert annotations[1].chord == "AonC#"
        assert annotations[1].position == 1
        assert annotations[2].chord == "Bm7"
        assert annotations[2].position == 2
    
    def test_parse_chord_sequence_with_newlines(self):
        """Test parsing chord sequence with newlines."""
        parser = GroundTruthParser()
        content = "[D]\n[AonC#]\n[Bm7]"
        
        annotations = parser.parse_chord_only_format(content)
        
        assert len(annotations) == 3
        assert annotations[0].chord == "D"
        assert annotations[1].chord == "AonC#"
        assert annotations[2].chord == "Bm7"
    
    def test_parse_ignores_empty_brackets(self):
        """Test that empty brackets are ignored."""
        parser = GroundTruthParser()
        content = "[D][][AonC#][Bm7][]"
        
        annotations = parser.parse_chord_only_format(content)
        
        # Should only have 3 chords, empty brackets ignored
        assert len(annotations) == 3
        assert annotations[0].chord == "D"
        assert annotations[0].position == 0
        assert annotations[1].chord == "AonC#"
        assert annotations[1].position == 1
        assert annotations[2].chord == "Bm7"
        assert annotations[2].position == 2
    
    def test_parse_single_chord(self):
        """Test parsing single chord."""
        parser = GroundTruthParser()
        content = "[D]"
        
        annotations = parser.parse_chord_only_format(content)
        
        assert len(annotations) == 1
        assert annotations[0].chord == "D"
        assert annotations[0].position == 0
    
    def test_parse_complex_chord_names(self):
        """Test parsing various complex chord names."""
        parser = GroundTruthParser()
        content = "[Cmaj7][Dm7][G7][Am][F#m7b5][Bb9]"
        
        annotations = parser.parse_chord_only_format(content)
        
        assert len(annotations) == 6
        assert annotations[0].chord == "Cmaj7"
        assert annotations[1].chord == "Dm7"
        assert annotations[2].chord == "G7"
        assert annotations[3].chord == "Am"
        assert annotations[4].chord == "F#m7b5"
        assert annotations[5].chord == "Bb9"
    
    def test_parse_positions_are_sequential(self):
        """Test that positions are sequential starting from 0."""
        parser = GroundTruthParser()
        content = "[C][D][E][F][G][A][B]"
        
        annotations = parser.parse_chord_only_format(content)
        
        assert len(annotations) == 7
        for i, annotation in enumerate(annotations):
            assert annotation.position == i
    
    def test_parse_chord_with_whitespace_inside_brackets(self):
        """Test parsing chords with whitespace inside brackets."""
        parser = GroundTruthParser()
        content = "[ D ][ AonC# ][ Bm7 ]"
        
        annotations = parser.parse_chord_only_format(content)
        
        # Whitespace should be stripped
        assert len(annotations) == 3
        assert annotations[0].chord == "D"
        assert annotations[1].chord == "AonC#"
        assert annotations[2].chord == "Bm7"
    
    def test_parse_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        parser = GroundTruthParser()
        
        with pytest.raises(ValueError, match="content must be a non-empty string"):
            parser.parse_chord_only_format("")
    
    def test_parse_none_content_raises_error(self):
        """Test that None content raises ValueError."""
        parser = GroundTruthParser()
        
        with pytest.raises(ValueError, match="content must be a non-empty string"):
            parser.parse_chord_only_format(None)
    
    def test_parse_only_empty_brackets_returns_empty_list(self):
        """Test that content with only empty brackets returns empty list."""
        parser = GroundTruthParser()
        content = "[][][]"
        
        # Should raise ValueError indicating no chords found
        with pytest.raises(ValueError, match="No chords found in chord-only format"):
            parser.parse_chord_only_format(content)
    
    def test_parse_returns_chord_annotation_objects(self):
        """Test that parser returns proper ChordAnnotation objects."""
        parser = GroundTruthParser()
        content = "[D][G]"
        
        annotations = parser.parse_chord_only_format(content)
        
        assert all(isinstance(ann, ChordAnnotation) for ann in annotations)
        assert all(ann.timestamp == 0.0 for ann in annotations)  # Default timestamp



class TestLyricsWithChordsParsing:
    """Test lyrics-with-chords format parsing functionality."""
    
    def test_parse_japanese_lyrics_with_chords(self):
        """Test parsing Japanese lyrics with embedded chords."""
        parser = GroundTruthParser()
        content = "涙[D]があふれ[AonC#]る"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 2
        assert annotations[0].chord == "D"
        assert annotations[0].position == 1  # Position of '[' in "涙[D]"
        assert annotations[1].chord == "AonC#"
        assert annotations[1].position == 8  # Position of '[' in "があふれ[AonC#]"
    
    def test_parse_english_lyrics_with_chords(self):
        """Test parsing English lyrics with embedded chords."""
        parser = GroundTruthParser()
        content = "Hello [G]world [C]today"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 2
        assert annotations[0].chord == "G"
        assert annotations[0].position == 6  # Position of '[' in "Hello [G]"
        assert annotations[1].chord == "C"
        assert annotations[1].position == 15  # Position of '[' in "world [C]"
    
    def test_parse_chord_at_start_of_lyrics(self):
        """Test parsing chord at the start of lyrics."""
        parser = GroundTruthParser()
        content = "[D]Hello world"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 1
        assert annotations[0].chord == "D"
        assert annotations[0].position == 0  # Position of '[' at start
    
    def test_parse_chord_at_end_of_lyrics(self):
        """Test parsing chord at the end of lyrics."""
        parser = GroundTruthParser()
        content = "Hello world[D]"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 1
        assert annotations[0].chord == "D"
        assert annotations[0].position == 11  # Position of '[' at "world[D]"
    
    def test_parse_multiple_chords_in_lyrics(self):
        """Test parsing multiple chords embedded in lyrics."""
        parser = GroundTruthParser()
        content = "First[D] line here[G]\nSecond[Am] line there[C]"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 4
        assert annotations[0].chord == "D"
        assert annotations[1].chord == "G"
        assert annotations[2].chord == "Am"
        assert annotations[3].chord == "C"
        
        # Verify positions are monotonically increasing
        for i in range(len(annotations) - 1):
            assert annotations[i].position < annotations[i + 1].position
    
    def test_parse_ignores_empty_brackets_in_lyrics(self):
        """Test that empty brackets are ignored in lyrics."""
        parser = GroundTruthParser()
        content = "Hello[]world[D]today[]end[G]"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        # Should only have 2 chords, empty brackets ignored
        assert len(annotations) == 2
        assert annotations[0].chord == "D"
        assert annotations[1].chord == "G"
    
    def test_parse_complex_chord_names_in_lyrics(self):
        """Test parsing various complex chord names in lyrics."""
        parser = GroundTruthParser()
        content = "Song[Cmaj7] with[Dm7] complex[G7] chords[F#m7b5]"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 4
        assert annotations[0].chord == "Cmaj7"
        assert annotations[1].chord == "Dm7"
        assert annotations[2].chord == "G7"
        assert annotations[3].chord == "F#m7b5"
    
    def test_parse_positions_reflect_character_indices(self):
        """Test that positions accurately reflect character indices."""
        parser = GroundTruthParser()
        content = "abc[D]efg[G]hij"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 2
        # Position should be the index of '[' character
        assert content[annotations[0].position] == '['
        assert content[annotations[1].position] == '['
        # Verify the chord follows the bracket
        assert content[annotations[0].position:annotations[0].position+3] == '[D]'
        assert content[annotations[1].position:annotations[1].position+3] == '[G]'
    
    def test_parse_chord_with_whitespace_inside_brackets(self):
        """Test parsing chords with whitespace inside brackets in lyrics."""
        parser = GroundTruthParser()
        content = "Hello[ D ]world[ G ]"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        # Whitespace should be stripped from chord names
        assert len(annotations) == 2
        assert annotations[0].chord == "D"
        assert annotations[1].chord == "G"
    
    def test_parse_multiline_lyrics_with_chords(self):
        """Test parsing multi-line lyrics with chords."""
        parser = GroundTruthParser()
        content = "First[D] line\nSecond[G] line\nThird[Am] line"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 3
        assert annotations[0].chord == "D"
        assert annotations[1].chord == "G"
        assert annotations[2].chord == "Am"
        
        # Positions should account for newline characters
        for i in range(len(annotations) - 1):
            assert annotations[i].position < annotations[i + 1].position
    
    def test_parse_unicode_lyrics_with_chords(self):
        """Test parsing Unicode lyrics with chords."""
        parser = GroundTruthParser()
        # Mix of Japanese, Chinese, and emoji
        content = "日本[D]語と中文[G]🎵"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 2
        assert annotations[0].chord == "D"
        assert annotations[1].chord == "G"
    
    def test_parse_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        parser = GroundTruthParser()
        
        with pytest.raises(ValueError, match="content must be a non-empty string"):
            parser.parse_lyrics_with_chords("")
    
    def test_parse_none_content_raises_error(self):
        """Test that None content raises ValueError."""
        parser = GroundTruthParser()
        
        with pytest.raises(ValueError, match="content must be a non-empty string"):
            parser.parse_lyrics_with_chords(None)
    
    def test_parse_only_empty_brackets_returns_empty_list(self):
        """Test that lyrics with only empty brackets returns empty list."""
        parser = GroundTruthParser()
        content = "Hello[]world[]"
        
        # Should raise ValueError indicating no chords found
        with pytest.raises(ValueError, match="No chords found in lyrics-with-chords format"):
            parser.parse_lyrics_with_chords(content)
    
    def test_parse_returns_chord_annotation_objects(self):
        """Test that parser returns proper ChordAnnotation objects."""
        parser = GroundTruthParser()
        content = "Test[D]lyrics[G]"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert all(isinstance(ann, ChordAnnotation) for ann in annotations)
        assert all(ann.timestamp == 0.0 for ann in annotations)  # Default timestamp
    
    def test_parse_positions_are_monotonically_increasing(self):
        """Test that positions are monotonically increasing."""
        parser = GroundTruthParser()
        content = "a[D]b[G]c[Am]d[C]e[F]"
        
        annotations = parser.parse_lyrics_with_chords(content)
        
        assert len(annotations) == 5
        # Verify monotonic increase
        for i in range(len(annotations) - 1):
            assert annotations[i].position < annotations[i + 1].position



class TestLyricsOnlyParsing:
    """Test lyrics-only format parsing functionality."""
    
    def test_parse_simple_lyrics_only(self):
        """Test parsing simple lyrics without any chords."""
        parser = GroundTruthParser()
        content = "This is just plain text without any chords"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_japanese_lyrics_only(self):
        """Test parsing Japanese lyrics without chords."""
        parser = GroundTruthParser()
        content = "涙があふれる心の中で"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_multiline_lyrics_only(self):
        """Test parsing multi-line lyrics without chords."""
        parser = GroundTruthParser()
        content = "First line of lyrics\nSecond line of lyrics\nThird line of lyrics"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_lyrics_with_special_characters(self):
        """Test parsing lyrics with special characters but no chords."""
        parser = GroundTruthParser()
        content = "Hello! How are you? I'm fine, thanks. 100% good!"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_lyrics_with_numbers(self):
        """Test parsing lyrics with numbers but no chords."""
        parser = GroundTruthParser()
        content = "One 1, Two 2, Three 3, Four 4"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_lyrics_with_unicode_emoji(self):
        """Test parsing lyrics with Unicode emoji but no chords."""
        parser = GroundTruthParser()
        content = "Happy song 🎵🎶 with emoji 😊"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_lyrics_with_punctuation(self):
        """Test parsing lyrics with various punctuation but no chords."""
        parser = GroundTruthParser()
        content = "Hello, world! How are you? I'm fine... Really? Yes!"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_long_lyrics_only(self):
        """Test parsing long lyrics without chords."""
        parser = GroundTruthParser()
        content = "This is a very long line of lyrics " * 10
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_lyrics_with_whitespace_variations(self):
        """Test parsing lyrics with various whitespace patterns."""
        parser = GroundTruthParser()
        content = "Line with    multiple   spaces\n\nAnd empty lines\t\tand tabs"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_lyrics_only_auto_detection(self):
        """Test that lyrics-only format is correctly auto-detected and returns empty list."""
        parser = GroundTruthParser()
        content = "Just plain lyrics without any brackets"
        
        # Auto-detect format
        annotations = parser.parse(content)
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_mixed_language_lyrics_only(self):
        """Test parsing mixed language lyrics without chords."""
        parser = GroundTruthParser()
        content = "English text 日本語 中文 한글 mixed together"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert isinstance(annotations, list)
        assert len(annotations) == 0
    
    def test_parse_lyrics_only_validates_requirement_1_3(self):
        """Test that lyrics-only format returns empty list as per Requirement 1.3."""
        parser = GroundTruthParser()
        
        # Various lyrics-only content
        test_cases = [
            "Simple lyrics",
            "涙があふれる",
            "Multi\nline\nlyrics",
            "Lyrics with punctuation!",
            "Numbers 123 and symbols @#$"
        ]
        
        for content in test_cases:
            annotations = parser.parse(content, format_type='lyrics_only')
            assert isinstance(annotations, list), f"Failed for content: {content}"
            assert len(annotations) == 0, f"Expected empty list for content: {content}"


class TestMainParseMethod:
    """Test the main parse method that dispatches to format-specific parsers."""
    
    def test_parse_with_explicit_chord_only_format(self):
        """Test parse method with explicit chord_only format."""
        parser = GroundTruthParser()
        content = "[D][AonC#][Bm7]"
        
        annotations = parser.parse(content, format_type='chord_only')
        
        assert len(annotations) == 3
        assert annotations[0].chord == "D"
        assert annotations[0].position == 0
        assert annotations[1].chord == "AonC#"
        assert annotations[1].position == 1
        assert annotations[2].chord == "Bm7"
        assert annotations[2].position == 2
    
    def test_parse_with_explicit_lyrics_with_chords_format(self):
        """Test parse method with explicit lyrics_with_chords format."""
        parser = GroundTruthParser()
        content = "涙[D]があふれ[AonC#]る"
        
        annotations = parser.parse(content, format_type='lyrics_with_chords')
        
        assert len(annotations) == 2
        assert annotations[0].chord == "D"
        assert annotations[0].position == 1
        assert annotations[1].chord == "AonC#"
        assert annotations[1].position == 8
    
    def test_parse_with_explicit_lyrics_only_format(self):
        """Test parse method with explicit lyrics_only format."""
        parser = GroundTruthParser()
        content = "This is just plain text"
        
        annotations = parser.parse(content, format_type='lyrics_only')
        
        assert len(annotations) == 0
    
    def test_parse_with_auto_detection_chord_only(self):
        """Test parse method with auto-detection for chord_only format."""
        parser = GroundTruthParser()
        content = "[D][AonC#][Bm7]"
        
        # No format_type specified, should auto-detect
        annotations = parser.parse(content)
        
        assert len(annotations) == 3
        assert annotations[0].chord == "D"
        assert annotations[1].chord == "AonC#"
        assert annotations[2].chord == "Bm7"
    
    def test_parse_with_auto_detection_lyrics_with_chords(self):
        """Test parse method with auto-detection for lyrics_with_chords format."""
        parser = GroundTruthParser()
        content = "涙[D]があふれ[AonC#]る"
        
        # No format_type specified, should auto-detect
        annotations = parser.parse(content)
        
        assert len(annotations) == 2
        assert annotations[0].chord == "D"
        assert annotations[1].chord == "AonC#"
    
    def test_parse_with_auto_detection_lyrics_only(self):
        """Test parse method with auto-detection for lyrics_only format."""
        parser = GroundTruthParser()
        content = "This is just plain text"
        
        # No format_type specified, should auto-detect
        annotations = parser.parse(content)
        
        assert len(annotations) == 0
    
    def test_parse_with_invalid_format_type(self):
        """Test parse method with invalid format type."""
        parser = GroundTruthParser()
        content = "[D][G]"
        
        with pytest.raises(ValueError, match="Unrecognized format type"):
            parser.parse(content, format_type='invalid_format')
    
    def test_parse_with_empty_content(self):
        """Test parse method with empty content."""
        parser = GroundTruthParser()
        
        with pytest.raises(ValueError, match="content must be a non-empty string"):
            parser.parse("")
    
    def test_parse_with_none_content(self):
        """Test parse method with None content."""
        parser = GroundTruthParser()
        
        with pytest.raises(ValueError, match="content must be a non-empty string"):
            parser.parse(None)
    
    def test_parse_returns_chord_annotation_objects(self):
        """Test that parse method returns proper ChordAnnotation objects."""
        parser = GroundTruthParser()
        
        # Test with chord_only
        annotations = parser.parse("[D][G]")
        assert all(isinstance(ann, ChordAnnotation) for ann in annotations)
        
        # Test with lyrics_with_chords
        annotations = parser.parse("Test[D]lyrics[G]")
        assert all(isinstance(ann, ChordAnnotation) for ann in annotations)
        
        # Test with lyrics_only
        annotations = parser.parse("Just text")
        assert isinstance(annotations, list)
        assert len(annotations) == 0



class TestErrorHandlingForInvalidFormats:
    """Test error handling for invalid formats (Requirements 11.1, 11.2, 11.3)."""
    
    def test_unrecognized_format_type_raises_descriptive_error(self):
        """Test that unrecognized format type raises ValueError with descriptive message.
        
        Validates: Requirement 11.1
        """
        parser = GroundTruthParser()
        content = "[D][G]"
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse(content, format_type='unknown_format')
        
        error_message = str(exc_info.value)
        # Check that error message is descriptive
        assert "Unrecognized format type" in error_message
        assert "unknown_format" in error_message
        assert "Expected" in error_message
    
    def test_unrecognized_format_provides_hints(self):
        """Test that unrecognized format error provides format detection hints.
        
        Validates: Requirement 11.3
        """
        parser = GroundTruthParser()
        content = "[D][G]"
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse(content, format_type='invalid')
        
        error_message = str(exc_info.value)
        # Check that error message provides hints
        assert "Hint:" in error_message
        assert "chord_only" in error_message
        assert "lyrics_with_chords" in error_message
        assert "lyrics_only" in error_message
    
    def test_empty_chord_only_format_raises_error(self):
        """Test that chord-only format with no chords raises ValueError.
        
        Validates: Requirement 11.2
        """
        parser = GroundTruthParser()
        content = "[][][]"  # Only empty brackets
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_chord_only_format(content)
        
        error_message = str(exc_info.value)
        assert "No chords found" in error_message
        assert "chord-only format" in error_message
    
    def test_empty_chord_only_format_provides_hints(self):
        """Test that empty chord-only format error provides format hints.
        
        Validates: Requirement 11.3
        """
        parser = GroundTruthParser()
        content = "[][][]"
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_chord_only_format(content)
        
        error_message = str(exc_info.value)
        # Check that error message provides format hints
        assert "Hint:" in error_message
        assert "Expected format:" in error_message
        assert "[D][AonC#][Bm7]" in error_message
        assert "brackets" in error_message
    
    def test_empty_lyrics_with_chords_format_raises_error(self):
        """Test that lyrics-with-chords format with no chords raises ValueError.
        
        Validates: Requirement 11.2
        """
        parser = GroundTruthParser()
        content = "Hello[]world[]"  # Only empty brackets
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_lyrics_with_chords(content)
        
        error_message = str(exc_info.value)
        assert "No chords found" in error_message
        assert "lyrics-with-chords format" in error_message
    
    def test_empty_lyrics_with_chords_format_provides_hints(self):
        """Test that empty lyrics-with-chords format error provides format hints.
        
        Validates: Requirement 11.3
        """
        parser = GroundTruthParser()
        content = "Hello[]world[]"
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_lyrics_with_chords(content)
        
        error_message = str(exc_info.value)
        # Check that error message provides format hints
        assert "Hint:" in error_message
        assert "Expected format:" in error_message
        assert "lyrics[D]with[G]chords" in error_message
        assert "brackets" in error_message
    
    def test_chord_only_with_no_brackets_raises_error(self):
        """Test that chord-only format with no brackets raises ValueError.
        
        Validates: Requirement 11.2
        """
        parser = GroundTruthParser()
        content = "D G Am C"  # No brackets
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_chord_only_format(content)
        
        error_message = str(exc_info.value)
        assert "No chords found" in error_message
    
    def test_lyrics_with_chords_no_brackets_raises_error(self):
        """Test that lyrics-with-chords format with no brackets raises ValueError.
        
        Validates: Requirement 11.2
        """
        parser = GroundTruthParser()
        content = "Hello world with no chords"
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_lyrics_with_chords(content)
        
        error_message = str(exc_info.value)
        assert "No chords found" in error_message
    
    def test_error_message_is_actionable_for_chord_only(self):
        """Test that error messages are actionable and help users fix issues.
        
        Validates: Requirements 11.1, 11.3
        """
        parser = GroundTruthParser()
        content = "[][]"
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_chord_only_format(content)
        
        error_message = str(exc_info.value)
        # Error message should be actionable
        assert "No chords found" in error_message
        assert "Expected format:" in error_message
        assert "Hint:" in error_message
        # Should tell user what to do
        assert "enclosed in brackets" in error_message
        assert "not empty" in error_message
    
    def test_error_message_is_actionable_for_lyrics_with_chords(self):
        """Test that error messages are actionable for lyrics-with-chords format.
        
        Validates: Requirements 11.1, 11.3
        """
        parser = GroundTruthParser()
        content = "lyrics[]with[]empty[]brackets"
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_lyrics_with_chords(content)
        
        error_message = str(exc_info.value)
        # Error message should be actionable
        assert "No chords found" in error_message
        assert "Expected format:" in error_message
        assert "Hint:" in error_message
        # Should tell user what to do
        assert "enclosed in brackets" in error_message
        assert "not empty" in error_message
    
    def test_error_message_includes_format_examples(self):
        """Test that error messages include format examples.
        
        Validates: Requirement 11.3
        """
        parser = GroundTruthParser()
        
        # Test chord-only format
        with pytest.raises(ValueError) as exc_info:
            parser.parse_chord_only_format("[]")
        assert "[D][AonC#][Bm7]" in str(exc_info.value)
        
        # Test lyrics-with-chords format
        with pytest.raises(ValueError) as exc_info:
            parser.parse_lyrics_with_chords("text[]")
        assert "lyrics[D]with[G]chords" in str(exc_info.value)
        
        # Test unrecognized format
        with pytest.raises(ValueError) as exc_info:
            parser.parse("[D]", format_type='bad_format')
        error_message = str(exc_info.value)
        assert "[D][G][Am]" in error_message
        assert "text[D]with[G]chords" in error_message
    
    def test_multiple_format_hints_in_unrecognized_format_error(self):
        """Test that unrecognized format error includes hints for all valid formats.
        
        Validates: Requirement 11.3
        """
        parser = GroundTruthParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse("[D]", format_type='wrong')
        
        error_message = str(exc_info.value)
        # Should mention all three valid formats
        assert "chord_only" in error_message
        assert "lyrics_with_chords" in error_message
        assert "lyrics_only" in error_message
        # Should provide examples
        assert "[D][G][Am]" in error_message
        assert "text[D]with[G]chords" in error_message
        assert "plain text" in error_message
