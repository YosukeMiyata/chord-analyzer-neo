"""Benchmark tool for evaluating chord recognition across multiple songs.

This module provides the BenchmarkTool class for:
- Discovering and matching audio files with ground truth files
- Processing multiple songs in batch
- Generating evaluation reports
- Calculating aggregate statistics

Validates: Requirements 6.1, 6.2, 12.4, 15.1
"""

import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any

from .models import BenchmarkResult

# Configure logging
logger = logging.getLogger(__name__)


class BenchmarkTool:
    """Tool for running benchmarks on multiple songs.
    
    This class handles:
    - File discovery and matching between audio and ground truth directories
    - Path validation to prevent security issues
    - Batch processing of song pairs
    - Report generation and statistics aggregation
    
    Validates: Requirements 6.1, 6.2, 12.4, 15.1
    """
    
    def __init__(self):
        """Initialize the BenchmarkTool.

        Creates instances of the parser and evaluator for processing songs.
        """
        from .parser import GroundTruthParser
        from .evaluator import Evaluator

        self.parser = GroundTruthParser()
        self.evaluator = Evaluator()
    
    def discover_file_pairs(
        self,
        audio_dir: Path,
        ground_truth_dir: Path
    ) -> List[Tuple[Path, Path]]:
        """Discover and match audio files with ground truth files.
        
        This method:
        1. Scans both directories for files
        2. Matches files by name (e.g., "song1.mp3" matches "song1.txt")
        3. Logs warnings for missing pairs
        4. Validates file paths to prevent path traversal
        
        Args:
            audio_dir: Directory containing audio files
            ground_truth_dir: Directory containing ground truth files
            
        Returns:
            List of tuples (audio_path, ground_truth_path) for matched pairs
            
        Raises:
            ValueError: If directories don't exist or paths are invalid
            
        Validates: Requirements 6.1, 6.2, 12.4, 15.1
        """
        # Validate directories exist
        if not audio_dir.exists():
            raise ValueError(f"Audio directory does not exist: {audio_dir}")
        
        if not ground_truth_dir.exists():
            raise ValueError(f"Ground truth directory does not exist: {ground_truth_dir}")
        
        if not audio_dir.is_dir():
            raise ValueError(f"Audio path is not a directory: {audio_dir}")
        
        if not ground_truth_dir.is_dir():
            raise ValueError(f"Ground truth path is not a directory: {ground_truth_dir}")
        
        # Validate paths to prevent path traversal
        self._validate_path(audio_dir)
        self._validate_path(ground_truth_dir)
        
        # Discover audio files (common audio extensions)
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'}
        audio_files = {}
        
        for audio_file in audio_dir.iterdir():
            if audio_file.is_file() and audio_file.suffix.lower() in audio_extensions:
                # Validate each file path
                self._validate_path(audio_file)
                stem = audio_file.stem
                audio_files[stem] = audio_file
        
        logger.info(f"Found {len(audio_files)} audio files in {audio_dir}")
        
        # Discover ground truth files (common text extensions)
        ground_truth_extensions = {'.txt', '.lab', '.chord', '.chords'}
        ground_truth_files = {}
        
        for gt_file in ground_truth_dir.iterdir():
            if gt_file.is_file() and gt_file.suffix.lower() in ground_truth_extensions:
                # Validate each file path
                self._validate_path(gt_file)
                stem = gt_file.stem
                ground_truth_files[stem] = gt_file
        
        logger.info(f"Found {len(ground_truth_files)} ground truth files in {ground_truth_dir}")
        
        # Match files by stem name
        matched_pairs = []
        
        for stem, audio_path in audio_files.items():
            if stem in ground_truth_files:
                gt_path = ground_truth_files[stem]
                matched_pairs.append((audio_path, gt_path))
            else:
                logger.warning(f"No ground truth file found for audio: {audio_path.name}")
        
        # Check for ground truth files without matching audio
        for stem, gt_path in ground_truth_files.items():
            if stem not in audio_files:
                logger.warning(f"No audio file found for ground truth: {gt_path.name}")
        
        logger.info(f"Matched {len(matched_pairs)} file pairs")
        
        return matched_pairs
    
    def _validate_path(self, path: Path) -> None:
        """Validate file path to prevent path traversal attacks.
        
        This method checks for:
        - Path traversal patterns (../)
        - Absolute paths that escape the working directory
        - Symbolic links that point outside allowed directories
        
        Args:
            path: Path to validate
            
        Raises:
            ValueError: If path contains traversal patterns or is invalid
            
        Validates: Requirements 12.4, 15.1
        """
        try:
            # Resolve the path to its absolute form
            resolved_path = path.resolve()
            
            # Check for path traversal by ensuring the resolved path
            # doesn't contain ".." components
            path_str = str(resolved_path)
            
            # Check for suspicious patterns
            if ".." in path.parts:
                raise ValueError(f"Path contains traversal pattern: {path}")
            
            # Ensure the path is within the current working directory or its subdirectories
            # This prevents accessing files outside the project
            cwd = Path.cwd().resolve()
            
            # Check if the resolved path is relative to cwd
            try:
                resolved_path.relative_to(cwd)
            except ValueError:
                # Path is not relative to cwd, which might be okay for absolute paths
                # but we should be cautious
                logger.debug(f"Path is outside current working directory: {resolved_path}")
            
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid path: {path}. Error: {e}")
    def process_single_song(
        self,
        audio_path: Path,
        ground_truth_path: Path
    ) -> BenchmarkResult:
        """Process a single song pair (audio file + ground truth file).

        This method:
        1. Parses the ground truth file using GroundTruthParser
        2. Runs chord recognition on the audio file using audio_engine
        3. Uses the Evaluator to calculate metrics (handles alignment internally)
        4. Creates a BenchmarkResult object with all information
        5. Handles errors gracefully with detailed logging

        Args:
            audio_path: Path to the audio file
            ground_truth_path: Path to the ground truth file

        Returns:
            BenchmarkResult object containing metrics and chord sequences

        Raises:
            FileNotFoundError: If either file doesn't exist
            ValueError: If ground truth parsing fails or chord recognition fails
            RuntimeError: If audio processing fails

        Validates: Requirements 6.3, 12.1, 12.2, 12.3
        """
        import time
        from src.audio_engine import AudioProcessingEngine

        song_name = audio_path.stem
        start_time = time.time()

        try:
            # Step 1: Parse ground truth file
            logger.info(f"Processing song: {song_name}")
            logger.info(f"Step 1/3: Parsing ground truth file: {ground_truth_path.name}")

            try:
                with open(ground_truth_path, 'r', encoding='utf-8') as f:
                    ground_truth_content = f.read()

                # Parse ground truth (format auto-detection)
                ground_truth_annotations = self.parser.parse(ground_truth_content)
                ground_truth_chords = [ann.chord for ann in ground_truth_annotations]

                if not ground_truth_chords:
                    raise ValueError(f"No chords found in ground truth file: {ground_truth_path.name}")

                logger.info(f"Parsed {len(ground_truth_chords)} chords from ground truth")

            except FileNotFoundError as e:
                logger.error(f"Ground truth file not found: {ground_truth_path.name}. Error: {e}")
                raise
            except ValueError as e:
                logger.error(f"Failed to parse ground truth file: {ground_truth_path.name}. Error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error reading ground truth file: {ground_truth_path.name}. Error: {e}")
                raise RuntimeError(f"Failed to read ground truth file: {e}")

            # Step 2: Run chord recognition on audio file
            logger.info(f"Step 2/3: Running chord recognition on: {audio_path.name}")

            try:
                # Initialize audio engine
                audio_engine = AudioProcessingEngine()

                # Load audio file
                audio_engine.load_audio_file(audio_path)

                # Perform analysis
                analysis_result = audio_engine.analyze_audio(use_cache=True)

                # Extract predicted chords from chord progression
                predicted_chords = [segment.chord for segment in analysis_result.chord_progression]

                if not predicted_chords:
                    raise ValueError(f"No chords recognized in audio file: {audio_path.name}")

                logger.info(f"Recognized {len(predicted_chords)} chords from audio")

            except FileNotFoundError as e:
                logger.error(f"Audio file not found: {audio_path.name}. Error: {e}")
                raise
            except ValueError as e:
                logger.error(f"Failed to recognize chords in audio file: {audio_path.name}. Error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error processing audio file: {audio_path.name}. Error: {e}")
                raise RuntimeError(f"Failed to process audio file: {e}")

            # Step 3: Calculate metrics using Evaluator
            logger.info(f"Step 3/3: Calculating evaluation metrics")

            try:
                # Evaluator handles alignment internally if sequences have different lengths
                metrics = self.evaluator.evaluate(predicted_chords, ground_truth_chords)

                logger.info(
                    f"Metrics calculated - "
                    f"Root accuracy: {metrics.root_accuracy:.2%}, "
                    f"Quality accuracy: {metrics.quality_accuracy:.2%}, "
                    f"Exact match: {metrics.exact_match_rate:.2%}"
                )

            except Exception as e:
                logger.error(f"Failed to calculate metrics for song: {song_name}. Error: {e}")
                raise RuntimeError(f"Failed to calculate metrics: {e}")

            # Calculate processing time
            processing_time = time.time() - start_time

            # Step 4: Create BenchmarkResult
            result = BenchmarkResult(
                song_name=song_name,
                metrics=metrics,
                predicted_chords=predicted_chords,
                ground_truth_chords=ground_truth_chords,
                processing_time=processing_time
            )

            logger.info(f"Successfully processed song: {song_name} in {processing_time:.2f}s")

            return result

        except (FileNotFoundError, ValueError, RuntimeError) as e:
            # Log the error with file name and exception details
            logger.error(
                f"Failed to process song pair: "
                f"audio={audio_path.name}, "
                f"ground_truth={ground_truth_path.name}. "
                f"Error: {type(e).__name__}: {e}"
            )
            # Re-raise the exception so caller can handle it
            raise
        except Exception as e:
            # Catch any unexpected errors
            logger.error(
                f"Unexpected error processing song pair: "
                f"audio={audio_path.name}, "
                f"ground_truth={ground_truth_path.name}. "
                f"Error: {type(e).__name__}: {e}"
            )
            raise RuntimeError(f"Unexpected error processing song: {e}")

    
    def run_benchmark(
        self,
        audio_dir: Path,
        ground_truth_dir: Path
    ) -> List[BenchmarkResult]:
        """Run benchmark on multiple songs.
        
        This method:
        1. Discovers all matching audio/ground truth file pairs
        2. Processes each pair using process_single_song
        3. Continues processing even if individual songs fail
        4. Logs errors for failed songs with file names and exception details
        5. Returns list of BenchmarkResult objects for all successfully processed songs
        
        Args:
            audio_dir: Directory containing audio files
            ground_truth_dir: Directory containing ground truth files
            
        Returns:
            List of BenchmarkResult objects for all successfully processed songs
            
        Validates: Requirements 6.5, 12.1, 12.2, 12.3
        """
        logger.info(f"Starting benchmark run")
        logger.info(f"Audio directory: {audio_dir}")
        logger.info(f"Ground truth directory: {ground_truth_dir}")
        
        # Step 1: Discover all matching file pairs
        try:
            file_pairs = self.discover_file_pairs(audio_dir, ground_truth_dir)
            logger.info(f"Discovered {len(file_pairs)} file pairs to process")
        except Exception as e:
            logger.error(f"Failed to discover file pairs: {e}")
            raise
        
        if not file_pairs:
            logger.warning("No file pairs found to process")
            return []
        
        # Step 2: Process each file pair
        results = []
        failed_count = 0
        
        for i, (audio_path, ground_truth_path) in enumerate(file_pairs, 1):
            logger.info(f"Processing file pair {i}/{len(file_pairs)}: {audio_path.name}")
            
            try:
                # Process single song
                result = self.process_single_song(audio_path, ground_truth_path)
                results.append(result)
                logger.info(f"Successfully processed {audio_path.stem}")
                
            except FileNotFoundError as e:
                # File not found error - log and continue
                failed_count += 1
                logger.error(
                    f"File not found error for song pair {i}/{len(file_pairs)}: "
                    f"audio={audio_path.name}, ground_truth={ground_truth_path.name}. "
                    f"Error: {e}. Skipping this file pair."
                )
                continue
                
            except ValueError as e:
                # Validation error (e.g., no chords found) - log and continue
                failed_count += 1
                logger.error(
                    f"Validation error for song pair {i}/{len(file_pairs)}: "
                    f"audio={audio_path.name}, ground_truth={ground_truth_path.name}. "
                    f"Error: {e}. Skipping this file pair."
                )
                continue
                
            except RuntimeError as e:
                # Runtime error (e.g., audio processing failed) - log and continue
                failed_count += 1
                logger.error(
                    f"Runtime error for song pair {i}/{len(file_pairs)}: "
                    f"audio={audio_path.name}, ground_truth={ground_truth_path.name}. "
                    f"Error: {e}. Skipping this file pair."
                )
                continue
                
            except Exception as e:
                # Unexpected error - log with full details and continue
                failed_count += 1
                logger.error(
                    f"Unexpected error for song pair {i}/{len(file_pairs)}: "
                    f"audio={audio_path.name}, ground_truth={ground_truth_path.name}. "
                    f"Error type: {type(e).__name__}, Error: {e}. Skipping this file pair."
                )
                continue
        
        # Step 3: Log summary
        logger.info(f"Benchmark run completed")
        logger.info(f"Successfully processed: {len(results)}/{len(file_pairs)} songs")
        logger.info(f"Failed: {failed_count}/{len(file_pairs)} songs")
        
        return results
    
    def generate_report(
        self,
        results: List[BenchmarkResult],
        output_path: Path
    ) -> None:
        """Generate evaluation report.
        
        This method will be implemented in a later task to:
        1. Format results as JSON or Markdown
        2. Include aggregate statistics
        3. Include per-song details
        4. Save to specified path
        
        Args:
            results: List of benchmark results
            output_path: Path to save the report
            
        Validates: Requirements 7.1, 7.2, 7.5
        """
        # This will be implemented in later tasks
        raise NotImplementedError("generate_report will be implemented in later tasks")
    
    def aggregate_metrics(
        self,
        results: List[BenchmarkResult]
    ) -> Dict[str, float]:
        """Calculate aggregate statistics across all songs.
        
        This method calculates:
        1. Mean for each metric
        2. Standard deviation for each metric
        3. Min and max values for each metric
        
        Args:
            results: List of benchmark results
            
        Returns:
            Dictionary with aggregate statistics containing:
            - {metric}_mean: Mean value for each metric
            - {metric}_std: Standard deviation for each metric
            - {metric}_min: Minimum value for each metric
            - {metric}_max: Maximum value for each metric
            
        Validates: Requirements 6.4
        """
        import statistics
        
        # Handle empty results list
        if not results:
            logger.warning("No results provided for aggregate statistics calculation")
            return {}
        
        # Extract all metric values
        metric_names = [
            'sequence_accuracy',
            'root_accuracy',
            'quality_accuracy',
            'dtw_distance',
            'exact_match_rate'
        ]
        
        # Collect values for each metric
        metric_values = {name: [] for name in metric_names}
        
        for result in results:
            metric_values['sequence_accuracy'].append(result.metrics.sequence_accuracy)
            metric_values['root_accuracy'].append(result.metrics.root_accuracy)
            metric_values['quality_accuracy'].append(result.metrics.quality_accuracy)
            metric_values['dtw_distance'].append(result.metrics.dtw_distance)
            metric_values['exact_match_rate'].append(result.metrics.exact_match_rate)
        
        # Calculate aggregate statistics
        aggregates = {}
        
        for metric_name, values in metric_values.items():
            # Calculate mean
            mean_value = statistics.mean(values)
            aggregates[f"{metric_name}_mean"] = mean_value
            
            # Calculate standard deviation (use stdev if more than 1 value, else 0)
            if len(values) > 1:
                std_value = statistics.stdev(values)
            else:
                std_value = 0.0
            aggregates[f"{metric_name}_std"] = std_value
            
            # Calculate min and max
            min_value = min(values)
            max_value = max(values)
            aggregates[f"{metric_name}_min"] = min_value
            aggregates[f"{metric_name}_max"] = max_value
        
        logger.info(f"Calculated aggregate statistics for {len(results)} songs")
        
        return aggregates
