# Requirements Document: Evaluation System

## Introduction

評価システムは、コード認識エンジンの精度を測定し、パラメータを最適化するための包括的なベンチマークフレームワークです。開発者が複数の楽曲に対してシステムの性能を定量的に評価し、最適なパラメータ設定を発見できるようにします。

## Glossary

- **System**: 評価システム全体
- **Parser**: 正解データパーサー（Ground Truth Parser）
- **Evaluator**: 評価器（予測結果と正解データを比較）
- **Benchmark_Tool**: ベンチマークツール（複数楽曲の一括評価）
- **Optimizer**: パラメータ最適化器
- **Ground_Truth**: 正解データ（コード進行の正しい答え）
- **Predicted_Chords**: 予測されたコード（システムが認識したコード）
- **Chord_Annotation**: コードアノテーション（コード名と位置情報）
- **Evaluation_Metrics**: 評価指標（精度を測定する複数の指標）
- **DTW**: Dynamic Time Warping（時間的ずれを考慮した距離計算）

## Requirements

### Requirement 1: Ground Truth Parsing

**User Story:** As a developer, I want to parse ground truth data from multiple formats, so that I can evaluate chord recognition accuracy against various data sources.

#### Acceptance Criteria

1. WHEN a chord-only format file is provided (e.g., `[D][AonC#][Bm7]`), THE Parser SHALL extract all chord annotations with sequential positions
2. WHEN a lyrics-with-chords format file is provided (e.g., `涙[D]があふれ[AonC#]る`), THE Parser SHALL extract chord annotations with character positions
3. WHEN a lyrics-only format file is provided, THE Parser SHALL return an empty list of annotations
4. WHEN the format type is not specified, THE Parser SHALL automatically detect the format type
5. WHEN empty brackets are encountered, THE Parser SHALL ignore them and continue processing
6. THE Parser SHALL ensure all extracted positions are monotonically increasing

### Requirement 2: Evaluation Metrics Calculation

**User Story:** As a developer, I want to calculate multiple evaluation metrics, so that I can assess chord recognition accuracy from different perspectives.

#### Acceptance Criteria

1. WHEN predicted chords and ground truth chords are provided, THE Evaluator SHALL calculate sequence accuracy (exact sequence match rate)
2. WHEN predicted chords and ground truth chords are provided, THE Evaluator SHALL calculate root note accuracy
3. WHEN predicted chords and ground truth chords are provided, THE Evaluator SHALL calculate chord quality accuracy (major, minor, 7th, etc.)
4. WHEN predicted chords and ground truth chords are provided, THE Evaluator SHALL calculate DTW distance for temporal alignment
5. WHEN predicted chords and ground truth chords are provided, THE Evaluator SHALL calculate exact match rate
6. THE Evaluator SHALL ensure all accuracy metrics are in the range [0.0, 1.0]
7. THE Evaluator SHALL ensure DTW distance is non-negative
8. WHEN predicted chords exactly match ground truth chords, THE Evaluator SHALL return perfect scores (1.0) for all accuracy metrics and zero DTW distance

### Requirement 3: Root Note Extraction

**User Story:** As a developer, I want to accurately extract root notes from chord names, so that root accuracy calculations are correct.

#### Acceptance Criteria

