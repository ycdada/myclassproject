"""Student and Profile models."""

import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    major = Column(String(100), nullable=True)
    grade = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    profiles = relationship("StudentProfile", back_populates="student", order_by="StudentProfile.profile_version.desc()")
    activities = relationship("LearningActivity", back_populates="student")
    paths = relationship("LearningPath", back_populates="student")


class StudentProfile(Base, TimestampMixin):
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    profile_version = Column(Integer, default=1, nullable=False)

    # 8 profile dimensions
    knowledge_foundation = Column(JSONB, default=dict)       # {topic_id: mastery_score 0-1}
    cognitive_style = Column(String(50), nullable=True)       # visual/auditory/kinesthetic/reading
    error_prone_areas = Column(JSONB, default=list)          # [{concept, frequency, last_occurred}]
    learning_pace = Column(Float, default=1.0)               # hours per topic
    preferred_resource_types = Column(JSONB, default=list)   # [video, text, exercise, mindmap, code]
    motivation_level = Column(String(20), default="medium")   # high/medium/low
    attention_span = Column(String(20), default="medium")     # short/medium/long
    goal = Column(String(100), default="course_study")        # exam_prep/interview/course_study
    prior_courses = Column(JSONB, default=list)               # [{name, grade, year}]

    is_active = Column(Boolean, default=True)

    # Relationships
    student = relationship("Student", back_populates="profiles")
