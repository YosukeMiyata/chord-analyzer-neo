#!/usr/bin/env python3
"""Test madmom chord recognition"""

import sys
from pathlib import Path
import numpy as np

# Test if madmom is installed and working
try:
    import madmom
    print(f"madmom version: {madmom.__version__}")
    print(f"madmom location: {madmom.__file__}")
except ImportError as e:
    print(f"Error importing madmom: {e}")
    sys.exit(1)

# Check available chord recognition features
print("\nAvailable madmom features:")
print(f"  - madmom.features: {hasattr(madmom, 'features')}")
if hasattr(madmom, 'features'):
    print(f"  - madmom.features.chords: {hasattr(madmom.features, 'chords')}")

# Test chord recognition on audio file
audio_path = "/Users/yousuke/Desktop/真夏の果実.mp3"

if not Path(audio_path).exists():
    print(f"\nError: Audio file not found: {audio_path}")
    sys.exit(1)

print(f"\nTesting chord recognition on: {audio_path}")

try:
    from madmom.features.chords import DeepChromaChordRecognitionProcessor
    from madmom.audio.signal import SignalProcessor, FramedSignalProcessor
    from madmom.audio.spectrogram import LogarithmicFilteredSpectrogramProcessor, SpectrogramDifferenceProcessor
    from madmom.audio.chroma import DeepChromaProcessor
    
    print("\nInitializing chord recognition processor...")
    
    # Create the chord recognition processor
    # This uses a deep learning model for chord recognition
    dcp = DeepChromaProcessor()
    decode = DeepChromaChordRecognitionProcessor()
    
    print("Processing audio file...")
    
    # Process the audio file
    chroma = dcp(audio_path)
    chords = decode(chroma)
    
    print(f"\nDetected {len(chords)} chord segments")
    print("\nFirst 20 chord segments:")
    print(f"{'Time':>10s} {'Chord':>10s}")
    print("-" * 25)
    
    for i, (time, chord) in enumerate(chords[:20]):
        print(f"{time:10.2f} {chord:>10s}")
    
    if len(chords) > 20:
        print(f"\n... and {len(chords) - 20} more segments")
    
    # Statistics
    print(f"\n{'='*60}")
    print("Statistics:")
    print(f"{'='*60}")
    
    unique_chords = {}
    for time, chord in chords:
        unique_chords[chord] = unique_chords.get(chord, 0) + 1
    
    print(f"\nUnique chords detected: {len(unique_chords)}")
    print("\nChord distribution:")
    for chord, count in sorted(unique_chords.items(), key=lambda x: -x[1])[:10]:
        pct = count / len(chords) * 100
        print(f"  {chord:10s}: {count:4d} ({pct:5.1f}%)")
    
    print(f"\n{'='*60}\n")
    
except Exception as e:
    print(f"\nError during chord recognition: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Test completed successfully!")
