"""Integration test for full lyrics transcription pipeline - Task 6.2

Tests the complete lyrics pipeline: Load audio → transcribe → display Japanese text correctly
Verifies end-to-end lyrics transcription preserves UTF-8 encoding

Validates Requirement: 2.7
"""

import pytest
import numpy as np
from pathlib import Path
import soundfile as sf
from unittest.mock import patch, Mock

from src.audio_engine import AudioProcessingEngine
from src.lyrics_transcription import LyricsTranscriptionModule
from src.models import LyricSegment


@pytest.fixture
def test_audio_with_japanese_speech(tmp_path):
    """Create test audio file with synthesized speech-like audio
    
    Note: We'll mock the Whisper transcription to return Japanese text,
    but we need real audio for the pipeline to process.
    """
    sample_rate = 22050
    duration = 3.0
    
    # Generate speech-like audio (varying frequencies to simulate speech)
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create a simple speech-like waveform with varying pitch
    audio = np.zeros_like(t)
    
    # Add fundamental frequency and harmonics (simulating voice)
    f0 = 200  # Base frequency (Hz)
    for harmonic in range(1, 6):
        freq = f0 * harmonic
        amplitude = 0.2 / harmonic  # Decreasing amplitude for higher harmonics
        audio += amplitude * np.sin(2 * np.pi * freq * t)
    
    # Add some variation to simulate speech prosody
    modulation = 1 + 0.3 * np.sin(2 * np.pi * 2 * t)
    audio = audio * modulation
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # Save as WAV file
    audio_file = tmp_path / "japanese_speech.wav"
    sf.write(str(audio_file), audio, sample_rate)
    
    return audio_file, sample_rate


@pytest.fixture
def audio_engine(tmp_path):
    """Create AudioProcessingEngine with test cache directory"""
    cache_dir = tmp_path / "cache"
    return AudioProcessingEngine(cache_dir=cache_dir)


def test_full_lyrics_pipeline_japanese_text_preservation(audio_engine, test_audio_with_japanese_speech):
    """Test full pipeline preserves Japanese text "春の風が吹く"
    
    This test verifies the complete lyrics transcription pipeline:
    1. Load audio file
    2. Transcribe with Whisper (mocked to return Japanese text)
    3. Verify all Japanese characters are preserved in the result
    
    Validates Requirement: 2.7
    """
    audio_file, sample_rate = test_audio_with_japanese_speech
    
    # Expected Japanese text
    expected_text = "春の風が吹く"
    
    # Create mock segments that will be returned
    from src.models import LyricSegment
    mock_segments = [
        LyricSegment(
            start_time=0.0,
            end_time=3.0,
            text=expected_text,
            confidence=0.9
        )
    ]
    
    # Load audio
    audio_engine.load_audio_file(audio_file)
    
    # Mock the transcribe method to return Japanese text
    with patch.object(LyricsTranscriptionModule, 'transcribe', return_value=mock_segments):
        # Perform full analysis (this will call lyrics transcription)
        result = audio_engine.analyze_audio(use_cache=False)
    
    # Verify lyrics were transcribed
    assert result is not None, "Analysis result should not be None"
    assert hasattr(result, 'lyrics'), "Result should have lyrics attribute"
    assert isinstance(result.lyrics, list), "Lyrics should be a list"
    assert len(result.lyrics) > 0, "Should have transcribed lyrics"
    
    # Get the transcribed text
    transcribed_text = result.lyrics[0].text
    
    # Verify all Japanese characters are preserved
    assert expected_text in transcribed_text, \
        f"Expected '{expected_text}' in transcribed text, got '{transcribed_text}'"
    
    # Verify specific Japanese characters
    expected_chars = ['春', 'の', '風', 'が', '吹', 'く']
    for char in expected_chars:
        assert char in transcribed_text, \
            f"Japanese character '{char}' missing from transcribed text '{transcribed_text}'"


