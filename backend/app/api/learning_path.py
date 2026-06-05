from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class PathTopic(BaseModel):
    topic_id: str
    topic_name: str
    order: int
    estimated_hours: float
    status: str = "pending"  # pending, in_progress, completed, skipped


class LearningPathResponse(BaseModel):
    id: str
    student_id: str
    topics_sequence: List[PathTopic]
    generated_at: str
    is_active: bool


class ProgressUpdate(BaseModel):
    student_id: str
    topic_id: str
    status: str  # in_progress, completed, skipped
    time_spent_minutes: Optional[float] = None


@router.post("/generate", response_model=LearningPathResponse)
async def generate_learning_path(student_id: str):
    """Generate personalized learning path based on student profile."""
    # TODO: Curriculum Planner Agent with knowledge graph traversal
    return LearningPathResponse(
        id="",
        student_id=student_id,
        topics_sequence=[],
        generated_at="",
        is_active=True,
    )


@router.get("/current/{student_id}", response_model=LearningPathResponse)
async def get_current_path(student_id: str):
    """Get active learning path for a student."""
    # TODO: Fetch from database
    return LearningPathResponse(
        id="",
        student_id=student_id,
        topics_sequence=[],
        generated_at="",
        is_active=True,
    )


@router.put("/progress")
async def update_progress(update: ProgressUpdate):
    """Update topic progress in learning path."""
    # TODO: Update in database, trigger assessment if needed
    return {"status": "updated", "student_id": update.student_id, "topic_id": update.topic_id}
