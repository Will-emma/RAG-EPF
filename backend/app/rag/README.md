# Module RAG / Agent

Ce dossier est le point d'entrée logique pour :

- `ingestion.py` (BACK-2) : extraction de texte (PyMuPDF/python-pptx/python-docx),
  découpage en chunks (LangChain Text Splitter), génération d'embeddings
  (sentence-transformers), écriture en base.
- `retrieval.py` (BACK-3) : recherche vectorielle top-K dans `chunks`, construction
  du contexte pour le prompt.
- `llm_client.py` (BACK-3) : client HTTP vers l'API Z.AI (GLM-5.3-Flash), à
  garder isolé pour pouvoir switcher de fournisseur facilement.
- `study_agent.py` (AGENT-1/AGENT-2) : graphe LangGraph du Study Agent
  (identifier le cours/chapitre → interroger le RAG → générer une question →
  évaluer la réponse → adapter la suite), cf. schéma d'architecture.

Un seul membre ne doit pas porter tout ce dossier : BACK-2/BACK-3 sont sur le
binôme Backend/RAG, AGENT-1/AGENT-2 sur le membre Agent/DevOps, en s'appuyant
sur les fonctions de retrieval déjà exposées.
