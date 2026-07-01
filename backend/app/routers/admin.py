from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Scan
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(403, "Admin access required")
    return current_user


@router.get("/users")
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {"id": u.id, "username": u.username, "email": u.email, "role": u.role, "created_at": str(u.created_at or "")}
        for u in users
    ]


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    total_users = db.query(User).count()
    total_scans = db.query(Scan).count()
    completed_scans = db.query(Scan).filter(Scan.status == "completed").count()
    avg_score = db.query(Scan.score).filter(Scan.status == "completed").all()
    avg_score = sum(s[0] for s in avg_score if s[0] is not None) / len(avg_score) if avg_score else 0
    return {
        "total_users": total_users,
        "total_scans": total_scans,
        "completed_scans": completed_scans,
        "average_score": round(avg_score, 1),
    }
