# Implementation Plan: ChordAI Model Integration

## Overview

This implementation replaces the current template matching chord recognition system with the ChordAI pre-trained machine learning model. The integration maintains compatibility with the existing audio pipeline while significantly improving chord recognition accuracy, particularly for minor chords and bass note detection.

## Tasks

- [x] 1. Research ChordAI repository and determine model format
  - Clone and examine the ChordAI repository (https://github.com/anime-song/ChordAI)
  - Identify model file format (TensorFlow, PyTorch, or ONNX)
  - Document model input/output specifications
  - Document required dependencies and versions
  - Create a brief summary document of findings
  - _Requirements: 1.1, 6.1_

- [ ] 2. Implement ChordAI model loader component
  - [x] 2.1 Create ChordAIModelLoader class in new file src/chordai_loader.py
    - Implement __init__ method to accept model_path parameter
    - Implement load_model method to load model weights from file
    - Implement validate_model method to verify model architecture
    - Add error handling for missing/corrupted model files
    - _Requirements: 1.1, 1.2, 1.4_
  
  - [ ]* 2.2 Write property test for model loader error handling
    - **Property 1: Invalid Model Files Raise Descriptive Errors**
    - **Validates: Requirements 1.2**
  
  - [ ]* 2.3 Write unit tests for ChordAIModelLoader
    - Test successful model loading with valid file
    - Test FileNotFoundError for missing model file
    - Test RuntimeError for corrupted model file
    - Test model architecture validation
    - _Requirements: 1.1, 1.2, 1.4_

- [ ] 3. Implement ChordAI inference engine component
  - [x] 3.1 Create ChordAIInferenceEngine class in src/chordai_inference.py
    - Implement __init__ method to accept loaded model
    - Implement predict_chords method to run inference on chroma features
    - Handle batch processing of chroma frames
    - Return list of ChordPrediction objects with timing, root, quality, bass_note, confidence
    - _Requirements: 2.3, 5.1_
  
  - [ ]* 3.2 Write property test for chroma feature passing
    - **Property 3: Chroma Features Passed to Inference Engine**
    - **Validates: Requirements 2.3**
  
  - [ ]* 3.3 Write unit tests for ChordAIInferenceEngine
    - Test inference with valid chroma input
    - Test output format (ChordPrediction list)
    - Test error handling for invalid input shapes
    - _Requirements: 2.3_

- [ ] 4. Create data models and output mapper
  - [x] 4.1 Create ChordPrediction dataclass in src/chordai_models.py
    - Define fields: start_time, end_time, root, quality, bass_note, confidence
    - Add type hints for all fields
    - _Requirements: 2.4, 4.2_
  
  - [x] 4.2 Create ChordAIOutputMapper class in src/chordai_mapper.py
    - Implement map_to_chord_segment static method
    - Implement map_quality_string static method with quality mapping table
    - Handle all chord quality types (major, minor, dim, aug, 7th, maj7, sus4, sus2, 9th, 11th, 13th)
    - Add error handling for unknown quality strings
    - _Requirements: 2.4, 5.2_
  
  - [ ]* 4.3 Write property test for output format compatibility
    - **Property 4: Output Format Compatibility**
    - **Validates: Requirements 2.4, 5.2**
  
  - [ ]* 4.4 Write unit tests for ChordAIOutputMapper
    - Test quality string mapping for all chord types
    - Test ChordPrediction to ChordSegment conversion
    - Test bass_note handling (present and absent)
    - Test error handling for unknown quality strings
    - _Requirements: 2.4, 4.2_

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Integrate ChordAI into ChordEstimationModule
  - [x] 6.1 Modify ChordEstimationModule.__init__ in src/chord_estimation.py
    - Add chordai_loader and inference_engine attributes
    - Load ChordAI model using ChordAIModelLoader
    - Initialize ChordAIInferenceEngine with loaded model
    - Add dependency verification at initialization
    - Add error handling for missing dependencies
    - _Requirements: 1.3, 6.2, 6.3_
  
  - [x] 6.2 Create _chordai_recognition method in ChordEstimationModule
    - Accept chroma and sample_rate parameters
    - Call inference_engine.predict_chords with chroma features
    - Map ChordPrediction objects to ChordSegment objects using ChordAIOutputMapper
    - Return list of ChordSegment objects
    - _Requirements: 2.1, 2.3, 2.4_
  
  - [x] 6.3 Replace _simple_chord_recognition call with _chordai_recognition in estimate_chords method
    - Update estimate_chords to call _chordai_recognition instead of _simple_chord_recognition
    - Verify chroma features are passed unchanged
    - _Requirements: 2.1, 2.3_
  
  - [ ]* 6.4 Write property test for input format compatibility
    - **Property 8: Input Format Compatibility**
    - **Validates: Requirements 5.1**
  
  - [ ]* 6.5 Write unit tests for ChordEstimationModule integration
    - Test ChordAI model loading in __init__
    - Test _chordai_recognition method with sample chroma
    - Test integration with existing pipeline (vocal separation → chroma → ChordAI)
    - _Requirements: 2.1, 2.3, 5.1_

- [ ] 7. Remove template matching code
  - [x] 7.1 Delete _simple_chord_recognition method from ChordEstimationModule
    - Remove entire method implementation
    - Remove chord_templates dictionary
    - Remove helper methods: _extract_quality_from_template_name, _extract_root_from_template_name, _detect_extensions
    - _Requirements: 2.2_
  
  - [ ]* 7.2 Verify template matching removal
    - Search codebase for any remaining references to template matching
    - Ensure no dead code remains
    - _Requirements: 2.2_

- [ ] 8. Implement bass note integration
  - [x] 8.1 Update bass note matching logic in estimate_chords method
    - Ensure ChordAI bass_note predictions are preserved
    - Only override with detected bass notes if ChordAI didn't provide one
    - Handle root position chords (bass_note matches root)
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ]* 8.2 Write property test for bass note handling
    - **Property 6: Bass Note Included When Detected**
    - **Property 7: Root Position Bass Note Handling**
    - **Validates: Requirements 4.2, 4.3**
  
  - [ ]* 8.3 Write unit tests for bass note integration
    - Test bass note preservation from ChordAI
    - Test bass note override from detect_bass_notes
    - Test root position handling
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Validate pipeline compatibility
  - [ ]* 10.1 Write integration tests for full audio pipeline
    - Test complete pipeline: audio file → vocal separation → chroma → ChordAI → bass matching → ChordSegment output
    - Verify cache system compatibility
    - Verify lyrics alignment compatibility
    - Verify chord visualization compatibility
    - _Requirements: 5.1, 5.2, 5.3, 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 10.2 Write property test for prediction consistency
    - **Property 5: Prediction Consistency**
    - **Validates: Requirements 3.3**
  
  - [ ]* 10.3 Write performance tests
    - Measure ChordAI inference time vs template matching baseline
    - Verify performance is within 20% of baseline
    - _Requirements: 5.4_

