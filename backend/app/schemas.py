from pydantic import BaseModel, Field
from typing import Optional, List


class ScanRequest(BaseModel):
    provider: str = Field(default="demo", pattern="^(openai|anthropic|webhook|demo)$")
    api_key: Optional[str] = None
    model: Optional[str] = None
    webhook_url: Optional[str] = None
    auth_header: Optional[str] = None
    system_prompt: Optional[str] = Field(default=None, max_length=10000)
    iterations: int = Field(default=5, ge=1, le=20)
    scenarios: Optional[List[str]] = Field(default=None, max_length=50)


class ScanResponse(BaseModel):
    scan_id: int
    status: str
    message: str


class ScanStatus(BaseModel):
    scan_id: int
    status: str
    score: Optional[float] = None
    progress: str
