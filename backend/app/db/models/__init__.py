"""Import every model here so Alembic's autogenerate sees the full metadata."""

from app.db.models.organization import Organization
from app.db.models.user import User

__all__ = ["Organization", "User"]
