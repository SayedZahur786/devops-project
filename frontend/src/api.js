async function request(path, options = {}) {
  const resp = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (!resp.ok) {
    throw new Error(`API ${resp.status}: ${await resp.text()}`)
  }
  if (resp.status === 204) return null
  return resp.json()
}

export const api = {
  listProjects: (status) =>
    request(`/api/projects${status ? `?status=${encodeURIComponent(status)}` : ''}`),
  stats: () => request('/api/projects/stats'),
  createProject: (data) =>
    request('/api/projects', { method: 'POST', body: JSON.stringify(data) }),
  updateProject: (id, data) =>
    request(`/api/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProject: (id) => request(`/api/projects/${id}`, { method: 'DELETE' })
}
