#!/usr/bin/env python3
"""Detailed model output inspection"""

import numpy as np
import librosa
from pathlib import Path
import tensorflow as tf
import json

# Load model
model_path = Path("models/chordai")
model = tf.saved_model.load(str(model_path))
infer_fn = model.signatures['serving_default']

# Load chord index
with open(model_path / "index.json", 'r') as f:
    chord_index = json.load(f)

# Load a short audio sample
audio_path = "/Users/yousuke/Desktop/真夏の果実.mp3"
audio, sr = librosa.load(audio_path, sr=22050, mono=True, duration=5)  # First 5 seconds

print(f"Audio: {len(audio)} samples, {sr} Hz")

# Extract CQT
cqt = librosa.cqt(
    y=audio,
    sr=sr,
    hop_length=512,
    n_bins=252,
    bins_per_octave=36
)

# Convert to magnitude and phase
cqt_mag = np.abs(cqt).T
cqt_phase = np.angle(cqt).T

# Simple normalization
cqt_mag_norm = cqt_mag / (np.max(cqt_mag) + 1e-8)
cqt_phase_norm = cqt_phase / np.pi

# Stack
cqt_features = np.stack([cqt_mag_norm, cqt_phase_norm], axis=-1)
print(f"CQT features shape: {cqt_features.shape}")
print(f"CQT features range: [{cqt_features.min():.4f}, {cqt_features.max():.4f}]")

# Pad to 256
n_frames = cqt_features.shape[0]
chunk_size = 256
if n_frames % chunk_size != 0:
    pad_frames = chunk_size - (n_frames % chunk_size)
    cqt_features = np.pad(cqt_features, ((0, pad_frames), (0, 0), (0, 0)), mode='edge')
    print(f"Padded to: {cqt_features.shape}")

# Add batch dimension
input_tensor = tf.constant(cqt_features[np.newaxis, :, :, :], dtype=tf.float32)
print(f"Input tensor shape: {input_tensor.shape}")

# Run inference
print("\nRunning inference...")
output = infer_fn(input_1=input_tensor)

print("\nAll outputs:")
for key, value in output.items():
    print(f"  {key}: shape={value.shape}, dtype={value.dtype}")
    if len(value.shape) <= 2:
        print(f"    value={value.numpy()}")

# Focus on ccf_1 (chord predictions)
chord_logits = output['ccf_1'].numpy()[0, :n_frames, :]
print(f"\nChord logits (ccf_1):")
print(f"  Shape: {chord_logits.shape}")
print(f"  Range: [{chord_logits.min():.4f}, {chord_logits.max():.4f}]")
print(f"  Mean: {chord_logits.mean():.4f}")
print(f"  Std: {chord_logits.std():.4f}")

# Check if all frames are identical
print(f"\nChecking frame variation:")
frame_diffs = []
for i in range(1, min(10, n_frames)):
    diff = np.abs(chord_logits[i] - chord_logits[0]).sum()
    frame_diffs.append(diff)
    print(f"  Frame {i} vs Frame 0: diff = {diff:.6f}")

if max(frame_diffs) < 1e-6:
    print("\n  WARNING: All frames are identical!")
else:
    print(f"\n  Frames show variation (max diff: {max(frame_diffs):.6f})")

# Apply softmax
from scipy.special import softmax
chord_probs = softmax(chord_logits, axis=1)

print(f"\nChord probabilities:")
print(f"  Shape: {chord_probs.shape}")
print(f"  Sum per frame (should be ~1.0): {chord_probs[0].sum():.6f}")

# Get top 5 predictions for first frame
print(f"\nTop 5 predictions for frame 0:")
top_indices = np.argsort(chord_probs[0])[::-1][:5]
for idx in top_indices:
    chord_label = chord_index[str(idx)]
    prob = chord_probs[0, idx]
    print(f"  {chord_label:15s}: {prob:.4%}")

# Check bass note predictions (bc_1)
bass_logits = output['bc_1'].numpy()[0, :n_frames, :]
print(f"\nBass note logits (bc_1):")
print(f"  Shape: {bass_logits.shape}")
print(f"  Range: [{bass_logits.min():.4f}, {bass_logits.max():.4f}]")

bass_probs = softmax(bass_logits, axis=1)
bass_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'N']
print(f"\nBass note predictions for frame 0:")
top_bass_indices = np.argsort(bass_probs[0])[::-1][:3]
for idx in top_bass_indices:
    note = bass_notes[idx] if idx < len(bass_notes) else f"Unknown({idx})"
    prob = bass_probs[0, idx]
    print(f"  {note:3s}: {prob:.4%}")
