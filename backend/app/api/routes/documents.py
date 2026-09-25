import io
import logging
import uuid
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Chunk, Document, User
from app.rag.ingestion import chunk_pages, embed_texts, extract_pages
from app.schemas.document import DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

EXTENSION_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def detect_document_mime(contents: bytes) -> str | None:
    """Detect the supported document type from its signature or OOXML package structure."""
    if b"%PDF-" in contents[:1024]:
        return EXTENSION_MIME_TYPES[".pdf"]

    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as archive:
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names:
                return None
            if archive.getinfo("[Content_Types].xml").file_size > 128 * 1024:
                return None
            content_types = archive.read("[Content_Types].xml").lower()
    except (zipfile.BadZipFile, KeyError, OSError, ValueError):
        return None

    if (
        "word/document.xml" in names
        and b"wordprocessingml.document.main+xml" in content_types
    ):
        return EXTENSION_MIME_TYPES[".docx"]
    if (
        "ppt/presentation.xml" in names
        and b"presentationml.presentation.main+xml" in content_types
    ):
        return EXTENSION_MIME_TYPES[".pptx"]
    return None

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    course_name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.allowed_extensions_list:
        logger.warning("Rejected document upload: unsupported extension")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension non autorisée: {ext}. Formats acceptés: {', '.join(settings.allowed_extensions_list)}",
        )

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        logger.warning("Rejected document upload: file size limit exceeded")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux ({size_mb:.1f} Mo). Maximum: {settings.MAX_UPLOAD_SIZE_MB} Mo.",
        )

    expected_mime = EXTENSION_MIME_TYPES.get(ext)
    detected_mime = detect_document_mime(contents)
    if expected_mime is None or detected_mime != expected_mime:
        logger.warning(
            "Rejected document upload: content does not match extension (extension=%s, detected_mime=%s)",
            ext,
            detected_mime or "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le contenu du fichier ne correspond pas à son extension.",
        )

    document = Document(
        owner_id=current_user.id,
        filename=file.filename,
        course_name=course_name,
        status="uploaded",
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    stored_filename = f"{document.id}{ext}"
    file_path = UPLOAD_DIR / stored_filename
    with open(file_path, "wb") as f:
        f.write(contents)

    document.status = "processing"
    await db.commit()

    try:
        pages = extract_pages(file_path)
        chunks = chunk_pages(pages)
        if chunks:
            texts = [text for _, text in chunks]
            embeddings = embed_texts(texts)
            for (page_number, text), embedding in zip(chunks, embeddings):
                db.add(
                    Chunk(
                        document_id=document.id,
                        content=text,
                        page_number=page_number,
                        embedding=embedding,
                    )
                )
        document.status = "ready"
    except Exception as exc:
        document.status = "error"
        logger.error(
            "Document processing failed (document_id=%s, error_type=%s)",
            document.id,
            type(exc).__name__,
        )
    finally:
        await db.commit()
        await db.refresh(document)

    return document


@router.get("/", response_model=list[DocumentOut])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document)
        .where(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Supprime un document de l'utilisateur, ses chunks (le chat et le QCM ne
    l'utilisent plus) et le fichier stocké. L'historique du chat est conservé."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.owner_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable.")

    await db.execute(delete(Chunk).where(Chunk.document_id == document.id))
    await db.execute(delete(Document).where(Document.id == document.id))
    await db.commit()

    # Le fichier est stocké sous "<id>.<extension>" (voir upload_document)
    for stored_file in UPLOAD_DIR.glob(f"{document_id}.*"):
        stored_file.unlink(missing_ok=True)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
