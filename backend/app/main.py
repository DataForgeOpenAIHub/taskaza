from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1 import apikeys, auth, login, tasks, users
from app.core import metadata
from app.core.config import settings
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Taskaza API",
    version="1.0.0",
    description=metadata.description,
    summary=metadata.summary,
    terms_of_service="https://github.com/kayvanshah1/taskaza/blob/main/LICENSE",
    # contact=metadata.contact,
    license_info=metadata.license_info,
    openapi_tags=metadata.tags_metadata,
    lifespan=lifespan,
)

# Handle CORS protection
origins = settings.BACKEND_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, tags=["Users"])
app.include_router(login.router, tags=["Login"])
app.include_router(tasks.router, tags=["Tasks"])
app.include_router(apikeys.router, tags=["API Keys"])
app.include_router(auth.router, tags=["Auth"])


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
