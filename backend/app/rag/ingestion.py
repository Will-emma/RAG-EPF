from pathlib import Path

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from pptx import Presentation
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from app.core.config import settings

_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedding_model


def extract_pages(file_path: Path) -> list[tuple[int, str]]:
    """Renvoie une liste de (numéro_de_page, texte) selon le type de fichier."""
    ext = file_path.suffix.lower()

    if ext == ".pdf":
        pages = []
        with fitz.open(file_path) as doc:
            for i, page in enumerate(doc, start=1):
                text = page.get_text()
                if text.strip():
                    pages.append((i, text))
        return pages

    if ext == ".pptx":
        prs = Presentation(file_path)
        pages = []
        for i, slide in enumerate(prs.slides, start=1):
            texts = [
                shape.text_frame.text
                for shape in slide.shapes
                if shape.has_text_frame
            ]
            content = "\n".join(t for t in texts if t.strip())
            if content.strip():
                pages.append((i, content))
        return pages

    if ext == ".docx":
        doc = DocxDocument(file_path)
        content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [(1, content)] if content.strip() else []

    raise ValueError(f"Format non supporté: {ext}")


def chunk_pages(
    pages: list[tuple[int, str]], chunk_size: int = 800, chunk_overlap: int = 100
) -> list[tuple[int, str]]:
    """Découpe chaque page en chunks, en conservant le numéro de page."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = []
    for page_number, text in pages:
        for piece in splitter.split_text(text):
            chunks.append((page_number, piece))
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()