from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.test_engine.payloads import ALL_PAYLOADS

router = APIRouter(tags=["payloads"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/payloads", response_class=HTMLResponse)
def payloads_page(request: Request):
    return templates.TemplateResponse(
        "payloads.html",
        {"request": request, "payloads": ALL_PAYLOADS},
    )
