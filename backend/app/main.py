from app.dependencies import get_current_user
from app.domain.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.dependencies import get_db
from app.domain.models.user import User
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.infrastructure.database import engine, Base
from app.api.routes.auth import router as auth_router
from app.api.schemas.auth import RegisterResponse
import app.domain.models 
from app.api.routes.workflows import router as workflow_router
from app.api.routes.prompt_blocks import router as prompt_block_router
from app.api.routes.executions import router as execution_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="PromptLab API",
    lifespan=lifespan,
)
app.include_router(auth_router)
app.include_router(workflow_router)
app.include_router(prompt_block_router)
app.include_router(execution_router)

@app.get("/")
async def root():
    return {
        "app_env": settings.app_env,
        "db": settings.database_url,
    }

@app.get("/me", response_model=RegisterResponse)
async def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return RegisterResponse(
        id=current_user.id,
        email=current_user.email,
    )