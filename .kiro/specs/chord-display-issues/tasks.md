# Implementation Plan

- [ ] 1. Write bug condition exploration tests
  - **Property 1: Bug Condition** - Chord Quality, Extension, Bass Note, Layout, and Lyrics Bugs
  - **CRITICAL**: These tests MUST FAIL on unfixed code - failure confirms the bugs exist
  - **DO NOT attempt to fix the tests or the code when they fail**
  - **NOTE**: These tests encode the expected behavior - they will validate the fixes when they pass after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bugs exist
  - **Scoped PBT Approach**: For deterministic bugs, scope properties to concrete failing cases to ensure reproducibility
  
  - [x] 1.1 Test chord quality detection bug
    - Test that Em7 chord is detected as "Em7" (not "E")
    - Test that A7 chord is detected as "A7" (not "A")
    - Test that A7sus4 chord is detected as "A7sus4" (not "A")
    - Test that A/G slash chord is detected as "A/G" (not "A")
    - Run tests on UNFIXED code
    - **EXPECTED OUTCOME**: Tests FAIL (confirms bugs exist)
    - Document counterexamples found (e.g., "Em7 detected as E major")
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 1.2 Test chord layout bug
    - Create test with 32 chords at 120 BPM (should be 2 lines of 16 bars each)
    - Assert chords are grouped into lines of exactly 16 bars
    - Run test on UNFIXED code
    - **EXPECTED OUTCOME**: Test FAILS (confirms layout bug exists)
    - Document incorrect bar grouping observed
    - _Requirements: 2.6_
  
  - [x] 1.3 Test lyrics encoding bug
    - Process Japanese audio with text "春の風が吹く"
    - Assert output contains all Japanese characters
    - Run test on UNFIXED code
    - **EXPECTED OUTCOME**: Test FAILS (confirms only "ん" is displayed)
    - Document which characters are lost
    - _Requirements: 2.7_

- [ ] 2. Write preservation property tests (BEFORE implementing fixes)
  - **Property 2: Preservation** - Major Chord Detection, UI Interactions, Audio Processing
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  
  - [x] 2.1 Test major chord preservation
    - Observe: Process audio with only major chords (C, G, Am is major A, F)
    - Write property-based test: for all major-only chord progressions, detection accuracy matches original
    - Run test on UNFIXED code
    - **EXPECTED OUTCOME**: Test PASSES (confirms baseline behavior to preserve)
    - _Requirements: 3.1_
  
  - [x] 2.2 Test confidence scoring preservation
    - Observe: Confidence scores for various chord detections on unfixed code
    - Write property-based test: confidence calculation methodology unchanged
    - Run test on UNFIXED code
    - **EXPECTED OUTCOME**: Test PASSES
    - _Requirements: 3.1_
  
  - [x] 2.3 Test UI interaction preservation
    - Observe: Click handlers on chord segments show chord details
    - Observe: Playback highlighting updates current position
    - Write tests: UI interactions produce same behavior
    - Run tests on UNFIXED code
    - **EXPECTED OUTCOME**: Tests PASS
    - _Requirements: 3.2, 3.3, 3.4_
  
  - [x] 2.4 Test audio processing preservation
    - Observe: Vocal separation output on unfixed code
    - Observe: Chroma extraction including silent segments (zero vectors)
    - Write property-based tests: preprocessing produces identical results
    - Run tests on UNFIXED code
    - **EXPECTED OUTCOME**: Tests PASS
    - _Requirements: 3.6, 3.7_

