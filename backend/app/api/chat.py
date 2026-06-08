"""Chat API — dialogue-based profile construction with SSE streaming."""

import json
import uuid
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.student import StudentProfile
from sqlalchemy import select

router = APIRouter()


class ChatMessage(BaseModel):
    content: str
    session_id: Optional[str] = None
    student_id: Optional[str] = None


class ProfileResponse(BaseModel):
    session_id: str
    profile_version: int
    extracted_dimensions: dict


async def profile_chat_stream(
    student_id: str, message: str, session_id: str
) -> AsyncGenerator[str, None]:
    """SSE streaming for profile-building dialogue with real Spark + Orchestrator."""

    try:
        # Step 1: Stream conversation response via Spark Pro
        from app.services.spark_client import SparkProClient

        client = SparkProClient()
        conv_messages = [
            {
                "role": "system",
                "content": """你是一个友好的学习助手。你正在帮助一位同学构建学习画像。

请通过对话了解以下信息（自然地提问，不要一次问太多）：
1. 学过哪些编程/算法相关课程？
2. 喜欢怎样的学习方式？（看视频/读教材/动手做练习/画思维导图）
3. 学习数据结构与算法的目标？（准备考试/找工作面试/课程学习）
4. 觉得哪些知识点比较难或容易出错？
5. 平时学习时间多吗？注意力能集中多久？

每次只问1-2个问题，保持对话轻松愉快。回复简短亲切（50-100字）。""",
            },
            {"role": "user", "content": message},
        ]

        full_response = ""
        async for chunk in client.chat_stream(conv_messages, temperature=0.7, max_tokens=512):
            full_response += chunk
            yield f"event: content_chunk\ndata: {json.dumps({'text': chunk, 'agent': 'ProfileAnalyzer'}, ensure_ascii=False)}\n\n"

        # Step 2: Extract structured profile via orchestrator
        from app.agents.orchestrator import MultiAgentOrchestrator

        orchestrator = MultiAgentOrchestrator()
        result = await orchestrator.run_profile_building(
            student_id=student_id,
            user_message=message,
            session_id=session_id,
        )

        profile = result.get("profile", {})
        if profile:
            yield f"event: profile_update\ndata: {json.dumps({'profile': profile}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"

    yield f"event: done\ndata: {json.dumps({'session_id': session_id}, ensure_ascii=False)}\n\n"


@router.post("/profile")
async def profile_chat(message: ChatMessage):
    """Dialogue-based profile construction endpoint (SSE)."""
    student_id = message.student_id or "demo_student"
    session_id = message.session_id or str(uuid.uuid4())[:8]

    return StreamingResponse(
        profile_chat_stream(student_id, message.content, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/profile/{student_id}")
async def get_profile(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get current student profile from database."""
    result = await db.execute(
        select(StudentProfile)
        .where(StudentProfile.student_id == student_id, StudentProfile.is_active == True)
        .order_by(StudentProfile.profile_version.desc())
        .limit(1)
    )
    profile = result.scalars().first()

    if not profile:
        return {
            "session_id": "",
            "profile_version": 0,
            "extracted_dimensions": {},
        }

    return {
        "session_id": str(profile.id),
        "profile_version": profile.profile_version,
        "extracted_dimensions": {
            "cognitive_style": profile.cognitive_style,
            "knowledge_foundation": profile.knowledge_foundation,
            "error_prone_areas": profile.error_prone_areas,
            "learning_pace": profile.learning_pace,
            "preferred_resource_types": profile.preferred_resource_types,
            "motivation_level": profile.motivation_level,
            "attention_span": profile.attention_span,
            "goal": profile.goal,
            "prior_courses": profile.prior_courses,
        },
    }
