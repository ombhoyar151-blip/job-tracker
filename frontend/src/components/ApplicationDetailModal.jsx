import { useState, useEffect } from 'react'
import { api } from '../services/api'

const STATUS_OPTIONS = [
  'wishlist', 'applied', 'under_review', 'interview_scheduled',
  'offer_received', 'rejected', 'accepted', 'withdrawn',
]

const STATUS_LABELS = {
  wishlist: 'Wishlist', applied: 'Applied', under_review: 'Under Review',
  interview_scheduled: 'Interview Scheduled', offer_received: 'Offer Received',
  rejected: 'Rejected', accepted: 'Accepted', withdrawn: 'Withdrawn',
}

const STATUS_COLORS = {
  wishlist: 'var(--accent)', applied: '#3b82f6', under_review: '#f59e0b',
  interview_scheduled: '#8b5cf6', offer_received: '#10b981',
  rejected: '#ef4444', accepted: '#059669', withdrawn: '#6b7280',
}

const ROUND_LABELS = {
  phone: 'Phone', technical: 'Technical', behavioral: 'Behavioral',
  onsite: 'Onsite', panel: 'Panel', take_home: 'Take Home', final: 'Final',
}

const OUTCOME_LABELS = {
  pending: 'Pending', passed: 'Passed', failed: 'Failed', cancelled: 'Cancelled',
}

const TAB = { DETAIL: 'detail', INTERVIEWS: 'interviews', PREP: 'prep' }

