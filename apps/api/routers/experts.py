"""NOVA X - Custom AI Experts Router
Manages specialized domain personas, consultation pipelines, and custom persona builders.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from apps.api.database import db_manager
from apps.api.auth import get_optional_user
from apps.api.models.expert import (
    ExpertCreate,
    ExpertUpdate,
    ExpertResponse,
    ExpertConsultRequest,
    ExpertConsultResponse,
)
from services.ai_core.registry import provider_registry
from services.ai_core.provider_base import ChatMessagePayload, ChatRole

router = APIRouter(prefix="/experts", tags=["AI Experts"])

DEFAULT_EXPERTS = [
    {
        "id": "exp-systems-arch",
        "user_id": "system",
        "is_system_default": True,
        "name": "Alex Vance",
        "role": "Principal Systems Architect",
        "avatar_icon": "Cpu",
        "color_theme": "cyan",
        "system_prompt": (
            "You are a world-class Principal Systems Architect with 25+ years designing distributed engines, "
            "fault-tolerant storage, and resilient zero-downtime platforms. Evaluate all problems through "
            "the lens of bounded contexts, backpressure, CAP guarantees, and high-concurrency throughput."
        ),
        "capabilities": ["Distributed Consensus", "Event Sourcing", "Zero-Downtime Migration", "Scale Bottlenecks"],
        "temperature": 0.2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "exp-security-audit",
        "user_id": "system",
        "is_system_default": True,
        "name": "Cipher Zero",
        "role": "Lead Security & Red Team Auditor",
        "avatar_icon": "ShieldAlert",
        "color_theme": "rose",
        "system_prompt": (
            "You are an elite offensive and defensive cybersecurity auditor. Rigorously inspect architectures "
            "for OWASP Top 10 vulnerabilities, supply chain vectors, privilege escalation, secret leakages, "
            "and cryptographic weaknesses. Always enforce zero-trust policies and state verifications."
        ),
        "capabilities": ["Threat Modeling", "Zero-Trust Enforcement", "Cryptographic Review", "Penetration Vectors"],
        "temperature": 0.1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "exp-perf-eng",
        "user_id": "system",
        "is_system_default": True,
        "name": "Elena Rostova",
        "role": "Full-Stack Performance Engineer",
        "avatar_icon": "Zap",
        "color_theme": "amber",
        "system_prompt": (
            "You are a dedicated Performance and Profiling Engineer. You optimize Web Vitals, React render passes, "
            "database indexing, query planning, memory allocations, and network packet overhead. Identify sub-millisecond "
            "inefficiencies and recommend measurable micro-optimizations."
        ),
        "capabilities": ["React Profiling", "SQL Query Optimization", "Memory Leak Tracing", "Sub-100ms Latency"],
        "temperature": 0.3,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "exp-ml-research",
        "user_id": "system",
        "is_system_default": True,
        "name": "Dr. Aris Thorne",
        "role": "AI/ML Research Scientist",
        "avatar_icon": "Brain",
        "color_theme": "purple",
        "system_prompt": (
            "You are a senior AI research scientist specializing in transformer mechanics, multi-vector RAG, "
            "test-time compute scaling, and autonomous multi-agent coordination. Ground your advice in peer-reviewed "
            "empirical findings and rigorous evaluation benchmarks."
        ),
        "capabilities": ["Hybrid Vector Search", "Attention Mechanics", "Evaluation Benchmarks", "Fine-Tuning"],
        "temperature": 0.4,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
]


async def ensure_default_experts():
    col = db_manager.get_collection("experts")
    count = await col.count_documents({})
    if count == 0:
        for exp in DEFAULT_EXPERTS:
            await col.insert_one(exp)


@router.get("", response_model=List[ExpertResponse])
async def list_experts(
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Lists all available AI experts, including system defaults and user-created specialists."""
    await ensure_default_experts()
    col = db_manager.get_collection("experts")
    user_id = user["id"] if user else "default"
    docs = await col.find({"$or": [{"user_id": user_id}, {"user_id": "system"}, {"user_id": "default"}]})
    for d in docs:
        d.pop("_id", None)
    return docs


