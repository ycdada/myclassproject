from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class ExerciseResponse(BaseModel):
    id: str
    resource_id: str
    question_type: str  # multiple_choice, coding, short_answer, true_false, fill_blank
    difficulty: int
    question_text: str
    options: Optional[List[dict]] = None
    hints: List[str] = []
    knowledge_points: List[dict] = []


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
):
    """Get practice questions with filters."""
    # TODO: Query from database
    return {"exercises": [], "total": 0, "count": count}


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: str):
    """Get a specific exercise."""
    # TODO: Fetch from database
    return ExerciseResponse(
        id=exercise_id, resource_id="", question_type="multiple_choice",
        difficulty=3, question_text="Sample question", hints=[], knowledge_points=[],
    )


@router.post("/submit", response_model=ExerciseSubmitResponse)
async def submit_answer(request: ExerciseSubmitRequest):
    """Submit an answer for evaluation."""
    # TODO: Evaluate with Assessor Agent
    return ExerciseSubmitResponse(
        is_correct=True,
        correct_answer="Sample answer",
        explanation="Detailed explanation here.",
        score=1.0,
    )


@router.get("/{exercise_id}/hints")
async def get_hints(exercise_id: str, hint_level: int = 1):
    """Get progressive hints for an exercise."""
    # TODO: Fetch hints from database
    return {"exercise_id": exercise_id, "hint_level": hint_level, "hint": "Think about the base case first..."}
