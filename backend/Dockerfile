FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Modèle d'embedding téléchargé une fois pour toutes dans l'image : pas de
# téléchargement au démarrage (utile sur Render, dont le disque n'est pas persistant).
ENV EMBEDDING_CACHE_DIR=/opt/fastembed-cache
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('sentence-transformers/all-MiniLM-L6-v2', cache_dir='/opt/fastembed-cache')"

COPY . .

EXPOSE 8000

# PORT est fourni par l'hébergeur (Render : 10000 par défaut) ; 8000 en local.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
