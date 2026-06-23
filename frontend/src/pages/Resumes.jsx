import { useState, useEffect, useCallback, useRef } from 'react'
import { api } from '../services/api'

export default function Resumes() {
  const [resumes, setResumes] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [analyzingId, setAnalyzingId] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const fileInputRef = useRef(null)

  const fetchResumes = useCallback(async () => {
    try {
      const data = await api.getResumes()
      setResumes(data)
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchResumes() }, [fetchResumes])

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setMessage('')
    try {
      await api.uploadResume(file)
      setMessage('Resume uploaded successfully')
      setTimeout(() => setMessage(''), 3000)
      fetchResumes()
    } catch (err) {
      setMessage(err.message)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (!file) return
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowed.includes(file.type)) {
      setMessage('Only PDF and DOCX files are allowed')
      return
    }
    setUploading(true)
    setMessage('')
    api.uploadResume(file)
      .then(() => {
        setMessage('Resume uploaded successfully')
        setTimeout(() => setMessage(''), 3000)
        fetchResumes()
      })
      .catch(err => setMessage(err.message))
      .finally(() => setUploading(false))
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
  }

  const handleAnalyze = async (resumeId) => {
    setAnalyzingId(resumeId)
    setMessage('')
    try {
      const result = await api.analyzeResume(resumeId)
      setAnalysisResult(result)
    } catch (err) {
      setMessage(err.message)
    } finally {
      setAnalyzingId(null)
    }
  }

  const handleViewAnalysis = async (resumeId) => {
    try {
      const result = await api.getAnalysis(resumeId)
      setAnalysisResult(result)
    } catch (err) {
      setMessage(err.message)
    }
  }

  const activeResume = resumes.find(r => r.is_active) || resumes[0]

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>Resumes</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Upload your resume for AI-powered analysis and insights.</p>
      </div>

      {message && (
        <div style={{
          padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem', fontSize: '0.875rem',
          background: message.includes('success') ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
          border: `1px solid ${message.includes('success') ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,
          color: message.includes('success') ? 'var(--success)' : 'var(--error)',
        }}>{message}</div>
      )}

      {/* Upload area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="card"
        style={{
          textAlign: 'center', padding: '3rem 2rem', marginBottom: '1.5rem',
          border: '2px dashed var(--border)', cursor: uploading ? 'wait' : 'pointer',
          transition: 'border-color var(--transition)',
        }}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        {uploading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
            <div className="loading-spinner" />
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Uploading...</span>
          </div>
        ) : (
          <>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📄</div>
            <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Upload Resume</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Drag & drop a PDF or DOCX file here, or click to browse
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.5rem' }}>
              Max file size: 10MB
            </div>
          </>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Resume list */}
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>Uploaded Resumes</h2>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
              <div className="loading-spinner" />
            </div>
          ) : resumes.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem', fontSize: '0.9rem' }}>
              No resumes uploaded yet.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {resumes.map(r => (
                <div key={r.id} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '0.75rem 1rem',
                  background: r.is_active ? 'var(--accent-light)' : 'var(--bg-secondary)',
                  borderRadius: 'var(--radius-sm)',
                  border: r.is_active ? '1px solid var(--accent)' : '1px solid transparent',
                }}>
                  <div>
                    <div style={{ fontWeight: 500, fontSize: '0.9rem' }}>
                      {r.file_name}
                      {r.is_active && <span style={{ color: 'var(--accent)', fontSize: '0.75rem', marginLeft: '0.5rem' }}>Active</span>}
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.15rem' }}>
                      v{r.version} · {new Date(r.uploaded_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
                    {r.has_analysis ? (
                      <button className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                        onClick={() => handleViewAnalysis(r.id)}>
                        View Analysis
                      </button>
                    ) : (
                      <button className="btn btn-primary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                        onClick={() => handleAnalyze(r.id)} disabled={analyzingId === r.id}>
                        {analyzingId === r.id ? 'Analyzing...' : 'Analyze'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Analysis results */}
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>AI Analysis</h2>
          {!analysisResult ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem', fontSize: '0.9rem' }}>
              {activeResume
                ? 'Select a resume and click "Analyze" to get AI-powered insights.'
                : 'Upload a resume to see AI-powered analysis.'}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {/* ATS Score */}
              {analysisResult.ats_score !== null && (
                <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '2.5rem', fontWeight: 700, color: analysisResult.ats_score >= 80 ? 'var(--success)' : analysisResult.ats_score >= 60 ? 'var(--warning)' : 'var(--error)' }}>
                    {analysisResult.ats_score}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>ATS Compatibility Score</div>
                </div>
              )}

              {/* Strengths */}
              <Section title="Strengths" color="var(--success)" items={analysisResult.strengths} />

              {/* Weaknesses */}
              <Section title="Weaknesses" color="var(--warning)" items={analysisResult.weaknesses} />

              {/* Missing Skills */}
              <Section title="Missing Skills" color="var(--error)" items={analysisResult.missing_skills} />

              {/* Suggested Roles */}
              {analysisResult.suggested_roles?.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                    Suggested Roles
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {analysisResult.suggested_roles.map((role, i) => (
                      <span key={i} style={{
                        padding: '0.25rem 0.75rem', background: 'var(--accent-light)',
                        color: 'var(--accent)', borderRadius: '20px', fontSize: '0.8rem',
                      }}>{role}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              <Section title="Recommendations" color="var(--accent)" items={analysisResult.recommendations} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function Section({ title, color, items }) {
  if (!items || items.length === 0) return null
  return (
    <div>
      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
        {title}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
        {items.map((item, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'flex-start', gap: '0.5rem',
            color: 'var(--text-primary)', fontSize: '0.85rem',
          }}>
            <span style={{ color, flexShrink: 0, marginTop: '2px' }}>•</span>
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
