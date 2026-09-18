import io
import re

from docx import Document as DocxDocument
from pypdf import PdfReader

ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "text/plain": "txt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


class UnsupportedFileTypeError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


class EmptyDocumentError(Exception):
    """Raised when extraction produced no usable text."""


def validate_upload(content_type: str, file_size: int) -> str:
    if file_size > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError(
            f"File exceeds the {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB limit."
        )
    kind = ALLOWED_CONTENT_TYPES.get(content_type)
    if kind is None:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{content_type}'. Allowed: PDF, TXT, DOCX."
        )
    return kind


def extract_pages(file_bytes: bytes, kind: str) -> list[tuple[int | None, str]]:
    """Returns (page_number, raw_text) pairs. page_number is None for
    formats without a natural page concept (txt, docx)."""
    if kind == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
    if kind == "docx":
        doc = DocxDocument(io.BytesIO(file_bytes))
        text = "\n".join(p.text for p in doc.paragraphs)
        return [(None, text)]
    if kind == "txt":
        text = file_bytes.decode("utf-8", errors="replace")
        return [(None, text)]
    raise UnsupportedFileTypeError(kind)


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end == length:
            break
        start = end - overlap
    return chunks


def build_chunks(pages: list[tuple[int | None, str]]) -> list[tuple[int | None, str]]:
    """Cleans and chunks each page's text, keeping page numbers attached
    so citations can point back to a specific page later (RAG feature)."""
    result: list[tuple[int | None, str]] = []
    for page_number, raw_text in pages:
        cleaned = clean_text(raw_text)
        for chunk in chunk_text(cleaned):
            result.append((page_number, chunk))
    return result
