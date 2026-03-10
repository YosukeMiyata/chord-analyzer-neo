"""Tests for chord correction module"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from src.chord_correction import ChordCorrectionModule
from src.models import ChordSegment, ChordQuality


@pytest.fixture
def temp_corrections_db():
    """Create a temporary corrections database file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'corrections.json'
        yield db_path
        # Cleanup happens automatically with TemporaryDirectory


@pytest.fixture
def temp_audio_file():
    """Create a temporary audio file for testing"""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.wav', delete=False) as f:
        # Write some dummy data
        f.write(b'RIFF' + b'\x00' * 100)
        audio_path = Path(f.name)
    yield audio_path
    # Cleanup
    if audio_path.exists():
        audio_path.unlink()


@pytest.fixture
def correction_module(temp_corrections_db):
    """Create a ChordCorrectionModule instance"""
    return ChordCorrectionModule(temp_corrections_db)


def test_init_creates_db_file(temp_corrections_db):
    """Test that initialization creates the database file"""
    # Remove the file if it exists
    if temp_corrections_db.exists():
        temp_corrections_db.unlink()
    
    module = ChordCorrectionModule(temp_corrections_db)
    
    assert temp_corrections_db.exists()
    with open(temp_corrections_db, 'r') as f:
        data = json.load(f)
        assert data == {}


def test_generate_audio_file_hash(correction_module, temp_audio_file):
    """Test audio file hash generation"""
    hash1 = correction_module._generate_audio_file_hash(temp_audio_file)
    hash2 = correction_module._generate_audio_file_hash(temp_audio_file)
    
    # Same file should produce same hash
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 produces 64 hex characters


def test_save_correction(correction_module, temp_audio_file):
    """Test saving a chord correction"""
    original = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="C",
        quality=ChordQuality.MAJOR,
        confidence=0.6
    )
    
    corrected = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="Dm",
        quality=ChordQuality.MINOR,
        confidence=1.0
    )
    
    correction_module.save_correction(
        audio_file=temp_audio_file,
        segment_index=5,
        original=original,
        corrected=corrected,
        user_id="test_user"
    )
    
    # Verify the correction was saved
    db = correction_module._load_db()
    audio_hash = correction_module._generate_audio_file_hash(temp_audio_file)
    
    assert audio_hash in db
    assert len(db[audio_hash]) == 1
    
    correction = db[audio_hash][0]
    assert correction['segment_index'] == 5
    assert correction['original_chord']['root'] == "C"
    assert correction['original_chord']['quality'] == "maj"
    assert correction['corrected_chord']['root'] == "Dm"
    assert correction['corrected_chord']['quality'] == "min"
    assert correction['user_id'] == "test_user"
    assert 'timestamp' in correction


def test_save_correction_updates_existing(correction_module, temp_audio_file):
    """Test that saving a correction for the same segment updates the existing one"""
    original = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="C",
        quality=ChordQuality.MAJOR,
        confidence=0.6
    )
    
    corrected1 = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="Dm",
        quality=ChordQuality.MINOR,
        confidence=1.0
    )
    
    corrected2 = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="Em",
        quality=ChordQuality.MINOR,
        confidence=1.0
    )
    
    # Save first correction
    correction_module.save_correction(
        audio_file=temp_audio_file,
        segment_index=5,
        original=original,
        corrected=corrected1
    )
    
    # Save second correction for the same segment
    correction_module.save_correction(
        audio_file=temp_audio_file,
        segment_index=5,
        original=original,
        corrected=corrected2
    )
    
    # Verify only one correction exists and it's the latest
    db = correction_module._load_db()
    audio_hash = correction_module._generate_audio_file_hash(temp_audio_file)
    
    assert len(db[audio_hash]) == 1
    assert db[audio_hash][0]['corrected_chord']['root'] == "Em"


def test_save_multiple_corrections(correction_module, temp_audio_file):
    """Test saving multiple corrections for different segments"""
    for i in range(3):
        original = ChordSegment(
            start_time=float(i * 2),
            end_time=float(i * 2 + 2),
            root="C",
            quality=ChordQuality.MAJOR,
            confidence=0.6
        )
        
        corrected = ChordSegment(
            start_time=float(i * 2),
            end_time=float(i * 2 + 2),
            root="Dm",
            quality=ChordQuality.MINOR,
            confidence=1.0
        )
        
        correction_module.save_correction(
            audio_file=temp_audio_file,
            segment_index=i,
            original=original,
            corrected=corrected
        )
    
    # Verify all corrections were saved
    db = correction_module._load_db()
    audio_hash = correction_module._generate_audio_file_hash(temp_audio_file)
    
    assert len(db[audio_hash]) == 3


