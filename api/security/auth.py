# Authentification (token JWT, OAuth2, etc.)
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

#from users import fake_users_db

import psycopg2
from passlib.context import CryptContext


# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Clé secrète utilisée pour signer les tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1000

# Crée un schéma OAuth2 pour extraire le token Bearer des requêtes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Fonction pour récupérer un utilisateur depuis PostgreSQL ---
def get_user_from_db(username: str):
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "trustpilot_users"),
        user=os.getenv("DB_USER", "airflow"),
        password=os.getenv("DB_PASSWORD", "airflow"),
        host=os.getenv("DB_HOST", "airflow_postgres"),
        port=os.getenv("DB_PORT", 5432)
    )
    cur = conn.cursor()
    cur.execute("SELECT username, password, role FROM public.users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"username": row[0], "password": row[1], "role": row[2]}
    return None

''''
# Vérifie si un utilisateur existe et si le mot de passe est correct
def authenticate_user(username: str, password: str):
    for user in fake_users_db.values():
        if user["username"] == username and user["password"] == password:
            return user
    return False
 '''   

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Vérifie si un utilisateur existe et si le mot de passe est correct
def authenticate_user(username: str, password: str):
    # Récupère l'utilisateur depuis PostgreSQL
    user = get_user_from_db(username)
    if not user:
        return False
    # Vérifie le mot de passe
    if not pwd_context.verify(password, user["password"]):
        return False
    return {"username": user["username"], "role": user["role"]}

# Crée un token JWT contenant des données (ex : username)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    # Définit la date d’expiration du token
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Décode le token JWT fourni et vérifie s'il est valide
    # 1. Lit le token envoyé dans l’en-tête HTTP
    # 2. Décode le token 
    # 3. Récupère le sub (subject) qui contient le nom d’utilisateur
    # 4. Retourne un dictionnaire utilisateur minimal
async def get_current_user(token: str = Depends(oauth2_scheme)):   
    credentials_exception = HTTPException (
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou manquant",
        headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Décode le token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        # Vérifie que l'utilisateur existe bien
        if username is None or role is None:
            raise credentials_exception
        
        #user = next((u for u in fake_users_db.values() if u["username"] == username), None)
        user = get_user_from_db(username)
        if user is None:
            raise credentials_exception
        return user

    except JWTError:
        raise credentials_exception

# Partie interactive
if __name__ == "__main__":
    print("=== AUTHENTIFICATION UTILISATEUR ===")

    username = input("Entrez votre nom d'utilisateur : ").strip().lower()
    password = input("Entrez votre mot de passe : ").strip()

    user = authenticate_user(username, password)

    if not user:
        print("\nÉchec de l'authentification. Nom d'utilisateur ou mot de passe incorrect.")
    else:
        print(f"\nBienvenue {user['username']} !")

        token = create_access_token(data={"sub": user["username"], "role": user["role"]})
        print(f"\nVoici votre token d'accès (JWT) :\n{token}\n")

        # Décodage pour afficher les infos contenues dans le token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Payload décodé :\n{decoded}")