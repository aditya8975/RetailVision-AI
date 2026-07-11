import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api.js'
import { imgUrl } from '../components/ProductCard.jsx'
import ProductCard from '../components/ProductCard.jsx'

function qualityColor(score) {
  if (score >= 75) return 'var(--signal)'
  if (score >= 50) return 'var(--amber)'
  return 'var(--red)'
}

export default function ProductDetail() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [similar, setSimilar] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    setProduct(null)
    api.getProduct(id).then(setProduct).catch((e) => setError(e.message))
    api.similarProducts(id).then((r) => setSimilar(r)).catch(() => setSimilar([]))
  }, [id])

  if (error) return <div className="panel" style={{ padding: 24 }}>Couldn't load this product: {error}</div>
  if (!product) return <div className="loading-panel"><span className="spinner" style={{ borderTopColor: 'var(--ink)', borderColor: 'rgba(20,23,28,0.15)' }} /></div>

  const attrs = [
    ['Category', product.category],
    ['Color', product.color],
    ['Pattern', product.pattern],
    ['Sleeve', product.sleeve_type],
    ['Neckline', product.neckline],
  ]
  const q = product.quality_details || {}

  return (
    <div>
      <Link to="/catalog" className="tag" style={{ marginBottom: 20, display: 'inline-flex' }}>← Back to catalog</Link>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.1fr', gap: 32, marginTop: 16 }}>
        <div>
          <div className="scan-frame">
            <div className="scan-corner tl" /><div className="scan-corner tr" />
            <div className="scan-corner bl" /><div className="scan-corner br" />
            <div className="scan-line" />
            <img src={imgUrl(product.original_path)} alt={product.category} />
          </div>

          {product.processed_path && (
            <div style={{ marginTop: 14 }}>
              <div className="attr-label" style={{ marginBottom: 8 }}>Background removed</div>
              <div className="scan-frame" style={{ aspectRatio: '4/3', background: 'repeating-conic-gradient(#e9e9e4 0% 25%, #f6f6f2 0% 50%) 50% / 20px 20px' }}>
                <img src={imgUrl(product.processed_path)} alt="background removed" />
              </div>
            </div>
          )}
        </div>

        <div>
          <div className="eyebrow">Analysis complete</div>
          <h1 className="page-title" style={{ fontSize: 26, textTransform: 'capitalize' }}>
            {product.color} {product.category}
          </h1>
          <p className="page-sub" style={{ marginBottom: 22 }}>{product.description}</p>

          <div className="panel" style={{ padding: '4px 20px', marginBottom: 18 }}>
            {attrs.map(([label, value]) => (
              <div className="attr-row" key={label}>
                <span className="attr-label">{label}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span className="attr-value" style={{ textTransform: 'capitalize' }}>{value || '—'}</span>
                  {product.attribute_confidences && (
                    <span className="attr-conf">
                      {Math.round((product.attribute_confidences[label.toLowerCase() === 'sleeve' ? 'sleeve_type' : label.toLowerCase()] || 0) * 100)}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="panel" style={{ padding: 20, marginBottom: 18 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10 }}>
              <span className="section-title" style={{ margin: 0, fontSize: 15 }}>Image quality</span>
              <span className="attr-conf" style={{ color: qualityColor(product.quality_score), fontSize: 15, fontWeight: 700 }}>
                {product.quality_score}/100
              </span>
            </div>
            <div className="quality-bar-track">
              <div className="quality-bar-fill" style={{ width: `${product.quality_score}%`, background: qualityColor(product.quality_score) }} />
            </div>
            {q.issues && q.issues.length > 0 ? (
              <ul style={{ margin: '12px 0 0', paddingLeft: 18, fontSize: 13, color: 'var(--ink-soft)' }}>
                {q.issues.map((issue) => <li key={issue}>{issue}</li>)}
              </ul>
            ) : (
              <div style={{ marginTop: 12, fontSize: 13, color: 'var(--signal)' }}>Publish-ready — no issues detected</div>
            )}
          </div>

          {product.ocr_text && (
            <div className="panel" style={{ padding: 20 }}>
              <div className="section-title" style={{ fontSize: 15 }}>Text detected on label</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--ink-soft)' }}>
                {product.ocr_text}
              </div>
            </div>
          )}
        </div>
      </div>

      {similar.length > 0 && (
        <div style={{ marginTop: 48 }}>
          <div className="section-title">Similar products</div>
          <div className="grid-4">
            {similar.map((s) => (
              <ProductCard key={s.product.id} product={s.product} similarity={s.similarity} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
