import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// Attach JWT token if present
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('ce_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data) => http.post('/auth/register', data),
  login: (data) => http.post('/auth/login', data),
  me: () => http.get('/auth/me'),
}

// ── Crimes ───────────────────────────────────────────────────────────────────
export const crimesApi = {
  list: (params) => http.get('/crimes', { params }),
  get: (id) => http.get(`/crimes/${id}`),
  create: (data) => http.post('/crimes', data),
  vote: (id, voteType) => http.post(`/crimes/${id}/vote`, { vote_type: voteType }),
  heatmap: (params) => http.get('/crimes/heatmap', { params }),
}

// ── Notes ────────────────────────────────────────────────────────────────────
export const notesApi = {
  list: (crimeId) => http.get(`/crimes/${crimeId}/notes`),
  create: (crimeId, data) => http.post(`/crimes/${crimeId}/notes`, data),
  vote: (crimeId, noteId, voteType) =>
    http.post(`/crimes/${crimeId}/notes/${noteId}/vote`, null, {
      params: { vote_type: voteType },
    }),
}

export default http
