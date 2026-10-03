import os
import ast
import uuid
import difflib
import logging
import subprocess
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("nova.developer.repo")

class FileChangeProposal(BaseModel):
    filepath: str
    original_content: str
    new_content: str
    diff: str = ""
    additions: int = 0
    deletions: int = 0
    syntax_valid: bool = True
    syntax_error: Optional[str] = None

class MultiFileProposal(BaseModel):
    proposal_id: str
    title: str
    description: str
    risk_level: int = 2  # Level 2 (Review) or Level 3 (Confirmation Required)
    status: str = "PENDING"  # PENDING, APPROVED, APPLIED, ROLLED_BACK, REJECTED
    changes: List[FileChangeProposal] = []
    created_at: float = Field(default_factory=lambda: 0.0)

class RepoService:
    """Repository Intelligence and Controlled Code Modification Engine."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or os.getcwd()
        self._staged_proposals: Dict[str, MultiFileProposal] = {}
        self._backups: Dict[str, Dict[str, str]] = {}  # proposal_id -> {filepath: original_content}

    def get_git_status(self) -> Dict[str, Any]:
        """Inspects current git branch, dirty status, and recent commits."""
        try:
            branch = subprocess.check_output(
                ["git", "branch", "--show-current"],
                cwd=self.workspace_root,
                stderr=subprocess.DEVNULL,
                text=True
            ).strip() or "master"
        except Exception:
            branch = "master"

        try:
            status_output = subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_root,
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            modified = []
            untracked = []
            if status_output:
                for line in status_output.splitlines():
                    if line.startswith("??"):
                        untracked.append(line[3:].strip())
                    else:
                        modified.append(line[3:].strip())
        except Exception:
            modified = []
            untracked = []

        try:
            log_output = subprocess.check_output(
                ["git", "log", "-n", "5", "--oneline"],
                cwd=self.workspace_root,
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            recent_commits = [c for c in log_output.splitlines() if c]
        except Exception:
            recent_commits = ["HEAD: initial setup"]

        return {
            "branch": branch,
            "is_clean": len(modified) == 0 and len(untracked) == 0,
            "modified_files": modified,
            "untracked_files": untracked,
            "recent_commits": recent_commits,
            "workspace_root": self.workspace_root
        }

    def generate_diff(self, original_text: str, new_text: str, filename: str = "file") -> Dict[str, Any]:
        """Generates unified diff lines with additions and deletions counts."""
        orig_lines = original_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)
        diff_lines = list(difflib.unified_diff(
            orig_lines,
            new_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}"
        ))
        diff_str = "".join(diff_lines)
        
        additions = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
        deletions = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))
        
        return {
            "diff": diff_str,
            "additions": additions,
            "deletions": deletions
        }

    def check_syntax(self, filepath: str, code: str) -> tuple[bool, Optional[str]]:
        """Validates syntax for Python files via AST parsing."""
        if filepath.endswith(".py"):
            try:
                ast.parse(code, filename=filepath)
                return True, None
            except SyntaxError as e:
                return False, f"SyntaxError at line {e.lineno}: {e.msg}"
        return True, None

    def stage_edit_proposal(self, title: str, description: str, files_changes: List[Dict[str, str]]) -> MultiFileProposal:
        """
        Prepares a safe multi-file edit proposal:
        files_changes: [{"filepath": "...", "new_content": "..."}]
        """
        import time
        proposal_id = f"prop_{uuid.uuid4().hex[:8]}"
        changes: List[FileChangeProposal] = []
        is_high_risk = len(files_changes) > 2

        for item in files_changes:
            rel_path = item["filepath"]
            full_path = os.path.normpath(os.path.join(self.workspace_root, rel_path))
            
            # Security boundary: Must stay inside workspace root
            if not full_path.startswith(os.path.normpath(self.workspace_root)):
                raise PermissionError(f"Path traversal detected: {rel_path} outside workspace")

            # High risk detection for critical files
            if any(crit in rel_path.lower() for crit in ["main.py", "database.py", "security", "package.json"]):
                is_high_risk = True

            original_content = ""
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        original_content = f.read()
                except Exception:
                    original_content = ""

            new_content = item.get("new_content", "")
            diff_info = self.generate_diff(original_content, new_content, rel_path)
            syntax_valid, syntax_err = self.check_syntax(rel_path, new_content)

            changes.append(FileChangeProposal(
                filepath=rel_path,
                original_content=original_content,
                new_content=new_content,
                diff=diff_info["diff"],
                additions=diff_info["additions"],
                deletions=diff_info["deletions"],
                syntax_valid=syntax_valid,
                syntax_error=syntax_err
            ))

        risk_level = 3 if is_high_risk else 2

        proposal = MultiFileProposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            risk_level=risk_level,
            status="PENDING",
            changes=changes,
            created_at=time.time()
        )

        self._staged_proposals[proposal_id] = proposal
        return proposal

    def apply_proposal(self, proposal_id: str, human_approved: bool = False) -> Dict[str, Any]:
        """Applies a staged proposal after verifying policy requirements."""
        if proposal_id not in self._staged_proposals:
            raise KeyError(f"Proposal {proposal_id} not found")

        proposal = self._staged_proposals[proposal_id]
        if proposal.risk_level >= 3 and not human_approved:
            return {
                "success": False,
                "status": "AWAITING_APPROVAL",
                "message": f"Proposal {proposal_id} requires explicit human authorization token (Risk Level {proposal.risk_level})."
            }

        # Backup prior contents
        backup_map: Dict[str, str] = {}
        for change in proposal.changes:
            backup_map[change.filepath] = change.original_content
        self._backups[proposal_id] = backup_map

        applied_files = []
        try:
            for change in proposal.changes:
                full_path = os.path.normpath(os.path.join(self.workspace_root, change.filepath))
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(change.new_content)
                applied_files.append(change.filepath)

            proposal.status = "APPLIED"
            return {
                "success": True,
                "status": "APPLIED",
                "proposal_id": proposal_id,
                "applied_files": applied_files,
                "message": f"Successfully applied changes to {len(applied_files)} files."
            }
        except Exception as e:
            # Rollback immediately on write error
            self.rollback_proposal(proposal_id)
            return {
                "success": False,
                "status": "ERROR_ROLLED_BACK",
                "message": f"Failed applying changes: {str(e)}. Rollback completed."
            }

    def rollback_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Restores original file snapshots from backup."""
        if proposal_id not in self._backups:
            raise KeyError(f"No backup found for proposal {proposal_id}")

        restored_files = []
        for rel_path, orig_content in self._backups[proposal_id].items():
            full_path = os.path.normpath(os.path.join(self.workspace_root, rel_path))
            try:
                if orig_content:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(orig_content)
                else:
                    if os.path.exists(full_path):
                        os.remove(full_path)
                restored_files.append(rel_path)
            except Exception as e:
                logger.error(f"Error rolling back {rel_path}: {e}")

        if proposal_id in self._staged_proposals:
            self._staged_proposals[proposal_id].status = "ROLLED_BACK"

        return {
            "success": True,
            "status": "ROLLED_BACK",
            "proposal_id": proposal_id,
            "restored_files": restored_files
        }

repo_service = RepoService()
