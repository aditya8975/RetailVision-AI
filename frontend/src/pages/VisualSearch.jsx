import { useCallback, useState } from 'react'
import { api } from '../api.js'
import ProductCard from '../components/ProductCard.jsx'

export default function VisualSearch() {
  const [queryFile, setQueryFile] = useState(null)
  const [queryPreview, setQueryPreview] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const runSearch = useCallback(async (file) => {
    if (!file) return
    setQueryFile(file)
    setQueryPreview(URL.createObjectURL(file))
    setLoading(true)
    setError(null)
    try {
      const r = await api.visualSearch(file)
      setResults(r)
    } catch (e) {
      setError(e.message || 'Search failed')
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <div>
      <div className="eyebrow">Visual search</div>
      <h1 className="page-title">Find visually similar products</h1>
      <p className="page-sub">
        Upload any product photo — the query image is embedded with CLIP and ranked
        against the catalog by cosine similarity. No text search, no tags required.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: 28, alignItems: 'start' }}>
        <label className="dropzone" style={{ padding: '32px 16px' }}>
          {queryPreview ? (
            <img src={queryPreview} alt="query" style={{ width: '100%', borderRadius: 8, marginBottom: 12 }} />
          ) : (
            <div className="dropzone-icon">◎</div>
          )}
          <div className="dropzone-title" style={{ fontSize: 14 }}>{queryFile ? 'Change query image' : 'Upload query image'}</div>
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            style={{ display: 'none' }}
            onChange={(e) => runSearch(e.target.files?.[0])}
          />
        </label>

        <div>
          {loading && <div className="loading-panel"><span className="spinner" style={{ borderTopColor: 'var(--ink)', borderColor: 'rgba(20,23,28,0.15)' }} /></div>}
          {error && <div className="panel" style={{ padding: 16, borderColor: 'var(--red)', background: 'var(--red-soft)', color: 'var(--red)' }}>{error}</div>}

          {!loading && results && results.length === 0 && (
            <div className="panel empty-state">
              <div className="empty-state-title">No matches yet</div>
              <div style={{ fontSize: 14 }}>Upload some products to the catalog first, then search again.</div>
            </div>
          )}

          {!loading && results && results.length > 0 && (
            <div className="grid-3">
              {results.map((r) => <ProductCard key={r.product.id} product={r.product} similarity={r.similarity} />)}
            </div>
          )}

          {!loading && !results && (
            <div className="panel empty-state">
              <div className="empty-state-title">Waiting for a query image</div>
              <div style={{ fontSize: 14 }}>Results will rank the whole catalog by visual similarity.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
