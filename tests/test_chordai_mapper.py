"""Unit tests for ChordAI Output Mapper

Tests the mapping functionality from ChordAI predictions to ChordSegment format.
"""

import pytest
from src.chordai_mapper import ChordAIOutputMapper
from src.chordai_models import ChordPrediction
from src.models import ChordSegment, ChordQuality


class TestMapQualityString:
    """Tests for map_quality_string method"""
    
    def test_major_variants(self):
        """Test mapping of major chord quality variants"""
        assert ChordAIOutputMapper.map_quality_string("maj") == ChordQuality.MAJOR
        assert ChordAIOutputMapper.map_quality_string("M") == ChordQuality.MAJOR
        assert ChordAIOutputMapper.map_quality_string("") == ChordQuality.MAJOR
    
    def test_minor_variants(self):
        """Test mapping of minor chord quality variants"""
        assert ChordAIOutputMapper.map_quality_string("min") == ChordQuality.MINOR
        assert ChordAIOutputMapper.map_quality_string("m") == ChordQuality.MINOR
    
    def test_diminished_variants(self):
        """Test mapping of diminished chord quality variants"""
        assert ChordAIOutputMapper.map_quality_string("dim") == ChordQuality.DIMINISHED
        assert ChordAIOutputMapper.map_quality_string("o") == ChordQuality.DIMINISHED
        assert ChordAIOutputMapper.map_quality_string("°") == ChordQuality.DIMINISHED
    
    def test_augmented_variants(self):
        """Test mapping of augmented chord quality variants"""
        assert ChordAIOutputMapper.map_quality_string("aug") == ChordQuality.AUGMENTED
        assert ChordAIOutputMapper.map_quality_string("+") == ChordQuality.AUGMENTED
    
    def test_dominant7_variants(self):
        """Test mapping of dominant 7th chord quality variants"""
        assert ChordAIOutputMapper.map_quality_string("7") == ChordQuality.DOMINANT7
        assert ChordAIOutputMapper.map_quality_string("dom7") == ChordQuality.DOMINANT7
    
    def test_major7_variants(self):
        """Test mapping of major 7th chord quality variants"""
        assert ChordAIOutputMapper.map_quality_string("maj7") == ChordQuality.MAJOR7
        assert ChordAIOutputMapper.map_quality_string("M7") == ChordQuality.MAJOR7
        assert ChordAIOutputMapper.map_quality_string("Δ7") == ChordQuality.MAJOR7
    
    def test_minor7_variants(self):
        """Test mapping of minor 7th chord quality variants"""
        assert ChordAIOutputMapper.map_quality_string("min7") == ChordQuality.MINOR7
        assert ChordAIOutputMapper.map_quality_string("m7") == ChordQuality.MINOR7
    
    def test_suspended_chords(self):
        """Test mapping of suspended chord qualities"""
        assert ChordAIOutputMapper.map_quality_string("sus4") == ChordQuality.SUS4
        assert ChordAIOutputMapper.map_quality_string("sus2") == ChordQuality.SUS2
    
    def test_extended_chords(self):
        """Test mapping of extended chord qualities"""
        assert ChordAIOutputMapper.map_quality_string("9") == ChordQuality.NINTH
        assert ChordAIOutputMapper.map_quality_string("11") == ChordQuality.ELEVENTH
        assert ChordAIOutputMapper.map_quality_string("13") == ChordQuality.THIRTEENTH
    
    def test_unknown_quality_raises_error(self):
        """Test that unknown quality strings raise ValueError"""
        with pytest.raises(ValueError) as exc_info:
            ChordAIOutputMapper.map_quality_string("unknown")
        
        error_msg = str(exc_info.value)
        assert "Unknown chord quality from ChordAI: 'unknown'" in error_msg
        assert "Cannot map to ChordQuality enum" in error_msg
        assert "Supported qualities:" in error_msg
    
    def test_error_message_includes_supported_qualities(self):
        """Test that error message lists supported quality strings"""
        with pytest.raises(ValueError) as exc_info:
            ChordAIOutputMapper.map_quality_string("invalid")
        
        error_msg = str(exc_info.value)
        # Check that some known qualities are mentioned
        assert "maj" in error_msg or "min" in error_msg


