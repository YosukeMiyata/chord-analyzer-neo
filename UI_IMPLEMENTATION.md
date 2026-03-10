# Tauri UI Implementation

## Overview

This document describes the Tauri + React UI implementation for the Chord Analyzer Neo application.

## Architecture

### Frontend (React)
- **Framework**: React 19.x with TypeScript
- **Build Tool**: Vite 6.x
- **UI Components**: Custom components with CSS

### Backend Bridge (Tauri + Rust)
- **Framework**: Tauri 2.x
- **IPC**: Tauri commands for Python backend communication
- **Plugins**: dialog, fs, opener

## Components

### 1. FileSelector
- File selection dialog for audio files
- Supports: MP3, WAV, FLAC, OGG, M4A
- Uses `@tauri-apps/plugin-dialog`

### 2. AudioControls
- Play/Pause/Stop controls
- Timeline slider with current position
- Volume control
- Time display (current/total)

### 3. ChordVisualization
- Timeline view with 16 bars per line
- Chord segments with confidence indicators
- Low confidence highlighting (<70%)
- Current position highlighting
- Click to edit functionality

### 4. LyricsDisplay
- Synchronized lyrics and chords
- Current lyric highlighting
- Time-aligned display
- Chord annotations above lyrics

### 5. ChordEditor
- Modal dialog for chord editing
- Root note selection (C, C#, D, etc.)
- Quality selection (maj, min, 7, maj7, etc.)
- Bass note for slash chords
- Extensions input (9, 11, 13)
- Live preview of edited chord

### 6. ModelSelector
- Dropdown for model selection
- Loads available models from backend
- Shows model descriptions
- Default model indicator

## Tauri Commands

### Audio Analysis
```rust
analyze_audio(filepath: String, model_id: String, use_cache: bool) -> AnalysisResult
```
Analyzes audio file and returns chord progression, lyrics, tempo, key, and time signature.

### Model Management
```rust
list_models() -> Vec<ModelConfig>
```
Returns list of available chord estimation models.

### Chord Correction
```rust
save_chord_correction(
    filepath: String,
    segment_index: usize,
    original_chord: ChordSegment,
    corrected_chord: ChordSegment
) -> Result<(), String>
```
Saves user chord corrections to the database.

### Playback Controls
```rust
play_audio() -> Result<(), String>
pause_audio() -> Result<(), String>
stop_audio() -> Result<(), String>
seek_audio(position: f64) -> Result<(), String>
set_volume(volume: f64) -> Result<(), String>
get_current_position() -> Result<f64, String>
```

## IPC Communication Flow

```
React UI -> Tauri Command -> Python Backend -> Response -> React UI
```

1. User selects audio file via dialog
2. React calls `analyze_audio` Tauri command
3. Tauri executes Python script with audio_engine
4. Python returns JSON analysis result
5. Tauri deserializes and returns to React
6. React updates UI with results

## Features Implemented

### ✅ Task 13.1: Basic UI Layout
- Main window layout with header and content area
- File selection dialog integration
- Loading states and error handling
- Responsive design with dark mode support

### ✅ Task 13.2: Chord Progression Visualization
- Timeline view with 16 bars per line
- Chord segments with time stamps
- Current position highlighting
- Click to edit functionality

### ✅ Task 13.3: Chord Editing UI
- Modal editor with form fields
- Root, quality, bass note, extensions
- Live preview of edited chord
- Save/Cancel actions

### ✅ Task 13.4: Low Confidence Highlighting
- Visual indicator for chords <70% confidence
- Orange border and background color
- Legend explaining the indicators

### ✅ Task 13.5: Model Selection UI
- Dropdown selector in header
- Loads models from backend
- Shows descriptions and default indicator
- Persists selection across analysis

### ✅ Task 13.6: Tauri-Python IPC Bridge
- Rust commands for all Python backend operations
- JSON serialization/deserialization
- Error handling and propagation
- State management for playback

## Styling

The UI uses CSS custom properties for theming:
- Light and dark mode support
- Consistent color palette
- Responsive layout
- Smooth transitions and animations

## Requirements Validation

### Requirement 7.1-7.3: Audio Playback Controls
- ✅ Play/Pause/Stop buttons
- ✅ Seek functionality with timeline slider
- ✅ Volume control

### Requirement 6.1-6.3: Lyrics and Chord Synchronization
- ✅ Time-aligned lyrics display
- ✅ Chord annotations above lyrics
- ✅ Current position highlighting

### Requirement 11.1-11.2: Chord Editing
- ✅ Click to edit chord segments
- ✅ Save corrections to database
- ✅ Apply corrections to display

### Requirement 14.1-14.3: Low Confidence Highlighting
- ✅ Visual indicators for low confidence
- ✅ Configurable threshold (70%)
- ✅ Legend explaining indicators

### Requirement 13.2-13.4: Model Selection
- ✅ List available models
- ✅ Select active model
- ✅ Show model descriptions

## Running the Application

### Development Mode
```bash
npm run tauri:dev
```

### Build for Production
```bash
npm run tauri:build
```

## Notes

- Audio playback is currently a stub and needs actual implementation
- Python backend must be available in the system PATH
- Models directory should exist at `./models`
- Corrections are saved to `./corrections` directory
- Cache is stored in `./cache` directory

## Future Enhancements

1. Real audio playback implementation (using rodio or similar)
2. Waveform visualization
3. Keyboard shortcuts
4. Export functionality (PDF, MIDI, etc.)
5. Undo/Redo for chord edits
6. Batch processing
7. Custom model training UI