def test_chord_segment_to_dict(correction_module):
    """Test conversion of ChordSegment to dictionary"""
    chord = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="C",
        quality=ChordQuality.MAJOR7,
        bass_note="E",
        extensions=["9th", "11th"],
        confidence=0.85
    )
    
    chord_dict = correction_module._chord_segment_to_dict(chord)
    
    assert chord_dict['start_time'] == 10.0
    assert chord_dict['end_time'] == 12.0
    assert chord_dict['root'] == "C"
    assert chord_dict['quality'] == "maj7"
    assert chord_dict['bass_note'] == "E"
    assert chord_dict['extensions'] == ["9th", "11th"]
    assert chord_dict['confidence'] == 0.85


def test_get_correction_statistics_empty(correction_module):
    """Test statistics with no corrections"""
    stats = correction_module.get_correction_statistics()
    
    assert stats['total_corrections'] == 0
    assert stats['most_corrected_quality'] is None
    assert stats['avg_confidence_before_correction'] == 0.0
    assert stats['corrections_by_quality'] == {}


def test_get_correction_statistics(correction_module, temp_audio_file):
    """Test correction statistics calculation"""
    # Save multiple corrections
    for i in range(3):
        original = ChordSegment(
            start_time=float(i * 2),
            end_time=float(i * 2 + 2),
            root="C",
            quality=ChordQuality.MAJOR if i < 2 else ChordQuality.MINOR,
            confidence=0.6 + i * 0.1
        )
        
        corrected = ChordSegment(
            start_time=float(i * 2),
            end_time=float(i * 2 + 2),
            root="Dm",
            quality=ChordQuality.MINOR,
            confidence=1.0
        )
        
        correction_module.save_correction(
            audio_file=temp_audio_file,
            segment_index=i,
            original=original,
            corrected=corrected
        )
    
    stats = correction_module.get_correction_statistics()
    
    assert stats['total_corrections'] == 3
    assert stats['most_corrected_quality'] == "maj"  # 2 major corrections vs 1 minor
    assert stats['avg_confidence_before_correction'] == pytest.approx(0.7, rel=0.01)
    assert stats['corrections_by_quality']['maj'] == 2
    assert stats['corrections_by_quality']['min'] == 1


def test_export_corrections_dataset(correction_module, temp_audio_file):
    """Test exporting corrections dataset"""
    # Save a correction
    original = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="C",
        quality=ChordQuality.MAJOR,
        confidence=0.6
    )
    
    corrected = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="Dm",
        quality=ChordQuality.MINOR,
        confidence=1.0
    )
    
    correction_module.save_correction(
        audio_file=temp_audio_file,
        segment_index=5,
        original=original,
        corrected=corrected
    )
    
    # Export dataset
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        export_path = Path(f.name)
    
    try:
        correction_module.export_corrections_dataset(export_path)
        
        # Verify export
        assert export_path.exists()
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        audio_hash = correction_module._generate_audio_file_hash(temp_audio_file)
        assert audio_hash in exported_data
        assert len(exported_data[audio_hash]) == 1
    finally:
        if export_path.exists():
            export_path.unlink()


def test_save_correction_with_extensions(correction_module, temp_audio_file):
    """Test saving corrections with chord extensions"""
    original = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="C",
        quality=ChordQuality.MAJOR7,
        extensions=["9th"],
        confidence=0.7
    )
    
    corrected = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="C",
        quality=ChordQuality.MAJOR7,
        extensions=["9th", "13th"],
        confidence=1.0
    )
    
    correction_module.save_correction(
        audio_file=temp_audio_file,
        segment_index=0,
        original=original,
        corrected=corrected
    )
    
    # Verify extensions were saved
    db = correction_module._load_db()
    audio_hash = correction_module._generate_audio_file_hash(temp_audio_file)
    
    correction = db[audio_hash][0]
    assert correction['original_chord']['extensions'] == ["9th"]
    assert correction['corrected_chord']['extensions'] == ["9th", "13th"]


def test_save_correction_with_bass_note(correction_module, temp_audio_file):
    """Test saving corrections with bass notes (slash chords)"""
    original = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="C",
        quality=ChordQuality.MAJOR,
        confidence=0.7
    )
    
    corrected = ChordSegment(
        start_time=10.0,
        end_time=12.0,
        root="C",
        quality=ChordQuality.MAJOR,
        bass_note="E",
        confidence=1.0
    )
    
    correction_module.save_correction(
        audio_file=temp_audio_file,
        segment_index=0,
        original=original,
        corrected=corrected
    )
    
    # Verify bass note was saved
    db = correction_module._load_db()
    audio_hash = correction_module._generate_audio_file_hash(temp_audio_file)
    
    correction = db[audio_hash][0]
    assert correction['original_chord']['bass_note'] is None
    assert correction['corrected_chord']['bass_note'] == "E"
