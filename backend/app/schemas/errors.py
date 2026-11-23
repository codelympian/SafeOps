from typing import Any

from pydantic import BaseModel


class ErrorOut(BaseModel):
    detail: str


def error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """Declare error responses in OpenAPI, so the generated client types them."""
    descriptions = {
        401: "Not authenticated",
        403: "Forbidden (missing CSRF token or insufficient role)",
        404: "Not found",
        409: "Conflict",
    }
    return {code: {"model": ErrorOut, "description": descriptions[code]} for code in codes}