@router.post("", response_model=ExpertResponse)
async def create_expert(
    payload: ExpertCreate,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Creates a new personalized AI expert specialist."""
    col = db_manager.get_collection("experts")
    user_id = user["id"] if user else "default"
    expert_id = f"exp-{uuid.uuid4().hex[:8]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    doc = {
        "id": expert_id,
        "user_id": user_id,
        "is_system_default": False,
        "name": payload.name,
        "role": payload.role,
        "avatar_icon": payload.avatar_icon,
        "color_theme": payload.color_theme,
        "system_prompt": payload.system_prompt,
        "capabilities": payload.capabilities,
        "temperature": payload.temperature,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    await col.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/{expert_id}", response_model=ExpertResponse)
async def get_expert(
    expert_id: str,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Retrieves an expert by ID."""
    await ensure_default_experts()
    col = db_manager.get_collection("experts")
    doc = await col.find_one({"id": expert_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Expert not found.")
    doc.pop("_id", None)
    return doc


@router.put("/{expert_id}", response_model=ExpertResponse)
async def update_expert(
    expert_id: str,
    payload: ExpertUpdate,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Updates an existing expert specialist."""
    col = db_manager.get_collection("experts")
    doc = await col.find_one({"id": expert_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Expert not found.")

    if doc.get("is_system_default") and not user:
        raise HTTPException(status_code=403, detail="Cannot mutate default system experts.")

    update_dict: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    for k, v in payload.model_dump(exclude_unset=True).items():
        if v is not None:
            update_dict[k] = v

    await col.update_one({"id": expert_id}, {"$set": update_dict})
    updated = await col.find_one({"id": expert_id})
    updated.pop("_id", None)
    return updated


@router.delete("/{expert_id}")
async def delete_expert(
    expert_id: str,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Deletes a custom expert."""
    col = db_manager.get_collection("experts")
    doc = await col.find_one({"id": expert_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Expert not found.")
    if doc.get("is_system_default"):
        raise HTTPException(status_code=400, detail="Cannot delete default system specialists.")

    await col.delete_one({"id": expert_id})
    return {"status": "success", "message": f"Expert {expert_id} deleted."}


@router.post("/{expert_id}/consult", response_model=ExpertConsultResponse)
async def consult_expert(
    expert_id: str,
    req: ExpertConsultRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Conducts a structured advisory consultation with a specialist persona."""
    await ensure_default_experts()
    col = db_manager.get_collection("experts")
    expert = await col.find_one({"id": expert_id})
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found.")

    provider = provider_registry.get_provider()
    tokens = []
    async for chunk in provider.chat_stream(
        messages=[
            ChatMessagePayload(role=ChatRole.SYSTEM, content=expert["system_prompt"]),
            ChatMessagePayload(role=ChatRole.USER, content=f"Topic / Problem:\n{req.query}\n\nContext:\n{req.context or 'None'}"),
        ],
        temperature=expert.get("temperature", 0.3),
    ):
        if chunk.token:
            tokens.append(chunk.token)
    llm_content = "".join(tokens)

    advice_text = (
        f"[{expert['name']} — {expert['role']}]\n\n"
        f"{llm_content}\n\n"
        f"Key Assessment for '{req.query}':\n"
        f"From the perspective of {expert['role']}, the critical factor is maintaining strict architectural invariants "
        f"and verifying every state change before committing to permanent storage."
    )

    recommendations = [
        f"Apply {expert['capabilities'][0] if expert.get('capabilities') else 'System Verification'} immediately.",
        "Profile latency and memory footprint under 5x peak load.",
        "Add automated end-to-end regression guardrails.",
    ]

    followups = [
        "How would this architecture behave during network partition?",
        "What are the fallback mechanisms if external dependencies fail?",
    ]

    return ExpertConsultResponse(
        expert_id=expert["id"],
        expert_name=expert["name"],
        role=expert["role"],
        consultation_response=advice_text,
        key_recommendations=recommendations,
        suggested_followups=followups,
    )
