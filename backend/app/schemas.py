from pydantic import BaseModel, Field
from typing import Optional, List


class ScanRequest(BaseModel):
    agent_type: str = Field(..., pattern="^(demo|custom)$")
    custom_webhook_url: Optional[str] = None
    system_prompt: Optional[str] = None
    iterations: int = Field(default=5, ge=1, le=20)
    scenarios: Optional[List[str]] = None


class ScanResponse(BaseModel):
    scan_id: int
    status: str
    message: str


class ScanStatus(BaseModel):
    scan_id: int
    status: str
    score: Optional[float] = None
    progress: str
