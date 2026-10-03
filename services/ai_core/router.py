from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class RouteRequest(BaseModel):
    query: str
    mode: Optional[str] = "AUTO"
    has_attachments: bool = False
    attachment_types: Optional[List[str]] = None
    privacy_level: str = "standard"  # standard, high, local_only
    latency_preference: str = "normal"  # low, normal
    cost_preference: str = "balanced"  # low, balanced, high_performance

class RouteResult(BaseModel):
    selected_provider: str
    selected_model: str
    pipeline: str
    requires_tools: List[str]
    reasoning: str

class IntelligenceRouter:
    """NOVA Intelligence Router: Analyzes intent, constraints, and routes to the optimal model pipeline."""
    
    def route(self, request: RouteRequest) -> RouteResult:
        query_lower = request.query.lower()
        mode = (request.mode or "AUTO").upper()

        # Rule 1: Privacy constraint overrides all
        if request.privacy_level == "local_only":
            return RouteResult(
                selected_provider="local",
                selected_model="llama3:latest",
                pipeline="local_offline",
                requires_tools=[],
                reasoning="Privacy preference is set to local_only. Bypassing cloud providers."
            )

        # Rule 2: Vision / Image attachments require Vision capability
        if request.has_attachments and request.attachment_types:
            img_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
            if any(t in img_types for t in request.attachment_types) or "screenshot" in query_lower:
                return RouteResult(
                    selected_provider="openai",
                    selected_model="gpt-4o",
                    pipeline="vision_multimodal",
                    requires_tools=["screen_ocr", "image_analyzer"],
                    reasoning="Image attachment detected. Routed to high-fidelity multimodal vision model."
                )

        # Rule 3: Explicit Mode Matching
        if mode == "CODE" or any(kw in query_lower for kw in ["def ", "class ", "function", "refactor", "debug", "python", "typescript", "npm "]):
            return RouteResult(
                selected_provider="anthropic",
                selected_model="claude-3-5-sonnet-20241022",
                pipeline="code_specialist",
                requires_tools=["code_runner", "file_reader"],
                reasoning="Coding request identified. Routed to Claude 3.5 Sonnet code reasoning pipeline."
            )

        if mode == "RESEARCH" or "deep research" in query_lower or "literature review" in query_lower:
            return RouteResult(
                selected_provider="openai",
                selected_model="o3-mini",
                pipeline="deep_research_tree",
                requires_tools=["search_web", "scraper", "fact_checker", "citation_verifier"],
                reasoning="Deep Research mode active. Routed to iterative reasoning tree pipeline."
            )

        if mode == "SEARCH" or any(kw in query_lower for kw in ["latest news", "current price", "today", "weather", "who is the current"]):
            return RouteResult(
                selected_provider="google",
                selected_model="gemini-2.0-flash",
                pipeline="grounded_search",
                requires_tools=["search_web", "page_reader", "citation_verifier"],
                reasoning="Live web search required. Routed to low-latency Gemini 2.0 grounded search pipeline."
            )

        if mode == "THINK" or any(kw in query_lower for kw in ["prove", "theorem", "step by step", "complex architecture"]):
            return RouteResult(
                selected_provider="anthropic",
                selected_model="claude-3-7-sonnet",
                pipeline="extended_reasoning",
                requires_tools=[],
                reasoning="Extended reasoning required. Routed to deep thinking reasoning pipeline."
            )

        if mode == "QUICK" or request.latency_preference == "low":
            return RouteResult(
                selected_provider="google",
                selected_model="gemini-2.0-flash",
                pipeline="quick_response",
                requires_tools=[],
                reasoning="Low-latency fast answer requested. Routed to fast lightweight model."
            )

        # Default AUTO balanced route
        return RouteResult(
            selected_provider="openai",
            selected_model="gpt-4o",
            pipeline="general_chat",
            requires_tools=[],
            reasoning="Balanced conversational request. Routed to default standard model."
        )

intelligence_router = IntelligenceRouter()

def get_intelligence_router() -> IntelligenceRouter:
    return intelligence_router
