# Implementation Plan: Evaluation System

## Overview

This plan implements a comprehensive evaluation system for chord recognition accuracy measurement. The system includes a ground truth parser supporting 3 formats, an evaluator with 5 metrics (sequence accuracy, root accuracy, quality accuracy, DTW distance, exact match rate), a benchmark tool for batch processing, and a parameter optimizer using grid search. All components include property-based tests to validate correctness properties.

## Tasks

- [x] 1. Set up evaluation system structure and core data models
  - Create directory structure: `src/evaluation/`
  - Define data models: `ChordAnnotation`, `EvaluationMetrics`, `BenchmarkResult`, `OptimizationConfig`, `OptimizedParameters`
  - Implement validation logic for all data models
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ]* 1.1 Write property tests for data model validation
  - **Property 18: ChordAnnotation Validation** - chord non-empty, position non-negative
  - **Property 19: EvaluationMetrics Validation** - accuracy metrics in [0.0, 1.0], DTW non-negative
  - **Property 20: BenchmarkResult Validation** - song name non-empty, chord lists non-empty
  - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**

- [ ] 2. Implement Ground Truth Parser
  - [x] 2.1 Create parser base class and format detection
    - Implement `GroundTruthParser` class with `detect_format()` method
    - Add format detection logic for chord-only, lyrics-with-chords, lyrics-only
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ]* 2.2 Write property test for format detection
    - **Property 4: Format Detection Correctness** - detected format matches actual format
    - **Validates: Requirements 9.1, 9.2, 9.3**
  
  - [x] 2.3 Implement chord-only format parser
    - Parse pattern `[D][AonC#][Bm7]` using regex
    - Extract chords with sequential positions
    - Handle empty brackets
    - _Requirements: 1.1, 1.5_
  
  - [ ]* 2.4 Write property test for chord-only parsing
    - **Property 1: Parsing Extracts All Chords** - all chords extracted with sequential positions
    - **Validates: Requirements 1.1**
  
  - [x] 2.5 Implement lyrics-with-chords format parser
    - Parse pattern `涙[D]があふれ[AonC#]る` using regex
    - Extract chords with character positions
    - Preserve position accuracy
    - _Requirements: 1.2, 1.5_
  
  - [ ]* 2.6 Write property test for lyrics-with-chords parsing
    - **Property 2: Parsing Preserves Character Positions** - positions match character indices
    - **Validates: Requirements 1.2**
  
  - [x] 2.7 Implement lyrics-only format handler
    - Return empty list for lyrics without chords
    - _Requirements: 1.3_
  
  - [ ]* 2.8 Write property test for position monotonicity
    - **Property 3: Position Monotonicity** - positions monotonically increasing
    - **Validates: Requirements 1.6**
  
  - [x] 2.9 Add error handling for invalid formats
    - Raise ValueError with descriptive messages
    - Provide format detection hints
    - _Requirements: 11.1, 11.2, 11.3_

- [ ] 3. Implement chord analysis utilities
  - [x] 3.1 Create root note extraction function
    - Extract root from simple chords (D, Am)
    - Extract root from slash chords (AonC#)
    - Extract root from chords with quality suffix (Bm7, Cmaj7)
    - Handle sharp and flat accidentals
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 3.2 Write property test for root extraction
    - **Property 6: Root Extraction Correctness** - root extracted correctly for all chord types
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
  
  - [x] 3.3 Create chord quality identification function
    - Identify major, minor, seventh, major seventh qualities
    - Handle various chord suffixes
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 3.4 Write property test for quality identification
    - **Property 7: Quality Identification Correctness** - quality matches chord suffix
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ] 4. Checkpoint - Ensure parser and utilities tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Evaluator core metrics
  - [x] 5.1 Create Evaluator class with sequence accuracy calculation
    - Implement exact sequence matching
    - Calculate match rate
    - _Requirements: 2.1_
  
  - [x] 5.2 Implement root accuracy calculation
    - Use root extraction utility
    - Compare root notes between predicted and ground truth
    - Calculate accuracy percentage
    - _Requirements: 2.2, 3.1, 3.2, 3.3, 3.4_
  
  - [x] 5.3 Implement quality accuracy calculation
    - Use quality identification utility
    - Compare chord qualities between predicted and ground truth
    - Calculate accuracy percentage
    - _Requirements: 2.3, 4.1, 4.2, 4.3, 4.4_
  
  - [x] 5.4 Implement exact match rate calculation
    - Count exact chord matches
    - Calculate match rate
    - _Requirements: 2.5_
  
  - [ ]* 5.5 Write property test for metric bounds
    - **Property 5: Metric Bounds** - all accuracy metrics in [0.0, 1.0], DTW non-negative
    - **Validates: Requirements 2.6, 2.7**

