import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../store/AuthContext'
import { api } from '../services/api'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsData, recsData] = await Promise.all([
          api.getDashboardStats(),
          api.getRecommendations(),
        ])
        setStats(statsData)
        setRecommendations(recsData)
      } catch {
        setStats({ saved_jobs: 0, total_applications: 0, interviews_scheduled: 0, offers_received: 0 })
        setRecommendations([])
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const statCards = stats
    ? [
        { label: 'Saved Jobs', value: stats.saved_jobs ?? 0, color: 'var(--accent)' },
        { label: 'Applications', value: stats.total_applications ?? 0, color: 'var(--success)' },
        { label: 'Interviews', value: stats.interviews_scheduled ?? 0, color: 'var(--warning)' },
        { label: 'Offers', value: stats.offers_received ?? 0, color: '#a78bfa' },
      ]
    : []

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>Welcome back, {user?.name}</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Here's an overview of your job search activity.
        </p>
      </div>

      {!loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          {statCards.map(stat => (
            <div key={stat.label} className="card" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: stat.color }}>{stat.value}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.25rem' }}>{stat.label}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>Recommended Jobs</h2>
          {loading ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '3rem 0', fontSize: '0.9rem' }}>Loading...</div>
          ) : recommendations.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '3rem 0', fontSize: '0.9rem' }}>
              No recommendations yet. Add skills to your profile to get started.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {recommendations.slice(0, 5).map((rec, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
                  padding: '0.75rem', borderRadius: '8px',
                  background: 'var(--bg-card)', border: '1px solid var(--border)',
                }}>
                  <div style={{
                    width: '40px', height: '40px', borderRadius: '8px',
                    background: 'var(--accent-light)', color: 'var(--accent)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '0.8rem', fontWeight: 700, flexShrink: 0,
                  }}>
                    {rec.match_score}%
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.125rem' }}>{rec.job.title}</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
                      {rec.job.company} &middot; {rec.job.location}
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', lineHeight: 1.4 }}>
                      {rec.match_reasons.slice(0, 2).map((r, j) => (
                        <span key={j} style={{ display: 'inline-block', marginRight: '0.5rem' }}>&bull; {r}</span>
                      ))}
                    </div>
                  </div>
                  <Link
                    to="/jobs"
                    style={{
                      fontSize: '0.75rem', color: 'var(--accent)', whiteSpace: 'nowrap',
                      textDecoration: 'none', marginTop: '0.25rem',
                    }}
                  >
                    View &rarr;
                  </Link>
                </div>
              ))}
              <Link
                to="/jobs"
                style={{
                  display: 'block', textAlign: 'center', color: 'var(--accent)',
                  fontSize: '0.875rem', textDecoration: 'none', padding: '0.5rem',
                }}
              >
                Browse all jobs &rarr;
              </Link>
            </div>
          )}
        </div>
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>Next Steps</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {[
              { text: 'Upload your resume for AI analysis', link: '/resumes' },
              { text: 'Set up your job preferences', link: '/profile' },
              { text: 'Discover matching jobs', link: '/jobs' },
            ].map((step, i) => (
              <Link
                key={i}
                to={step.link}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.75rem',
                  color: 'var(--text-secondary)', fontSize: '0.875rem',
                  textDecoration: 'none', padding: '0.25rem 0',
                }}
              >
                <span style={{
                  width: '24px', height: '24px', borderRadius: '50%',
                  background: 'var(--accent-light)', color: 'var(--accent)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.75rem', fontWeight: 600, flexShrink: 0,
                }}>{i + 1}</span>
                {step.text}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
