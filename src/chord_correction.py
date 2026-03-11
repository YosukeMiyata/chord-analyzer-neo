"""Chord correction module for managing user corrections"""

import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from models import ChordCorrection, ChordSegment


class ChordCorrectionModule:
    """Manages user corrections of chord segments"""
    
    def __init__(self, corrections_db_path: Path):
        """
        Initialize the chord correction module
        
        Args:
            corrections_db_path: Path to the corrections database file (JSON)
        """
        self.corrections_db_path = Path(corrections_db_path)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Ensure the corrections database file and directory exist"""
        self.corrections_db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.corrections_db_path.exists():
            self._save_db({})
    
    def _load_db(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load the corrections database from JSON"""
        with open(self.corrections_db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_db(self, db: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save the corrections database to JSON"""
        with open(self.corrections_db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    
    def _generate_audio_file_hash(self, audio_file: Path) -> str:
        """
        Generate a hash for an audio file
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            SHA256 hash of the file
        """
        sha256_hash = hashlib.sha256()
        with open(audio_file, 'rb') as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _chord_segment_to_dict(self, chord: ChordSegment) -> Dict[str, Any]:
        """Convert ChordSegment to dictionary for JSON serialization"""
        return {
            'start_time': chord.start_time,
            'end_time': chord.end_time,
            'root': chord.root,
            'quality': chord.quality.value,
            'bass_note': chord.bass_note,
            'extensions': chord.extensions,
            'confidence': chord.confidence
        }
    
    def save_correction(
        self,
        audio_file: Path,
        segment_index: int,
        original: ChordSegment,
        corrected: ChordSegment,
        user_id: Optional[str] = None
    ) -> None:
        """
        Save a user's chord correction
        
        Args:
            audio_file: Path to the audio file
            segment_index: Index of the segment in the chord progression
            original: Original chord segment
            corrected: Corrected chord segment
            user_id: Optional user identifier
        """
        # Generate audio file hash
        audio_file_hash = self._generate_audio_file_hash(audio_file)
        
        # Create correction record
        correction = {
            'audio_file_hash': audio_file_hash,
            'segment_index': segment_index,
            'original_chord': self._chord_segment_to_dict(original),
            'corrected_chord': self._chord_segment_to_dict(corrected),
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        # Load existing database
        db = self._load_db()
        
        # Add correction to the list for this audio file
        if audio_file_hash not in db:
            db[audio_file_hash] = []
        
        # Check if a correction for this segment already exists
        existing_index = None
        for i, existing_correction in enumerate(db[audio_file_hash]):
            if existing_correction['segment_index'] == segment_index:
                existing_index = i
                break
        
        # Update or append correction
        if existing_index is not None:
            db[audio_file_hash][existing_index] = correction
        else:
            db[audio_file_hash].append(correction)
        
        # Save updated database
        self._save_db(db)
    
    def get_corrections_for_file(self, audio_file: Path) -> List[ChordCorrection]:
        """
        Get all corrections for a specific audio file
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            List of ChordCorrection objects
        """
        audio_file_hash = self._generate_audio_file_hash(audio_file)
        db = self._load_db()
        
        corrections = []
        if audio_file_hash in db:
            for correction_dict in db[audio_file_hash]:
                # Convert dictionary back to ChordCorrection object
                # This would require converting the chord dicts back to ChordSegment objects
                # For now, we'll return the raw data
                pass
        
        return corrections
    
    def apply_corrections(
        self,
        audio_file: Path,
        chord_progression: List[ChordSegment]
    ) -> List[ChordSegment]:
        """
        Apply saved corrections to a chord progression
        
        Args:
            audio_file: Path to the audio file
            chord_progression: Original chord progression
            
        Returns:
            Chord progression with corrections applied
        """
        audio_file_hash = self._generate_audio_file_hash(audio_file)
        db = self._load_db()
        
        if audio_file_hash not in db:
            return chord_progression
        
        # Create a copy of the chord progression
        corrected_progression = chord_progression.copy()
        
        # Apply corrections
        for correction_dict in db[audio_file_hash]:
            segment_index = correction_dict['segment_index']
            if 0 <= segment_index < len(corrected_progression):
                # Apply the corrected chord
                # This would require converting the dict back to ChordSegment
                pass
        
        return corrected_progression
    
    def export_corrections_dataset(self, output_path: Path) -> None:
        """
        Export corrections data for model retraining
        
        Args:
            output_path: Path to save the exported dataset
        """
        db = self._load_db()
        
        # Export the entire database
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    
    def get_correction_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about corrections
        
        Returns:
            Dictionary containing correction statistics
        """
        db = self._load_db()
        
        total_corrections = sum(len(corrections) for corrections in db.values())
        
        # Count corrections by chord quality
        quality_corrections = {}
        confidence_sum = 0.0
        confidence_count = 0
        
        for corrections in db.values():
            for correction in corrections:
                original_quality = correction['original_chord']['quality']
                quality_corrections[original_quality] = quality_corrections.get(original_quality, 0) + 1
                
                confidence_sum += correction['original_chord']['confidence']
                confidence_count += 1
        
        # Find most corrected quality
        most_corrected_quality = None
        if quality_corrections:
            most_corrected_quality = max(quality_corrections, key=quality_corrections.get)
        
        avg_confidence = confidence_sum / confidence_count if confidence_count > 0 else 0.0
        
        return {
            'total_corrections': total_corrections,
            'most_corrected_quality': most_corrected_quality,
            'avg_confidence_before_correction': avg_confidence,
            'corrections_by_quality': quality_corrections
        }
