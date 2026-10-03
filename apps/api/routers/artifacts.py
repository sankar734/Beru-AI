"""NOVA X - Artifact Studio Router
Manages multi-format creative & engineering artifacts, version tracking, and diffing.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import difflib

from apps.api.database import db_manager, DatabaseManager
from apps.api.auth import get_optional_user
from apps.api.models.artifact import (
    ArtifactCreate,
    ArtifactUpdate,
    ArtifactResponse,
    ArtifactVersion,
    ArtifactDiffResponse,
)

router = APIRouter(prefix="/artifacts", tags=["NOVA Studio"])


DEFAULT_ARTIFACTS = [
    {
        "id": "art-webapp-analytics",
        "user_id": "default",
        "title": "Real-time Telemetry Dashboard",
        "type": "WEB_APP",
        "description": "Self-contained interactive canvas visualizer with live simulated metrics",
        "tags": ["dashboard", "html5", "telemetry"],
        "current_version": 1,
        "versions": [
            {
                "version": 1,
                "summary": "Initial release with SVG gauge charts",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "content": (
                    "<!DOCTYPE html>\n"
                    "<html>\n"
                    "<head>\n"
                    "  <style>\n"
                    "    body { font-family: monospace; background: #0b0f19; color: #38bdf8; padding: 20px; }\n"
                    "    .card { background: #131b2e; border: 1px solid #1e293b; border-radius: 12px; padding: 24px; max-width: 480px; }\n"
                    "    .bar { height: 12px; background: #1e293b; border-radius: 6px; overflow: hidden; margin-top: 8px; }\n"
                    "    .fill { height: 100%; width: 78%; background: linear-gradient(90deg, #38bdf8, #818cf8); border-radius: 6px; }\n"
                    "  </style>\n"
                    "</head>\n"
                    "<body>\n"
                    "  <div class='card'>\n"
                    "    <h2>NOVA X Telemetry Stream</h2>\n"
                    "    <p>System Load: <strong>78.4%</strong></p>\n"
                    "    <div class='bar'><div class='fill'></div></div>\n"
                    "    <p style='margin-top: 16px; color: #94a3b8; font-size: 12px;'>Nodes active: 4 / 4 | Latency: 1.2ms</p>\n"
                    "  </div>\n"
                    "</body>\n"
                    "</html>"
                ),
            }
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "art-diagram-arch",
        "user_id": "default",
        "title": "Zero-Trust Agent Security Architecture",
        "type": "DIAGRAM",
        "description": "Mermaid diagram illustrating the 5-layer Policy Barrier and OS Execution Sandbox",
        "tags": ["architecture", "mermaid", "security"],
        "current_version": 1,
        "versions": [
            {
                "version": 1,
                "summary": "Initial diagram specification",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "content": (
                    "graph TD\n"
                    "    User([User Request]) --> Agent[AI Agent Orchestrator]\n"
                    "    Agent --> ToolCall[Tool Proposal]\n"
                    "    ToolCall --> Policy{Policy Engine: Risk 0-4}\n"
                    "    Policy -- Level 0-2 Read-Only --> Sandbox[Isolated Execution]\n"
                    "    Policy -- Level 3-4 Consequential --> Barrier[[Human Confirmation Barrier]]\n"
                    "    Barrier -- Approved --> Sandbox\n"
                    "    Barrier -- Rejected --> Abort[Action Aborted]\n"
                    "    Sandbox --> Verify[State Verification Engine]\n"
                    "    Verify --> Feedback[User Feedback & Transcript Log]"
                ),
            }
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": "art-doc-spec",
        "user_id": "default",
        "title": "Unified RAG Engine Specification",
        "type": "DOCUMENT",
        "description": "Technical design doc explaining Dense Vector and BM25 Reciprocal Rank Fusion",
        "tags": ["design-doc", "rag", "search"],
        "current_version": 1,
        "versions": [
            {
                "version": 1,
                "summary": "Full design documentation",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "content": (
                    "# Unified Hybrid RAG Pipeline Specification\n\n"
                    "## 1. Overview\n"
                    "NOVA X employs a multi-stage retrieval architecture combining high-dimensional dense vector embeddings with lexical BM25 term matching.\n\n"
                    "## 2. Fusion Formulation\n"
                    "Rankings are merged via Reciprocal Rank Fusion (RRF):\n\n"
                    "$$RRF(d) = \\sum_{m \\in M} \\frac{1}{k + r_m(d)}$$\n\n"
                    "where $k = 60$ and $r_m(d)$ represents document rank in candidate list $m$."
                ),
            }
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
]


async def ensure_default_artifacts():
    col = db_manager.get_collection("artifacts")
    count = await col.count_documents({})
    if count == 0:
        for art in DEFAULT_ARTIFACTS:
            await col.insert_one(art)


@router.get("", response_model=List[ArtifactResponse])
async def list_artifacts(
    type: Optional[str] = None,
    tag: Optional[str] = None,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Lists artifacts accessible to the user, with optional type or tag filtering."""
    await ensure_default_artifacts()
    col = db_manager.get_collection("artifacts")
    query: Dict[str, Any] = {}
    if user:
        query["$or"] = [{"user_id": user["id"]}, {"user_id": "default"}]
    if type:
        query["type"] = type.upper()
    if tag:
        query["tags"] = tag

    results = await col.find(query)
    for r in results:
        r.pop("_id", None)
    return results