1. WHEN a simple chord is provided (e.g., "D", "Am"), THE System SHALL extract the root note correctly
2. WHEN a slash chord is provided (e.g., "AonC#"), THE System SHALL extract the first note as the root (e.g., "A")
3. WHEN a chord with quality suffix is provided (e.g., "Bm7", "Cmaj7"), THE System SHALL extract only the root note (e.g., "B", "C")
4. THE System SHALL handle both sharp (#) and flat (b) accidentals correctly

### Requirement 4: Chord Quality Recognition

**User Story:** As a developer, I want to identify chord qualities, so that I can measure how well the system recognizes chord types.

#### Acceptance Criteria

1. WHEN a major chord is provided, THE System SHALL identify it as major quality
2. WHEN a minor chord is provided (e.g., "Am", "Dm"), THE System SHALL identify it as minor quality
3. WHEN a seventh chord is provided (e.g., "D7", "Am7"), THE System SHALL identify it as seventh quality
4. WHEN a major seventh chord is provided (e.g., "Cmaj7"), THE System SHALL identify it as major seventh quality
5. THE System SHALL distinguish between different chord qualities for accuracy calculation

### Requirement 5: DTW Distance Calculation

**User Story:** As a developer, I want to calculate DTW distance between chord sequences, so that I can measure accuracy even when timing is slightly off.

#### Acceptance Criteria

1. WHEN two chord sequences are provided, THE Evaluator SHALL calculate the DTW distance using chord similarity
2. WHEN two identical chord sequences are provided, THE Evaluator SHALL return zero DTW distance
3. WHEN chord sequences have different lengths, THE Evaluator SHALL handle the alignment correctly
4. THE Evaluator SHALL use a chord distance function where identical chords have distance 0.0, same root different quality has distance 0.5, and different roots have distance 1.0
5. THE Evaluator SHALL normalize the DTW distance by the path length

### Requirement 6: Benchmark Execution

**User Story:** As a developer, I want to run benchmarks on multiple songs, so that I can evaluate system performance across a dataset.

#### Acceptance Criteria

1. WHEN audio directory and ground truth directory are provided, THE Benchmark_Tool SHALL process all matching file pairs
2. WHEN a file pair is missing (audio without ground truth or vice versa), THE Benchmark_Tool SHALL log a warning and skip that file
3. WHEN processing each song, THE Benchmark_Tool SHALL store the song name, metrics, predicted chords, and ground truth chords
4. THE Benchmark_Tool SHALL calculate aggregate statistics (mean, standard deviation, min, max) across all songs
5. WHEN benchmark execution completes, THE Benchmark_Tool SHALL return a list of results for all processed songs

### Requirement 7: Report Generation

**User Story:** As a developer, I want to generate evaluation reports, so that I can review and share benchmark results.

#### Acceptance Criteria

1. WHEN benchmark results are provided, THE Benchmark_Tool SHALL generate a report in JSON format
2. WHEN benchmark results are provided, THE Benchmark_Tool SHALL generate a report in Markdown format
3. THE Benchmark_Tool SHALL include aggregate statistics in the report
4. THE Benchmark_Tool SHALL include per-song detailed results in the report
5. WHEN an output path is specified, THE Benchmark_Tool SHALL save the report to that path

### Requirement 8: Parameter Optimization

**User Story:** As a developer, I want to automatically optimize system parameters, so that I can find the best configuration for chord recognition accuracy.

#### Acceptance Criteria

1. WHEN optimization configuration is provided, THE Optimizer SHALL perform grid search over the specified parameter ranges
2. WHEN evaluating each parameter combination, THE Optimizer SHALL run the full benchmark and calculate the target metric
3. THE Optimizer SHALL track the best parameter combination that achieves the highest target metric score
4. WHEN optimization completes, THE Optimizer SHALL return the optimal parameters and the achieved metric score
5. THE Optimizer SHALL ensure the achieved metric is greater than or equal to the baseline metric with default parameters

### Requirement 9: Format Detection

**User Story:** As a developer, I want automatic format detection, so that I don't need to manually specify the ground truth format.

#### Acceptance Criteria

1. WHEN content contains only bracketed chords with no other text, THE Parser SHALL detect it as chord-only format
2. WHEN content contains text with embedded bracketed chords, THE Parser SHALL detect it as lyrics-with-chords format
3. WHEN content contains text with no bracketed chords, THE Parser SHALL detect it as lyrics-only format
4. THE Parser SHALL return the detected format type as a string

### Requirement 10: Sequence Alignment

**User Story:** As a developer, I want to align predicted and ground truth sequences, so that evaluation is accurate even when sequence lengths differ.

#### Acceptance Criteria

1. WHEN predicted and ground truth sequences have different lengths, THE System SHALL align them before calculating metrics
2. THE System SHALL use an alignment strategy that minimizes distortion
3. WHEN sequences are aligned, THE System SHALL ensure both aligned sequences have the same length
4. THE System SHALL preserve the original sequences for reference in the results

### Requirement 11: Error Handling for Invalid Formats

**User Story:** As a developer, I want clear error messages for invalid ground truth formats, so that I can fix data issues quickly.

#### Acceptance Criteria

1. WHEN ground truth content is in an unrecognized format, THE Parser SHALL raise a ValueError with a descriptive message
2. WHEN ground truth content is empty, THE Parser SHALL raise a ValueError indicating no chords found
3. THE Parser SHALL provide format detection hints in error messages

### Requirement 12: Error Handling for File Operations

**User Story:** As a developer, I want robust file handling, so that benchmark execution continues even when individual files fail.

#### Acceptance Criteria

1. WHEN an audio file cannot be processed, THE Benchmark_Tool SHALL log the error with file name and exception details
2. WHEN an audio file fails, THE Benchmark_Tool SHALL skip that file and continue processing remaining files
3. WHEN a ground truth file cannot be read, THE Benchmark_Tool SHALL log the error and skip that file pair
4. THE Benchmark_Tool SHALL ensure file path validation to prevent path traversal attacks

### Requirement 13: Data Validation

**User Story:** As a developer, I want data validation for all inputs, so that the system fails fast with clear error messages.

#### Acceptance Criteria

1. WHEN a ChordAnnotation is created, THE System SHALL validate that the chord field is non-empty
2. WHEN a ChordAnnotation is created, THE System SHALL validate that the position is non-negative
3. WHEN EvaluationMetrics are created, THE System SHALL validate that all accuracy metrics are in range [0.0, 1.0]
4. WHEN EvaluationMetrics are created, THE System SHALL validate that DTW distance is non-negative
5. WHEN BenchmarkResult is created, THE System SHALL validate that song name is non-empty and chord lists are non-empty

### Requirement 14: Performance Optimization

**User Story:** As a developer, I want efficient benchmark execution, so that I can evaluate large datasets in reasonable time.

#### Acceptance Criteria

1. WHERE parallel processing is available, THE Benchmark_Tool SHALL process multiple songs concurrently
2. WHEN the same audio file is processed multiple times during optimization, THE System SHALL use caching to avoid redundant processing
3. THE System SHALL implement DTW calculation with O(n*m) complexity where n and m are sequence lengths
4. WHEN processing large datasets, THE System SHALL provide progress indicators

### Requirement 15: Security Constraints

**User Story:** As a developer, I want security safeguards, so that the evaluation system cannot be exploited.

#### Acceptance Criteria

1. WHEN file paths are provided, THE System SHALL validate them to prevent path traversal attacks
2. WHEN reading ground truth files, THE System SHALL enforce a maximum file size limit to prevent DoS attacks
3. WHEN processing regular expressions, THE System SHALL sanitize inputs to prevent regex injection attacks
4. THE System SHALL not execute arbitrary code from ground truth files
