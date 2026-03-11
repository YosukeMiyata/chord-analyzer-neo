#!/usr/bin/env python3
"""Test with NNLS Chroma features instead of CQT"""

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

# Load audio
audio_path = "/Users/yousuke/Desktop/真夏の果実.mp3"
audio, sr = librosa.load(audio_path, sr=22050, mono=True, duration=10)

print(f"Audio: {len(audio)} samples, {sr} Hz")

# Try using chroma_cqt (which is closer to NNLS-Chroma)
chroma = librosa.feature.chroma_cqt(
    y=audio,
    sr=sr,
    hop_length=512,
    n_chroma=12,
    n_octaves=7,
    bins_per_octave=36
)

print(f"Chroma shape: {chroma.shape}")  # Should be (12, n_frames)

# The model expects (n_frames, 252, 2)
# 252 = 12 chroma * 21 = ???
# OR 252 = 36 bins/octave * 7 octaves

# Let's try expanding chroma to 252 bins by repeating
chroma_expanded = np.repeat(chroma.T, 21, axis=1)  # (n_frames, 252)
print(f"Chroma expanded shape: {chroma_expanded.shape}")

# Create a dummy phase channel (all zeros)
phase_channel = np.zeros_like(chroma_expanded)

# Stack
features = np.stack([chroma_expanded, phase_channel], axis=-1)
print(f"Features shape: {features.shape}")

# Pad to 256
n_frames = features.shape[0]
chunk_size = 256
if n_frames % chunk_size != 0:
    pad_frames = chunk_size - (n_frames % chunk_size)
    features = np.pad(features, ((0, pad_frames), (0, 0), (0, 0)), mode='edge')

input_tensor = tf.constant(features[np.newaxis, :, :, :], dtype=tf.float32)
output = infer_fn(input_1=input_tensor)

chord_logits = output['ccf_1'].numpy()[0, :n_frames, :]

print(f"\nChord logits:")
print(f"  Range: [{chord_logits.min():.4f}, {chord_logits.max():.4f}]")

# Check variation
frame_diffs = []
for i in range(1, min(10, n_frames)):
    diff = np.abs(chord_logits[i] - chord_logits[0]).sum()
    frame_diffs.append(diff)

print(f"  Frame variation: max diff = {max(frame_diffs):.6f}")

# Apply softmax
from scipy.special import softmax
chord_probs = softmax(chord_logits, axis=1)

print(f"\nTop 5 predictions for frame 0:")
top_indices = np.argsort(chord_probs[0])[::-1][:5]
for idx in top_indices:
    chord_label = chord_index[str(idx)]
    prob = chord_probs[0, idx]
    print(f"  {chord_label:15s}: {prob:.4%}")

# Check unique chords
unique_chords = set()
for i in range(n_frames):
    chord_idx = np.argmax(chord_probs[i])
    chord_label = chord_index[str(chord_idx)]
    unique_chords.add(chord_label)

print(f"\nUnique chords detected: {len(unique_chords)}")
if len(unique_chords) <= 20:
    print(f"Chords: {sorted(unique_chords)}")
