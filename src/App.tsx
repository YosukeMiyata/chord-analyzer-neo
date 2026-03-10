import { useState } from 'react'
import { open } from '@tauri-apps/plugin-dialog'
import { invoke } from '@tauri-apps/api/core'
import FileSelector from './components/FileSelector'
import AudioControls from './components/AudioControls'
import ChordVisualization from './components/ChordVisualization'
import LyricsDisplay from './components/LyricsDisplay'
import ChordEditor from './components/ChordEditor'
import ModelSelector from './components/ModelSelector'
import './styles.css'

interface ChordSegment {
  start_time: number
  end_time: number
  root: string
  quality: string
  bass_note?: string
  extensions?: string[]
  confidence: number
}

interface LyricSegment {
  start_time: number
  end_time: number
  text: string
  confidence: number
}

interface AnalysisResult {
  chord_progression: ChordSegment[]
  lyrics: LyricSegment[]
  tempo: number
  key: string
  time_signature: [number, number]
}

function App() {
  const [audioFile, setAudioFile] = useState<string | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentPosition, setCurrentPosition] = useState(0)
  const [volume, setVolume] = useState(0.8)
  const [selectedChord, setSelectedChord] = useState<ChordSegment | null>(null)
  const [selectedModel, setSelectedModel] = useState<string>('default')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = async () => {
    const selected = await open({
      multiple: false,
      filters: [{
        name: 'Audio',
        extensions: ['mp3', 'wav', 'flac', 'ogg', 'm4a']
      }]
    })

    if (selected && typeof selected === 'string') {
      setAudioFile(selected)
      setError(null)
      await analyzeAudio(selected)
    }
  }

  const analyzeAudio = async (filepath: string) => {
    setIsAnalyzing(true)
    setError(null)
    try {
      const result = await invoke<AnalysisResult>('analyze_audio', {
        filepath,
        modelId: selectedModel,
        useCache: true
      })
      setAnalysisResult(result)
    } catch (err) {
      console.error('Analysis failed:', err)
      setError(err as string)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handlePlayPause = async () => {
    try {
      if (isPlaying) {
        await invoke('pause_audio')
      } else {
        await invoke('play_audio')
      }
      setIsPlaying(!isPlaying)
    } catch (err) {
      console.error('Playback error:', err)
    }
  }

  const handleStop = async () => {
    try {
      await invoke('stop_audio')
      setIsPlaying(false)
      setCurrentPosition(0)
    } catch (err) {
      console.error('Stop error:', err)
    }
  }

  const handleSeek = async (position: number) => {
    try {
      await invoke('seek_audio', { position })
      setCurrentPosition(position)
    } catch (err) {
      console.error('Seek error:', err)
    }
  }

  const handleVolumeChange = async (newVolume: number) => {
    try {
      await invoke('set_volume', { volume: newVolume })
      setVolume(newVolume)
    } catch (err) {
      console.error('Volume error:', err)
    }
  }

  const handleChordEdit = async (chord: ChordSegment, newChord: ChordSegment) => {
    if (!audioFile || !analysisResult) return

    try {
      const segmentIndex = analysisResult.chord_progression.indexOf(chord)
      await invoke('save_chord_correction', {
        filepath: audioFile,
        segmentIndex,
        originalChord: chord,
        correctedChord: newChord
      })

      const updatedChords = analysisResult.chord_progression.map(c =>
        c === chord ? newChord : c
      )
      setAnalysisResult({
        ...analysisResult,
        chord_progression: updatedChords
      })
      setSelectedChord(null)
    } catch (err) {
      console.error('Chord correction error:', err)
      setError(err as string)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Chord Analyzer Neo</h1>
        <ModelSelector
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <span>エラー: {error}</span>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {!audioFile ? (
          <FileSelector onFileSelect={handleFileSelect} />
        ) : (
          <>
            <div className="file-info">
              <span className="file-name">{audioFile.split('/').pop()}</span>
              <button onClick={handleFileSelect} className="btn-secondary">
                別のファイルを選択
              </button>
            </div>

            {isAnalyzing ? (
              <div className="loading">
                <div className="spinner"></div>
                <p>音声を解析中...</p>
              </div>
            ) : analysisResult ? (
              <>
                <AudioControls
                  isPlaying={isPlaying}
                  currentPosition={currentPosition}
                  duration={analysisResult.chord_progression[analysisResult.chord_progression.length - 1]?.end_time || 0}
                  volume={volume}
                  onPlayPause={handlePlayPause}
                  onStop={handleStop}
                  onSeek={handleSeek}
                  onVolumeChange={handleVolumeChange}
                />

                <div className="analysis-info">
                  <span>テンポ: {analysisResult.tempo} BPM</span>
                  <span>キー: {analysisResult.key}</span>
                  <span>拍子: {analysisResult.time_signature[0]}/{analysisResult.time_signature[1]}</span>
                </div>

                <ChordVisualization
                  chords={analysisResult.chord_progression}
                  currentPosition={currentPosition}
                  onChordClick={setSelectedChord}
                />

                <LyricsDisplay
                  lyrics={analysisResult.lyrics}
                  chords={analysisResult.chord_progression}
                  currentPosition={currentPosition}
                />
              </>
            ) : null}
          </>
        )}
      </main>

      {selectedChord && (
        <ChordEditor
          chord={selectedChord}
          onSave={handleChordEdit}
          onCancel={() => setSelectedChord(null)}
        />
      )}
    </div>
  )
}

export default App
