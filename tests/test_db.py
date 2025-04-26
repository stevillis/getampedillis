from backend import db


def test_get_connection_env(monkeypatch):
    # Setup dummy environment variables
    monkeypatch.setenv("GETAMPEDVIVE_USER", "dummy_user")
    monkeypatch.setenv("GETAMPEDVIVE_PASSWORD", "dummy_pass")
    monkeypatch.setenv("GETAMPEDVIVE_HOST", "dummy_host")
    monkeypatch.setenv("GETAMPEDVIVE_PORT", "1234")
    monkeypatch.setenv("GETAMPEDVIVE_DBNAME", "dummy_db")

    # Patch psycopg2.connect to a dummy function to avoid real DB connection
    class DummyConn:
        def close(self):
            pass

    def dummy_connect(**kwargs):
        assert kwargs["user"] == "dummy_user"
        assert kwargs["password"] == "dummy_pass"
        assert kwargs["host"] == "dummy_host"
        assert kwargs["port"] == "1234"
        assert kwargs["dbname"] == "dummy_db"
        return DummyConn()

    monkeypatch.setattr(db.psycopg2, "connect", dummy_connect)

    conn = db.get_connection()

    assert isinstance(conn, DummyConn)

    conn.close()
