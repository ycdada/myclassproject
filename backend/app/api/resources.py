from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
import json
import asyncio

router = APIRouter()


class ResourceGenerateRequest(BaseModel):
    student_id: str
    topic_id: str
    resource_types: Optional[List[str]] = None  # e.g., ["lecture", "mindmap", "exercise", "reading", "video", "code"]


class ResourceResponse(BaseModel):
    id: str
    student_id: str
    topic_id: str
    resource_type: str
    title: str
    content: Optional[str] = None
    metadata: dict = {}


async def resource_generation_stream(request: ResourceGenerateRequest) -> AsyncGenerator[str, None]:
    """SSE streaming for resource generation progress."""
    # TODO: Trigger multi-agent orchestration
    steps = [
        {"agent": "Orchestrator", "status": "Planning resource generation..."},
        {"agent": "ContentGenerator", "status": "Creating lecture document..."},
        {"agent": "MultimediaCreator", "status": "Generating mind map..."},
        {"agent": "ExerciseDesigner", "status": "Designing practice questions..."},
        {"agent": "CodeMentor", "status": "Preparing code examples..."},
        {"agent": "Assessor", "status": "Reviewing content quality..."},
    ]
    for i, step in enumerate(steps):
        progress = (i + 1) / len(steps)
        yield f"event: progress\ndata: {json.dumps({'step': step['status'], 'progress': progress, 'agent': step['agent']}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.3)
    yield f"event: done\ndata: {json.dumps({'resources_generated': []})}\n\n"


@router.post("/generate")
async def generate_resources(request: ResourceGenerateRequest):
    """Trigger resource generation for a topic (SSE)."""
    return StreamingResponse(
        resource_generation_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: str):
    """Get a generated resource by ID."""
    # TODO: Fetch from database
    return ResourceResponse(
        id=resource_id, student_id="", topic_id="", resource_type="lecture",
        title="Sample Resource",
    )


@router.get("")
async def list_resources(
    student_id: Optional[str] = None,
    topic_id: Optional[str] = None,
    resource_type: Optional[str] = None,
):
    """List resources with optional filters."""
    # TODO: Query from database
    return {"resources": [], "total": 0}


@router.post("/{resource_id}/feedback")
async def submit_feedback(resource_id: str, rating: int = 5, comment: Optional[str] = None):
    """Submit feedback/rating for a resource."""
    return {"resource_id": resource_id, "rating": rating, "status": "received"}
