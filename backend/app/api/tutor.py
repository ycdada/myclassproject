"""Tutor API — multi-modal Q&A with streaming."""

import json
import uuid
from typing import Optional, AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


class TutorQuestion(BaseModel):
    student_id: str
    question: str
    topic_id: Optional[str] = None
    session_id: Optional[str] = None


async def tutor_stream(question: TutorQuestion) -> AsyncGenerator[str, None]:
    """SSE streaming for multi-modal tutoring with RAG + Spark."""

    session_id = question.session_id or str(uuid.uuid4())[:8]

    try:
        # Step 1: RAG context retrieval
        yield f"event: agent_thinking\ndata: {json.dumps({'agent': 'Tutor', 'status': 'Searching relevant knowledge...'})}\n\n"

        context = ""
        try:
            from app.services.rag_service import get_rag_service
            rag = await get_rag_service()
            context = await rag.retrieve_context(
                question.question,
                topic_id=question.topic_id,
                max_tokens=1500,
            )
        except Exception as e:
            yield f"event: agent_thinking\ndata: {json.dumps({'agent': 'Tutor', 'status': f'RAG unavailable: {e}'})}\n\n"

        # Step 2: Stream response from Spark Pro
        from app.services.spark_client import SparkProClient

        system_prompt = f"""你是一个耐心、专业的数据结构与算法助教。请回答学生的问题。

{('## 参考资料\n' + context) if context else ''}

## 回答要求
1. 先给出简洁的核心答案（2-3句话）
2. 然后分点详细解释
3. 如果涉及代码，提供 Python 示例
4. 如果涉及概念，给出直观的类比帮助理解
5. 最后提醒常见误区
6. 鼓励学生继续提问"""

        client = SparkProClient()
        async for chunk in client.chat_stream(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question.question},
            ],
            temperature=0.5,
            max_tokens=2048,
        ):
            yield f"event: content_chunk\ndata: {json.dumps({'text': chunk, 'agent': 'Tutor'}, ensure_ascii=False)}\n\n"

        # Step 3: For code questions, provide code example
        if any(kw in question.question.lower() for kw in ["code", "代码", "实现", "implement", "写", "函数", "算法"]):
            try:
                from app.services.spark_client import SparkMaxClient
                code_client = SparkMaxClient()
                code_prompt = f"为以下问题提供一个简短的 Python 代码示例：{question.question[:200]}。只输出 ```python ... ``` 代码块。"
                code_resp = await code_client.chat(
                    [{"role": "user", "content": code_prompt}],
                    temperature=0.3, max_tokens=1024,
                )
                import re
                match = re.search(r'```python\n(.*?)```', code_resp, re.DOTALL)
                if match:
                    yield f"event: code\ndata: {json.dumps({'code': match.group(1), 'language': 'python'}, ensure_ascii=False)}\n\n"
            except Exception:
                pass

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"

    yield f"event: done\ndata: {json.dumps({'session_id': session_id}, ensure_ascii=False)}\n\n"


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
