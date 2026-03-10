"""Tests for CacheManager - Cache loading and validation"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from src.cache_manager import CacheManager
from src.models import AudioAnalysisResult, ChordSegment, LyricSegment, ChordQuality


@pytest.fixture
def cache_dir(tmp_path):
    """Create temporary cache directory"""
    return tmp_path / "cache"


@pytest.fixture
def cache_manager(cache_dir):
    """Create CacheManager instance"""
    return CacheManager(cache_dir=cache_dir)


@pytest.fixture
def sample_audio_file(tmp_path):
    """Create a sample audio file for testing"""
    audio_file = tmp_path / "test_audio.wav"
    audio_file.write_text("dummy audio content")
    return audio_file


@pytest.fixture
def sample_analysis_result():
    """Create sample analysis result"""
    return AudioAnalysisResult(
        chord_progression=[
            ChordSegment(
                start_time=0.0,
                end_time=2.0,
                root="C",
                quality=ChordQuality.MAJOR,
                confidence=0.95
            ),
            ChordSegment(
                start_time=2.0,
                end_time=4.0,
                root="G",
                quality=ChordQuality.DOMINANT7,
                bass_note="B",
                extensions=["9"],
                confidence=0.88
            )
        ],
        lyrics=[
            LyricSegment(
                start_time=0.0,
                end_time=2.0,
                text="Hello world",
                confidence=0.92
            )
        ],
        tempo=120.0,
        key="C",
        time_signature=(4, 4)
    )


class TestCacheExistence:
    """Test cache existence checking (Requirement 8.2)"""
    
    def test_has_cache_returns_false_when_no_cache(self, cache_manager, sample_audio_file):
        """Test has_cache returns False when cache doesn't exist"""
        assert cache_manager.has_cache(sample_audio_file) is False
    
    def test_has_cache_returns_true_after_save(
        self, 
        cache_manager, 
        sample_audio_file, 
        sample_analysis_result
    ):
        """Test has_cache returns True after saving cache"""
        cache_manager.save_cache(sample_audio_file, sample_analysis_result)
        assert cache_manager.has_cache(sample_audio_file) is True
    
    def test_has_cache_different_files(
        self, 
        cache_manager, 
        sample_audio_file, 
        sample_analysis_result,
        tmp_path
    ):
        """Test has_cache distinguishes between different files"""
        # Save cache for first file
        cache_manager.save_cache(sample_audio_file, sample_analysis_result)
        
        # Create second file
        other_file = tmp_path / "other_audio.wav"
        other_file.write_text("different content")
        
        # Cache should not exist for second file
        assert cache_manager.has_cache(other_file) is False


class TestCacheLoading:
    """Test cache loading functionality (Requirement 8.3)"""
    
    def test_load_cache_returns_none_when_no_cache(self, cache_manager, sample_audio_file):
        """Test load_cache returns None when cache doesn't exist"""
        result = cache_manager.load_cache(sample_audio_file)
        assert result is None
    
    def test_load_cache_returns_analysis_result(
        self, 
        cache_manager, 
        sample_audio_file, 
        sample_analysis_result
    ):
        """Test load_cache returns correct AudioAnalysisResult"""
        # Save cache
        cache_manager.save_cache(sample_audio_file, sample_analysis_result)
        
        # Load cache
        loaded_result = cache_manager.load_cache(sample_audio_file)
        
        # Verify result is not None
        assert loaded_result is not None
        
        # Verify chord progression
        assert len(loaded_result.chord_progression) == 2
        
        chord1 = loaded_result.chord_progression[0]
        assert chord1.start_time == 0.0
        assert chord1.end_time == 2.0
        assert chord1.root == "C"
        assert chord1.quality == ChordQuality.MAJOR
        assert chord1.confidence == 0.95
        assert chord1.bass_note is None
        assert chord1.extensions == []
        
        chord2 = loaded_result.chord_progression[1]
        assert chord2.start_time == 2.0
        assert chord2.end_time == 4.0
        assert chord2.root == "G"
        assert chord2.quality == ChordQuality.DOMINANT7
        assert chord2.bass_note == "B"
        assert chord2.extensions == ["9"]
        assert chord2.confidence == 0.88
        
        # Verify lyrics
        assert len(loaded_result.lyrics) == 1
        lyric = loaded_result.lyrics[0]
        assert lyric.start_time == 0.0
        assert lyric.end_time == 2.0
        assert lyric.text == "Hello world"
        assert lyric.confidence == 0.92
        
        # Verify tempo, key, time signature
        assert loaded_result.tempo == 120.0
        assert loaded_result.key == "C"
        assert loaded_result.time_signature == (4, 4)
    
    def test_load_cache_with_empty_lists(self, cache_manager, sample_audio_file):
        """Test loading cache with empty chord progression and lyrics"""
        empty_result = AudioAnalysisResult(
            chord_progression=[],
            lyrics=[],
            tempo=100.0,
            key="A",
            time_signature=(3, 4)
        )
        
        cache_manager.save_cache(sample_audio_file, empty_result)
        loaded_result = cache_manager.load_cache(sample_audio_file)
        
        assert loaded_result is not None
        assert len(loaded_result.chord_progression) == 0
        assert len(loaded_result.lyrics) == 0
        assert loaded_result.tempo == 100.0
        assert loaded_result.key == "A"
        assert loaded_result.time_signature == (3, 4)
    
    def test_load_cache_handles_corrupted_file(
        self, 
        cache_manager, 
        sample_audio_file,
        cache_dir
    ):
        """Test load_cache returns None for corrupted cache file"""
        # Create corrupted cache file
        cache_key = cache_manager._generate_cache_key(sample_audio_file)
        cache_file = cache_dir / f"{cache_key}.json"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text("invalid json content {{{")
        
        # Should return None for corrupted cache
        result = cache_manager.load_cache(sample_audio_file)
        assert result is None


