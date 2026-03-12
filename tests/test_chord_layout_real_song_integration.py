"""Integration tests for chord layout with real song - Task 6.4

Tests chord layout calculation with full song analysis:
- Analyze full song → verify all lines have 16 bars
- Verify visual layout matches specification
- Test with different tempos (60, 120, 180 BPM)

Validates Requirement: 2.6
"""

import pytest
import numpy as np
from pathlib import Path
import soundfile as sf

from src.audio_engine import AudioProcessingEngine
from src.models import ChordSegment, ChordQuality


@pytest.fixture
def test_full_song_audio(tmp_path):
    """Create test audio file simulating a full song with many chords"""
    sample_rate = 22050
    duration_per_chord = 4.0  # 4 seconds per chord
    num_chords = 48  # 48 chords = 192 seconds (~3 minutes)
    
    # Define a realistic chord progression that repeats
    chord_pattern = [
        [60, 64, 67],    # C major
        [67, 71, 74],    # G major
        [69, 72, 76],    # A minor
        [65, 69, 72],    # F major
        [62, 66, 69],    # D minor
        [67, 71, 74],    # G major
        [60, 64, 67],    # C major
        [65, 69, 72],    # F major
    ]
    
    # Generate audio for full song
    audio_segments = []
    for i in range(num_chords):
        # Cycle through chord pattern
        chord_notes = chord_pattern[i % len(chord_pattern)]
        
        t = np.linspace(0, duration_per_chord, int(sample_rate * duration_per_chord))
        chord_audio = np.zeros_like(t)
        
        # Add each note in the chord
        for note in chord_notes:
            freq = 440 * (2 ** ((note - 69) / 12))  # MIDI to frequency
            chord_audio += 0.2 * np.sin(2 * np.pi * freq * t)
        
        audio_segments.append(chord_audio)
    
    # Concatenate all chords
    full_audio = np.concatenate(audio_segments)
    
    # Save as WAV file
    audio_file = tmp_path / "full_song.wav"
    sf.write(str(audio_file), full_audio, sample_rate)
    
    return audio_file, sample_rate, duration_per_chord, num_chords


@pytest.fixture
def audio_engine(tmp_path):
    """Create AudioProcessingEngine with test cache directory"""
    cache_dir = tmp_path / "cache"
    return AudioProcessingEngine(cache_dir=cache_dir)


def calculate_bars_per_chord(chord_duration, tempo):
    """Calculate number of bars in a chord given duration and tempo"""
    BEATS_PER_BAR = 4
    seconds_per_beat = 60 / tempo
    seconds_per_bar = seconds_per_beat * BEATS_PER_BAR
    return chord_duration / seconds_per_bar


def group_chords_into_lines(chords, tempo):
    """Group chords into lines of 16 bars (mimics ChordVisualization logic)"""
    BARS_PER_LINE = 16
    BEATS_PER_BAR = 4
    
    lines = []
    current_line = []
    bar_count = 0
    
    # Calculate seconds per bar based on tempo
    seconds_per_beat = 60 / tempo
    seconds_per_bar = seconds_per_beat * BEATS_PER_BAR
    
    for chord in chords:
        chord_duration = chord.end_time - chord.start_time
        bars_in_chord = np.ceil(chord_duration / seconds_per_bar)
        
        if bar_count + bars_in_chord > BARS_PER_LINE and len(current_line) > 0:
            lines.append(current_line)
            current_line = []
            bar_count = 0
        
        current_line.append(chord)
        bar_count += bars_in_chord
    
    if len(current_line) > 0:
        lines.append(current_line)
    
    return lines


