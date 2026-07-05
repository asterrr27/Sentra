from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.limiter import limiter
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
@limiter.limit("30/minute")
def list_users(request: Request, db: Session = Depends(get_db), _=Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    def mask_email(email: str) -> str:
        at = email.find("@")
        if at < 2:
            return email
        return email[0] + "***" + email[at - 1:] if at > 2 else email[0] + "***" + email[at:]
    return [
        {"id": u.id, "username": u.username, "email": mask_email(u.email), "role": u.role, "created_at": str(u.created_at or "")}
        for u in users
    ]


@router.get("/stats")
@limiter.limit("30/minute")
def get_stats(request: Request, db: Session = Depends(get_db), _=Depends(require_admin)):
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
@limiter.limit("10/minute")
def reset_password(request: Request, user_id: int, req: ResetPasswordRequest, db: Session = Depends(get_db), _=Depends(require_admin)):
    if len(req.new_password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"ok": True, "message": f"Password reset for {user.username}"}
