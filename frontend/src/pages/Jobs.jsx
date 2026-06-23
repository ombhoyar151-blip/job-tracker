import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'

const JOB_TYPES = ['', 'Remote', 'On-site', 'Hybrid']
const EXP_LEVELS = ['', 'Internship', 'Junior', 'Mid', 'Mid-Senior', 'Senior', 'Lead', 'Principal']
const PAGE_SIZE = 20

export default function Jobs() {
  const [jobs, setJobs] = useState([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [seeding, setSeeding] = useState(false)
  const [message, setMessage] = useState('')
  const [savingId, setSavingId] = useState(null)

  const [filters, setFilters] = useState({
    q: '', location: '', job_type: '', experience_level: '', salary_min: '',
  })

  const fetchJobs = useCallback(async (p = 1) => {
    setLoading(true)
    try {
      const params = { ...filters, page: p, page_size: PAGE_SIZE }
      const data = await api.getJobs(params)
      setJobs(data.jobs)
      setTotal(data.total)
      setTotalPages(data.total_pages)
      setPage(data.page)
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => { fetchJobs(1) }, [fetchJobs])

  const handleSearch = (e) => {
    e.preventDefault()
    fetchJobs(1)
  }

  const handleSeed = async () => {
    setSeeding(true)
    try {
      const res = await api.seedJobs()
      setMessage(res.message)
      setTimeout(() => setMessage(''), 3000)
      fetchJobs(1)
    } catch (err) {
      setMessage(err.message)
    } finally {
      setSeeding(false)
    }
  }

  const handleSave = async (jobId, isSaved) => {
    setSavingId(jobId)
    try {
      if (isSaved) {
        await api.unsaveJob(jobId)
      } else {
        await api.saveJob(jobId)
      }
      setJobs(prev => prev.map(j => j.id === jobId ? { ...j, is_saved: !isSaved } : j))
    } catch (err) {
      setMessage(err.message)
    } finally {
      setSavingId(null)
    }
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <h1 style={{ fontSize: '1.75rem' }}>Jobs</h1>
          <button className="btn btn-secondary" onClick={handleSeed} disabled={seeding} style={{ fontSize: '0.8rem' }}>
            {seeding ? 'Seeding...' : 'Seed Mock Data'}
          </button>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          {total > 0 ? `Found ${total} jobs` : 'Discover and save job opportunities.'}
        </p>
      </div>

      {message && (
        <div style={{
          padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem', fontSize: '0.875rem',
          background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.3)', color: 'var(--accent)',
        }}>{message}</div>
      )}

      {/* Filters */}
      <form onSubmit={handleSearch} className="card" style={{ marginBottom: '1.5rem', padding: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <input
            className="input"
            placeholder="Search jobs, companies, keywords..."
            value={filters.q}
            onChange={e => setFilters({ ...filters, q: e.target.value })}
            style={{ flex: '2', minWidth: '200px' }}
          />
          <input
            className="input"
            placeholder="Location"
            value={filters.location}
            onChange={e => setFilters({ ...filters, location: e.target.value })}
            style={{ flex: '1', minWidth: '140px' }}
          />
          <select className="input" value={filters.job_type} onChange={e => setFilters({ ...filters, job_type: e.target.value })} style={{ width: '130px' }}>
            {JOB_TYPES.map(t => <option key={t} value={t}>{t || 'All Types'}</option>)}
          </select>
          <select className="input" value={filters.experience_level} onChange={e => setFilters({ ...filters, experience_level: e.target.value })} style={{ width: '140px' }}>
            {EXP_LEVELS.map(l => <option key={l} value={l}>{l || 'All Levels'}</option>)}
          </select>
          <input
            className="input"
            type="number"
            placeholder="Min salary"
            value={filters.salary_min}
            onChange={e => setFilters({ ...filters, salary_min: e.target.value })}
            style={{ width: '120px' }}
          />
          <button className="btn btn-primary" type="submit">Search</button>
        </div>
      </form>

      {/* Job cards */}
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <div className="loading-spinner" />
        </div>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>🔍</div>
          <div style={{ fontSize: '0.9rem' }}>No jobs found. Try adjusting your filters or seed mock data.</div>
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {jobs.map(job => (
              <JobCard key={job.id} job={job} onSave={handleSave} savingId={savingId} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', marginTop: '1.5rem' }}>
              <button className="btn btn-secondary" disabled={page <= 1} onClick={() => fetchJobs(page - 1)} style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}>
                Previous
              </button>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Page {page} of {totalPages}
              </span>
              <button className="btn btn-secondary" disabled={page >= totalPages} onClick={() => fetchJobs(page + 1)} style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}>
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function formatSalary(min, max, currency) {
  if (!min && !max) return ''
  const fmt = (n) => {
    if (!n) return ''
    if (n >= 1000) return `$${Math.round(n / 1000)}k`
    return `$${n}`
  }
  const sym = currency === 'USD' ? '' : ` ${currency}`
  if (min && max) return `${fmt(min)} - ${fmt(max)}${sym}`
  if (min) return `From ${fmt(min)}${sym}`
  return `Up to ${fmt(max)}${sym}`
}

function daysAgo(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 30) return `${days}d ago`
  return `${Math.floor(days / 30)}mo ago`
}

function JobCard({ job, onSave, savingId }) {
  return (
    <div className="card" style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', padding: '1.25rem' }}>
      {/* Logo placeholder */}
      <div style={{
        width: '48px', height: '48px', borderRadius: 'var(--radius-sm)',
        background: 'var(--bg-secondary)', display: 'flex', alignItems: 'center',
        justifyContent: 'center', fontSize: '1.25rem', flexShrink: 0,
        border: '1px solid var(--border)',
      }}>
        {job.company.charAt(0)}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>{job.title}</h3>
          <span style={{ color: 'var(--text-muted)' }}>·</span>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{job.company}</span>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginTop: '0.35rem', color: 'var(--text-muted)', fontSize: '0.8rem', flexWrap: 'wrap' }}>
          {job.location && <span>{job.location}</span>}
          {job.job_type && <span>{job.job_type}</span>}
          {job.experience_level && <span>{job.experience_level}</span>}
          {formatSalary(job.salary_min, job.salary_max, job.salary_currency) && (
            <span style={{ color: 'var(--success)', fontWeight: 500 }}>
              {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
            </span>
          )}
          <span>{daysAgo(job.posted_at)}</span>
        </div>

        {job.description && (
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.825rem', marginTop: '0.5rem', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
            {job.description}
          </div>
        )}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flexShrink: 0 }}>
        <button
          className={`btn ${job.is_saved ? 'btn-secondary' : 'btn-primary'}`}
          onClick={() => onSave(job.id, job.is_saved)}
          disabled={savingId === job.id}
          style={{ padding: '0.4rem 0.75rem', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
        >
          {savingId === job.id ? '...' : job.is_saved ? 'Saved' : 'Save'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => window.open(job.apply_url, '_blank')}
          style={{ padding: '0.4rem 0.75rem', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
        >
          Apply
        </button>
      </div>
    </div>
  )
}
