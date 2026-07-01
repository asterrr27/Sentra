from fastapi import APIRouter
from app.test_engine.payloads import ALL_PAYLOADS

router = APIRouter(tags=["payloads"])


@router.get("/api/payloads")
def get_payloads():
    return ALL_PAYLOADS
