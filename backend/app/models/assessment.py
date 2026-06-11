"""Assessment, Activity, and Learning Path models."""

import uuid
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class LearningPath(Base, TimestampMixin):
    __tablename__ = "learning_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    topics_sequence = Column(JSONB, default=list)  # [{topic_id, order, status, estimated_hours}]
    strategy = Column(String(50), default="standard")
    is_active = Column(Boolean, default=True)

    # Relationship
    student = relationship("Student", back_populates="paths")


class LearningActivity(Base, TimestampMixin):
    __tablename__ = "learning_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # view/answer/ask/watch/complete
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=True)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    score = Column(Float, nullable=True)
    student_response = Column(JSONB, nullable=True)
    is_correct = Column(Boolean, nullable=True)

    # Relationship
    student = relationship("Student", back_populates="activities")


class AssessmentResult(Base, TimestampMixin):
    __tablename__ = "assessment_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    topic_id = Column(String(100), ForeignKey("dsa_topics.id"), nullable=True)
    assessment_type = Column(String(50), nullable=False)  # quiz/test/practice/adaptive
    scores = Column(JSONB, default=dict)
    weaknesses = Column(JSONB, default=list)
    recommendations = Column(JSONB, default=list)
    mastery_probability = Column(Float, nullable=True)


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    role = Column(String(20), nullable=False)  # user/assistant/agent/system
    content = Column(Text, nullable=False)
    content_type = Column(String(30), default="text")  # text/image/audio/code/diagram
    extra_meta = Column("metadata", JSONB, default=dict)  # {intent, extracted_entities, agent_name}
