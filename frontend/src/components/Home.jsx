import { useState } from 'react'
import { api } from '../api.js'

const MODES = [
  { id: 'hr', title: 'HR Round', desc: 'Behavioral questions — tell me about yourself, strengths, teamwork.', icon: '💼' },
  { id: 'dsa', title: 'DSA Round', desc: 'Coding problems with live code execution and test cases.', icon: '💻' },
  { id: 'cs', title: 'CS Fundamentals', desc: 'OS, DBMS and Computer Networks concepts.', icon: '🧠' },
]

const TOPICS = [
  { id: 'arrays', label: 'Arrays' },
  { id: 'strings', label: 'Strings' },
  { id: 'linkedlist', label: 'Linked Lists' },
  { id: 'trees', label: 'Trees' },
  { id: 'dp', label: 'Dynamic Programming' },
]

export default function Home({ onStart }) {
  const [mode, setMode] = useState('hr')
  const [difficulty, setDifficulty] = useState('medium')
  const [topic, setTopic] = useState('arrays')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const start = async () => {
    setLoading(true)
    setError('')
    try {
      const s = await api.createSession({
        mode,
        difficulty,
        topic: mode === 'dsa' ? topic : 'general',
      })
      onStart(s)
    } catch (e) {
      setError('Could not reach the backend. Is it running on port 8000?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="home">
      <h1>Practice interviews with an AI interviewer</h1>
      <p className="sub">Voice-based questions, live code execution, rubric scoring.</p>

      <div className="cards">
        {MODES.map((m) => (
          <button
            key={m.id}
            className={`card ${mode === m.id ? 'active' : ''}`}
            onClick={() => setMode(m.id)}
          >
            <span className="card-icon">{m.icon}</span>
            <strong>{m.title}</strong>
            <span className="card-desc">{m.desc}</span>
          </button>
        ))}
      </div>

      <div className="controls">
        <label>
          Difficulty
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </label>
        {mode === 'dsa' && (
          <label>
            Topic
            <select value={topic} onChange={(e) => setTopic(e.target.value)}>
              {TOPICS.map((t) => (
                <option key={t.id} value={t.id}>{t.label}</option>
              ))}
            </select>
          </label>
        )}
      </div>

      {error && <div className="error">{error}</div>}
      <button className="primary big" onClick={start} disabled={loading}>
        {loading ? 'Starting…' : 'Start Interview 🎙️'}
      </button>
    </div>
  )
}
