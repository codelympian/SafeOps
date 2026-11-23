from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings

router = APIRouter(prefix="/system", tags=["system"])


class SystemInfoOut(BaseModel):
    app_env: str
    llm_provider: str
    mock_mode: bool
    embedding_model: str


@router.get("/info", response_model=SystemInfoOut)
async def system_info(settings: Settings = Depends(get_settings)) -> SystemInfoOut:
    """Public, non-sensitive runtime info. The UI uses it to show the mock-provider banner."""
    return SystemInfoOut(
        app_env=settings.app_env,
        llm_provider=settings.llm_provider,
        mock_mode=settings.llm_provider == "mock",
        embedding_model=settings.embedding_model,
    )
