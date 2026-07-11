import { useNavigate } from 'react-router-dom'

function imgUrl(path) {
  if (!path) return ''
  const idx = path.indexOf('/data/')
  if (idx !== -1) {
    const rel = path.slice(idx + 6) // after "/data/"
    return `/media/${rel}`
  }
  return path
}

export default function ProductCard({ product, similarity }) {
  const navigate = useNavigate()
  return (
    <div className="product-card" onClick={() => navigate(`/product/${product.id}`)}>
      <img
        className="product-card-img"
        src={imgUrl(product.original_path)}
        alt={product.category || 'product'}
        loading="lazy"
      />
      <div className="product-card-body">
        <div className="product-card-title">
          {product.color ? `${product.color} ` : ''}{product.category || 'Unclassified'}
        </div>
        <div className="product-card-meta">
          {similarity !== undefined
            ? `${Math.round(similarity * 100)}% match`
            : `Quality ${product.quality_score ?? '—'}`}
        </div>
      </div>
    </div>
  )
}

export { imgUrl }
