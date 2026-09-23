# Contrat API — EPF Study AI

Référence pour l'équipe frontend : endpoints disponibles, leur format
d'entrée/sortie, et leur statut. Mis à jour à chaque ticket backend mergé
dans `main`.

Base URL en local : `http://localhost:8000/api`

Toutes les routes protégées attendent un header :
```
Authorization: Bearer <token>
```
(token obtenu via `POST /auth/login`)

---

## Disponibles

### `POST /auth/register`
**Body**
```json
{ "email": "etudiant@epf.fr", "password": "motdepasse" }
```
**Réponses**
- `201` → `{ "id": "uuid", "email": "...", "created_at": "..." }`
- `400` → email déjà utilisé

### `POST /auth/login`
**Body**
```json
{ "email": "etudiant@epf.fr", "password": "motdepasse" }
```
**Réponses**
- `200` → `{ "access_token": "...", "token_type": "bearer" }`
- `401` → identifiants invalides

### `POST /documents/upload`
**Body** : `multipart/form-data`
- `file` : fichier `.pdf`, `.pptx` ou `.docx`
- `course_name` (optionnel) : string

**Réponses**
- `201` →
```json
{
  "id": "uuid",
  "filename": "Cours1.pdf",
  "course_name": null,
  "status": "ready",
  "created_at": "2026-09-21T08:56:43.723619"
}
```
  ⚠️ `status` peut valoir `uploaded`, `processing`, `ready` ou `error`. La
  réponse du POST renvoie le statut final (`ready`/`error`) car le
  traitement (extraction + embeddings) se fait avant de répondre — prévoir
  un état de chargement côté UI le temps de la requête (peut prendre
  quelques secondes selon la taille du fichier).
- `400` → extension non autorisée ou fichier trop volumineux (`detail`
  contient un message lisible à afficher tel quel)
- `401` → non authentifié

### `GET /documents/` 
**Réponse `200`** → liste des documents de l'utilisateur connecté,
triée du plus récent au plus ancien :
```json
[
  { "id": "uuid", "filename": "Cours2.pdf", "course_name": null, "status": "uploaded", "created_at": "..." },
  { "id": "uuid", "filename": "Cours1.pdf", "course_name": null, "status": "ready", "created_at": "..." }
]
```
Utile pour la page "Mes cours" (FRONT-3) : afficher cette liste avec un
badge de statut par document.

### `GET /search/?q=...&top_k=5` 
**Réponse `200`** :
```json
[
  {
    "chunk_id": "uuid",
    "document_id": "uuid",
    "filename": "Cours1.pdf",
    "course_name": null,
    "page_number": 3,
    "content": "extrait du texte...",
    "score": 0.82
  }
]
```
Recherche vectorielle limitée aux documents de l'utilisateur connecté
(isolation par `owner_id`).

### `POST /chat/` 
**Body**
```json
{ "message": "Qu'est-ce que le deep learning ?", "course_id": null }
```
**Réponses**
- `200` →
```json
{
  "answer": "Le deep learning est...",
  "sources": [{ "course": "Deep Learning", "page": 3 }]
}
```
  Si aucun contenu pertinent n'est trouvé dans les cours de l'utilisateur,
  `answer` contient un message l'invitant à importer le cours concerné et
  `sources` est vide (`[]`) plutôt que de renvoyer une erreur.
- `502` → le service IA a répondu avec une erreur (ex : rate limit du
  fournisseur, `detail` contient un message lisible)
- `504` → le service IA a mis trop de temps à répondre

### `POST /agent/qcm` 
Génère un quiz (QCM) à partir du contenu des cours de l'utilisateur, via
le Study Agent (LangGraph).

**Body**
```json
{ "course_name": null, "num_questions": 5 }
```
- `course_name` (optionnel) : filtre implicite sur le sujet recherché ;
  laisser `null` pour couvrir l'ensemble des cours importés.
- `num_questions` (optionnel, défaut `5`) : nombre de questions
  souhaitées.

**Réponses**
- `200` →
```json
{
  "questions": [
    {
      "question": "Dans une matrice de confusion pour une classification binaire malade/sain, que désignent les 'Faux positifs' (FP) ?",
      "options": [
        "Des individus classés comme malades alors qu'ils sont sains",
        "Des individus classés sains alors qu'ils sont malades",
        "Des individus classés malades qui le sont vraiment",
        "Des individus classés sains qui le sont vraiment"
      ],
      "correctAnswer": 0
    }
  ]
}
```
  ⚠️ Format volontairement identique à celui déjà utilisé en mock côté
  frontend (`revision.component.ts`) : `options` contient toujours
  exactement 4 propositions, `correctAnswer` est l'index (0 à 3) de la
  bonne réponse. La correction du quiz reste faite côté client, comme
  dans l'implémentation actuelle de la page Révision — il n'y a pas
  d'endpoint séparé de correction pour l'instant.
- `502` → génération impossible (aucun cours importé, ou erreur du
  service IA — rate limit notamment ; `detail` contient un message
  lisible à afficher tel quel)

---

**Convention d'erreurs** : toutes les erreurs renvoient
`{ "detail": "message lisible en français" }`. Le frontend peut afficher
`detail` directement à l'utilisateur dans la plupart des cas.
