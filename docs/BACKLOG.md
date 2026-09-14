# Backlog agile — EPF Study AI

Chaque ticket est prêt à être copié en issue GitHub (ou importé via
`scripts/create_github_issues.sh`, voir plus bas). Format : ID, rôle, sprint,
user story, critères d'acceptance.

Labels suggérés à créer dans le repo : `sprint-0`, `sprint-1`, `sprint-2`,
`sprint-3`, `backend`, `frontend`, `agent-devops`, `security`, `docs`.

---

## Sprint 0 — Kickoff

### SETUP-1 — Mettre en place l'environnement de développement
**Rôle** : tous (piloté par 1 personne)
**Story** : En tant qu'équipe, je veux un environnement reproductible pour
que chacun puisse lancer le projet en local en moins de 10 minutes.
**Acceptance**
- [ ] `docker compose up` lance la base Postgres+pgvector et le backend sans erreur
- [ ] `.env.example` documenté, chacun a son `.env` local (non commité)
- [ ] Le frontend Angular est généré et démarre avec `npm start`
- [ ] `GET /health` répond 200 depuis le frontend (CORS OK)
- [ ] README à jour avec les commandes de démarrage

### SETUP-2 — Créer le backlog et les tickets GitHub
**Rôle** : scrum master tournant
**Story** : En tant qu'équipe, je veux un backlog GitHub avec labels et
milestones pour suivre l'avancement pendant les 2 semaines.
**Acceptance**
- [ ] Tous les tickets ci-dessous créés en issues avec labels sprint/rôle
- [ ] 3 milestones créés (Sprint 1, Sprint 2, Sprint 3) avec dates
- [ ] Un board GitHub Projects (To Do / In Progress / Done) lié aux issues

---

## Sprint 1 — Fondations

### BACK-1 — Authentification JWT
**Rôle** : Backend & Auth
**Story** : En tant qu'utilisateur, je veux m'inscrire et me connecter pour
accéder à mes cours et mon historique en toute sécurité.
**Acceptance**
- [ ] `POST /api/auth/register` crée un utilisateur (mot de passe hashé bcrypt)
- [ ] `POST /api/auth/login` renvoie un token JWT valide
- [ ] Une dépendance `get_current_user` protège les endpoints sensibles
- [ ] Erreurs claires (email déjà pris, mauvais mot de passe) avec codes HTTP corrects

### BACK-2 — Upload et pipeline d'ingestion des documents
**Rôle** : Backend & RAG
**Story** : En tant qu'étudiant, je veux importer un cours (PDF/PPTX/DOCX)
pour que son contenu soit exploitable par le chat.
**Acceptance**
- [ ] `POST /api/documents/upload` valide type et taille (`.env`), rejette le reste avec message clair
- [ ] Extraction du texte pour les 3 formats (PyMuPDF, python-pptx, python-docx)
- [ ] Découpage en chunks avec métadonnées (page, cours) via LangChain Text Splitter
- [ ] Génération d'embeddings (sentence-transformers) et stockage dans `chunks` (pgvector)
- [ ] Le statut du document passe `uploaded → processing → ready` (ou `error`)

### FRONT-1 — Squelette de l'application Angular
**Rôle** : Frontend
**Story** : En tant qu'utilisateur, je veux naviguer entre les pages
principales (Accueil, Mes cours, Chat IA, Révision/QCM, Historique, Profil).
**Acceptance**
- [ ] Routing Angular avec les 6 pages (même vides/mock au départ)
- [ ] Layout responsive (menu latéral desktop / menu replié mobile)
- [ ] Service HTTP configuré avec `environment.apiUrl`, intercepteur JWT (ajout du token, redirection si 401)
- [ ] Écran de login/register connecté à BACK-1

