import re
from typing import List
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    chunk_index: int
    text: str
    page_number: int = 1
    section_title: str = "General"
    word_count: int

class TextChunker:
    def __init__(self, chunk_size: int = 350, chunk_overlap: int = 60):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[DocumentChunk]:
        if not text or not text.strip():
            return []

        # Check for page markers
        pages = re.split(r"--- Page (\d+) ---", text)
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        if len(pages) > 1:
            # Check if there is preamble content before the first page marker (which is page 1)
            if pages[0].strip():
                preamble_chunks = self._chunk_single_text(pages[0], 1, start_idx=chunk_idx)
                chunks.extend(preamble_chunks)
                chunk_idx += len(preamble_chunks)

            current_page = 1
            i = 1
            while i < len(pages):
                current_page = int(pages[i])
                page_text = pages[i + 1] if i + 1 < len(pages) else ""
                i += 2
                page_chunks = self._chunk_single_text(page_text, current_page, start_idx=chunk_idx)
                chunks.extend(page_chunks)
                chunk_idx += len(page_chunks)
        else:
            chunks = self._chunk_single_text(text, 1, start_idx=0)

        return chunks

    def _chunk_single_text(self, text: str, page_number: int, start_idx: int) -> List[DocumentChunk]:
        words = text.split()
        if not words:
            return []

        chunks: List[DocumentChunk] = []
        i = 0
        current_idx = start_idx

        while i < len(words):
            chunk_words = words[i : i + self.chunk_size]
            chunk_content = " ".join(chunk_words)

            # Heuristic section detection
            section = "General"
            for line in chunk_content.splitlines():
                if line.startswith("# ") or line.startswith("## ") or line.endswith(":"):
                    section = line.strip("# :")[:40]
                    break

            chunks.append(DocumentChunk(
                chunk_index=current_idx,
                text=chunk_content,
                page_number=page_number,
                section_title=section,
                word_count=len(chunk_words)
            ))
            current_idx += 1

            if i + self.chunk_size >= len(words):
                break
            i += self.chunk_size - self.chunk_overlap

        return chunks

text_chunker = TextChunker()
