"""Gemini wrapper with graceful offline fallback.

Every public function here works WITHOUT an API key: when GEMINI_API_KEY is
unset (or the request fails), we fall back to the local question bank and a
heuristic evaluator. Nothing in this module ever raises to the caller.
"""

import json
import os
import re

from http_client import make_client
from question_bank import CS_QUESTIONS, HR_QUESTIONS

MODEL = "gemini-2.0-flash"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def _api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()


def has_key() -> bool:
    return bool(_api_key())


def _call_gemini(prompt: str, system: str = "") -> str | None:
    """Raw text completion; returns None on any failure (never raises)."""
    key = _api_key()
    if not key:
        return None
    try:
        body = {"contents": [{"parts": [{"text": (system + "\n\n" + prompt) if system else prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}}
        with make_client() as client:
            r = client.post(ENDPOINT, params={"key": key}, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None


def _extract_json(text: str) -> dict | None:
    """Pull the first {...} block out of model output and parse it."""
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(m.group(0)) if m else None
    except Exception:
        return None


# ---------------------------------------------------------------- evaluation
def heuristic_evaluate(question: str, answer_text: str, code: str, mode: str) -> dict:
    """Keyword/length-based rubric scoring used when no Gemini key is set.

    Scores are 0-10 per rubric. This is intentionally simple — it rewards
    substantive answers and penalises empty ones, and always returns the
    same schema as the AI evaluator so the frontend needs no branching.
    """
    text = (answer_text or "").strip()
    code = (code or "").strip()
    words = len(text.split())

    if not text and not code:
        return {
            "scores": {"correctness": 1, "approach": 1, "communication": 1},
            "feedback": "No answer was provided. Even a partial attempt — your thought "
                        "process, an approach outline, or brute-force idea — earns points "
                        "in a real interview.",
            "better_answer": "Start by restating the problem in your own words, then walk "
                             "through a simple example before jumping to code.",
            "follow_up": "How would you explain your approach to this question out loud, step by step?",
        }

    # communication: rewards structured, reasonably long answers
    communication = min(10, 2 + words // 25)
    if any(w in text.lower() for w in ("first", "then", "because", "example", "complexity")):
        communication = min(10, communication + 2)

    # correctness/approach: keyword coverage against the question
    q_words = {w.strip(".,?").lower() for w in question.split() if len(w) > 4}
    t_words = set(text.lower().split())
    overlap = len(q_words & t_words) / max(1, len(q_words))
    base = 3 + int(overlap * 5)

    if mode == "dsa" and code:
        # code present: reward structure (function defs, loops, returns)
        structure = sum(k in code for k in ("def ", "return", "for ", "while ", "if "))
        approach = min(10, base + min(3, structure))
        correctness = min(10, base + (2 if "def " in code and "return" in code else 0))
    elif mode == "dsa":
        approach = min(10, base)
        correctness = min(10, max(2, base - 2))  # no code => capped correctness
    else:
        approach = min(10, base + (1 if words > 60 else 0))
        correctness = min(10, base + (1 if words > 100 else 0))

    feedback_bits = []
    if words < 40:
        feedback_bits.append("Your answer is quite short — interviewers want to hear your reasoning, not just the conclusion.")
    if mode == "dsa" and not code:
        feedback_bits.append("For coding questions, always write code — even brute force. Talking through it is good, shipping code is better.")
    if "complexity" not in text.lower() and mode == "dsa":
        feedback_bits.append("Mention time/space complexity unprompted — interviewers love that.")
    if not feedback_bits:
        feedback_bits.append("Solid attempt. Tighten it by leading with the key insight, then the details.")

    return {
        "scores": {"correctness": correctness, "approach": approach, "communication": communication},
        "feedback": " ".join(feedback_bits),
        "better_answer": "A strong answer restates the problem, works a small example, states the approach "
                         "and complexity, then implements cleanly.",
        "follow_up": "Can you walk me through the time and space complexity of your approach?",
    }


def evaluate_answer(question: str, answer_text: str, code: str, language: str, mode: str) -> dict:
    """Evaluate one answer. Uses Gemini when a key is set, else heuristics."""
    text = _call_gemini(
        system="You are a strict but fair technical interviewer. Reply ONLY with a JSON object.",
        prompt=(
            f"Interview mode: {mode}\nQuestion: {question}\n"
            f"Candidate's spoken/written answer: {answer_text or '(none)'}\n"
            f"Candidate's code ({language or 'n/a'}):\n{code or '(none)'}\n\n"
            "Return JSON: {\"scores\": {\"correctness\": 0-10, \"approach\": 0-10, "
            "\"communication\": 0-10}, \"feedback\": \"2-3 sentences\", "
            "\"better_answer\": \"what a great answer looks like\", "
            "\"follow_up\": \"one sharp follow-up question\"}"
        ),
    ) if has_key() else None

    if text:
        parsed = _extract_json(text)
        if parsed and isinstance(parsed.get("scores"), dict):
            s = parsed["scores"]
            parsed["scores"] = {
                "correctness": max(0, min(10, int(s.get("correctness", 5)))),
                "approach": max(0, min(10, int(s.get("approach", 5)))),
                "communication": max(0, min(10, int(s.get("communication", 5)))),
            }
            for k in ("feedback", "better_answer", "follow_up"):
                parsed.setdefault(k, "")
            return parsed

    return heuristic_evaluate(question, answer_text, code, mode)


# ---------------------------------------------------------------- questions
def ai_generate_question(mode: str, difficulty: str, topic: str, asked: list[str]) -> str | None:
    """Ask Gemini for a fresh question; None if no key or on failure."""
    if not has_key():
        return None
    text = _call_gemini(
        system="You are a technical interviewer. Reply with ONLY the interview question, no preamble.",
        prompt=(
            f"Write one {difficulty} interview question. Mode: {mode}. "
            f"Topic: {topic}. Avoid these already-asked questions: {asked[:10]}. "
            "For coding questions include a clear input/output format."
        ),
    )
    return text.strip() if text else None


def get_fallback_question(mode: str, topic: str, asked: list[str]):
    """Local-bank question when Gemini is unavailable. Returns (text, category, extra)."""
    import random
    from question_bank import get_dsa_question

    if mode == "hr":
        pool = [q for q in HR_QUESTIONS if q not in asked] or HR_QUESTIONS
        return random.choice(pool), "hr", {}
    if mode == "cs":
        pool = [q for q in CS_QUESTIONS if q["question"] not in asked] or CS_QUESTIONS
        q = random.choice(pool)
        return q["question"], f"cs:{q['category']}", {}
    # dsa
    asked_titles = {a for a in asked}
    q = get_dsa_question(topic, "medium", exclude_titles=asked_titles)
    if not q:
        q = get_dsa_question(topic, "easy")
    if not q:
        return "Explain Big-O notation with an example.", "dsa:general", {}
    text = f"{q['title']}\n\n{q['prompt']}"
    return text, f"dsa:{topic}", {"starter_code": q["starter_code"], "tests": q["tests"], "title": q["title"]}
