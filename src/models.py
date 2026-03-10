"""Core data models for chord analysis"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple
from datetime import datetime


class ChordQuality(Enum):
    """Chord quality types"""
    MAJOR = "maj"
    MINOR = "min"
    DOMINANT7 = "7"
    MAJOR7 = "maj7"
    MINOR7 = "min7"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    SUS4 = "sus4"
    SUS2 = "sus2"
    NINTH = "9"
    ELEVENTH = "11"
    THIRTEENTH = "13"


@dataclass
class ChordSegment:
    """Represents a chord segment with timing information"""
    start_time: float
    end_time: float
    root: str  # "C", "D", "E", etc.
    quality: ChordQuality
    bass_note: Optional[str] = None  # For slash chords
    extensions: List[str] = field(default_factory=list)  # 9th, 11th, 13th
    confidence: float = 0.0

    def __str__(self) -> str:
        chord_str = f"{self.root}{self.quality.value}"
        if self.extensions:
            chord_str += f"({','.join(self.extensions)})"
        if self.bass_note:
            chord_str += f"/{self.bass_note}"
        return chord_str


@dataclass
class LyricSegment:
    """Represents a lyric segment with timing information"""
    start_time: float
    end_time: float
    text: str
    confidence: float


@dataclass
class AudioAnalysisResult:
    """Complete audio analysis result"""
    chord_progression: List[ChordSegment]
    lyrics: List[LyricSegment]
    tempo: float
    key: str
    time_signature: Tuple[int, int]


@dataclass
class ChordCorrection:
    """User correction of a chord segment"""
    audio_file_hash: str
    segment_index: int
    original_chord: ChordSegment
    corrected_chord: ChordSegment
    timestamp: datetime
    user_id: Optional[str] = None


@dataclass
class ModelConfig:
    """Configuration for a chord estimation model"""
    model_id: str
    model_name: str
    model_path: str
    model_type: str  # "tensorflow", "onnx", "pytorch"
    description: str
    accuracy_metrics: dict = field(default_factory=dict)
    is_default: bool = False
