interface AudioControlsProps {
  isPlaying: boolean
  currentPosition: number
  duration: number
  volume: number
  onPlayPause: () => void
  onStop: () => void
  onSeek: (position: number) => void
  onVolumeChange: (volume: number) => void
}

function AudioControls({
  isPlaying,
  currentPosition,
  duration,
  volume,
  onPlayPause,
  onStop,
  onSeek,
  onVolumeChange
}: AudioControlsProps) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="audio-controls">
      <div className="playback-controls">
        <button onClick={onStop} className="control-btn" title="停止">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" />
          </svg>
        </button>
        <button onClick={onPlayPause} className="control-btn play-btn" title={isPlaying ? '一時停止' : '再生'}>
          {isPlaying ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="4" width="4" height="16" />
              <rect x="14" y="4" width="4" height="16" />
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z" />
            </svg>
          )}
        </button>
      </div>

      <div className="timeline">
        <span className="time-display">{formatTime(currentPosition)}</span>
        <input
          type="range"
          min="0"
          max={duration}
          value={currentPosition}
          onChange={(e) => onSeek(parseFloat(e.target.value))}
          className="timeline-slider"
        />
        <span className="time-display">{formatTime(duration)}</span>
      </div>

      <div className="volume-control">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" />
        </svg>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={volume}
          onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
          className="volume-slider"
        />
      </div>
    </div>
  )
}

export default AudioControls
