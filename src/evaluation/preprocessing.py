"""
Chord evaluation preprocessing module.

This module provides functionality for preprocessing chord data before evaluation,
including normalization of chord notation and aggregation of high-resolution
predictions to match ground truth resolution.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Configure module logger
logger = logging.getLogger(__name__)


class NormalizationMode(Enum):
    """Chord normalization mode.
    
    Defines how slash chords and bass notes should be represented:
    - SLASH: Use slash notation (e.g., C/E)
    - ON: Use 'on' notation (e.g., ConE)
    - STANDARD: Use the most common/standard format
    """
    SLASH = "slash"
    ON = "on"
    STANDARD = "standard"


class AggregationStrategy(Enum):
    """Chord aggregation strategy.
    
    Defines how to select a single chord from multiple candidates in a time interval:
    - MOST_FREQUENT: Select the most frequently occurring chord
    - LONGEST_DURATION: Select the chord with the longest duration
    - FIRST: Select the first chord in the interval
    - LAST: Select the last chord in the interval
    """
    MOST_FREQUENT = "most_frequent"
    LONGEST_DURATION = "longest_duration"
    FIRST = "first"
    LAST = "last"


@dataclass
class PreprocessingConfig:
    """Configuration for chord preprocessing.
    
    Attributes:
        enable_normalization: Whether to normalize chord notation (default: True)
        enable_aggregation: Whether to aggregate chords to target resolution (default: True)
        normalization_mode: Mode for chord normalization (default: STANDARD)
        aggregation_strategy: Strategy for chord aggregation (default: MOST_FREQUENT)
        aggregation_tolerance: Timestamp tolerance in seconds for aggregation (default: 0.1)
    """
    enable_normalization: bool = True
    enable_aggregation: bool = True
    normalization_mode: NormalizationMode = NormalizationMode.STANDARD
    aggregation_strategy: AggregationStrategy = AggregationStrategy.MOST_FREQUENT
    aggregation_tolerance: float = 0.1


@dataclass
class ChordWithTimestamp:
    """Chord with timestamp information.
    
    Attributes:
        chord: The chord symbol (e.g., "C", "Am", "G/B")
        start_time: Start time in seconds
        end_time: End time in seconds (optional)
    """
    chord: str
    start_time: float
    end_time: Optional[float] = None
    
    @property
    def duration(self) -> float:
        """Calculate the duration of the chord.
        
        Returns:
            Duration in seconds. Returns 0.0 if end_time is not set.
        """
        if self.end_time is None:
            return 0.0
        return self.end_time - self.start_time


class ChordNormalizer:
    """Chord notation normalizer.
    
    Normalizes chord notation to a standard form, handling variations in:
    - Whitespace
    - Slash notation (C/E) vs on notation (ConE)
    - Quality representations (maj, M, major, min, m, etc.)
    - Enharmonic equivalents (C# vs Db)
    
    The normalizer ensures consistent chord representation for accurate evaluation.
    
    Attributes:
        mode: The normalization mode to use for bass note representation
    
    Example:
        >>> normalizer = ChordNormalizer(NormalizationMode.STANDARD)
        >>> normalizer.normalize("C maj / E")
        'CM/E'
        >>> normalizer.normalize("D min on F#")
        'Dm/F#'
    """
    
    def __init__(self, mode: NormalizationMode = NormalizationMode.STANDARD):
        """Initialize the chord normalizer.
        
        Args:
            mode: The normalization mode for bass note representation.
                  Defaults to STANDARD.
        
        Requirements:
            - 1.2: Handle slash notation and on notation
            - 1.3: Support configurable normalization modes
            - 5.3: Store normalization mode configuration
        """
        self.mode = mode
        self.logger = logging.getLogger(f"{__name__}.ChordNormalizer")

    def _parse_chord(self, chord: str) -> tuple[str, str, Optional[str]]:
        """Parse a chord string into root, quality, and bass components.

        Extracts the three main components of a chord:
        - Root note: The base note (e.g., "C", "F#", "Bb")
        - Quality: The chord type (e.g., "maj", "m", "7", "sus2")
        - Bass note: The bass note for slash chords (e.g., "E" in "C/E"), or None

        Handles both slash notation (C/E) and on notation (ConE).

        Args:
            chord: The chord string to parse (e.g., "Cmaj/E", "DonF#", "Am7")

        Returns:
            A tuple of (root, quality, bass) where:
            - root: Root note string (e.g., "C", "F#")
            - quality: Quality string (e.g., "maj", "m", "7", "")
            - bass: Bass note string or None if no bass note

        Raises:
            ValueError: If the chord cannot be parsed

        Examples:
            >>> self._parse_chord("C")
            ('C', '', None)
            >>> self._parse_chord("Cmaj")
            ('C', 'maj', None)
            >>> self._parse_chord("C/E")
            ('C', '', 'E')
            >>> self._parse_chord("Cmaj/E")
            ('C', 'maj', 'E')
            >>> self._parse_chord("ConE")
            ('C', '', 'E')
            >>> self._parse_chord("DonF#")
            ('D', '', 'F#')
            >>> self._parse_chord("Am7")
            ('A', 'm7', None)
            >>> self._parse_chord("Dsus2/C")
            ('D', 'sus2', 'C')

        Requirements:
            - 1.2: Handle slash notation (C/E)
            - 1.3: Handle on notation (ConE)
            - 1.4: Support various quality representations
        """
        import re

        if not chord:
            raise ValueError("Chord string cannot be empty")

        # Initialize bass as None
        bass = None

        # Check for slash notation (C/E)
        if "/" in chord:
            parts = chord.split("/", 1)
            chord_part = parts[0].strip()
            bass = parts[1].strip()
        # Check for on notation (ConE, DonF#)
        elif "on" in chord:
            # Use regex to split on "on" but preserve case
            match = re.match(r'^(.+?)on(.+)$', chord, re.IGNORECASE)
            if match:
                chord_part = match.group(1).strip()
                bass = match.group(2).strip()
            else:
                chord_part = chord
        else:
            chord_part = chord

        # Extract root note (A-G followed by optional # or b)
        root_pattern = r'^([A-G][#b]?)'
        match = re.match(root_pattern, chord_part)

        if not match:
            raise ValueError(f"Could not extract root note from chord: '{chord}'")

        root = match.group(1)

        # Extract quality (everything after the root note)
        quality = chord_part[match.end():].strip()

        return (root, quality, bass)
    def _normalize_root(self, root: str) -> str:
        """Normalize a root note to standard form.

        Normalizes root notes by:
        1. Converting to uppercase
        2. Handling enharmonic equivalents (e.g., C# vs Db)
        3. Preserving pitch class

        The normalization prefers sharps over flats for consistency with the codebase.
        Enharmonic mapping:
        - Db → C#
        - Eb → D#
        - Gb → F#
        - Ab → G#
        - Bb → A#

        Args:
            root: Root note string (e.g., "c", "C#", "Db", "f#")

        Returns:
            Normalized root note string (e.g., "C", "C#", "F#")

        Raises:
            ValueError: If the root note is invalid

        Examples:
            >>> self._normalize_root("c")
            'C'
            >>> self._normalize_root("C#")
            'C#'
            >>> self._normalize_root("Db")
            'C#'
            >>> self._normalize_root("f#")
            'F#'
            >>> self._normalize_root("Gb")
            'F#'

        Requirements:
            - 1.5: Handle enharmonic equivalents (C# vs Db)
            - 8.1: Preserve root note pitch class
        """
        if not root:
            raise ValueError("Root note cannot be empty")

        # Validate root note format before conversion (A-G followed by optional # or b)
        import re
        if not re.match(r'^[A-Ga-g][#bB]?$', root):
            raise ValueError(f"Invalid root note format: '{root}'")

        # Convert to uppercase
        root = root.upper()

        # Map enharmonic equivalents to sharps
        enharmonic_map = {
            'DB': 'C#',
            'EB': 'D#',
            'GB': 'F#',
            'AB': 'G#',
            'BB': 'A#',
        }

        # Apply enharmonic mapping if needed
        if root in enharmonic_map:
            root = enharmonic_map[root]

        return root
    def _normalize_quality(self, quality: str) -> str:
        """Normalize chord quality to standard form.

        Normalizes chord quality representations by mapping variations to standard forms:
        - Major: "maj", "M", "major" → "M"
        - Minor: "min", "m" → "m"
        - Other qualities (7, sus2, sus4, dim, aug, etc.) are preserved

        Compound qualities are also handled:
        - "maj7" → "M7"
        - "min7" → "m7"
        - "major7" → "M7"

        Args:
            quality: Quality string (e.g., "maj", "m", "7", "sus2", "maj7")

        Returns:
            Normalized quality string (e.g., "M", "m", "7", "sus2", "M7")

        Examples:
            >>> self._normalize_quality("")
            ''
            >>> self._normalize_quality("maj")
            'M'
            >>> self._normalize_quality("M")
            'M'
            >>> self._normalize_quality("major")
            'M'
            >>> self._normalize_quality("min")
            'm'
            >>> self._normalize_quality("m")
            'm'
            >>> self._normalize_quality("maj7")
            'M7'
            >>> self._normalize_quality("min7")
            'm7'
            >>> self._normalize_quality("7")
            '7'
            >>> self._normalize_quality("sus2")
            'sus2'
            >>> self._normalize_quality("sus4")
            'sus4'

        Requirements:
            - 1.4: Map quality variations to standard forms
            - 8.2: Preserve chord quality meaning
        """
        if not quality:
            return ""

        # Normalize to lowercase for comparison
        quality_lower = quality.lower()

        # Handle compound qualities with major first (longer match first)
        if quality_lower.startswith("major"):
            # Replace "major" with "M" at the start
            return "M" + quality[5:]
        elif quality_lower.startswith("maj"):
            # Replace "maj" with "M" at the start
            return "M" + quality[3:]

        # Handle compound qualities with minor
        elif quality_lower.startswith("min"):
            # Replace "min" with "m" at the start
            return "m" + quality[3:]

        # Map standalone major variations to "M"
        elif quality_lower == "m" and quality == "M":
            # Already standard major form
            return "M"

        # Map standalone minor variations to "m"
        elif quality_lower == "m" and quality == "m":
            # Already standard minor form
            return "m"

        # Preserve other qualities as-is (7, sus2, sus4, dim, aug, etc.)
        else:
            return quality

    def _build_chord(
        self, root: str, quality: str, bass: Optional[str]
    ) -> str:
        """Build a normalized chord string from components.

        Constructs a chord string from root, quality, and optional bass note,
        applying the configured normalization mode for bass note representation.

        Normalization modes:
        - SLASH: Use "/" separator (e.g., "C/E")
        - ON: Use "on" separator (e.g., "ConE")
        - STANDARD: Use "/" separator (same as SLASH)

        Args:
            root: Normalized root note (e.g., "C", "F#")
            quality: Normalized quality (e.g., "M", "m", "7", "sus2")
            bass: Normalized bass note or None (e.g., "E", "F#", None)

        Returns:
            Normalized chord string (e.g., "CM/E", "DmonF#", "Am7")

        Examples:
            >>> # STANDARD mode (default)
            >>> self._build_chord("C", "M", "E")
            'CM/E'
            >>> self._build_chord("D", "m", None)
            'Dm'
            >>> self._build_chord("A", "", "C#")
            'A/C#'

            >>> # SLASH mode
            >>> normalizer = ChordNormalizer(NormalizationMode.SLASH)
            >>> normalizer._build_chord("C", "M", "E")
            'CM/E'

            >>> # ON mode
            >>> normalizer = ChordNormalizer(NormalizationMode.ON)
            >>> normalizer._build_chord("C", "M", "E")
            'CMonE'

        Requirements:
            - 1.2: Apply normalization mode for bass notes
            - 1.3: Handle SLASH, ON, STANDARD modes
            - 8.3: Preserve bass note information
        """
        # Build base chord (root + quality)
        chord = root + quality

        # Add bass note if present
        if bass:
            if self.mode == NormalizationMode.ON:
                # Use "on" notation
                chord = chord + "on" + bass
            else:
                # Use "/" notation for both SLASH and STANDARD modes
                chord = chord + "/" + bass

        return chord

    def normalize(self, chord: str) -> str:
        """Normalize a chord string to standard form.

        Applies all normalization steps to convert a chord to standard notation:
        1. Strip whitespace from input
        2. Parse chord into root, quality, and bass components
        3. Normalize root note (uppercase, enharmonic equivalents)
        4. Normalize quality (standard representations)
        5. Normalize bass note if present
        6. Build normalized chord string according to mode

        Args:
            chord: The chord string to normalize (e.g., "C maj / E", "DonF#", "Am7")

        Returns:
            Normalized chord string (e.g., "CM/E", "D/F#", "Am7")

        Raises:
            ValueError: If the chord is empty or has invalid notation

        Examples:
            >>> normalizer = ChordNormalizer(NormalizationMode.STANDARD)
            >>> normalizer.normalize("C maj / E")
            'CM/E'
            >>> normalizer.normalize("  Dm  ")
            'Dm'
            >>> normalizer.normalize("DonF#")
            'D/F#'
            >>> normalizer.normalize("Dbmaj7")
            'C#M7'

        Requirements:
            - 1.1: Strip whitespace from input
            - 1.6: Idempotent normalization
            - 1.8: Raise ValueError for invalid chords
            - 6.1: Provide detailed error messages
            - 8.1: Preserve root note pitch class
            - 8.2: Preserve chord quality meaning
            - 8.3: Preserve bass note pitch
        """
        # Step 1: Strip whitespace from input
        chord = chord.strip()
        
        # Step 1.5: Convert full-width characters to half-width
        # Replace full-width sharp (♯) with half-width (#)
        # Replace full-width flat (♭) with half-width (b)
        chord = chord.replace('♯', '#').replace('♭', 'b')

        # Step 2: Validate input
        if not chord:
            error_msg = "Chord string cannot be empty. Expected format: root[quality][/bass] (e.g., 'C', 'Am', 'G/B')"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate chord string length (max 100 characters) - Requirement 7.5
        if len(chord) > 100:
            error_msg = f"Chord string too long: {len(chord)} characters (max 100). Input: '{chord[:50]}...'"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 3: Parse chord into root, quality, bass
        try:
            root, quality, bass = self._parse_chord(chord)
        except ValueError as e:
            # Re-raise with more context
            error_msg = f"Invalid chord notation '{chord}': {str(e)}. Expected format: root[quality][/bass] (e.g., 'C', 'Am7', 'G/B')"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 4: Normalize root note
        try:
            normalized_root = self._normalize_root(root)
        except ValueError as e:
            error_msg = f"Invalid root note in chord '{chord}': {str(e)}. Root must be A-G followed by optional # or b (e.g., 'C', 'F#', 'Bb')"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 5: Normalize quality
        normalized_quality = self._normalize_quality(quality)

        # Step 6: Normalize bass note (if present)
        if bass:
            try:
                normalized_bass = self._normalize_root(bass)
            except ValueError as e:
                error_msg = f"Invalid bass note in chord '{chord}': {str(e)}. Bass note must be A-G followed by optional # or b (e.g., 'E', 'C#', 'Bb')"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            normalized_bass = None

        # Step 7: Build normalized chord string
        normalized_chord = self._build_chord(
            normalized_root,
            normalized_quality,
            normalized_bass
        )

        return normalized_chord

    def normalize_batch(self, chords: list[str]) -> list[str]:
        """Normalize multiple chords to standard form.

        Applies normalization to each chord in the input list. This is equivalent
        to calling normalize() on each chord individually.

        Args:
            chords: List of chord strings to normalize

        Returns:
            List of normalized chord strings in the same order

        Examples:
            >>> normalizer = ChordNormalizer(NormalizationMode.STANDARD)
            >>> normalizer.normalize_batch(["C maj / E", "Dm", "DonF#"])
            ['CM/E', 'Dm', 'D/F#']
            >>> normalizer.normalize_batch([])
            []

        Requirements:
            - 1.7: Batch normalization equivalent to individual normalization
        """
        return [self.normalize(chord) for chord in chords]








class ChordAggregator:
    """Chord aggregator for matching prediction resolution to ground truth.
    
    Aggregates high-resolution predicted chords to match the lower resolution
    of ground truth annotations. This addresses the mismatch between predicted
    chords (e.g., 3009) and ground truth chords (e.g., 125) that causes low
    evaluation accuracy.
    
    The aggregator divides time into intervals based on ground truth timestamps
    and selects a single representative chord for each interval using the
    configured strategy.
    
    Attributes:
        strategy: The aggregation strategy to use for chord selection
        tolerance: Timestamp tolerance in seconds for interval boundaries
    
    Example:
        >>> aggregator = ChordAggregator(
        ...     strategy=AggregationStrategy.MOST_FREQUENT,
        ...     tolerance=0.1
        ... )
        >>> predicted = ["C", "C", "C", "D", "D", "E"]
        >>> pred_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]
        >>> target_times = [0.0, 1.5, 3.0]
        >>> aggregator.aggregate(predicted, pred_times, target_times)
        ['C', 'D']
    """
    
    def __init__(
        self,
        strategy: AggregationStrategy = AggregationStrategy.MOST_FREQUENT,
        tolerance: float = 0.1
    ):
        """Initialize the chord aggregator.
        
        Args:
            strategy: The aggregation strategy for selecting chords from intervals.
                     Defaults to MOST_FREQUENT.
            tolerance: Timestamp tolerance in seconds for interval boundaries.
                      Chords within tolerance of an interval boundary are included
                      in that interval. Defaults to 0.1 seconds.
        
        Requirements:
            - 2.7: Apply tolerance to interval boundaries
            - 5.4: Store aggregation strategy configuration
            - 5.5: Store tolerance configuration
        """
        self.strategy = strategy
        self.tolerance = tolerance
        self.logger = logging.getLogger(f"{__name__}.ChordAggregator")


    def _collect_chords_in_interval(
        self,
        predicted_chords: list[str],
        predicted_timestamps: list[float],
        start_time: float,
        end_time: float
    ) -> list[tuple[str, float]]:
        """Find all chords within a timestamp interval.

        Collects predicted chords that fall within the specified time interval,
        applying tolerance to the interval boundaries. This helper method is used
        by the aggregation logic to gather candidate chords for each target interval.

        Args:
            predicted_chords: List of predicted chord strings
            predicted_timestamps: List of timestamps for predicted chords
            start_time: Start of the interval (inclusive with tolerance)
            end_time: End of the interval (exclusive with tolerance)

        Returns:
            List of (chord, timestamp) tuples for chords within the interval.
            Returns empty list if no chords fall within the interval.

        Requirements:
            - 2.1: Find chords within timestamp interval
            - 2.7: Apply tolerance to interval boundaries

        Example:
            >>> aggregator = ChordAggregator(tolerance=0.1)
            >>> chords = ["C", "D", "E", "F"]
            >>> times = [0.0, 1.0, 2.0, 3.0]
            >>> aggregator._collect_chords_in_interval(chords, times, 0.5, 2.5)
            [('D', 1.0), ('E', 2.0)]
        """
        chords_in_interval = []

        for i in range(len(predicted_chords)):
            pred_time = predicted_timestamps[i]

            # Apply tolerance to interval boundaries
            # A chord is included if its timestamp is within tolerance of the interval
            if start_time - self.tolerance <= pred_time < end_time + self.tolerance:
                chords_in_interval.append((predicted_chords[i], pred_time))

        return chords_in_interval

    def _select_chord_by_strategy(
        self,
        chords_in_interval: list[tuple[str, float]]
    ) -> str:
        """Select a single chord from an interval based on the aggregation strategy.

        Applies the configured aggregation strategy to select one representative
        chord from the list of candidates in a time interval.

        Strategies:
        - MOST_FREQUENT: Returns the chord that appears most often in the interval.
          If there's a tie, returns the first chord among the tied chords.
        - LONGEST_DURATION: Returns the chord with the longest duration.
          Duration is calculated as the time until the next chord.
          For the last chord, a default duration of 0.0 is used.
          If there's a tie, returns the first chord among the tied chords.
        - FIRST: Returns the first chord in the interval (earliest timestamp).
        - LAST: Returns the last chord in the interval (latest timestamp).

        Args:
            chords_in_interval: List of (chord, timestamp) tuples representing
                               chords within a time interval. Must not be empty.

        Returns:
            The selected chord string based on the strategy.

        Raises:
            ValueError: If chords_in_interval is empty.

        Requirements:
            - 2.2: Implement MOST_FREQUENT strategy
            - 2.3: Implement LONGEST_DURATION strategy
            - 2.4: Implement FIRST strategy
            - 2.5: Implement LAST strategy

        Example:
            >>> aggregator = ChordAggregator(strategy=AggregationStrategy.MOST_FREQUENT)
            >>> chords = [("C", 0.0), ("C", 0.5), ("D", 1.0)]
            >>> aggregator._select_chord_by_strategy(chords)
            'C'

            >>> aggregator = ChordAggregator(strategy=AggregationStrategy.FIRST)
            >>> aggregator._select_chord_by_strategy(chords)
            'C'

            >>> aggregator = ChordAggregator(strategy=AggregationStrategy.LAST)
            >>> aggregator._select_chord_by_strategy(chords)
            'D'
        """
        if not chords_in_interval:
            raise ValueError("Cannot select chord from empty interval")

        if self.strategy == AggregationStrategy.MOST_FREQUENT:
            # Count occurrences of each chord
            from collections import Counter
            chord_counts = Counter(chord for chord, _ in chords_in_interval)
            # Return the most common chord (first in case of tie)
            most_common_chord, _ = chord_counts.most_common(1)[0]
            return most_common_chord

        elif self.strategy == AggregationStrategy.LONGEST_DURATION:
            # Calculate duration for each chord
            max_duration = 0.0
            longest_chord = chords_in_interval[0][0]  # Default to first chord

            for i in range(len(chords_in_interval)):
                chord, start_time = chords_in_interval[i]

                # Calculate duration as time until next chord
                if i + 1 < len(chords_in_interval):
                    end_time = chords_in_interval[i + 1][1]
                    duration = end_time - start_time
                else:
                    # Last chord: use default duration of 0.0
                    duration = 0.0

                # Update if this chord has longer duration
                if duration > max_duration:
                    max_duration = duration
                    longest_chord = chord

            return longest_chord

        elif self.strategy == AggregationStrategy.FIRST:
            # Return the first chord (earliest timestamp)
            return chords_in_interval[0][0]

        elif self.strategy == AggregationStrategy.LAST:
            # Return the last chord (latest timestamp)
            return chords_in_interval[-1][0]

        else:
            raise ValueError(f"Unknown aggregation strategy: {self.strategy}")

    def _find_nearest_chord(
        self,
        predicted_chords: list[str],
        predicted_timestamps: list[float],
        target_time: float
    ) -> str:
        """Find the chord with minimum time distance to target time.

        When no chords fall within a target interval, this method finds the
        predicted chord that is closest in time to the interval start. This
        ensures every interval has a valid chord assignment.

        Args:
            predicted_chords: List of predicted chord strings
            predicted_timestamps: List of timestamps for predicted chords
            target_time: The target time (typically interval start) to find nearest chord for

        Returns:
            The chord string with minimum absolute time distance to target_time.

        Raises:
            ValueError: If predicted_chords or predicted_timestamps is empty.

        Requirements:
            - 2.6: Find nearest chord when interval is empty

        Example:
            >>> aggregator = ChordAggregator()
            >>> chords = ["C", "D", "E"]
            >>> times = [0.0, 2.0, 4.0]
            >>> aggregator._find_nearest_chord(chords, times, 1.5)
            'D'
            >>> aggregator._find_nearest_chord(chords, times, 3.5)
            'E'
        """
        if not predicted_chords or not predicted_timestamps:
            raise ValueError("Cannot find nearest chord from empty list")

        # Find the chord with minimum absolute time distance
        min_distance = float('inf')
        nearest_chord = predicted_chords[0]

        for i in range(len(predicted_chords)):
            distance = abs(predicted_timestamps[i] - target_time)
            if distance < min_distance:
                min_distance = distance
                nearest_chord = predicted_chords[i]

        return nearest_chord

    def aggregate(
        self,
        predicted_chords: list[str],
        predicted_timestamps: list[float],
        target_timestamps: list[float]
    ) -> list[str]:
        """Aggregate predicted chords to match target timestamp resolution.

        This is the main public method that aggregates high-resolution predicted
        chords to match the lower resolution of ground truth timestamps. For each
        target timestamp interval, it collects chords within that interval and
        selects one representative chord using the configured strategy.

        The algorithm:
        1. Validate inputs (chord count matches timestamp count, timestamps sorted, non-negative)
        2. For each target timestamp interval:
           a. Collect chords in the interval (with tolerance)
           b. If chords found, select one using the configured strategy
           c. If no chords found, use nearest chord fallback
        3. Return aggregated chord list matching target timestamp count

        Args:
            predicted_chords: List of predicted chord strings
            predicted_timestamps: List of timestamps for predicted chords (in seconds)
            target_timestamps: List of target timestamps to aggregate to (ground truth resolution)

        Returns:
            List of aggregated chords with length equal to len(target_timestamps).
            Each chord represents the selected chord for the corresponding target interval.

        Raises:
            ValueError: If chord count doesn't match timestamp count
            ValueError: If timestamps are not sorted in ascending order
            ValueError: If timestamps contain negative values

        Requirements:
            - 2.1: Select one chord for each target timestamp interval
            - 2.8: Ensure aggregated chord count matches target timestamp count
            - 2.9: Validate chord count matches timestamp count
            - 2.10: Validate timestamps are sorted in ascending order
            - 6.2: Validate chord count matches timestamp count
            - 6.4: Validate timestamps are sorted
            - 6.5: Validate timestamps are non-negative
            - 8.4: Preserve timestamp order
            - 8.5: Assign valid chord to each interval

        Example:
            >>> aggregator = ChordAggregator(
            ...     strategy=AggregationStrategy.MOST_FREQUENT,
            ...     tolerance=0.1
            ... )
            >>> predicted = ["C", "C", "C", "D", "D", "E", "E", "E"]
            >>> pred_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
            >>> target_times = [0.0, 1.5, 3.0]
            >>> result = aggregator.aggregate(predicted, pred_times, target_times)
            >>> result
            ['C', 'D', 'E']
            >>> len(result) == len(target_times)
            True
        """
        # Step 1: Input validation

        # Validate chord count limit (max 100,000) - Requirement 7.4
        if len(predicted_chords) > 100000:
            error_msg = (
                f"Chord count exceeds maximum limit: {len(predicted_chords)} chords "
                f"(max 100,000). Consider processing in smaller batches."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate chord count matches timestamp count
        if len(predicted_chords) != len(predicted_timestamps):
            error_msg = (
                f"Chord count ({len(predicted_chords)}) must match "
                f"timestamp count ({len(predicted_timestamps)}). "
                f"Each chord must have exactly one timestamp."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate timestamps are non-negative and within range (0 to 10,000 seconds) - Requirements 6.5, 7.6
        for i, timestamp in enumerate(predicted_timestamps):
            if timestamp < 0:
                error_msg = (
                    f"Predicted timestamp at index {i} is negative: {timestamp} seconds. "
                    "All timestamps must be non-negative (>= 0)."
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            if timestamp > 10000:
                error_msg = (
                    f"Predicted timestamp at index {i} exceeds maximum: {timestamp} seconds "
                    "(max 10,000). Timestamp out of valid range."
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)

        for i, timestamp in enumerate(target_timestamps):
            if timestamp < 0:
                error_msg = (
                    f"Target timestamp at index {i} is negative: {timestamp} seconds. "
                    "All timestamps must be non-negative (>= 0)."
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            if timestamp > 10000:
                error_msg = (
                    f"Target timestamp at index {i} exceeds maximum: {timestamp} seconds "
                    "(max 10,000). Timestamp out of valid range."
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)

        # Validate timestamps are sorted in ascending order
        for i in range(len(predicted_timestamps) - 1):
            if predicted_timestamps[i] > predicted_timestamps[i + 1]:
                error_msg = (
                    f"Predicted timestamps not sorted in ascending order: "
                    f"timestamp[{i}]={predicted_timestamps[i]} > "
                    f"timestamp[{i+1}]={predicted_timestamps[i+1]}. "
                    "Timestamps must be sorted before aggregation."
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)

        for i in range(len(target_timestamps) - 1):
            if target_timestamps[i] > target_timestamps[i + 1]:
                error_msg = (
                    f"Target timestamps not sorted in ascending order: "
                    f"timestamp[{i}]={target_timestamps[i]} > "
                    f"timestamp[{i+1}]={target_timestamps[i+1]}. "
                    "Timestamps must be sorted before aggregation."
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)

        # Step 2: Aggregate chords for each target timestamp interval
        aggregated_chords = []
        empty_intervals = 0

        for i in range(len(target_timestamps)):
            # Determine interval boundaries
            start_time = target_timestamps[i]

            # End time is the next target timestamp, or infinity for the last interval
            if i + 1 < len(target_timestamps):
                end_time = target_timestamps[i + 1]
            else:
                end_time = float('inf')

            # Collect chords in this interval
            chords_in_interval = self._collect_chords_in_interval(
                predicted_chords,
                predicted_timestamps,
                start_time,
                end_time
            )

            # Select chord based on strategy or use nearest chord fallback
            if chords_in_interval:
                # Chords found in interval - select using strategy
                selected_chord = self._select_chord_by_strategy(chords_in_interval)
            else:
                # No chords in interval - use nearest chord fallback
                empty_intervals += 1
                selected_chord = self._find_nearest_chord(
                    predicted_chords,
                    predicted_timestamps,
                    start_time
                )
                # Log warning for empty interval with fallback
                self.logger.warning(
                    f"No chords found in interval [{start_time:.2f}, {end_time:.2f}). "
                    f"Using nearest chord fallback: '{selected_chord}'"
                )

            aggregated_chords.append(selected_chord)

        # Log summary if there were empty intervals
        if empty_intervals > 0:
            self.logger.warning(
                f"Aggregation completed with {empty_intervals} empty intervals "
                f"out of {len(target_timestamps)} total intervals. "
                "Nearest chord fallback was used for these intervals."
            )

        # Step 3: Return aggregated chord list
        # Post-condition: length matches target_timestamps
        assert len(aggregated_chords) == len(target_timestamps), \
            f"Aggregated chord count ({len(aggregated_chords)}) must match " \
            f"target timestamp count ({len(target_timestamps)})"

        return aggregated_chords






class PreprocessingPipeline:
    """Preprocessing pipeline for chord evaluation.
    
    Integrates chord normalization and aggregation into a unified preprocessing
    pipeline. This class provides a high-level interface for preprocessing both
    predicted and ground truth chords before evaluation.
    
    The pipeline applies preprocessing in the following order:
    1. Normalization (if enabled): Standardizes chord notation
    2. Aggregation (if enabled): Matches predicted chord resolution to ground truth
    
    Attributes:
        config: The preprocessing configuration
        normalizer: The chord normalizer instance
        aggregator: The chord aggregator instance
    
    Example:
        >>> config = PreprocessingConfig(
        ...     enable_normalization=True,
        ...     enable_aggregation=True,
        ...     normalization_mode=NormalizationMode.STANDARD,
        ...     aggregation_strategy=AggregationStrategy.MOST_FREQUENT
        ... )
        >>> pipeline = PreprocessingPipeline(config)
        >>> predicted = ["C maj / E", "D min", "G"]
        >>> ground_truth = ["CM/E", "Dm", "G"]
        >>> pred_times = [0.0, 1.0, 2.0]
        >>> gt_times = [0.0, 2.0]
        >>> processed_pred, processed_gt = pipeline.preprocess(
        ...     predicted, ground_truth, pred_times, gt_times
        ... )
    """
    
    def __init__(self, config: PreprocessingConfig):
        """Initialize the preprocessing pipeline.
        
        Creates a preprocessing pipeline with the specified configuration.
        Initializes the chord normalizer and aggregator based on the config settings.
        
        Args:
            config: The preprocessing configuration specifying which features
                   to enable and how to configure them.
        
        Requirements:
            - 3.1: Initialize based on configuration
            - 5.1: Accept PreprocessingConfig
            - 5.2: Initialize ChordNormalizer and ChordAggregator
            - 5.3: Use config.normalization_mode for normalizer
            - 5.4: Use config.aggregation_strategy for aggregator
            - 5.5: Use config.aggregation_tolerance for aggregator
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PreprocessingPipeline")
        
        # Initialize ChordNormalizer with configured normalization mode
        self.normalizer = ChordNormalizer(mode=config.normalization_mode)
        
        # Initialize ChordAggregator with configured strategy and tolerance
        self.aggregator = ChordAggregator(
            strategy=config.aggregation_strategy,
            tolerance=config.aggregation_tolerance
        )


    def preprocess(
        self,
        predicted: list[str],
        ground_truth: list[str],
        predicted_timestamps: Optional[list[float]] = None,
        ground_truth_timestamps: Optional[list[float]] = None
    ) -> tuple[list[str], list[str]]:
        """Preprocess predicted and ground truth chords.

        This is the main public method that applies preprocessing to both predicted
        and ground truth chords. The preprocessing steps are applied in order:
        1. Input validation (empty lists)
        2. Normalization (if enabled) - applied to both predicted and ground_truth
        3. Aggregation (if enabled and timestamps provided) - applied to predicted only

        The method ensures that:
        - Both chord lists are non-empty
        - Normalization is applied before aggregation
        - Aggregation is skipped if timestamps are not provided
        - The output maintains the same structure as input (tuple of two lists)

        Args:
            predicted: List of predicted chord strings
            ground_truth: List of ground truth chord strings
            predicted_timestamps: Optional list of timestamps for predicted chords (in seconds)
            ground_truth_timestamps: Optional list of timestamps for ground truth chords (in seconds)

        Returns:
            A tuple of (processed_predicted, processed_ground_truth) where:
            - processed_predicted: Preprocessed predicted chords
            - processed_ground_truth: Preprocessed ground truth chords

        Raises:
            ValueError: If predicted or ground_truth is empty

        Requirements:
            - 3.2: Apply normalization if enabled (both predicted and ground_truth)
            - 3.3: Apply aggregation if enabled and timestamps provided
            - 3.4: Ensure processing order: normalization before aggregation
            - 3.5: Return input unchanged if both features disabled
            - 3.6: Skip aggregation if timestamps not provided
            - 3.7: Return tuple of (processed_predicted, processed_ground_truth)
            - 3.8: Raise ValueError for empty chord lists
            - 6.3: Validate input and raise ValueError for empty lists

        Example:
            >>> config = PreprocessingConfig(
            ...     enable_normalization=True,
            ...     enable_aggregation=True
            ... )
            >>> pipeline = PreprocessingPipeline(config)
            >>> predicted = ["C maj / E", "C maj / E", "D min"]
            >>> ground_truth = ["CM/E", "Dm"]
            >>> pred_times = [0.0, 1.0, 2.0]
            >>> gt_times = [0.0, 2.0]
            >>> processed_pred, processed_gt = pipeline.preprocess(
            ...     predicted, ground_truth, pred_times, gt_times
            ... )
            >>> len(processed_pred) == len(gt_times)
            True
            >>> processed_pred
            ['CM/E', 'Dm']
            >>> processed_gt
            ['CM/E', 'Dm']
        """
        # Step 1: Input validation
        if not predicted:
            error_msg = (
                "Predicted chord list cannot be empty. "
                "Provide at least one predicted chord for preprocessing."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        if not ground_truth:
            error_msg = (
                "Ground truth chord list cannot be empty. "
                "Provide at least one ground truth chord for preprocessing."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate chord count limit (max 100,000) - Requirement 7.4
        if len(predicted) > 100000:
            error_msg = (
                f"Predicted chord count exceeds maximum limit: {len(predicted)} chords "
                f"(max 100,000). Consider processing in smaller batches."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        if len(ground_truth) > 100000:
            error_msg = (
                f"Ground truth chord count exceeds maximum limit: {len(ground_truth)} chords "
                f"(max 100,000). Consider processing in smaller batches."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 2: Apply normalization if enabled
        if self.config.enable_normalization:
            self.logger.debug(
                f"Normalizing {len(predicted)} predicted chords and "
                f"{len(ground_truth)} ground truth chords"
            )
            # Normalize both predicted and ground truth chords
            try:
                normalized_predicted = self.normalizer.normalize_batch(predicted)
                normalized_ground_truth = self.normalizer.normalize_batch(ground_truth)
            except ValueError as e:
                error_msg = f"Normalization failed: {str(e)}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            # Use original chords if normalization is disabled
            normalized_predicted = predicted
            normalized_ground_truth = ground_truth

        # Step 3: Apply aggregation if enabled and timestamps are provided
        if self.config.enable_aggregation:
            # Check if timestamps are provided
            if predicted_timestamps is not None and ground_truth_timestamps is not None:
                self.logger.debug(
                    f"Aggregating {len(normalized_predicted)} predicted chords to "
                    f"{len(ground_truth_timestamps)} target timestamps using "
                    f"{self.config.aggregation_strategy.value} strategy"
                )
                # Aggregate predicted chords to ground truth resolution
                try:
                    aggregated_predicted = self.aggregator.aggregate(
                        normalized_predicted,
                        predicted_timestamps,
                        ground_truth_timestamps
                    )
                except ValueError as e:
                    error_msg = f"Aggregation failed: {str(e)}"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)
            else:
                # Skip aggregation if timestamps not provided
                self.logger.warning(
                    "Aggregation is enabled but timestamps not provided. "
                    "Skipping aggregation step."
                )
                aggregated_predicted = normalized_predicted
        else:
            # Use normalized chords if aggregation is disabled
            aggregated_predicted = normalized_predicted

        # Step 4: Return tuple of processed chords
        self.logger.debug(
            f"Preprocessing complete: {len(aggregated_predicted)} predicted chords, "
            f"{len(normalized_ground_truth)} ground truth chords"
        )
        return (aggregated_predicted, normalized_ground_truth)

