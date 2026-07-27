import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../store/AuthContext'
import { api } from '../services/api'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [notifs, setNotifs] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [showNotifs, setShowNotifs] = useState(false)
  const bellRef = useRef(null)

  useEffect(() => {
    if (!user) return
    const fetchNotifs = async () => {
      try {
        const [unread, all] = await Promise.all([
          api.getUnreadCount(),
          api.getNotifications(),
        ])
        setUnreadCount(unread.unread_count)
        setNotifs(all)
      } catch {}
    }
    fetchNotifs()
    const interval = setInterval(fetchNotifs, 30000)
    return () => clearInterval(interval)
  }, [user])

  useEffect(() => {
    const handleClick = (e) => {
      if (bellRef.current && !bellRef.current.contains(e.target)) {
        setShowNotifs(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const handleMarkAll = async () => {
    try {
      await api.markAllNotificationsRead()
      setNotifs(prev => prev.map(n => ({ ...n, is_read: true })))
      setUnreadCount(0)
    } catch {}
  }

  const handleMarkRead = async (id) => {
    try {
      await api.markNotificationRead(id)
      setNotifs(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch {}
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 2rem', height: '60px',
      background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
        <Link to="/" style={{ fontWeight: 700, fontSize: '1.125rem', color: 'var(--text-primary)' }}>
          JobTracker
        </Link>
        <div style={{ display: 'flex', gap: '1.25rem' }}>
          <Link to="/" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Dashboard</Link>
          <Link to="/profile" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Profile</Link>
          <Link to="/resumes" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Resumes</Link>
          <Link to="/jobs" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Jobs</Link>
          <Link to="/tracker" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Tracker</Link>
          <Link to="/insights" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Insights</Link>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div ref={bellRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'var(--text-secondary)', fontSize: '1.1rem',
              position: 'relative', padding: '0.25rem',
            }}
          >
            {'\u{1F514}'}
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute', top: '-2px', right: '-4px',
                background: '#ef4444', color: '#fff', fontSize: '0.6rem',
                fontWeight: 700, padding: '1px 5px', borderRadius: '999px',
                lineHeight: 1.2,
              }}>
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {showNotifs && (
            <div style={{
              position: 'absolute', top: '100%', right: 0, marginTop: '0.5rem',
              width: '360px', maxHeight: '400px', overflow: 'auto',
              background: 'var(--bg-secondary)', border: '1px solid var(--border)',
              borderRadius: '10px', boxShadow: '0 8px 24px rgba(0,0,0,0.3)',
              zIndex: 100,
            }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.75rem 1rem', borderBottom: '1px solid var(--border)',
              }}>
                <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>Notifications</span>
                {notifs.some(n => !n.is_read) && (
                  <button onClick={handleMarkAll}
                    style={{ background: 'none', border: 'none', color: 'var(--accent)', fontSize: '0.75rem', cursor: 'pointer' }}>
                    Mark all read
                  </button>
                )}
              </div>
              {notifs.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  No notifications yet.
                </div>
              ) : (
                notifs.map(n => (
                  <div key={n.id}
                    onClick={() => handleMarkRead(n.id)}
                    style={{
                      padding: '0.75rem 1rem', cursor: 'pointer',
                      borderBottom: '1px solid var(--border)',
                      background: n.is_read ? 'transparent' : 'rgba(99,102,241,0.08)',
                    }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span style={{ fontWeight: n.is_read ? 400 : 600, fontSize: '0.8rem', flex: 1 }}>
                        {n.title}
                      </span>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.65rem', whiteSpace: 'nowrap', marginLeft: '0.5rem' }}>
                        {new Date(n.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginTop: '0.125rem' }}>
                      {n.message}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{user?.name}</span>
        <button className="btn btn-secondary" onClick={handleLogout} style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}>
          Logout
        </button>
      </div>
    </nav>
  )
}
