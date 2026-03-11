# Debug Logging Guide for Lyrics Transcription

## Overview

Debug logging has been added to the lyrics transcription module to help identify where text corruption might occur during the processing pipeline. This is particularly useful for debugging encoding issues with Japanese or other non-ASCII text.

## What is Logged

The debug logging captures text at three critical stages:

1. **Raw Whisper Output**: The text exactly as returned by the Whisper model before any processing
2. **After `.strip()` Operation**: The text after whitespace trimming
3. **Final LyricSegment Text**: The text as stored in the final LyricSegment object

Each log entry includes:
- The text in Python's `repr()` format (showing escape sequences)
- The UTF-8 byte representation (showing actual byte values)

## How to Enable Debug Logging

### Option 1: Enable for All Modules

Set the logging level to DEBUG before running your code:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now run your code
from src.audio_engine import AudioEngine
engine = AudioEngine()
result = engine.analyze_audio("path/to/audio.mp3")
```

### Option 2: Enable Only for Lyrics Transcription Module

Enable debug logging only for the lyrics transcription module:

```python
import logging

# Enable debug logging only for lyrics transcription
logger = logging.getLogger('src.lyrics_transcription')
logger.setLevel(logging.DEBUG)

# Add a handler to see the output
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Now run your code
from src.audio_engine import AudioEngine
engine = AudioEngine()
result = engine.analyze_audio("path/to/audio.mp3")
```

### Option 3: Enable via Environment Variable

Set the `PYTHONVERBOSE` environment variable:

```bash
export PYTHONVERBOSE=1
python your_script.py
```

## Example Output

When processing Japanese lyrics "春の風が吹く", you'll see output like:

```
DEBUG:src.lyrics_transcription:[DEBUG] Raw Whisper output: '  春の風が吹く  ' (bytes: b'  \xe6\x98\xa5\xe3\x81\xae\xe9\xa2\xa8\xe3\x81\x8c\xe5\x90\xb9\xe3\x81\x8f  ')
DEBUG:src.lyrics_transcription:[DEBUG] After strip(): '春の風が吹く' (bytes: b'\xe6\x98\xa5\xe3\x81\xae\xe9\xa2\xa8\xe3\x81\x8c\xe5\x90\xb9\xe3\x81\x8f')
DEBUG:src.lyrics_transcription:[DEBUG] Final LyricSegment text: '春の風が吹く' (bytes: b'\xe6\x98\xa5\xe3\x81\xae\xe9\xa2\xa8\xe3\x81\x8c\xe5\x90\xb9\xe3\x81\x8f')
```

## Interpreting the Output

### Normal Behavior (No Corruption)

If text is preserved correctly, you should see:
- All three stages show the same text (after strip removes whitespace)
- Byte representation shows valid UTF-8 sequences
- No unexpected characters or escape sequences

### Detecting Corruption

If text corruption occurs, you'll see differences between stages:

**Example 1: Corruption during strip()**
```
DEBUG: Raw Whisper output: '春の風が吹く' (bytes: b'\xe6\x98\xa5...')
DEBUG: After strip(): 'ん' (bytes: b'\xe3\x82\x93')  ← CORRUPTION HERE
DEBUG: Final LyricSegment text: 'ん' (bytes: b'\xe3\x82\x93')
```

**Example 2: Corruption in LyricSegment creation**
```
DEBUG: Raw Whisper output: '春の風が吹く' (bytes: b'\xe6\x98\xa5...')
DEBUG: After strip(): '春の風が吹く' (bytes: b'\xe6\x98\xa5...')
DEBUG: Final LyricSegment text: '???' (bytes: b'\x3f\x3f\x3f')  ← CORRUPTION HERE
```

### Understanding Byte Representations

UTF-8 encoding uses multiple bytes for non-ASCII characters:
- ASCII characters: 1 byte (e.g., 'A' = `\x41`)
- Japanese hiragana/katakana: 3 bytes (e.g., 'あ' = `\xe3\x81\x82`)
- Japanese kanji: 3 bytes (e.g., '春' = `\xe6\x98\xa5`)

If you see:
- `\x3f` (question mark): Character couldn't be encoded
- `\xef\xbf\xbd` (replacement character): Invalid UTF-8 sequence
- Truncated sequences: Incomplete multi-byte characters

## Troubleshooting

### Issue: No debug logs appear

**Solution**: Make sure logging is configured before importing the module:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Do this FIRST

from src.lyrics_transcription import LyricsTranscriptionModule  # Then import
```

### Issue: Too much debug output

**Solution**: Use a more specific logger:

```python
import logging

# Only show debug logs from lyrics transcription
logging.basicConfig(level=logging.INFO)  # Default to INFO
lyrics_logger = logging.getLogger('src.lyrics_transcription')
lyrics_logger.setLevel(logging.DEBUG)
```

### Issue: Debug logs in production

**Solution**: Debug logging is disabled by default (only INFO and above are shown). To ensure it stays disabled:

```python
import logging

# Explicitly set to INFO or higher
logging.basicConfig(level=logging.INFO)
```

## Related Files

- **Implementation**: `src/lyrics_transcription.py` (lines 85-115)
- **Tests**: `tests/test_debug_logging.py`
- **Bug Fix**: Task 5.1 fixed the root cause in `src-tauri/src/main.rs`

## When to Use Debug Logging

Use debug logging when:
- Investigating text encoding issues
- Verifying UTF-8 preservation through the pipeline
- Debugging unexpected character corruption
- Testing with new languages or character sets
- Troubleshooting Whisper model output

## Performance Impact

Debug logging has minimal performance impact:
- Only active when logging level is set to DEBUG
- Uses Python's built-in logging (efficient)
- Byte representation is computed only when logging is enabled
- No impact on production deployments (INFO level by default)

## Note

The root cause of the Japanese lyrics bug was fixed in Task 5.1 by adding `ensure_ascii=False` to the JSON serialization in the Tauri backend. This debug logging is now primarily useful for:
- Verifying the fix works correctly
- Debugging future encoding issues
- Understanding the text processing pipeline
- Troubleshooting other language support
