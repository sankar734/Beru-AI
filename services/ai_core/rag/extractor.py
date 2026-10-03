import os
import csv
import json
from typing import Dict, Any, List

class DocumentExtractor:
    """Extracts raw textual content and metadata from multiple file formats."""

    @staticmethod
    def extract_text(file_path: str, mime_type: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Plain text, markdown, code, json
        if any(mime in mime_type for mime in ["text/", "json", "javascript", "python", "csv"]):
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    if "csv" in mime_type or file_path.endswith(".csv"):
                        # Format CSV as readable markdown table preview
                        lines = content.splitlines()
                        if lines:
                            reader = csv.reader(lines)
                            rows = list(reader)
                            if rows:
                                header = " | ".join(rows[0])
                                separator = " | ".join(["---"] * len(rows[0]))
                                body = "\n".join([" | ".join(r) for r in rows[1:50]])
                                return f"{header}\n{separator}\n{body}"
                    return content
            except Exception as e:
                return f"Error reading text file: {e}"

        # PDF fallback extraction
        if "pdf" in mime_type or file_path.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                pages_text = []
                for idx, page in enumerate(reader.pages):
                    txt = page.extract_text() or ""
                    pages_text.append(f"--- Page {idx + 1} ---\n{txt}")
                return "\n\n".join(pages_text)
            except Exception:
                # Basic string extraction if pypdf not present
                with open(file_path, "rb") as f:
                    raw = f.read()
                    # Filter printable characters
                    printable = bytes([b for b in raw if 32 <= b <= 126 or b in (10, 13)])
                    return printable.decode("latin1", errors="ignore")[:50000]

        return f"[Document {os.path.basename(file_path)} uploaded with MIME: {mime_type}]"

document_extractor = DocumentExtractor()