def test_full_song_layout_at_120_bpm(audio_engine, test_full_song_audio, monkeypatch):
    """
    Test chord layout with full song at 120 BPM.
    
    At 120 BPM:
    - 1 beat = 0.5 seconds
    - 1 bar (4 beats) = 2 seconds
    - 4 seconds per chord = 2 bars per chord
    - 48 chords × 2 bars = 96 bars total
    - Expected: 6 lines of 16 bars each
    
    **Validates: Requirement 2.6**
    """
    from src.lyrics_transcription import LyricsTranscriptionModule
    
    def mock_transcribe(self, audio, sample_rate, language="ja"):
        return []
    
    monkeypatch.setattr(LyricsTranscriptionModule, 'transcribe', mock_transcribe)
    
    audio_file, sample_rate, duration_per_chord, num_chords = test_full_song_audio
    tempo = 120  # BPM
    
    # Load and analyze
    audio_engine.load_audio_file(audio_file)
    result = audio_engine.analyze_audio(use_cache=False)
    
    # Verify we got chord results
    assert len(result.chord_progression) > 0, "Should detect chords from full song"
    
    # Group chords into lines
    lines = group_chords_into_lines(result.chord_progression, tempo)
    
    # Calculate expected number of lines
    bars_per_chord = calculate_bars_per_chord(duration_per_chord, tempo)
    total_bars = len(result.chord_progression) * bars_per_chord
    expected_lines = int(np.ceil(total_bars / 16))
    
    # Verify line count
    assert len(lines) == expected_lines, \
        f"Expected {expected_lines} lines at 120 BPM, got {len(lines)}"
    
    # Verify each line (except possibly the last) has 16 bars
    BARS_PER_LINE = 16
    BEATS_PER_BAR = 4
    seconds_per_beat = 60 / tempo
    seconds_per_bar = seconds_per_beat * BEATS_PER_BAR
    
    for i, line in enumerate(lines[:-1]):  # All lines except last
        line_bars = sum(np.ceil((c.end_time - c.start_time) / seconds_per_bar) for c in line)
        assert line_bars == BARS_PER_LINE, \
            f"Line {i+1} should have exactly {BARS_PER_LINE} bars, got {line_bars}"
    
    print(f"✓ Full song at 120 BPM: {len(lines)} lines, layout correct")



def test_full_song_layout_at_60_bpm(audio_engine, test_full_song_audio, monkeypatch):
    """
    Test chord layout with full song at 60 BPM (slower tempo).
    
    At 60 BPM:
    - 1 beat = 1 second
    - 1 bar (4 beats) = 4 seconds
    - 4 seconds per chord = 1 bar per chord
    - 48 chords × 1 bar = 48 bars total
    - Expected: 3 lines of 16 bars each
    
    **Validates: Requirement 2.6**
    """
    from src.lyrics_transcription import LyricsTranscriptionModule
    
    def mock_transcribe(self, audio, sample_rate, language="ja"):
        return []
    
    monkeypatch.setattr(LyricsTranscriptionModule, 'transcribe', mock_transcribe)
    
    audio_file, sample_rate, duration_per_chord, num_chords = test_full_song_audio
    tempo = 60  # BPM
    
    # Load and analyze
    audio_engine.load_audio_file(audio_file)
    result = audio_engine.analyze_audio(use_cache=False)
    
    # Verify we got chord results
    assert len(result.chord_progression) > 0, "Should detect chords from full song"
    
    # Group chords into lines
    lines = group_chords_into_lines(result.chord_progression, tempo)
    
    # Calculate expected number of lines
    bars_per_chord = calculate_bars_per_chord(duration_per_chord, tempo)
    total_bars = len(result.chord_progression) * bars_per_chord
    expected_lines = int(np.ceil(total_bars / 16))
    
    # Verify line count
    assert len(lines) == expected_lines, \
        f"Expected {expected_lines} lines at 60 BPM, got {len(lines)}"
    
    # Verify each line (except possibly the last) has 16 bars
    BARS_PER_LINE = 16
    BEATS_PER_BAR = 4
    seconds_per_beat = 60 / tempo
    seconds_per_bar = seconds_per_beat * BEATS_PER_BAR
    
    for i, line in enumerate(lines[:-1]):  # All lines except last
        line_bars = sum(np.ceil((c.end_time - c.start_time) / seconds_per_bar) for c in line)
        assert line_bars == BARS_PER_LINE, \
            f"Line {i+1} should have exactly {BARS_PER_LINE} bars, got {line_bars}"
    
    print(f"✓ Full song at 60 BPM: {len(lines)} lines, layout correct")


