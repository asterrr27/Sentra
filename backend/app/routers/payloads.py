from fastapi import APIRouter, Depends
from app.auth import get_current_user, CurrentUser
from app.test_engine.payloads import ALL_PAYLOADS

router = APIRouter(tags=["payloads"])


@router.get("/api/payloads")
def get_payloads(user: CurrentUser = Depends(get_current_user)):
    return ALL_PAYLOADS
