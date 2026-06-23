import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'
import ApplicationDetailModal from '../components/ApplicationDetailModal'

const COLUMNS = [
  { key: 'wishlist', label: 'Wishlist', color: 'var(--accent)' },
  { key: 'applied', label: 'Applied', color: '#3b82f6' },
  { key: 'under_review', label: 'Under Review', color: '#f59e0b' },
  { key: 'interview_scheduled', label: 'Interview', color: '#8b5cf6' },
  { key: 'offer_received', label: 'Offer', color: '#10b981' },
  { key: 'rejected', label: 'Rejected', color: '#ef4444' },
  { key: 'accepted', label: 'Accepted', color: '#059669' },
  { key: 'withdrawn', label: 'Withdrawn', color: '#6b7280' },
]

export default function Tracker() {
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedId, setSelectedId] = useState(null)
  const [error, setError] = useState(null)

  const fetchApps = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getApplications()
      setApps(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchApps() }, [fetchApps])

  const handleDrop = async (appId, newStatus) => {
    try {
      await api.updateApplication(appId, { status: newStatus })
      setApps(prev => prev.map(a =>
        a.id === appId ? { ...a, status: newStatus } : a
      ))
    } catch { }
  }

  const grouped = {}
  COLUMNS.forEach(col => { grouped[col.key] = [] })
  apps.forEach(app => {
    if (grouped[app.status]) {
      grouped[app.status].push(app)
    } else {
      grouped.wishlist.push(app)
    }
  })

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>Application Tracker</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Drag applications between columns or click to update status.
          </p>
        </div>
        <button className="btn btn-primary" onClick={fetchApps} style={{ fontSize: '0.85rem' }}>
          Refresh
        </button>
      </div>

      {error && (
        <div style={{
          background: 'rgba(239,68,68,0.1)', color: '#ef4444',
          padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem',
          fontSize: '0.875rem',
        }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>Loading applications...</div>
      ) : apps.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem' }}>
          <div style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>No applications yet</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Start by saving jobs from the Jobs page to build your tracker.
          </div>
          <a href="/jobs" style={{ color: 'var(--accent)', fontSize: '0.9rem' }}>Browse Jobs &rarr;</a>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
          gap: '1rem',
          minHeight: '60vh',
        }}>
          {COLUMNS.map(col => (
            <div
              key={col.key}
              className="card"
              style={{
                padding: '0',
                display: 'flex',
                flexDirection: 'column',
                maxHeight: 'calc(100vh - 220px)',
              }}
              onDragOver={e => e.preventDefault()}
              onDrop={e => {
                e.preventDefault()
                const appId = e.dataTransfer.getData('applicationId')
                if (appId) handleDrop(appId, col.key)
              }}
            >
              <div style={{
                padding: '0.75rem 1rem',
                borderBottom: '2px solid ' + col.color,
                display: 'flex', justifyContent: 'space-between',
                alignItems: 'center',
                flexShrink: 0,
              }}>
                <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{col.label}</span>
                <span style={{
                  background: col.color + '22',
                  color: col.color,
                  padding: '0.125rem 0.5rem',
                  borderRadius: '999px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                }}>
                  {(grouped[col.key] || []).length}
                </span>
              </div>
              <div style={{
                padding: '0.5rem',
                overflowY: 'auto',
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem',
              }}>
                {(grouped[col.key] || []).map(app => (
                  <div
                    key={app.id}
                    draggable
                    onDragStart={e => {
                      e.dataTransfer.setData('applicationId', app.id)
                      e.dataTransfer.effectAllowed = 'move'
                    }}
                    onClick={() => setSelectedId(app.id)}
                    style={{
                      padding: '0.75rem',
                      borderRadius: '8px',
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border)',
                      cursor: 'pointer',
                      transition: 'border-color 0.15s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = col.color}
                    onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
                  >
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.125rem' }}>
                      {app.job.title}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      {app.job.company}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                      {app.job.location || 'Remote'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedId && (
        <ApplicationDetailModal
          applicationId={selectedId}
          onClose={() => setSelectedId(null)}
          onUpdate={fetchApps}
        />
      )}
    </div>
  )
}
