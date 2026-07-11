const BASE = '/api';

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  uploadProduct: (file) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/products/upload`, { method: 'POST', body: form }).then(handle);
  },
  listProducts: (limit = 100) =>
    fetch(`${BASE}/products?limit=${limit}`).then(handle),
  getProduct: (id) => fetch(`${BASE}/products/${id}`).then(handle),
  deleteProduct: (id) =>
    fetch(`${BASE}/products/${id}`, { method: 'DELETE' }).then(handle),
  visualSearch: (file, topK = 12) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/search/visual?top_k=${topK}`, { method: 'POST', body: form }).then(handle);
  },
  similarProducts: (id, topK = 8) =>
    fetch(`${BASE}/search/similar/${id}?top_k=${topK}`).then(handle),
  dashboardStats: () => fetch(`${BASE}/dashboard/stats`).then(handle),
};
