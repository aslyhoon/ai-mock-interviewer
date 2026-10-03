// Thin wrappers over the FastAPI backend (proxied via vite dev server).
const j = (r) => {
  if (!r.ok) return r.text().then((t) => { throw new Error(t || `HTTP ${r.status}`) })
  return r.json()
}

export const api = {
  health: () => fetch('/api/health').then(j),
  createSession: (body) =>
    fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then(j),
  nextQuestion: (id) => fetch(`/api/sessions/${id}/next-question`).then(j),
  answer: (id, body) =>
    fetch(`/api/sessions/${id}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then(j),
  finish: (id) => fetch(`/api/sessions/${id}/finish`, { method: 'POST' }).then(j),
  report: (id) => fetch(`/api/sessions/${id}/report`).then(j),
  execute: (body) =>
    fetch('/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then(j),
}
