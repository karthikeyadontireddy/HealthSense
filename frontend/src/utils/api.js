const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export async function apiRequest(path, token, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || response.statusText || 'Request failed')
  }

  return response.json()
}
