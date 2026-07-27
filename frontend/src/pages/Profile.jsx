import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'

const JOB_TYPES = ['', 'Remote', 'On-site', 'Hybrid']
const PROFICIENCY_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert']

function calculateCompleteness(profile) {
  let score = 0
  const fields = ['name', 'location', 'desired_role', 'years_of_experience', 'preferred_job_type', 'bio']
  fields.forEach(f => { if (profile[f]) score += 10 })
  if (profile.skills?.length > 0) score += 15
  if (profile.education?.length > 0) score += 15
  if (profile.work_experiences?.length > 0) score += 15
  return Math.min(score, 100)
}

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const [form, setForm] = useState({
    name: '', location: '', desired_role: '', years_of_experience: '',
    preferred_job_type: '', bio: '',
  })

  // New skill form
  const [newSkill, setNewSkill] = useState({ skill_name: '', proficiency_level: '' })
  const [showSkillForm, setShowSkillForm] = useState(false)

  // New education form
  const emptyEdu = { institution: '', degree: '', field_of_study: '', start_date: '', end_date: '', is_current: false, grade: '', description: '' }
  const [newEdu, setNewEdu] = useState({ ...emptyEdu })
  const [showEduForm, setShowEduForm] = useState(false)
  const [editEduId, setEditEduId] = useState(null)

  // New work form
  const emptyWork = { company: '', role: '', location: '', start_date: '', end_date: '', is_current: false, description: '' }
  const [newWork, setNewWork] = useState({ ...emptyWork })
  const [showWorkForm, setShowWorkForm] = useState(false)
  const [editWorkId, setEditWorkId] = useState(null)

  const fetchProfile = useCallback(async () => {
    try {
      const data = await api.getProfile()
      setProfile(data)
      setForm({
        name: data.name || '',
        location: data.location || '',
        desired_role: data.desired_role || '',
        years_of_experience: data.years_of_experience || '',
        preferred_job_type: data.preferred_job_type || '',
        bio: data.bio || '',
      })
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchProfile() }, [fetchProfile])

  const handleSaveProfile = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const data = await api.updateProfile({
        ...form,
        years_of_experience: form.years_of_experience ? Number(form.years_of_experience) : null,
      })
      setProfile(data)
      setMessage('Profile saved')
      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      setMessage(err.message)
    } finally {
      setSaving(false)
    }
  }

  // Skills
  const handleAddSkill = async (e) => {
    e.preventDefault()
    if (!newSkill.skill_name) return
    try {
      await api.addSkill(newSkill)
      setNewSkill({ skill_name: '', proficiency_level: '' })
      setShowSkillForm(false)
      fetchProfile()
    } catch (err) { setMessage(err.message) }
  }

  const handleDeleteSkill = async (id) => {
    try {
      await api.deleteSkill(id)
      fetchProfile()
    } catch (err) { setMessage(err.message) }
  }

  // Education
  const handleAddEducation = async (e) => {
    e.preventDefault()
    try {
      if (editEduId) {
        await api.updateEducation(editEduId, newEdu)
      } else {
        await api.addEducation(newEdu)
      }
      setNewEdu({ ...emptyEdu })
      setShowEduForm(false)
      setEditEduId(null)
      fetchProfile()
    } catch (err) { setMessage(err.message) }
  }

  const handleEditEducation = (edu) => {
    setNewEdu({
      institution: edu.institution || '',
      degree: edu.degree || '',
      field_of_study: edu.field_of_study || '',
      start_date: edu.start_date || '',
      end_date: edu.end_date || '',
      is_current: edu.is_current || false,
      grade: edu.grade || '',
      description: edu.description || '',
    })
    setEditEduId(edu.id)
    setShowEduForm(true)
  }

  const handleDeleteEducation = async (id) => {
    try {
      await api.deleteEducation(id)
      fetchProfile()
    } catch (err) { setMessage(err.message) }
  }

  // Work
  const handleAddWork = async (e) => {
    e.preventDefault()
    try {
      if (editWorkId) {
        await api.updateWork(editWorkId, newWork)
      } else {
        await api.addWork(newWork)
      }
      setNewWork({ ...emptyWork })
      setShowWorkForm(false)
      setEditWorkId(null)
      fetchProfile()
    } catch (err) { setMessage(err.message) }
  }

  const handleEditWork = (work) => {
    setNewWork({
      company: work.company || '',
      role: work.role || '',
      location: work.location || '',
      start_date: work.start_date || '',
      end_date: work.end_date || '',
      is_current: work.is_current || false,
      description: work.description || '',
    })
    setEditWorkId(work.id)
    setShowWorkForm(true)
  }

  const handleDeleteWork = async (id) => {
    try {
      await api.deleteWork(id)
      fetchProfile()
    } catch (err) { setMessage(err.message) }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
        <div className="loading-spinner" />
      </div>
    )
  }

  const completeness = profile ? calculateCompleteness(profile) : 0

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>Profile</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Manage your personal information, skills, and experience.</p>
      </div>

      {message && (
        <div style={{
          padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem',
          background: message === 'Profile saved' ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
          border: `1px solid ${message === 'Profile saved' ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,
          color: message === 'Profile saved' ? 'var(--success)' : 'var(--error)',
          fontSize: '0.875rem',
        }}>{message}</div>
      )}

      {/* Profile completeness */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Profile Completeness</span>
          <span style={{ color: completeness === 100 ? 'var(--success)' : 'var(--warning)', fontWeight: 600 }}>{completeness}%</span>
        </div>
        <div style={{ height: '8px', background: 'var(--bg-secondary)', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{
            height: '100%', borderRadius: '4px', transition: 'width 0.4s ease',
            background: completeness === 100 ? 'var(--success)' : completeness > 50 ? 'var(--warning)' : 'var(--accent)',
            width: `${completeness}%`,
          }} />
        </div>
      </div>

      <div style={{ display: 'grid', gap: '1.5rem' }}>
        {/* Basic Info */}
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '1.25rem' }}>Basic Information</h2>
          <form onSubmit={handleSaveProfile}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="label">Full Name</label>
                <input className="input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="label">Location</label>
                <input className="input" value={form.location} onChange={e => setForm({ ...form, location: e.target.value })} placeholder="City, Country" />
              </div>
              <div className="form-group">
                <label className="label">Desired Role</label>
                <input className="input" value={form.desired_role} onChange={e => setForm({ ...form, desired_role: e.target.value })} placeholder="e.g. Frontend Developer" />
              </div>
              <div className="form-group">
                <label className="label">Years of Experience</label>
                <input className="input" type="number" min="0" value={form.years_of_experience} onChange={e => setForm({ ...form, years_of_experience: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="label">Preferred Job Type</label>
                <select className="input" value={form.preferred_job_type} onChange={e => setForm({ ...form, preferred_job_type: e.target.value })}>
                  {JOB_TYPES.map(t => <option key={t} value={t}>{t || 'Select...'}</option>)}
                </select>
              </div>
            </div>
            <div className="form-group" style={{ marginTop: '0.5rem' }}>
              <label className="label">Bio</label>
              <textarea className="input" rows="3" value={form.bio} onChange={e => setForm({ ...form, bio: e.target.value })} placeholder="Brief summary about yourself" style={{ resize: 'vertical' }} />
            </div>
            <button className="btn btn-primary" type="submit" disabled={saving} style={{ marginTop: '0.5rem' }}>
              {saving ? <span className="loading-spinner" style={{ width: '1.25rem', height: '1.25rem', borderWidth: '2px' }} /> : 'Save Changes'}
            </button>
          </form>
        </div>

        {/* Skills */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.125rem' }}>Skills</h2>
            <button className="btn btn-secondary" onClick={() => { setShowSkillForm(!showSkillForm); setNewSkill({ skill_name: '', proficiency_level: '' }) }}>
              {showSkillForm ? 'Cancel' : '+ Add Skill'}
            </button>
          </div>

          {showSkillForm && (
            <form onSubmit={handleAddSkill} style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
              <input className="input" placeholder="Skill name" value={newSkill.skill_name} onChange={e => setNewSkill({ ...newSkill, skill_name: e.target.value })} required style={{ flex: 1 }} />
              <select className="input" value={newSkill.proficiency_level} onChange={e => setNewSkill({ ...newSkill, proficiency_level: e.target.value })} style={{ width: '140px' }}>
                <option value="">Level</option>
                {PROFICIENCY_LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
              <button className="btn btn-primary" type="submit">Add</button>
            </form>
          )}

          {profile?.skills?.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '1.5rem', fontSize: '0.9rem' }}>
              No skills added yet. Skills will also be auto-detected from resume analysis.
            </div>
          ) : (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {profile?.skills?.map(skill => (
                <div key={skill.id} style={{
                  display: 'flex', alignItems: 'center', gap: '0.5rem',
                  padding: '0.35rem 0.75rem', background: 'var(--accent-light)',
                  borderRadius: '20px', fontSize: '0.85rem',
                }}>
                  <span>{skill.skill_name}</span>
                  {skill.proficiency_level && (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({skill.proficiency_level})</span>
                  )}
                  <button onClick={() => handleDeleteSkill(skill.id)} style={{
                    background: 'none', border: 'none', color: 'var(--text-muted)',
                    cursor: 'pointer', fontSize: '1rem', lineHeight: 1, padding: '0 0.15rem',
                  }} title="Remove">&times;</button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Education */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.125rem' }}>Education</h2>
            <button className="btn btn-secondary" onClick={() => { setShowEduForm(!showEduForm); setEditEduId(null); setNewEdu({ ...emptyEdu }) }}>
              {showEduForm ? 'Cancel' : '+ Add Education'}
            </button>
          </div>

          {showEduForm && (
            <form onSubmit={handleAddEducation} style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', marginBottom: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">Institution</label>
                  <input className="input" value={newEdu.institution} onChange={e => setNewEdu({ ...newEdu, institution: e.target.value })} required />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">Degree</label>
                  <input className="input" value={newEdu.degree} onChange={e => setNewEdu({ ...newEdu, degree: e.target.value })} required />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">Field of Study</label>
                  <input className="input" value={newEdu.field_of_study} onChange={e => setNewEdu({ ...newEdu, field_of_study: e.target.value })} />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">Grade</label>
                  <input className="input" value={newEdu.grade} onChange={e => setNewEdu({ ...newEdu, grade: e.target.value })} />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">Start Date</label>
                  <input className="input" type="date" value={newEdu.start_date} onChange={e => setNewEdu({ ...newEdu, start_date: e.target.value })} />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">End Date</label>
                  <input className="input" type="date" value={newEdu.end_date} onChange={e => setNewEdu({ ...newEdu, end_date: e.target.value })} disabled={newEdu.is_current} />
                </div>
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: '0.75rem 0', color: 'var(--text-secondary)', fontSize: '0.875rem', cursor: 'pointer' }}>
                <input type="checkbox" checked={newEdu.is_current} onChange={e => setNewEdu({ ...newEdu, is_current: e.target.checked })} />
                Currently studying here
              </label>
              <button className="btn btn-primary" type="submit">{editEduId ? 'Update' : 'Add'}</button>
            </form>
          )}

          {profile?.education?.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '1.5rem', fontSize: '0.9rem' }}>
              No education history added.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {profile?.education?.map(edu => (
                <div key={edu.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', padding: '0.75rem 1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{edu.degree} at {edu.institution}</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.15rem' }}>
                      {edu.field_of_study && `${edu.field_of_study} · `}
                      {edu.start_date && `${edu.start_date.split('-')[0]}`}
                      {edu.is_current ? ' - Present' : edu.end_date ? ` - ${edu.end_date.split('-')[0]}` : ''}
                      {edu.grade && ` · ${edu.grade}`}
                    </div>
                    {edu.description && <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.25rem' }}>{edu.description}</div>}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
                    <button className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleEditEducation(edu)}>Edit</button>
                    <button className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', color: 'var(--error)' }} onClick={() => handleDeleteEducation(edu.id)}>Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Work Experience */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.125rem' }}>Work Experience</h2>
            <button className="btn btn-secondary" onClick={() => { setShowWorkForm(!showWorkForm); setEditWorkId(null); setNewWork({ ...emptyWork }) }}>
              {showWorkForm ? 'Cancel' : '+ Add Experience'}
            </button>
          </div>

          {showWorkForm && (
            <form onSubmit={handleAddWork} style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', marginBottom: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">Company</label>
                  <input className="input" value={newWork.company} onChange={e => setNewWork({ ...newWork, company: e.target.value })} required />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">Role</label>
                  <input className="input" value={newWork.role} onChange={e => setNewWork({ ...newWork, role: e.target.value })} required />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">Location</label>
                  <input className="input" value={newWork.location} onChange={e => setNewWork({ ...newWork, location: e.target.value })} />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">Start Date</label>
                  <input className="input" type="date" value={newWork.start_date} onChange={e => setNewWork({ ...newWork, start_date: e.target.value })} />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="label">End Date</label>
                  <input className="input" type="date" value={newWork.end_date} onChange={e => setNewWork({ ...newWork, end_date: e.target.value })} disabled={newWork.is_current} />
                </div>
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: '0.75rem 0', color: 'var(--text-secondary)', fontSize: '0.875rem', cursor: 'pointer' }}>
                <input type="checkbox" checked={newWork.is_current} onChange={e => setNewWork({ ...newWork, is_current: e.target.checked })} />
                I currently work here
              </label>
              <div className="form-group" style={{ marginBottom: '0.75rem' }}>
                <label className="label">Description</label>
                <textarea className="input" rows="2" value={newWork.description} onChange={e => setNewWork({ ...newWork, description: e.target.value })} style={{ resize: 'vertical' }} />
              </div>
              <button className="btn btn-primary" type="submit">{editWorkId ? 'Update' : 'Add'}</button>
            </form>
          )}

          {profile?.work_experiences?.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '1.5rem', fontSize: '0.9rem' }}>
              No work experience added.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {profile?.work_experiences?.map(work => (
                <div key={work.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', padding: '0.75rem 1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{work.role} at {work.company}</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.15rem' }}>
                      {work.location && `${work.location} · `}
                      {work.start_date && `${work.start_date.split('-')[0]}`}
                      {work.is_current ? ' - Present' : work.end_date ? ` - ${work.end_date.split('-')[0]}` : ''}
                    </div>
                    {work.description && <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.25rem' }}>{work.description}</div>}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
                    <button className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleEditWork(work)}>Edit</button>
                    <button className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', color: 'var(--error)' }} onClick={() => handleDeleteWork(work.id)}>Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