class TestCacheInvalidation:
    """Test cache invalidation when file changes"""
    
    def test_cache_invalidated_on_file_modification(
        self, 
        cache_manager, 
        sample_audio_file, 
        sample_analysis_result
    ):
        """Test cache is invalidated when file is modified"""
        # Save cache
        cache_manager.save_cache(sample_audio_file, sample_analysis_result)
        assert cache_manager.has_cache(sample_audio_file) is True
        
        # Modify file (change content and modification time)
        import time
        time.sleep(0.01)  # Ensure modification time changes
        sample_audio_file.write_text("modified audio content")
        
        # Cache should no longer be valid (different modification time)
        assert cache_manager.has_cache(sample_audio_file) is False


class TestCacheClear:
    """Test cache clearing functionality"""
    
    def test_clear_specific_cache(
        self, 
        cache_manager, 
        sample_audio_file, 
        sample_analysis_result
    ):
        """Test clearing cache for specific file"""
        cache_manager.save_cache(sample_audio_file, sample_analysis_result)
        assert cache_manager.has_cache(sample_audio_file) is True
        
        cache_manager.clear_cache(sample_audio_file)
        assert cache_manager.has_cache(sample_audio_file) is False
    
    def test_clear_all_cache(
        self, 
        cache_manager, 
        sample_audio_file, 
        sample_analysis_result,
        tmp_path
    ):
        """Test clearing all cache"""
        # Create and cache multiple files
        file1 = sample_audio_file
        file2 = tmp_path / "audio2.wav"
        file2.write_text("content2")
        
        cache_manager.save_cache(file1, sample_analysis_result)
        cache_manager.save_cache(file2, sample_analysis_result)
        
        assert cache_manager.has_cache(file1) is True
        assert cache_manager.has_cache(file2) is True
        
        # Clear all cache
        cache_manager.clear_cache(None)
        
        assert cache_manager.has_cache(file1) is False
        assert cache_manager.has_cache(file2) is False


class TestCacheKeyGeneration:
    """Test cache key generation"""
    
    def test_same_file_generates_same_key(self, cache_manager, sample_audio_file):
        """Test same file generates same cache key"""
        key1 = cache_manager._generate_cache_key(sample_audio_file)
        key2 = cache_manager._generate_cache_key(sample_audio_file)
        assert key1 == key2
    
    def test_different_files_generate_different_keys(
        self, 
        cache_manager, 
        sample_audio_file,
        tmp_path
    ):
        """Test different files generate different cache keys"""
        file2 = tmp_path / "other.wav"
        file2.write_text("different content")
        
        key1 = cache_manager._generate_cache_key(sample_audio_file)
        key2 = cache_manager._generate_cache_key(file2)
        assert key1 != key2
    
    def test_modified_file_generates_different_key(
        self, 
        cache_manager, 
        sample_audio_file
    ):
        """Test modified file generates different cache key"""
        key1 = cache_manager._generate_cache_key(sample_audio_file)
        
        # Modify file
        import time
        time.sleep(0.01)
        sample_audio_file.write_text("modified content")
        
        key2 = cache_manager._generate_cache_key(sample_audio_file)
        assert key1 != key2