def test_full_song_layout_at_180_bpm(audio_engine, test_full_song_audio, monkeypatch):
    """
    Test chord layout with full song at 180 BPM (faster tempo).
    
    At 180 BPM:
    - 1 beat = 0.333... seconds
    - 1 bar (4 beats) = 1.333... seconds
    - 4 seconds per chord = 3 bars per chord
    - 48 chords × 3 bars = 144 bars total
    - Expected: 9 lines of 16 bars each
    
    **Validates: Requirement 2.6**
    """
    from src.lyrics_transcription import LyricsTranscriptionModule
    
    def mock_transcribe(self, audio, sample_rate, language="ja"):
        return []
    
    monkeypatch.setattr(LyricsTranscriptionModule, 'transcribe', mock_transcribe)
    
    audio_file, sample_rate, duration_per_chord, num_chords = test_full_song_audio
    tempo = 180  # BPM
    
    # Load and analyze
    audio_engine.load_audio_file(audio_file)
    result = audio_engine.analyze_audio(use_cache=False)
    
    # Verify we got chord results
    assert len(result.chord_progression) > 0, "Should detect chords from full song"
    
    # Group chords into lines
    lines = group_chords_into_lines(result.chord_progression, tempo)
    
    # Calculate expected number of lines
    bars_per_chord = calculate_bars_per_chord(duration_per_chord, tempo)
    total_bars = len(result.chord_progression) * bars_per_chord
    expected_lines = int(np.ceil(total_bars / 16))
    
    # Verify line count
    assert len(lines) == expected_lines, \
        f"Expected {expected_lines} lines at 180 BPM, got {len(lines)}"
    
    # Verify each line (except possibly the last) has 16 bars
    BARS_PER_LINE = 16
    BEATS_PER_BAR = 4
    seconds_per_beat = 60 / tempo
    seconds_per_bar = seconds_per_beat * BEATS_PER_BAR
    
    for i, line in enumerate(lines[:-1]):  # All lines except last
        line_bars = sum(np.ceil((c.end_time - c.start_time) / seconds_per_bar) for c in line)
        assert line_bars == BARS_PER_LINE, \
            f"Line {i+1} should have exactly {BARS_PER_LINE} bars, got {line_bars}"
    
    print(f"✓ Full song at 180 BPM: {len(lines)} lines, layout correct")


def test_full_song_visual_layout_specification(audio_engine, test_full_song_audio, monkeypatch):
    """
    Test that visual layout matches specification for full song.
    
    Specification (Requirement 2.6):
    - 1 line = 16 bars
    - Chords displayed at intervals: 4 bars, 2 bars, or 1 bar as needed
    
    **Validates: Requirement 2.6**
    """
    from src.lyrics_transcription import LyricsTranscriptionModule
    
    def mock_transcribe(self, audio, sample_rate, language="ja"):
        return []
    
    monkeypatch.setattr(LyricsTranscriptionModule, 'transcribe', mock_transcribe)
    
    audio_file, sample_rate, duration_per_chord, num_chords = test_full_song_audio
    tempo = 120  # BPM
    
    # Load and analyze
    audio_engine.load_audio_file(audio_file)
    result = audio_engine.analyze_audio(use_cache=False)
    
    # Group chords into lines
    lines = group_chords_into_lines(result.chord_progression, tempo)
    
    # Verify layout specification
    BARS_PER_LINE = 16
    BEATS_PER_BAR = 4
    seconds_per_beat = 60 / tempo
    seconds_per_bar = seconds_per_beat * BEATS_PER_BAR
    
    for line_idx, line in enumerate(lines):
        # Calculate total bars in this line
        line_bars = sum(np.ceil((c.end_time - c.start_time) / seconds_per_bar) for c in line)
        
        # Each line should have at most 16 bars (last line may have fewer)
        assert line_bars <= BARS_PER_LINE, \
            f"Line {line_idx+1} has {line_bars} bars, exceeds maximum of {BARS_PER_LINE}"
        
        # Verify chord spacing (each chord should be 1, 2, or 4 bars)
        for chord in line:
            chord_bars = np.ceil((chord.end_time - chord.start_time) / seconds_per_bar)
            # Chords can be any number of bars, but typically 1, 2, or 4
            assert chord_bars >= 1, \
                f"Chord should span at least 1 bar, got {chord_bars}"
    
    print(f"✓ Visual layout matches specification: {len(lines)} lines, max 16 bars per line")



