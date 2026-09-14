"""
TICKET: BACK-1 Authentification JWT
À compléter par le binôme Backend : inscription, connexion, dépendance
get_current_user réutilisable dans les autres routers.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register():
    # TODO: valider l'email, hasher le mot de passe (security.hash_password),
    # créer le User en base, renvoyer un token.
    raise NotImplementedError


@router.post("/login")
async def login():
    # TODO: vérifier les identifiants, renvoyer un access_token JWT.
    raise NotImplementedError