### DEVOPS-1 — CI de base
**Rôle** : Agent & DevOps
**Story** : En tant qu'équipe, je veux une CI GitHub Actions pour éviter de
casser `main` avec des PR non testées.
**Acceptance**
- [ ] Workflow CI lance les tests backend et le build frontend sur chaque PR
- [ ] Statut CI visible et requis avant merge (branch protection sur `main`)
- [ ] Lint basique (ruff ou flake8 côté Python, eslint côté Angular) — au moins configuré, pas forcément bloquant au sprint 1

---

## Sprint 2 — Cœur RAG + Chat

### RAG-1 — Recherche vectorielle
**Rôle** : Backend & RAG
**Story** : En tant que service, je veux retrouver les chunks les plus
pertinents pour une question donnée.
**Acceptance**
- [ ] Fonction `search(query, top_k, user_id)` qui embed la question et fait une recherche par similarité cosinus dans pgvector
- [ ] Filtrage par utilisateur (isolation, cf SEC-1) et éventuellement par cours
- [ ] Temps de réponse mesuré et raisonnable (< 1s sur un corpus de test)

### RAG-2 — Génération de réponse avec sources
**Rôle** : Backend & RAG
**Story** : En tant qu'étudiant, je veux une réponse claire à ma question
avec les sources (cours + page) pour vérifier l'information.
**Acceptance**
- [ ] `POST /api/chat` construit un prompt avec le contexte des chunks trouvés
- [ ] Appel à l'API Z.AI GLM-5.3-Flash (clé côté backend uniquement, jamais exposée au frontend)
- [ ] Réponse structurée `{answer, sources: [{course, page}]}`
- [ ] Gestion des erreurs API (timeout, quota dépassé) avec message utilisateur propre

### FRONT-2 — Page Chat IA
**Rôle** : Frontend
**Story** : En tant qu'étudiant, je veux discuter avec mes cours comme dans
un chat pour poser mes questions naturellement.
**Acceptance**
- [ ] Zone de saisie + historique de la conversation dans la page
- [ ] Affichage des sources sous chaque réponse (cours + page)
- [ ] État de chargement pendant l'appel API, gestion des erreurs affichée à l'utilisateur
- [ ] Design responsive (mobile/desktop)

### FRONT-3 — Upload de documents (UI)
**Rôle** : Frontend
**Story** : En tant qu'étudiant, je veux importer mes cours depuis
l'interface et suivre leur statut de traitement.
**Acceptance**
- [ ] Formulaire d'upload avec sélection de fichier + nom du cours
- [ ] Affichage du statut (uploadé / en cours de traitement / prêt / erreur)
- [ ] Liste "Mes cours" avec les documents déjà importés

### AGENT-1 — Squelette du Study Agent (LangGraph)
**Rôle** : Agent & DevOps
**Story** : En tant que système, je veux orchestrer plusieurs étapes
(identifier le chapitre → interroger le RAG → générer une question) pour
préparer le mode révision.
**Acceptance**
- [ ] Graphe LangGraph avec au moins les nœuds "identifier cours/chapitre" et "interroger le RAG" fonctionnels
- [ ] Le graphe s'appuie sur les fonctions RAG-1/RAG-2 existantes (pas de duplication de la logique de recherche)
- [ ] Testable en local via un script/endpoint de debug

---

## Sprint 3 — Agent, sécurité, finitions

### AGENT-2 — Génération de QCM et évaluation des réponses
**Rôle** : Agent & DevOps
**Story** : En tant qu'étudiant, je veux être interrogé sous forme de QCM
sur mes cours et recevoir un retour sur ma réponse.
**Acceptance**
- [ ] Le Study Agent génère une question à choix multiples pertinente à partir d'un chunk/chapitre
- [ ] Évaluation de la réponse de l'utilisateur (correct/incorrect + explication)
- [ ] Endpoint `POST /api/agent/qcm` exposé au frontend

