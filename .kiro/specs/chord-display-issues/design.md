# Chord Display Issues Bugfix Design

## Overview

This bugfix addresses seven critical issues in the chord analysis tool that prevent accurate chord and lyrics display. The primary issues are: (1) all chords being classified as major regardless of actual quality, (2) missing detection of minor chords, 7th notes, sus4 chords, and slash chord bass notes, (3) incorrect chord layout (not following 16 bars per line specification), and (4) lyrics displaying only "ん" character instead of full Japanese text. The fix strategy involves expanding chord templates to include all chord qualities, implementing proper chord quality detection logic, fixing the bar calculation in the visualization component, and ensuring proper UTF-8 encoding handling in the lyrics transcription module.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bugs - when chord estimation processes audio containing non-major chords (minor, 7th, sus4, slash) or when lyrics transcription processes Japanese text
- **Property (P)**: The desired behavior - chords should be classified with correct quality/extensions/bass notes, displayed in 16-bar lines, and lyrics should show all Japanese characters
- **Preservation**: Existing major chord detection, confidence scoring, click interactions, current playback highlighting, and vocal separation that must remain unchanged
- **ChordEstimationModule**: The class in `src/chord_estimation.py` that extracts chroma features and recognizes chords using template matching
- **_simple_chord_recognition**: The method that performs template matching to identify chords, currently only using major chord templates
- **ChordVisualization**: The React component in `src/components/ChordVisualization.tsx` that displays chord progressions in a timeline layout
- **LyricsTranscriptionModule**: The class in `src/lyrics_transcription.py` that uses Whisper to transcribe lyrics from audio
- **ChordQuality**: Enum defining chord types (MAJOR, MINOR, DIMINISHED, AUGMENTED, SUSPENDED)
- **Chroma Features**: 12-dimensional vector representing pitch class distribution in audio

## Bug Details

### Bug Condition

The bugs manifest in multiple scenarios:

1. **Chord Quality Bug**: When the `_simple_chord_recognition` method processes chroma features, it only uses major chord templates and hardcodes `quality = ChordQuality.MAJOR` for all detected chords (line 268 in chord_estimation.py)

2. **Extension Detection Bug**: When chords contain 7th notes or sus4 alterations, the template matching cannot detect them because templates only define triads (root, 3rd, 5th)

3. **Bass Note Bug**: When slash chords are present, the `detect_bass_notes` method exists but is never called in the chord recognition pipeline

4. **Layout Bug**: When `groupChordsIntoLines` calculates bars per chord, it uses `chordDuration / BEATS_PER_BAR` which assumes 1 second = 1 beat, but this doesn't account for actual tempo

5. **Lyrics Encoding Bug**: When Whisper transcribes Japanese text, the output may not be properly decoded or the text processing strips non-ASCII characters

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type AudioData OR ChordData OR LyricsData
  OUTPUT: boolean
  
  RETURN (input.type == "audio" AND containsNonMajorChords(input))
         OR (input.type == "chordDisplay" AND needsLayoutCalculation(input))
         OR (input.type == "lyrics" AND containsJapaneseText(input))
         
  WHERE:
    containsNonMajorChords(audio) = audio contains minor, 7th, sus4, or slash chords
    needsLayoutCalculation(chords) = chords need to be arranged in 16-bar lines
    containsJapaneseText(lyrics) = lyrics contain Japanese characters beyond "ん"
