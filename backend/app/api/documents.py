from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.schemas.document import DocumentDetail, DocumentSummary
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path(__file__).resolve().parents[3] / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=DocumentDetail, status_code=201)
async def upload_document(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> Document:
    file_bytes = await file.read()

    try:
        kind = document_service.validate_upload(file.content_type, len(file_bytes))
    except document_service.FileTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except document_service.UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    document = Document(
        filename=file.filename,
        content_type=file.content_type,
        file_size_bytes=len(file_bytes),
        status=DocumentStatus.PROCESSING,
    )
    db.add(document)
    db.flush()

    (UPLOAD_DIR / f"{document.id}_{file.filename}").write_bytes(file_bytes)

    try:
        pages = document_service.extract_pages(file_bytes, kind)
        chunk_rows = document_service.build_chunks(pages)
        if not chunk_rows:
            raise document_service.EmptyDocumentError(
                "No extractable text was found in this document."
            )
        for index, (page_number, content) in enumerate(chunk_rows):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    page_number=page_number,
                )
            )
        document.status = DocumentStatus.READY
    except document_service.EmptyDocumentError as exc:
        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)
    except Exception as exc:
        # Uploaded files are untrusted input — a corrupt/malformed PDF or
        # DOCX can raise all sorts of library-specific errors. Record the
        # failure on the document rather than 500ing the whole request.
        document.status = DocumentStatus.FAILED
        document.error_message = f"Failed to process document: {exc}"

    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentSummary])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    stmt = select(Document).order_by(Document.created_at.desc())
    return list(db.scalars(stmt))


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()

    for path in UPLOAD_DIR.glob(f"{document_id}_*"):
        path.unlink(missing_ok=True)
