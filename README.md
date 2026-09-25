# EPF Study AI — Application RAG sur les cours de l'EPF

Hackathon EPF x Artik Consulting — sujet "Mineure IA et Cloud" : *Créer une
application RAG qui lit les cours de l'EPF.*

- Deadline commit + démo : **dimanche 27/09/2026, 23h59**
- Soutenance avec évaluation : **lundi 28/09/2026**

Voir `docs/PLANNING.md` pour le déroulé sprint par sprint, `docs/BACKLOG.md`
pour les tickets agile (à importer en issues GitHub) et `docs/API_CONTRACT.md`
pour le détail des endpoints.

## Fonctionnalités

| Fonctionnalité | État | Détail |
|---|---|---|
| Inscription / connexion | ✅ | JWT stocké dans `localStorage`, ajouté automatiquement aux appels API par un interceptor. Routes protégées par un guard. |
| Déconnexion | ✅ | Bouton dans la barre du haut (avec l'email connecté) et sur la page Profil. Session expirée (401) → retour automatique au login. |
| Mes cours | ✅ | Import de PDF / PPTX / DOCX (25 Mo max), découpage + embeddings côté backend, liste des documents avec leur statut (Prêt, En traitement, Erreur). |
| Chat IA | ✅ | Réponses générées à partir de vos cours, avec les sources (cours + page). |
| Révision / QCM | ✅ | Quiz de 5 questions généré par l'agent LangGraph à partir de vos cours. |
| Profil | ✅ | Email du compte connecté + déconnexion. |
| Historique | 🚧 | Maquette : les conversations affichées sont des exemples, pas encore branchées sur l'API. |

## Stack

- Frontend : Angular 18 (standalone components, SCSS)
- Backend : FastAPI (Python)
- Base de données : PostgreSQL + pgvector
- Embeddings : sentence-transformers (local, gratuit) — fallback API Mistral
- LLM : OpenRouter, modèles gratuits (défaut `nvidia/nemotron-3-ultra-550b-a55b:free`,
  clé perso par membre) — voir [Choisir le modèle LLM](#choisir-le-modèle-llm)
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
# éditez .env : mettez votre clé LLM_API_KEY OpenRouter (gratuite,
# https://openrouter.ai/keys), changez JWT_SECRET_KEY et les mots de
# passe Postgres (dans POSTGRES_PASSWORD *et* dans DATABASE_URL)
```

### 2. Lancer la base de données + le backend
```bash
docker compose up -d
```
- API disponible sur http://localhost:8000 (doc auto : http://localhost:8000/docs)
- Adminer (admin DB) sur http://localhost:8081 (system: PostgreSQL, serveur: db)
- Logs du backend : `docker compose logs backend --tail=20` (attendre
  `Application startup complete`)

> ⚠️ Après une modification de `.env`, relancez avec `docker compose up -d`
> (qui recrée le conteneur). Un simple `docker restart` ne relit **pas** le `.env`.

### 3. Lancer le frontend
```bash
cd frontend
npm install
npm start   # ng serve
```
Frontend sur http://localhost:4200

### 4. Vérifier que tout communique
- `GET http://localhost:8000/health` doit répondre `{"status": "ok"}`
- Le frontend doit pouvoir appeler l'API sans erreur CORS (vérifiez
  `CORS_ORIGINS` dans `.env`)

## Parcours de démo

1. Sur http://localhost:4200, un visiteur non connecté est redirigé vers **Connexion**.
2. **Créer un compte** (mot de passe de 8 caractères minimum) → retour sur la
   page de connexion avec le message « Compte créé, vous pouvez vous connecter ».
3. Se connecter → l'email apparaît en haut à droite avec le bouton **Déconnexion**.
4. **Mes cours** → sélectionner un PDF / PPTX / DOCX → **Télécharger le document**
   → le document apparaît dans « Mes documents » avec le statut **Prêt**.
5. **Chat IA** → poser une question sur le cours → réponse + cartes de sources.
6. **Révision / QCM** → le quiz est généré à partir des cours importés
   (compter 10 à 20 secondes).

Un compte sans document importé obtient « Je n'ai trouvé aucun contenu dans vos
cours… » dans le chat et une erreur dans le QCM : c'est normal, il faut d'abord
importer un cours.

## Frontend

```
frontend/src/
  environments/environment.ts   # URL de l'API
  app/
    core/auth/       # AuthService, authGuard, authInterceptor (JWT + gestion des 401)
    features/
      auth/          # pages Connexion / Créer un compte
      home/          # accueil
      chat/          # Chat IA
      documents/     # Mes cours (upload + liste)
      revision/      # Révision / QCM
      history/       # Historique (maquette)
      profile/       # Profil
    shared/          # navbar, sidebar
```

L'URL de l'API est définie dans `frontend/src/environments/environment.ts` :

```ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
};
```

Tests unitaires : `cd frontend && npm test` (Karma + Chrome).

## Choisir le modèle LLM

Le modèle est défini par `LLM_MODEL` dans `.env`. Les modèles gratuits
d'OpenRouter (suffixe `:free`) changent souvent : un modèle peut disparaître
(erreur 404) ou être saturé temporairement (erreur 429).

- Liste des modèles disponibles : `GET https://openrouter.ai/api/v1/models`
  (public, sans clé)
- Modèle par défaut : `nvidia/nemotron-3-ultra-550b-a55b:free` (testé : chat
  en 1 à 10 s, QCM de 5 questions en 10 à 20 s)
- Secours gratuit : `dots-studio/dots-3-note-preview:free` (chat correct, mais
  QCM lent, 30 à 40 s, proche du timeout de 30 s du backend)
- Secours payant : `z-ai/glm-5.2` (nécessite du crédit OpenRouter)

Après tout changement : `docker compose up -d`.

## Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| Chat : « Erreur du service IA (404) » | Le modèle `LLM_MODEL` n'existe plus sur OpenRouter | Choisir un autre modèle (voir ci-dessus) puis `docker compose up -d` |
| Chat : « Erreur du service IA (429) » | Modèle gratuit saturé | Réessayer plus tard ou changer de modèle |
| Chat : « Le service IA met trop de temps à répondre » | Modèle trop lent (timeout 30 s) | Changer de modèle |
| QCM : « Impossible de générer le QCM… » | Aucun cours importé, ou modèle trop lent / indisponible | Importer un cours ; sinon voir les lignes ci-dessus |
| Retour inattendu sur la page de connexion | Session expirée (`ACCESS_TOKEN_EXPIRE_MINUTES`, 60 min par défaut) | Se reconnecter |
| « Impossible de joindre le serveur » | Backend arrêté ou erreur CORS | `docker compose ps`, vérifier `CORS_ORIGINS` |

## Organisation du repo

```
epf-rag/
  backend/           # FastAPI + pipeline RAG + agent
  frontend/          # Angular
  docs/              # architecture, contrat API, planning, backlog
  scripts/           # scripts utilitaires (création des issues GitHub)
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
