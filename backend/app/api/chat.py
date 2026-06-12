"""Chat API — dialogue-based conversation with automatic resource generation."""

import json
import uuid
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base import get_db
from app.models.student import StudentProfile

router = APIRouter()


class ChatMessage(BaseModel):
    content: str
    session_id: Optional[str] = None
    student_id: Optional[str] = None


class ProfileResponse(BaseModel):
    session_id: str
    profile_version: int
    extracted_dimensions: dict


# System prompt that combines conversation + topic detection
SESSION_SYSTEM_PROMPT = """你是一个数据结构与算法学习助手。你同时具备两种能力：

1. **对话交流**：以友好、耐心的态度与学生自然对话。了解他们的学习背景、目标和偏好。
2. **内容生成**：当学生明确表示想学习某个具体的数据结构或算法知识点时（例如"我想学数组"、"给我讲讲二叉树"、"我需要练习链表"），你需要：
   - 先简短回应（1-2句话确认理解）
   - 然后告诉学生"我来为你生成个性化的学习材料，请稍候..."
   - 系统将自动调用多智能体系统为你生成讲义、练习题和思维导图

## 可生成资源的知识点（学生可能提到的关键词）
数组、链表、栈、队列、字符串、二叉树、二叉搜索树、AVL树、红黑树、堆、字典树(Trie)、
图、图的遍历(BFS/DFS)、最短路径、最小生成树、排序算法、快速排序、归并排序、堆排序、
哈希表、递归、分治法、动态规划、贪心算法、回溯算法、并查集、线段树、树状数组

## 对话风格
- 每次回复控制在 50-120 字
- 如果学生只是闲聊或介绍自己，自然地继续对话，收集学习画像信息
- 只有当学生明确说想学某个具体知识点时，才触发内容生成
- 在触发内容生成时，回复末尾加上 [GENERATE:知识点名称]"""


def _match_topic_from_text(text: str) -> Optional[str]:
    """Match DSA topic ID from user text using keyword matching."""
    from app.knowledge_graph.seed_data import DSA_TOPICS

    text_lower = text.lower()
    best_match = None
    best_len = 0

    for topic in DSA_TOPICS:
        name = topic["name"]
        keywords = [
            name,
            name.replace("（", "").replace("）", ""),
            *[obj["objective"] for obj in topic.get("learning_objectives", [])],
        ]
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in text_lower and len(kw_lower) > best_len:
                best_match = topic["id"]
                best_len = len(kw_lower)

    return best_match


