#!/usr/bin/env python3
"""Inspect ChordAI model input/output specifications"""

import tensorflow as tf
from pathlib import Path

model_path = Path("models/chordai")

print("Loading ChordAI model...")
model = tf.saved_model.load(str(model_path))

print("\n" + "="*60)
print("Model Signatures:")
print("="*60)
for sig_name in model.signatures.keys():
    print(f"\n{sig_name}:")
    sig = model.signatures[sig_name]
    
    print("\n  Inputs:")
    for input_name, input_spec in sig.structured_input_signature[1].items():
        print(f"    {input_name}:")
        print(f"      dtype: {input_spec.dtype}")
        print(f"      shape: {input_spec.shape}")
    
    print("\n  Outputs:")
    for output_name, output_spec in sig.structured_outputs.items():
        print(f"    {output_name}:")
        print(f"      dtype: {output_spec.dtype}")
        print(f"      shape: {output_spec.shape}")

print("\n" + "="*60)
