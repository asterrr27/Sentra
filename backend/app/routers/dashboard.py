from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Scan, TestResult
from app.test_engine.runner import ALL_SCENARIO_NAMES

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(20).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "scans": scans, "scenarios": ALL_SCENARIO_NAMES},
    )


@router.get("/results/{scan_id}", response_class=HTMLResponse)
def results(request: Request, scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return HTMLResponse("Scan not found", status_code=404)

    rows = db.query(TestResult).filter(TestResult.scan_id == scan_id).all()

    scenarios = {}
    for r in rows:
        if r.scenario_name not in scenarios:
            scenarios[r.scenario_name] = []
        scenarios[r.scenario_name].append({
            "iteration": r.iteration,
            "passed": bool(r.passed),
            "payload_used": r.payload_used,
        })

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "scan": scan,
            "scenarios": scenarios,
        },
    )


@router.get("/compare", response_class=HTMLResponse)
def compare(request: Request, id1: int, id2: int, db: Session = Depends(get_db)):
    scan1 = db.query(Scan).filter(Scan.id == id1).first()
    scan2 = db.query(Scan).filter(Scan.id == id2).first()

    if not scan1 or not scan2:
        return HTMLResponse("One or both scans not found", status_code=404)

    rows1 = db.query(TestResult).filter(TestResult.scan_id == id1).all()
    rows2 = db.query(TestResult).filter(TestResult.scan_id == id2).all()

    def group(rows):
        grouped = {}
        for r in rows:
            if r.scenario_name not in grouped:
                grouped[r.scenario_name] = []
            grouped[r.scenario_name].append(bool(r.passed))
        return grouped

    return templates.TemplateResponse(
        "compare.html",
        {
            "request": request,
            "scan1": scan1,
            "scan2": scan2,
            "results1": group(rows1),
            "results2": group(rows2),
        },
    )


@router.get("/api/scans/history")
def scan_history(db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(20).all()
    return [
        {"id": s.id, "score": s.score, "date": s.created_at.isoformat() if s.created_at else None}
        for s in scans
    ]
