"""ChordAI Data Models

This module provides data models for ChordAI model predictions.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChordPrediction:
    """Raw prediction from ChordAI model
    
    Represents a chord prediction with timing information, chord components,
    and confidence score before mapping to the application's ChordSegment format.
    
    Attributes:
        start_time: Start time of the chord segment in seconds
        end_time: End time of the chord segment in seconds
        root: Root note of the chord (e.g., "C", "C#", "D")
        quality: Chord quality string from ChordAI (e.g., "maj", "min", "7", "maj7")
        bass_note: Optional bass note for chord inversions (slash chords)
        confidence: Prediction confidence score (0.0 to 1.0)
    """
    start_time: float
    end_time: float
    root: str
    quality: str
    bass_note: Optional[str] = None
    confidence: float = 0.0
