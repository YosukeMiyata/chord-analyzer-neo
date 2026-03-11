"""ChordAI Output Mapper

This module provides mapping functionality to convert ChordAI model predictions
to the application's ChordSegment format.
"""

from typing import Dict
from src.chordai_models import ChordPrediction
from src.models import ChordSegment, ChordQuality


class ChordAIOutputMapper:
    """Maps ChordAI model predictions to ChordSegment format
    
    This class provides static methods to convert raw ChordAI predictions
    (ChordPrediction objects) into the application's standard ChordSegment
    format, including quality string mapping and error handling.
    """
    
    # Quality mapping table: ChordAI output strings -> ChordQuality enum
    QUALITY_MAP: Dict[str, ChordQuality] = {
        # Special cases
        "N.C.": ChordQuality.MAJOR,  # No chord - map to major as placeholder
        
        # Major variants
        "maj": ChordQuality.MAJOR,
        "M": ChordQuality.MAJOR,
        "": ChordQuality.MAJOR,  # Empty string defaults to major
        
        # Minor variants
        "min": ChordQuality.MINOR,
        "m": ChordQuality.MINOR,
        
        # Diminished variants
        "dim": ChordQuality.DIMINISHED,
        "dim7": ChordQuality.DIMINISHED,
        "o": ChordQuality.DIMINISHED,
        "°": ChordQuality.DIMINISHED,
        
        # Augmented variants
        "aug": ChordQuality.AUGMENTED,
        "aug7": ChordQuality.DOMINANT7,
        "augM7": ChordQuality.MAJOR7,
        "+": ChordQuality.AUGMENTED,
        
        # Power chords
        "5": ChordQuality.MAJOR,  # Power chord - map to major
        
        # Seventh chords
        "7": ChordQuality.DOMINANT7,
        "7-5": ChordQuality.DOMINANT7,
        "dom7": ChordQuality.DOMINANT7,
        
        # Major seventh variants
        "maj7": ChordQuality.MAJOR7,
        "M7": ChordQuality.MAJOR7,
        "M7-5": ChordQuality.MAJOR7,
        "Δ7": ChordQuality.MAJOR7,
        
        # Minor seventh variants
        "min7": ChordQuality.MINOR7,
        "m7": ChordQuality.MINOR7,
        "m7-5": ChordQuality.MINOR7,
        "mM7": ChordQuality.MINOR7,
        
        # Sixth chords
        "6": ChordQuality.MAJOR,  # Map 6th to major
        "m6": ChordQuality.MINOR,
        "69": ChordQuality.MAJOR,
        "m69": ChordQuality.MINOR,
        
        # Suspended chords
        "sus4": ChordQuality.SUS4,
        "sus2": ChordQuality.SUS2,
        "7sus4": ChordQuality.SUS4,
        
        # Add chords
        "add9": ChordQuality.MAJOR,
        "madd9": ChordQuality.MINOR,
        
        # Extended chords - map to closest simple quality
        "9": ChordQuality.NINTH,
        "11": ChordQuality.ELEVENTH,
        "13": ChordQuality.THIRTEENTH,
        
        # Complex seventh chords with extensions - map to base seventh
        "7(b9)": ChordQuality.DOMINANT7,
        "7(#9)": ChordQuality.DOMINANT7,
        "7(b13)": ChordQuality.DOMINANT7,
        "7(9)": ChordQuality.DOMINANT7,
        "7(13)": ChordQuality.DOMINANT7,
        "7(b9,b13)": ChordQuality.DOMINANT7,
        "7(b9,13)": ChordQuality.DOMINANT7,
        "7(#9,b13)": ChordQuality.DOMINANT7,
        "7(9,13)": ChordQuality.DOMINANT7,
        "7(#9,13)": ChordQuality.DOMINANT7,
        "7(9,#11,13)": ChordQuality.DOMINANT7,
        
        # Extended major seventh chords
        "M7(9)": ChordQuality.MAJOR7,
        "M7(13)": ChordQuality.MAJOR7,
        "M7(9,13)": ChordQuality.MAJOR7,
        
        # Extended minor seventh chords
        "m7(9)": ChordQuality.MINOR7,
        "m7(11)": ChordQuality.MINOR7,
        "m7(13)": ChordQuality.MINOR7,
        "m7(9,11)": ChordQuality.MINOR7,
        "m7(9,13)": ChordQuality.MINOR7,
        
        # Extended minor major seventh
        "mM7(9)": ChordQuality.MINOR7,
        "mM7(13)": ChordQuality.MINOR7,
    }
    
    @staticmethod
    def map_quality_string(quality: str) -> ChordQuality:
        """Map ChordAI quality string to ChordQuality enum
        
        Converts a quality string from ChordAI model output to the corresponding
        ChordQuality enum value. Supports various notation styles (e.g., "maj"/"M",
        "min"/"m", "dim"/"o").
        
        Args:
            quality: Quality string from ChordAI (e.g., "maj", "min", "7", "maj7")
            
        Returns:
            Corresponding ChordQuality enum value
            
        Raises:
            ValueError: If quality string cannot be mapped to ChordQuality enum
            
        Examples:
            >>> ChordAIOutputMapper.map_quality_string("maj")
            ChordQuality.MAJOR
            >>> ChordAIOutputMapper.map_quality_string("m")
            ChordQuality.MINOR
            >>> ChordAIOutputMapper.map_quality_string("7")
            ChordQuality.DOMINANT7
        """
        if quality not in ChordAIOutputMapper.QUALITY_MAP:
            raise ValueError(
                f"Unknown chord quality from ChordAI: '{quality}'. "
                f"Cannot map to ChordQuality enum. "
                f"Supported qualities: {', '.join(ChordAIOutputMapper.QUALITY_MAP.keys())}"
            )
        
        return ChordAIOutputMapper.QUALITY_MAP[quality]
    
    @staticmethod
    def map_to_chord_segment(prediction: ChordPrediction) -> ChordSegment:
        """Convert ChordPrediction to ChordSegment
        
        Transforms a raw ChordAI prediction into the application's standard
        ChordSegment format, mapping quality strings to enum values and
        preserving all timing and chord information.
        
        Args:
            prediction: Raw ChordAI prediction with timing, root, quality, bass_note, confidence
            
        Returns:
            ChordSegment with mapped ChordQuality enum and all prediction data
            
        Raises:
            ValueError: If quality string cannot be mapped to ChordQuality enum
            
        Examples:
            >>> pred = ChordPrediction(0.0, 2.0, "C", "maj", None, 0.95)
            >>> segment = ChordAIOutputMapper.map_to_chord_segment(pred)
            >>> segment.root
            'C'
            >>> segment.quality
            ChordQuality.MAJOR
        """
        # Map quality string to enum
        quality_enum = ChordAIOutputMapper.map_quality_string(prediction.quality)
        
        # Create ChordSegment with mapped quality
        return ChordSegment(
            start_time=prediction.start_time,
            end_time=prediction.end_time,
            root=prediction.root,
            quality=quality_enum,
            bass_note=prediction.bass_note,
            extensions=[],  # Extensions not currently extracted from ChordAI
            confidence=prediction.confidence
        )