def test_full_lyrics_pipeline_mixed_japanese_characters(audio_engine, test_audio_with_japanese_speech):
    """Test full pipeline preserves mixed Japanese text (hiragana, katakana, kanji)
    
    Validates Requirement: 2.7
    """
    audio_file, sample_rate = test_audio_with_japanese_speech
    
    # Mixed Japanese text: kanji (春, 吹), hiragana (の, が, く), katakana (カゼ)
    expected_text = "春のカゼが吹く"
    
    from src.models import LyricSegment
    mock_segments = [
        LyricSegment(
            start_time=0.0,
            end_time=3.0,
            text=expected_text,
            confidence=0.9
        )
    ]
    
    audio_engine.load_audio_file(audio_file)
    
    with patch.object(LyricsTranscriptionModule, 'transcribe', return_value=mock_segments):
        result = audio_engine.analyze_audio(use_cache=False)
    
    assert len(result.lyrics) > 0, "Should have transcribed lyrics"
    transcribed_text = result.lyrics[0].text
    
    # Verify all character types are preserved
    assert '春' in transcribed_text, f"Kanji '春' missing from '{transcribed_text}'"
    assert 'の' in transcribed_text, f"Hiragana 'の' missing from '{transcribed_text}'"
    assert 'カ' in transcribed_text, f"Katakana 'カ' missing from '{transcribed_text}'"
    assert 'ゼ' in transcribed_text, f"Katakana 'ゼ' missing from '{transcribed_text}'"
    assert 'が' in transcribed_text, f"Hiragana 'が' missing from '{transcribed_text}'"
    assert '吹' in transcribed_text, f"Kanji '吹' missing from '{transcribed_text}'"
    assert 'く' in transcribed_text, f"Hiragana 'く' missing from '{transcribed_text}'"


def test_full_lyrics_pipeline_multiple_segments(audio_engine, test_audio_with_japanese_speech):
    """Test full pipeline preserves Japanese text across multiple segments
    
    Validates Requirement: 2.7
    """
    audio_file, sample_rate = test_audio_with_japanese_speech
    
    # Multiple segments with Japanese text
    segments_data = [
        (0.0, 1.0, "春の風が"),
        (1.0, 2.0, "吹いている"),
        (2.0, 3.0, "今日も")
    ]
    
    from src.models import LyricSegment
    mock_segments = [
        LyricSegment(
            start_time=start,
            end_time=end,
            text=text,
            confidence=0.9
        )
        for start, end, text in segments_data
    ]
    
    audio_engine.load_audio_file(audio_file)
    
    with patch.object(LyricsTranscriptionModule, 'transcribe', return_value=mock_segments):
        result = audio_engine.analyze_audio(use_cache=False)
    
    # Verify all segments are present
    assert len(result.lyrics) == 3, f"Expected 3 segments, got {len(result.lyrics)}"
    
    # Verify each segment preserves Japanese text
    for i, (start, end, expected_text) in enumerate(segments_data):
        segment = result.lyrics[i]
        assert expected_text in segment.text, \
            f"Segment {i}: Expected '{expected_text}' in '{segment.text}'"
        
        # Verify timing
        assert segment.start_time == start, \
            f"Segment {i}: Expected start_time {start}, got {segment.start_time}"
        assert segment.end_time == end, \
            f"Segment {i}: Expected end_time {end}, got {segment.end_time}"


