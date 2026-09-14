# Architecture cible

Reprise du schéma validé avec le groupe (proposé par une IA, à justifier et
adapter pendant le hackathon) :

- **Frontend** : Angular — pages Accueil, Mes cours, Chat IA, Révision/QCM,
  Historique, Profil. Chat avec les cours, upload PDF/PPTX/DOCX, affichage
  des sources (cours + page), interface responsive.
- **Backend** : FastAPI (Python)
  - Authentification JWT (inscription/connexion, sécurisation des endpoints)
  - Gestion des documents (upload, validation, stockage, suivi de traitement)
  - Service RAG (recherche vectorielle, construction du contexte, appel LLM)
  - Service Agent (orchestration des tâches, génération de QCM, évaluation)
  - API REST versionnée, doc OpenAPI auto, gestion des erreurs
- **Pipeline d'ingestion** : extraction texte (PyMuPDF/python-pptx/python-docx)
  → découpage en chunks (LangChain Text Splitter, taille/overlap + métadonnées
  page/cours) → embeddings (sentence-transformers local, ou API Mistral si
  quota) → stockage vectoriel (PostgreSQL + pgvector)
- **Base de données** : PostgreSQL + pgvector — documents, chunks, embeddings,
  utilisateurs, historique/QCM
- **LLM** : Z.AI GLM-5.3-Flash, clé API côté backend uniquement (`.env`,
  jamais côté frontend), appels via HTTPS
- **Study Agent (LangGraph)** : identifier le cours/chapitre → interroger le
  RAG → générer une question (GLM) → évaluer la réponse → expliquer/adapter
  la suite
- **Hébergement** : Vercel (frontend), Render (backend) — alternative
  Azure/GCP/AWS avec les crédits gratuits fournis pour le hackathon
- **Sécurité** : JWT, clé API côté backend, validation des fichiers (type +
  taille), isolation des données par utilisateur, logs/monitoring
- **Méthodologie** : Agile sur GitHub — issues/backlog, branches
  `feature/*`, Pull Requests + code review obligatoires, GitHub Actions (CI),
  tests automatisés (Pytest + Angular)

## Points à trancher en Sprint 0 (choix à documenter et justifier)

1. Embeddings locaux (sentence-transformers, gratuit, mais CPU) vs API
   Mistral (quota gratuit limité) — recommandé : **local** pour ne pas
   dépendre d'un quota externe pendant la démo.
2. Stockage vectoriel : pgvector (déjà dans le schéma, simple à héberger avec
   Postgres) plutôt qu'une base vectorielle dédiée (Chroma) pour limiter le
   nombre de services à déployer.
3. Frontière RAG vs Agent : le Service RAG expose une fonction de recherche +
   génération réutilisable ; le Study Agent (LangGraph) l'appelle comme un
   outil pour construire le mode révision/QCM, il ne duplique pas la logique
   de recherche.
4. Isolation utilisateurs : chaque document/chunk est rattaché à un
   `owner_id`, toutes les requêtes de lecture filtrent dessus (cf. SEC-1).
