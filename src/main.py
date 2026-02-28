import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .core.config import settings
from .core.models import db_helper
from .routers import posts_router

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("dispose engine")
    await db_helper.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="CMS",
    description="Система управления контентом (статьи, категории, пользователи, медиа)",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router, prefix=settings.api.prefix)
app.include_router(posts_router)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host=settings.run.host, port=settings.run.port)
