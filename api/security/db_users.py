import psycopg2
from passlib.context import CryptContext
from users import fake_users_db

# Contexte pour hacher les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Retourne un hash sécurisé du mot de passe"""
    return pwd_context.hash(password)

def add_user(username: str, password: str, role: str, created_at=None):
    """Ajoute un utilisateur avec mot de passe hashé dans Postgres"""
    conn = psycopg2.connect(
        dbname="trustpilot_users",      
        user="airflow",         
        password="airflow",   
        host="airflow_postgres", # airflow_postgres ou 127.0.0.1 sur windows
        port=5432
    )
    cur = conn.cursor()

    # Création table si elle n'existe pas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS public.users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # Hachage du mot de passe
    hashed_pw = get_password_hash(password)

    # Insertion de l’utilisateur
    if created_at:
        cur.execute("""
            INSERT INTO public.users (username, password, role, created_at) 
            VALUES (%s, %s, %s, %s) 
            ON CONFLICT (username) DO NOTHING
            """, (username, hashed_pw, role, created_at)
        )
    else:
        cur.execute("""
            INSERT INTO public.users (username, password, role) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (username) DO NOTHING
            """, (username, hashed_pw, role)
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Utilisateur {username} ajouté avec succès.")


if __name__ == "__main__":
    
    # add user from fake db to postgres
    #for _, user in fake_users_db.items():
        #add_user(user["username"], user["password"], user["role"])

    # Exemple d'ajout manuel
    # add_user("pogba", "monaco", "client")
    # add_user("isak", "liverpool", "client")
    # add_user("wirtz", "liverpool", "client")
    # add_user("ekitike", "liverpool", "client")
    # add_user("sesko", "manchester", "client")
    # add_user("mbeumo", "manchester", "client")
    # add_user("osimhen", "galatasaray", "client")
    # add_user("cunha", "manchester", "client")
    # add_user("diaz", "bayern", "client")
    # add_user("eze", "arsenal", "client")
    # add_user("zabarnyi", "psg", "client")
    # add_user("chevalier", "psg", "client")
    # add_user("marin", "psg", "client")
    # add_user("donnaruma", "city", "client")
    # add_user("gyokeres", "arsenal", "client")
     add_user("frimpong", "liverpool", "client")
     add_user("mkerkez", "liverpool", "client")
     add_user("mamardashvili", "liverpool", "client")
     add_user("simons", "tottenham", "client")
    # add_user("kudus", "tottenham", "client")
    # add_user("dier", "monaco", "client")
    # add_user("fati", "monaco", "client")
    # add_user("joaopedro", "chelsea", "client")
    # add_user("garnacho", "chelsea", "client")
    # add_user("rabiot", "milan", "client")
    # add_user("mosquera", "arsenal", "client")
    # add_user("reijnders", "manchester", "client")
    # add_user("cherki", "city", "client")
    # add_user("bettinelli", "city", "client")
    # add_user("quansah", "leverkusen", "client")
    # add_user("ben seghir", "leverkusen", "client")