END FUNCTION
```

### Examples

**Chord Quality Examples:**
- Input: Audio with Em7 chord → Current: Displays "E" (major) → Expected: Displays "Em7"
- Input: Audio with A7 chord → Current: Displays "A" (major) → Expected: Displays "A7"
- Input: Audio with A7sus4 chord → Current: Displays "A" (major) → Expected: Displays "A7sus4"
- Input: Audio with A/G slash chord → Current: Displays "A" → Expected: Displays "A/G"

**Layout Example:**
- Input: 8 chords, each 2 seconds long, tempo 120 BPM → Current: Incorrect bar grouping → Expected: 16 bars per line with proper spacing

**Lyrics Example:**
- Input: Japanese lyrics "春の風が吹く" → Current: Displays "ん" → Expected: Displays "春の風が吹く"

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Major chord detection must continue to work exactly as before for actual major chords
- Confidence scoring (based on template matching score) must remain unchanged
- Low confidence visualization (< 70%) must continue to highlight uncertain chords
- Click interaction on chord segments must continue to show chord details
- Current playback position highlighting must remain unchanged
- Lyrics-chord time alignment logic must remain unchanged
- Vocal separation functionality must remain unchanged
- Chroma extraction for silent segments (zero vectors) must remain unchanged

**Scope:**
All inputs that contain only major chords, or all existing UI interactions and audio processing pipelines should be completely unaffected by this fix. This includes:
- Major chord recognition accuracy
- Confidence calculation methodology
- UI event handlers and state management
- Audio preprocessing (vocal separation, chroma extraction)
- Time-based synchronization between audio playback and visualization

## Hypothesized Root Cause

Based on the bug description and code analysis, the root causes are:

1. **Incomplete Chord Templates**: The `chord_templates` dictionary in `_simple_chord_recognition` only defines major triads (12 roots). Minor, diminished, augmented, 7th, and sus4 templates are missing.

2. **Hardcoded Chord Quality**: Line 268 in `chord_estimation.py` contains `quality = ChordQuality.MAJOR if best_chord != 'N' else ChordQuality.MAJOR`, which always assigns MAJOR quality regardless of the actual chord type detected.

3. **No Quality Detection Logic**: After template matching finds the best chord root, there's no logic to determine if it's major, minor, diminished, or augmented by analyzing the chroma pattern.

4. **Unused Bass Detection**: The `detect_bass_notes` method exists but is never called in the `estimate_chords` or `_simple_chord_recognition` methods, so slash chord bass notes are never detected.

5. **Incorrect Tempo Assumption**: The `groupChordsIntoLines` function calculates `barsInChord = Math.ceil(chordDuration / BEATS_PER_BAR)` assuming 1 second = 1 beat, but this doesn't account for actual tempo (e.g., 120 BPM means 1 beat = 0.5 seconds).

6. **Lyrics Encoding Issue**: The Whisper model output may be correctly transcribed, but somewhere in the processing pipeline (either in Python or when passing to TypeScript), the UTF-8 encoding is corrupted or only certain characters are preserved.

## Correctness Properties

Property 1: Bug Condition - Chord Quality Detection

_For any_ audio input where non-major chords are present (minor, 7th, sus4, slash chords), the fixed chord estimation module SHALL correctly identify the chord quality, extensions, and bass notes, displaying them with proper notation (e.g., "Em7", "A7sus4", "A/G").

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

Property 2: Bug Condition - Chord Layout

_For any_ set of chord segments that need to be displayed, the fixed ChordVisualization component SHALL arrange chords in lines of exactly 16 bars, with proper tempo-aware bar calculation.

**Validates: Requirements 2.6**

Property 3: Bug Condition - Lyrics Display

_For any_ Japanese lyrics transcribed by Whisper, the fixed lyrics transcription module SHALL preserve all UTF-8 characters and display the complete text without corruption.

**Validates: Requirements 2.7**

Property 4: Preservation - Major Chord Detection

_For any_ audio input containing only major chords, the fixed chord estimation module SHALL produce exactly the same detection results as the original module, preserving major chord recognition accuracy.

**Validates: Requirements 3.1**

Property 5: Preservation - UI Interactions

_For any_ user interaction with the chord visualization (clicks, playback highlighting) or lyrics display, the fixed components SHALL produce exactly the same behavior as the original components, preserving all interactive functionality.

**Validates: Requirements 3.2, 3.3, 3.4, 3.5**

Property 6: Preservation - Audio Processing

_For any_ audio input requiring preprocessing (vocal separation, chroma extraction), the fixed modules SHALL produce exactly the same preprocessing results as the original modules, preserving audio analysis quality.

**Validates: Requirements 3.6, 3.7**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `src/chord_estimation.py`

**Method**: `_simple_chord_recognition`

**Specific Changes**:

1. **Expand Chord Templates**: Add templates for all chord qualities
   - Add minor triad templates (e.g., Cm: [1,0,0,1,0,0,0,1,0,0,0,0])
   - Add dominant 7th templates (e.g., C7: [1,0,0,0,1,0,0,1,0,0,1,0])
   - Add major 7th templates (e.g., Cmaj7: [1,0,0,0,1,0,0,1,0,0,0,1])
   - Add sus4 templates (e.g., Csus4: [1,0,0,0,0,1,0,1,0,0,0,0])
   - Add diminished templates (e.g., Cdim: [1,0,0,1,0,0,1,0,0,0,0,0])

2. **Implement Quality Detection**: Replace hardcoded quality assignment
   - After finding best matching template, extract the quality from the template name
   - Map template names to ChordQuality enum values
   - Store quality in the ChordSegment object

3. **Integrate Bass Note Detection**: Call `detect_bass_notes` in the pipeline
   - After chord recognition, call `detect_bass_notes` on the audio segment
   - If bass note differs from root, store it in the `bass_note` field
   - This enables slash chord notation (e.g., "A/G")

4. **Fix Extension Detection**: Update `_detect_extensions` to handle 7th and sus4
   - Current implementation only checks for 9th, 11th, 13th
   - Add logic to detect 7th (minor 7th at index 10, major 7th at index 11)
   - Add logic to detect sus4 (4th at index 5 instead of 3rd at index 4)
   - Return extensions list including "7", "maj7", "sus4" as appropriate

**File**: `src/components/ChordVisualization.tsx`

**Method**: `groupChordsIntoLines`

**Specific Changes**:

5. **Fix Bar Calculation**: Add tempo parameter and calculate bars correctly
   - Add `tempo` prop to ChordVisualization (default 120 BPM)
   - Calculate `secondsPerBeat = 60 / tempo`
   - Calculate `secondsPerBar = secondsPerBeat * BEATS_PER_BAR`
   - Update: `barsInChord = Math.ceil(chordDuration / secondsPerBar)`
   - This ensures chords are grouped into exactly 16-bar lines

**File**: `src/lyrics_transcription.py`

**Method**: `transcribe`

**Specific Changes**:

6. **Ensure UTF-8 Encoding**: Verify text encoding throughout pipeline
   - Check that Whisper model is loaded with correct language parameter ("ja")
   - Ensure `segment['text']` is properly decoded as UTF-8
   - Verify no string operations strip non-ASCII characters
   - Add explicit UTF-8 encoding when returning LyricSegment objects

7. **Debug Logging**: Add logging to identify where text corruption occurs
   - Log raw Whisper output before any processing
   - Log text after `.strip()` operation
   - Log final LyricSegment text values
   - This will help identify the exact point of corruption

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bugs on unfixed code, then verify the fixes work correctly and preserve existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bugs BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that process audio with known chord progressions (minor, 7th, sus4, slash chords) and Japanese lyrics, then assert the expected output. Run these tests on the UNFIXED code to observe failures and understand the root cause.

**Test Cases**:
1. **Minor Chord Test**: Process audio with Em7 chord, assert output is "Em7" (will fail on unfixed code, showing "E")
2. **Dominant 7th Test**: Process audio with A7 chord, assert output is "A7" (will fail on unfixed code, showing "A")
3. **Sus4 Test**: Process audio with A7sus4 chord, assert output is "A7sus4" (will fail on unfixed code, showing "A")
4. **Slash Chord Test**: Process audio with A/G chord, assert output is "A/G" (will fail on unfixed code, showing "A")
5. **Layout Test**: Create 32 chords at 120 BPM, assert they're grouped into 2 lines of 16 bars each (will fail on unfixed code with incorrect grouping)
6. **Lyrics Test**: Process Japanese audio "春の風が吹く", assert output contains all characters (will fail on unfixed code, showing only "ん")

**Expected Counterexamples**:
- All non-major chords will be detected as major chords
- Chord layout will not follow 16-bar-per-line specification
- Japanese lyrics will show only "ん" character
- Possible causes: missing templates, hardcoded quality, incorrect bar calculation, encoding corruption

### Fix Checking

**Goal**: Verify that for all inputs where the bug conditions hold, the fixed functions produce the expected behavior.

**Pseudocode:**
```
FOR ALL audio WHERE containsNonMajorChords(audio) DO
  chords := chord_estimation_fixed(audio)
  ASSERT chords contain correct quality, extensions, and bass notes
