# EPF Study AI — Application RAG sur les cours de l'EPF

Hackathon EPF x Artik Consulting — sujet "Mineure IA et Cloud" : *Créer une
application RAG qui lit les cours de l'EPF.*

- Deadline commit + démo : **dimanche 27/09/2026, 23h59**
- Soutenance avec évaluation : **lundi 28/09/2026**

Voir `docs/PLANNING.md` pour le déroulé sprint par sprint et `docs/BACKLOG.md`
pour les tickets agile (à importer en issues GitHub).

## Stack

- Frontend : Angular
- Backend : FastAPI (Python)
- Base de données : PostgreSQL + pgvector
- Embeddings : sentence-transformers (local, gratuit) — fallback API Mistral
- LLM : Z.AI GLM-5.3-Flash (clé partagée, budget 200$ — usage parcimonieux)
- Agent : LangGraph (mode révision / QCM)
- Déploiement : Vercel (front) + Render (back)

## Démarrage rapide (environnement local)

### Prérequis
- Docker + Docker Compose
- Node.js 20+ et npm
- Python 3.11+ (optionnel en local si vous préférez tourner le backend hors
  Docker pour itérer plus vite)

### 1. Cloner et configurer
```bash
git clone <url-du-repo-github-du-groupe>
cd epf-rag
cp .env.example .env
# éditez .env : mettez la clé ZAI_API_KEY fournie par le prof,
# changez JWT_SECRET_KEY et les mots de passe Postgres
```

### 2. Lancer la base de données + le backend
```bash
docker compose up -d db adminer
docker compose up backend
```
- API disponible sur http://localhost:8000 (doc auto : http://localhost:8000/docs)
- Adminer (admin DB) sur http://localhost:8081 (system: PostgreSQL, serveur: db)

### 3. Générer et lancer le frontend
```bash
cd frontend
npx @angular/cli@18 new . --routing --style=scss --skip-git --ssr=false
npm start
```
Frontend sur http://localhost:4200

### 4. Vérifier que tout communique
- `GET http://localhost:8000/health` doit répondre `{"status": "ok"}`
- Le frontend doit pouvoir appeler l'API sans erreur CORS (vérifiez
  `CORS_ORIGINS` dans `.env`)

## Organisation du repo

```
epf-rag/
  backend/           # FastAPI + pipeline RAG + agent
  frontend/          # Angular (à générer, voir frontend/README.md)
  docs/              # architecture, planning, backlog
  .github/           # templates d'issues + CI
  docker-compose.yml
  .env.example
```

## Règles de travail (imposées par le cours)

1. Toute fonctionnalité passe par un **ticket** (voir `docs/BACKLOG.md` /
   template d'issue) avec des **critères d'acceptance**.
2. Une **branche par ticket** (`feature/back-2-ingestion`, ...), jamais de
   push direct sur `main`.
3. Une **Pull Request** obligatoire avant merge, avec au moins une relecture
   par un autre membre.
4. Si vous utilisez un harness IA type Claude Code/Codex, appuyez-vous sur un
   framework agentique (ex: spec-kit, BMAD) pour garder une trace des
   spécifications et ne pas faire du "vibe coding" pur — c'est noté.
5. Vous devez pouvoir justifier chaque choix d'architecture et chaque ligne
   de code générée par une IA le jour de la soutenance.
