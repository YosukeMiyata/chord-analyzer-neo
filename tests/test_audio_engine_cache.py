"""Tests for AudioProcessingEngine cache integration (Requirements 8.2-8.5)"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.audio_engine import AudioProcessingEngine
from src.models import AudioAnalysisResult, ChordSegment, LyricSegment, ChordQuality


@pytest.fixture
def cache_dir(tmp_path):
    """Create temporary cache directory"""
    return tmp_path / "cache"


@pytest.fixture
def audio_engine(cache_dir):
    """Create AudioProcessingEngine instance with test cache directory"""
    return AudioProcessingEngine(cache_dir=cache_dir)


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
            )
        ],
        lyrics=[
            LyricSegment(
                start_time=0.0,
                end_time=2.0,
                text="Test lyrics",
                confidence=0.90
            )
        ],
        tempo=120.0,
        key="C",
        time_signature=(4, 4)
    )


class TestCacheCheckOnLoad:
    """Test cache existence check when audio file is loaded (Requirement 8.2)"""
    
    def test_analyze_audio_checks_cache_existence(self, audio_engine, tmp_path):
        """Test that analyze_audio checks for cache existence"""
        # Create mock audio file
        audio_file = tmp_path / "test.wav"
        audio_file.write_text("dummy")
        
        # Mock the audio engine state
        audio_engine.audio_data = Mock()
        audio_engine.current_file_path = audio_file
        
        # Mock cache manager
        audio_engine.cache_manager.has_cache = Mock(return_value=False)
        
        # Attempt analysis (will fail at _perform_new_analysis, but that's ok)
        try:
            audio_engine.analyze_audio(use_cache=True)
        except NotImplementedError:
            pass  # Expected since analysis is not implemented yet
        
        # Verify cache existence was checked
        audio_engine.cache_manager.has_cache.assert_called_once_with(audio_file)


class TestLoadFromCache:
    """Test loading analysis results from cache (Requirement 8.3)"""
    
    def test_analyze_audio_loads_from_cache_when_exists(
        self, 
        audio_engine, 
        tmp_path,
        sample_analysis_result
    ):
        """Test that analyze_audio loads from cache when valid cache exists"""
        # Create mock audio file
        audio_file = tmp_path / "test.wav"
        audio_file.write_text("dummy")
        
        # Mock the audio engine state
        audio_engine.audio_data = Mock()
        audio_engine.current_file_path = audio_file
        
        # Mock cache manager to return cached result
        audio_engine.cache_manager.has_cache = Mock(return_value=True)
        audio_engine.cache_manager.load_cache = Mock(return_value=sample_analysis_result)
        
        # Perform analysis
        result = audio_engine.analyze_audio(use_cache=True)
        
        # Verify cache was checked and loaded
        audio_engine.cache_manager.has_cache.assert_called_once_with(audio_file)
        audio_engine.cache_manager.load_cache.assert_called_once_with(audio_file)
        
        # Verify result is from cache
        assert result == sample_analysis_result
    
    def test_analyze_audio_performs_new_analysis_when_cache_load_fails(
        self, 
        audio_engine, 
        tmp_path
    ):
        """Test that analyze_audio performs new analysis when cache load fails"""
        # Create mock audio file
        audio_file = tmp_path / "test.wav"
        audio_file.write_text("dummy")
        
        # Mock the audio engine state
        audio_engine.audio_data = Mock()
        audio_engine.current_file_path = audio_file
        
        # Mock cache manager: cache exists but load returns None (corrupted)
        audio_engine.cache_manager.has_cache = Mock(return_value=True)
        audio_engine.cache_manager.load_cache = Mock(return_value=None)
        
        # Attempt analysis (will fail at _perform_new_analysis)
        try:
            audio_engine.analyze_audio(use_cache=True)
        except NotImplementedError:
            pass  # Expected
        
        # Verify cache load was attempted
        audio_engine.cache_manager.load_cache.assert_called_once_with(audio_file)


class TestNewAnalysisWhenNoCacheExists:
    """Test new analysis execution when cache doesn't exist (Requirement 8.4)"""
    
    def test_analyze_audio_performs_new_analysis_when_no_cache(
        self, 
        audio_engine, 
        tmp_path
    ):
        """Test that analyze_audio performs new analysis when cache doesn't exist"""
        # Create mock audio file
        audio_file = tmp_path / "test.wav"
        audio_file.write_text("dummy")
        
        # Mock the audio engine state
        audio_engine.audio_data = Mock()
        audio_engine.current_file_path = audio_file
        
        # Mock cache manager: no cache exists
        audio_engine.cache_manager.has_cache = Mock(return_value=False)
        audio_engine.cache_manager.load_cache = Mock()  # Add mock for load_cache
        
        # Attempt analysis (will fail at _perform_new_analysis)
        try:
            audio_engine.analyze_audio(use_cache=True)
        except NotImplementedError:
            pass  # Expected
        
        # Verify cache was checked
        audio_engine.cache_manager.has_cache.assert_called_once_with(audio_file)
        
        # Verify load_cache was NOT called (no cache exists)
        audio_engine.cache_manager.load_cache.assert_not_called()