- [ ] 3. Fix chord quality, extension, and bass note detection

  - [x] 3.1 Expand chord templates in _simple_chord_recognition
    - Add minor triad templates for all 12 roots (e.g., Cm: [1,0,0,1,0,0,0,1,0,0,0,0])
    - Add dominant 7th templates for all 12 roots (e.g., C7: [1,0,0,0,1,0,0,1,0,0,1,0])
    - Add major 7th templates for all 12 roots (e.g., Cmaj7: [1,0,0,0,1,0,0,1,0,0,0,1])
    - Add sus4 templates for all 12 roots (e.g., Csus4: [1,0,0,0,0,1,0,1,0,0,0,0])
    - Add diminished templates for all 12 roots (e.g., Cdim: [1,0,0,1,0,0,1,0,0,0,0,0])
    - _Bug_Condition: isBugCondition(input) where input.type == "audio" AND containsNonMajorChords(input)_
    - _Expected_Behavior: Chords classified with correct quality (Property 1)_
    - _Preservation: Major chord detection unchanged (Property 4)_
    - _Requirements: 2.1, 2.2, 3.1_

  - [x] 3.2 Implement chord quality detection logic
    - Replace hardcoded `quality = ChordQuality.MAJOR` on line 268
    - Extract quality from best matching template name
    - Map template names to ChordQuality enum values (MAJOR, MINOR, DIMINISHED, AUGMENTED, SUSPENDED)
    - Store quality in ChordSegment object
    - _Bug_Condition: isBugCondition(input) where input.type == "audio" AND containsNonMajorChords(input)_
    - _Expected_Behavior: Chords classified with correct quality (Property 1)_
    - _Preservation: Major chord detection unchanged (Property 4)_
    - _Requirements: 2.1, 2.2, 3.1_

  - [x] 3.3 Fix _detect_extensions to handle 7th and sus4
    - Add logic to detect minor 7th (chroma index 10) and major 7th (chroma index 11)
    - Add logic to detect sus4 (4th at index 5 instead of 3rd at index 4)
    - Return extensions list including "7", "maj7", "sus4" as appropriate
    - Update existing 9th, 11th, 13th detection to work with new templates
    - _Bug_Condition: isBugCondition(input) where input.type == "audio" AND containsNonMajorChords(input)_
    - _Expected_Behavior: Extensions detected correctly (Property 1)_
    - _Preservation: Existing extension detection unchanged (Property 4)_
    - _Requirements: 2.3, 2.4, 3.1_

  - [x] 3.4 Integrate bass note detection for slash chords
    - Call `detect_bass_notes` method after chord recognition in the pipeline
    - If detected bass note differs from chord root, store in `bass_note` field
    - Enable slash chord notation (e.g., "A/G")
    - _Bug_Condition: isBugCondition(input) where input.type == "audio" AND containsNonMajorChords(input)_
    - _Expected_Behavior: Bass notes detected for slash chords (Property 1)_
    - _Preservation: Non-slash chord behavior unchanged (Property 4)_
    - _Requirements: 2.5, 3.1_

  - [x] 3.5 Verify chord quality exploration tests now pass
    - **Property 1: Expected Behavior** - Chord Quality, Extension, Bass Note Detection
    - **IMPORTANT**: Re-run the SAME tests from task 1.1 - do NOT write new tests
    - Run tests for Em7, A7, A7sus4, A/G detection
    - **EXPECTED OUTCOME**: Tests PASS (confirms bugs are fixed)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 3.6 Verify chord preservation tests still pass
    - **Property 2: Preservation** - Major Chord Detection
    - **IMPORTANT**: Re-run the SAME tests from tasks 2.1 and 2.2 - do NOT write new tests
    - Run major chord preservation and confidence scoring tests
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.1_

- [ ] 4. Fix chord layout calculation

  - [x] 4.1 Add tempo parameter to ChordVisualization component
    - Add `tempo` prop with default value 120 BPM
    - Pass tempo to `groupChordsIntoLines` function
    - Update component prop types
    - _Bug_Condition: isBugCondition(input) where input.type == "chordDisplay" AND needsLayoutCalculation(input)_
    - _Expected_Behavior: Tempo-aware bar calculation (Property 2)_
    - _Preservation: UI interactions unchanged (Property 5)_
    - _Requirements: 2.6, 3.2, 3.3, 3.4_

  - [x] 4.2 Fix bar calculation in groupChordsIntoLines
    - Calculate `secondsPerBeat = 60 / tempo`
    - Calculate `secondsPerBar = secondsPerBeat * BEATS_PER_BAR`
    - Update: `barsInChord = Math.ceil(chordDuration / secondsPerBar)`
    - Ensure chords are grouped into exactly 16-bar lines
    - _Bug_Condition: isBugCondition(input) where input.type == "chordDisplay" AND needsLayoutCalculation(input)_
    - _Expected_Behavior: 16 bars per line (Property 2)_
    - _Preservation: UI interactions unchanged (Property 5)_
    - _Requirements: 2.6, 3.2, 3.3, 3.4_

  - [x] 4.3 Verify layout exploration test now passes
    - **Property 1: Expected Behavior** - Chord Layout
    - **IMPORTANT**: Re-run the SAME test from task 1.2 - do NOT write a new test
    - Run test with 32 chords at 120 BPM
    - **EXPECTED OUTCOME**: Test PASSES (confirms layout bug is fixed)
    - _Requirements: 2.6_

  - [x] 4.4 Verify UI interaction preservation tests still pass
    - **Property 2: Preservation** - UI Interactions
    - **IMPORTANT**: Re-run the SAME tests from task 2.3 - do NOT write new tests
    - Run click handler and playback highlighting tests
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.2, 3.3, 3.4_

