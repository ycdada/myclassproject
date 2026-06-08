from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.models.base import init_db
    await init_db()

    # Auto-seed database if empty
    from sqlalchemy import text, select
    from app.models.base import async_session
    from app.models.resource import DSATopic

    async with async_session() as session:
        result = await session.execute(select(DSATopic).limit(1))
        if not result.scalars().first():
            from app.scripts.seed_db import seed_all
            await seed_all()

    # Pre-load embedding model
    try:
        from app.services.rag_service import get_rag_service
        rag = await get_rag_service()
        await rag.embed_query("warmup")
    except Exception:
        pass  # Model will load on first use

    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于大模型的个性化资源生成与学习多智能体系统 - 数据结构与算法",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


# Import and include routers
from app.api import auth, chat, topics, resources, exercises, tutor, assessment, learning_path

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat & Profile"])
app.include_router(topics.router, prefix="/api/topics", tags=["Knowledge Graph"])
app.include_router(learning_path.router, prefix="/api/learning-path", tags=["Learning Path"])
app.include_router(resources.router, prefix="/api/resources", tags=["Resources"])
app.include_router(exercises.router, prefix="/api/exercises", tags=["Exercises"])
app.include_router(tutor.router, prefix="/api/tutor", tags=["Tutoring"])
app.include_router(assessment.router, prefix="/api/assessment", tags=["Assessment"])
