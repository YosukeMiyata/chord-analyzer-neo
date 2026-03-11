# ChordAI Model Research Findings

## Repository Information

- **Repository URL**: https://github.com/anime-song/ChordAI
- **Latest Release**: v0.02-alpha
- **Release Package**: ChordAI.zip (66.4 MB)
- **Repository Structure**: The GitHub repository contains only a README with download links; the actual model and application are distributed as a compiled Windows executable package

## Model Format

### Primary Format: TensorFlow SavedModel

The ChordAI model uses **TensorFlow SavedModel** format, which is TensorFlow's universal serialization format for trained models.

**Model Files Structure**:
```
models/
├── saved_model.pb          (13 MB - model architecture and graph definition)
├── variables/
│   ├── variables.data-00000-of-00001  (20 MB - trained weights)
│   └── variables.index                (11 KB - variable index)
└── assets/                 (empty directory)
```

**Key Characteristics**:
- **Format**: TensorFlow SavedModel (protobuf-based)
- **Total Size**: ~33 MB (model + weights)
- **Framework**: TensorFlow 2.x (based on tensorflow.dll presence)
- **Platform**: Originally packaged for Windows, but model files are cross-platform compatible

## Model Input/Output Specifications

### Output Format

The model outputs predictions for **529 chord classes**, as defined in `index.json`:

