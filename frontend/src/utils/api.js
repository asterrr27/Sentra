import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

let onUnauthorized = null

export function setOnUnauthorized(fn) {
  onUnauthorized = fn
}

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('sentra_token')
      delete api.defaults.headers.common['Authorization']
      if (onUnauthorized) {
        onUnauthorized()
      } else {
        window.location.href = '/'
      }
    }
    return Promise.reject(err)
  },
)

export function createScan(data) {
  return api.post('/scans', data).then(r => r.data)
}

export function getScanStatus(id) {
  return api.get(`/scans/${id}`).then(r => r.data)
}

export function getScanResults(id) {
  return api.get(`/scans/${id}/results`).then(r => r.data)
}

export function listScans() {
  return api.get('/scans').then(r => r.data)
}

export function exportScan(id) {
  return api.get(`/scans/${id}/export`, { responseType: 'blob' }).then(r => r.data)
}

export function exportScanPdf(id) {
  return api.get(`/scans/${id}/export/pdf`, { responseType: 'blob' }).then(r => r.data)
}

export function exportScanCsv(id) {
  return api.get(`/scans/${id}/export/csv`, { responseType: 'blob' }).then(r => r.data)
}

export function cancelScan(id) {
  return api.post(`/scans/${id}/cancel`).then(r => r.data)
}

export function getAllPayloads() {
  return api.get('/payloads').then(r => r.data)
}

export function resetUserPassword(userId, newPassword) {
  return api.post(`/admin/users/${userId}/reset-password`, { new_password: newPassword }).then(r => r.data)
}

export default api
