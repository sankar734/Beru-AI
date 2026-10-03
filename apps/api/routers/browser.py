"""NOVA X - Browser Automation API Router
Provides safe web navigation, DOM parsing, and SSRF-protected extraction.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from services.ai_core.browser.browser_agent import (
    browser_agent,
    BrowserNavigationResult,
)
from apps.api.auth import get_optional_user

router = APIRouter(prefix="/browser", tags=["Browser Automation"])


class NavigateRequest(BaseModel):
    url: str = Field(..., min_length=3, description="Target web URL to navigate")


@router.post("/navigate", response_model=BrowserNavigationResult)
async def navigate_browser(
    req: NavigateRequest,
    user=Depends(get_optional_user),
):
    """Navigates to a web URL, returning clean textual DOM content and discovered links."""
    try:
        return await browser_agent.navigate(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
