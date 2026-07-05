import csv
import io
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from fastapi.responses import Response

from app.config import settings
from app.database import get_db, SessionLocal
from app.limiter import limiter
from app.models import Scan, TestResult
from app.schemas import ScanRequest, ScanResponse, ScanStatus
from app.agents import get_connector
from app.auth import get_current_user, CurrentUser
from app.report_generator import generate_pdf
from app.scoring.calculator import SCENARIO_OWASP_MAP
from app.reporting.vulnerability_data import SCENARIO_METADATA
from app.test_engine.runner import ScanRunner, ALL_SCENARIO_NAMES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/scans", tags=["scans"])


def _get_user_scan(scan_id: int, user: CurrentUser, db: Session) -> Scan:
    q = db.query(Scan).filter(Scan.id == scan_id)
    if user.role != "admin":
        q = q.filter(Scan.user_id == user.id)
    scan = q.first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    return scan


def run_scan_in_background(scan_id: int, connector, scenario_names: Optional[list[str]]):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            logger.warning(f"Background task: Scan {scan_id} not found, skipping")
            return
        runner = ScanRunner(db, scan, connector, scenario_names)
        runner.run()
    except Exception:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = "failed"
            db.commit()
            logger.error(f"Background task: Scan {scan_id} failed", exc_info=True)
    finally:
        db.close()