async def session_chat_stream(
    student_id: str, message: str, session_id: str
) -> AsyncGenerator[str, None]:
    """SSE streaming: conversation + topic detection + resource generation."""

    from app.services.spark_client import SparkProClient

    resource_generated = False

    try:
        # Step 1: Stream conversation via Spark Pro
        client = SparkProClient()
        conv_messages = [
            {"role": "system", "content": SESSION_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        full_response = ""
        async for chunk in client.chat_stream(conv_messages, temperature=0.7, max_tokens=512):
            full_response += chunk
            yield f"event: content_chunk\ndata: {json.dumps({'text': chunk, 'agent': 'DSALearn'}, ensure_ascii=False)}\n\n"

        # Step 2: Extract profile (always, for incremental learning)
        try:
            from app.agents.orchestrator import MultiAgentOrchestrator
            orchestrator = MultiAgentOrchestrator()
            profile_result = await orchestrator.run_profile_building(
                student_id=student_id, user_message=message, session_id=session_id,
            )
            profile = profile_result.get("profile", {})
            if profile:
                yield f"event: profile_update\ndata: {json.dumps({'profile': profile}, ensure_ascii=False)}\n\n"
        except Exception as e:
            pass  # Profile extraction is best-effort

        # Step 3: Check for [GENERATE:topic] marker in response
        import re
        gen_match = re.search(r'\[GENERATE:([^\]]+)\]', full_response)
        topic_name = None
        topic_id = None

        if gen_match:
            topic_name = gen_match.group(1).strip()
            topic_id = _match_topic_from_text(topic_name)
        else:
            # Fallback: try to match topic from user message directly
            topic_id = _match_topic_from_text(message)

        # Step 4: Trigger resource generation if topic detected
        if topic_id:
            from app.knowledge_graph.seed_data import get_topic_by_id
            topic = get_topic_by_id(topic_id)
            if topic:
                topic_name = topic["name"]

            yield f"event: progress\ndata: {json.dumps({'step': f'正在为「{topic_name}」生成个性化学习材料...', 'progress': 0.05, 'agent': 'Orchestrator'}, ensure_ascii=False)}\n\n"

            try:
                result = await orchestrator.run_resource_generation(
                    student_id=student_id,
                    topic_id=topic_id,
                    topic_name=topic_name or topic_id,
                    profile={},
                    session_id=f"{session_id}_gen_{topic_id}",
                )

                resources = result.get("generated_resources", [])
                for i, res in enumerate(resources):
                    progress = 0.15 + 0.75 * (i + 1) / max(len(resources), 1)
                    res_type = res.get("type", "unknown")
                    yield f"event: progress\ndata: {json.dumps({'step': f'生成完成: {res_type}', 'progress': round(progress, 2), 'agent': res_type}, ensure_ascii=False)}\n\n"

                    # Emit resource_ready with full content for frontend
                    res_summary = {k: v for k, v in res.items() if k != "content"} if res.get("content") else dict(res)
                    yield f"event: resource_ready\ndata: {json.dumps({'id': res.get('id'), 'topic_id': topic_id, 'resource_type': res.get('type'), 'title': res.get('title'), 'content': res.get('content', ''), 'mindmap': res.get('mindmap', ''), 'questions': res.get('questions', []), 'hints': res.get('hints', []), 'solution': res.get('solution', ''), 'test_cases': res.get('test_cases', []), 'verification': res.get('verification', {}), 'quality': res.get('quality', {})}, ensure_ascii=False)}\n\n"

                    # If lecture, stream content chunks
                    if res.get("type") == "lecture" and res.get("content"):
                        content = res["content"]
                        chunk_size = 200
                        for j in range(0, len(content), chunk_size):
                            yield f"event: content_chunk\ndata: {json.dumps({'text': content[j:j+chunk_size], 'agent': 'ContentGenerator'}, ensure_ascii=False)}\n\n"

                resource_generated = True

                # Quality check
                quality = result.get("quality_checks", [])
                if quality:
                    failed = [q for q in quality if not q["passed"]]
                    yield f"event: progress\ndata: {json.dumps({'step': f'质量检查: {len(quality)-len(failed)}/{len(quality)} 通过', 'progress': 0.93, 'agent': 'Assessor'}, ensure_ascii=False)}\n\n"

            except Exception as e:
                yield f"event: progress\ndata: {json.dumps({'step': f'内容生成遇到问题: {str(e)[:100]}', 'progress': 0.5, 'agent': 'System'}, ensure_ascii=False)}\n\n"

        # Final response
        if resource_generated:
            yield f"event: message\ndata: {json.dumps({'text': f'✅ 已为你生成「{topic_name}」的学习材料！包括课程讲义、思维导图和练习题。你可以切换到学习资源页面查看完整内容。', 'agent': 'DSALearn'}, ensure_ascii=False)}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)[:200]}, ensure_ascii=False)}\n\n"

    yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'resources_generated': resource_generated}, ensure_ascii=False)}\n\n"


@router.post("/session")
async def session_chat(message: ChatMessage):
    """Intelligent chat session — conversation + topic detection + resource generation (SSE)."""
    student_id = message.student_id or "demo_student"
    session_id = message.session_id or str(uuid.uuid4())[:8]

    return StreamingResponse(
        session_chat_stream(student_id, message.content, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/profile")
async def profile_chat(message: ChatMessage):
    """Legacy: dialogue-based profile construction endpoint (SSE)."""
    student_id = message.student_id or "demo_student"
    session_id = message.session_id or str(uuid.uuid4())[:8]
    return StreamingResponse(
        session_chat_stream(student_id, message.content, session_id),
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
    try:
        result = await db.execute(
            select(StudentProfile)
            .where(StudentProfile.student_id == student_id, StudentProfile.is_active == True)
            .order_by(StudentProfile.profile_version.desc())
            .limit(1)
        )
        profile = result.scalars().first()
    except Exception:
        return {"session_id": "", "profile_version": 0, "extracted_dimensions": {}}

    if not profile:
        return {"session_id": "", "profile_version": 0, "extracted_dimensions": {}}

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
