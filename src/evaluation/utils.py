"""Utility functions for chord analysis in the evaluation system.

This module provides helper functions for extracting and analyzing chord components:
- Root note extraction from various chord formats
- Chord quality identification

Validates: Requirements 3.1, 3.2, 3.3, 3.4
"""

import re


def extract_root(chord: str) -> str:
    """Extract the root note from a chord name.
    
    This function handles multiple chord formats:
    1. Simple chords: "D", "Am" → "D", "A"
    2. Slash chords: "AonC#", "D/F#" → "A", "D"
    3. Chords with quality suffixes: "Bm7", "Cmaj7", "F#m7b5" → "B", "C", "F#"
    4. Accidentals: Preserves sharp (#) and flat (b) in root notes
    
    Args:
        chord: Chord name string (e.g., "D", "AonC#", "Bm7", "Cmaj7")
        
    Returns:
        Root note string with accidentals preserved (e.g., "D", "A", "B", "C", "F#", "Bb")
        
    Raises:
        ValueError: If chord is empty or invalid
        
    Examples:
        >>> extract_root("D")
        "D"
        >>> extract_root("Am")
        "A"
        >>> extract_root("AonC#")
        "A"
        >>> extract_root("Bm7")
        "B"
        >>> extract_root("Cmaj7")
        "C"
        >>> extract_root("F#m7b5")
        "F#"
        >>> extract_root("Bb9")
        "Bb"
        >>> extract_root("D/F#")
        "D"
        
    Validates: Requirements 3.1, 3.2, 3.3, 3.4
    """
    if not chord or not isinstance(chord, str):
        raise ValueError("chord must be a non-empty string")
    
    chord = chord.strip()
    if not chord:
        raise ValueError("chord cannot be empty after stripping whitespace")
    
    # Handle slash chords (e.g., "AonC#" or "D/F#")
    # Extract the part before "on" or "/"
    if "on" in chord:
        chord = chord.split("on")[0]
    elif "/" in chord:
        chord = chord.split("/")[0]
    
    # Now extract the root note from the remaining chord
    # Root note pattern: A note letter (A-G) optionally followed by # or b
    # This should be at the start of the string
    root_pattern = r'^([A-G][#b]?)'
    match = re.match(root_pattern, chord)
    
    if not match:
        raise ValueError(f"Could not extract root note from chord: '{chord}'")
    
    root = match.group(1)
    return root