@router.post("", response_model=ScanResponse)
@limiter.limit(settings.RATE_LIMIT)
def create_scan(request: Request, req: ScanRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    scenario_names = req.scenarios or ALL_SCENARIO_NAMES
    for s in scenario_names:
        if s not in ALL_SCENARIO_NAMES:
            raise HTTPException(400, f"Unknown scenario: {s}")

    connector = get_connector(req.provider, {
        "api_key": req.api_key,
        "model": req.model,
        "url": req.webhook_url,
        "auth_header": req.auth_header,
        "system_prompt": req.system_prompt,
    })

    scan = Scan(
        user_id=user.id,
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

    background_tasks.add_task(run_scan_in_background, scan.id, connector, scenario_names)

    return ScanResponse(
        scan_id=scan.id,
        status="queued",
        message="Scan queued.",
    )


@router.get("", response_model=list[ScanStatus])
def list_scans(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    q = db.query(Scan)
    if user.role != "admin":
        q = q.filter(Scan.user_id == user.id)
    scans = q.order_by(Scan.created_at.desc()).limit(20).all()
    return [
        ScanStatus(
            scan_id=s.id,
            status=s.status,
            score=s.score,
            agent_type=s.agent_type,
            progress=f"{s.status}"
        )
        for s in scans
    ]


@router.post("/{scan_id}/cancel")
def cancel_scan(scan_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    scan = _get_user_scan(scan_id, user, db)
    if scan.status not in ("queued", "running"):
        raise HTTPException(400, f"Scan is '{scan.status}', cannot cancel")
    scan.status = "cancelled"
    db.commit()
    return {"scan_id": scan.id, "status": "cancelled", "message": "Scan cancelled."}


@router.get("/{scan_id}", response_model=ScanStatus)
def get_scan_status(scan_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    scan = _get_user_scan(scan_id, user, db)
    total = db.query(TestResult).filter(TestResult.scan_id == scan_id).count()
    return ScanStatus(
        scan_id=scan.id,
        status=scan.status,
        score=scan.score,
        agent_type=scan.agent_type,
        progress=f"{total} results recorded",
    )


@router.get("/{scan_id}/results")
def get_scan_results(scan_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    scan = _get_user_scan(scan_id, user, db)
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
    scenario_owasp = {
        name: SCENARIO_OWASP_MAP.get(name, "Uncategorized")
        for name in scenarios
    }
    return {
        "scan_id": scan.id,
        "provider": scan.provider,
        "agent_type": scan.agent_type,
        "status": scan.status,
        "score": scan.score,
        "owasp_breakdown": scan.owasp_breakdown,
        "scenario_owasp": scenario_owasp,
        "iterations": scan.iterations,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "scenarios": scenarios,
    }


@router.get("/{scan_id}/export")
def export_scan(scan_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    scan = _get_user_scan(scan_id, user, db)
    results = db.query(TestResult).filter(TestResult.scan_id == scan_id).all()
    total_tests = len(results)
    total_passed = sum(1 for r in results if r.passed)
    total_failed = total_tests - total_passed
    pass_rate = round(total_passed / total_tests * 100, 1) if total_tests else 0
    scenario_groups = {}
    for r in results:
        scenario_groups.setdefault(r.scenario_name, []).append(r)
    owasp_categories = set(SCENARIO_OWASP_MAP.get(s, "") for s in scenario_groups)

    scenarios_out = []
    for sname, sresults in scenario_groups.items():
        passed = sum(1 for r in sresults if r.passed)
        total = len(sresults)
        meta = SCENARIO_METADATA.get(sname, {})
        scenarios_out.append({
            "name": sname,
            "label": meta.get("label", sname.replace("_", " ").title()),
            "owasp_category": meta.get("owasp_category", SCENARIO_OWASP_MAP.get(sname, "")),
            "severity": meta.get("severity_label", "Medium"),
            "severity_weight": meta.get("severity_weight", 1.0),
            "passed": passed,
            "total": total,
            "pass_rate": round(passed / total * 100, 1) if total else 0,
            "vulnerability": {
                "description": meta.get("description", ""),
                "mitigation": meta.get("mitigation", ""),
            } if passed < total else None,
            "iterations": [
                {
                    "iteration": r.iteration,
                    "passed": bool(r.passed),
                    "payload_used": r.payload_used or "",
                }
                for r in sresults
            ],
        })

    risk_level = "Low Risk" if scan.score is not None and scan.score >= 80 else "Moderate Risk" if scan.score is not None and scan.score >= 50 else "High Risk"

    data = {
        "report_metadata": {
            "tool": "Sentra",
            "version": "2.3.0",
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "scan_id": scan.id,
        },
        "summary": {
            "score": scan.score,
            "risk_level": risk_level if scan.score is not None else None,
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "pass_rate": pass_rate,
            "scenarios_tested": len(scenario_groups),
            "owasp_categories_covered": len(owasp_categories),
            "owasp_breakdown": scan.owasp_breakdown or {},
        },
        "scenarios": scenarios_out,
        "agent": {
            "provider": scan.provider,
            "agent_type": scan.agent_type,
            "iterations": scan.iterations,
            "system_prompt": scan.system_prompt,
        },
        "metadata": {
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "exported_at": datetime.utcnow().isoformat() + "Z",
        },
    }
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}.json"},
    )


@router.get("/{scan_id}/export/pdf")
def export_scan_pdf(scan_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    scan = _get_user_scan(scan_id, user, db)
    results = db.query(TestResult).filter(TestResult.scan_id == scan_id).all()
    pdf_bytes = generate_pdf(scan, results)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}.pdf"},
    )


@router.get("/{scan_id}/export/csv")
def export_scan_csv(scan_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    scan = _get_user_scan(scan_id, user, db)
    results = db.query(TestResult).filter(TestResult.scan_id == scan_id).all()
    output = io.StringIO()
    writer = csv.writer(output)

    risk_level = "Low Risk" if scan.score is not None and scan.score >= 80 else "Moderate Risk" if scan.score is not None and scan.score >= 50 else "High Risk"
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    created = scan.created_at.strftime("%Y-%m-%d %H:%M UTC") if scan.created_at else ""

    writer.writerow(["SCAN METADATA"])
    writer.writerow(["Scan ID", "Provider", "Score", "Risk Level", "Iterations", "Agent Type", "Date"])
    writer.writerow([scan.id, scan.provider or "", scan.score or "", risk_level if scan.score is not None else "", scan.iterations, scan.agent_type or "", created])
    writer.writerow([])

    scenario_groups = {}
    for r in results:
        scenario_groups.setdefault(r.scenario_name, []).append(r)

    writer.writerow(["SCENARIO SUMMARY"])
    writer.writerow(["Scenario", "OWASP Category", "Severity", "Passed", "Total", "Pass Rate"])
    for sname, sresults in scenario_groups.items():
        passed = sum(1 for r in sresults if r.passed)
        total = len(sresults)
        pct = round(passed / total * 100, 1) if total else 0
        meta = SCENARIO_METADATA.get(sname, {})
        writer.writerow([
            meta.get("label", sname),
            meta.get("owasp_category", ""),
            meta.get("severity_label", "Medium"),
            passed,
            total,
            f"{pct}%",
        ])
    writer.writerow([])

    writer.writerow(["DETAILED RESULTS"])
    writer.writerow(["Scenario", "Label", "OWASP Category", "Iteration", "Result", "Payload Used", "Mitigation"])
    for r in results:
        meta = SCENARIO_METADATA.get(r.scenario_name, {})
        writer.writerow([
            r.scenario_name,
            meta.get("label", ""),
            meta.get("owasp_category", SCENARIO_OWASP_MAP.get(r.scenario_name, "")),
            r.iteration,
            "PASS" if r.passed else "FAIL",
            r.payload_used or "",
            meta.get("mitigation", "") if not r.passed else "",
        ])
    writer.writerow([])
    writer.writerow([f"Exported: {now}"])
    writer.writerow(["Tool: Sentra v2.3.0"])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}.csv"},
    )
