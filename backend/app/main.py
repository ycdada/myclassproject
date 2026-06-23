from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — DB init is optional (won't block server start)
    try:
        from app.models.base import init_db
        await init_db()

        from app.models.base import _get_async_session
        from sqlalchemy import select
        from app.models.resource import DSATopic

        async with _get_async_session()() as session:
            result = await session.execute(select(DSATopic).limit(1))
            if not result.scalars().first():
                from app.scripts.seed_db import seed_all
                await seed_all()
        print("[startup] Database initialized and seeded.")
    except Exception as e:
        print(f"[startup] Database unavailable — running without persistence: {e}")

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于大模型的个性化资源生成与学习多智能体系统 - 数据结构与算法",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
