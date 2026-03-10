"""Cache Manager - Manages analysis result caching"""

import json
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

from src.models import AudioAnalysisResult, ChordSegment, LyricSegment, ChordQuality

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching of audio analysis results"""
    
    def __init__(self, cache_dir: Path = Path("cache")):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"CacheManager initialized with cache_dir: {cache_dir}")
    
    def _generate_cache_key(self, audio_file_path: Path) -> str:
        """
        Generate cache key from audio file path and content
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Cache key (hash string)
        """
        # Use file path and modification time for cache key
        file_stat = audio_file_path.stat()
        key_string = f"{audio_file_path.absolute()}_{file_stat.st_mtime}_{file_stat.st_size}"
        
        # Generate SHA256 hash
        cache_key = hashlib.sha256(key_string.encode()).hexdigest()
        
        return cache_key
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get cache file path for a given cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def has_cache(self, audio_file_path: Path) -> bool:
        """
        Check if cache exists for audio file
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            True if cache exists, False otherwise
        """
        cache_key = self._generate_cache_key(audio_file_path)
        cache_file = self._get_cache_file_path(cache_key)
        
        exists = cache_file.exists()
        logger.info(f"Cache check for {audio_file_path.name}: {'exists' if exists else 'not found'}")
        
        return exists
    
    def save_cache(
        self,
        audio_file_path: Path,
        analysis_result: AudioAnalysisResult
    ) -> None:
        """
        Save analysis result to cache
        
        Args:
            audio_file_path: Path to audio file
            analysis_result: Analysis result to cache
        """
        cache_key = self._generate_cache_key(audio_file_path)
        cache_file = self._get_cache_file_path(cache_key)
        
        # Serialize analysis result
        cache_data = {
            "audio_file": str(audio_file_path.absolute()),
            "cached_at": datetime.now().isoformat(),
            "chord_progression": [
                {
                    "start_time": chord.start_time,
                    "end_time": chord.end_time,
                    "root": chord.root,
                    "quality": chord.quality.value,
                    "bass_note": chord.bass_note,
                    "extensions": chord.extensions,
                    "confidence": chord.confidence
                }
                for chord in analysis_result.chord_progression
            ],
            "lyrics": [
                {
                    "start_time": lyric.start_time,
                    "end_time": lyric.end_time,
                    "text": lyric.text,
                    "confidence": lyric.confidence
                }
                for lyric in analysis_result.lyrics
            ],
            "tempo": analysis_result.tempo,
            "key": analysis_result.key,
            "time_signature": list(analysis_result.time_signature)
        }
        
        # Write to cache file
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Cache saved for {audio_file_path.name} (key: {cache_key})")
    
    def load_cache(self, audio_file_path: Path) -> Optional[AudioAnalysisResult]:
        """
        Load analysis result from cache
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Cached analysis result, or None if not found
        """
        if not self.has_cache(audio_file_path):
            return None
        
        cache_key = self._generate_cache_key(audio_file_path)
        cache_file = self._get_cache_file_path(cache_key)
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Deserialize chord progression
            chord_progression = [
                ChordSegment(
                    start_time=chord["start_time"],
                    end_time=chord["end_time"],
                    root=chord["root"],
                    quality=ChordQuality(chord["quality"]),
                    bass_note=chord.get("bass_note"),
                    extensions=chord.get("extensions", []),
                    confidence=chord["confidence"]
                )
                for chord in cache_data["chord_progression"]
            ]
            
            # Deserialize lyrics
            lyrics = [
                LyricSegment(
                    start_time=lyric["start_time"],
                    end_time=lyric["end_time"],
                    text=lyric["text"],
                    confidence=lyric["confidence"]
                )
                for lyric in cache_data["lyrics"]
            ]
            
            # Create analysis result
            analysis_result = AudioAnalysisResult(
                chord_progression=chord_progression,
                lyrics=lyrics,
                tempo=cache_data["tempo"],
                key=cache_data["key"],
                time_signature=tuple(cache_data["time_signature"])
            )
            
            logger.info(f"Cache loaded for {audio_file_path.name}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return None
    
    def clear_cache(self, audio_file_path: Optional[Path] = None) -> None:
        """
        Clear cache for specific file or all cache
        
        Args:
            audio_file_path: Path to audio file, or None to clear all cache
        """
        if audio_file_path is None:
            # Clear all cache
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("All cache cleared")
        else:
            # Clear specific cache
            cache_key = self._generate_cache_key(audio_file_path)
            cache_file = self._get_cache_file_path(cache_key)
            
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"Cache cleared for {audio_file_path.name}")