- [ ] 5. Fix lyrics UTF-8 encoding

  - [x] 5.1 Ensure UTF-8 encoding in transcribe method
    - Verify Whisper model is loaded with correct language parameter ("ja")
    - Ensure `segment['text']` is properly decoded as UTF-8
    - Verify no string operations strip non-ASCII characters
    - Add explicit UTF-8 encoding when returning LyricSegment objects
    - _Bug_Condition: isBugCondition(input) where input.type == "lyrics" AND containsJapaneseText(input)_
    - _Expected_Behavior: All Japanese characters preserved (Property 3)_
    - _Preservation: Lyrics-chord alignment unchanged (Property 5)_
    - _Requirements: 2.7, 3.5_

  - [x] 5.2 Add debug logging to identify corruption point
    - Log raw Whisper output before any processing
    - Log text after `.strip()` operation
    - Log final LyricSegment text values
    - This helps identify exact point of corruption if issue persists
    - _Bug_Condition: isBugCondition(input) where input.type == "lyrics" AND containsJapaneseText(input)_
    - _Expected_Behavior: All Japanese characters preserved (Property 3)_
    - _Requirements: 2.7_

  - [x] 5.3 Verify lyrics exploration test now passes
    - **Property 1: Expected Behavior** - Lyrics Display
    - **IMPORTANT**: Re-run the SAME test from task 1.3 - do NOT write a new test
    - Run test with Japanese text "春の風が吹く"
    - **EXPECTED OUTCOME**: Test PASSES (confirms lyrics bug is fixed)
    - _Requirements: 2.7_

  - [x] 5.4 Verify lyrics alignment preservation test still passes
    - **Property 2: Preservation** - Lyrics-Chord Alignment
    - Write test observing lyrics-chord time alignment on unfixed code
    - Run test on fixed code
    - **EXPECTED OUTCOME**: Test PASSES (confirms no regressions)
    - _Requirements: 3.5_

- [ ] 6. Run integration tests

  - [x] 6.1 Test full audio analysis pipeline
    - Load audio → separate vocals → extract chroma → detect chords → display with correct quality/extensions/bass
    - Verify end-to-end chord detection works for all chord types
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [~] 6.2 Test full lyrics pipeline
    - Load audio → transcribe → display Japanese text correctly
    - Verify end-to-end lyrics transcription preserves UTF-8
    - _Requirements: 2.7_

  - [~] 6.3 Test synchronized playback
    - Play audio → verify chords highlight at correct times → verify lyrics display at correct times
    - Verify time-based synchronization works correctly
    - _Requirements: 3.3, 3.4, 3.5_

  - [~] 6.4 Test chord layout with real song
    - Analyze full song → verify all lines have 16 bars → verify visual layout matches specification
    - Test with different tempos (60, 120, 180 BPM)
    - _Requirements: 2.6_

  - [~] 6.5 Test mixed content
    - Song with major, minor, 7th, sus4, and slash chords → verify all are detected and displayed correctly
    - Verify no regressions in major chord detection
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1_

- [ ] 7. Checkpoint - Ensure all tests pass
  - Verify all exploration tests pass (chord quality, layout, lyrics)
  - Verify all preservation tests pass (major chords, UI, audio processing)
  - Verify all integration tests pass
  - Ask the user if questions arise
