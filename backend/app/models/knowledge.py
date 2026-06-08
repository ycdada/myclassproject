"""
Knowledge Document model for RAG pipeline.

Stores DSA textbook chunks with pgvector embeddings for
semantic similarity search.
"""

import uuid
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base, TimestampMixin
from app.config import get_settings

settings = get_settings()


class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(String(100), ForeignKey("dsa_topics.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    source_file = Column(String(255), nullable=False)
    content_type = Column(String(50), default="text")  # text / code / formula / definition
    metadata = Column(JSONB, default=dict)             # {section, subsection, keywords}
    embedding = Column(Vector(settings.VECTOR_DIMENSION), nullable=False)

    __table_args__ = (
        Index(
            "idx_knowledge_embedding",
            embedding,
            postgresql_using="ivfflat",
            postgresql_with={"lists": 10},
        ),
    )