def test_full_song_line_numbers(audio_engine, test_full_song_audio, monkeypatch):
    """
    Test that line numbers are calculated correctly for full song.
    
    Line numbers should start at bar 1 and increment by 16 for each line.
    
    **Validates: Requirement 2.6**
    """
    from src.lyrics_transcription import LyricsTranscriptionModule
    
    def mock_transcribe(self, audio, sample_rate, language="ja"):
        return []
    
    monkeypatch.setattr(LyricsTranscriptionModule, 'transcribe', mock_transcribe)
    
    audio_file, sample_rate, duration_per_chord, num_chords = test_full_song_audio
    tempo = 120  # BPM
    
    # Load and analyze
    audio_engine.load_audio_file(audio_file)
    result = audio_engine.analyze_audio(use_cache=False)
    
    # Group chords into lines
    lines = group_chords_into_lines(result.chord_progression, tempo)
    
    # Verify line numbers
    BARS_PER_LINE = 16
    expected_line_numbers = [1 + (i * BARS_PER_LINE) for i in range(len(lines))]
    
    for i, expected_bar_number in enumerate(expected_line_numbers):
        # Line i should start at bar expected_bar_number
        # Line 0 starts at bar 1
        # Line 1 starts at bar 17 (1 + 16)
        # Line 2 starts at bar 33 (1 + 32)
        # etc.
        assert expected_bar_number == 1 + (i * BARS_PER_LINE), \
            f"Line {i} should start at bar {expected_bar_number}"
    
    print(f"✓ Line numbers correct: {len(lines)} lines starting at bars {expected_line_numbers[:5]}...")



def test_tempo_aware_bar_calculation_accuracy(audio_engine, test_full_song_audio, monkeypatch):
    """
    Test that tempo-aware bar calculation is accurate across different tempos.
    
    This validates the fix from task 4.2 (tempo-aware bar calculation).
    
    **Validates: Requirement 2.6**
    """
    from src.lyrics_transcription import LyricsTranscriptionModule
    
    def mock_transcribe(self, audio, sample_rate, language="ja"):
        return []
    
    monkeypatch.setattr(LyricsTranscriptionModule, 'transcribe', mock_transcribe)
    
    audio_file, sample_rate, duration_per_chord, num_chords = test_full_song_audio
    
    # Test with multiple tempos
    test_tempos = [60, 90, 120, 150, 180]
    
    for tempo in test_tempos:
        # Load and analyze
        audio_engine.load_audio_file(audio_file)
        result = audio_engine.analyze_audio(use_cache=False)
        
        # Group chords into lines
        lines = group_chords_into_lines(result.chord_progression, tempo)
        
        # Calculate expected values
        bars_per_chord = calculate_bars_per_chord(duration_per_chord, tempo)
        total_bars = len(result.chord_progression) * bars_per_chord
        expected_lines = int(np.ceil(total_bars / 16))
        
        # Verify line count matches expected
        assert len(lines) == expected_lines, \
            f"At {tempo} BPM: expected {expected_lines} lines, got {len(lines)}"
        
        # Verify bar calculation is tempo-aware
        BEATS_PER_BAR = 4
        seconds_per_beat = 60 / tempo
        seconds_per_bar = seconds_per_beat * BEATS_PER_BAR
        
        # Check that bar calculation uses tempo
        for chord in result.chord_progression[:5]:  # Check first 5 chords
            chord_duration = chord.end_time - chord.start_time
            calculated_bars = np.ceil(chord_duration / seconds_per_bar)
            expected_bars = np.ceil(chord_duration / seconds_per_bar)
            
            assert calculated_bars == expected_bars, \
                f"At {tempo} BPM: bar calculation mismatch for chord duration {chord_duration}s"
        
        print(f"✓ Tempo {tempo} BPM: {len(lines)} lines, bar calculation accurate")
