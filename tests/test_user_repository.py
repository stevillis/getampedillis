import pytest
from backend.repository import user_repository


# Example test for fetch_roles (requires a test DB or mocking)
def test_fetch_roles(monkeypatch):
    class DummyCursor:
        def execute(self, q):
            pass

        def fetchall(self):
            return [(1, "admin"), (2, "user")]

        def close(self):
            pass

    class DummyConn:
        def cursor(self):
            return DummyCursor()

        def close(self):
            pass

    monkeypatch.setattr(user_repository, "get_connection", lambda: DummyConn())

    roles = user_repository.fetch_roles()
    assert roles == [(1, "admin"), (2, "user")]


def test_fetch_roles_raises_runtimeerror(monkeypatch):
    def fake_get_connection():
        raise Exception("DB down")

    monkeypatch.setattr(user_repository, "get_connection", fake_get_connection)

    with pytest.raises(RuntimeError) as excinfo:
        user_repository.fetch_roles()

    assert "Erro ao buscar papéis" in str(excinfo.value)
    assert "DB down" in str(excinfo.value)


# Example test for create_user (would need more mocking for a real test)
def test_create_user(monkeypatch):
    class DummyCursor:
        def execute(self, q, params):
            assert params[1] == "testuser"

        def close(self):
            pass

    class DummyConn:
        def cursor(self):
            return DummyCursor()

        def commit(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(user_repository, "get_connection", lambda: DummyConn())

    user_repository.create_user("2024-01-01", "testuser", "testpass", 1)


def test_create_user_raises_runtimeerror(monkeypatch):
    def fake_hashpw(*args, **kwargs):
        raise Exception("bcrypt error")

    monkeypatch.setattr(user_repository.bcrypt, "hashpw", fake_hashpw)

    with pytest.raises(RuntimeError) as excinfo:
        user_repository.create_user("2024-01-01", "login", "pass", 1)

    assert "Erro ao criar usuário" in str(excinfo.value)
    assert "bcrypt error" in str(excinfo.value)
