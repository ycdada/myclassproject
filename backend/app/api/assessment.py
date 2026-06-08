"""Assessment API — learning assessment reports and dashboard."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.base import get_db
from app.models.assessment import LearningActivity, AssessmentResult
from app.models.student import StudentProfile

router = APIRouter()


@router.get("/report/{student_id}")
async def get_report(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get comprehensive learning assessment report."""
    # Get profile
    profile_result = await db.execute(
        select(StudentProfile).where(
            StudentProfile.student_id == student_id,
            StudentProfile.is_active == True,
        ).order_by(StudentProfile.profile_version.desc()).limit(1)
    )
    profile = profile_result.scalars().first()

    # Get assessment results
    assessments = await db.execute(
        select(AssessmentResult).where(
            AssessmentResult.student_id == student_id
        ).order_by(AssessmentResult.assessed_at.desc()).limit(20)
    )
    assessment_list = assessments.scalars().all()

    # Calculate overall mastery from profile
    kf = profile.knowledge_foundation if profile else {}
    overall_mastery = sum(kf.values()) / len(kf) if kf else 0.0

    # Identify strengths and weaknesses
    strengths = [topic for topic, score in kf.items() if score > 0.7]
    weaknesses = [
        {"topic": topic, "gap_description": f"Current mastery: {score:.0%}"}
        for topic, score in kf.items() if score < 0.4
    ]

    return {
        "student_id": student_id,
        "overall_mastery": round(overall_mastery, 2),
        "topic_assessments": [
            {
                "topic_id": a.topic_id,
                "assessment_type": a.assessment_type,
                "mastery_probability": a.mastery_probability,
                "scores": a.scores,
            }
            for a in assessment_list
        ],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": [
            {"action": "review", "resource_type": "lecture", "priority": "high"}
            for _ in weaknesses[:3]
        ],
        "learning_velocity": round(overall_mastery / max(len(kf), 1), 2),
        "engagement_score": 0.5,
    }


@router.get("/dashboard/{student_id}")
async def get_dashboard(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get learning dashboard analytics."""
    # Activity counts
    total_activities = await db.execute(
        select(func.count(LearningActivity.id)).where(
            LearningActivity.student_id == student_id
        )
    )
    activities_count = total_activities.scalar() or 0

    exercises_attempted = await db.execute(
        select(func.count(LearningActivity.id)).where(
            LearningActivity.student_id == student_id,
            LearningActivity.activity_type == "answer",
        )
    )
    exercises_count = exercises_attempted.scalar() or 0

    correct_count = await db.execute(
        select(func.count(LearningActivity.id)).where(
            LearningActivity.student_id == student_id,
            LearningActivity.is_correct == True,
        )
    )
    correct = correct_count.scalar() or 0

    total_time = await db.execute(
        select(func.sum(LearningActivity.duration_seconds)).where(
            LearningActivity.student_id == student_id
        )
    )
    total_seconds = total_time.scalar() or 0

    # Recent activities
    recent = await db.execute(
        select(LearningActivity).where(
            LearningActivity.student_id == student_id
        ).order_by(LearningActivity.created_at.desc()).limit(10)
    )
    recent_activities = recent.scalars().all()

    # Get profile for mastery radar
    profile_result = await db.execute(
        select(StudentProfile).where(
            StudentProfile.student_id == student_id,
            StudentProfile.is_active == True,
        ).order_by(StudentProfile.profile_version.desc()).limit(1)
    )
    profile = profile_result.scalars().first()

    return {
        "student_id": student_id,
        "topics_completed": len([k for k, v in (profile.knowledge_foundation or {}).items() if v > 0.8]) if profile else 0,
        "total_topics": 30,
        "exercises_attempted": exercises_count,
        "exercises_correct": correct,
        "resources_generated": 0,
        "total_study_time_minutes": total_seconds // 60,
        "recent_activities": [
            {
                "type": a.activity_type,
                "resource_id": str(a.resource_id) if a.resource_id else None,
                "duration_seconds": a.duration_seconds,
                "score": a.score,
                "created_at": str(a.created_at),
            }
            for a in recent_activities
        ],
        "mastery_radar": profile.knowledge_foundation if profile else {},
        "weekly_progress": [],
    }


@router.post("/self-eval/{student_id}")
async def submit_self_eval(
    student_id: str,
    topic_id: str,
    confidence: float,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Submit self-assessment for a topic."""
    import uuid
    assessment = AssessmentResult(
        id=uuid.uuid4(),
        student_id=student_id,
        topic_id=topic_id,
        assessment_type="self_eval",
        scores={"confidence": confidence},
        mastery_probability=confidence,
    )
    db.add(assessment)
    await db.commit()
    return {"student_id": student_id, "topic_id": topic_id, "confidence": confidence, "status": "recorded"}
