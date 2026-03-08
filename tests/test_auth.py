from unittest.mock import MagicMock, patch

import bcrypt
import pytest

from backend.utils import auth

# Set up test credentials (these should correspond to test users in your DB)
TEST_USERS = [
    {"login": "guest", "password": "guest", "expected_role": "guest"},
]


@pytest.mark.parametrize("user", TEST_USERS)
def test_authenticate_user_valid(user):
    hashed = bcrypt.hashpw(user["password"].encode(), bcrypt.gensalt()).decode()

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (hashed, user["expected_role"])
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch.object(auth.psycopg2, "connect", return_value=mock_conn):
        success, role = auth.authenticate_user(user["login"], user["password"])

    assert success is True
    assert role == user["expected_role"]


def test_authenticate_user_invalid():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch.object(auth.psycopg2, "connect", return_value=mock_conn):
        success, role = auth.authenticate_user("nonexistent", "wrongpass")

    assert success is False
    assert role is None


def test_authenticate_user_wrong_password():
    hashed = bcrypt.hashpw(b"correctpassword", bcrypt.gensalt()).decode()

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (hashed, "guest")
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch.object(auth.psycopg2, "connect", return_value=mock_conn):
        success, role = auth.authenticate_user("guest", "wrongpassword")

    assert success is False
    assert role is None


def test_authenticate_user_exception(monkeypatch):
    def fake_connect(*args, **kwargs):
        raise Exception("DB connection failed")

    monkeypatch.setattr(auth.psycopg2, "connect", fake_connect)

    success, role = auth.authenticate_user("guest", "guest")

    assert success is False
    assert role is None


def test_require_login_redirect(monkeypatch):
    # Simulate not logged in
    class DummySession(dict):
        pass

    dummy_state = DummySession()
    monkeypatch.setattr(auth.st, "session_state", dummy_state)
    called = {}

    def fake_switch_page(page):
        called["page"] = page

    monkeypatch.setattr(auth.st, "switch_page", fake_switch_page)

    auth.require_login("loginpage.py")
    assert called["page"] == "loginpage.py"
