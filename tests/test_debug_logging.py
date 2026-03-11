"""Test debug logging in lyrics transcription module"""

import pytest
import numpy as np
import logging
from unittest.mock import Mock, patch, MagicMock
from src.lyrics_transcription import LyricsTranscriptionModule


def test_debug_logging_captures_text_at_all_stages(caplog):
    """
    Test that debug logging captures text at all three stages:
    1. Raw Whisper output
    2. After strip() operation
    3. Final LyricSegment text
    """
    # Create module
    module = LyricsTranscriptionModule(model_size="base")
    
    # Mock Whisper model
    mock_model = Mock()
    mock_result = {
        'text': '春の風が吹く',
        'segments': [
            {
                'text': '  春の風が吹く  ',  # With whitespace to test strip()
                'start': 0.0,
                'end': 2.5,
                'no_speech_prob': 0.1
            }
        ]
    }
    mock_model.transcribe.return_value = mock_result
    module.model = mock_model
    
    # Create test audio
    audio = np.random.randn(16000).astype(np.float32) * 0.1
    
    # Enable debug logging
    with caplog.at_level(logging.DEBUG):
        segments = module.transcribe(audio, 16000, language="ja")
    
    # Verify segments were created
    assert len(segments) == 1
    assert segments[0].text == '春の風が吹く'
    
    # Verify debug logs were captured
    debug_logs = [record.message for record in caplog.records if record.levelname == 'DEBUG']
    
    # Should have 3 debug logs per segment
    assert len(debug_logs) == 3
    
    # Check raw Whisper output log
    assert '[DEBUG] Raw Whisper output:' in debug_logs[0]
    assert '春の風が吹く' in debug_logs[0]
    
    # Check after strip() log
    assert '[DEBUG] After strip():' in debug_logs[1]
    assert '春の風が吹く' in debug_logs[1]
    
    # Check final LyricSegment log
    assert '[DEBUG] Final LyricSegment text:' in debug_logs[2]
    assert '春の風が吹く' in debug_logs[2]


def test_debug_logging_shows_byte_representation(caplog):
    """
    Test that debug logging includes byte representation to help identify encoding issues
    """
    # Create module
    module = LyricsTranscriptionModule(model_size="base")
    
    # Mock Whisper model
    mock_model = Mock()
    mock_result = {
        'text': 'テスト',
        'segments': [
            {
                'text': 'テスト',
                'start': 0.0,
                'end': 1.0,
                'no_speech_prob': 0.05
            }
        ]
    }
    mock_model.transcribe.return_value = mock_result
    module.model = mock_model
    
    # Create test audio
    audio = np.random.randn(16000).astype(np.float32) * 0.1
    
    # Enable debug logging
    with caplog.at_level(logging.DEBUG):
        segments = module.transcribe(audio, 16000, language="ja")
    
    # Verify debug logs include byte representation
    debug_logs = [record.message for record in caplog.records if record.levelname == 'DEBUG']
    
    # Each debug log should contain "(bytes: b'...')"
    for log in debug_logs:
        assert '(bytes:' in log
        assert "b'" in log


def test_debug_logging_with_multiple_segments(caplog):
    """
    Test that debug logging works correctly with multiple segments
    """
    # Create module
    module = LyricsTranscriptionModule(model_size="base")
    
    # Mock Whisper model with multiple segments
    mock_model = Mock()
    mock_result = {
        'text': '春の風 夏の雨',
        'segments': [
            {
                'text': '春の風',
                'start': 0.0,
                'end': 1.5,
                'no_speech_prob': 0.1
            },
            {
                'text': '夏の雨',
                'start': 1.5,
                'end': 3.0,
                'no_speech_prob': 0.15
            }
        ]
    }
    mock_model.transcribe.return_value = mock_result
    module.model = mock_model
    
    # Create test audio
    audio = np.random.randn(16000).astype(np.float32) * 0.1
    
    # Enable debug logging
    with caplog.at_level(logging.DEBUG):
        segments = module.transcribe(audio, 16000, language="ja")
    
    # Verify segments were created
    assert len(segments) == 2
    
    # Verify debug logs were captured (3 logs per segment = 6 total)
    debug_logs = [record.message for record in caplog.records if record.levelname == 'DEBUG']
    assert len(debug_logs) == 6
    
    # Verify both segments are logged
    all_debug_text = ' '.join(debug_logs)
    assert '春の風' in all_debug_text
    assert '夏の雨' in all_debug_text
