import bcrypt

from backend.db import get_connection


def fetch_roles():
    """Fetch all roles from the database, returns a list of (role_id, name)."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT role_id, name FROM roles ORDER BY name")
        roles = cur.fetchall()

        cur.close()
        conn.close()

        return roles
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar papéis: {e}")


def create_user(created_at, login, password, role_id):
    """Create a new user in the database."""
    try:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (created_at, login, password, role_id) VALUES (%s, %s, %s, %s)",
            (created_at, login, hashed_pw, role_id),
        )

        conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        raise RuntimeError(f"Erro ao criar usuário: {e}")