### FRONT-4 — Mode révision / QCM (UI)
**Rôle** : Frontend
**Story** : En tant qu'étudiant, je veux m'entraîner avec des QCM générés
sur mes cours pour réviser efficacement.
**Acceptance**
- [ ] Affichage d'une question à choix multiples + sélection d'une réponse
- [ ] Feedback immédiat (correct/incorrect + explication de l'agent)
- [ ] Score de session affiché (nombre de bonnes réponses / total)

### FRONT-5 — Historique des échanges
**Rôle** : Frontend
**Story** : En tant qu'étudiant, je veux retrouver mes anciennes questions/
réponses pour ne pas perdre le fil de mes révisions.
**Acceptance**
- [ ] Page Historique listant les conversations passées (chat + QCM)
- [ ] Possibilité de rouvrir/consulter un échange passé

### SEC-1 — Sécurité et isolation des données
**Rôle** : Backend & Auth (avec relecture de toute l'équipe)
**Story** : En tant qu'utilisateur, je veux être sûr que mes documents et
mon historique ne sont visibles que par moi.
**Acceptance**
- [ ] Toutes les requêtes (documents, chunks, historique) filtrent par `owner_id`/utilisateur courant
- [ ] Validation stricte des fichiers uploadés (type MIME réel, pas juste l'extension ; taille max)
- [ ] Clé API Z.AI uniquement en variable d'environnement backend, absente de tout code frontend/commit
- [ ] Logs basiques des erreurs et des appels au LLM (sans logger les données sensibles)

### TEST-1 — Tests backend (Pytest)
**Rôle** : Backend & Auth / Backend & RAG (partagé)
**Story** : En tant qu'équipe, je veux des tests automatisés sur les
endpoints critiques pour éviter les régressions avant la démo.
**Acceptance**
- [ ] Tests sur auth (register/login, cas d'erreur)
- [ ] Tests sur l'upload (extension refusée, fichier valide)
- [ ] Tests sur la recherche vectorielle (isolation utilisateur respectée)
- [ ] CI passe sur ces tests (retirer le `|| true` du workflow)

### TEST-2 — Tests frontend (Angular)
**Rôle** : Frontend
**Story** : En tant qu'équipe, je veux des tests sur les composants clés
pour sécuriser le rendu avant la démo.
**Acceptance**
- [ ] Tests unitaires sur le service HTTP (mock des appels API)
- [ ] Test du composant Chat (affichage message + sources)
- [ ] `npm test` passe en CI

### DEVOPS-2 — Déploiement
**Rôle** : Agent & DevOps
**Story** : En tant qu'équipe, je veux une démo accessible par un lien
public pour la soutenance et le vote du public.
**Acceptance**
- [ ] Frontend déployé sur Vercel, backend sur Render (ou Azure/GCP/AWS avec crédits)
- [ ] Variables d'environnement de prod configurées (clé Z.AI, secrets JWT, CORS)
- [ ] Le lien de démo fonctionne de bout en bout (upload → chat → QCM)
- [ ] Lien noté dans le README et prêt à être envoyé sur Discord

---

## Freeze (dim 27/09)

### DOC-1 — Documentation finale et justification des choix
**Rôle** : tous
**Story** : En tant qu'équipe, je veux pouvoir justifier chaque choix
d'architecture et chaque ligne générée par IA le jour de la soutenance.
**Acceptance**
- [ ] README complet (installation, architecture, choix techniques et pourquoi)
- [ ] Une note courte par choix clé (embeddings local vs API, pgvector vs Chroma, etc.)
- [ ] Liste des parties générées avec un assistant IA et comment elles ont été relues/adaptées

### DOC-2 — Préparation de la soutenance
**Rôle** : tous
**Story** : En tant qu'équipe, je veux une présentation claire et un
scénario de démo qui ne plante pas devant le jury.
**Acceptance**
- [ ] Slides courtes (contexte, architecture, démo, difficultés/choix, perspectives)
- [ ] Scénario de démo testé au moins 2 fois de bout en bout avant le 28/09
- [ ] Répartition de la parole entre les 4 membres définie
