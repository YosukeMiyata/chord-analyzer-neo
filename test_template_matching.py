#!/usr/bin/env python3
"""Test template matching chord recognition on real audio"""

import sys
from pathlib import Path
import numpy as np
import librosa
from src.chord_estimation import ChordEstimationModule

audio_path = "/Users/yousuke/Desktop/真夏の果実.mp3"

if not Path(audio_path).exists():
    print(f"Error: Audio file not found: {audio_path}")
    sys.exit(1)

print(f"Testing template matching chord recognition on: {audio_path}")
print("=" * 80)

# Load audio
print("\nLoading audio...")
audio, sr = librosa.load(audio_path, sr=22050, mono=True, duration=30)  # First 30 seconds
duration = len(audio) / sr
print(f"Audio loaded: {duration:.2f} seconds, {sr} Hz")

# Create chord estimator with template matching (default)
print("\nInitializing ChordEstimationModule with template matching...")
estimator = ChordEstimationModule(use_chordai=False)
print(f"Mode: {'ChordAI' if estimator.use_chordai else 'Template Matching'}")

# Estimate chords
print("\nEstimating chords...")
chords = estimator.estimate_chords(audio, sr, use_vocal_separation=False)

print(f"\nDetected {len(chords)} chord segments")
print("\nFirst 20 chord segments:")
print(f"{'Start':>8s} {'End':>8s} {'Duration':>8s} {'Chord':>10s} {'Confidence':>10s}")
print("-" * 60)

for i, chord in enumerate(chords[:20]):
    duration = chord.end_time - chord.start_time
    chord_name = f"{chord.root}{chord.quality.value}"
    if chord.bass_note:
        chord_name += f"/{chord.bass_note}"
    print(f"{chord.start_time:8.2f} {chord.end_time:8.2f} {duration:8.2f} {chord_name:>10s} {chord.confidence:10.2%}")

if len(chords) > 20:
    print(f"\n... and {len(chords) - 20} more segments")

# Statistics
print(f"\n{'='*80}")
print("Statistics:")
print(f"{'='*80}")

unique_chords = {}
for chord in chords:
    duration = chord.end_time - chord.start_time
    chord_name = f"{chord.root}{chord.quality.value}"
    if chord.bass_note:
        chord_name += f"/{chord.bass_note}"
    unique_chords[chord_name] = unique_chords.get(chord_name, 0) + duration

print(f"\nUnique chords detected: {len(unique_chords)}")
print("\nChord distribution (by duration):")
total_duration = sum(unique_chords.values())
for chord_name, dur in sorted(unique_chords.items(), key=lambda x: -x[1])[:10]:
    pct = dur / total_duration * 100
    print(f"  {chord_name:10s}: {dur:6.2f}s ({pct:5.1f}%)")

# Average confidence
avg_confidence = np.mean([chord.confidence for chord in chords])
print(f"\nAverage confidence: {avg_confidence:.2%}")

print(f"\n{'='*80}\n")
