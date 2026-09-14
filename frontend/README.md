# Frontend Angular — EPF Study AI

Ce dossier accueillera le projet Angular. Pour éviter de figer une version
Angular dans le scaffold, générez-le vous-même en local (le CLI a besoin de
network + de votre Node local, plus fiable qu'un scaffold pré-fait) :

```bash
cd frontend
npx @angular/cli@18 new . --routing --style=scss --skip-git --ssr=false
```

Répondez "No" à la question sur l'analytics si elle apparaît.

## Structure cible (voir FRONT-1)

```
src/app/
  core/            # auth guard, interceptor JWT, services HTTP
  features/
    chat/          # Chat IA (FRONT-2)
    documents/     # Upload de cours (FRONT-3)
    revision/      # Mode révision / QCM (FRONT-4)
    history/       # Historique des échanges (FRONT-5)
    profile/
  shared/          # composants réutilisables (bulle de message, source-card...)
```

## Config à ajouter

`src/environments/environment.ts` :

```ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
};
```

## Lancer en dev

```bash
npm install
npm start   # ng serve, http://localhost:4200
```

Le backend doit tourner sur `http://localhost:8000` (voir `docker-compose.yml`
à la racine du repo) et autoriser `http://localhost:4200` dans `CORS_ORIGINS`.
