import { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Report({ sessionId, onAgain }) {
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.report(sessionId).then(setReport).catch((e) => setError(e.message))
  }, [sessionId])

  if (error) return <div className="error">{error}</div>
  if (!report) return <div className="loading">Building your report…</div>

  const { session, aggregate, overall, weak_topics, turns } = report

  return (
    <div className="report">
      <h1>Interview Report</h1>
      <p className="sub">{session.mode.toUpperCase()} · {session.difficulty} · {turns.length} questions</p>

      <div className="overall">
        <div className="big-score">{overall}<small>/10</small></div>
        <div className="agg">
          {Object.entries(aggregate).map(([k, v]) => (
            <div key={k} className="score">
              <span>{k}</span>
              <div className="bar"><div className="fill" style={{ width: `${v * 10}%` }} /></div>
              <b>{v}/10</b>
            </div>
          ))}
        </div>
      </div>

      {weak_topics.length > 0 && (
        <div className="weak">
          <h3>🎯 Topics to work on</h3>
          <ul>{weak_topics.map((t) => <li key={t}>{t}</li>)}</ul>
        </div>
      )}

      <h2>Per-question breakdown</h2>
      {turns.map((t, i) => (
        <div key={t.id} className="turn">
          <h3>Q{i + 1}. {t.question.split('\n')[0]}</h3>
          <div className="scores small">
            {Object.entries(t.scores || {}).map(([k, v]) => (
              <span key={k} className="chip">{k}: <b>{v}</b></span>
            ))}
          </div>
          {t.answer_text && <p><b>Your answer:</b> {t.answer_text.slice(0, 300)}{t.answer_text.length > 300 ? '…' : ''}</p>}
          {t.code && <details><summary>Your code</summary><pre className="code-view">{t.code}</pre></details>}
          <p><b>Feedback:</b> {t.feedback}</p>
          <p><b>Better answer:</b> {t.better_answer}</p>
        </div>
      ))}

      <button className="primary big" onClick={onAgain}>Practice again 🔁</button>
    </div>
  )
}
