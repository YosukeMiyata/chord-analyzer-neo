import { useState } from 'react'

function App() {
  const [message, setMessage] = useState('Chord Analyzer Neo')

  return (
    <div className="container">
      <h1>{message}</h1>
      <p>音声ファイルからコード進行を自動推定</p>
    </div>
  )
}

export default App
