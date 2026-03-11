#!/usr/bin/env python3
"""Test JSON output format from backend"""

import json
from src.models import ChordSegment, ChordQuality

# Create test chord segments with various qualities
test_chords = [
    ChordSegment(0.0, 2.0, "C", ChordQuality.MAJOR, confidence=0.95),
    ChordSegment(2.0, 4.0, "F", ChordQuality.MAJOR, confidence=0.92),
    ChordSegment(4.0, 6.0, "G", ChordQuality.DOMINANT7, confidence=0.88),
    ChordSegment(6.0, 8.0, "Am", ChordQuality.MINOR, confidence=0.90),
    ChordSegment(8.0, 10.0, "Dm", ChordQuality.MINOR7, confidence=0.85),
    ChordSegment(10.0, 12.0, "Cmaj7", ChordQuality.MAJOR7, confidence=0.87),
]

# Convert to JSON format (as done in main.rs)
output = {
    'chord_progression': [
        {
            'start_time': c.start_time,
            'end_time': c.end_time,
            'root': c.root,
            'quality': c.quality.value,  # This is the key line
            'bass_note': c.bass_note,
            'extensions': c.extensions,
            'confidence': c.confidence
        } for c in test_chords
    ]
}

print("JSON Output:")
print(json.dumps(output, indent=2, ensure_ascii=False))

print("\n\nQuality values:")
for c in test_chords:
    print(f"{c.root}: quality={c.quality}, quality.value={c.quality.value}")
