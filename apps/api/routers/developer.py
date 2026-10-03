import logging
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from apps.api.auth import get_optional_user
from services.developer.supervisor import dev_supervisor, SupervisedService
from services.developer.repo_service import repo_service, MultiFileProposal
from services.developer.diagnostics import diagnostics_engine, DiagnosticReport, TestRunResult

logger = logging.getLogger("nova.api.developer")

router = APIRouter(prefix="/developer", tags=["Developer Agent & Supervisor"])

# Request / Response Schemas
class RestartServiceRequest(BaseModel):
    service_id: str

class DiffRequest(BaseModel):
    original_text: str = ""
    new_text: str = ""
    filename: str = "file.py"

class DiffResponse(BaseModel):
    diff: str
    additions: int
    deletions: int

class ProposeEditRequest(BaseModel):
    title: str
    description: str
    changes: List[Dict[str, str]]  # [{"filepath": "...", "new_content": "..."}]

class ApplyProposalRequest(BaseModel):
    proposal_id: str
    human_approved: bool = False
    authorization_token: Optional[str] = None

class RollbackProposalRequest(BaseModel):
    proposal_id: str

class DiagnoseRequest(BaseModel):
    log_text: str

class RunTestsRequest(BaseModel):
    test_target: str = "tests/test_phase0.py"
    timeout: int = 20

@router.get("/services", response_model=List[SupervisedService])
async def list_services(user: Optional[dict] = Depends(get_optional_user)):
    """Lists all monitored developer services and process statuses."""
    return dev_supervisor.list_services()

@router.post("/services/{service_id}/restart", response_model=SupervisedService)
async def restart_service(service_id: str, user: Optional[dict] = Depends(get_optional_user)):
    """Restarts a supervised development service."""
    try:
        return dev_supervisor.restart_service(service_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found")

@router.get("/services/{service_id}/logs")
async def get_service_logs(service_id: str, limit: int = 50, user: Optional[dict] = Depends(get_optional_user)):
    """Retrieves recent log buffer for a service."""
    logs = dev_supervisor.get_logs(service_id, limit=limit)
    return {"service_id": service_id, "logs": logs}

@router.get("/git/status")
async def get_git_status(user: Optional[dict] = Depends(get_optional_user)):
    """Returns repository git status, current branch, and recent commits."""
    return repo_service.get_git_status()

@router.post("/diff", response_model=DiffResponse)
async def calculate_diff(req: DiffRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Calculates unified diff between original and modified text."""
    res = repo_service.generate_diff(req.original_text, req.new_text, req.filename)
    return DiffResponse(**res)

@router.post("/propose-edit", response_model=MultiFileProposal)
async def propose_edit(req: ProposeEditRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Stages a multi-file edit proposal with AST syntax validation and risk assessment."""
    try:
        proposal = repo_service.stage_edit_proposal(req.title, req.description, req.changes)
        return proposal
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/apply-proposal")
async def apply_proposal(req: ApplyProposalRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Applies a staged proposal with policy checks for Risk Level >= 3."""
    try:
        res = repo_service.apply_proposal(req.proposal_id, human_approved=req.human_approved)
        if not res.get("success") and res.get("status") == "AWAITING_APPROVAL":
            raise HTTPException(status_code=403, detail=res["message"])
        return res
    except KeyError:
        raise HTTPException(status_code=404, detail="Proposal not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollback-proposal")
async def rollback_proposal(req: RollbackProposalRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Rolls back applied changes from backup snapshots."""
    try:
        return repo_service.rollback_proposal(req.proposal_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="No backup found for this proposal")

@router.post("/diagnose", response_model=DiagnosticReport)
async def diagnose_error(req: DiagnoseRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Analyzes error tracebacks or build logs to identify root cause and recommendations."""
    return diagnostics_engine.diagnose_traceback(req.log_text)

@router.post("/run-tests", response_model=TestRunResult)
async def run_sandboxed_tests(req: RunTestsRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Runs a sandboxed pytest suite and returns structured test results."""
    return diagnostics_engine.run_tests_sandboxed(target=req.test_target, timeout=req.timeout)