- [ ] 6. Implement DTW distance calculation
  - [ ] 6.1 Create chord distance function
    - Return 0.0 for identical chords
    - Return 0.5 for same root, different quality
    - Return 1.0 for different roots
    - _Requirements: 5.4_
  
  - [ ]* 6.2 Write property test for chord distance function
    - **Property 9: DTW Chord Distance Function** - distance values match specification
    - **Validates: Requirements 5.4**
  
  - [ ] 6.3 Implement DTW matrix calculation
    - Initialize DTW matrix with infinity
    - Fill matrix using dynamic programming
    - Handle sequences of different lengths
    - _Requirements: 5.1, 5.3_
  
  - [ ] 6.4 Add DTW normalization
    - Normalize by path length (sum of sequence lengths)
    - _Requirements: 5.5_
  
  - [ ]* 6.5 Write property test for DTW identity
    - **Property 8: DTW Identity** - distance between sequence and itself is zero
    - **Validates: Requirements 5.2**
  
  - [ ]* 6.6 Write property test for DTW normalization
    - **Property 10: DTW Normalization** - distance normalized by path length
    - **Validates: Requirements 5.5**
  
  - [ ] 6.7 Integrate DTW into Evaluator
    - Add DTW distance to evaluation metrics
    - _Requirements: 2.4_

- [ ] 7. Implement sequence alignment
  - [ ] 7.1 Create alignment function for different length sequences
    - Implement alignment strategy to minimize distortion
    - Ensure aligned sequences have same length
    - Preserve original sequences
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ]* 7.2 Write property test for aligned sequences
    - **Property 11: Aligned Sequences Same Length** - both aligned sequences have same length
    - **Validates: Requirements 10.3**
  
  - [ ]* 7.3 Write property test for original sequence preservation
    - **Property 12: Original Sequences Preserved** - original sequences stored unchanged
    - **Validates: Requirements 10.4**

- [ ] 8. Complete Evaluator with main evaluation method
  - [ ] 8.1 Implement main `evaluate()` method
    - Align sequences if lengths differ
    - Calculate all metrics (sequence, root, quality, DTW, exact match)
    - Return EvaluationMetrics object
    - Handle perfect match case (all metrics 1.0, DTW 0.0)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.8_
  
  - [ ]* 8.2 Write unit tests for Evaluator edge cases
    - Test empty sequences
    - Test single chord sequences
    - Test perfect matches
    - Test complete mismatches
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.8_

- [ ] 9. Checkpoint - Ensure evaluator tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement Benchmark Tool
  - [ ] 10.1 Create BenchmarkTool class with file discovery
    - Scan audio and ground truth directories
    - Match audio files with ground truth files
    - Log warnings for missing pairs
    - Validate file paths to prevent path traversal
    - _Requirements: 6.1, 6.2, 12.4, 15.1_
  
  - [ ] 10.2 Implement single song processing
    - Parse ground truth file
    - Run chord recognition on audio file
    - Align sequences
    - Calculate metrics
    - Create BenchmarkResult
    - Handle file processing errors gracefully
    - _Requirements: 6.3, 12.1, 12.2, 12.3_
  
  - [ ]* 10.3 Write property test for benchmark result structure
    - **Property 13: Benchmark Result Structure** - result contains all required fields
    - **Validates: Requirements 6.3**
  
  - [ ] 10.4 Implement batch processing with error handling
    - Process all file pairs
    - Continue on individual file failures
    - Log errors with file names and exception details
    - Return list of successful results
    - _Requirements: 6.5, 12.1, 12.2, 12.3_
  
  - [ ] 10.5 Implement aggregate statistics calculation
    - Calculate mean, standard deviation, min, max for each metric
    - Handle empty results list
    - _Requirements: 6.4_
  
  - [ ]* 10.6 Write property test for aggregate statistics
    - **Property 14: Aggregate Statistics Calculation** - statistics calculated correctly
    - **Validates: Requirements 6.4**

- [ ] 11. Implement report generation
  - [ ] 11.1 Create JSON report generator
    - Include aggregate statistics
    - Include per-song detailed results
    - Save to specified output path
    - _Requirements: 7.1, 7.3, 7.4, 7.5_
  
  - [ ] 11.2 Create Markdown report generator
    - Format aggregate statistics in table
    - Format per-song results in readable format
    - Save to specified output path
    - _Requirements: 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 11.3 Write property test for report content
    - **Property 15: Report Contains Required Information** - report includes aggregate and per-song results
    - **Validates: Requirements 7.3, 7.4**