@router.post("", response_model=ArtifactResponse)
async def create_artifact(
    payload: ArtifactCreate,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Creates a new artifact with an initial version snapshot."""
    col = db_manager.get_collection("artifacts")
    now_iso = datetime.now(timezone.utc).isoformat()
    user_id = user["id"] if user else "default"

    artifact_id = f"art-{uuid.uuid4().hex[:10]}"
    initial_version = ArtifactVersion(
        version=1,
        content=payload.initial_content,
        summary="Initial version",
        created_at=now_iso,
    )

    doc = {
        "id": artifact_id,
        "user_id": user_id,
        "title": payload.title,
        "type": payload.type.upper(),
        "description": payload.description or "",
        "tags": payload.tags or [],
        "current_version": 1,
        "versions": [initial_version.model_dump()],
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    await col.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: str,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Retrieves an artifact by ID."""
    await ensure_default_artifacts()
    col = db_manager.get_collection("artifacts")
    art = await col.find_one({"id": artifact_id})
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found.")
    art.pop("_id", None)
    return art


@router.put("/{artifact_id}", response_model=ArtifactResponse)
async def update_artifact(
    artifact_id: str,
    payload: ArtifactUpdate,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Updates artifact metadata or appends a new version snapshot."""
    col = db_manager.get_collection("artifacts")
    art = await col.find_one({"id": artifact_id})
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found.")

    update_fields: Dict[str, Any] = {
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    if payload.title is not None:
        update_fields["title"] = payload.title
    if payload.description is not None:
        update_fields["description"] = payload.description
    if payload.tags is not None:
        update_fields["tags"] = payload.tags

    versions = art.get("versions", [])
    if payload.new_content is not None:
        new_v_num = len(versions) + 1
        new_v = ArtifactVersion(
            version=new_v_num,
            content=payload.new_content,
            summary=payload.version_summary or f"Version {new_v_num}",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        versions.append(new_v.model_dump())
        update_fields["versions"] = versions
        update_fields["current_version"] = new_v_num

    await col.update_one({"id": artifact_id}, {"$set": update_fields})
    updated_art = await col.find_one({"id": artifact_id})
    updated_art.pop("_id", None)
    return updated_art


@router.get("/{artifact_id}/diff", response_model=ArtifactDiffResponse)
async def get_artifact_diff(
    artifact_id: str,
    v1: int = Query(..., ge=1),
    v2: int = Query(..., ge=1),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Computes a unified line-by-line diff between two version snapshots of an artifact."""
    col = db_manager.get_collection("artifacts")
    art = await col.find_one({"id": artifact_id})
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found.")

    versions = art.get("versions", [])
    v1_doc = next((v for v in versions if v["version"] == v1), None)
    v2_doc = next((v for v in versions if v["version"] == v2), None)

    if not v1_doc or not v2_doc:
        raise HTTPException(status_code=400, detail="One or both version numbers do not exist.")

    v1_lines = v1_doc["content"].splitlines(keepends=True)
    v2_lines = v2_doc["content"].splitlines(keepends=True)

    diff = list(difflib.unified_diff(
        v1_lines,
        v2_lines,
        fromfile=f"v{v1}",
        tofile=f"v{v2}",
    ))

    return ArtifactDiffResponse(
        artifact_id=artifact_id,
        v1=v1,
        v2=v2,
        diff_lines=[line.rstrip("\r\n") for line in diff],
        has_changes=len(diff) > 0,
    )


@router.delete("/{artifact_id}")
async def delete_artifact(
    artifact_id: str,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    """Deletes an artifact."""
    col = db_manager.get_collection("artifacts")
    res = await col.delete_one({"id": artifact_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return {"status": "success", "message": f"Artifact {artifact_id} deleted."}
