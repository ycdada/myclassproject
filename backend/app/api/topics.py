from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class TopicNode(BaseModel):
    id: str
    name: str
    difficulty_level: int
    category: str
    parent_id: Optional[str] = None
    prerequisites: List[dict] = []
    learning_objectives: List[dict] = []


class TopicListResponse(BaseModel):
    topics: List[TopicNode]
    total: int


@router.get("", response_model=TopicListResponse)
async def list_topics(category: Optional[str] = None, difficulty: Optional[int] = None):
    """List all DSA topics, optionally filtered."""
    # TODO: Query from knowledge graph
    return TopicListResponse(topics=[], total=0)


@router.get("/{topic_id}", response_model=TopicNode)
async def get_topic(topic_id: str):
    """Get topic details with prerequisites and learning objectives."""
    # TODO: Query from knowledge graph
    return TopicNode(
        id=topic_id,
        name="Sample Topic",
        difficulty_level=3,
        category="data_structure",
    )


@router.get("/{topic_id}/prerequisites")
async def get_prerequisites(topic_id: str):
    """Get prerequisite chain for a topic."""
    # TODO: Traverse knowledge graph
    return {"topic_id": topic_id, "prerequisites": []}


@router.get("/{topic_id}/path")
async def get_learning_path_to_topic(topic_id: str):
    """Get recommended learning path from fundamentals to this topic."""
    # TODO: Topological sort from knowledge graph
    return {"topic_id": topic_id, "path": []}
