# Implementation Plan: Chord Evaluation Preprocessing

## Overview

This implementation plan breaks down the chord evaluation preprocessing feature into actionable coding tasks. The feature adds normalization and aggregation capabilities to the evaluation system, addressing the mismatch between predicted chords (3009) and ground truth chords (125) that currently causes low evaluation accuracy.

Implementation will follow this order:
1. Core data structures and enums
2. Chord normalization with property tests
3. Chord aggregation with property tests
4. Preprocessing pipeline integration
5. BenchmarkTool integration
6. Performance optimization and validation

## Tasks

- [x] 1. Set up preprocessing module structure and core types
  - Create `src/evaluation/preprocessing.py` module
  - Define `NormalizationMode` enum (SLASH, ON, STANDARD)
  - Define `AggregationStrategy` enum (MOST_FREQUENT, LONGEST_DURATION, FIRST, LAST)
  - Define `PreprocessingConfig` dataclass with default values
  - Define `ChordWithTimestamp` dataclass with duration property
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 2. Implement ChordNormalizer
  - [x] 2.1 Create ChordNormalizer class with initialization
    - Implement `__init__` method accepting NormalizationMode
    - Store normalization mode configuration
    - _Requirements: 1.2, 1.3, 5.3_
  
  - [x] 2.2 Implement chord parsing logic
    - Write `_parse_chord` method to extract root, quality, and bass
    - Handle slash notation (C/E) and on notation (ConE)
    - Support various quality representations (maj, M, major, min, m, etc.)
    - _Requirements: 1.2, 1.3, 1.4_
  
  - [x] 2.3 Implement root note normalization
    - Write `_normalize_root` method for root note standardization
    - Handle enharmonic equivalents (C# vs Db)
    - Ensure uppercase formatting
    - _Requirements: 1.5, 8.1_
  
  - [x] 2.4 Implement quality normalization
    - Write `_normalize_quality` method for quality standardization
    - Map quality variations to standard forms (maj→M, min→m)
    - _Requirements: 1.4, 8.2_
  
  - [x] 2.5 Implement chord building logic
    - Write `_build_chord` method to construct normalized chord string
    - Apply normalization mode (SLASH, ON, STANDARD) for bass notes
    - Handle chords without bass notes
    - _Requirements: 1.2, 1.3, 8.3_
  
  - [x] 2.6 Implement normalize method
    - Write `normalize` method combining all normalization steps
    - Strip whitespace from input
    - Validate input and raise ValueError for invalid chords
    - Return normalized chord string
    - _Requirements: 1.1, 1.6, 1.8, 6.1, 8.1, 8.2, 8.3_
  
  - [x] 2.7 Implement batch normalization
    - Write `normalize_batch` method for list processing
    - Apply normalize to each chord in the list
    - _Requirements: 1.7_
  
  - [ ]* 2.8 Write property test for normalization idempotency
    - **Property 1: Normalization idempotency**
    - **Validates: Requirements 1.6**
    - Generate random valid chords
    - Verify normalize(normalize(x)) == normalize(x)
  
  - [ ]* 2.9 Write property test for batch normalization equivalence
    - **Property 2: Batch normalization equivalence**
    - **Validates: Requirements 1.7**
    - Generate random chord lists
    - Verify batch result equals individual normalization results
  
  - [ ]* 2.10 Write property test for whitespace removal
    - **Property 3: Whitespace removal**
    - **Validates: Requirements 1.1**
    - Generate chords with various whitespace patterns
    - Verify normalized chords contain no whitespace
  
  - [ ]* 2.11 Write property test for root note preservation
    - **Property 4: Root note preservation**
    - **Validates: Requirements 8.1**
    - Generate valid chords with various root notes
    - Verify pitch class is preserved after normalization
  
  - [ ]* 2.12 Write property test for quality preservation
    - **Property 5: Quality preservation**
    - **Validates: Requirements 8.2**
    - Generate chords with various qualities
    - Verify quality meaning is preserved after normalization
  
  - [ ]* 2.13 Write property test for bass note preservation
    - **Property 6: Bass note preservation**
    - **Validates: Requirements 8.3**
    - Generate slash chords with bass notes
    - Verify bass note pitch is preserved after normalization
  
  - [ ]* 2.14 Write property test for invalid chord error detection
    - **Property 20: Invalid chord error detection**
    - **Validates: Requirements 1.8, 6.1**
    - Generate invalid chord notations
    - Verify ValueError is raised with descriptive message

- [x] 3. Checkpoint - Verify normalization functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement ChordAggregator
  - [x] 4.1 Create ChordAggregator class with initialization
    - Implement `__init__` method accepting strategy and tolerance
    - Store aggregation strategy and tolerance configuration
    - _Requirements: 2.7, 5.4, 5.5_
  
  - [x] 4.2 Implement interval chord collection logic
    - Write helper method to find chords within timestamp interval
    - Apply tolerance to interval boundaries
    - Return list of (chord, timestamp) tuples in interval
    - _Requirements: 2.1, 2.7_
  
  - [x] 4.3 Implement chord selection strategies
    - Write `_select_chord_by_strategy` method
    - Implement MOST_FREQUENT: count occurrences, return most common
    - Implement LONGEST_DURATION: calculate durations, return longest
    - Implement FIRST: return first chord in interval
    - Implement LAST: return last chord in interval
    - _Requirements: 2.2, 2.3, 2.4, 2.5_
  
  - [x] 4.4 Implement nearest chord fallback
    - Write `_find_nearest_chord` method for empty intervals
    - Find chord with minimum time distance to interval start
    - _Requirements: 2.6_
  
  - [x] 4.5 Implement aggregate method
    - Write `aggregate` method with input validation
    - Validate chord count matches timestamp count
    - Validate timestamps are sorted in ascending order
    - Validate timestamps are non-negative
    - Iterate through target timestamp intervals
    - Collect chords in each interval and select by strategy
    - Return aggregated chord list matching target timestamp count
    - _Requirements: 2.1, 2.8, 2.9, 2.10, 6.2, 6.4, 6.5, 8.4, 8.5_
  
  - [ ]* 4.6 Write property test for aggregated chord count
    - **Property 7: Aggregated chord count matches target**
    - **Validates: Requirements 2.1, 2.8**
    - Generate random predicted chords and timestamps
    - Verify len(aggregate(pred, pred_t, target_t)) == len(target_t)
  
  - [ ]* 4.7 Write property test for MOST_FREQUENT strategy
    - **Property 8: Most frequent strategy correctness**
    - **Validates: Requirements 2.2**
    - Generate intervals with known chord frequencies
    - Verify selected chord is the most frequent in interval
  
  - [ ]* 4.8 Write property test for LONGEST_DURATION strategy
    - **Property 9: Longest duration strategy correctness**
    - **Validates: Requirements 2.3**
    - Generate intervals with known chord durations
    - Verify selected chord has longest duration in interval
  
  - [ ]* 4.9 Write property test for FIRST strategy
    - **Property 10: First strategy correctness**
    - **Validates: Requirements 2.4**
    - Generate intervals with multiple chords
    - Verify selected chord is the first in interval
  
  - [ ]* 4.10 Write property test for LAST strategy
    - **Property 11: Last strategy correctness**
    - **Validates: Requirements 2.5**
    - Generate intervals with multiple chords
    - Verify selected chord is the last in interval
  
  - [ ]* 4.11 Write property test for timestamp order preservation
    - **Property 12: Timestamp order preservation**
    - **Validates: Requirements 8.4**
    - Generate random timestamps
    - Verify aggregated chords maintain temporal order
  
  - [ ]* 4.12 Write property test for tolerance application
    - **Property 13: Tolerance application**
    - **Validates: Requirements 2.7**
    - Generate chords near interval boundaries
    - Verify chords within tolerance are included in interval
  
  - [ ]* 4.13 Write property test for length mismatch error detection
    - **Property 21: Length mismatch error detection**
    - **Validates: Requirements 2.9, 6.2**
    - Generate mismatched chord and timestamp lists
    - Verify ValueError is raised
  
  - [ ]* 4.14 Write property test for unsorted timestamp error detection
    - **Property 22: Unsorted timestamp error detection**
    - **Validates: Requirements 2.10, 6.4**
    - Generate unsorted timestamp lists
    - Verify ValueError is raised
  
  - [ ]* 4.15 Write property test for negative timestamp error detection
    - **Property 23: Negative timestamp error detection**
    - **Validates: Requirements 6.5**
    - Generate negative timestamps
    - Verify ValueError is raised

- [x] 5. Checkpoint - Verify aggregation functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement PreprocessingPipeline
  - [x] 6.1 Create PreprocessingPipeline class with initialization
    - Implement `__init__` method accepting PreprocessingConfig
    - Initialize ChordNormalizer with config.normalization_mode
    - Initialize ChordAggregator with config.aggregation_strategy and tolerance
    - Store configuration
    - _Requirements: 3.1, 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 6.2 Implement preprocess method
    - Write `preprocess` method accepting predicted, ground_truth, and optional timestamps
    - Validate input: raise ValueError for empty chord lists
    - Apply normalization if enabled (both predicted and ground_truth)
    - Apply aggregation if enabled and timestamps provided
    - Skip aggregation if timestamps not provided
    - Return tuple of (processed_predicted, processed_ground_truth)
    - Ensure processing order: normalization before aggregation
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 6.3_
  
  - [ ]* 6.3 Write property test for normalization application
    - **Property 14: Normalization applied when enabled**
    - **Validates: Requirements 3.2**
    - Generate random chord lists with config.enable_normalization=True
    - Verify both predicted and ground_truth are normalized
  
  - [ ]* 6.4 Write property test for aggregation application
    - **Property 15: Aggregation applied when enabled**
    - **Validates: Requirements 3.3**
    - Generate chord lists with timestamps and config.enable_aggregation=True
    - Verify predicted chords are aggregated to ground_truth resolution
  
  - [ ]* 6.5 Write property test for processing order
    - **Property 16: Processing order guarantee**
    - **Validates: Requirements 3.4**
    - Generate chords requiring both normalization and aggregation
    - Verify normalization is applied before aggregation
  
  - [ ]* 6.6 Write property test for identity when disabled
    - **Property 17: Identity when disabled**
    - **Validates: Requirements 3.5**
    - Generate chord lists with both features disabled
    - Verify output equals input
  
  - [ ]* 6.7 Write property test for aggregation skip without timestamps
    - **Property 18: Aggregation skip without timestamps**
    - **Validates: Requirements 3.6**
    - Generate chord lists without timestamps
    - Verify aggregation is skipped even if enabled
  
  - [ ]* 6.8 Write property test for return type guarantee
    - **Property 19: Return type guarantee**
    - **Validates: Requirements 3.7**
    - Generate various inputs
    - Verify return value is always a tuple of two lists

- [x] 7. Checkpoint - Verify pipeline integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Integrate preprocessing with BenchmarkTool
  - [x] 8.1 Add preprocessing pipeline field to BenchmarkTool
    - Add `preprocessing_pipeline` optional field to BenchmarkTool class
    - Initialize to None by default
    - _Requirements: 4.1, 4.3_
  
  - [x] 8.2 Implement set_preprocessing_pipeline method
    - Write method to configure preprocessing pipeline
    - Accept PreprocessingPipeline or None
    - Store pipeline instance
    - _Requirements: 4.1_
  
  - [x] 8.3 Modify run_benchmark to apply preprocessing
    - Check if preprocessing_pipeline is configured
    - If configured, call preprocess before evaluation
    - Pass preprocessed chords to Evaluator
    - If not configured, use original chords
    - _Requirements: 4.2, 4.3, 4.5_
  
  - [x] 8.4 Add preprocessing enable/disable option
    - Add optional parameter to run_benchmark for preprocessing control
    - Allow temporary override of pipeline configuration
    - _Requirements: 4.4_
  
  - [ ]* 8.5 Write integration test for BenchmarkTool preprocessing
    - Test with preprocessing enabled and disabled
    - Verify preprocessed chords are passed to evaluator
    - Verify evaluation results improve with preprocessing
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 9. Add error handling and logging
  - [x] 9.1 Implement comprehensive error messages
    - Add descriptive error messages for all ValueError cases
    - Include context information (input values, expected format)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 9.2 Add logging for error conditions
    - Import logging module
    - Add logger to each class
    - Log errors with ERROR level before raising exceptions
    - Log warnings for edge cases (empty intervals, fallback to nearest)
    - _Requirements: 6.6_
  
  - [x] 9.3 Add input validation and constraints
    - Validate chord string length (max 100 characters)
    - Validate timestamp range (0 to 10,000 seconds)
    - Validate chord count limit (max 100,000)
    - _Requirements: 7.4, 7.5, 7.6_

- [ ] 10. Add comprehensive documentation
  - [x] 10.1 Write docstrings for all classes and methods
    - Add module-level docstring explaining preprocessing functionality
    - Add class docstrings with usage examples
    - Add method docstrings with Args, Returns, Raises sections
    - Follow Google or NumPy docstring style
    - _Requirements: 10.1_
  
  - [x] 10.2 Create usage examples
    - Add examples to module docstring
    - Create example scripts in examples/ directory
    - Show basic usage, configuration options, and BenchmarkTool integration
    - _Requirements: 10.2_
  
  - [x] 10.3 Document configuration options
    - Document each PreprocessingConfig field
    - Explain normalization modes and their effects
    - Explain aggregation strategies and when to use each
    - Document default values and recommended settings
    - _Requirements: 10.3_
  
  - [x] 10.4 Document error messages
    - Create error message reference
    - Explain common error scenarios and solutions
    - _Requirements: 10.4_
  
  - [x] 10.5 Document performance characteristics
    - Document time complexity for each operation
    - Document space complexity
    - Document performance targets and benchmarks
    - _Requirements: 10.5_

- [ ] 11. Performance optimization and validation
  - [x] 11.1 Implement binary search for timestamp lookup
    - Replace linear search with binary search in aggregation
    - Reduce time complexity from O(n*m) to O(n*log(m))
    - _Requirements: 7.1, 7.2_
  
  - [x] 11.2 Add normalization result caching
    - Implement LRU cache for normalize method
    - Cache size: 1000 entries
    - Reduce redundant normalization of repeated chords
    - _Requirements: 7.1, 7.2_
  
  - [x] 11.3 Write performance benchmark tests
    - Test 3009→125 chord aggregation completes in <100ms
    - Test 10,000 chord normalization completes in <500ms
    - Test memory usage stays O(n)
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [ ]* 11.4 Write integration test with real song data
    - Use actual benchmark data (3009 predicted, 125 ground truth)
    - Verify preprocessing improves evaluation metrics
    - Compare results with and without preprocessing
    - Measure performance on real data
    - _Requirements: 9.5, 7.1_

- [x] 12. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Integration tests ensure the preprocessing system works correctly with BenchmarkTool
- Performance tests validate the system meets the specified performance targets
- The implementation follows the design document's Python specifications
- All 23 correctness properties from the design are covered by property-based tests
