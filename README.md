---
title: AI Mock Interviewer
sdk: docker
app_port: 8000
---

# 🎙️ AI Mock Interviewer

Practice technical interviews with an AI interviewer — right in your browser.
The AI asks questions **by voice**, you answer by voice or by writing code,
your code gets **executed live**, and at the end you get **rubric-based
feedback, scores, and a weak-topics report**.

## ✨ Features

- **3 interview modes** — HR Round, DSA Round, CS Fundamentals (OS / DBMS / CN)
- **Voice in & out** — questions spoken aloud (Speech Synthesis), answers dictated (Speech Recognition, Chrome)
- **Live code execution** — Python, JavaScript, Java, C via the free WandBox API (no key needed)
- **Rubric evaluation** — correctness / approach / communication scored 0–10 per answer, with written feedback, a "better answer" example, and a follow-up question
- **Session report** — aggregate scores, per-question breakdown, weak topics
- **Works without any API key** — built-in question bank (10 HR, 12 CS, 14 DSA problems with starter code + test cases) and heuristic evaluation. Add a free Gemini key for AI-generated questions + AI evaluation.

## 🏗️ Architecture

```
┌──────────────┐      ┌──────────────────┐      ┌───────────────┐
│ React (Vite) │─────▶│ FastAPI backend  │─────▶│ Gemini API    │
│  · Home      │ /api │  · sessions CRUD │      │ (optional)    │
│  · Interview │      │  · question bank │      └───────────────┘
│  · Report    │      │  · evaluation    │
└──────────────┘      │  · /execute ─────┼─────▶ WandBox API (free, keyless)
  Web Speech API      │  · SQLite/Postgres│
  (voice, free)       └──────────────────┘
```

## 🚀 Run locally

**Backend** (needs Python 3.10+):

```bash
cd backend
cp .env.example .env        # optional — add GEMINI_API_KEY for AI mode
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend** (needs Node 18+), in another terminal:

```bash
cd frontend
npm install
npm run dev                # http://localhost:5173
```

Open http://localhost:5173, pick a mode, and start. The dev server proxies
`/api` to the backend automatically.

### Environment variables (backend `.env`)

| Var | Required | Default | Notes |
|-----|----------|---------|-------|
| `GEMINI_API_KEY` | No | — | Free key from Google AI Studio enables AI questions + evaluation |
| `DATABASE_URL` | No | `sqlite:///./app.db` | e.g. `postgresql+psycopg://user:pass@host/db` for Postgres |

## 🌐 Deploy (free tiers)

- **Backend → Render**: new Web Service, build `pip install -r requirements.txt`, start `uvicorn main:app --host 0.0.0.0 --port $PORT`. Add `GEMINI_API_KEY` and a Postgres `DATABASE_URL` in env vars for production.
- **Frontend → Vercel**: import the `frontend/` folder. Set the API base: either proxy `/api` via `vercel.json` rewrites to your Render URL, or point `api.js` at the deployed backend URL.

## 📡 API quick reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/sessions` | Create session `{mode, difficulty, topic}` |
| GET | `/api/sessions/{id}/next-question` | Next question (bank or Gemini) |
| POST | `/api/sessions/{id}/answer` | Submit answer → evaluation |
| POST | `/api/sessions/{id}/finish` | End session |
| GET | `/api/sessions/{id}/report` | Aggregate scores + weak topics |
| POST | `/api/execute` | Run code `{language, code, stdin}` |

## 📝 Notes

- Speech recognition works best in Chrome (uses `webkitSpeechRecognition`).
- Code execution uses the free WandBox API — be kind, don't hammer it.
- Gemini model used: `gemini-2.0-flash` (free tier).
