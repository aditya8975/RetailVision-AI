import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line,
} from 'recharts'
import { api } from '../api.js'

const PALETTE = ['#00B37A', '#14171C', '#E8A33D', '#6B7280', '#8FD9BE', '#D64545', '#B8B4A6']

function toChartData(obj) {
  return Object.entries(obj || {}).map(([name, value]) => ({ name, value }))
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.dashboardStats().then(setStats).catch(() => setStats(null))
  }, [])

  if (!stats) return <div className="loading-panel"><span className="spinner" style={{ borderTopColor: 'var(--ink)', borderColor: 'rgba(20,23,28,0.15)' }} /></div>

  const categoryData = toChartData(stats.category_breakdown)
  const colorData = toChartData(stats.color_breakdown)
  const patternData = toChartData(stats.pattern_breakdown)
  const uploadsData = Object.entries(stats.uploads_by_day || {}).map(([date, count]) => ({ date, count }))

  return (
    <div>
      <div className="eyebrow">Analytics</div>
      <h1 className="page-title">Catalog dashboard</h1>
      <p className="page-sub">A live rollup of everything the pipeline has processed so far.</p>

      <div className="grid-4" style={{ marginBottom: 32 }}>
        <div className="panel stat-card">
          <div className="stat-value">{stats.total_products}</div>
          <div className="stat-label">Total products</div>
        </div>
        <div className="panel stat-card">
          <div className="stat-value" style={{ color: 'var(--signal)' }}>{stats.avg_quality_score}</div>
          <div className="stat-label">Avg. quality score</div>
        </div>
        <div className="panel stat-card">
          <div className="stat-value" style={{ color: stats.low_quality_count > 0 ? 'var(--amber)' : undefined }}>{stats.low_quality_count}</div>
          <div className="stat-label">Below quality threshold</div>
        </div>
        <div className="panel stat-card">
          <div className="stat-value">{Object.keys(stats.category_breakdown).length}</div>
          <div className="stat-label">Distinct categories</div>
        </div>
      </div>

      {stats.total_products === 0 ? (
        <div className="panel empty-state">
          <div className="empty-state-title">No data yet</div>
          <div style={{ fontSize: 14 }}>Upload some products to populate the dashboard.</div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 20 }}>
          <div className="panel" style={{ padding: 20 }}>
            <div className="section-title">Uploads over time</div>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={uploadsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E4E2DC" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fontFamily: 'JetBrains Mono' }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11, fontFamily: 'JetBrains Mono' }} />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#00B37A" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="panel" style={{ padding: 20 }}>
            <div className="section-title">Color distribution</div>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={colorData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                  {colorData.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="panel" style={{ padding: 20 }}>
            <div className="section-title">Category breakdown</div>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={categoryData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E4E2DC" />
                <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11, fontFamily: 'JetBrains Mono' }} />
                <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 11.5, textTransform: 'capitalize' }} />
                <Tooltip />
                <Bar dataKey="value" fill="#14171C" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="panel" style={{ padding: 20 }}>
            <div className="section-title">Pattern breakdown</div>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={patternData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E4E2DC" />
                <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11, fontFamily: 'JetBrains Mono' }} />
                <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 11.5, textTransform: 'capitalize' }} />
                <Tooltip />
                <Bar dataKey="value" fill="#E8A33D" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
