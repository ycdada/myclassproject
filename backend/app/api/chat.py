from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
import json
import asyncio

router = APIRouter()


class ChatMessage(BaseModel):
    content: str
    session_id: Optional[str] = None


class ProfileResponse(BaseModel):
    session_id: str
    profile_version: int
    extracted_dimensions: dict


async def profile_chat_stream(session_id: str, message: str) -> AsyncGenerator[str, None]:
    """SSE streaming for profile-building dialogue."""
    # TODO: Integrate with Profile Analyzer Agent
    events = [
        {"event": "agent_thinking", "data": {"agent": "ProfileAnalyzer", "status": "Analyzing your response..."}},
        {"event": "message", "data": {"role": "assistant", "content": "Thank you for sharing! Let me ask you a bit more about your learning preferences..."}},
        {"event": "profile_update", "data": {"dimension": "cognitive_style", "value": "visual", "confidence": 0.85}},
        {"event": "done", "data": {"session_id": session_id}},
    ]
    for event in events:
        yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.1)


@router.post("/profile")
async def profile_chat(message: ChatMessage):
    """Dialogue-based profile construction endpoint (SSE)."""
    session_id = message.session_id or "new_session"
    return StreamingResponse(
        profile_chat_stream(session_id, message.content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/profile/{student_id}", response_model=ProfileResponse)
async def get_profile(student_id: str):
    """Get current student profile."""
    # TODO: Fetch from database
    return ProfileResponse(
        session_id="",
        profile_version=1,
        extracted_dimensions={},
    )
