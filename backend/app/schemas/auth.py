import uuid
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints

from app.core.roles import Role


def _normalise_email(value: str) -> str:
    return value.strip().lower()


# A deliberately simple check: something@something.tld. Real deliverability is
# out of scope (no email verification in this project).
Email = Annotated[
    str,
    StringConstraints(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    AfterValidator(_normalise_email),
]
Password = Annotated[str, StringConstraints(min_length=10, max_length=128)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class RegisterRequest(BaseModel):
    org_name: Name
    full_name: Name
    email: Email
    password: Password


class LoginRequest(BaseModel):
    email: Email
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class CreateUserRequest(BaseModel):
    full_name: Name
    email: Email
    password: Password
    role: Role = Role.ENGINEER


class OrgOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: Role
    is_active: bool


class SessionOut(BaseModel):
    """Returned by login, register and /auth/me. Holds no secret except the CSRF token."""

    user: UserOut
    organization: OrgOut
    csrf_token: str = Field(description="Send back in the X-CSRF-Token header on writes")