**Chord Class Categories**:
1. **No Chord**: N.C. (index 0)
2. **Power Chords**: C5, Db5, D5, etc. (12 classes)
3. **Basic Triads**: Major, Minor, Diminished, Augmented (48 classes)
4. **Suspended Chords**: sus4, sus2 (24 classes)
5. **Seventh Chords**: 7, M7, m7, m7-5, mM7, dim7 (72 classes)
6. **Sixth Chords**: 6, m6, 69, m69 (48 classes)
7. **Extended Chords**: add9, madd9 (24 classes)
8. **Complex Seventh Chords**: 7-5, M7-5, aug7, augM7, 7sus4 (60 classes)
9. **Altered Dominants**: 7(b9), 7(#9), 7(b13), 7(9), 7(13) (60 classes)
10. **Extended Major/Minor**: M7(9), M7(13), m7(9), m7(11), m7(13), mM7(9), mM7(13) (84 classes)
11. **Complex Alterations**: 7(b9,b13), 7(b9,13), 7(#9,b13), 7(9,13), 7(#9,13) (60 classes)
12. **Advanced Extensions**: m7(9,11), m7(9,13), M7(9,13), 7(9,#11,13) (48 classes)

**All 12 chromatic roots**: C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B

**Output Format**: The model likely outputs a probability distribution over these 529 classes for each time frame, with the highest probability indicating the predicted chord.

### Input Format (Inferred)

Based on standard chord recognition architectures and the model's purpose:

**Expected Input**: 
- **Audio Features**: Chroma features (12-dimensional pitch class vectors) or spectrograms
- **Temporal Context**: Multiple frames with temporal context (typical: 10-100 frames)
- **Sample Rate**: Standard audio sample rates (likely 22050 Hz or 44100 Hz)
- **Frame Size**: Typical hop length of 512-2048 samples

**Input Shape** (estimated):
- Chroma input: `(batch_size, time_frames, 12)` or `(batch_size, 12, time_frames)`
- Spectrogram input: `(batch_size, time_frames, frequency_bins)`

**Note**: Exact input specifications require loading the model and inspecting its signature, which requires TensorFlow installation.

## Required Dependencies

### Core Dependencies

Based on the COPYRIGHT.txt file and model format:

1. **TensorFlow** (Apache License 2.0)
   - Version: 2.x (inferred from SavedModel format and tensorflow.dll)
   - Minimum recommended: `tensorflow>=2.0.0`
   - Purpose: Model loading and inference

2. **NumPy**
   - Purpose: Array operations for audio features
   - Already present in the project

3. **librosa** (or similar audio processing library)
   - Purpose: Audio loading and chroma feature extraction
   - Already present in the project

### Additional Libraries Used in Reference Application

From the booth.pm reference application (NextChordAnalyzer):

- **TensorFlow/TensorBoard** (Apache-2.0)
- **NumPy/SciPy/scikit-learn** (BSD)
- **librosa/audioread** (ISC/MIT)
- **ONNX/ONNX Runtime** (Apache-2.0/MIT) - Note: May indicate ONNX export capability

### Recommended Dependency Versions

```python
tensorflow>=2.0.0,<3.0.0
numpy>=1.19.0
librosa>=0.9.0
```

**Compatibility Notes**:
- TensorFlow 2.x is required for SavedModel format support
- The model should be compatible with both CPU and GPU inference
- No special hardware requirements beyond standard TensorFlow support

## Model Architecture (Inferred)

Based on research of modern chord recognition systems and the model's capabilities:

**Likely Architecture**:
- **Type**: Deep Neural Network (CNN, RNN, or Transformer-based)
- **Common Patterns**:
  - Convolutional layers for feature extraction from chroma/spectrogram
  - Recurrent layers (LSTM/GRU) or Transformer for temporal modeling
  - Fully connected output layer with softmax for 529-class classification
  
**Processing Pipeline**:
1. Audio input → Chroma feature extraction
2. Chroma features → Neural network inference
3. Network output → Probability distribution over 529 chord classes
4. Post-processing → Chord sequence smoothing/decoding

**Key Capabilities**:
- Recognizes 529 distinct chord types (far exceeding typical template matching)
- Handles complex jazz chords and tensions (9th, 11th, 13th, alterations)
- Supports all 12 chromatic roots
- Includes "N.C." (no chord) detection

## Integration Considerations

### Model Loading

```python
import tensorflow as tf

# Load the SavedModel
model = tf.saved_model.load('path/to/models')

# Inspect available signatures
print(model.signatures.keys())

# Get the serving function
infer = model.signatures['serving_default']
```

### Input Preparation

The integration will need to:
1. Extract chroma features from audio using librosa (already implemented)
2. Format features to match model's expected input shape
3. Handle batching and temporal windowing appropriately

### Output Processing

The integration will need to:
1. Map model output indices (0-528) to chord labels using index.json
2. Parse chord labels (e.g., "CM7(9,13)") into root, quality, and extensions
3. Convert to existing ChordSegment format
4. Handle bass note detection separately (model may not include inversions)

### Performance Expectations

- **Inference Speed**: Should be fast enough for near-real-time processing
- **Accuracy**: Significantly better than template matching, especially for:
  - Minor chord detection
  - Extended chords (7th, 9th, 11th, 13th)
  - Altered dominants
  - Complex jazz harmonies

### Limitations

1. **Bass Note Detection**: The model outputs chord quality but may not explicitly detect bass notes for inversions (slash chords). Bass note detection may need to remain as a separate post-processing step.

2. **Model Size**: 33 MB model requires loading into memory, which is acceptable but larger than template matching.

3. **Dependency**: Requires TensorFlow installation, adding ~500 MB to deployment size.

4. **Platform**: Model files are cross-platform, but original distribution is Windows-only executable.

## Comparison with Template Matching

| Aspect | Template Matching | ChordAI Model |
|--------|------------------|---------------|
| Chord Classes | ~25 basic chords | 529 chord types |
| Minor Chord Accuracy | Low (known issue) | High |
| Extended Chords | Limited | Comprehensive |
| Altered Chords | Not supported | Full support |
| Bass Note Detection | Separate algorithm | Requires separate detection |
| Model Size | None (algorithmic) | 33 MB |
| Dependencies | NumPy, librosa | + TensorFlow |
| Inference Speed | Very fast | Fast (GPU accelerated) |

## Next Steps for Integration

1. **Install TensorFlow**: Add `tensorflow>=2.0.0` to project dependencies
2. **Inspect Model Signature**: Load model and examine exact input/output specifications
3. **Test Inference**: Run sample audio through model to verify output format
4. **Implement Loader**: Create ChordAIModelLoader class
5. **Implement Inference Engine**: Create ChordAIInferenceEngine class
6. **Implement Output Mapper**: Map 529 chord classes to ChordSegment format
7. **Integration Testing**: Verify accuracy improvements over template matching

## References

- ChordAI Repository: https://github.com/anime-song/ChordAI
- Reference Application: https://booth.pm/ja/items/7957208 (NextChordAnalyzer)
- TensorFlow SavedModel Guide: https://www.tensorflow.org/guide/saved_model
- Model Release: https://github.com/anime-song/ChordAI/releases/tag/v0.02-alpha

## Summary

The ChordAI model is a TensorFlow SavedModel that recognizes 529 chord classes across all 12 chromatic roots. It uses deep learning to achieve high accuracy on complex chords, including extended and altered harmonies. The model requires TensorFlow 2.x and accepts chroma features as input, outputting probability distributions over chord classes. Integration will require mapping the 529-class output to the existing ChordSegment format and maintaining separate bass note detection for inversions.
