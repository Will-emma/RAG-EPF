from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Document, User
from app.db.models import Chunk
from app.rag.ingestion import chunk_pages, embed_texts, extract_pages
from app.schemas.document import DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension non autorisée: {ext}. Formats acceptés: {', '.join(settings.allowed_extensions_list)}",
        )

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux ({size_mb:.1f} Mo). Maximum: {settings.MAX_UPLOAD_SIZE_MB} Mo.",
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
    except Exception:
        document.status = "error"
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