- [ ] 11. Create accuracy validation tests
  - [ ]* 11.1 Write tests for minor chord recognition accuracy
    - Test ChordAI on audio samples with known minor chords
    - Compare accuracy against template matching baseline
    - Verify ChordAI correctly identifies minor chord quality
    - _Requirements: 3.1, 3.2, 8.3_
  
  - [ ]* 11.2 Write tests for bass note detection accuracy
    - Test ChordAI on audio samples with known chord inversions
    - Verify bass note detection for slash chords
    - Compare against template matching baseline (which has no bass detection)
    - _Requirements: 4.1, 8.4_
  
  - [ ]* 11.3 Write tests comparing against reference application
    - Test ChordAI output matches reference application quality
    - Use same audio inputs as reference application
    - Verify chord predictions match expected results
    - _Requirements: 8.1, 8.2_

- [ ] 12. Update documentation and dependencies
  - [x] 12.1 Update requirements.txt or pyproject.toml with ChordAI dependencies
    - Add required ML framework (tensorflow/torch/onnxruntime)
    - Document version constraints
    - _Requirements: 6.1, 6.4_
  
  - [x] 12.2 Add model download instructions to README
    - Document where to obtain ChordAI model weights
    - Document model file placement location
    - Document dependency installation steps
    - _Requirements: 6.1_
  
  - [x] 12.3 Update code comments and docstrings
    - Update ChordEstimationModule docstring to mention ChordAI
    - Add docstrings to all new classes and methods
    - Remove outdated comments about template matching
    - _Requirements: 2.1_

- [x] 13. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The ChordAI model format will be determined in task 1 and may affect implementation details in tasks 2-3
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples, edge cases, and integration points
- Accuracy validation tests ensure the ChordAI integration improves chord recognition quality
