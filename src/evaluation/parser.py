"""Ground truth parser for chord recognition evaluation.

This module provides parsing functionality for three ground truth formats:
1. chord-only: Contains only bracketed chords (e.g., [D][AonC#][Bm7])
2. lyrics-with-chords: Contains text with embedded bracketed chords (e.g., 涙[D]があふれ[AonC#]る)
3. lyrics-only: Contains text with no bracketed chords

Validates: Requirements 1.1, 1.2, 1.3, 1.4, 9.1, 9.2, 9.3, 9.4
"""

import re
from typing import List
from src.evaluation.models import ChordAnnotation


class GroundTruthParser:
    """Parser for ground truth chord annotations in multiple formats."""
    
    def detect_format(self, content: str) -> str:
        """Automatically detect the format type of ground truth content.
        
        Args:
            content: The ground truth content string
            
        Returns:
            Format type: 'chord_only', 'lyrics_with_chords', or 'lyrics_only'
            
        Format detection rules:
        - chord_only: Contains only bracketed chords with no other text
        - lyrics_with_chords: Contains text with embedded bracketed chords
        - lyrics_only: Contains text with no bracketed chords
        
        Validates: Requirements 9.1, 9.2, 9.3, 9.4
        """
        if not content or not isinstance(content, str):
            raise ValueError("content must be a non-empty string")
        
        # Strip whitespace for analysis
        stripped_content = content.strip()
        
        if not stripped_content:
            raise ValueError("content cannot be empty after stripping whitespace")
        
        # Find all bracketed chords
        chord_pattern = r'\[([^\]]*)\]'
        matches = list(re.finditer(chord_pattern, stripped_content))
        
        # Check if there are any brackets
        has_brackets = len(matches) > 0
        
        if not has_brackets:
            # No brackets found -> lyrics-only format
            return 'lyrics_only'
        
        # Remove all bracketed content to see what remains
        content_without_brackets = re.sub(chord_pattern, '', stripped_content)
        # Remove whitespace to check if there's any other text
        remaining_text = content_without_brackets.strip()
        
        if not remaining_text:
            # Only brackets, no other text -> chord-only format
            return 'chord_only'
        else:
            # Has both brackets and other text -> lyrics-with-chords format
            return 'lyrics_with_chords'
    def parse(self, content: str, format_type: str = None) -> List[ChordAnnotation]:
        """Parse ground truth from various formats.

        Args:
            content: The ground truth content string
            format_type: Format type ('chord_only', 'lyrics_with_chords', 'lyrics_only')
                        If None, format will be auto-detected

        Returns:
            List of ChordAnnotation objects

        Raises:
            ValueError: If content is invalid or format is unrecognized

        This is the main entry point for parsing ground truth data. It dispatches
        to the appropriate format-specific parser based on the format_type.

        Validates: Requirements 1.1, 1.2, 1.3, 1.4, 11.1, 11.3
        """
        if not content or not isinstance(content, str):
            raise ValueError("content must be a non-empty string")

        # Auto-detect format if not specified
        if format_type is None:
            format_type = self.detect_format(content)

        # Dispatch to appropriate parser
        if format_type == 'chord_only':
            return self.parse_chord_only_format(content)
        elif format_type == 'lyrics_with_chords':
            return self.parse_lyrics_with_chords(content)
        elif format_type == 'lyrics_only':
            return self.parse_lyrics_only_format(content)
        else:
            raise ValueError(
                f"Unrecognized format type: '{format_type}'. "
                f"Expected 'chord_only', 'lyrics_with_chords', or 'lyrics_only'. "
                f"Hint: Use chord_only for [D][G][Am] format, "
                f"lyrics_with_chords for text[D]with[G]chords format, "
                f"or lyrics_only for plain text without chords."
            )

    
    def parse_chord_only_format(self, content: str) -> List[ChordAnnotation]:
        """Parse chord-only format: [D][AonC#][Bm7]
        
        Args:
            content: Ground truth content in chord-only format
            
        Returns:
            List of ChordAnnotation objects with sequential positions
            
        Raises:
            ValueError: If content is empty or no chords are found
            
        The parser:
        - Uses regex to find all bracketed chords
        - Extracts chord names from brackets
        - Assigns sequential positions starting from 0
        - Ignores empty brackets
        
        Validates: Requirements 1.1, 1.5, 11.2
        """
        if not content or not isinstance(content, str):
            raise ValueError("content must be a non-empty string")
        
        annotations = []
        position = 0
        
        # Pattern to find all bracketed content
        chord_pattern = r'\[([^\]]*)\]'
        matches = re.finditer(chord_pattern, content)
        
        for match in matches:
            chord = match.group(1).strip()
            # Ignore empty brackets
            if chord:
                annotations.append(ChordAnnotation(
                    chord=chord,
                    position=position
                ))
                position += 1
        
        # Check if no chords were found
        if not annotations:
            raise ValueError(
                "No chords found in chord-only format. "
                "Expected format: [D][AonC#][Bm7]. "
                "Hint: Ensure chords are enclosed in brackets [chord_name] and brackets are not empty."
            )
        
        return annotations

    def parse_lyrics_with_chords(self, content: str) -> List[ChordAnnotation]:
        """Parse lyrics-with-chords format: 涙[D]があふれ[AonC#]る

        Args:
            content: Ground truth content in lyrics-with-chords format

        Returns:
            List of ChordAnnotation objects with character positions

        Raises:
            ValueError: If content is empty or no chords are found

        The parser:
        - Uses regex to find all bracketed chords
        - Extracts chord names from brackets
        - Assigns positions based on character index where the bracket appears
        - Ignores empty brackets

        Example:
            Input: "涙[D]があふれ[AonC#]る"
            Output: [
                ChordAnnotation(chord="D", position=1),      # position is index of '['
                ChordAnnotation(chord="AonC#", position=7)   # position is index of '['
            ]

        Validates: Requirements 1.2, 1.5, 11.2
        """
        if not content or not isinstance(content, str):
            raise ValueError("content must be a non-empty string")

        annotations = []

        # Pattern to find all bracketed content
        chord_pattern = r'\[([^\]]*)\]'
        matches = re.finditer(chord_pattern, content)

        for match in matches:
            chord = match.group(1).strip()
            # Ignore empty brackets
            if chord:
                # Position is the character index where the bracket starts
                char_position = match.start()
                annotations.append(ChordAnnotation(
                    chord=chord,
                    position=char_position
                ))

        # Check if no chords were found
        if not annotations:
            raise ValueError(
                "No chords found in lyrics-with-chords format. "
                "Expected format: lyrics[D]with[G]chords. "
                "Hint: Ensure chords are enclosed in brackets [chord_name] within lyrics text and brackets are not empty."
            )

        return annotations


    def parse_lyrics_only_format(self, content: str) -> List[ChordAnnotation]:
        """Parse lyrics-only format: text without any chord annotations.

        Args:
            content: Ground truth content in lyrics-only format (text without chords)

        Returns:
            Empty list (no chord annotations available)

        This handler processes lyrics that contain no chord information. According to
        Requirement 1.3, when a lyrics-only format file is provided, the parser shall
        return an empty list of annotations.

        This is useful for:
        - Handling ground truth files that only contain lyrics text
        - Gracefully processing files where chord information is not available
        - Maintaining consistency in the parsing interface across all format types

        Examples:
            Input: "This is just plain text without any chords"
            Output: []

            Input: "涙があふれる心の中で"
            Output: []

            Input: "Multi-line lyrics\\nwithout any\\nchord annotations"
            Output: []

        Validates: Requirements 1.3
        """
        if not content or not isinstance(content, str):
            raise ValueError("content must be a non-empty string")

        # Lyrics-only format has no chord annotations
        # Return empty list as per Requirement 1.3
        return []
