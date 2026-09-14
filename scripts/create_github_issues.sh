#!/usr/bin/env bash
# Crée automatiquement les issues GitHub du backlog (docs/BACKLOG.md) à
# partir du fichier scripts/issues.tsv, avec labels et milestone.
#
# Prérequis : gh CLI installé et authentifié (`gh auth login`), lancé depuis
# un clone du repo GitHub du groupe, sur la branche par défaut.
#
# Usage : ./scripts/create_github_issues.sh

set -euo pipefail

if ! command -v gh &> /dev/null; then
  echo "gh CLI introuvable. Installe-le : https://cli.github.com/"
  exit 1
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Création des issues dans $REPO ..."

# Crée les labels s'ils n'existent pas déjà (ignore l'erreur si déjà présents)
for label in sprint-0 sprint-1 sprint-2 sprint-3 backend frontend agent-devops security docs; do
  gh label create "$label" --color "ededed" 2>/dev/null || true
done

# Crée les milestones (ignore l'erreur si déjà présents)
gh api repos/$REPO/milestones -f title="Sprint 1" -f due_on="2026-09-18T23:59:00Z" 2>/dev/null || true
gh api repos/$REPO/milestones -f title="Sprint 2" -f due_on="2026-09-24T23:59:00Z" 2>/dev/null || true
gh api repos/$REPO/milestones -f title="Sprint 3" -f due_on="2026-09-27T23:59:00Z" 2>/dev/null || true

tail -n +2 "$(dirname "$0")/issues.tsv" | while IFS=$'\t' read -r id title role sprint labels body; do
  echo "-> $id: $title"
  gh issue create \
    --title "[$id] $title" \
    --body "**Rôle :** $role
**Sprint :** $sprint

$body

Voir le détail complet et les critères d'acceptance dans \`docs/BACKLOG.md\` (ticket $id)." \
    --label "$labels" || echo "   (échec pour $id, à créer manuellement)"
done

echo "Terminé. Ajoute les issues créées à ton board GitHub Projects si besoin."
