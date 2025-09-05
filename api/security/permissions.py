from fastapi import Depends, HTTPException, status
from .auth import get_current_user

# Rôles, scopes, accès restreint


def require_role(*allowed_roles):
    """Vérifie si l'utilisateur a un des rôles autorisés"""

    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permission refusée"
            )
        return user

    return role_checker
