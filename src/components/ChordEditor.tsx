import { useState } from 'react'

interface ChordSegment {
  start_time: number
  end_time: number
  root: string
  quality: string
  bass_note?: string
  extensions?: string[]
  confidence: number
}

interface ChordEditorProps {
  chord: ChordSegment
  onSave: (originalChord: ChordSegment, newChord: ChordSegment) => void
  onCancel: () => void
}

const ROOTS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
const QUALITIES = [
  { value: 'maj', label: 'Major' },
  { value: 'min', label: 'Minor' },
  { value: '7', label: 'Dominant 7th' },
  { value: 'maj7', label: 'Major 7th' },
  { value: 'min7', label: 'Minor 7th' },
  { value: 'dim', label: 'Diminished' },
  { value: 'aug', label: 'Augmented' },
  { value: 'sus4', label: 'Sus4' },
  { value: 'sus2', label: 'Sus2' },
  { value: '9', label: '9th' },
  { value: '11', label: '11th' },
  { value: '13', label: '13th' }
]

function ChordEditor({ chord, onSave, onCancel }: ChordEditorProps) {
  const [root, setRoot] = useState(chord.root)
  const [quality, setQuality] = useState(chord.quality)
  const [bassNote, setBassNote] = useState(chord.bass_note || '')
  const [extensions, setExtensions] = useState(chord.extensions?.join(',') || '')

  const handleSave = () => {
    const newChord: ChordSegment = {
      ...chord,
      root,
      quality,
      bass_note: bassNote || undefined,
      extensions: extensions ? extensions.split(',').map(e => e.trim()) : undefined,
      confidence: 1.0 // User-corrected chords have 100% confidence
    }
    onSave(chord, newChord)
  }

  const formatChord = () => {
    let chordStr = `${root}${quality}`
    if (extensions) {
      chordStr += `(${extensions})`
    }
    if (bassNote) {
      chordStr += `/${bassNote}`
    }
    return chordStr
  }

  return (
    <div className="chord-editor-overlay" onClick={onCancel}>
      <div className="chord-editor" onClick={(e) => e.stopPropagation()}>
        <h3>コードを編集</h3>
        
        <div className="editor-preview">
          <span className="preview-label">プレビュー:</span>
          <span className="preview-chord">{formatChord()}</span>
        </div>

        <div className="editor-field">
          <label>ルート音</label>
          <select value={root} onChange={(e) => setRoot(e.target.value)}>
            {ROOTS.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        <div className="editor-field">
          <label>コード品質</label>
          <select value={quality} onChange={(e) => setQuality(e.target.value)}>
            {QUALITIES.map(q => (
              <option key={q.value} value={q.value}>{q.label}</option>
            ))}
          </select>
        </div>

        <div className="editor-field">
          <label>ベース音 (分数コード)</label>
          <select value={bassNote} onChange={(e) => setBassNote(e.target.value)}>
            <option value="">なし</option>
            {ROOTS.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        <div className="editor-field">
          <label>拡張音 (カンマ区切り)</label>
          <input
            type="text"
            value={extensions}
            onChange={(e) => setExtensions(e.target.value)}
            placeholder="例: 9, 11"
          />
        </div>

        <div className="editor-info">
          <div>開始時刻: {chord.start_time.toFixed(2)}s</div>
          <div>終了時刻: {chord.end_time.toFixed(2)}s</div>
          <div>元の信頼度: {(chord.confidence * 100).toFixed(0)}%</div>
        </div>

        <div className="editor-actions">
          <button onClick={onCancel} className="btn-secondary">
            キャンセル
          </button>
          <button onClick={handleSave} className="btn-primary">
            保存
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChordEditor
