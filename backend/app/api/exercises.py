"""Exercises API — practice question management and submission."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base import get_db
from app.models.resource import Exercise

router = APIRouter()


class ExerciseSubmitRequest(BaseModel):
    student_id: str
    exercise_id: str
    answer: str
    time_spent_seconds: Optional[int] = None


class ExerciseSubmitResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    score: float


@router.get("")
async def list_exercises(
    topic_id: Optional[str] = None,
    difficulty: Optional[int] = None,
    question_type: Optional[str] = None,
    count: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get practice questions with filters from database."""
    query = select(Exercise)
    if difficulty is not None:
        query = query.where(Exercise.difficulty == difficulty)
    if question_type:
        query = query.where(Exercise.question_type == question_type)
    # Join with Resource for topic filtering
    if topic_id:
        from app.models.resource import Resource
        query = query.join(Resource).where(Resource.topic_id == topic_id)
    query = query.limit(count)

    result = await db.execute(query)
    exercises = result.scalars().all()

    return {
        "exercises": [
            {
                "id": str(e.id),
                "resource_id": str(e.resource_id) if e.resource_id else None,
                "question_type": e.question_type,
                "difficulty": e.difficulty,
                "question_text": e.question_text,
                "options": e.options,
                "hints": e.hints,
                "knowledge_points": e.knowledge_points,
                "bloom_level": e.bloom_level,
            }
            for e in exercises
        ],
        "total": len(exercises),
        "count": count,
    }


@router.get("/{exercise_id}")
async def get_exercise(exercise_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific exercise."""
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalars().first()
    if not exercise:
        raise HTTPException(404, "Exercise not found")
    return {
        "id": str(exercise.id),
        "resource_id": str(exercise.resource_id) if exercise.resource_id else None,
        "question_type": exercise.question_type,
        "difficulty": exercise.difficulty,
        "question_text": exercise.question_text,
        "options": exercise.options,
        "hints": exercise.hints or [],
        "knowledge_points": exercise.knowledge_points or [],
        "bloom_level": exercise.bloom_level,
    }


@router.post("/submit", response_model=ExerciseSubmitResponse)
async def submit_answer(
    request: ExerciseSubmitRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit an answer for evaluation."""
    result = await db.execute(select(Exercise).where(Exercise.id == request.exercise_id))
    exercise = result.scalars().first()
    if not exercise:
        raise HTTPException(404, "Exercise not found")

    is_correct = request.answer.strip().lower() == exercise.correct_answer.strip().lower()
    return ExerciseSubmitResponse(
        is_correct=is_correct,
        correct_answer=exercise.correct_answer,
        explanation=exercise.explanation or "No explanation available.",
        score=1.0 if is_correct else 0.0,
    )


@router.get("/{exercise_id}/hints")
async def get_hints(exercise_id: str, hint_level: int = 1, db: AsyncSession = Depends(get_db)):
    """Get progressive hints for an exercise."""
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalars().first()
    if not exercise:
        raise HTTPException(404, "Exercise not found")

    hints = exercise.hints or []
    idx = min(hint_level - 1, len(hints) - 1)
    return {"exercise_id": exercise_id, "hint_level": hint_level, "hint": hints[idx] if hints else ""}
