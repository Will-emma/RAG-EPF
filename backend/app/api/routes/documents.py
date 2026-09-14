"""
TICKET: BACK-2 Upload & pipeline d'ingestion des cours
À compléter : validation du fichier (extension, taille), sauvegarde,
extraction texte (PyMuPDF/python-pptx/python-docx), chunking, embeddings,
insertion dans `chunks` avec pgvector.
"""
from fastapi import APIRouter, UploadFile, File

from app.core.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    if ext not in settings.allowed_extensions_list:
        raise ValueError(f"Extension non autorisée: {ext}")
    # TODO: limiter la taille (settings.MAX_UPLOAD_SIZE_MB), sauvegarder le
    # fichier, créer un Document(status="uploaded"), lancer le pipeline
    # d'ingestion (idéalement en tâche de fond / worker).
    raise NotImplementedError


@router.get("/")
async def list_documents():
    # TODO: lister les documents de l'utilisateur courant (isolation !).
    raise NotImplementedError
