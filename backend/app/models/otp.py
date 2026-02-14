# OTP and pending signup storage — Postgres (replaces in-memory dicts)
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone, timedelta
from app.db.base import Base


class OTPRecord(Base):
    """Stores OTP codes for email verification (replaces in-memory otp_storage dict)."""
    __tablename__ = "otp_records"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    otp = Column(String(10), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PendingSignup(Base):
    """Stores pending user signups until OTP is verified (replaces in-memory pending_users dict)."""
    __tablename__ = "pending_signups"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(String(50), default="patient")
    registration_number = Column(String(100))
    specialization = Column(String(255))
    experience_years = Column(Integer)
    hospital_address = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RAGInteraction(Base):
    """Stores RAG chatbot interactions for feedback / learning loop
    (replaces raw sqlite3 in rag/learning.py)."""
    __tablename__ = "rag_interactions"

    id = Column(String(20), primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(Text, default="[]")       # JSON string
    confidence = Column(Integer, default=0)     # stored as float but Column type is fine
    risk_level = Column(String(20), default="low")
    feedback = Column(String(20))              # 'helpful' | 'not_helpful' | NULL
    feedback_note = Column(Text)
    ingested = Column(Integer, default=0)       # 1 = added to vector store
    question_hash = Column(String(64), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
