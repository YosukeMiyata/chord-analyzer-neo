import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { convertFileSrc } from '@tauri-apps/api/core'
import { open } from '@tauri-apps/plugin-dialog'
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
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null)

  const handleFileSelect = async (filepath: string) => {
    if (filepath) {
      setAudioFile(filepath)
      setError(null)
      
      // Create audio element for playback using Tauri's convertFileSrc
      const audioSrc = convertFileSrc(filepath)
      console.log('Audio source:', audioSrc)
      const audio = new Audio(audioSrc)
      audio.volume = volume
      audio.addEventListener('timeupdate', () => {
        setCurrentPosition(audio.currentTime)
      })
      audio.addEventListener('ended', () => {
        setIsPlaying(false)
        setCurrentPosition(0)
      })
      audio.addEventListener('error', (e) => {
        console.error('Audio element error:', e)
        setError('音声ファイルの読み込みエラー')
      })
      setAudioElement(audio)
      
      await analyzeAudio(filepath)
    }
  }

  const analyzeAudio = async (filepath: string, forceNoCache: boolean = false) => {
    setIsAnalyzing(true)
    setError(null)
    try {
      const result = await invoke<AnalysisResult>('analyze_audio', {
        filepath,
        modelId: selectedModel,
        useCache: !forceNoCache
      })
      
      // Merge consecutive identical chords
      const mergedChords = mergeConsecutiveChords(result.chord_progression)
      
      // Automatically determine optimal grouping based on chord change frequency
      const groupedChords = smartGroupChords(mergedChords, result.tempo)
      
      setAnalysisResult({
        ...result,
        chord_progression: groupedChords
      })
    } catch (err) {
      console.error('Analysis failed:', err)
      setError(err as string)
    } finally {
      setIsAnalyzing(false)
    }
  }

  // Helper function to merge consecutive identical chords
  const mergeConsecutiveChords = (chords: ChordSegment[]): ChordSegment[] => {
    if (chords.length === 0) return chords
    
    const merged: ChordSegment[] = []
    let current = { ...chords[0] }
    
    for (let i = 1; i < chords.length; i++) {
      const chord = chords[i]
      
      // Check if chord is identical to current (same root, quality, bass, extensions)
      const isSame = 
        chord.root === current.root &&
        chord.quality === current.quality &&
        chord.bass_note === current.bass_note &&
        JSON.stringify(chord.extensions) === JSON.stringify(current.extensions)
      
      if (isSame) {
        // Extend the current chord's end time
        current.end_time = chord.end_time
        // Average the confidence
        current.confidence = (current.confidence + chord.confidence) / 2
      } else {
        // Push the current chord and start a new one
        merged.push(current)
        current = { ...chord }
      }
    }
    
    // Push the last chord
    merged.push(current)
    
    return merged
  }

  // Helper function to group chords by bars (4 bars per group)
  // Takes the most common or highest confidence chord in each group
  const groupChordsByBars = (chords: ChordSegment[], tempo: number, barsPerGroup: number = 4): ChordSegment[] => {
    if (chords.length === 0) return chords
    
    const BEATS_PER_BAR = 4 // Assuming 4/4 time signature
    const secondsPerBeat = 60 / tempo
    const secondsPerBar = secondsPerBeat * BEATS_PER_BAR
    const secondsPerGroup = secondsPerBar * barsPerGroup
    
    const grouped: ChordSegment[] = []
    let currentGroupStart = 0
    
    while (currentGroupStart < chords[chords.length - 1].end_time) {
      const groupEnd = currentGroupStart + secondsPerGroup
      
      // Find all chords that overlap with this group
      const chordsInGroup = chords.filter(chord => 
        chord.start_time < groupEnd && chord.end_time > currentGroupStart
      )
      
      if (chordsInGroup.length > 0) {
        // Calculate weighted score for each chord (duration * confidence - penalty)
        let bestChord = chordsInGroup[0]
        let bestScore = -Infinity
        
        chordsInGroup.forEach(chord => {
          const overlapStart = Math.max(chord.start_time, currentGroupStart)
          const overlapEnd = Math.min(chord.end_time, groupEnd)
          const duration = overlapEnd - overlapStart
          
          // Apply penalty for maj7 (prefer simpler major chords)
          let penalty = 0
          if (chord.quality === 'maj7') {
            penalty = 0.10
          }
          
          // Score = duration * confidence - penalty
          const score = duration * chord.confidence - penalty
          
          if (score > bestScore) {
            bestScore = score
            bestChord = chord
          }
        })
        
        // Use the best scored chord as representative
        const representativeChord = { ...bestChord }
        representativeChord.start_time = currentGroupStart
        representativeChord.end_time = Math.min(groupEnd, chords[chords.length - 1].end_time)
        
        grouped.push(representativeChord)
      }
      
      currentGroupStart = groupEnd
    }
    
    return grouped
  }

  // Helper function to automatically determine optimal grouping based on chord change frequency
  const smartGroupChords = (chords: ChordSegment[], tempo: number): ChordSegment[] => {
    if (chords.length === 0) return chords
    
    const BEATS_PER_BAR = 4
    const secondsPerBeat = 60 / tempo
    const secondsPerBar = secondsPerBeat * BEATS_PER_BAR
    
    // Analyze chord change frequency
    // Calculate average chord duration in bars
    const avgChordDuration = chords.reduce((sum, chord) => 
      sum + (chord.end_time - chord.start_time), 0) / chords.length
    const avgBarsPerChord = avgChordDuration / secondsPerBar
    
    // Determine grouping strategy: 4-bar or 2-bar grouping
    let barsPerGroup: number
    
    if (avgBarsPerChord >= 1.5) {
      // Slow chord changes: use 4-bar grouping
      barsPerGroup = 4
    } else {
      // Fast chord changes: use 2-bar grouping
      barsPerGroup = 2
    }
    
    return groupChordsByBars(chords, tempo, barsPerGroup)
  }

  const handlePlayPause = async () => {
    if (!audioElement) return
    
    try {
      if (isPlaying) {
        audioElement.pause()
      } else {
        await audioElement.play()
      }
      setIsPlaying(!isPlaying)
    } catch (err) {
      console.error('Playback error:', err)
      setError('音声再生エラー: ' + err)
    }
  }

  const handleStop = async () => {
    if (!audioElement) return
    
    try {
      audioElement.pause()
      audioElement.currentTime = 0
      setIsPlaying(false)
      setCurrentPosition(0)
    } catch (err) {
      console.error('Stop error:', err)
    }
  }

  const handleSeek = async (position: number) => {
    if (!audioElement) return
    
    try {
      audioElement.currentTime = position
      setCurrentPosition(position)
    } catch (err) {
      console.error('Seek error:', err)
    }
  }

  const handleVolumeChange = async (newVolume: number) => {
    if (!audioElement) return
    
    try {
      audioElement.volume = newVolume
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
              <button onClick={async () => {
                console.log('Re-analyze without cache')
                await analyzeAudio(audioFile, true)
              }} className="btn-secondary" disabled={isAnalyzing}>
                キャッシュなしで再解析
              </button>
              <button onClick={async () => {
                console.log('Change file button clicked')
                try {
                  const selected = await open({
                    multiple: false,
                    filters: [{
                      name: 'Audio',
                      extensions: ['mp3', 'wav', 'flac', 'ogg', 'm4a']
                    }]
                  })
                  console.log('Selected file:', selected)
                  if (selected && typeof selected === 'string') {
                    handleFileSelect(selected)
                  }
                } catch (err) {
                  console.error('File selection error:', err)
                  alert('ファイル選択エラー: ' + err)
                }
              }} className="btn-secondary">
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
                  tempo={analysisResult.tempo}
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
