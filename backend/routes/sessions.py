"""Session lifecycle: create -> next question -> answer/evaluate -> finish -> report."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db
from models import InterviewSession, Turn
import gemini_client
from gemini_client import evaluate_answer, get_fallback_question, ai_generate_question, has_key

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

VALID_MODES = {"hr", "dsa", "cs"}
VALID_DIFFICULTY = {"easy", "medium", "hard"}


class CreateSessionIn(BaseModel):
    mode: str = "hr"
    difficulty: str = "medium"
    topic: str = "general"


class AnswerIn(BaseModel):
    question: str
    answer_text: str = ""
    code: str = ""
    language: str = ""


def _asked_questions(db: Session, session_id: int) -> list[str]:
    rows = db.query(Turn.question).filter(Turn.session_id == session_id).all()
    return [r[0] for r in rows]


def _get_session(db: Session, session_id: int) -> InterviewSession:
    s = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not s:
        raise HTTPException(404, "session not found")
    return s


@router.post("")
def create_session(payload: CreateSessionIn, db: Session = Depends(get_db)):
    mode = payload.mode.lower()
    if mode not in VALID_MODES:
        raise HTTPException(400, f"mode must be one of {sorted(VALID_MODES)}")
    difficulty = payload.difficulty.lower()
    if difficulty not in VALID_DIFFICULTY:
        difficulty = "medium"
    s = InterviewSession(mode=mode, difficulty=difficulty, topic=payload.topic or "general")
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "mode": s.mode, "difficulty": s.difficulty, "topic": s.topic, "status": s.status}


@router.get("/{session_id}/next-question")
def next_question(session_id: int, db: Session = Depends(get_db)):
    s = _get_session(db, session_id)
    if s.status != "active":
        raise HTTPException(400, "session is finished")
    asked = _asked_questions(db, session_id)

    question, category, extra = None, "", {}
    if has_key():
        q = ai_generate_question(s.mode, s.difficulty, s.topic, asked)
        if q:
            question, category = q, f"{s.mode}:{s.topic}"
    if not question:
        question, category, extra = get_fallback_question(s.mode, s.topic, asked)

    return {"question": question, "category": category, **extra, "ai_powered": has_key()}


@router.post("/{session_id}/answer")
def submit_answer(session_id: int, payload: AnswerIn, db: Session = Depends(get_db)):
    s = _get_session(db, session_id)
    if s.status != "active":
        raise HTTPException(400, "session is finished")
    if not payload.question:
        raise HTTPException(400, "question is required")

    result = evaluate_answer(payload.question, payload.answer_text, payload.code,
                             payload.language, s.mode)

    turn = Turn(
        session_id=session_id,
        question=payload.question,
        category="",
        answer_text=payload.answer_text,
        code=payload.code,
        language=payload.language,
        scores=result.get("scores", {}),
        feedback=result.get("feedback", ""),
        better_answer=result.get("better_answer", ""),
        follow_up=result.get("follow_up", ""),
    )
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return {
        "turn_id": turn.id,
        "scores": turn.scores,
        "feedback": turn.feedback,
        "better_answer": turn.better_answer,
        "follow_up": turn.follow_up,
        "ai_powered": has_key(),
    }


@router.post("/{session_id}/finish")
def finish_session(session_id: int, db: Session = Depends(get_db)):
    s = _get_session(db, session_id)
    s.status = "finished"
    db.commit()
    return {"id": s.id, "status": s.status}


@router.get("/{session_id}/report")
def session_report(session_id: int, db: Session = Depends(get_db)):
    s = _get_session(db, session_id)
    turns = db.query(Turn).filter(Turn.session_id == session_id).order_by(Turn.id).all()

    def avg(key):
        vals = [t.scores.get(key, 0) for t in turns if t.scores]
        return round(sum(vals) / len(vals), 1) if vals else 0

    aggregate = {
        "correctness": avg("correctness"),
        "approach": avg("approach"),
        "communication": avg("communication"),
    }
    overall = round(sum(aggregate.values()) / 3, 1) if turns else 0

    # weak topics: categories whose average correctness < 6
    by_cat: dict[str, list[float]] = {}
    for t in turns:
        cat = t.category or "general"
        by_cat.setdefault(cat, []).append(t.scores.get("correctness", 0))
    weak_topics = sorted(
        [c for c, v in by_cat.items() if v and sum(v) / len(v) < 6],
        key=lambda c: sum(by_cat[c]) / len(by_cat[c]),
    )

    return {
        "session": {"id": s.id, "mode": s.mode, "difficulty": s.difficulty,
                    "topic": s.topic, "status": s.status},
        "aggregate": aggregate,
        "overall": overall,
        "weak_topics": weak_topics,
        "turns": [
            {"id": t.id, "question": t.question, "category": t.category,
             "answer_text": t.answer_text, "code": t.code, "language": t.language,
             "scores": t.scores, "feedback": t.feedback,
             "better_answer": t.better_answer, "follow_up": t.follow_up}
            for t in turns
        ],
    }
