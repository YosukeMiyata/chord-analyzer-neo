#!/usr/bin/env python3
"""Test librosa-based chord recognition using template matching"""

import sys
from pathlib import Path
import numpy as np
import librosa

audio_path = "/Users/yousuke/Desktop/真夏の果実.mp3"

if not Path(audio_path).exists():
    print(f"Error: Audio file not found: {audio_path}")
    sys.exit(1)

print(f"Testing chord recognition on: {audio_path}")
print("Loading audio...")

# Load audio
audio, sr = librosa.load(audio_path, sr=22050, mono=True, duration=30)  # First 30 seconds
duration = len(audio) / sr

print(f"Audio loaded: {duration:.2f} seconds, {sr} Hz")

# Extract chroma features
print("Extracting chroma features...")
chroma = librosa.feature.chroma_cqt(y=audio, sr=sr, hop_length=512)

print(f"Chroma shape: {chroma.shape}")

# Define chord templates (24 major and minor chords)
chord_templates = {}

# Major chord template (root, major third, perfect fifth)
major_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])

# Minor chord template (root, minor third, perfect fifth)
minor_template = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])

# Create templates for all 12 roots
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

for i, note in enumerate(note_names):
    # Major chord
    chord_templates[f"{note}"] = np.roll(major_template, i)
    # Minor chord
    chord_templates[f"{note}m"] = np.roll(minor_template, i)

# Normalize templates
for key in chord_templates:
    chord_templates[key] = chord_templates[key] / np.linalg.norm(chord_templates[key])

print(f"Created {len(chord_templates)} chord templates")

# Recognize chords frame by frame
print("Recognizing chords...")

n_frames = chroma.shape[1]
frame_duration = 512 / sr  # hop_length / sr

chords = []
for i in range(n_frames):
    frame_chroma = chroma[:, i]
    
    # Normalize frame chroma
    if np.sum(frame_chroma) > 0:
        frame_chroma = frame_chroma / np.linalg.norm(frame_chroma)
    
    # Find best matching chord
    best_chord = None
    best_score = -1
    
    for chord_name, template in chord_templates.items():
        # Cosine similarity
        score = np.dot(frame_chroma, template)
        if score > best_score:
            best_score = score
            best_chord = chord_name
    
    time = i * frame_duration
    chords.append((time, best_chord, best_score))

# Merge consecutive identical chords
print("Merging consecutive chords...")
merged_chords = []
if chords:
    current_chord = chords[0][1]
    start_time = chords[0][0]
    
    for i in range(1, len(chords)):
        if chords[i][1] != current_chord:
            end_time = chords[i][0]
            merged_chords.append((start_time, end_time, current_chord))
            current_chord = chords[i][1]
            start_time = chords[i][0]
    
    # Add last chord
    merged_chords.append((start_time, chords[-1][0], current_chord))

print(f"\nDetected {len(merged_chords)} chord segments")
print("\nFirst 20 chord segments:")
print(f"{'Start':>8s} {'End':>8s} {'Chord':>10s}")
print("-" * 30)

for i, (start, end, chord) in enumerate(merged_chords[:20]):
    print(f"{start:8.2f} {end:8.2f} {chord:>10s}")

if len(merged_chords) > 20:
    print(f"\n... and {len(merged_chords) - 20} more segments")

# Statistics
print(f"\n{'='*60}")
print("Statistics:")
print(f"{'='*60}")

unique_chords = {}
for start, end, chord in merged_chords:
    duration = end - start
    unique_chords[chord] = unique_chords.get(chord, 0) + duration

print(f"\nUnique chords detected: {len(unique_chords)}")
print("\nChord distribution (by duration):")
total_duration = sum(unique_chords.values())
for chord, dur in sorted(unique_chords.items(), key=lambda x: -x[1])[:10]:
    pct = dur / total_duration * 100
    print(f"  {chord:10s}: {dur:6.2f}s ({pct:5.1f}%)")

print(f"\n{'='*60}\n")