- [ ] 12. Implement security and validation
  - [ ] 12.1 Add file path validation
    - Prevent path traversal attacks
    - Validate paths are within allowed directories
    - _Requirements: 12.4, 15.1_
  
  - [ ]* 12.2 Write property test for path traversal prevention
    - **Property 21: Path Traversal Prevention** - traversal patterns rejected
    - **Validates: Requirements 12.4, 15.1**
  
  - [ ] 12.3 Add file size limit enforcement
    - Check ground truth file sizes before reading
    - Reject files exceeding maximum size
    - _Requirements: 15.2_
  
  - [ ]* 12.4 Write property test for file size limit
    - **Property 22: File Size Limit Enforcement** - oversized files rejected
    - **Validates: Requirements 15.2**
  
  - [ ] 12.5 Add input sanitization for regex patterns
    - Sanitize inputs to prevent regex injection
    - _Requirements: 15.3_

- [ ] 13. Checkpoint - Ensure benchmark tool tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Implement Parameter Optimizer
  - [ ] 14.1 Create ParameterOptimizer class with grid generation
    - Generate parameter grid from ranges
    - Support penalty and threshold parameters
    - _Requirements: 8.1_
  
  - [ ] 14.2 Implement single parameter evaluation
    - Update system parameters
    - Run benchmark
    - Calculate target metric
    - _Requirements: 8.2_
  
  - [ ] 14.3 Implement grid search optimization
    - Iterate over parameter grid
    - Track best score and parameters
    - Return optimized parameters
    - _Requirements: 8.1, 8.3, 8.4_
  
  - [ ]* 14.4 Write property test for optimization tracking
    - **Property 16: Optimization Tracks Best Score** - best score is maximum found
    - **Validates: Requirements 8.3**
  
  - [ ]* 14.5 Write property test for optimization non-regression
    - **Property 17: Optimization Non-Regression** - optimized metric ≥ baseline
    - **Validates: Requirements 8.5**

- [ ] 15. Implement performance optimizations
  - [ ] 15.1 Add caching for audio processing
    - Cache audio processing results during optimization
    - Use file path as cache key
    - _Requirements: 14.2_
  
  - [ ]* 15.2 Write property test for cache efficiency
    - **Property 25: Cache Hit Efficiency** - subsequent processing uses cache
    - **Validates: Requirements 14.2**
  
  - [ ] 15.3 Add progress indicators for long-running operations
    - Show progress during benchmark execution
    - Show progress during optimization
    - _Requirements: 14.4_
  
  - [ ] 15.4 Consider parallel processing for benchmark tool
    - Use multiprocessing for concurrent song processing
    - Handle process pool management
    - _Requirements: 14.1_

- [ ] 16. Add comprehensive error handling
  - [ ] 16.1 Implement error handling for invalid formats
    - Raise ValueError with descriptive messages
    - Include format detection hints
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [ ]* 16.2 Write property test for error messages
    - **Property 24: Invalid Format Error Messages** - error messages are descriptive
    - **Validates: Requirements 11.1, 11.3**
  
  - [ ] 16.3 Implement error handling for file operations
    - Log errors with file names and exception details
    - Continue processing on individual failures
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [ ]* 16.4 Write property test for error handling resilience
    - **Property 23: Error Handling Resilience** - benchmark continues on file failures
    - **Validates: Requirements 12.1, 12.2, 12.3**

- [ ] 17. Create integration and wiring
  - [ ] 17.1 Wire all components together
    - Connect Parser, Evaluator, BenchmarkTool, Optimizer
    - Create main evaluation workflow function
    - Integrate with existing audio_engine
    - _Requirements: All requirements_
  
  - [ ]* 17.2 Write integration tests
    - Test end-to-end evaluation workflow
    - Test end-to-end benchmark workflow
    - Test end-to-end optimization workflow
    - Use real audio files and ground truth data
    - _Requirements: All requirements_

- [ ] 18. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end workflows with real data
- The implementation uses Python as specified in the design document
- All components integrate with existing `src.audio_engine` and `src.chord_estimation` modules
- Security considerations (path validation, file size limits, input sanitization) are implemented throughout
- Performance optimizations (caching, parallel processing) are included for large-scale benchmarks
