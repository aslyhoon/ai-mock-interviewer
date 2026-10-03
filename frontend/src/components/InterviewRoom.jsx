import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api.js'

const LANGUAGES = ['python', 'javascript', 'java', 'c']
const QUESTION_TIME = 300 // 5 minutes per question

function useSpeech() {
  // Web Speech API wrappers (Chrome: webkitSpeechRecognition).
  const speak = useCallback((text) => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'en-US'
    u.rate = 1
    window.speechSynthesis.speak(u)
  }, [])

  const listen = useCallback((onResult, onEnd) => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) {
      onEnd && onEnd(new Error('Speech recognition not supported in this browser. Use Chrome.'))
      return null
    }
    const rec = new SR()
    rec.lang = 'en-US'
    rec.interimResults = true
    rec.continuous = true
    rec.onresult = (e) => {
      let text = ''
      for (let i = e.resultIndex; i < e.results.length; i++) text += e.results[i][0].transcript
      onResult(text)
    }
    rec.onend = () => onEnd && onEnd()
    rec.onerror = (e) => onEnd && onEnd(new Error(e.error))
    rec.start()
    return rec
  }, [])

  return { speak, listen }
}

export default function InterviewRoom({ session, onFinish, onExit }) {
  const [question, setQuestion] = useState(null)
  const [loading, setLoading] = useState(true)
  const [answer, setAnswer] = useState('')
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [stdin, setStdin] = useState('')
  const [runOut, setRunOut] = useState('')
  const [running, setRunning] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const [listening, setListening] = useState(false)
  const [seconds, setSeconds] = useState(QUESTION_TIME)
  const [result, setResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [qCount, setQCount] = useState(0)
  const recRef = useRef(null)
  const { speak, listen } = useSpeech()

  const loadQuestion = useCallback(async () => {
    setLoading(true)
    setError('')
    setResult(null)
    setAnswer('')
    setCode('')
    setRunOut('')
    setSeconds(QUESTION_TIME)
    try {
      const q = await api.nextQuestion(session.id)
      setQuestion(q)
      if (q.starter_code) setCode(q.starter_code)
      setQCount((c) => c + 1)
    } catch (e) {
      setError('Failed to load question: ' + e.message)
    } finally {
      setLoading(false)
    }
  }, [session.id])

  useEffect(() => {
    loadQuestion()
    return () => {
      window.speechSynthesis && window.speechSynthesis.cancel()
      recRef.current && recRef.current.stop()
    }
  }, [loadQuestion])

  // countdown
  useEffect(() => {
    if (loading || result) return
    const t = setInterval(() => setSeconds((s) => Math.max(0, s - 1)), 1000)
    return () => clearInterval(t)
  }, [loading, result])

  const speakQuestion = () => {
    if (!question) return
    setSpeaking(true)
    speak(question.question)
    // crude speaking indicator: reset after estimated duration
    setTimeout(() => setSpeaking(false), Math.min(15000, question.question.length * 90))
  }

  const toggleMic = () => {
    if (listening) {
      recRef.current && recRef.current.stop()
      setListening(false)
      return
    }
    setListening(true)
    recRef.current = listen(
      (text) => setAnswer(text),
      (err) => {
        setListening(false)
        if (err) setError(err.message)
      }
    )
  }

  const runCode = async () => {
    setRunning(true)
    setRunOut('')
    try {
      const r = await api.execute({ language, code, stdin })
      setRunOut((r.output || '') + (r.stderr ? '\nSTDERR:\n' + r.stderr : ''))
    } catch (e) {
      setRunOut('Execution failed: ' + e.message)
    } finally {
      setRunning(false)
    }
  }

  const submit = async () => {
    if (!question) return
    recRef.current && recRef.current.stop()
    setListening(false)
    window.speechSynthesis && window.speechSynthesis.cancel()
    setSubmitting(true)
    setError('')
    try {
      const r = await api.answer(session.id, {
        question: question.question,
        answer_text: answer,
        code,
        language,
      })
      setResult(r)
    } catch (e) {
      setError('Submit failed: ' + e.message)
    } finally {
      setSubmitting(false)
    }
  }

  const endInterview = async () => {
    try {
      await api.finish(session.id)
    } catch {
      /* report still works with stored turns */
    }
    onFinish()
  }

  const fmt = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

  return (
    <div className="room">
      <div className="room-head">
        <span className="pill">{session.mode.toUpperCase()} · {session.difficulty}</span>
        <span className={`timer ${seconds < 60 ? 'low' : ''}`}>⏱ {fmt(seconds)}</span>
        <button className="ghost" onClick={onExit}>Exit</button>
        <button className="danger" onClick={endInterview}>End Interview & See Report</button>
      </div>

      {error && <div className="error">{error}</div>}

      {loading && <div className="loading">Loading question…</div>}

      {!loading && question && (
        <>
          <div className="qcard">
            <div className="q-head">
              <h2>Question {qCount}</h2>
              <button className="primary" onClick={speakQuestion}>
                {speaking ? '🔊 Speaking…' : '🔊 Speak question'}
              </button>
            </div>
            <pre className="qtext">{question.question}</pre>
            {question.tests && (
              <details className="tests">
                <summary>Sample test cases ({question.tests.length})</summary>
                {question.tests.map((t, i) => (
                  <div key={i} className="test">
                    <div><b>Input:</b><pre>{t.input}</pre></div>
                    <div><b>Expected:</b><pre>{t.output}</pre></div>
                  </div>
                ))}
              </details>
            )}
          </div>

          <div className="workspace">
            <div className="panel">
              <h3>Your answer</h3>
              <div className="mic-row">
                <button className={`mic ${listening ? 'on' : ''}`} onClick={toggleMic}>
                  {listening ? '⏹ Stop mic' : '🎤 Speak answer'}
                </button>
                {listening && <span className="pulse">● listening…</span>}
              </div>
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type or dictate your answer / explain your approach…"
                rows={8}
              />
            </div>

            {session.mode === 'dsa' && (
              <div className="panel">
                <h3>Code</h3>
                <div className="code-bar">
                  <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                    {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
                  </select>
                  <input
                    value={stdin}
                    onChange={(e) => setStdin(e.target.value)}
                    placeholder="stdin (use \n for new lines)"
                  />
                  <button className="primary" onClick={runCode} disabled={running}>
                    {running ? 'Running…' : '▶ Run'}
                  </button>
                </div>
                <textarea
                  className="code"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="// write your solution here"
                  rows={12}
                  spellCheck={false}
                />
                {runOut && <pre className="output">{runOut}</pre>}
              </div>
            )}
          </div>

          {!result && (
            <button className="primary big" onClick={submit} disabled={submitting}>
              {submitting ? 'Evaluating…' : 'Submit Answer'}
            </button>
          )}

          {result && (
            <div className="eval">
              <h3>AI Evaluation {result.ai_powered ? '🤖' : '(heuristic)'}</h3>
              <div className="scores">
                {Object.entries(result.scores || {}).map(([k, v]) => (
                  <div key={k} className="score">
                    <span>{k}</span>
                    <div className="bar"><div className="fill" style={{ width: `${v * 10}%` }} /></div>
                    <b>{v}/10</b>
                  </div>
                ))}
              </div>
              <p><b>Feedback:</b> {result.feedback}</p>
              <p><b>Better answer:</b> {result.better_answer}</p>
              {result.follow_up && <p className="follow">Follow-up: <i>{result.follow_up}</i></p>}
              <button className="primary big" onClick={loadQuestion}>Next Question →</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
