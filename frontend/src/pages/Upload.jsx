import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api.js'

const STEPS = [
  'Localizing product region (YOLO)',
  'Classifying attributes (CLIP zero-shot)',
  'Generating description (BLIP)',
  'Scoring image quality (OpenCV)',
  'Reading labels (OCR)',
  'Removing background (U2Net)',
  'Indexing for visual search (CLIP embedding)',
]

export default function Upload() {
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [stepIdx, setStepIdx] = useState(0)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleFile = useCallback(async (file) => {
    if (!file) return
    setError(null)
    setUploading(true)
    setStepIdx(0)
    const interval = setInterval(() => {
      setStepIdx((i) => (i < STEPS.length - 1 ? i + 1 : i))
    }, 900)
    try {
      const product = await api.uploadProduct(file)
      clearInterval(interval)
      navigate(`/product/${product.id}`)
    } catch (e) {
      clearInterval(interval)
      setError(e.message || 'Upload failed')
      setUploading(false)
    }
  }, [navigate])

  const onDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    const file = e.dataTransfer.files?.[0]
    handleFile(file)
  }

  return (
    <div>
      <div className="eyebrow">Ingestion</div>
      <h1 className="page-title">Upload a product photo</h1>
      <p className="page-sub">
        Drop a clothing or product image and the pipeline detects attributes, writes a
        description, removes the background, scores image quality, reads any printed
        labels, and indexes it for visual search — all in one pass.
      </p>

      {!uploading && (
        <label
          className={`dropzone${dragActive ? ' active' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
          onDragLeave={() => setDragActive(false)}
          onDrop={onDrop}
        >
          <div className="dropzone-icon">↑</div>
          <div className="dropzone-title">Drag & drop, or click to browse</div>
          <div className="dropzone-sub">JPEG · PNG · WEBP</div>
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            style={{ display: 'none' }}
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
        </label>
      )}

      {uploading && (
        <div className="panel loading-panel">
          <span className="spinner" style={{ borderTopColor: 'var(--ink)', borderColor: 'rgba(20,23,28,0.15)' }} />
          <div className="loading-steps">{STEPS[stepIdx]}…</div>
        </div>
      )}

      {error && (
        <div className="panel" style={{ padding: 16, marginTop: 16, borderColor: 'var(--red)', background: 'var(--red-soft)', color: 'var(--red)', fontSize: 14 }}>
          {error}
        </div>
      )}
    </div>
  )
}
