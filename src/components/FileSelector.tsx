interface FileSelectorProps {
  onFileSelect: () => void
}

function FileSelector({ onFileSelect }: FileSelectorProps) {
  return (
    <div className="file-selector">
      <div className="file-selector-content">
        <svg
          className="file-icon"
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M9 18V5l12-2v13" />
          <circle cx="6" cy="18" r="3" />
          <circle cx="18" cy="16" r="3" />
        </svg>
        <h2>音声ファイルを選択</h2>
        <p>MP3, WAV, FLAC, OGG, M4A形式に対応</p>
        <button onClick={onFileSelect} className="btn-primary">
          ファイルを選択
        </button>
      </div>
    </div>
  )
}

export default FileSelector