export default function ApplicationDetailModal({ applicationId, onClose, onUpdate }) {
  const [app, setApp] = useState(null)
  const [loading, setLoading] = useState(true)
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [tab, setTab] = useState(TAB.DETAIL)

  const [interviews, setInterviews] = useState([])
  const [prepData, setPrepData] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    scheduled_at: '', round_type: 'phone', interview_format: '',
    location_or_link: '', interviewer_name: '', interviewer_role: '', notes: '',
  })
  const [editingId, setEditingId] = useState(null)

  useEffect(() => {
    if (!applicationId) return
    setLoading(true)
    api.getApplication(applicationId)
      .then(data => {
        setApp(data)
        setNotes(data.notes || '')
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [applicationId])

  const loadInterviews = async () => {
    try {
      const data = await api.getInterviews(applicationId)
      setInterviews(data)
    } catch {}
  }

  const handleTabChange = async (newTab) => {
    setTab(newTab)
    if (newTab === TAB.INTERVIEWS && interviews.length === 0) {
      await loadInterviews()
    }
    if (newTab === TAB.PREP && !prepData) {
      try {
        const data = await api.getInterviewPrep(applicationId)
        setPrepData(data)
      } catch {}
    }
  }

  const handleStatusChange = async (newStatus) => {
    if (!app || newStatus === app.status) return
    setSaving(true)
    try {
      const updated = await api.updateApplication(app.id, { status: newStatus })
      setApp(updated)
      if (onUpdate) onUpdate()
    } catch {}
    finally { setSaving(false) }
  }

  const handleSaveNotes = async () => {
    setSaving(true)
    try {
      await api.updateApplicationNotes(app.id, notes)
      if (onUpdate) onUpdate()
    } catch {}
    finally { setSaving(false) }
  }

  const handleSubmitInterview = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = { ...form, application_id: applicationId }
      if (editingId) {
        await api.updateInterview(editingId, payload)
      } else {
        await api.createInterview(payload)
      }
      setShowForm(false)
      setEditingId(null)
      setForm({ scheduled_at: '', round_type: 'phone', interview_format: '', location_or_link: '', interviewer_name: '', interviewer_role: '', notes: '' })
      await loadInterviews()
    } catch {}
    finally { setSaving(false) }
  }

  const handleEditInterview = (iv) => {
    setForm({
      scheduled_at: iv.scheduled_at ? iv.scheduled_at.slice(0, 16) : '',
      round_type: iv.round_type,
      interview_format: iv.interview_format || '',
      location_or_link: iv.location_or_link || '',
      interviewer_name: iv.interviewer_name || '',
      interviewer_role: iv.interviewer_role || '',
      notes: iv.notes || '',
    })
    setEditingId(iv.id)
    setShowForm(true)
  }

  const handleDeleteInterview = async (id) => {
    try {
      await api.deleteInterview(id)
      await loadInterviews()
    } catch {}
  }

  if (!applicationId) return null

  const tabStyle = (t) => ({
    padding: '0.5rem 1rem', borderRadius: '6px', border: 'none',
    cursor: 'pointer', fontSize: '0.8rem', fontWeight: 500,
    background: tab === t ? 'var(--accent)' : 'var(--bg-secondary)',
    color: tab === t ? '#fff' : 'var(--text-secondary)',
  })

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 1000,
      background: 'rgba(0,0,0,0.6)', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      padding: '1rem',
    }} onClick={onClose}>
      <div className="card" style={{
        maxWidth: '700px', width: '100%', maxHeight: '90vh',
        overflow: 'auto', position: 'relative',
      }} onClick={e => e.stopPropagation()}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading...</div>
        ) : app ? (
          <>
            <button onClick={onClose} style={{
              position: 'absolute', top: '1rem', right: '1rem',
              background: 'none', border: 'none', color: 'var(--text-secondary)',
              fontSize: '1.25rem', cursor: 'pointer', lineHeight: 1,
            }}>&times;</button>

            <div style={{ marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>{app.job.title}</h2>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                {app.job.company} &middot; {app.job.location || 'Remote'}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
              {[TAB.DETAIL, TAB.INTERVIEWS, TAB.PREP].map(t => (
                <button key={t} style={tabStyle(t)} onClick={() => handleTabChange(t)}>
                  {t === TAB.DETAIL ? 'Details' : t === TAB.INTERVIEWS ? `Interviews (${interviews.length})` : 'Prep'}
                </button>
              ))}
            </div>

            {tab === TAB.DETAIL && (
              <>
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Status</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
                    {STATUS_OPTIONS.map(s => (
                      <button key={s} onClick={() => handleStatusChange(s)}
                        disabled={saving || s === app.status}
                        style={{
                          padding: '0.35rem 0.65rem', borderRadius: '6px', border: '1px solid var(--border)',
                          fontSize: '0.75rem', cursor: 'pointer',
                          background: s === app.status ? STATUS_COLORS[s] : 'var(--bg-secondary)',
                          color: s === app.status ? '#fff' : 'var(--text-secondary)',
                          fontWeight: s === app.status ? 600 : 400,
                        }}
                      >{STATUS_LABELS[s]}</button>
                    ))}
                  </div>
                </div>

                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Notes</label>
                  <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={4}
                    style={{
                      width: '100%', padding: '0.75rem', borderRadius: '8px',
                      border: '1px solid var(--border)', background: 'var(--bg-secondary)',
                      color: 'var(--text-primary)', fontSize: '0.875rem', resize: 'vertical',
                      fontFamily: 'inherit',
                    }}
                  />
                  <button onClick={handleSaveNotes} disabled={saving}
                    className="btn btn-primary" style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}
                  >{saving ? 'Saving...' : 'Save Notes'}</button>
                </div>

                {app.history && app.history.length > 0 && (
                  <div>
                    <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Activity History</label>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {app.history.map(h => (
                        <div key={h.id} style={{
                          display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
                          padding: '0.5rem 0', borderBottom: '1px solid var(--border)',
                        }}>
                          <div style={{
                            width: '8px', height: '8px', borderRadius: '50%',
                            background: STATUS_COLORS[h.new_status] || 'var(--accent)',
                            marginTop: '0.375rem', flexShrink: 0,
                          }} />
                          <div style={{ flex: 1, fontSize: '0.8rem' }}>
                            <span style={{ fontWeight: 600 }}>
                              {h.old_status ? `${STATUS_LABELS[h.old_status] || h.old_status} \u2192 ` : ''}
                              {STATUS_LABELS[h.new_status] || h.new_status}
                            </span>
                            <span style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                              {new Date(h.changed_at).toLocaleDateString()}
                            </span>
                            {h.notes && <div style={{ color: 'var(--text-secondary)', marginTop: '0.125rem' }}>{h.notes}</div>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {tab === TAB.INTERVIEWS && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Scheduled Interviews</label>
                  <button className="btn btn-primary" onClick={() => { setShowForm(true); setEditingId(null); setForm({ scheduled_at: '', round_type: 'phone', interview_format: '', location_or_link: '', interviewer_name: '', interviewer_role: '', notes: '' }) }}
                    style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}>
                    + Add Interview
                  </button>
                </div>

                {showForm && (
                  <form onSubmit={handleSubmitInterview} style={{
                    background: 'var(--bg-secondary)', padding: '1rem', borderRadius: '8px',
                    marginBottom: '1rem',
                  }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
                      <div>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>Date & Time</label>
                        <input type="datetime-local" value={form.scheduled_at}
                          onChange={e => setForm({ ...form, scheduled_at: e.target.value })}
                          style={{ width: '100%', padding: '0.4rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)', fontSize: '0.8rem' }} />
                      </div>
                      <div>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>Round Type</label>
                        <select value={form.round_type} onChange={e => setForm({ ...form, round_type: e.target.value })}
                          style={{ width: '100%', padding: '0.4rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)', fontSize: '0.8rem' }}>
                          {Object.entries(ROUND_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                        </select>
                      </div>
                      <div>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>Format</label>
                        <input type="text" value={form.interview_format} placeholder="Video, In-person, Phone..."
                          onChange={e => setForm({ ...form, interview_format: e.target.value })}
                          style={{ width: '100%', padding: '0.4rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)', fontSize: '0.8rem' }} />
                      </div>
                      <div>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>Location / Link</label>
                        <input type="text" value={form.location_or_link} placeholder="Zoom link or address"
                          onChange={e => setForm({ ...form, location_or_link: e.target.value })}
                          style={{ width: '100%', padding: '0.4rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)', fontSize: '0.8rem' }} />
                      </div>
                      <div>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>Interviewer Name</label>
                        <input type="text" value={form.interviewer_name}
                          onChange={e => setForm({ ...form, interviewer_name: e.target.value })}
                          style={{ width: '100%', padding: '0.4rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)', fontSize: '0.8rem' }} />
                      </div>
                      <div>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>Interviewer Role</label>
                        <input type="text" value={form.interviewer_role}
                          onChange={e => setForm({ ...form, interviewer_role: e.target.value })}
                          style={{ width: '100%', padding: '0.4rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)', fontSize: '0.8rem' }} />
                      </div>
                    </div>
                    <div style={{ marginBottom: '0.75rem' }}>
                      <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>Notes</label>
                      <textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} rows={2}
                        style={{ width: '100%', padding: '0.4rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-primary)', color: 'var(--text-primary)', fontSize: '0.8rem', fontFamily: 'inherit', resize: 'vertical' }} />
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button type="submit" disabled={saving} className="btn btn-primary" style={{ fontSize: '0.8rem' }}>
                        {saving ? 'Saving...' : editingId ? 'Update' : 'Add Interview'}
                      </button>
                      <button type="button" onClick={() => { setShowForm(false); setEditingId(null) }}
                        className="btn btn-secondary" style={{ fontSize: '0.8rem' }}>Cancel</button>
                    </div>
                  </form>
                )}

                {interviews.length === 0 && !showForm ? (
                  <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    No interviews scheduled yet.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {interviews.map(iv => (
                      <div key={iv.id} style={{
                        padding: '0.75rem', borderRadius: '8px',
                        border: '1px solid var(--border)', background: 'var(--bg-secondary)',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
                          <div>
                            <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{ROUND_LABELS[iv.round_type] || iv.round_type}</span>
                            {iv.scheduled_at && (
                              <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginLeft: '0.5rem' }}>
                                {new Date(iv.scheduled_at).toLocaleString()}
                              </span>
                            )}
                          </div>
                          <span style={{
                            fontSize: '0.7rem', padding: '0.125rem 0.5rem', borderRadius: '999px',
                            background: iv.outcome === 'passed' ? 'rgba(16,185,129,0.15)' : iv.outcome === 'failed' ? 'rgba(239,68,68,0.15)' : 'rgba(107,114,128,0.15)',
                            color: iv.outcome === 'passed' ? '#10b981' : iv.outcome === 'failed' ? '#ef4444' : '#6b7280',
                          }}>
                            {OUTCOME_LABELS[iv.outcome]}
                          </span>
                        </div>
                        {iv.interview_format && <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{iv.interview_format}{iv.location_or_link ? ` \u00b7 ${iv.location_or_link}` : ''}</div>}
                        {(iv.interviewer_name || iv.interviewer_role) && (
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            {[iv.interviewer_name, iv.interviewer_role].filter(Boolean).join(' - ')}
                          </div>
                        )}
                        {iv.notes && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{iv.notes}</div>}
                        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                          <button onClick={() => handleEditInterview(iv)}
                            style={{ background: 'none', border: 'none', color: 'var(--accent)', fontSize: '0.7rem', cursor: 'pointer', padding: 0 }}>Edit</button>
                          <button onClick={() => handleDeleteInterview(iv.id)}
                            style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '0.7rem', cursor: 'pointer', padding: 0 }}>Delete</button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {tab === TAB.PREP && (
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                  Practice Questions for {prepData?.role || app.job.title}
                </label>
                {!prepData ? (
                  <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Generating questions...</div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {prepData.questions.map((q, i) => (
                      <div key={i} style={{
                        padding: '0.75rem', borderRadius: '8px',
                        border: '1px solid var(--border)', background: 'var(--bg-secondary)',
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                          <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>Q{i + 1}</span>
                          <span style={{
                            fontSize: '0.7rem', padding: '0.125rem 0.5rem', borderRadius: '999px',
                            background: q.type === 'technical' ? 'rgba(59,130,246,0.15)' : q.type === 'behavioral' ? 'rgba(139,92,246,0.15)' : 'rgba(245,158,11,0.15)',
                            color: q.type === 'technical' ? '#3b82f6' : q.type === 'behavioral' ? '#8b5cf6' : '#f59e0b',
                          }}>
                            {q.type}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.8rem', marginBottom: '0.25rem' }}>{q.question}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          <span style={{ color: 'var(--text-secondary)' }}>Focus: {q.focus_area}</span>
                        </div>
                        <details style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>
                          <summary style={{ color: 'var(--accent)', cursor: 'pointer' }}>Suggested Answer</summary>
                          <div style={{ color: 'var(--text-secondary)', marginTop: '0.25rem', lineHeight: 1.5 }}>{q.suggested_answer}</div>
                        </details>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Application not found.</div>
        )}
      </div>
    </div>
  )
}