class TestCacheInvalidationOption:
    """Test cache invalidation option (Requirement 8.5)"""
    
    def test_analyze_audio_always_performs_new_analysis_when_cache_disabled(
        self, 
        audio_engine, 
        tmp_path,
        sample_analysis_result
    ):
        """Test that analyze_audio always performs new analysis when use_cache=False"""
        # Create mock audio file
        audio_file = tmp_path / "test.wav"
        audio_file.write_text("dummy")
        
        # Mock the audio engine state
        audio_engine.audio_data = Mock()
        audio_engine.current_file_path = audio_file
        
        # Mock cache manager: cache exists
        audio_engine.cache_manager.has_cache = Mock(return_value=True)
        audio_engine.cache_manager.load_cache = Mock(return_value=sample_analysis_result)
        
        # Attempt analysis with cache disabled (will fail at _perform_new_analysis)
        try:
            audio_engine.analyze_audio(use_cache=False)
        except NotImplementedError:
            pass  # Expected
        
        # Verify cache was NOT checked or loaded
        audio_engine.cache_manager.has_cache.assert_not_called()
        audio_engine.cache_manager.load_cache.assert_not_called()
    
    def test_analyze_audio_bypasses_cache_when_use_cache_false(
        self, 
        audio_engine, 
        tmp_path
    ):
        """Test that use_cache=False bypasses all cache operations"""
        # Create mock audio file
        audio_file = tmp_path / "test.wav"
        audio_file.write_text("dummy")
        
        # Mock the audio engine state
        audio_engine.audio_data = Mock()
        audio_engine.current_file_path = audio_file
        
        # Create spies on cache manager methods
        has_cache_spy = Mock(return_value=True)
        load_cache_spy = Mock(return_value=Mock())
        
        audio_engine.cache_manager.has_cache = has_cache_spy
        audio_engine.cache_manager.load_cache = load_cache_spy
        
        # Attempt analysis with cache disabled
        try:
            audio_engine.analyze_audio(use_cache=False)
        except NotImplementedError:
            pass
        
        # Verify no cache operations were performed
        assert has_cache_spy.call_count == 0
        assert load_cache_spy.call_count == 0


class TestAnalyzeAudioErrorHandling:
    """Test error handling in analyze_audio"""
    
    def test_analyze_audio_raises_error_when_no_audio_loaded(self, audio_engine):
        """Test analyze_audio raises RuntimeError when no audio is loaded"""
        with pytest.raises(RuntimeError, match="No audio file loaded"):
            audio_engine.analyze_audio()
    
    def test_analyze_audio_raises_error_when_no_file_path(self, audio_engine):
        """Test analyze_audio raises RuntimeError when no file path is available"""
        # Set audio data but not file path
        audio_engine.audio_data = Mock()
        audio_engine.current_file_path = None
        
        with pytest.raises(RuntimeError, match="No audio file path available"):
            audio_engine.analyze_audio()


class TestCacheManagerIntegration:
    """Test CacheManager is properly integrated into AudioProcessingEngine"""
    
    def test_audio_engine_initializes_cache_manager(self, cache_dir):
        """Test AudioProcessingEngine initializes CacheManager"""
        engine = AudioProcessingEngine(cache_dir=cache_dir)
        assert engine.cache_manager is not None
        assert engine.cache_manager.cache_dir == cache_dir
    
    def test_audio_engine_uses_default_cache_dir(self):
        """Test AudioProcessingEngine uses default cache directory"""
        engine = AudioProcessingEngine()
        assert engine.cache_manager is not None
        assert engine.cache_manager.cache_dir == Path("cache")
