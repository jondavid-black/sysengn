import os
import uuid
import bcrypt
import logging
import json
from dataclasses import dataclass, field
from enum import Enum, auto

from flet.auth.oauth_provider import OAuthProvider
from flet.auth.providers import GitHubOAuthProvider, GoogleOAuthProvider

from sysengn.db.database import get_connection

logger = logging.getLogger(__name__)


class Role(Enum):
    ADMIN = auto()
    USER = auto()
    GUEST = auto()


@dataclass
class User:
    """Represents an authenticated user."""

    id: str
    email: str
    name: str | None = None
    roles: list[Role] = field(default_factory=list)

    def has_role(self, role: Role) -> bool:
        """Checks if the user has a specific role."""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """Checks if the user has a specific permission (mock implementation)."""
        # In a real app, this would check against a permissions table
        if Role.ADMIN in self.roles:
            return True
        return False


def get_oauth_providers() -> list[OAuthProvider]:
    """Configures and returns the list of available OAuth providers.

    Requires environment variables:
    - GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    - GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
    """
    providers: list[OAuthProvider] = []

    # Google
    g_id = os.getenv("GOOGLE_CLIENT_ID")
    g_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if g_id and g_secret:
        providers.append(
            GoogleOAuthProvider(
                client_id=g_id,
                client_secret=g_secret,
                redirect_url="http://localhost:8550/api/oauth/redirect",
            )
        )

    # GitHub
    gh_id = os.getenv("GITHUB_CLIENT_ID")
    gh_secret = os.getenv("GITHUB_CLIENT_SECRET")
    if gh_id and gh_secret:
        providers.append(
            GitHubOAuthProvider(
                client_id=gh_id,
                client_secret=gh_secret,
                redirect_url="http://localhost:8550/api/oauth/redirect",
            )
        )

    return providers


def authenticate_local_user(email: str, password: str) -> User | None:
    """Authenticates a user against the local database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, name, password_hash, roles FROM users WHERE email = ?",
            (email,),
        )
        row = cursor.fetchone()

        if not row:
            # If no users exist, create the first one as admin/test user
            cursor.execute("SELECT count(*) FROM users")
            if cursor.fetchone()[0] == 0:
                logger.info("Creating initial admin user")
                return create_user(
                    email, password, name="Admin User", roles=[Role.ADMIN, Role.USER]
                )
            return None

        stored_hash = row["password_hash"]
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            # Parse roles from JSON or comma-separated string
            try:
                role_names = json.loads(row["roles"])
            except json.JSONDecodeError:
                role_names = []

            roles = []
            for r_name in role_names:
                try:
                    # Handle auto() enum values which are integers in some contexts or names
                    # For simplicity, we stored names. Let's assume we store "ADMIN"
                    roles.append(Role[r_name])
                except KeyError:
                    pass

            return User(
                id=row["id"],
                email=row["email"],
                name=row["name"],
                roles=roles,
            )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
    finally:
        conn.close()

    return None


def create_user(
    email: str, password: str, name: str = "", roles: list[Role] | None = None
) -> User:
    """Creates a new user in the database."""
    if roles is None:
        roles = [Role.USER]

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    user_id = str(uuid.uuid4())
    role_names = json.dumps([r.name for r in roles])

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (id, email, name, password_hash, roles)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, email, name, password_hash, role_names),
        )
        conn.commit()

        return User(id=user_id, email=email, name=name, roles=roles)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise
    finally:
        conn.close()
