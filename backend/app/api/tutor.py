from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import json
import asyncio

router = APIRouter()


class TutorQuestion(BaseModel):
    student_id: str
    question: str
    topic_id: Optional[str] = None
    question_type: Optional[str] = "text"  # text, voice, image
    session_id: Optional[str] = None


async def tutor_stream(question: TutorQuestion) -> AsyncGenerator[str, None]:
    """SSE streaming for multi-modal tutoring response."""
    # TODO: Integrate with Tutor Agent, Code Mentor, TTS
    events = [
        {"event": "agent_thinking", "data": {"agent": "Tutor", "status": "Understanding your question..."}},
        {"event": "content_chunk", "data": {"agent": "Tutor", "text": "That's a great question about data structures!"}},
        {"event": "diagram", "data": {"agent": "MultimediaCreator", "type": "mermaid", "code": "graph TD\n    A[Array] --> B[Linked List]"}},
        {"event": "audio", "data": {"agent": "TTS", "url": "/api/files/explanation.mp3"}},
        {"event": "done", "data": {"session_id": question.session_id}},
    ]
    for event in events:
        yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.2)


@router.post("/ask")
async def ask_tutor(question: TutorQuestion):
    """Ask the tutor agent a question (SSE multi-modal response)."""
    return StreamingResponse(
        tutor_stream(question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
