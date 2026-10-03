"""SQLAlchemy models: one interview session holds many Q&A turns."""

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from db import Base


class InterviewSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String(32), nullable=False)          # hr | dsa | cs
    difficulty = Column(String(16), default="medium")  # easy | medium | hard
    topic = Column(String(64), default="general")
    status = Column(String(16), default="active")       # active | finished
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    turns = relationship("Turn", back_populates="session", cascade="all, delete-orphan")


class Turn(Base):
    __tablename__ = "turns"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    category = Column(String(64), default="")          # e.g. dsa:arrays / hr / cs:os
    answer_text = Column(Text, default="")
    code = Column(Text, default="")
    language = Column(String(32), default="")
    scores = Column(JSON, default=dict)                # {correctness, approach, communication}
    feedback = Column(Text, default="")
    better_answer = Column(Text, default="")
    follow_up = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("InterviewSession", back_populates="turns")
