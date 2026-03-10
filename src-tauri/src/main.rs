// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use std::sync::Mutex;
use tauri::State;

#[derive(Debug, Serialize, Deserialize)]
struct ChordSegment {
    start_time: f64,
    end_time: f64,
    root: String,
    quality: String,
    bass_note: Option<String>,
    extensions: Option<Vec<String>>,
    confidence: f64,
}

#[derive(Debug, Serialize, Deserialize)]
struct LyricSegment {
    start_time: f64,
    end_time: f64,
    text: String,
    confidence: f64,
}

#[derive(Debug, Serialize, Deserialize)]
struct AnalysisResult {
    chord_progression: Vec<ChordSegment>,
    lyrics: Vec<LyricSegment>,
    tempo: f64,
    key: String,
    time_signature: (u32, u32),
}

#[derive(Debug, Serialize, Deserialize)]
struct ModelConfig {
    model_id: String,
    model_name: String,
    model_path: String,
    model_type: String,
    description: String,
    accuracy_metrics: serde_json::Value,
    is_default: bool,
}

struct AudioEngineState {
    is_playing: Mutex<bool>,
    current_position: Mutex<f64>,
    volume: Mutex<f64>,
}

#[tauri::command]
async fn analyze_audio(
    filepath: String,
    _model_id: String,
    use_cache: bool,
) -> Result<AnalysisResult, String> {
    // Call Python backend to analyze audio
    let output = Command::new("python3")
        .arg("-c")
        .arg(format!(
            r#"
import sys
import json
sys.path.insert(0, 'src')
from audio_engine import AudioProcessingEngine
from pathlib import Path

engine = AudioProcessingEngine()
engine.load_audio_file(Path('{}'))
result = engine.analyze_audio(use_cache={})

# Convert result to JSON
output = {{
    'chord_progression': [
        {{
            'start_time': c.start_time,
            'end_time': c.end_time,
            'root': c.root,
            'quality': c.quality.value,
            'bass_note': c.bass_note,
            'extensions': c.extensions,
            'confidence': c.confidence
        }} for c in result.chord_progression
    ],
    'lyrics': [
        {{
            'start_time': l.start_time,
            'end_time': l.end_time,
            'text': l.text,
            'confidence': l.confidence
        }} for l in result.lyrics
    ],
    'tempo': result.tempo,
    'key': result.key,
    'time_signature': result.time_signature
}}
print(json.dumps(output))
"#,
            filepath, use_cache
        ))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .map_err(|e| format!("Failed to execute Python: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python error: {}", stderr));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    serde_json::from_str(&stdout).map_err(|e| format!("Failed to parse result: {}", e))
}

#[tauri::command]
async fn list_models() -> Result<Vec<ModelConfig>, String> {
    let output = Command::new("python3")
        .arg("-c")
        .arg(r#"
import sys
import json
sys.path.insert(0, 'src')
from model_configuration import ModelConfigurationModule
from pathlib import Path

module = ModelConfigurationModule(Path('./models'))
models = module.list_available_models()

output = [
    {
        'model_id': m.model_id,
        'model_name': m.model_name,
        'model_path': str(m.model_path),
        'model_type': m.model_type,
        'description': m.description,
        'accuracy_metrics': m.accuracy_metrics,
        'is_default': m.is_default
    } for m in models
]
print(json.dumps(output))
"#)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .map_err(|e| format!("Failed to execute Python: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python error: {}", stderr));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    serde_json::from_str(&stdout).map_err(|e| format!("Failed to parse models: {}", e))
}

#[tauri::command]
async fn save_chord_correction(
    filepath: String,
    segment_index: usize,
    original_chord: ChordSegment,
    corrected_chord: ChordSegment,
) -> Result<(), String> {
    let original_json = serde_json::to_string(&original_chord)
        .map_err(|e| format!("Failed to serialize original chord: {}", e))?;
    let corrected_json = serde_json::to_string(&corrected_chord)
        .map_err(|e| format!("Failed to serialize corrected chord: {}", e))?;

    let output = Command::new("python3")
        .arg("-c")
        .arg(format!(
            r#"
import sys
import json
sys.path.insert(0, 'src')
from chord_correction import ChordCorrectionModule
from models import ChordSegment, ChordQuality
from pathlib import Path

module = ChordCorrectionModule(Path('./corrections'))

# Parse chords
original_data = json.loads('{}')
corrected_data = json.loads('{}')

# Convert to ChordSegment objects
original = ChordSegment(
    start_time=original_data['start_time'],
    end_time=original_data['end_time'],
    root=original_data['root'],
    quality=ChordQuality(original_data['quality']),
    bass_note=original_data.get('bass_note'),
    extensions=original_data.get('extensions'),
    confidence=original_data['confidence']
)

corrected = ChordSegment(
    start_time=corrected_data['start_time'],
    end_time=corrected_data['end_time'],
    root=corrected_data['root'],
    quality=ChordQuality(corrected_data['quality']),
    bass_note=corrected_data.get('bass_note'),
    extensions=corrected_data.get('extensions'),
    confidence=corrected_data['confidence']
)

module.save_correction(Path('{}'), {}, original, corrected)
print('success')
"#,
            original_json.replace('\'', "\\'"),
            corrected_json.replace('\'', "\\'"),
            filepath,
            segment_index
        ))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .map_err(|e| format!("Failed to execute Python: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python error: {}", stderr));
    }

    Ok(())
}

#[tauri::command]
fn play_audio(state: State<AudioEngineState>) -> Result<(), String> {
    let mut is_playing = state.is_playing.lock().unwrap();
    *is_playing = true;
    // TODO: Implement actual audio playback
    Ok(())
}

#[tauri::command]
fn pause_audio(state: State<AudioEngineState>) -> Result<(), String> {
    let mut is_playing = state.is_playing.lock().unwrap();
    *is_playing = false;
    // TODO: Implement actual audio pause
    Ok(())
}

#[tauri::command]
fn stop_audio(state: State<AudioEngineState>) -> Result<(), String> {
    let mut is_playing = state.is_playing.lock().unwrap();
    let mut position = state.current_position.lock().unwrap();
    *is_playing = false;
    *position = 0.0;
    // TODO: Implement actual audio stop
    Ok(())
}

#[tauri::command]
fn seek_audio(state: State<AudioEngineState>, position: f64) -> Result<(), String> {
    let mut current_position = state.current_position.lock().unwrap();
    *current_position = position;
    // TODO: Implement actual audio seek
    Ok(())
}

#[tauri::command]
fn set_volume(state: State<AudioEngineState>, volume: f64) -> Result<(), String> {
    let mut vol = state.volume.lock().unwrap();
    *vol = volume.clamp(0.0, 1.0);
    // TODO: Implement actual volume control
    Ok(())
}

#[tauri::command]
fn get_current_position(state: State<AudioEngineState>) -> Result<f64, String> {
    let position = state.current_position.lock().unwrap();
    Ok(*position)
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_opener::init())
        .manage(AudioEngineState {
            is_playing: Mutex::new(false),
            current_position: Mutex::new(0.0),
            volume: Mutex::new(0.8),
        })
        .invoke_handler(tauri::generate_handler![
            analyze_audio,
            list_models,
            save_chord_correction,
            play_audio,
            pause_audio,
            stop_audio,
            seek_audio,
            set_volume,
            get_current_position,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