class TestMapToChordSegment:
    """Tests for map_to_chord_segment method"""
    
    def test_basic_major_chord(self):
        """Test mapping of basic major chord prediction"""
        prediction = ChordPrediction(
            start_time=0.0,
            end_time=2.0,
            root="C",
            quality="maj",
            bass_note=None,
            confidence=0.95
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert isinstance(segment, ChordSegment)
        assert segment.start_time == 0.0
        assert segment.end_time == 2.0
        assert segment.root == "C"
        assert segment.quality == ChordQuality.MAJOR
        assert segment.bass_note is None
        assert segment.confidence == 0.95
        assert segment.extensions == []
    
    def test_minor_chord_with_bass_note(self):
        """Test mapping of minor chord with bass note (slash chord)"""
        prediction = ChordPrediction(
            start_time=2.0,
            end_time=4.0,
            root="A",
            quality="min",
            bass_note="C",
            confidence=0.88
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "A"
        assert segment.quality == ChordQuality.MINOR
        assert segment.bass_note == "C"
        assert segment.confidence == 0.88
    
    def test_dominant7_chord(self):
        """Test mapping of dominant 7th chord"""
        prediction = ChordPrediction(
            start_time=4.0,
            end_time=6.0,
            root="G",
            quality="7",
            bass_note=None,
            confidence=0.92
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "G"
        assert segment.quality == ChordQuality.DOMINANT7
    
    def test_major7_chord(self):
        """Test mapping of major 7th chord"""
        prediction = ChordPrediction(
            start_time=6.0,
            end_time=8.0,
            root="F",
            quality="maj7",
            bass_note=None,
            confidence=0.90
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "F"
        assert segment.quality == ChordQuality.MAJOR7
    
    def test_diminished_chord(self):
        """Test mapping of diminished chord"""
        prediction = ChordPrediction(
            start_time=8.0,
            end_time=10.0,
            root="B",
            quality="dim",
            bass_note=None,
            confidence=0.85
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "B"
        assert segment.quality == ChordQuality.DIMINISHED
    
    def test_augmented_chord(self):
        """Test mapping of augmented chord"""
        prediction = ChordPrediction(
            start_time=10.0,
            end_time=12.0,
            root="C",
            quality="aug",
            bass_note=None,
            confidence=0.87
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "C"
        assert segment.quality == ChordQuality.AUGMENTED
    
    def test_sus4_chord(self):
        """Test mapping of sus4 chord"""
        prediction = ChordPrediction(
            start_time=12.0,
            end_time=14.0,
            root="D",
            quality="sus4",
            bass_note=None,
            confidence=0.91
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "D"
        assert segment.quality == ChordQuality.SUS4
    
    def test_sus2_chord(self):
        """Test mapping of sus2 chord"""
        prediction = ChordPrediction(
            start_time=14.0,
            end_time=16.0,
            root="E",
            quality="sus2",
            bass_note=None,
            confidence=0.89
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "E"
        assert segment.quality == ChordQuality.SUS2
    
    def test_ninth_chord(self):
        """Test mapping of 9th chord"""
        prediction = ChordPrediction(
            start_time=16.0,
            end_time=18.0,
            root="A",
            quality="9",
            bass_note=None,
            confidence=0.86
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "A"
        assert segment.quality == ChordQuality.NINTH
    
    def test_eleventh_chord(self):
        """Test mapping of 11th chord"""
        prediction = ChordPrediction(
            start_time=18.0,
            end_time=20.0,
            root="F",
            quality="11",
            bass_note=None,
            confidence=0.84
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "F"
        assert segment.quality == ChordQuality.ELEVENTH
    
    def test_thirteenth_chord(self):
        """Test mapping of 13th chord"""
        prediction = ChordPrediction(
            start_time=20.0,
            end_time=22.0,
            root="G",
            quality="13",
            bass_note=None,
            confidence=0.83
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "G"
        assert segment.quality == ChordQuality.THIRTEENTH
    
    def test_sharp_root_note(self):
        """Test mapping with sharp root note"""
        prediction = ChordPrediction(
            start_time=0.0,
            end_time=2.0,
            root="C#",
            quality="min",
            bass_note=None,
            confidence=0.90
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "C#"
        assert segment.quality == ChordQuality.MINOR
    
    def test_flat_root_note(self):
        """Test mapping with flat root note"""
        prediction = ChordPrediction(
            start_time=0.0,
            end_time=2.0,
            root="Bb",
            quality="maj",
            bass_note=None,
            confidence=0.93
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.root == "Bb"
        assert segment.quality == ChordQuality.MAJOR
    
    def test_unknown_quality_raises_error(self):
        """Test that unknown quality in prediction raises ValueError"""
        prediction = ChordPrediction(
            start_time=0.0,
            end_time=2.0,
            root="C",
            quality="unknown_quality",
            bass_note=None,
            confidence=0.50
        )
        
        with pytest.raises(ValueError) as exc_info:
            ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert "Unknown chord quality from ChordAI: 'unknown_quality'" in str(exc_info.value)
    
    def test_zero_confidence(self):
        """Test mapping with zero confidence score"""
        prediction = ChordPrediction(
            start_time=0.0,
            end_time=2.0,
            root="C",
            quality="maj",
            bass_note=None,
            confidence=0.0
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.confidence == 0.0
    
    def test_high_confidence(self):
        """Test mapping with high confidence score"""
        prediction = ChordPrediction(
            start_time=0.0,
            end_time=2.0,
            root="C",
            quality="maj",
            bass_note=None,
            confidence=0.99
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        assert segment.confidence == 0.99
    
    def test_extensions_empty_list(self):
        """Test that extensions field is always an empty list"""
        prediction = ChordPrediction(
            start_time=0.0,
            end_time=2.0,
            root="C",
            quality="maj7",
            bass_note=None,
            confidence=0.90
        )
        
        segment = ChordAIOutputMapper.map_to_chord_segment(prediction)
        
        # Extensions are not currently extracted from ChordAI
        assert segment.extensions == []
        assert isinstance(segment.extensions, list)

