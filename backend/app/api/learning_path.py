"""Learning Path API — personalized path generation and management."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base import get_db
from app.models.assessment import LearningPath
from app.models.student import StudentProfile

router = APIRouter()


class ProgressUpdate(BaseModel):
    student_id: str
    topic_id: str
    status: str = "in_progress"
    time_spent_minutes: Optional[float] = None


@router.post("/generate")
async def generate_learning_path(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Generate personalized learning path based on student profile."""
    # Get student profile
    result = await db.execute(
        select(StudentProfile).where(
            StudentProfile.student_id == student_id,
            StudentProfile.is_active == True,
        ).order_by(StudentProfile.profile_version.desc()).limit(1)
    )
    profile = result.scalars().first()

    # Generate path using knowledge graph
    from app.knowledge_graph.dsa_graph import get_knowledge_graph, PathStrategy

    kg = get_knowledge_graph()
    completed = list((profile.knowledge_foundation or {}).keys()) if profile else []
    goal = profile.goal if profile else "course_study"

    strategy_map = {
        "exam_prep": PathStrategy.STANDARD,
        "interview": PathStrategy.DIFFICULTY_ASC,
        "course_study": PathStrategy.STANDARD,
    }
    path_nodes = kg.generate_learning_path(completed, strategy=strategy_map.get(goal, PathStrategy.STANDARD))

    topics_sequence = [
        {
            "topic_id": n.topic_id,
            "topic_name": n.topic_name,
            "order": n.order,
            "difficulty": n.difficulty,
            "status": n.status,
            "estimated_hours": n.estimated_hours,
        }
        for n in path_nodes
    ]

    # Persist to database
    import uuid
    path_entry = LearningPath(
        id=uuid.uuid4(),
        student_id=student_id,
        topics_sequence=topics_sequence,
        strategy=goal,
        is_active=True,
    )
    # Deactivate old paths
    from sqlalchemy import update
    await db.execute(
        update(LearningPath).where(
            LearningPath.student_id == student_id, LearningPath.is_active == True
        ).values(is_active=False)
    )
    db.add(path_entry)
    await db.commit()

    return {
        "id": str(path_entry.id),
        "student_id": student_id,
        "topics_sequence": topics_sequence,
        "generated_at": str(path_entry.created_at),
        "is_active": True,
    }


@router.get("/current/{student_id}")
async def get_current_path(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get active learning path for a student."""
    result = await db.execute(
        select(LearningPath).where(
            LearningPath.student_id == student_id,
            LearningPath.is_active == True,
        ).order_by(LearningPath.created_at.desc()).limit(1)
    )
    path = result.scalars().first()
    if not path:
        return {"id": "", "student_id": student_id, "topics_sequence": [], "generated_at": "", "is_active": False}

    return {
        "id": str(path.id),
        "student_id": str(path.student_id),
        "topics_sequence": path.topics_sequence,
        "generated_at": str(path.created_at),
        "is_active": path.is_active,
    }


@router.put("/progress")
async def update_progress(
    update: ProgressUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update topic progress in learning path."""
    result = await db.execute(
        select(LearningPath).where(
            LearningPath.student_id == update.student_id,
            LearningPath.is_active == True,
        ).order_by(LearningPath.created_at.desc()).limit(1)
    )
    path = result.scalars().first()
    if not path:
        raise HTTPException(404, "No active learning path found")

    topics = path.topics_sequence or []
    for topic in topics:
        if topic["topic_id"] == update.topic_id:
            topic["status"] = update.status

    path.topics_sequence = topics
    await db.commit()

    return {"status": "updated", "student_id": update.student_id, "topic_id": update.topic_id}
