from sqlalchemy import Boolean, CheckConstraint, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.roles import Role
from app.db.base import Base, OrgOwnedMixin, TimestampMixin, UUIDPrimaryKeyMixin

_ROLE_VALUES = ", ".join(f"'{role.value}'" for role in Role)


class User(UUIDPrimaryKeyMixin, OrgOwnedMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        # A plain string column + CHECK is easier to migrate than a Postgres ENUM
        # (adding a role later is one constraint swap, not an ALTER TYPE).
        CheckConstraint(f"role IN ({_ROLE_VALUES})", name="role_valid"),
        # Emails are stored lowercased by the application; the CHECK makes that an invariant.
        CheckConstraint("email = lower(email)", name="email_lowercase"),
    )

    # Globally unique: login is by email alone, before we know the org.
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
