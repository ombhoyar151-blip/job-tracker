const BASE_URL = '/api'

async function getToken() {
  return localStorage.getItem('access_token')
}

async function request(path, options = {}) {
  const token = await getToken()
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${BASE_URL}${path}`, { headers, ...options })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  if (res.status === 204) return null
  return res.json()
}

async function requestFile(path, file) {
  const token = await getToken()
  const formData = new FormData()
  formData.append('file', file)
  const headers = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${BASE_URL}${path}`, { method: 'POST', headers, body: formData })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Upload failed')
  }
  return res.json()
}

export const api = {
  register(name, email, password) {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    })
  },

  login(email, password) {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  },

  refresh(refreshToken) {
    return request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
  },

  getMe() {
    return request('/auth/me')
  },

  getProfile() {
    return request('/profile')
  },

  updateProfile(data) {
    return request('/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  addSkill(data) {
    return request('/profile/skills', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateSkill(id, data) {
    return request(`/profile/skills/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  deleteSkill(id) {
    return request(`/profile/skills/${id}`, { method: 'DELETE' })
  },

  addEducation(data) {
    return request('/profile/education', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateEducation(id, data) {
    return request(`/profile/education/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  deleteEducation(id) {
    return request(`/profile/education/${id}`, { method: 'DELETE' })
  },

  addWork(data) {
    return request('/profile/work', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateWork(id, data) {
    return request(`/profile/work/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  deleteWork(id) {
    return request(`/profile/work/${id}`, { method: 'DELETE' })
  },

  getResumes() {
    return request('/resumes')
  },

  uploadResume(file) {
    return requestFile('/resumes/upload', file)
  },

  getResume(id) {
    return request(`/resumes/${id}`)
  },

  analyzeResume(id) {
    return request(`/resumes/${id}/analyze`, { method: 'POST' })
  },

  getAnalysis(id) {
    return request(`/resumes/${id}/analysis`)
  },

  seedJobs() {
    return request('/jobs/seed', { method: 'POST' })
  },

  getJobs(params = {}) {
    const qs = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => { if (v) qs.set(k, v) })
    return request(`/jobs?${qs.toString()}`)
  },

  getJob(id) {
    return request(`/jobs/${id}`)
  },

  saveJob(id) {
    return request(`/jobs/${id}/save`, { method: 'POST' })
  },

  unsaveJob(id) {
    return request(`/jobs/${id}/unsave`, { method: 'POST' })
  },

  getRecommendations() {
    return request('/jobs/recommendations')
  },

  getDashboardStats() {
    return request('/dashboard/stats')
  },

  getApplications(status) {
    const qs = status ? `?status=${status}` : ''
    return request(`/applications${qs}`)
  },

  getApplication(id) {
    return request(`/applications/${id}`)
  },

  updateApplication(id, data) {
    return request(`/applications/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  updateApplicationNotes(id, notes) {
    return request(`/applications/${id}/notes`, {
      method: 'PUT',
      body: JSON.stringify({ notes }),
    })
  },

  getInterviews(applicationId) {
    return request(`/interviews/application/${applicationId}`)
  },

  createInterview(data) {
    return request('/interviews', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateInterview(id, data) {
    return request(`/interviews/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  deleteInterview(id) {
    return request(`/interviews/${id}`, { method: 'DELETE' })
  },

  getInterviewPrep(applicationId) {
    return request(`/interviews/prep/${applicationId}`)
  },

  getNotifications() {
    return request('/notifications')
  },

  getUnreadCount() {
    return request('/notifications/unread')
  },

  markNotificationRead(id) {
    return request(`/notifications/${id}/read`, { method: 'PUT' })
  },

  markAllNotificationsRead() {
    return request('/notifications/read-all', { method: 'PUT' })
  },

  deleteNotification(id) {
    return request(`/notifications/${id}`, { method: 'DELETE' })
  },

  getInsights() {
    return request('/insights')
  },
}
