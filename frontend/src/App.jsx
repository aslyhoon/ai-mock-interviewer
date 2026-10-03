import { useState } from 'react'
import Home from './components/Home.jsx'
import InterviewRoom from './components/InterviewRoom.jsx'
import Report from './components/Report.jsx'

// Simple view state machine — no router library needed.
export default function App() {
  const [view, setView] = useState('home') // home | interview | report
  const [session, setSession] = useState(null)

  return (
    <div className="app">
      <header className="topbar">
        <span className="logo">🎙️ AI Mock Interviewer</span>
      </header>
      {view === 'home' && (
        <Home
          onStart={(s) => {
            setSession(s)
            setView('interview')
          }}
        />
      )}
      {view === 'interview' && session && (
        <InterviewRoom
          session={session}
          onFinish={() => setView('report')}
          onExit={() => setView('home')}
        />
      )}
      {view === 'report' && session && (
        <Report
          sessionId={session.id}
          onAgain={() => setView('home')}
        />
      )}
    </div>
  )
}
