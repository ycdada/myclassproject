"""Resource and Topic models."""

import uuid
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class DSATopic(Base, TimestampMixin):
    __tablename__ = "dsa_topics"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    parent_id = Column(String(100), ForeignKey("dsa_topics.id"), nullable=True)
    difficulty_level = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    prerequisites = Column(JSONB, default=list)
    learning_objectives = Column(JSONB, default=list)
    common_misconceptions = Column(JSONB, default=list)

    # Relationships
    children = relationship("DSATopic", backref="parent", remote_side=[id])


class Resource(Base, TimestampMixin):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    topic_id = Column(String(100), ForeignKey("dsa_topics.id"), nullable=True)

    resource_type = Column(String(50), nullable=False)  # lecture/mindmap/exercise/reading/video/code
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=True)
    metadata = Column(JSONB, default=dict)
    files = Column(JSONB, default=list)

    quality_score = Column(Float, nullable=True)
    generation_prompt = Column(Text, nullable=True)
    agent_trace = Column(JSONB, default=list)

    # Relationships
    exercises = relationship("Exercise", back_populates="resource")


class Exercise(Base, TimestampMixin):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=True)

    question_type = Column(String(50), nullable=False)
    difficulty = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    hints = Column(JSONB, default=list)
    knowledge_points = Column(JSONB, default=list)
    bloom_level = Column(String(30), nullable=True)

    # Relationship
    resource = relationship("Resource", back_populates="exercises")
