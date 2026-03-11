#!/usr/bin/env python3
"""Debug ChordAI inference to understand output format"""

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
audio, sr = librosa.load(audio_path, sr=22050, mono=True, duration=10)  # First 10 seconds

print(f"Audio: {len(audio)} samples, {sr} Hz")

# Extract CQT
cqt = librosa.cqt(
    y=audio,
    sr=sr,
    hop_length=512,
    n_bins=252,
    bins_per_octave=36
)

print(f"CQT shape: {cqt.shape}")

# Convert to magnitude and phase
cqt_mag = np.abs(cqt).T
cqt_phase = np.angle(cqt).T

print(f"CQT mag shape: {cqt_mag.shape}")
print(f"CQT mag range: [{cqt_mag.min():.4f}, {cqt_mag.max():.4f}]")
print(f"CQT phase range: [{cqt_phase.min():.4f}, {cqt_phase.max():.4f}]")

# Try different normalizations
print("\n" + "="*60)
print("Testing different normalizations:")
print("="*60)

# Method 1: Log scale + global normalization
cqt_mag_v1 = librosa.amplitude_to_db(cqt_mag, ref=np.max)
cqt_mag_v1 = (cqt_mag_v1 - cqt_mag_v1.min()) / (cqt_mag_v1.max() - cqt_mag_v1.min() + 1e-8)
cqt_phase_v1 = cqt_phase / np.pi

print(f"\nMethod 1 (log + global norm):")
print(f"  Mag range: [{cqt_mag_v1.min():.4f}, {cqt_mag_v1.max():.4f}]")
print(f"  Phase range: [{cqt_phase_v1.min():.4f}, {cqt_phase_v1.max():.4f}]")

# Stack and pad
cqt_features_v1 = np.stack([cqt_mag_v1, cqt_phase_v1], axis=-1)
n_frames = cqt_features_v1.shape[0]
chunk_size = 256
if n_frames % chunk_size != 0:
    pad_frames = chunk_size - (n_frames % chunk_size)
    cqt_features_v1 = np.pad(cqt_features_v1, ((0, pad_frames), (0, 0), (0, 0)), mode='edge')

input_tensor_v1 = tf.constant(cqt_features_v1[np.newaxis, :, :, :], dtype=tf.float32)
output_v1 = infer_fn(input_1=input_tensor_v1)
chord_logits_v1 = output_v1['ccf_1'].numpy()[0, :n_frames, :]

print(f"  Output shape: {chord_logits_v1.shape}")
print(f"  Output range: [{chord_logits_v1.min():.4f}, {chord_logits_v1.max():.4f}]")

# Get predictions for first 5 frames
from scipy.special import softmax
chord_probs_v1 = softmax(chord_logits_v1, axis=1)
print(f"\n  First 5 frames:")
for i in range(min(5, n_frames)):
    chord_idx = np.argmax(chord_probs_v1[i])
    confidence = chord_probs_v1[i, chord_idx]
    chord_label = chord_index[str(chord_idx)]
    print(f"    Frame {i}: {chord_label} ({confidence:.2%})")

# Method 2: No log, simple normalization
cqt_mag_v2 = cqt_mag / (np.max(cqt_mag) + 1e-8)
cqt_phase_v2 = cqt_phase / np.pi

print(f"\nMethod 2 (simple norm):")
print(f"  Mag range: [{cqt_mag_v2.min():.4f}, {cqt_mag_v2.max():.4f}]")
print(f"  Phase range: [{cqt_phase_v2.min():.4f}, {cqt_phase_v2.max():.4f}]")

cqt_features_v2 = np.stack([cqt_mag_v2, cqt_phase_v2], axis=-1)
if cqt_features_v2.shape[0] % chunk_size != 0:
    pad_frames = chunk_size - (cqt_features_v2.shape[0] % chunk_size)
    cqt_features_v2 = np.pad(cqt_features_v2, ((0, pad_frames), (0, 0), (0, 0)), mode='edge')

input_tensor_v2 = tf.constant(cqt_features_v2[np.newaxis, :, :, :], dtype=tf.float32)
output_v2 = infer_fn(input_1=input_tensor_v2)
chord_logits_v2 = output_v2['ccf_1'].numpy()[0, :n_frames, :]

print(f"  Output shape: {chord_logits_v2.shape}")
print(f"  Output range: [{chord_logits_v2.min():.4f}, {chord_logits_v2.max():.4f}]")

chord_probs_v2 = softmax(chord_logits_v2, axis=1)
print(f"\n  First 5 frames:")
for i in range(min(5, n_frames)):
    chord_idx = np.argmax(chord_probs_v2[i])
    confidence = chord_probs_v2[i, chord_idx]
    chord_label = chord_index[str(chord_idx)]
    print(f"    Frame {i}: {chord_label} ({confidence:.2%})")

# Method 3: Per-frame normalization
cqt_mag_v3 = cqt_mag.copy()
for i in range(cqt_mag_v3.shape[0]):
    frame_max = cqt_mag_v3[i].max()
    if frame_max > 0:
        cqt_mag_v3[i] = cqt_mag_v3[i] / frame_max
cqt_phase_v3 = cqt_phase / np.pi

print(f"\nMethod 3 (per-frame norm):")
print(f"  Mag range: [{cqt_mag_v3.min():.4f}, {cqt_mag_v3.max():.4f}]")
print(f"  Phase range: [{cqt_phase_v3.min():.4f}, {cqt_phase_v3.max():.4f}]")

cqt_features_v3 = np.stack([cqt_mag_v3, cqt_phase_v3], axis=-1)
if cqt_features_v3.shape[0] % chunk_size != 0:
    pad_frames = chunk_size - (cqt_features_v3.shape[0] % chunk_size)
    cqt_features_v3 = np.pad(cqt_features_v3, ((0, pad_frames), (0, 0), (0, 0)), mode='edge')

input_tensor_v3 = tf.constant(cqt_features_v3[np.newaxis, :, :, :], dtype=tf.float32)
output_v3 = infer_fn(input_1=input_tensor_v3)
chord_logits_v3 = output_v3['ccf_1'].numpy()[0, :n_frames, :]

print(f"  Output shape: {chord_logits_v3.shape}")
print(f"  Output range: [{chord_logits_v3.min():.4f}, {chord_logits_v3.max():.4f}]")

chord_probs_v3 = softmax(chord_logits_v3, axis=1)
print(f"\n  First 5 frames:")
for i in range(min(5, n_frames)):
    chord_idx = np.argmax(chord_probs_v3[i])
    confidence = chord_probs_v3[i, chord_idx]
    chord_label = chord_index[str(chord_idx)]
    print(f"    Frame {i}: {chord_label} ({confidence:.2%})")

print("\n" + "="*60)
print("Checking for variation in predictions:")
print("="*60)

for method_name, probs in [("Method 1", chord_probs_v1), ("Method 2", chord_probs_v2), ("Method 3", chord_probs_v3)]:
    unique_chords = set()
    for i in range(n_frames):
        chord_idx = np.argmax(probs[i])
        chord_label = chord_index[str(chord_idx)]
        unique_chords.add(chord_label)
    print(f"{method_name}: {len(unique_chords)} unique chords detected")
    if len(unique_chords) <= 10:
        print(f"  Chords: {sorted(unique_chords)}")
