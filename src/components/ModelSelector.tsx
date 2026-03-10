import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'

interface ModelConfig {
  model_id: string
  model_name: string
  description: string
  is_default: boolean
}

interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (modelId: string) => void
}

function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
  const [models, setModels] = useState<ModelConfig[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadModels = async () => {
      try {
        const availableModels = await invoke<ModelConfig[]>('list_models')
        setModels(availableModels)
      } catch (error) {
        console.error('Failed to load models:', error)
        // Fallback to default model
        setModels([
          {
            model_id: 'default',
            model_name: 'デフォルトモデル',
            description: '汎用的なコード推定モデル',
            is_default: true
          }
        ])
      } finally {
        setIsLoading(false)
      }
    }
    loadModels()
  }, [])

  const selectedModelConfig = models.find(m => m.model_id === selectedModel)

  if (isLoading) {
    return (
      <div className="model-selector">
        <button className="model-selector-button" disabled>
          <span>読み込み中...</span>
        </button>
      </div>
    )
  }

  return (
    <div className="model-selector">
      <button
        className="model-selector-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="3" />
          <path d="M12 1v6m0 6v6m5.2-13.2l-4.2 4.2m0 6l4.2 4.2M23 12h-6m-6 0H1m18.2 5.2l-4.2-4.2m0-6l4.2-4.2" />
        </svg>
        <span>{selectedModelConfig?.model_name || 'モデルを選択'}</span>
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {isOpen && (
        <div className="model-dropdown">
          {models.map(model => (
            <button
              key={model.model_id}
              className={`model-option ${selectedModel === model.model_id ? 'selected' : ''}`}
              onClick={() => {
                onModelChange(model.model_id)
                setIsOpen(false)
              }}
            >
              <div className="model-option-header">
                <span className="model-name">{model.model_name}</span>
                {model.is_default && <span className="model-badge">デフォルト</span>}
              </div>
              <p className="model-description">{model.description}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default ModelSelector
