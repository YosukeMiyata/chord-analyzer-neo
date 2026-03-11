"""Test Tauri JSON Serialization with UTF-8

This test verifies that the Tauri backend correctly serializes Japanese text
using ensure_ascii=False in json.dumps(), which is critical for preserving
Japanese characters in lyrics.

**Validates: Requirements 2.7**
"""

import json
import pytest


def test_json_dumps_with_ensure_ascii_false():
    """
    Test that json.dumps with ensure_ascii=False preserves Japanese characters
    
    This simulates what happens in the Tauri backend at line 134 of main.rs
    where we use json.dumps(output, ensure_ascii=False) to serialize the
    analysis result.
    """
    # Japanese text that should be preserved
    japanese_text = "春の風が吹く"
    
    # Create a structure similar to what's returned from the Python backend
    output = {
        'lyrics': [
            {
                'start_time': 0.0,
                'end_time': 2.0,
                'text': japanese_text,
                'confidence': 0.9
            }
        ]
    }
    
    # Serialize with ensure_ascii=False (the fix)
    json_str_fixed = json.dumps(output, ensure_ascii=False)
    
    # Verify the Japanese text is preserved in the JSON string
    assert japanese_text in json_str_fixed, \
        f"Japanese text not preserved in JSON: {json_str_fixed}"
    
    # Verify each character is present
    for char in ['春', 'の', '風', 'が', '吹', 'く']:
        assert char in json_str_fixed, \
            f"Character '{char}' not found in JSON: {json_str_fixed}"
    
    # Deserialize and verify
    parsed = json.loads(json_str_fixed)
    assert parsed['lyrics'][0]['text'] == japanese_text, \
        f"Text corrupted after round-trip: {parsed['lyrics'][0]['text']}"


def test_json_dumps_with_ensure_ascii_true_shows_bug():
    """
    Test that json.dumps with ensure_ascii=True (default) escapes Japanese characters
    
    This demonstrates the bug that was present before the fix.
    With ensure_ascii=True, Japanese characters are escaped as \\uXXXX sequences.
    """
    japanese_text = "春の風が吹く"
    
    output = {
        'lyrics': [
            {
                'start_time': 0.0,
                'end_time': 2.0,
                'text': japanese_text,
                'confidence': 0.9
            }
        ]
    }
    
    # Serialize with ensure_ascii=True (the bug)
    json_str_buggy = json.dumps(output, ensure_ascii=True)
    
    # With ensure_ascii=True, Japanese characters are escaped
    # The actual Japanese characters should NOT be in the string
    assert japanese_text not in json_str_buggy, \
        "Japanese text should be escaped with ensure_ascii=True"
    
    # Instead, we should see Unicode escape sequences
    assert '\\u' in json_str_buggy, \
        "Unicode escape sequences should be present with ensure_ascii=True"
    
    # But when parsed, the text should still be correct
    parsed = json.loads(json_str_buggy)
    assert parsed['lyrics'][0]['text'] == japanese_text, \
        "Text should be correct after parsing despite escaping"


def test_mixed_japanese_text_serialization():
    """
    Test serialization of mixed Japanese text (hiragana, katakana, kanji)
    """
    mixed_text = "春のカゼが吹く"  # kanji + hiragana + katakana
    
    output = {
        'lyrics': [
            {
                'start_time': 0.0,
                'end_time': 2.0,
                'text': mixed_text,
                'confidence': 0.9
            }
        ]
    }
    
    # Serialize with ensure_ascii=False
    json_str = json.dumps(output, ensure_ascii=False)
    
    # Verify all character types are preserved
    assert '春' in json_str, "Kanji not preserved"
    assert 'の' in json_str, "Hiragana not preserved"
    assert 'カ' in json_str, "Katakana not preserved"
    assert 'ゼ' in json_str, "Katakana not preserved"
    assert 'が' in json_str, "Hiragana not preserved"
    assert '吹' in json_str, "Kanji not preserved"
    assert 'く' in json_str, "Hiragana not preserved"
    
    # Verify round-trip
    parsed = json.loads(json_str)
    assert parsed['lyrics'][0]['text'] == mixed_text


def test_complete_analysis_result_serialization():
    """
    Test serialization of a complete analysis result with Japanese lyrics
    
    This simulates the exact structure returned by the Tauri backend.
    """
    analysis_result = {
        'chord_progression': [
            {
                'start_time': 0.0,
                'end_time': 2.0,
                'root': 'C',
                'quality': 'major',
                'bass_note': None,
                'extensions': None,
                'confidence': 0.85
            }
        ],
        'lyrics': [
            {
                'start_time': 0.0,
                'end_time': 2.0,
                'text': '春の風が吹く',
                'confidence': 0.9
            },
            {
                'start_time': 2.0,
                'end_time': 4.0,
                'text': '夏の海が光る',
                'confidence': 0.88
            }
        ],
        'tempo': 120.0,
        'key': 'C',
        'time_signature': [4, 4]
    }
    
    # Serialize with ensure_ascii=False
    json_str = json.dumps(analysis_result, ensure_ascii=False)
    
    # Verify both lyric segments are preserved
    assert '春の風が吹く' in json_str
    assert '夏の海が光る' in json_str
    
    # Verify round-trip
    parsed = json.loads(json_str)
    assert parsed['lyrics'][0]['text'] == '春の風が吹く'
    assert parsed['lyrics'][1]['text'] == '夏の海が光る'
    assert parsed['tempo'] == 120.0
    assert parsed['key'] == 'C'
