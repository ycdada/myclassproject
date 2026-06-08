"""Topics API — DSA knowledge graph queries."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base import get_db
from app.models.resource import DSATopic

router = APIRouter()


class TopicNode(BaseModel):
    id: str
    name: str
    difficulty_level: int
    category: str
    parent_id: Optional[str] = None
    prerequisites: list = []
    learning_objectives: list = []
    common_misconceptions: list = []

    class Config:
        from_attributes = True


@router.get("")
async def list_topics(
    category: Optional[str] = None,
    difficulty: Optional[int] = None,
):
    """List all DSA topics, filtered by category/difficulty."""
    from app.knowledge_graph.dsa_graph import get_knowledge_graph
    kg = get_knowledge_graph()

    topics = kg.get_all_topics()
    if category:
        topics = [t for t in topics if t["category"] == category]
    if difficulty is not None:
        topics = [t for t in topics if t["difficulty_level"] == difficulty]

    return {"topics": topics, "total": len(topics)}


@router.get("/{topic_id}")
async def get_topic(topic_id: str):
    """Get topic details with prerequisites and learning objectives."""
    from app.knowledge_graph.dsa_graph import get_knowledge_graph
    kg = get_knowledge_graph()

    topic = kg.get_topic(topic_id)
    if not topic:
        raise HTTPException(404, f"Topic not found: {topic_id}")
    return topic


@router.get("/{topic_id}/prerequisites")
async def get_prerequisites(topic_id: str):
    """Get prerequisite chain for a topic."""
    from app.knowledge_graph.dsa_graph import get_knowledge_graph
    kg = get_knowledge_graph()

    prereqs = kg.get_prerequisites(topic_id)
    return {"topic_id": topic_id, "prerequisites": prereqs}


@router.get("/{topic_id}/dependents")
async def get_dependents(topic_id: str):
    """Get topics that depend on this topic."""
    from app.knowledge_graph.dsa_graph import get_knowledge_graph
    kg = get_knowledge_graph()

    dependents = kg.get_dependents(topic_id)
    return {"topic_id": topic_id, "dependents": dependents}
