import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import ProductCard from '../components/ProductCard.jsx'

export default function Catalog() {
  const [products, setProducts] = useState(null)

  useEffect(() => {
    api.listProducts().then(setProducts).catch(() => setProducts([]))
  }, [])

  return (
    <div>
      <div className="eyebrow">Catalog</div>
      <h1 className="page-title">All products</h1>
      <p className="page-sub">Every image processed through the pipeline, with its detected attributes and quality score.</p>

      {products === null && <div className="loading-panel"><span className="spinner" style={{ borderTopColor: 'var(--ink)', borderColor: 'rgba(20,23,28,0.15)' }} /></div>}

      {products && products.length === 0 && (
        <div className="panel empty-state">
          <div className="empty-state-title">No products yet</div>
          <div style={{ fontSize: 14, marginBottom: 18 }}>Upload your first image to see it analyzed here.</div>
          <Link to="/" className="btn">Upload an image</Link>
        </div>
      )}

      {products && products.length > 0 && (
        <div className="grid-4">
          {products.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  )
}
