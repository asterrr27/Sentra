from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Scan
from app.auth import hash_password
from app.auth import get_current_user, CurrentUser


class ResetPasswordRequest(BaseModel):
    new_password: str

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != "admin":
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
    scores = [s[0] for s in db.query(Scan.score).filter(Scan.status == "completed").all() if s[0] is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    return {
        "total_users": total_users,
        "total_scans": total_scans,
        "completed_scans": completed_scans,
        "average_score": round(avg_score, 1),
    }


@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: int, req: ResetPasswordRequest, db: Session = Depends(get_db), _=Depends(require_admin)):
    if len(req.new_password) < 4:
        raise HTTPException(400, "Password must be at least 4 characters")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"ok": True, "message": f"Password reset for {user.username}"}
