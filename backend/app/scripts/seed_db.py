"""
Database seeding script.

Populates dsa_topics table from seed data and creates
a demo student account for testing.
"""

import uuid
import asyncio
from passlib.context import CryptContext
from sqlalchemy import text, select

from app.models.base import async_session
from app.models.resource import DSATopic
from app.models.student import Student, StudentProfile


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_STUDENT = {
    "username": "demo_student",
    "email": "demo@dsalearn.com",
    "password": "demo123",
    "major": "计算机科学与技术",
    "grade": "大三",
}

DEMO_PROFILE = {
    "knowledge_foundation": {
        "dsa_intro": 0.6,
        "arrays": 0.7,
        "basic_sorting": 0.5,
        "recursion": 0.4,
    },
    "cognitive_style": "visual",
    "error_prone_areas": ["递归边界条件", "链表指针操作"],
    "learning_pace": 1.2,
    "preferred_resource_types": ["video", "exercise", "code"],
    "motivation_level": "high",
    "attention_span": "medium",
    "goal": "course_study",
    "prior_courses": ["C语言程序设计", "Python程序设计"],
}


async def seed_dsa_topics():
    """Seed DSA topics from knowledge graph seed data."""
    from app.knowledge_graph.seed_data import DSA_TOPICS

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(DSATopic).limit(1))
        if result.scalars().first():
            print("[seed] DSA topics already seeded, skipping.")
            return

        for topic_data in DSA_TOPICS:
            topic = DSATopic(
                id=topic_data["id"],
                name=topic_data["name"],
                parent_id=topic_data.get("parent_id"),
                difficulty_level=topic_data["difficulty_level"],
                category=topic_data["category"],
                prerequisites=topic_data.get("prerequisites", []),
                learning_objectives=topic_data.get("learning_objectives", []),
                common_misconceptions=topic_data.get("common_misconceptions", []),
            )
            session.add(topic)

        await session.commit()
        print(f"[seed] Seeded {len(DSA_TOPICS)} DSA topics.")


async def seed_demo_student():
    """Create a demo student account for testing."""
    async with async_session() as session:
        result = await session.execute(
            select(Student).where(Student.username == DEMO_STUDENT["username"])
        )
        if result.scalars().first():
            print("[seed] Demo student already exists, skipping.")
            return

        student_id = uuid.uuid4()

        student = Student(
            id=student_id,
            username=DEMO_STUDENT["username"],
            email=DEMO_STUDENT["email"],
            hashed_password=pwd_context.hash(DEMO_STUDENT["password"]),
            major=DEMO_STUDENT["major"],
            grade=DEMO_STUDENT["grade"],
        )
        session.add(student)

        profile = StudentProfile(
            student_id=student_id,
            profile_version=1,
            knowledge_foundation=DEMO_PROFILE["knowledge_foundation"],
            cognitive_style=DEMO_PROFILE["cognitive_style"],
            error_prone_areas=DEMO_PROFILE["error_prone_areas"],
            learning_pace=DEMO_PROFILE["learning_pace"],
            preferred_resource_types=DEMO_PROFILE["preferred_resource_types"],
            motivation_level=DEMO_PROFILE["motivation_level"],
            attention_span=DEMO_PROFILE["attention_span"],
            goal=DEMO_PROFILE["goal"],
            prior_courses=DEMO_PROFILE["prior_courses"],
        )
        session.add(profile)

        await session.commit()
        print(f"[seed] Demo student created: {DEMO_STUDENT['username']} / {DEMO_STUDENT['password']}")


async def seed_all():
    """Run all seed operations."""
    print("[seed] Starting database seeding...")
    await seed_dsa_topics()
    await seed_demo_student()
    print("[seed] Database seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed_all())