def test_full_lyrics_pipeline_not_only_n_character(audio_engine, test_audio_with_japanese_speech):
    """Test that the bug (only "ん" displayed) is fixed
    
    This test specifically verifies the reported bug is fixed:
    - Bug: Only "ん" character was displayed
    - Fix: All Japanese characters are preserved
    
    Validates Requirement: 2.7
    """
    audio_file, sample_rate = test_audio_with_japanese_speech
    
    expected_text = "春の風が吹く"
    
    from src.models import LyricSegment
    mock_segments = [
        LyricSegment(
            start_time=0.0,
            end_time=3.0,
            text=expected_text,
            confidence=0.9
        )
    ]
    
    audio_engine.load_audio_file(audio_file)
    
    with patch.object(LyricsTranscriptionModule, 'transcribe', return_value=mock_segments):
        result = audio_engine.analyze_audio(use_cache=False)
    
    assert len(result.lyrics) > 0, "Should have transcribed lyrics"
    transcribed_text = result.lyrics[0].text
    
    # Verify it's NOT just "ん"
    assert transcribed_text != "ん", \
        f"Bug still present: only 'ん' is displayed instead of '{expected_text}'"
    
    # Verify text length is correct
    assert len(transcribed_text) >= len(expected_text), \
        f"Text too short: got '{transcribed_text}' (length {len(transcribed_text)}), " \
        f"expected '{expected_text}' (length {len(expected_text)})"
    
    # Verify it's not just "ん" repeated
    assert transcribed_text != "ん" * len(transcribed_text), \
        f"Bug still present: only 'ん' characters, expected '{expected_text}'"
    
    # Verify the actual expected text
    assert expected_text == transcribed_text, \
        f"Expected '{expected_text}', got '{transcribed_text}'"


def test_full_lyrics_pipeline_utf8_encoding_preserved(audio_engine, test_audio_with_japanese_speech):
    """Test that UTF-8 encoding is preserved throughout the pipeline
    
    Validates Requirement: 2.7
    """
    audio_file, sample_rate = test_audio_with_japanese_speech
    
    # Use text with various UTF-8 characters
    expected_text = "春の風が吹く🎵"  # Including emoji to test full UTF-8 support
    
    from src.models import LyricSegment
    mock_segments = [
        LyricSegment(
            start_time=0.0,
            end_time=3.0,
            text=expected_text,
            confidence=0.9
        )
    ]
    
    audio_engine.load_audio_file(audio_file)
    
    with patch.object(LyricsTranscriptionModule, 'transcribe', return_value=mock_segments):
        result = audio_engine.analyze_audio(use_cache=False)
    
    assert len(result.lyrics) > 0, "Should have transcribed lyrics"
    transcribed_text = result.lyrics[0].text
    
    # Verify UTF-8 encoding is preserved
    assert expected_text == transcribed_text, \
        f"UTF-8 encoding not preserved: expected '{expected_text}', got '{transcribed_text}'"
    
    # Verify we can encode/decode as UTF-8 without errors
    try:
        encoded = transcribed_text.encode('utf-8')
        decoded = encoded.decode('utf-8')
        assert decoded == transcribed_text, "UTF-8 round-trip failed"
    except UnicodeEncodeError as e:
        pytest.fail(f"UTF-8 encoding failed: {e}")
    except UnicodeDecodeError as e:
        pytest.fail(f"UTF-8 decoding failed: {e}")


def test_full_lyrics_pipeline_confidence_scores(audio_engine, test_audio_with_japanese_speech):
    """Test that lyrics segments include confidence scores
    
    Validates Requirement: 2.7 (complete lyrics functionality)
    """
    audio_file, sample_rate = test_audio_with_japanese_speech
    
    expected_text = "春の風が吹く"
    expected_confidence = 0.8
    
    from src.models import LyricSegment
    mock_segments = [
        LyricSegment(
            start_time=0.0,
            end_time=3.0,
            text=expected_text,
            confidence=expected_confidence
        )
    ]
    
    audio_engine.load_audio_file(audio_file)
    
    with patch.object(LyricsTranscriptionModule, 'transcribe', return_value=mock_segments):
        result = audio_engine.analyze_audio(use_cache=False)
    
    assert len(result.lyrics) > 0, "Should have transcribed lyrics"
    
    # Verify confidence score
    segment = result.lyrics[0]
    assert hasattr(segment, 'confidence'), "Segment should have confidence attribute"
    assert 0.0 <= segment.confidence <= 1.0, \
        f"Confidence should be between 0 and 1, got {segment.confidence}"
    
    # Verify confidence value
    assert abs(segment.confidence - expected_confidence) < 0.01, \
        f"Expected confidence {expected_confidence}, got {segment.confidence}"


