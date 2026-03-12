"""Tests for the BenchmarkTool class.

This module tests:
- File discovery and matching
- Path validation and security
- Warning logging for missing pairs

Validates: Requirements 6.1, 6.2, 12.4, 15.1
"""

import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch

from src.evaluation.benchmark import BenchmarkTool


class TestBenchmarkToolFileDiscovery:
    """Test file discovery and matching functionality."""
    
    def test_discover_matching_pairs(self, tmp_path):
        """Test discovering matching audio and ground truth file pairs.
        
        Validates: Requirement 6.1
        """
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create matching files
        (audio_dir / "song1.mp3").touch()
        (audio_dir / "song2.wav").touch()
        (audio_dir / "song3.flac").touch()
        
        (gt_dir / "song1.txt").touch()
        (gt_dir / "song2.txt").touch()
        (gt_dir / "song3.txt").touch()
        
        # Discover pairs
        tool = BenchmarkTool()
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        # Verify all pairs are found
        assert len(pairs) == 3
        
        # Verify pairs are correctly matched
        stems = {audio.stem for audio, gt in pairs}
        assert stems == {"song1", "song2", "song3"}
        
        # Verify each pair has matching stems
        for audio, gt in pairs:
            assert audio.stem == gt.stem
    
    def test_discover_with_missing_ground_truth(self, tmp_path, caplog):
        """Test that missing ground truth files are logged as warnings.
        
        Validates: Requirement 6.2
        """
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create audio files
        (audio_dir / "song1.mp3").touch()
        (audio_dir / "song2.wav").touch()
        (audio_dir / "song3.flac").touch()
        
        # Create only some ground truth files
        (gt_dir / "song1.txt").touch()
        # song2 and song3 are missing ground truth
        
        # Discover pairs with logging
        tool = BenchmarkTool()
        with caplog.at_level(logging.WARNING):
            pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        # Verify only matching pair is returned
        assert len(pairs) == 1
        assert pairs[0][0].stem == "song1"
        
        # Verify warnings were logged for missing ground truth
        warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
        assert any("song2.wav" in msg for msg in warning_messages)
        assert any("song3.flac" in msg for msg in warning_messages)
    
    def test_discover_with_missing_audio(self, tmp_path, caplog):
        """Test that missing audio files are logged as warnings.
        
        Validates: Requirement 6.2
        """
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create only some audio files
        (audio_dir / "song1.mp3").touch()
        
        # Create ground truth files
        (gt_dir / "song1.txt").touch()
        (gt_dir / "song2.txt").touch()
        (gt_dir / "song3.txt").touch()
        
        # Discover pairs with logging
        tool = BenchmarkTool()
        with caplog.at_level(logging.WARNING):
            pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        # Verify only matching pair is returned
        assert len(pairs) == 1
        assert pairs[0][0].stem == "song1"
        
        # Verify warnings were logged for missing audio
        warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
        assert any("song2.txt" in msg for msg in warning_messages)
        assert any("song3.txt" in msg for msg in warning_messages)
    
    def test_discover_multiple_audio_formats(self, tmp_path):
        """Test discovering audio files with various extensions.
        
        Validates: Requirement 6.1
        """
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create audio files with different extensions
        audio_formats = [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"]
        for i, ext in enumerate(audio_formats):
            (audio_dir / f"song{i}{ext}").touch()
            (gt_dir / f"song{i}.txt").touch()
        
        # Discover pairs
        tool = BenchmarkTool()
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        # Verify all formats are discovered
        assert len(pairs) == len(audio_formats)
    
    def test_discover_multiple_ground_truth_formats(self, tmp_path):
        """Test discovering ground truth files with various extensions.
        
        Validates: Requirement 6.1
        """
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create ground truth files with different extensions
        gt_formats = [".txt", ".lab", ".chord", ".chords"]
        for i, ext in enumerate(gt_formats):
            (audio_dir / f"song{i}.mp3").touch()
            (gt_dir / f"song{i}{ext}").touch()
        
        # Discover pairs
        tool = BenchmarkTool()
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        # Verify all formats are discovered
        assert len(pairs) == len(gt_formats)
    
    def test_discover_ignores_non_audio_files(self, tmp_path):
        """Test that non-audio files in audio directory are ignored.
        
        Validates: Requirement 6.1
        """
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create audio files and non-audio files
        (audio_dir / "song1.mp3").touch()
        (audio_dir / "readme.txt").touch()
        (audio_dir / "metadata.json").touch()
        (audio_dir / "image.jpg").touch()
        
        (gt_dir / "song1.txt").touch()
        
        # Discover pairs
        tool = BenchmarkTool()
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        # Verify only audio file is matched
        assert len(pairs) == 1
        assert pairs[0][0].name == "song1.mp3"
    
    def test_discover_empty_directories(self, tmp_path):
        """Test discovering files in empty directories.
        
        Validates: Requirement 6.1
        """
        # Create empty directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Discover pairs
        tool = BenchmarkTool()
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        # Verify no pairs are found
        assert len(pairs) == 0


class TestBenchmarkToolPathValidation:
    """Test path validation and security features."""
    
    def test_validate_path_traversal_in_parts(self, tmp_path):
        """Test that paths with .. in parts are rejected.
        
        Validates: Requirements 12.4, 15.1
        """
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create a file with .. in the path (simulated)
        tool = BenchmarkTool()
        
        # Test path with .. component
        bad_path = tmp_path / ".." / "audio"
        
        with pytest.raises(ValueError, match="traversal pattern"):
            tool._validate_path(bad_path)
    
    def test_nonexistent_audio_directory(self, tmp_path):
        """Test that nonexistent audio directory raises error.
        
        Validates: Requirement 12.4
        """
        # Create only ground truth directory
        gt_dir = tmp_path / "ground_truth"
        gt_dir.mkdir()
        
        audio_dir = tmp_path / "nonexistent"
        
        tool = BenchmarkTool()
        with pytest.raises(ValueError, match="Audio directory does not exist"):
            tool.discover_file_pairs(audio_dir, gt_dir)
    
    def test_nonexistent_ground_truth_directory(self, tmp_path):
        """Test that nonexistent ground truth directory raises error.
        
        Validates: Requirement 12.4
        """
        # Create only audio directory
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()
        
        gt_dir = tmp_path / "nonexistent"
        
        tool = BenchmarkTool()
        with pytest.raises(ValueError, match="Ground truth directory does not exist"):
            tool.discover_file_pairs(audio_dir, gt_dir)
    
    def test_audio_path_is_file_not_directory(self, tmp_path):
        """Test that audio path must be a directory.
        
        Validates: Requirement 12.4
        """
        # Create a file instead of directory
        audio_file = tmp_path / "audio.txt"
        audio_file.touch()
        
        gt_dir = tmp_path / "ground_truth"
        gt_dir.mkdir()
        
        tool = BenchmarkTool()
        with pytest.raises(ValueError, match="Audio path is not a directory"):
            tool.discover_file_pairs(audio_file, gt_dir)
    
    def test_ground_truth_path_is_file_not_directory(self, tmp_path):
        """Test that ground truth path must be a directory.
        
        Validates: Requirement 12.4
        """
        # Create audio directory
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()
        
        # Create a file instead of directory
        gt_file = tmp_path / "ground_truth.txt"
        gt_file.touch()
        
        tool = BenchmarkTool()
        with pytest.raises(ValueError, match="Ground truth path is not a directory"):
            tool.discover_file_pairs(audio_dir, gt_file)
    
    def test_case_insensitive_extension_matching(self, tmp_path):
        """Test that file extensions are matched case-insensitively.
        
        Validates: Requirement 6.1
        """
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create files with uppercase extensions
        (audio_dir / "song1.MP3").touch()
        (audio_dir / "song2.WAV").touch()
        (gt_dir / "song1.TXT").touch()
        (gt_dir / "song2.TXT").touch()
        
        # Discover pairs
        tool = BenchmarkTool()
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        # Verify pairs are found despite uppercase extensions
        assert len(pairs) == 2


class TestBenchmarkToolNotImplemented:
    """Test that unimplemented methods raise NotImplementedError."""
    
    def test_generate_report_json_implemented(self, tmp_path):
        """Test that generate_report with JSON format is now implemented."""
        tool = BenchmarkTool()
        output_path = tmp_path / "report.json"
        
        # JSON format should work (no longer raises NotImplementedError)
        tool.generate_report([], output_path, format='json')
        
        # Verify file was created
        assert output_path.exists()
class TestBenchmarkToolSingleSongProcessing:
    """Test single song processing functionality.

    Validates: Requirements 6.3, 12.1, 12.2, 12.3
    """

    def test_process_single_song_success(self, tmp_path):
        """Test successful processing of a single song pair.

        Validates: Requirement 6.3
        """
        from unittest.mock import Mock, patch
        from src.evaluation.models import ChordAnnotation, EvaluationMetrics

        # Create test files
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()

        audio_file = audio_dir / "test_song.mp3"
        gt_file = gt_dir / "test_song.txt"

        audio_file.touch()
        gt_file.write_text("[D][A][Bm7][G]")

        # Mock the audio engine and its methods
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            # Create mock instance
            mock_engine = Mock()
            MockEngine.return_value = mock_engine

            # Mock the analysis result
            mock_analysis = Mock()
            mock_chord_segment_1 = Mock()
            mock_chord_segment_1.chord = "D"
            mock_chord_segment_2 = Mock()
            mock_chord_segment_2.chord = "A"
            mock_chord_segment_3 = Mock()
            mock_chord_segment_3.chord = "Bm7"
            mock_chord_segment_4 = Mock()
            mock_chord_segment_4.chord = "G"

            mock_analysis.chord_progression = [
                mock_chord_segment_1,
                mock_chord_segment_2,
                mock_chord_segment_3,
                mock_chord_segment_4
            ]

            mock_engine.analyze_audio.return_value = mock_analysis

            # Process the song
            tool = BenchmarkTool()
            result = tool.process_single_song(audio_file, gt_file)

            # Verify result structure
            assert result.song_name == "test_song"
            assert len(result.predicted_chords) == 4
            assert len(result.ground_truth_chords) == 4
            assert result.predicted_chords == ["D", "A", "Bm7", "G"]
            assert result.ground_truth_chords == ["D", "A", "Bm7", "G"]

            # Verify metrics are calculated (perfect match)
            assert result.metrics.sequence_accuracy == 1.0
            assert result.metrics.root_accuracy == 1.0
            assert result.metrics.quality_accuracy == 1.0
            assert result.metrics.exact_match_rate == 1.0
            assert result.metrics.dtw_distance == 0.0

            # Verify processing time is recorded
            assert result.processing_time > 0

            # Verify audio engine was called correctly
            mock_engine.load_audio_file.assert_called_once_with(audio_file)
            mock_engine.analyze_audio.assert_called_once_with(use_cache=True)

    def test_process_single_song_with_mismatches(self, tmp_path):
        """Test processing a song with chord mismatches.

        Validates: Requirement 6.3
        """
        from unittest.mock import Mock, patch

        # Create test files
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()

        audio_file = audio_dir / "test_song.mp3"
        gt_file = gt_dir / "test_song.txt"

        audio_file.touch()
        gt_file.write_text("[D][A][Bm7][G]")

        # Mock the audio engine with different predictions
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine

            # Mock analysis with different chords
            mock_analysis = Mock()
            mock_chord_segment_1 = Mock()
            mock_chord_segment_1.chord = "C"  # Wrong
            mock_chord_segment_2 = Mock()
            mock_chord_segment_2.chord = "A"  # Correct
            mock_chord_segment_3 = Mock()
            mock_chord_segment_3.chord = "Em"  # Wrong
            mock_chord_segment_4 = Mock()
            mock_chord_segment_4.chord = "G"  # Correct

            mock_analysis.chord_progression = [
                mock_chord_segment_1,
                mock_chord_segment_2,
                mock_chord_segment_3,
                mock_chord_segment_4
            ]

            mock_engine.analyze_audio.return_value = mock_analysis

            # Process the song
            tool = BenchmarkTool()
            result = tool.process_single_song(audio_file, gt_file)

            # Verify result
            assert result.song_name == "test_song"
            assert result.predicted_chords == ["C", "A", "Em", "G"]
            assert result.ground_truth_chords == ["D", "A", "Bm7", "G"]

            # Verify metrics show imperfect match
            assert result.metrics.sequence_accuracy == 0.0  # Not exact sequence match
            assert result.metrics.exact_match_rate == 0.5  # 2 out of 4 match
            assert result.metrics.root_accuracy < 1.0
            assert result.metrics.quality_accuracy < 1.0

    def test_process_single_song_ground_truth_file_not_found(self, tmp_path):
        """Test handling of missing ground truth file.

        Validates: Requirements 12.1, 12.3
        """
        # Create only audio file
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()

        audio_file = audio_dir / "test_song.mp3"
        audio_file.touch()

        gt_file = tmp_path / "nonexistent.txt"

        # Process should raise FileNotFoundError
        tool = BenchmarkTool()
        with pytest.raises(FileNotFoundError):
            tool.process_single_song(audio_file, gt_file)

    def test_process_single_song_audio_file_not_found(self, tmp_path):
        """Test handling of missing audio file.

        Validates: Requirements 12.1, 12.2
        """
        from unittest.mock import Mock, patch

        # Create only ground truth file
        gt_dir = tmp_path / "ground_truth"
        gt_dir.mkdir()

        gt_file = gt_dir / "test_song.txt"
        gt_file.write_text("[D][A][Bm7][G]")

        audio_file = tmp_path / "nonexistent.mp3"

        # Mock AudioProcessingEngine to raise FileNotFoundError
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            mock_engine.load_audio_file.side_effect = FileNotFoundError("Audio file not found")

            # Process should raise FileNotFoundError
            tool = BenchmarkTool()
            with pytest.raises(FileNotFoundError):
                tool.process_single_song(audio_file, gt_file)

    def test_process_single_song_invalid_ground_truth_format(self, tmp_path):
        """Test handling of invalid ground truth format.

        Validates: Requirements 12.1, 12.3
        """
        from unittest.mock import Mock, patch

        # Create test files
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()

        audio_file = audio_dir / "test_song.mp3"
        gt_file = gt_dir / "test_song.txt"

        audio_file.touch()
        # Write invalid content (no chords)
        gt_file.write_text("This is just text without any chords")

        # Mock the audio engine
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine

            # Process should raise ValueError due to no chords in ground truth
            tool = BenchmarkTool()
            with pytest.raises(ValueError, match="No chords found"):
                tool.process_single_song(audio_file, gt_file)

    def test_process_single_song_chord_recognition_failure(self, tmp_path):
        """Test handling of chord recognition failure.

        Validates: Requirements 12.1, 12.2
        """
        from unittest.mock import Mock, patch

        # Create test files
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()

        audio_file = audio_dir / "test_song.mp3"
        gt_file = gt_dir / "test_song.txt"

        audio_file.touch()
        gt_file.write_text("[D][A][Bm7][G]")

        # Mock the audio engine to fail
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            mock_engine.analyze_audio.side_effect = RuntimeError("Audio processing failed")

            # Process should raise RuntimeError
            tool = BenchmarkTool()
            with pytest.raises(RuntimeError, match="Failed to process audio file"):
                tool.process_single_song(audio_file, gt_file)

    def test_process_single_song_no_chords_recognized(self, tmp_path):
        """Test handling when no chords are recognized from audio.

        Validates: Requirements 12.1, 12.2
        """
        from unittest.mock import Mock, patch

        # Create test files
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()

        audio_file = audio_dir / "test_song.mp3"
        gt_file = gt_dir / "test_song.txt"

        audio_file.touch()
        gt_file.write_text("[D][A][Bm7][G]")

        # Mock the audio engine to return empty chord progression
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine

            mock_analysis = Mock()
            mock_analysis.chord_progression = []  # Empty

            mock_engine.analyze_audio.return_value = mock_analysis

            # Process should raise ValueError
            tool = BenchmarkTool()
            with pytest.raises(ValueError, match="No chords recognized"):
                tool.process_single_song(audio_file, gt_file)

    def test_process_single_song_error_logging(self, tmp_path, caplog):
        """Test that errors are logged with file names and exception details.

        Validates: Requirements 12.1, 12.3
        """
        import logging

        # Create test files
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()

        audio_file = audio_dir / "test_song.mp3"
        gt_file = gt_dir / "test_song.txt"

        audio_file.touch()
        # Invalid ground truth (no chords)
        gt_file.write_text("No chords here")

        # Process and capture logs
        tool = BenchmarkTool()
        with caplog.at_level(logging.ERROR):
            try:
                tool.process_single_song(audio_file, gt_file)
            except ValueError:
                pass  # Expected

        # Verify error was logged with file name
        error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
        assert any("test_song.txt" in msg for msg in error_messages)
        assert any("No chords found" in msg for msg in error_messages)

    def test_process_single_song_with_different_sequence_lengths(self, tmp_path):
        """Test processing when predicted and ground truth have different lengths.

        The evaluator should handle alignment internally.

        Validates: Requirement 6.3
        """
        from unittest.mock import Mock, patch

        # Create test files
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()

        audio_file = audio_dir / "test_song.mp3"
        gt_file = gt_dir / "test_song.txt"

        audio_file.touch()
        gt_file.write_text("[D][A][Bm7][G]")  # 4 chords

        # Mock the audio engine with different length
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine

            # Mock analysis with only 3 chords
            mock_analysis = Mock()
            mock_chord_segment_1 = Mock()
            mock_chord_segment_1.chord = "D"
            mock_chord_segment_2 = Mock()
            mock_chord_segment_2.chord = "A"
            mock_chord_segment_3 = Mock()
            mock_chord_segment_3.chord = "G"

            mock_analysis.chord_progression = [
                mock_chord_segment_1,
                mock_chord_segment_2,
                mock_chord_segment_3
            ]

            mock_engine.analyze_audio.return_value = mock_analysis

            # Process the song
            tool = BenchmarkTool()
            result = tool.process_single_song(audio_file, gt_file)

            # Verify result (original sequences preserved)
            assert result.song_name == "test_song"
            assert len(result.predicted_chords) == 3
            assert len(result.ground_truth_chords) == 4

            # Verify metrics are calculated (evaluator handles alignment)
            assert isinstance(result.metrics.sequence_accuracy, float)
            assert isinstance(result.metrics.root_accuracy, float)
            assert isinstance(result.metrics.quality_accuracy, float)
            assert isinstance(result.metrics.exact_match_rate, float)
            assert isinstance(result.metrics.dtw_distance, float)




class TestBenchmarkToolBatchProcessing:
    """Test batch processing with error handling.
    
    Validates: Requirements 6.5, 12.1, 12.2, 12.3
    """
    
    def test_run_benchmark_success_all_songs(self, tmp_path):
        """Test successful batch processing of multiple songs.
        
        Validates: Requirement 6.5
        """
        from unittest.mock import Mock, patch
        
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create 3 song pairs
        for i in range(1, 4):
            (audio_dir / f"song{i}.mp3").touch()
            (gt_dir / f"song{i}.txt").write_text(f"[D][A][Bm7][G]")
        
        # Mock the audio engine
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            
            # Mock analysis result
            mock_analysis = Mock()
            mock_chord_segments = [Mock(chord=c) for c in ["D", "A", "Bm7", "G"]]
            mock_analysis.chord_progression = mock_chord_segments
            mock_engine.analyze_audio.return_value = mock_analysis
            
            # Run benchmark
            tool = BenchmarkTool()
            results = tool.run_benchmark(audio_dir, gt_dir)
            
            # Verify all songs were processed
            assert len(results) == 3
            assert {r.song_name for r in results} == {"song1", "song2", "song3"}
            
            # Verify each result has correct structure
            for result in results:
                assert len(result.predicted_chords) == 4
                assert len(result.ground_truth_chords) == 4
                assert result.metrics.sequence_accuracy == 1.0
                assert result.processing_time > 0
    
    def test_run_benchmark_continues_on_individual_failures(self, tmp_path):
        """Test that benchmark continues processing when individual songs fail.
        
        Validates: Requirements 12.1, 12.2
        """
        from unittest.mock import Mock, patch
        
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create 3 song pairs
        (audio_dir / "song1.mp3").touch()
        (gt_dir / "song1.txt").write_text("[D][A][Bm7][G]")
        
        (audio_dir / "song2.mp3").touch()
        (gt_dir / "song2.txt").write_text("[C][G][Am][F]")
        
        (audio_dir / "song3.mp3").touch()
        (gt_dir / "song3.txt").write_text("[E][B][C#m][A]")
        
        # Mock the audio engine to fail on song2
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            
            # Create a side effect that fails on second call
            call_count = [0]
            
            def analyze_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 2:  # Fail on song2
                    raise RuntimeError("Audio processing failed")
                
                # Success for other songs
                mock_analysis = Mock()
                mock_chord_segments = [Mock(chord=c) for c in ["D", "A", "Bm7", "G"]]
                mock_analysis.chord_progression = mock_chord_segments
                return mock_analysis
            
            mock_engine.analyze_audio.side_effect = analyze_side_effect
            
            # Run benchmark
            tool = BenchmarkTool()
            results = tool.run_benchmark(audio_dir, gt_dir)
            
            # Verify only 2 songs were successfully processed (song2 failed)
            assert len(results) == 2
            assert {r.song_name for r in results} == {"song1", "song3"}
    
    def test_run_benchmark_logs_errors_with_file_names(self, tmp_path, caplog):
        """Test that errors are logged with file names and exception details.
        
        Validates: Requirements 12.1, 12.3
        """
        import logging
        from unittest.mock import Mock, patch
        
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create 2 song pairs
        (audio_dir / "song1.mp3").touch()
        (gt_dir / "song1.txt").write_text("[D][A][Bm7][G]")
        
        (audio_dir / "song2.mp3").touch()
        (gt_dir / "song2.txt").write_text("No chords here")  # Invalid format
        
        # Mock the audio engine
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            
            mock_analysis = Mock()
            mock_chord_segments = [Mock(chord=c) for c in ["D", "A", "Bm7", "G"]]
            mock_analysis.chord_progression = mock_chord_segments
            mock_engine.analyze_audio.return_value = mock_analysis
            
            # Run benchmark with logging
            tool = BenchmarkTool()
            with caplog.at_level(logging.ERROR):
                results = tool.run_benchmark(audio_dir, gt_dir)
            
            # Verify only song1 was processed (song2 failed due to invalid format)
            assert len(results) == 1
            assert results[0].song_name == "song1"
            
            # Verify error was logged with file name and exception details
            error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
            assert any("song2.txt" in msg for msg in error_messages)
            assert any("No chords found" in msg for msg in error_messages)
    
    def test_run_benchmark_returns_empty_list_when_no_pairs(self, tmp_path):
        """Test that empty list is returned when no file pairs are found.
        
        Validates: Requirement 6.5
        """
        # Create empty directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Run benchmark
        tool = BenchmarkTool()
        results = tool.run_benchmark(audio_dir, gt_dir)
        
        # Verify empty list is returned
        assert results == []
    
    def test_run_benchmark_returns_empty_list_when_all_fail(self, tmp_path):
        """Test that empty list is returned when all songs fail to process.
        
        Validates: Requirements 12.1, 12.2
        """
        from unittest.mock import Mock, patch
        
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create 2 song pairs with invalid ground truth
        (audio_dir / "song1.mp3").touch()
        (gt_dir / "song1.txt").write_text("No chords")
        
        (audio_dir / "song2.mp3").touch()
        (gt_dir / "song2.txt").write_text("Also no chords")
        
        # Run benchmark
        tool = BenchmarkTool()
        results = tool.run_benchmark(audio_dir, gt_dir)
        
        # Verify empty list is returned
        assert results == []
    
    def test_run_benchmark_handles_file_not_found_errors(self, tmp_path, caplog):
        """Test handling of FileNotFoundError during processing.
        
        Validates: Requirements 12.1, 12.2
        """
        import logging
        from unittest.mock import Mock, patch
        
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create song pairs
        (audio_dir / "song1.mp3").touch()
        (gt_dir / "song1.txt").write_text("[D][A][Bm7][G]")
        
        (audio_dir / "song2.mp3").touch()
        (gt_dir / "song2.txt").write_text("[C][G][Am][F]")
        
        # Mock the audio engine to raise FileNotFoundError on song2
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            
            call_count = [0]
            
            def load_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 2:  # Fail on song2
                    raise FileNotFoundError("Audio file not found")
            
            mock_engine.load_audio_file.side_effect = load_side_effect
            
            mock_analysis = Mock()
            mock_chord_segments = [Mock(chord=c) for c in ["D", "A", "Bm7", "G"]]
            mock_analysis.chord_progression = mock_chord_segments
            mock_engine.analyze_audio.return_value = mock_analysis
            
            # Run benchmark with logging
            tool = BenchmarkTool()
            with caplog.at_level(logging.ERROR):
                results = tool.run_benchmark(audio_dir, gt_dir)
            
            # Verify only song1 was processed
            assert len(results) == 1
            assert results[0].song_name == "song1"
            
            # Verify error was logged
            error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
            assert any("song2.mp3" in msg for msg in error_messages)
            assert any("File not found" in msg for msg in error_messages)
    
    def test_run_benchmark_handles_value_errors(self, tmp_path, caplog):
        """Test handling of ValueError during processing.
        
        Validates: Requirements 12.1, 12.3
        """
        import logging
        from unittest.mock import Mock, patch
        
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create song pairs
        (audio_dir / "song1.mp3").touch()
        (gt_dir / "song1.txt").write_text("[D][A][Bm7][G]")
        
        (audio_dir / "song2.mp3").touch()
        (gt_dir / "song2.txt").write_text("[C][G][Am][F]")
        
        # Mock the audio engine to return empty chords on song2
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            
            call_count = [0]
            
            def analyze_side_effect(*args, **kwargs):
                call_count[0] += 1
                mock_analysis = Mock()
                
                if call_count[0] == 2:  # Empty chords on song2
                    mock_analysis.chord_progression = []
                else:
                    mock_chord_segments = [Mock(chord=c) for c in ["D", "A", "Bm7", "G"]]
                    mock_analysis.chord_progression = mock_chord_segments
                
                return mock_analysis
            
            mock_engine.analyze_audio.side_effect = analyze_side_effect
            
            # Run benchmark with logging
            tool = BenchmarkTool()
            with caplog.at_level(logging.ERROR):
                results = tool.run_benchmark(audio_dir, gt_dir)
            
            # Verify only song1 was processed
            assert len(results) == 1
            assert results[0].song_name == "song1"
            
            # Verify error was logged
            error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
            assert any("song2.mp3" in msg for msg in error_messages)
            assert any("No chords recognized" in msg for msg in error_messages)
    
    def test_run_benchmark_handles_runtime_errors(self, tmp_path, caplog):
        """Test handling of RuntimeError during processing.
        
        Validates: Requirements 12.1, 12.2
        """
        import logging
        from unittest.mock import Mock, patch
        
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create song pairs
        (audio_dir / "song1.mp3").touch()
        (gt_dir / "song1.txt").write_text("[D][A][Bm7][G]")
        
        (audio_dir / "song2.mp3").touch()
        (gt_dir / "song2.txt").write_text("[C][G][Am][F]")
        
        # Mock the audio engine to raise RuntimeError on song2
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            
            call_count = [0]
            
            def analyze_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 2:  # Fail on song2
                    raise RuntimeError("Audio processing failed")
                
                mock_analysis = Mock()
                mock_chord_segments = [Mock(chord=c) for c in ["D", "A", "Bm7", "G"]]
                mock_analysis.chord_progression = mock_chord_segments
                return mock_analysis
            
            mock_engine.analyze_audio.side_effect = analyze_side_effect
            
            # Run benchmark with logging
            tool = BenchmarkTool()
            with caplog.at_level(logging.ERROR):
                results = tool.run_benchmark(audio_dir, gt_dir)
            
            # Verify only song1 was processed
            assert len(results) == 1
            assert results[0].song_name == "song1"
            
            # Verify error was logged
            error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
            assert any("song2.mp3" in msg for msg in error_messages)
            assert any("Audio processing failed" in msg for msg in error_messages)
    
    def test_run_benchmark_handles_unexpected_errors(self, tmp_path, caplog):
        """Test handling of unexpected errors during processing.
        
        Validates: Requirements 12.1, 12.2
        """
        import logging
        from unittest.mock import Mock, patch
        
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create song pairs
        (audio_dir / "song1.mp3").touch()
        (gt_dir / "song1.txt").write_text("[D][A][Bm7][G]")
        
        (audio_dir / "song2.mp3").touch()
        (gt_dir / "song2.txt").write_text("[C][G][Am][F]")
        
        # Mock the audio engine to raise unexpected error on song2
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            
            call_count = [0]
            
            def analyze_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 2:  # Fail on song2 with unexpected error
                    raise KeyError("Unexpected error")
                
                mock_analysis = Mock()
                mock_chord_segments = [Mock(chord=c) for c in ["D", "A", "Bm7", "G"]]
                mock_analysis.chord_progression = mock_chord_segments
                return mock_analysis
            
            mock_engine.analyze_audio.side_effect = analyze_side_effect
            
            # Run benchmark with logging
            tool = BenchmarkTool()
            with caplog.at_level(logging.ERROR):
                results = tool.run_benchmark(audio_dir, gt_dir)
            
            # Verify only song1 was processed
            assert len(results) == 1
            assert results[0].song_name == "song1"
            
            # Verify error was logged with file name
            # Note: The KeyError is wrapped in RuntimeError by process_single_song
            error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
            assert any("song2.mp3" in msg for msg in error_messages)
            assert any("Unexpected error" in msg for msg in error_messages)
    
    def test_run_benchmark_logs_summary(self, tmp_path, caplog):
        """Test that benchmark logs summary of processed and failed songs.
        
        Validates: Requirement 6.5
        """
        import logging
        from unittest.mock import Mock, patch
        
        # Create test directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        # Create 3 song pairs
        for i in range(1, 4):
            (audio_dir / f"song{i}.mp3").touch()
            (gt_dir / f"song{i}.txt").write_text("[D][A][Bm7][G]")
        
        # Mock the audio engine to fail on song2
        with patch('src.audio_engine.AudioProcessingEngine') as MockEngine:
            mock_engine = Mock()
            MockEngine.return_value = mock_engine
            
            call_count = [0]
            
            def analyze_side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 2:  # Fail on song2
                    raise RuntimeError("Processing failed")
                
                mock_analysis = Mock()
                mock_chord_segments = [Mock(chord=c) for c in ["D", "A", "Bm7", "G"]]
                mock_analysis.chord_progression = mock_chord_segments
                return mock_analysis
            
            mock_engine.analyze_audio.side_effect = analyze_side_effect
            
            # Run benchmark with logging
            tool = BenchmarkTool()
            with caplog.at_level(logging.INFO):
                results = tool.run_benchmark(audio_dir, gt_dir)
            
            # Verify results
            assert len(results) == 2
            
            # Verify summary was logged
            info_messages = [record.message for record in caplog.records if record.levelname == "INFO"]
            assert any("Successfully processed: 2/3" in msg for msg in info_messages)
            assert any("Failed: 1/3" in msg for msg in info_messages)



class TestBenchmarkToolAggregateMetrics:
    """Test aggregate statistics calculation.
    
    Validates: Requirement 6.4
    """
    
    def test_aggregate_metrics_with_single_result(self):
        """Test aggregate statistics with a single result.
        
        With only one result, std should be 0 and min/max should equal mean.
        
        Validates: Requirement 6.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create a single result
        metrics = EvaluationMetrics(
            sequence_accuracy=0.8,
            root_accuracy=0.9,
            quality_accuracy=0.85,
            dtw_distance=0.15,
            exact_match_rate=0.75
        )
        
        result = BenchmarkResult(
            song_name="test_song",
            metrics=metrics,
            predicted_chords=["D", "A", "Bm7"],
            ground_truth_chords=["D", "A", "G"],
            processing_time=1.5
        )
        
        # Calculate aggregates
        tool = BenchmarkTool()
        aggregates = tool.aggregate_metrics([result])
        
        # Verify all metrics have mean, std, min, max
        assert "sequence_accuracy_mean" in aggregates
        assert "sequence_accuracy_std" in aggregates
        assert "sequence_accuracy_min" in aggregates
        assert "sequence_accuracy_max" in aggregates
        
        # Verify values for single result
        assert aggregates["sequence_accuracy_mean"] == 0.8
        assert aggregates["sequence_accuracy_std"] == 0.0  # Only one value
        assert aggregates["sequence_accuracy_min"] == 0.8
        assert aggregates["sequence_accuracy_max"] == 0.8
        
        assert aggregates["root_accuracy_mean"] == 0.9
        assert aggregates["root_accuracy_std"] == 0.0
        assert aggregates["root_accuracy_min"] == 0.9
        assert aggregates["root_accuracy_max"] == 0.9
        
        assert aggregates["quality_accuracy_mean"] == 0.85
        assert aggregates["dtw_distance_mean"] == 0.15
        assert aggregates["exact_match_rate_mean"] == 0.75
    
    def test_aggregate_metrics_with_multiple_results(self):
        """Test aggregate statistics with multiple results.
        
        Validates: Requirement 6.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create multiple results with different metrics
        results = [
            BenchmarkResult(
                song_name="song1",
                metrics=EvaluationMetrics(
                    sequence_accuracy=1.0,
                    root_accuracy=1.0,
                    quality_accuracy=1.0,
                    dtw_distance=0.0,
                    exact_match_rate=1.0
                ),
                predicted_chords=["D", "A"],
                ground_truth_chords=["D", "A"],
                processing_time=1.0
            ),
            BenchmarkResult(
                song_name="song2",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.5,
                    root_accuracy=0.8,
                    quality_accuracy=0.6,
                    dtw_distance=0.3,
                    exact_match_rate=0.5
                ),
                predicted_chords=["C", "G"],
                ground_truth_chords=["D", "A"],
                processing_time=1.5
            ),
            BenchmarkResult(
                song_name="song3",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.0,
                    root_accuracy=0.6,
                    quality_accuracy=0.4,
                    dtw_distance=0.5,
                    exact_match_rate=0.3
                ),
                predicted_chords=["E", "B"],
                ground_truth_chords=["D", "A"],
                processing_time=2.0
            )
        ]
        
        # Calculate aggregates
        tool = BenchmarkTool()
        aggregates = tool.aggregate_metrics(results)
        
        # Verify mean calculations
        # sequence_accuracy: (1.0 + 0.5 + 0.0) / 3 = 0.5
        assert aggregates["sequence_accuracy_mean"] == 0.5
        
        # root_accuracy: (1.0 + 0.8 + 0.6) / 3 = 0.8
        assert aggregates["root_accuracy_mean"] == 0.8
        
        # quality_accuracy: (1.0 + 0.6 + 0.4) / 3 ≈ 0.6667
        assert abs(aggregates["quality_accuracy_mean"] - 0.6667) < 0.001
        
        # dtw_distance: (0.0 + 0.3 + 0.5) / 3 ≈ 0.2667
        assert abs(aggregates["dtw_distance_mean"] - 0.2667) < 0.001
        
        # exact_match_rate: (1.0 + 0.5 + 0.3) / 3 = 0.6
        assert aggregates["exact_match_rate_mean"] == 0.6
        
        # Verify min/max calculations
        assert aggregates["sequence_accuracy_min"] == 0.0
        assert aggregates["sequence_accuracy_max"] == 1.0
        
        assert aggregates["root_accuracy_min"] == 0.6
        assert aggregates["root_accuracy_max"] == 1.0
        
        assert aggregates["quality_accuracy_min"] == 0.4
        assert aggregates["quality_accuracy_max"] == 1.0
        
        assert aggregates["dtw_distance_min"] == 0.0
        assert aggregates["dtw_distance_max"] == 0.5
        
        assert aggregates["exact_match_rate_min"] == 0.3
        assert aggregates["exact_match_rate_max"] == 1.0
        
        # Verify standard deviation is calculated (should be > 0 for varying values)
        assert aggregates["sequence_accuracy_std"] > 0
        assert aggregates["root_accuracy_std"] > 0
        assert aggregates["quality_accuracy_std"] > 0
        assert aggregates["dtw_distance_std"] > 0
        assert aggregates["exact_match_rate_std"] > 0
    
    def test_aggregate_metrics_with_empty_results(self):
        """Test aggregate statistics with empty results list.
        
        Should return empty dictionary and log warning.
        
        Validates: Requirement 6.4
        """
        import logging
        
        tool = BenchmarkTool()
        
        # Test with empty list
        aggregates = tool.aggregate_metrics([])
        
        # Should return empty dictionary
        assert aggregates == {}
    
    def test_aggregate_metrics_all_metrics_included(self):
        """Test that all 5 metrics are included in aggregates.
        
        Validates: Requirement 6.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create a result
        result = BenchmarkResult(
            song_name="test",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D"],
            ground_truth_chords=["D"],
            processing_time=1.0
        )
        
        # Calculate aggregates
        tool = BenchmarkTool()
        aggregates = tool.aggregate_metrics([result])
        
        # Verify all 5 metrics have 4 statistics each (mean, std, min, max)
        expected_metrics = [
            'sequence_accuracy',
            'root_accuracy',
            'quality_accuracy',
            'dtw_distance',
            'exact_match_rate'
        ]
        
        for metric in expected_metrics:
            assert f"{metric}_mean" in aggregates
            assert f"{metric}_std" in aggregates
            assert f"{metric}_min" in aggregates
            assert f"{metric}_max" in aggregates
        
        # Total should be 5 metrics * 4 statistics = 20 entries
        assert len(aggregates) == 20
    
    def test_aggregate_metrics_perfect_scores(self):
        """Test aggregate statistics when all results have perfect scores.
        
        Validates: Requirement 6.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create multiple results with perfect scores
        results = []
        for i in range(3):
            result = BenchmarkResult(
                song_name=f"song{i}",
                metrics=EvaluationMetrics(
                    sequence_accuracy=1.0,
                    root_accuracy=1.0,
                    quality_accuracy=1.0,
                    dtw_distance=0.0,
                    exact_match_rate=1.0
                ),
                predicted_chords=["D", "A"],
                ground_truth_chords=["D", "A"],
                processing_time=1.0
            )
            results.append(result)
        
        # Calculate aggregates
        tool = BenchmarkTool()
        aggregates = tool.aggregate_metrics(results)
        
        # All accuracy metrics should have mean=1.0, min=1.0, max=1.0, std=0.0
        for metric in ['sequence_accuracy', 'root_accuracy', 'quality_accuracy', 'exact_match_rate']:
            assert aggregates[f"{metric}_mean"] == 1.0
            assert aggregates[f"{metric}_min"] == 1.0
            assert aggregates[f"{metric}_max"] == 1.0
            assert aggregates[f"{metric}_std"] == 0.0
        
        # DTW distance should be 0.0 for all
        assert aggregates["dtw_distance_mean"] == 0.0
        assert aggregates["dtw_distance_min"] == 0.0
        assert aggregates["dtw_distance_max"] == 0.0
        assert aggregates["dtw_distance_std"] == 0.0
    
    def test_aggregate_metrics_worst_scores(self):
        """Test aggregate statistics when all results have worst scores.
        
        Validates: Requirement 6.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create multiple results with worst scores
        results = []
        for i in range(3):
            result = BenchmarkResult(
                song_name=f"song{i}",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.0,
                    root_accuracy=0.0,
                    quality_accuracy=0.0,
                    dtw_distance=1.0,
                    exact_match_rate=0.0
                ),
                predicted_chords=["D", "A"],
                ground_truth_chords=["C", "G"],
                processing_time=1.0
            )
            results.append(result)
        
        # Calculate aggregates
        tool = BenchmarkTool()
        aggregates = tool.aggregate_metrics(results)
        
        # All accuracy metrics should have mean=0.0, min=0.0, max=0.0, std=0.0
        for metric in ['sequence_accuracy', 'root_accuracy', 'quality_accuracy', 'exact_match_rate']:
            assert aggregates[f"{metric}_mean"] == 0.0
            assert aggregates[f"{metric}_min"] == 0.0
            assert aggregates[f"{metric}_max"] == 0.0
            assert aggregates[f"{metric}_std"] == 0.0
        
        # DTW distance should be 1.0 for all
        assert aggregates["dtw_distance_mean"] == 1.0
        assert aggregates["dtw_distance_min"] == 1.0
        assert aggregates["dtw_distance_max"] == 1.0
        assert aggregates["dtw_distance_std"] == 0.0
    
    def test_aggregate_metrics_standard_deviation_calculation(self):
        """Test that standard deviation is calculated correctly.
        
        Validates: Requirement 6.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        import statistics
        
        # Create results with known values for easy std calculation
        # Values: 0.2, 0.5, 0.8 for sequence_accuracy
        results = [
            BenchmarkResult(
                song_name="song1",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.2,
                    root_accuracy=0.5,
                    quality_accuracy=0.5,
                    dtw_distance=0.5,
                    exact_match_rate=0.5
                ),
                predicted_chords=["D"],
                ground_truth_chords=["D"],
                processing_time=1.0
            ),
            BenchmarkResult(
                song_name="song2",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.5,
                    root_accuracy=0.5,
                    quality_accuracy=0.5,
                    dtw_distance=0.5,
                    exact_match_rate=0.5
                ),
                predicted_chords=["D"],
                ground_truth_chords=["D"],
                processing_time=1.0
            ),
            BenchmarkResult(
                song_name="song3",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.8,
                    root_accuracy=0.5,
                    quality_accuracy=0.5,
                    dtw_distance=0.5,
                    exact_match_rate=0.5
                ),
                predicted_chords=["D"],
                ground_truth_chords=["D"],
                processing_time=1.0
            )
        ]
        
        # Calculate aggregates
        tool = BenchmarkTool()
        aggregates = tool.aggregate_metrics(results)
        
        # Calculate expected std manually
        values = [0.2, 0.5, 0.8]
        expected_std = statistics.stdev(values)
        
        # Verify std is calculated correctly
        assert abs(aggregates["sequence_accuracy_std"] - expected_std) < 0.001
        
        # For metrics with same values, std should be 0
        assert aggregates["root_accuracy_std"] == 0.0
        assert aggregates["quality_accuracy_std"] == 0.0
        assert aggregates["dtw_distance_std"] == 0.0
        assert aggregates["exact_match_rate_std"] == 0.0
    
    def test_aggregate_metrics_two_results(self):
        """Test aggregate statistics with exactly two results.
        
        Standard deviation should be calculated correctly with 2 values.
        
        Validates: Requirement 6.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        import statistics
        
        # Create two results
        results = [
            BenchmarkResult(
                song_name="song1",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.6,
                    root_accuracy=0.7,
                    quality_accuracy=0.8,
                    dtw_distance=0.2,
                    exact_match_rate=0.5
                ),
                predicted_chords=["D"],
                ground_truth_chords=["D"],
                processing_time=1.0
            ),
            BenchmarkResult(
                song_name="song2",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.8,
                    root_accuracy=0.9,
                    quality_accuracy=1.0,
                    dtw_distance=0.1,
                    exact_match_rate=0.7
                ),
                predicted_chords=["D"],
                ground_truth_chords=["D"],
                processing_time=1.0
            )
        ]
        
        # Calculate aggregates
        tool = BenchmarkTool()
        aggregates = tool.aggregate_metrics(results)
        
        # Verify mean
        assert aggregates["sequence_accuracy_mean"] == 0.7  # (0.6 + 0.8) / 2
        assert aggregates["root_accuracy_mean"] == 0.8  # (0.7 + 0.9) / 2
        
        # Verify min/max
        assert aggregates["sequence_accuracy_min"] == 0.6
        assert aggregates["sequence_accuracy_max"] == 0.8
        
        # Verify std is calculated (should be > 0)
        assert aggregates["sequence_accuracy_std"] > 0
        
        # Calculate expected std for sequence_accuracy
        expected_std = statistics.stdev([0.6, 0.8])
        assert abs(aggregates["sequence_accuracy_std"] - expected_std) < 0.001



class TestBenchmarkToolReportGeneration:
    """Test report generation functionality.
    
    Validates: Requirements 7.1, 7.3, 7.4, 7.5
    """
    
    def test_generate_json_report_success(self, tmp_path):
        """Test successful JSON report generation.
        
        Validates: Requirements 7.1, 7.3, 7.4, 7.5
        """
        import json
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create test results
        results = [
            BenchmarkResult(
                song_name="song1",
                metrics=EvaluationMetrics(
                    sequence_accuracy=1.0,
                    root_accuracy=1.0,
                    quality_accuracy=1.0,
                    dtw_distance=0.0,
                    exact_match_rate=1.0
                ),
                predicted_chords=["D", "A", "Bm7", "G"],
                ground_truth_chords=["D", "A", "Bm7", "G"],
                processing_time=1.5
            ),
            BenchmarkResult(
                song_name="song2",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.5,
                    root_accuracy=0.8,
                    quality_accuracy=0.6,
                    dtw_distance=0.3,
                    exact_match_rate=0.5
                ),
                predicted_chords=["C", "G", "Am", "F"],
                ground_truth_chords=["D", "A", "Bm7", "G"],
                processing_time=2.0
            )
        ]
        
        # Generate report
        output_path = tmp_path / "report.json"
        tool = BenchmarkTool()
        tool.generate_report(results, output_path, format='json')
        
        # Verify file was created
        assert output_path.exists()
        
        # Read and parse JSON
        with open(output_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Verify report structure
        assert 'summary' in report
        assert 'detailed_results' in report
        
        # Verify summary
        assert report['summary']['total_songs'] == 2
        assert 'aggregate_statistics' in report['summary']
        
        # Verify aggregate statistics are present
        agg_stats = report['summary']['aggregate_statistics']
        assert 'sequence_accuracy_mean' in agg_stats
        assert 'root_accuracy_mean' in agg_stats
        assert 'quality_accuracy_mean' in agg_stats
        assert 'dtw_distance_mean' in agg_stats
        assert 'exact_match_rate_mean' in agg_stats
        
        # Verify detailed results
        assert len(report['detailed_results']) == 2
        
        # Verify first song details
        song1 = report['detailed_results'][0]
        assert song1['song_name'] == 'song1'
        assert song1['metrics']['sequence_accuracy'] == 1.0
        assert song1['metrics']['root_accuracy'] == 1.0
        assert song1['predicted_chords'] == ["D", "A", "Bm7", "G"]
        assert song1['ground_truth_chords'] == ["D", "A", "Bm7", "G"]
        assert song1['processing_time'] == 1.5
        
        # Verify second song details
        song2 = report['detailed_results'][1]
        assert song2['song_name'] == 'song2'
        assert song2['metrics']['sequence_accuracy'] == 0.5
        assert song2['predicted_chords'] == ["C", "G", "Am", "F"]
        assert song2['ground_truth_chords'] == ["D", "A", "Bm7", "G"]
        assert song2['processing_time'] == 2.0
    
    def test_generate_json_report_with_empty_results(self, tmp_path):
        """Test JSON report generation with empty results list.
        
        Validates: Requirements 7.1, 7.5
        """
        import json
        
        # Generate report with empty results
        output_path = tmp_path / "empty_report.json"
        tool = BenchmarkTool()
        tool.generate_report([], output_path, format='json')
        
        # Verify file was created
        assert output_path.exists()
        
        # Read and parse JSON
        with open(output_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Verify report structure
        assert report['summary']['total_songs'] == 0
        assert report['summary']['aggregate_statistics'] == {}
        assert report['detailed_results'] == []
    
    def test_generate_json_report_with_single_result(self, tmp_path):
        """Test JSON report generation with a single result.
        
        Validates: Requirements 7.1, 7.3, 7.4, 7.5
        """
        import json
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create single result
        result = BenchmarkResult(
            song_name="test_song",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D", "A", "Bm7"],
            ground_truth_chords=["D", "A", "G"],
            processing_time=1.2
        )
        
        # Generate report
        output_path = tmp_path / "single_report.json"
        tool = BenchmarkTool()
        tool.generate_report([result], output_path, format='json')
        
        # Verify file was created
        assert output_path.exists()
        
        # Read and parse JSON
        with open(output_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Verify summary
        assert report['summary']['total_songs'] == 1
        
        # Verify aggregate statistics (with single result, std should be 0)
        agg_stats = report['summary']['aggregate_statistics']
        assert agg_stats['sequence_accuracy_mean'] == 0.8
        assert agg_stats['sequence_accuracy_std'] == 0.0
        assert agg_stats['sequence_accuracy_min'] == 0.8
        assert agg_stats['sequence_accuracy_max'] == 0.8
        
        # Verify detailed results
        assert len(report['detailed_results']) == 1
        assert report['detailed_results'][0]['song_name'] == 'test_song'
    
    def test_generate_json_report_all_metrics_included(self, tmp_path):
        """Test that all 5 metrics are included in JSON report.
        
        Validates: Requirements 7.3, 7.4
        """
        import json
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create result
        result = BenchmarkResult(
            song_name="test",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D"],
            ground_truth_chords=["D"],
            processing_time=1.0
        )
        
        # Generate report
        output_path = tmp_path / "metrics_report.json"
        tool = BenchmarkTool()
        tool.generate_report([result], output_path, format='json')
        
        # Read and parse JSON
        with open(output_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Verify all metrics are in detailed results
        song_metrics = report['detailed_results'][0]['metrics']
        assert 'sequence_accuracy' in song_metrics
        assert 'root_accuracy' in song_metrics
        assert 'quality_accuracy' in song_metrics
        assert 'dtw_distance' in song_metrics
        assert 'exact_match_rate' in song_metrics
        
        # Verify all metrics are in aggregate statistics
        agg_stats = report['summary']['aggregate_statistics']
        for metric in ['sequence_accuracy', 'root_accuracy', 'quality_accuracy', 
                       'dtw_distance', 'exact_match_rate']:
            assert f'{metric}_mean' in agg_stats
            assert f'{metric}_std' in agg_stats
            assert f'{metric}_min' in agg_stats
            assert f'{metric}_max' in agg_stats
    
    def test_generate_json_report_with_unicode_song_names(self, tmp_path):
        """Test JSON report generation with Unicode song names.
        
        Validates: Requirements 7.1, 7.5
        """
        import json
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create result with Japanese song name
        result = BenchmarkResult(
            song_name="涙があふれる",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D", "A"],
            ground_truth_chords=["D", "A"],
            processing_time=1.0
        )
        
        # Generate report
        output_path = tmp_path / "unicode_report.json"
        tool = BenchmarkTool()
        tool.generate_report([result], output_path, format='json')
        
        # Read and parse JSON
        with open(output_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Verify Unicode song name is preserved
        assert report['detailed_results'][0]['song_name'] == "涙があふれる"
    
    def test_generate_report_invalid_format(self, tmp_path):
        """Test that invalid format raises ValueError.
        
        Validates: Requirement 7.1
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        result = BenchmarkResult(
            song_name="test",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D"],
            ground_truth_chords=["D"],
            processing_time=1.0
        )
        
        output_path = tmp_path / "report.txt"
        tool = BenchmarkTool()
        
        # Should raise ValueError for invalid format
        with pytest.raises(ValueError, match="Invalid format"):
            tool.generate_report([result], output_path, format='xml')
    
    def test_generate_markdown_report_success(self, tmp_path):
        """Test successful Markdown report generation.
        
        Validates: Requirements 7.2, 7.3, 7.4, 7.5
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        result = BenchmarkResult(
            song_name="test",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D", "A", "Bm7"],
            ground_truth_chords=["D", "A", "Bm7"],
            processing_time=1.0
        )
        
        output_path = tmp_path / "report.md"
        tool = BenchmarkTool()
        
        # Generate markdown report
        tool.generate_report([result], output_path, format='markdown')
        
        # Verify file was created
        assert output_path.exists()
        
        # Read and verify content
        content = output_path.read_text(encoding='utf-8')
        
        # Verify title
        assert "# Chord Recognition Evaluation Report" in content
        
        # Verify summary section
        assert "## Summary" in content
        assert "**Total Songs Processed:** 1" in content
        
        # Verify aggregate statistics table
        assert "## Aggregate Statistics" in content
        assert "| Metric | Mean | Std Dev | Min | Max |" in content
        assert "Sequence Accuracy" in content
        assert "Root Accuracy" in content
        assert "Quality Accuracy" in content
        assert "DTW Distance" in content
        assert "Exact Match Rate" in content
        
        # Verify detailed results section
        assert "## Detailed Results by Song" in content
        assert "### 1. test" in content
        
        # Verify metrics are displayed
        assert "80.00%" in content  # sequence_accuracy
        assert "90.00%" in content  # root_accuracy
        assert "85.00%" in content  # quality_accuracy
        assert "0.1500" in content  # dtw_distance
        assert "75.00%" in content  # exact_match_rate
        assert "1.00s" in content   # processing_time
        
        # Verify chord sequences are displayed
        assert "**Predicted Chords:**" in content
        assert "D | A | Bm7" in content
        assert "**Ground Truth Chords:**" in content
    
    def test_generate_json_report_io_error(self, tmp_path):
        """Test handling of IO errors when writing JSON report.
        
        Validates: Requirement 7.5
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        result = BenchmarkResult(
            song_name="test",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D"],
            ground_truth_chords=["D"],
            processing_time=1.0
        )
        
        # Try to write to a directory (should fail)
        output_path = tmp_path / "subdir"
        output_path.mkdir()
        
        tool = BenchmarkTool()
        
        # Should raise IOError when trying to write to a directory
        with pytest.raises(IOError):
            tool.generate_report([result], output_path, format='json')
    
    def test_generate_json_report_preserves_chord_sequences(self, tmp_path):
        """Test that predicted and ground truth chord sequences are preserved in report.
        
        Validates: Requirements 7.4
        """
        import json
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create result with specific chord sequences
        predicted = ["D", "A", "Bm7", "G", "D", "A"]
        ground_truth = ["D", "AonC#", "Bm7", "G", "D", "A"]
        
        result = BenchmarkResult(
            song_name="test_song",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=predicted,
            ground_truth_chords=ground_truth,
            processing_time=1.5
        )
        
        # Generate report
        output_path = tmp_path / "chords_report.json"
        tool = BenchmarkTool()
        tool.generate_report([result], output_path, format='json')
        
        # Read and parse JSON
        with open(output_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Verify chord sequences are preserved exactly
        song_data = report['detailed_results'][0]
        assert song_data['predicted_chords'] == predicted
        assert song_data['ground_truth_chords'] == ground_truth
    
    def test_generate_json_report_processing_time_included(self, tmp_path):
        """Test that processing time is included in JSON report.
        
        Validates: Requirement 7.4
        """
        import json
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create result with specific processing time
        result = BenchmarkResult(
            song_name="test_song",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D", "A"],
            ground_truth_chords=["D", "A"],
            processing_time=2.5
        )
        
        # Generate report
        output_path = tmp_path / "time_report.json"
        tool = BenchmarkTool()
        tool.generate_report([result], output_path, format='json')
        
        # Read and parse JSON
        with open(output_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Verify processing time is included
        song_data = report['detailed_results'][0]
        assert 'processing_time' in song_data
        assert song_data['processing_time'] == 2.5


class TestMarkdownReportGeneration:
    """Test Markdown report generation functionality.
    
    Validates: Requirements 7.2, 7.3, 7.4, 7.5
    """
    
    def test_generate_markdown_report_empty_results(self, tmp_path):
        """Test markdown report generation with empty results list.
        
        Validates: Requirement 7.2
        """
        output_path = tmp_path / "empty_report.md"
        tool = BenchmarkTool()
        
        # Generate report with empty results
        tool.generate_report([], output_path, format='markdown')
        
        # Verify file was created
        assert output_path.exists()
        
        # Read and verify content
        content = output_path.read_text(encoding='utf-8')
        
        # Verify basic structure
        assert "# Chord Recognition Evaluation Report" in content
        assert "## Summary" in content
        assert "**Total Songs Processed:** 0" in content
        assert "*No results to display.*" in content
    
    def test_generate_markdown_report_single_song(self, tmp_path):
        """Test markdown report generation with a single song.
        
        Validates: Requirements 7.2, 7.3, 7.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        result = BenchmarkResult(
            song_name="test_song",
            metrics=EvaluationMetrics(
                sequence_accuracy=1.0,
                root_accuracy=1.0,
                quality_accuracy=1.0,
                dtw_distance=0.0,
                exact_match_rate=1.0
            ),
            predicted_chords=["D", "A", "Bm7", "G"],
            ground_truth_chords=["D", "A", "Bm7", "G"],
            processing_time=2.5
        )
        
        output_path = tmp_path / "single_song_report.md"
        tool = BenchmarkTool()
        
        # Generate report
        tool.generate_report([result], output_path, format='markdown')
        
        # Verify file was created
        assert output_path.exists()
        
        # Read and verify content
        content = output_path.read_text(encoding='utf-8')
        
        # Verify structure
        assert "# Chord Recognition Evaluation Report" in content
        assert "**Total Songs Processed:** 1" in content
        
        # Verify aggregate statistics (with single song, std dev should be 0)
        assert "## Aggregate Statistics" in content
        assert "0.00%" in content  # std dev for single song
        
        # Verify song details
        assert "### 1. test_song" in content
        assert "100.00%" in content  # perfect scores
        assert "0.0000" in content   # zero DTW distance
        assert "2.50s" in content    # processing time
        
        # Verify chord sequences
        assert "D | A | Bm7 | G" in content
    
    def test_generate_markdown_report_multiple_songs(self, tmp_path):
        """Test markdown report generation with multiple songs.
        
        Validates: Requirements 7.2, 7.3, 7.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        results = [
            BenchmarkResult(
                song_name="song1",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.8,
                    root_accuracy=0.9,
                    quality_accuracy=0.85,
                    dtw_distance=0.15,
                    exact_match_rate=0.75
                ),
                predicted_chords=["D", "A", "Bm7"],
                ground_truth_chords=["D", "A", "Bm7"],
                processing_time=1.0
            ),
            BenchmarkResult(
                song_name="song2",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.9,
                    root_accuracy=0.95,
                    quality_accuracy=0.92,
                    dtw_distance=0.08,
                    exact_match_rate=0.88
                ),
                predicted_chords=["C", "G", "Am", "F"],
                ground_truth_chords=["C", "G", "Am", "F"],
                processing_time=1.5
            ),
            BenchmarkResult(
                song_name="song3",
                metrics=EvaluationMetrics(
                    sequence_accuracy=0.7,
                    root_accuracy=0.85,
                    quality_accuracy=0.80,
                    dtw_distance=0.20,
                    exact_match_rate=0.70
                ),
                predicted_chords=["E", "B", "C#m"],
                ground_truth_chords=["E", "B", "C#m"],
                processing_time=2.0
            )
        ]
        
        output_path = tmp_path / "multiple_songs_report.md"
        tool = BenchmarkTool()
        
        # Generate report
        tool.generate_report(results, output_path, format='markdown')
        
        # Verify file was created
        assert output_path.exists()
        
        # Read and verify content
        content = output_path.read_text(encoding='utf-8')
        
        # Verify summary
        assert "**Total Songs Processed:** 3" in content
        
        # Verify aggregate statistics table exists
        assert "## Aggregate Statistics" in content
        assert "| Metric | Mean | Std Dev | Min | Max |" in content
        
        # Verify all three songs are listed
        assert "### 1. song1" in content
        assert "### 2. song2" in content
        assert "### 3. song3" in content
        
        # Verify each song has its chord sequences
        assert "D | A | Bm7" in content
        assert "C | G | Am | F" in content
        assert "E | B | C#m" in content
    
    def test_generate_markdown_report_preserves_chord_sequences(self, tmp_path):
        """Test that chord sequences are preserved in markdown report.
        
        Validates: Requirement 7.4
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        # Create result with specific chord sequences
        predicted = ["D", "AonC#", "Bm7", "G", "D", "A"]
        ground_truth = ["D", "A", "Bm7", "G", "D", "A"]
        
        result = BenchmarkResult(
            song_name="chord_test",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.83
            ),
            predicted_chords=predicted,
            ground_truth_chords=ground_truth,
            processing_time=1.5
        )
        
        output_path = tmp_path / "chords_report.md"
        tool = BenchmarkTool()
        
        # Generate report
        tool.generate_report([result], output_path, format='markdown')
        
        # Read content
        content = output_path.read_text(encoding='utf-8')
        
        # Verify chord sequences are preserved exactly
        predicted_str = " | ".join(predicted)
        ground_truth_str = " | ".join(ground_truth)
        
        assert predicted_str in content
        assert ground_truth_str in content
        assert "AonC#" in content  # Verify slash chord is preserved
    
    def test_generate_markdown_report_io_error(self, tmp_path):
        """Test handling of IO errors when writing markdown report.
        
        Validates: Requirement 7.5
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        result = BenchmarkResult(
            song_name="test",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D"],
            ground_truth_chords=["D"],
            processing_time=1.0
        )
        
        # Try to write to a directory (should fail)
        output_path = tmp_path / "subdir"
        output_path.mkdir()
        
        tool = BenchmarkTool()
        
        # Should raise IOError when trying to write to a directory
        with pytest.raises(IOError):
            tool.generate_report([result], output_path, format='markdown')
    
    def test_generate_markdown_report_formatting(self, tmp_path):
        """Test that markdown report has proper formatting.
        
        Validates: Requirements 7.2, 7.3
        """
        from src.evaluation.models import BenchmarkResult, EvaluationMetrics
        
        result = BenchmarkResult(
            song_name="format_test",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8765,
                root_accuracy=0.9234,
                quality_accuracy=0.8543,
                dtw_distance=0.1234,
                exact_match_rate=0.7890
            ),
            predicted_chords=["D", "A"],
            ground_truth_chords=["D", "A"],
            processing_time=1.234
        )
        
        output_path = tmp_path / "format_report.md"
        tool = BenchmarkTool()
        
        # Generate report
        tool.generate_report([result], output_path, format='markdown')
        
        # Read content
        content = output_path.read_text(encoding='utf-8')
        
        # Verify percentage formatting (2 decimal places)
        assert "87.65%" in content  # sequence_accuracy
        assert "92.34%" in content  # root_accuracy
        assert "85.43%" in content  # quality_accuracy
        assert "78.90%" in content  # exact_match_rate
        
        # Verify DTW distance formatting (4 decimal places)
        assert "0.1234" in content
        
        # Verify processing time formatting (2 decimal places)
        assert "1.23s" in content
        
        # Verify table structure
        assert "|--------|-------|" in content  # Table separator
        assert "| Metric | Value |" in content  # Table header
