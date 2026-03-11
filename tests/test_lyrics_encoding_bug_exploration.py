"""Bug Condition Exploration Test for Lyrics Encoding

This test is designed to FAIL on unfixed code to surface counterexamples
that demonstrate the lyrics encoding bug. The goal is to confirm the root
cause analysis before implementing fixes.

EXPECTED OUTCOME: Test FAILS on unfixed code
- Japanese lyrics "春の風が吹く" are NOT fully displayed
- Only "ん" character is displayed
- Other Japanese characters (春, の, 風, が, 吹, く) are lost

The bug is that UTF-8 encoding is not properly handled somewhere in the
lyrics transcription pipeline, causing non-ASCII characters to be corrupted
or stripped.

**Validates: Requirements 2.7**
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.lyrics_transcription import LyricsTranscriptionModule


@pytest.fixture
def lyrics_module():
    """Create LyricsTranscriptionModule instance"""
    return LyricsTranscriptionModule(model_size="tiny")


def generate_silent_audio(duration: float = 2.0, sample_rate: int = 22050) -> np.ndarray:
    """
    Generate silent audio for testing
    
    Note: Since we're testing encoding, not actual transcription accuracy,
    we use silent audio. The Whisper model will be mocked or we'll test
    the text processing directly.
    
    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        Silent audio signal as numpy array
    """
    return np.zeros(int(sample_rate * duration), dtype=np.float32)


def test_japanese_lyrics_encoding():
    """
    Test that Japanese lyrics "春の風が吹く" are fully preserved
    
    This test processes Japanese text through the lyrics transcription module
    and verifies that all Japanese characters are preserved without corruption.
    
    Expected Japanese text: "春の風が吹く" (haru no kaze ga fuku - "spring wind blows")
    
    EXPECTED ON UNFIXED CODE: Fails - only "ん" is displayed
    EXPECTED ON FIXED CODE: Passes - all characters "春の風が吹く" are displayed
    
    Note: This test will need to be adapted based on how we can inject
    Japanese text into the transcription pipeline. Options:
    1. Mock the Whisper model to return Japanese text
    2. Use actual Japanese audio (if available)
    3. Test the text processing directly
    """
    # Japanese text we expect to see
    expected_text = "春の風が吹く"
    
    # For this exploration test, we'll mock the Whisper transcription
    # to return Japanese text and verify it's preserved
    lyrics_module = LyricsTranscriptionModule(model_size="tiny")
    
    # Generate silent audio (we'll mock the transcription)
    audio = generate_silent_audio(duration=2.0)
    sample_rate = 22050
    
    # Mock the Whisper model to return Japanese text
    # This simulates what Whisper would return for Japanese audio
    mock_result = {
        'text': expected_text,
        'segments': [
            {
                'start': 0.0,
                'end': 2.0,
                'text': expected_text,
                'no_speech_prob': 0.1
            }
        ]
    }
    
    with patch.object(lyrics_module, '_load_model'):
        lyrics_module.model = Mock()
        lyrics_module.model.transcribe = Mock(return_value=mock_result)
        
        # Transcribe with Japanese language
        segments = lyrics_module.transcribe(audio, sample_rate, language="ja")
    
    # Verify we got segments
    assert len(segments) > 0, "No lyric segments returned"
    
    # Get the transcribed text
    transcribed_text = segments[0].text
    
    # Check that all Japanese characters are preserved
    assert expected_text in transcribed_text, \
        f"Counterexample: Expected '{expected_text}' in transcribed text, got '{transcribed_text}'. " \
        f"Characters lost: {set(expected_text) - set(transcribed_text)}"
    
    # Check specific characters that should be present
    expected_chars = ['春', 'の', '風', 'が', '吹', 'く']
    missing_chars = [char for char in expected_chars if char not in transcribed_text]
    
    assert len(missing_chars) == 0, \
        f"Counterexample: Missing Japanese characters: {missing_chars}. " \
        f"Transcribed text: '{transcribed_text}'. " \
        f"Bug: UTF-8 encoding not properly handled, only 'ん' is displayed"


def test_japanese_lyrics_with_hiragana_katakana_kanji():
    """
    Test that mixed Japanese text (hiragana, katakana, kanji) is preserved
    
    This test uses a more comprehensive Japanese text with different character types
    to verify that all Japanese character encodings are handled correctly.
    
    Expected text: "春のカゼが吹く" (mixed kanji, hiragana, katakana)
    
    EXPECTED ON UNFIXED CODE: Fails - characters are corrupted or lost
    EXPECTED ON FIXED CODE: Passes - all characters are preserved
    """
    # Mixed Japanese text: kanji (春), hiragana (の, が, く), katakana (カゼ)
    expected_text = "春のカゼが吹く"
    
    lyrics_module = LyricsTranscriptionModule(model_size="tiny")
    audio = generate_silent_audio(duration=2.0)
    sample_rate = 22050
    
    mock_result = {
        'text': expected_text,
        'segments': [
            {
                'start': 0.0,
                'end': 2.0,
                'text': expected_text,
                'no_speech_prob': 0.1
            }
        ]
    }
    
    with patch.object(lyrics_module, '_load_model'):
        lyrics_module.model = Mock()
        lyrics_module.model.transcribe = Mock(return_value=mock_result)
        
        segments = lyrics_module.transcribe(audio, sample_rate, language="ja")
    
    assert len(segments) > 0, "No lyric segments returned"
    
    transcribed_text = segments[0].text
    
    # Verify all character types are preserved
    assert '春' in transcribed_text, f"Kanji '春' missing from '{transcribed_text}'"
    assert 'の' in transcribed_text, f"Hiragana 'の' missing from '{transcribed_text}'"
    assert 'カ' in transcribed_text, f"Katakana 'カ' missing from '{transcribed_text}'"
    assert 'ゼ' in transcribed_text, f"Katakana 'ゼ' missing from '{transcribed_text}'"
    assert 'が' in transcribed_text, f"Hiragana 'が' missing from '{transcribed_text}'"
    assert '吹' in transcribed_text, f"Kanji '吹' missing from '{transcribed_text}'"
    assert 'く' in transcribed_text, f"Hiragana 'く' missing from '{transcribed_text}'"
    
    assert expected_text == transcribed_text, \
        f"Counterexample: Expected '{expected_text}', got '{transcribed_text}'. " \
        f"Bug: UTF-8 encoding corrupts Japanese characters"


def test_japanese_lyrics_only_n_character_bug():
    """
    Test specifically for the reported bug: only "ん" character is displayed
    
    This test verifies the specific bug behavior where Japanese text is
    reduced to only the "ん" character.
    
    Expected text: "春の風が吹く"
    Buggy behavior: Only "ん" is displayed
    
    EXPECTED ON UNFIXED CODE: Fails - demonstrates the specific bug
    EXPECTED ON FIXED CODE: Passes - full text is preserved
    """
    expected_text = "春の風が吹く"
    
    lyrics_module = LyricsTranscriptionModule(model_size="tiny")
    audio = generate_silent_audio(duration=2.0)
    sample_rate = 22050
    
    mock_result = {
        'text': expected_text,
        'segments': [
            {
                'start': 0.0,
                'end': 2.0,
                'text': expected_text,
                'no_speech_prob': 0.1
            }
        ]
    }
    
    with patch.object(lyrics_module, '_load_model'):
        lyrics_module.model = Mock()
        lyrics_module.model.transcribe = Mock(return_value=mock_result)
        
        segments = lyrics_module.transcribe(audio, sample_rate, language="ja")
    
    assert len(segments) > 0, "No lyric segments returned"
    
    transcribed_text = segments[0].text
    
    # The bug is that ONLY "ん" is displayed, so the text should NOT be just "ん"
    assert transcribed_text != "ん", \
        f"Counterexample: Bug confirmed - only 'ん' is displayed instead of '{expected_text}'"
    
    # Verify the full text is present (not just "ん")
    assert len(transcribed_text) > 1, \
        f"Counterexample: Text too short ('{transcribed_text}'), expected '{expected_text}'"
    
    # Verify it's not just the "ん" character repeated
    assert transcribed_text != "ん" * len(transcribed_text), \
        f"Counterexample: Only 'ん' characters present, expected '{expected_text}'"
    
    # Verify the actual expected text
    assert expected_text == transcribed_text, \
        f"Counterexample: Expected '{expected_text}', got '{transcribed_text}'. " \
        f"Bug: UTF-8 encoding issue causes only 'ん' to be displayed"
