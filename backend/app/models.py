from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    provider = Column(String(20), default="demo")
    model_name = Column(String(100), nullable=True)
    webhook_url = Column(String(500), nullable=True)
    agent_type = Column(String(50), nullable=False)
    custom_webhook_url = Column(String(500), nullable=True)
    system_prompt = Column(Text, nullable=True)
    iterations = Column(Integer, default=5)
    score = Column(Float, nullable=True)
    owasp_breakdown = Column(JSON, nullable=True)
    status = Column(String(20), default="queued")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", backref="scans")
    results = relationship("TestResult", back_populates="scan", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    scenario_name = Column(String(100), nullable=False)
    iteration = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    payload_used = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)

    scan = relationship("Scan", back_populates="results")
