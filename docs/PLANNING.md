# Planning agile — 2 semaines (14/09/2026 → 28/09/2026)

Contraintes imposées par le cours :
- Dernier commit + lien démo + supports envoyés sur Discord : **dimanche
  27/09, 23h59** (pénalité en cas de retard)
- Soutenance avec évaluation : **lundi 28/09**
- Travail en équipe agile obligatoire : planification, spécifications,
  tickets, critères d'acceptance, PR, validation
- L'application doit avoir une brique IA générative et/ou agentique
- Si usage d'un harness IA (Claude Code, Codex...), usage d'un framework
  agentique (spec-kit, BMAD...) attendu — pas de "vibe coding" pur

## Répartition des rôles (4 membres)

| Rôle | Périmètre principal |
|---|---|
| **Dev Backend & Auth** | FastAPI, base de données, authentification JWT, sécurité API, endpoints documents |
| **Dev Backend & RAG** | Pipeline d'ingestion (extraction/chunking/embeddings), service RAG (recherche + prompt + appel LLM) |
| **Dev Frontend Angular** | Toutes les pages/écrans, intégration API, UX, responsive |
| **Dev Agent & DevOps** | Study Agent LangGraph (mode révision/QCM), Docker, CI/CD, déploiement, monitoring |

La revue de code croise les rôles (jamais l'auteur qui approuve sa propre
PR). Un membre "scrum master" tournant anime le daily de 10 min (peut être
la même personne toute la durée si le groupe préfère).

## Sprint 0 — Kickoff (lundi 14/09)

- Choix définitif du sujet (fait : RAG cours EPF) et de la stack (validée,
  voir `docs/ARCHITECTURE.md`)
- Création des comptes : cloud provider (Azure/GCP/AWS crédits gratuits),
  Vercel, Render, récupération de la clé API Z.AI
- Mise en place de l'environnement (ce scaffold), push initial sur le repo
  GitHub du groupe
- Création du backlog complet en issues GitHub (`docs/BACKLOG.md`)
- Répartition des rôles + tickets du Sprint 1

## Sprint 1 — Fondations (mar 15/09 → ven 18/09)

Objectif : avoir un squelette qui tourne de bout en bout (auth + upload +
stockage, même sans intelligence encore).

- SETUP-1, BACK-1 (auth), BACK-2 (upload + pipeline ingestion), FRONT-1
  (skeleton Angular + routing + layout), DEVOPS-1 (CI de base)
- Weekend 19-20/09 : temps tampon / rattrapage, pas de nouveau ticket lancé
  sans avoir fini le sprint

**Démo de fin de sprint (interne)** : un fichier de cours uploadé est bien
découpé en chunks avec embeddings stockés en base (vérifiable dans Adminer).

## Sprint 2 — Cœur RAG + Chat (lun 21/09 → jeu 24/09)

- RAG-1 (recherche vectorielle top-K), RAG-2 (construction contexte + appel
  Z.AI), FRONT-2 (page Chat IA connectée), FRONT-3 (upload de documents côté
  UI), AGENT-1 (squelette LangGraph du Study Agent)

**Démo de fin de sprint (interne)** : je pose une question sur un cours
uploadé, je reçois une réponse avec les sources (cours + page).

## Sprint 3 — Agent, sécurité, finitions (ven 25/09 → dim 27/09 12h)

- AGENT-2 (génération QCM + évaluation), FRONT-4 (mode révision/QCM),
  FRONT-5 (historique), SEC-1 (isolation utilisateurs + validation fichiers),
  TEST-1 (tests backend), TEST-2 (tests frontend), DEVOPS-2 (déploiement
  Vercel + Render)

## Freeze & Démo (dim 27/09 12h → 23h59)

- Plus de nouvelle fonctionnalité : uniquement bugfix, polish UX, README
- DOC-1 (README + justification des choix d'architecture pour la
  soutenance), DOC-2 (script de démo + slides)
- Vérifier le lien de démo déployé + dernier commit avant 23h59
- Envoyer les liens + supports sur le Discord du hackathon

## Lundi 28/09 — Soutenance

- Répétition rapide le matin (15 min), répartition de la parole entre les 4
  membres (chacun doit pouvoir justifier son code et ses choix)
- Grille d'évaluation à garder en tête pendant la présentation (4 points
  chacun) : qualité du code, qualité de l'architecture (perf/coût/sécurité,
  penser "produit" au-delà du POC), qualité UX, qualité de la présentation/
  créativité, note du public