def test_full_lyrics_pipeline_timing_accuracy(audio_engine, test_audio_with_japanese_speech):
    """Test that lyrics segments have accurate timing information
    
    Validates Requirement: 2.7 (complete lyrics functionality)
    """
    audio_file, sample_rate = test_audio_with_japanese_speech
    
    segments_data = [
        (0.0, 1.5, "春の風が"),
        (1.5, 3.0, "吹いている")
    ]
    
    from src.models import LyricSegment
    mock_segments = [
        LyricSegment(
            start_time=start,
            end_time=end,
            text=text,
            confidence=0.9
        )
        for start, end, text in segments_data
    ]
    
    audio_engine.load_audio_file(audio_file)
    
    with patch.object(LyricsTranscriptionModule, 'transcribe', return_value=mock_segments):
        result = audio_engine.analyze_audio(use_cache=False)
    
    assert len(result.lyrics) == 2, f"Expected 2 segments, got {len(result.lyrics)}"
    
    # Verify timing for each segment
    for i, (expected_start, expected_end, expected_text) in enumerate(segments_data):
        segment = result.lyrics[i]
        
        assert segment.start_time == expected_start, \
            f"Segment {i}: Expected start_time {expected_start}, got {segment.start_time}"
        assert segment.end_time == expected_end, \
            f"Segment {i}: Expected end_time {expected_end}, got {segment.end_time}"
        
        # Verify duration is positive
        duration = segment.end_time - segment.start_time
        assert duration > 0, \
            f"Segment {i}: Duration should be positive, got {duration}"


def test_full_lyrics_pipeline_empty_audio(audio_engine, tmp_path):
    """Test pipeline handles audio with no speech gracefully
    
    Validates Requirement: 2.7 (robust lyrics functionality)
    """
    # Create silent audio
    sample_rate = 22050
    duration = 2.0
    audio = np.zeros(int(sample_rate * duration), dtype=np.float32)
    
    audio_file = tmp_path / "silent.wav"
    sf.write(str(audio_file), audio, sample_rate)
    
    # Mock Whisper to return no segments (no speech detected)
    mock_result = {
        'text': '',
        'segments': []
    }
    
    audio_engine.load_audio_file(audio_file)
    
    with patch.object(LyricsTranscriptionModule, '_load_model'):
        with patch.object(LyricsTranscriptionModule, 'model', create=True) as mock_model:
            mock_model.transcribe = Mock(return_value=mock_result)
            result = audio_engine.analyze_audio(use_cache=False)
    
    # Should return empty lyrics list, not crash
    assert result is not None, "Result should not be None"
    assert hasattr(result, 'lyrics'), "Result should have lyrics attribute"
    assert isinstance(result.lyrics, list), "Lyrics should be a list"
    assert len(result.lyrics) == 0, "Should have no lyrics for silent audio"


def test_full_lyrics_pipeline_language_parameter(audio_engine, test_audio_with_japanese_speech):
    """Test that language parameter is correctly passed to Whisper
    
    Validates Requirement: 2.7 (proper Japanese language support)
    """
    audio_file, sample_rate = test_audio_with_japanese_speech
    
    expected_text = "春の風が吹く"
    
    from src.models import LyricSegment
    mock_segments = [
        LyricSegment(
            start_time=0.0,
            end_time=3.0,
            text=expected_text,
            confidence=0.9
        )
    ]
    
    audio_engine.load_audio_file(audio_file)
    
    # Create a mock that we can inspect
    mock_transcribe = Mock(return_value=mock_segments)
    
    with patch.object(LyricsTranscriptionModule, 'transcribe', mock_transcribe):
        result = audio_engine.analyze_audio(use_cache=False)
    
    # Verify Whisper was called with Japanese language parameter
    assert mock_transcribe.called, "Whisper transcribe should be called"
    
    # Get the call arguments
    call_args = mock_transcribe.call_args
    
    # Verify language parameter was passed
    assert 'language' in call_args.kwargs, "Language parameter should be passed"
    assert call_args.kwargs['language'] == 'ja', \
        f"Expected language='ja', got language='{call_args.kwargs['language']}'"