END FOR

FOR ALL chordSet WHERE needsLayoutCalculation(chordSet) DO
  lines := groupChordsIntoLines_fixed(chordSet, tempo)
  ASSERT each line contains exactly 16 bars (except possibly last line)
END FOR

FOR ALL lyrics WHERE containsJapaneseText(lyrics) DO
  segments := transcribe_fixed(lyrics)
  ASSERT segments contain all Japanese characters without corruption
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug conditions do NOT hold, the fixed functions produce the same results as the original functions.

**Pseudocode:**
```
FOR ALL audio WHERE containsOnlyMajorChords(audio) DO
  ASSERT chord_estimation_original(audio) = chord_estimation_fixed(audio)
END FOR

FOR ALL interaction WHERE isUIInteraction(interaction) DO
  ASSERT handleInteraction_original(interaction) = handleInteraction_fixed(interaction)
END FOR

FOR ALL audio WHERE requiresPreprocessing(audio) DO
  ASSERT preprocess_original(audio) = preprocess_fixed(audio)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for major chords, UI interactions, and audio preprocessing, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Major Chord Preservation**: Generate random audio with only major chords, verify detection accuracy is unchanged
2. **Confidence Preservation**: Verify confidence scores are calculated identically for all chord types
3. **Click Interaction Preservation**: Verify chord click handlers continue to show correct details
4. **Playback Highlighting Preservation**: Verify current position highlighting works identically
5. **Vocal Separation Preservation**: Verify vocal separation produces identical output
6. **Chroma Extraction Preservation**: Verify chroma features are extracted identically, including silent segments

### Unit Tests

- Test each chord quality template matches correctly (major, minor, 7th, sus4, diminished)
- Test bass note detection for slash chords
- Test bar calculation with different tempos (60, 120, 180 BPM)
- Test edge cases (no chords, single chord, chords shorter than 1 bar)
- Test Japanese text encoding with various character sets (hiragana, katakana, kanji)
- Test lyrics with mixed languages (Japanese + English)

### Property-Based Tests

- Generate random chord progressions with all quality types, verify correct detection
- Generate random tempo values and chord durations, verify 16-bar layout is maintained
- Generate random Japanese text, verify all characters are preserved
- Generate random major-only progressions, verify preservation of original behavior
- Generate random UI interaction sequences, verify preservation of click/highlight behavior

### Integration Tests

- Test full audio analysis pipeline: load audio → separate vocals → extract chroma → detect chords → display with correct quality/extensions/bass
- Test full lyrics pipeline: load audio → transcribe → display Japanese text correctly
- Test synchronized playback: play audio → verify chords highlight at correct times → verify lyrics display at correct times
- Test chord layout with real song: analyze full song → verify all lines have 16 bars → verify visual layout matches specification
- Test mixed content: song with major, minor, 7th, sus4, and slash chords → verify all are detected and displayed correctly
