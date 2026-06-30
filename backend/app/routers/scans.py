import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import Scan, TestResult
from app.schemas import ScanRequest, ScanResponse, ScanStatus
from app.demo_agent.agent import DemoAgent
from app.test_engine.runner import ScanRunner, ALL_SCENARIO_NAMES

router = APIRouter(prefix="/api/scans", tags=["scans"])


def run_scan_in_background(scan_id: int, agent: DemoAgent, scenario_names: Optional[list[str]]):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return
        runner = ScanRunner(db, scan, agent, scenario_names)
        runner.run()
    finally:
        db.close()


@router.post("", response_model=ScanResponse)
def create_scan(req: ScanRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if req.agent_type == "custom" and not req.custom_webhook_url:
        raise HTTPException(400, "custom_webhook_url required for custom agent")

    scenario_names = req.scenarios or ALL_SCENARIO_NAMES
    for s in scenario_names:
        if s not in ALL_SCENARIO_NAMES:
            raise HTTPException(400, f"Unknown scenario: {s}")

    scan = Scan(
        agent_type=req.agent_type,
        custom_webhook_url=req.custom_webhook_url,
        system_prompt=req.system_prompt,
        iterations=req.iterations,
        status="queued",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    agent = DemoAgent(system_prompt=req.system_prompt)
    background_tasks.add_task(run_scan_in_background, scan.id, agent, scenario_names)

    return ScanResponse(
        scan_id=scan.id,
        status="queued",
        message="Scan queued. Check /api/scans/{id} for status.",
    )


@router.get("", response_model=list[ScanStatus])
def list_scans(db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(20).all()
    return [
        ScanStatus(
            scan_id=s.id,
            status=s.status,
            score=s.score,
            progress=f"{s.status}"
        )
        for s in scans
    ]


@router.get("/{scan_id}", response_model=ScanStatus)
def get_scan_status(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")

    total = db.query(TestResult).filter(TestResult.scan_id == scan_id).count()
    return ScanStatus(
        scan_id=scan.id,
        status=scan.status,
        score=scan.score,
        progress=f"{total} results recorded",
    )


@router.get("/{scan_id}/results")
def get_scan_results(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")

    results = db.query(TestResult).filter(TestResult.scan_id == scan_id).all()

    scenarios = {}
    for r in results:
        if r.scenario_name not in scenarios:
            scenarios[r.scenario_name] = []
        scenarios[r.scenario_name].append({
            "iteration": r.iteration,
            "passed": bool(r.passed),
            "payload_used": r.payload_used,
        })

    return {
        "scan_id": scan.id,
        "agent_type": scan.agent_type,
        "status": scan.status,
        "score": scan.score,
        "owasp_breakdown": scan.owasp_breakdown,
        "iterations": scan.iterations,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "scenarios": scenarios,
    }


@router.get("/{scan_id}/export")
def export_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")

    results = db.query(TestResult).filter(TestResult.scan_id == scan_id).all()

    data = {
        "scan": {
            "id": scan.id,
            "agent_type": scan.agent_type,
            "status": scan.status,
            "score": scan.score,
            "owasp_breakdown": scan.owasp_breakdown,
            "iterations": scan.iterations,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
        },
        "results": [
            {
                "scenario": r.scenario_name,
                "iteration": r.iteration,
                "passed": bool(r.passed),
                "payload_used": r.payload_used,
            }
            for r in results
        ],
    }

    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}.json"},
    )
