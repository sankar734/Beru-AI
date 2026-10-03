"""NOVA X - Desktop File Intelligence & Local Indexer
Enforces strict workspace directory allowlists, path traversal protection,
and rapid local file indexing with search.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

DEFAULT_ALLOWED_ROOTS = [
    os.path.abspath(r"d:\5536\Projects\Beru"),
    os.path.abspath(r"d:\5536\Projects"),
]


class IndexedFileItem(BaseModel):
    filepath: str
    filename: str
    extension: str
    size_bytes: int
    modified_at: str
    is_dir: bool


class DesktopFileIndexer:
    """Manages secure indexing and search of approved local workspace files."""

    def __init__(self, allowed_roots: Optional[List[str]] = None):
        self.allowed_roots = [os.path.abspath(r) for r in (allowed_roots or DEFAULT_ALLOWED_ROOTS)]

    def is_path_allowed(self, target_path: str) -> bool:
        """Enforces path allowlist and protects against traversal attacks."""
        try:
            norm_target = os.path.abspath(target_path)
            # Case-insensitive comparison for Windows
            return any(
                norm_target.lower().startswith(root.lower())
                for root in self.allowed_roots
            )
        except Exception:
            return False

    def validate_path(self, target_path: str) -> str:
        """Validates path against security allowlist or raises PermissionError."""
        norm = os.path.abspath(target_path)
        if not self.is_path_allowed(norm):
            raise PermissionError(
                f"ACCESS_DENIED: Path '{target_path}' is outside approved workspace roots: {self.allowed_roots}"
            )
        return norm

    def index_directory(self, root_path: str, max_files: int = 100) -> List[IndexedFileItem]:
        """Indexes files within an approved directory."""
        validated_root = self.validate_path(root_path)
        indexed: List[IndexedFileItem] = []

        if not os.path.exists(validated_root):
            return []

        for root, dirs, files in os.walk(validated_root):
            # Skip hidden and cache folders
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "dist", "build")]

            for f in files:
                if len(indexed) >= max_files:
                    break
                full_path = os.path.join(root, f)
                try:
                    stat = os.stat(full_path)
                    ext = os.path.splitext(f)[1].lower()
                    mod_time = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
                    indexed.append(
                        IndexedFileItem(
                            filepath=full_path,
                            filename=f,
                            extension=ext,
                            size_bytes=stat.st_size,
                            modified_at=mod_time,
                            is_dir=False,
                        )
                    )
                except Exception:
                    continue

            if len(indexed) >= max_files:
                break

        return indexed

    def search_local_files(self, query: str, root_path: str, limit: int = 20) -> List[IndexedFileItem]:
        """Performs filename and content search within an approved directory."""
        all_files = self.index_directory(root_path, max_files=300)
        q_lower = query.lower()
        matches = []

        for item in all_files:
            # Filename match
            if q_lower in item.filename.lower():
                matches.append(item)
                if len(matches) >= limit:
                    break
                continue

            # Content match for text files
            if item.extension in (".py", ".ts", ".tsx", ".js", ".md", ".json", ".txt"):
                try:
                    with open(item.filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(4096)  # Read first 4KB
                        if q_lower in content.lower():
                            matches.append(item)
                            if len(matches) >= limit:
                                break
                except Exception:
                    pass

        return matches


# Global indexer instance
desktop_file_indexer = DesktopFileIndexer()
