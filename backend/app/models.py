import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(50), nullable=False)
    custom_webhook_url = Column(String(500), nullable=True)
    system_prompt = Column(Text, nullable=True)
    iterations = Column(Integer, default=5)
    score = Column(Float, nullable=True)
    owasp_breakdown = Column(JSON, nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    results = relationship("TestResult", back_populates="scan", cascade="all, delete-orphan")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    scenario_name = Column(String(100), nullable=False)
    iteration = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)
    payload_used = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)

    scan = relationship("Scan", back_populates="results")
