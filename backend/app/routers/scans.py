import csv
import io
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from fastapi.responses import Response

from app.database import get_db, SessionLocal
from app.models import Scan, TestResult
from app.schemas import ScanRequest, ScanResponse, ScanStatus
from app.agents import get_connector
from app.report_generator import generate_pdf
from app.test_engine.runner import ScanRunner, ALL_SCENARIO_NAMES

router = APIRouter(prefix="/api/scans", tags=["scans"])


def run_scan_in_background(scan_id: int, connector, scenario_names: Optional[list[str]]):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return
        runner = ScanRunner(db, scan, connector, scenario_names)
        runner.run()
    finally:
        db.close()


@router.post("", response_model=ScanResponse)
def create_scan(req: ScanRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    scenario_names = req.scenarios or ALL_SCENARIO_NAMES
    for s in scenario_names:
        if s not in ALL_SCENARIO_NAMES:
            raise HTTPException(400, f"Unknown scenario: {s}")

    scan = Scan(
        provider=req.provider,
        model_name=req.model,
        webhook_url=req.webhook_url,
        agent_type=req.provider,
        system_prompt=req.system_prompt,
        iterations=req.iterations,
        status="queued",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    connector = get_connector(req.provider, {
        "api_key": req.api_key,
        "model": req.model,
        "url": req.webhook_url,
        "auth_header": req.auth_header,
        "system_prompt": req.system_prompt,
    })
    background_tasks.add_task(run_scan_in_background, scan.id, connector, scenario_names)

    return ScanResponse(
        scan_id=scan.id,
        status="queued",
        message="Scan queued.",
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


@router.post("/{scan_id}/cancel")
def cancel_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    if scan.status not in ("queued", "running"):
        raise HTTPException(400, f"Scan is '{scan.status}', cannot cancel")
    scan.status = "cancelled"
    db.commit()
    return {"scan_id": scan.id, "status": "cancelled", "message": "Scan cancelled."}


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
        "provider": scan.provider,
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
            "provider": scan.provider,
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


@router.get("/{scan_id}/export/pdf")
def export_scan_pdf(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    results = db.query(TestResult).filter(TestResult.scan_id == scan_id).all()
    pdf_bytes = generate_pdf(scan, results)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}.pdf"},
    )


@router.get("/{scan_id}/export/csv")
def export_scan_csv(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    results = db.query(TestResult).filter(TestResult.scan_id == scan_id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Scan ID", "Provider", "Score", "Scenario", "Iteration", "Passed", "Payload Used"])
    for r in results:
        writer.writerow([scan.id, scan.provider, scan.score, r.scenario_name, r.iteration, "PASS" if r.passed else "FAIL", r.payload_used or ""])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}.csv"},
    )
