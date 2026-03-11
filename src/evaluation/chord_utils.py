"""Chord utility functions for the evaluation system.

This module provides helper functions for extracting and analyzing chord components:
- Root note extraction from various chord formats
- Chord quality identification

Validates: Requirements 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5
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


def identify_quality(chord: str) -> str:
    """Identify the quality of a chord.
    
    This function identifies chord qualities based on suffixes:
    1. Major: No suffix or explicit "maj" (but not "maj7")
    2. Minor: "m" or "min" suffix
    3. Seventh: "7" suffix (including minor seventh like "m7")
    4. Major seventh: "maj7" or "M7" suffix
    5. Suspended: "sus" suffix (sus2, sus4)
    6. Augmented: "aug" or "+" suffix
    7. Diminished: "dim" or "°" suffix
    
    Args:
        chord: Chord name string (e.g., "D", "Am", "D7", "Cmaj7")
        
    Returns:
        Quality string: "major", "minor", "seventh", "major_seventh", 
                       "minor_seventh", "suspended", "augmented", "diminished"
        
    Raises:
        ValueError: If chord is empty or invalid
        
    Examples:
        >>> identify_quality("D")
        "major"
        >>> identify_quality("Am")
        "minor"
        >>> identify_quality("D7")
        "seventh"
        >>> identify_quality("Cmaj7")
        "major_seventh"
        >>> identify_quality("Bm7")
        "minor_seventh"
        >>> identify_quality("F#m7b5")
        "minor_seventh"
        >>> identify_quality("Gsus4")
        "suspended"
        >>> identify_quality("Cadd9")
        "major"
        >>> identify_quality("Cdim")
        "diminished"
        >>> identify_quality("Caug")
        "augmented"
        
    Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
    """
    if not chord or not isinstance(chord, str):
        raise ValueError("chord must be a non-empty string")
    
    chord = chord.strip()
    if not chord:
        raise ValueError("chord cannot be empty after stripping whitespace")
    
    # Handle slash chords - only analyze the first part
    if "on" in chord:
        chord = chord.split("on")[0]
    elif "/" in chord:
        chord = chord.split("/")[0]
    
    # Extract the suffix after the root note
    # Root note pattern: A note letter (A-G) optionally followed by # or b
    root_pattern = r'^[A-G][#b]?'
    match = re.match(root_pattern, chord)
    
    if not match:
        raise ValueError(f"Could not extract root note from chord: '{chord}'")
    
    # Get the suffix (everything after the root note)
    suffix = chord[match.end():].strip()
    
    # Check for diminished first (before seventh, since dim7 contains "7")
    if "dim" in suffix.lower() or "°" in suffix:
        return "diminished"
    
    # Check for major seventh first (before minor seventh to avoid confusion)
    # Match "maj7", "Maj7", "MAJ7", "M7" (but not "m7")
    if re.search(r'^maj7', suffix, re.IGNORECASE) or re.search(r'^M7', suffix):
        return "major_seventh"
    
    # Check for minor seventh (m7, min7)
    if re.search(r'^m7|^min7', suffix, re.IGNORECASE):
        return "minor_seventh"
    
    # Check for seventh (must come after maj7, m7, and dim checks)
    if "7" in suffix:
        return "seventh"
    
    # Check for suspended
    if "sus" in suffix.lower():
        return "suspended"
    
    # Check for augmented
    if "aug" in suffix.lower() or "+" in suffix:
        return "augmented"
    
    # Check for minor (m, min)
    if re.search(r'^m(?![a-z])|^min', suffix, re.IGNORECASE):
        return "minor"
    
    # Check for explicit major
    if "maj" in suffix.lower():
        return "major"
    
    # Default to major if no quality suffix
    return "major"
