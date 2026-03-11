interface ChordSegment {
  start_time: number
  end_time: number
  root: string
  quality: string
  bass_note?: string
  extensions?: string[]
  confidence: number
}

interface ChordVisualizationProps {
  chords: ChordSegment[]
  currentPosition: number
  onChordClick: (chord: ChordSegment) => void
  tempo?: number // BPM, defaults to 120
}

function ChordVisualization({ chords, currentPosition, onChordClick, tempo = 120 }: ChordVisualizationProps) {
  const BARS_PER_LINE = 16
  const BEATS_PER_BAR = 4 // Assuming 4/4 time signature for now

  const formatChord = (chord: ChordSegment) => {
    let chordStr = `${chord.root}${chord.quality}`
    if (chord.extensions && chord.extensions.length > 0) {
      chordStr += `(${chord.extensions.join(',')})`
    }
    if (chord.bass_note) {
      chordStr += `/${chord.bass_note}`
    }
    return chordStr
  }

  const isLowConfidence = (chord: ChordSegment) => {
    return chord.confidence < 0.7
  }

  const isCurrentChord = (chord: ChordSegment) => {
    return currentPosition >= chord.start_time && currentPosition < chord.end_time
  }

  // Group chords into lines of 16 bars
  const groupChordsIntoLines = () => {
    const lines: ChordSegment[][] = []
    let currentLine: ChordSegment[] = []
    let barCount = 0

    // Calculate seconds per bar based on tempo
    const secondsPerBeat = 60 / tempo
    const secondsPerBar = secondsPerBeat * BEATS_PER_BAR

    chords.forEach((chord) => {
      const chordDuration = chord.end_time - chord.start_time
      const barsInChord = Math.ceil(chordDuration / secondsPerBar)

      if (barCount + barsInChord > BARS_PER_LINE && currentLine.length > 0) {
        lines.push(currentLine)
        currentLine = []
        barCount = 0
      }

      currentLine.push(chord)
      barCount += barsInChord
    })

    if (currentLine.length > 0) {
      lines.push(currentLine)
    }

    return lines
  }

  const chordLines = groupChordsIntoLines()

  return (
    <div className="chord-visualization">
      <h3>コード進行</h3>
      <div className="chord-timeline">
        {chordLines.map((line, lineIndex) => (
          <div key={lineIndex} className="chord-line">
            <span className="line-number">{lineIndex * BARS_PER_LINE + 1}</span>
            <div className="chord-bars">
              {line.map((chord, chordIndex) => (
                <button
                  key={`${lineIndex}-${chordIndex}`}
                  className={`chord-segment ${isCurrentChord(chord) ? 'current' : ''} ${isLowConfidence(chord) ? 'low-confidence' : ''}`}
                  onClick={() => onChordClick(chord)}
                  title={`${formatChord(chord)} (信頼度: ${(chord.confidence * 100).toFixed(0)}%)`}
                >
                  <span className="chord-name">{formatChord(chord)}</span>
                  <span className="chord-time">{chord.start_time.toFixed(1)}s</span>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="legend">
        <div className="legend-item">
          <span className="legend-color current"></span>
          <span>現在再生中</span>
        </div>
        <div className="legend-item">
          <span className="legend-color low-confidence"></span>
          <span>低信頼度 (&lt;70%)</span>
        </div>
      </div>
    </div>
  )
}

export default ChordVisualization
