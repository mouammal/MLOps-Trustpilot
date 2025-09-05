# Rôles, scopes, accès restreint
from fastapi import Depends, HTTPException, status
#from api.security.users import fake_users_db
from .auth import get_current_user

'''
def require_role(*allowed_roles):
    """
    Vérifie si l'utilisateur a l'un des rôles autorisés.
    """
    def role_checker(user: dict = Depends(get_current_user)):
        db_user = next((u for u in fake_users_db.values() if u["username"] == user["username"]), None)

        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Utilisateur introuvable")
        
        if db_user.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                detail="Permission refusée")
        return user
    return role_checker
'''

def require_role(*allowed_roles):
    """Vérifie si l'utilisateur a un des rôles autorisés"""
    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission refusée")
        return user
    return role_checker