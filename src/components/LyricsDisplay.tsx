interface LyricSegment {
  start_time: number
  end_time: number
  text: string
  confidence: number
}

interface ChordSegment {
  start_time: number
  end_time: number
  root: string
  quality: string
  bass_note?: string
  extensions?: string[]
  confidence: number
}

interface LyricsDisplayProps {
  lyrics: LyricSegment[]
  chords: ChordSegment[]
  currentPosition: number
}

function LyricsDisplay({ lyrics, chords, currentPosition }: LyricsDisplayProps) {
  const formatChord = (chord: ChordSegment) => {
    let chordStr = `${chord.root}${chord.quality}`
    if (chord.bass_note) {
      chordStr += `/${chord.bass_note}`
    }
    return chordStr
  }

  const getChordsForLyric = (lyric: LyricSegment): ChordSegment[] => {
    return chords.filter(chord =>
      (chord.start_time >= lyric.start_time && chord.start_time < lyric.end_time) ||
      (chord.end_time > lyric.start_time && chord.end_time <= lyric.end_time) ||
      (chord.start_time <= lyric.start_time && chord.end_time >= lyric.end_time)
    )
  }

  const isCurrentLyric = (lyric: LyricSegment) => {
    return currentPosition >= lyric.start_time && currentPosition < lyric.end_time
  }

  if (lyrics.length === 0) {
    return (
      <div className="lyrics-display">
        <h3>歌詞</h3>
        <p className="no-lyrics">歌詞が検出されませんでした</p>
      </div>
    )
  }

  return (
    <div className="lyrics-display">
      <h3>歌詞とコード</h3>
      <div className="lyrics-content">
        {lyrics.map((lyric, index) => {
          const associatedChords = getChordsForLyric(lyric)
          return (
            <div
              key={index}
              className={`lyric-line ${isCurrentLyric(lyric) ? 'current' : ''}`}
            >
              {associatedChords.length > 0 && (
                <div className="lyric-chords">
                  {associatedChords.map((chord, chordIndex) => (
                    <span key={chordIndex} className="lyric-chord">
                      {formatChord(chord)}
                    </span>
                  ))}
                </div>
              )}
              <div className="lyric-text">{lyric.text}</div>
              <div className="lyric-time">{lyric.start_time.toFixed(1)}s</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default LyricsDisplay
