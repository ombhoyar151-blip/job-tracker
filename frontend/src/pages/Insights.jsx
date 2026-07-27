import { useState, useEffect } from 'react'
import { api } from '../services/api'

const STATUS_COLORS = {
  saved: 'var(--accent)', Applied: '#3b82f6', 'Under Review': '#f59e0b',
  Interview: '#8b5cf6', Offer: '#10b981', Rejected: '#ef4444',
  Accepted: '#059669', Withdrawn: '#6b7280',
}

export default function Insights() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getInsights()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>Loading insights...</div>
  }

  if (!data) {
    return <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>Failed to load insights.</div>
  }

  const maxFunnel = Math.max(...data.funnel.map(f => f.count), 1)
  const maxTrend = Math.max(...data.trends.map(t => t.count), 1)

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>Career Insights</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Analytics and trends for your job search.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent)' }}>{data.total_applications}</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.25rem' }}>Total Applications</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#3b82f6' }}>{data.active_applications}</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.25rem' }}>Active</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#8b5cf6' }}>{data.interview_rate}%</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.25rem' }}>Interview Rate</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#10b981' }}>{data.offer_rate}%</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.25rem' }}>Offer Rate</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>Application Funnel</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {data.funnel.map(step => (
              <div key={step.status}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{step.label}</span>
                  <span style={{ fontWeight: 600 }}>{step.count}</span>
                </div>
                <div style={{ height: '8px', background: 'var(--bg-primary)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%', width: `${(step.count / maxFunnel) * 100}%`,
                    background: STATUS_COLORS[step.label] || 'var(--accent)',
                    borderRadius: '4px', transition: 'width 0.3s',
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>Applications Over Time</h2>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem', height: '160px' }}>
            {data.trends.map(t => (
              <div key={t.month} style={{
                flex: 1, display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'flex-end',
                height: '100%',
              }}>
                <div style={{
                  width: '100%', maxWidth: '40px',
                  height: `${(t.count / maxTrend) * 140}px`,
                  minHeight: t.count > 0 ? '4px' : '2px',
                  background: 'var(--accent)',
                  borderRadius: '4px 4px 0 0',
                  transition: 'height 0.3s',
                }} />
                <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', marginTop: '0.25rem', textAlign: 'center' }}>
                  {t.month.split(' ')[0]}<br />{t.count}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {data.skill_gaps && data.skill_gaps.length > 0 && (
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>Skills in Demand (You Don't Have Yet)</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '1rem' }}>
            These skills appear frequently in job listings but are missing from your profile.
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {data.skill_gaps.map(sg => (
              <div key={sg.skill} style={{
                display: 'flex', alignItems: 'center', gap: '0.5rem',
                padding: '0.4rem 0.75rem', borderRadius: '8px',
                background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)',
                fontSize: '0.8rem',
              }}>
                <span style={{ color: 'var(--text-primary)' }}>{sg.skill}</span>
                <span style={{
                  background: 'rgba(245,158,11,0.2)', color: '#f59e0b',
                  padding: '0.125rem 0.4rem', borderRadius: '999px',
                  fontSize: '0.65rem', fontWeight: 600,
                }}>
                  {sg.demand_count}
                </span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Add these skills to your profile to improve job match scores.
          </div>
        </div>
      )}
    </div>
  )
}
