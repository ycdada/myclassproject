"""Resources API — generation and retrieval of personalized learning resources."""

import json
import uuid
from typing import Optional, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base import get_db
from app.models.resource import Resource, DSATopic

router = APIRouter()


class ResourceGenerateRequest(BaseModel):
    student_id: str
    topic_id: str
    resource_types: Optional[list[str]] = None


class ResourceResponse(BaseModel):
    id: str
    student_id: str
    topic_id: str
    resource_type: str
    title: str
    content: Optional[str] = None
    metadata: dict = {}


async def resource_generation_stream(request: ResourceGenerateRequest) -> AsyncGenerator[str, None]:
    """SSE stream for resource generation with real orchestrator."""

    yield f"event: progress\ndata: {json.dumps({'step': 'Initializing resource generation...', 'progress': 0.0, 'agent': 'Orchestrator'})}\n\n"

    try:
        # Get topic name from knowledge graph
        from app.knowledge_graph.dsa_graph import get_knowledge_graph
        kg = get_knowledge_graph()
        topic = kg.get_topic(request.topic_id)
        topic_name = topic["name"] if topic else request.topic_id

        yield f"event: progress\ndata: {json.dumps({'step': f'Generating resources for: {topic_name}', 'progress': 0.1, 'agent': 'Orchestrator'})}\n\n"

        # Run the orchestrator
        from app.agents.orchestrator import MultiAgentOrchestrator
        orchestrator = MultiAgentOrchestrator()
        session_id = f"gen_{request.student_id}_{request.topic_id}_{uuid.uuid4().hex[:6]}"

        result = await orchestrator.run_resource_generation(
            student_id=request.student_id,
            topic_id=request.topic_id,
            topic_name=topic_name,
            profile={},
            session_id=session_id,
        )

        # Emit generated resources
        for i, res in enumerate(result.get("generated_resources", [])):
            progress = 0.3 + 0.6 * (i + 1) / max(len(result.get("generated_resources", [])), 1)
            res_type = res.get("type", "unknown")
            yield f"event: progress\ndata: {json.dumps({'step': f'Generated: {res_type}', 'progress': round(progress, 2), 'agent': 'Orchestrator'})}\n\n"

            # Stream content chunks for lecture type
            if res.get("type") == "lecture" and res.get("content"):
                content = res["content"]
                chunk_size = 200
                for j in range(0, len(content), chunk_size):
                    yield f"event: content_chunk\ndata: {json.dumps({'text': content[j:j+chunk_size], 'agent': 'ContentGenerator'})}\n\n"

            # Emit resource ready event
            res_summary = {k: v for k, v in res.items() if k != "content"}
            yield f"event: resource_ready\ndata: {json.dumps(res_summary)}\n\n"

        # Quality check results
        quality = result.get("quality_checks", [])
        if quality:
            failed = [q for q in quality if not q["passed"]]
            yield f"event: progress\ndata: {json.dumps({'step': f'Quality check: {len(quality) - len(failed)}/{len(quality)} passed', 'progress': 0.95, 'agent': 'Assessor'})}\n\n"

        error = result.get("error")
        if error:
            yield f"event: error\ndata: {json.dumps({'message': error})}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"


@router.post("/generate")
async def generate_resources(request: ResourceGenerateRequest):
    """Trigger resource generation for a topic (SSE streaming)."""
    return StreamingResponse(
        resource_generation_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{resource_id}")
async def get_resource(
    resource_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a generated resource by ID from database."""
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = result.scalars().first()
    if not resource:
        raise HTTPException(404, "Resource not found")
    return {
        "id": str(resource.id),
        "student_id": str(resource.student_id),
        "topic_id": resource.topic_id,
        "resource_type": resource.resource_type,
        "title": resource.title,
        "content": resource.content,
        "metadata": resource.meta or {},
    }


@router.get("")
async def list_resources(
    student_id: Optional[str] = None,
    topic_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List resources with optional filters."""
    query = select(Resource)
    if student_id:
        query = query.where(Resource.student_id == student_id)
    if topic_id:
        query = query.where(Resource.topic_id == topic_id)
    if resource_type:
        query = query.where(Resource.resource_type == resource_type)
    query = query.order_by(Resource.created_at.desc()).limit(50)

    result = await db.execute(query)
    resources = result.scalars().all()
    return {
        "resources": [
            {
                "id": str(r.id),
                "student_id": str(r.student_id),
                "topic_id": r.topic_id,
                "resource_type": r.resource_type,
                "title": r.title,
                "metadata": r.metadata or {},
                "created_at": str(r.created_at),
            }
            for r in resources
        ],
        "total": len(resources),
    }


@router.post("/{resource_id}/feedback")
async def submit_feedback(
    resource_id: str,
    rating: int = 5,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback/rating for a resource."""
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = result.scalars().first()
    if not resource:
        raise HTTPException(404, "Resource not found")
    # Update quality score based on feedback
    resource.quality_score = rating / 5.0
    await db.commit()
    return {"resource_id": resource_id, "rating": rating, "status": "recorded"}
