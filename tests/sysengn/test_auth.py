import pytest
import os
from unittest.mock import patch
from sysengn.auth import (
    User,
    Role,
    get_oauth_providers,
    authenticate_local_user,
    create_user,
)
from sysengn.db.database import get_connection, init_db


# Use an in-memory database for testing
@pytest.fixture(autouse=True)
def setup_test_db():
    # Use patch to replace get_connection so that it always returns a connection to :memory:
    # BUT we need to ensure it's the SAME :memory: instance if we close and reopen?
    # No, sqlite3.connect(":memory:") creates a new database each time.
    # So we must mock get_connection to return the SAME connection or a connection to a shared resource.
    # Alternatively, we can use a temporary file.

    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as tmp_db:
        tmp_db_path = tmp_db.name

    # Initialize the temp DB
    init_db(tmp_db_path)

    # Patch DB_PATH in database module to point to our temp file
    # Note: This only works if get_connection uses DB_PATH global.
    with patch("sysengn.db.database.DB_PATH", tmp_db_path):
        yield

    # Cleanup
    if os.path.exists(tmp_db_path):
        os.remove(tmp_db_path)


def test_user_roles():
    """Verify role checking logic."""
    user = User(id="1", email="test@test.com", roles=[Role.USER])
    assert user.has_role(Role.USER)
    assert not user.has_role(Role.ADMIN)


def test_user_permissions():
    """Verify permission checking (mock logic)."""
    admin = User(id="1", email="admin@test.com", roles=[Role.ADMIN])
    user = User(id="2", email="user@test.com", roles=[Role.USER])

    assert admin.has_permission("anything")
    assert not user.has_permission("anything")


def test_get_oauth_providers_empty():
    """Verify empty list when no env vars set."""
    with patch.dict(os.environ, {}, clear=True):
        providers = get_oauth_providers()
        assert len(providers) == 0


def test_get_oauth_providers_google():
    """Verify Google provider is added."""
    env = {"GOOGLE_CLIENT_ID": "g_id", "GOOGLE_CLIENT_SECRET": "g_secret"}
    with patch.dict(os.environ, env, clear=True):
        providers = get_oauth_providers()
        assert len(providers) == 1
        assert "google" in providers[0].authorization_endpoint


def test_get_oauth_providers_github():
    """Verify GitHub provider is added."""
    env = {"GITHUB_CLIENT_ID": "gh_id", "GITHUB_CLIENT_SECRET": "gh_secret"}
    with patch.dict(os.environ, env, clear=True):
        providers = get_oauth_providers()
        assert len(providers) == 1
        assert "github" in providers[0].authorization_endpoint


def test_authenticate_local_user_success():
    """Verify successful local authentication."""
    # Create a user first
    create_user("test@example.com", "password", "Test User", [Role.USER])

    user = authenticate_local_user("test@example.com", "password")
    assert user is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert Role.USER in user.roles


def test_authenticate_local_user_failure():
    """Verify authentication failure."""
    # We must ensure there is at least one user in the DB, otherwise the "first user admin creation" logic
    # will kick in and create an admin user even for a "failure" test case if the email doesn't exist.
    create_user("existing@example.com", "password", "Existing User", [Role.USER])

    assert authenticate_local_user("wrong@example.com", "pass") is None
    assert authenticate_local_user("existing@example.com", "wrongpass") is None


def test_create_initial_admin():
    """Verify that the first user created (implicitly) is an admin if the DB is empty."""
    # Ensure DB is empty
    conn = get_connection()
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()

    # Authenticating against an empty DB triggers admin creation in the current logic?
    # No, authenticate_local_user only creates if no users exist AND we try to auth?
    # Wait, the logic says:
    # if not row:
    #     cursor.execute("SELECT count(*) FROM users")
    #     if cursor.fetchone()[0] == 0:
    #          return create_user(...)

    # So if we try to auth with ANY credentials and the DB is empty, it creates that user as admin?
    # That's what the code currently does. Let's verify.

    user = authenticate_local_user("admin@example.com", "adminpass")
    assert user is not None
    assert Role.ADMIN in user.roles
    assert user.email == "admin@example.com"
