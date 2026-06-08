"""
Multi-Agent Orchestrator using LangGraph StateGraph.

Coordinates 9 specialized agents for personalized DSA learning:
- Orchestrator: central coordinator, intent routing
- Profile Analyzer: 6+ dimension student profiling
- Curriculum Planner: learning path planning with knowledge graph
- Content Generator: lecture docs, reading materials
- Exercise Designer: 5 types of practice questions
- Multimedia Creator: mind maps, diagrams, video scripts
- Code Mentor: code examples, sandbox execution
- Tutor: multi-modal Q&A
- Assessor: quality review & learning assessment
"""

import logging
import re
import time
import json as json_module
from typing import TypedDict, List, Optional, Annotated, Literal
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ========================
# State Definitions
# ========================

class StudentProfile(TypedDict, total=False):
    knowledge_foundation: dict       # {topic_id: mastery_level 0-1}
    cognitive_style: str             # visual / auditory / kinesthetic / reading
    error_prone_areas: List[str]
    learning_pace: float             # hours per topic
    preferred_resource_types: List[str]  # [video, text, exercise, mindmap, code]
    motivation_level: str            # high / medium / low
    attention_span: str              # short / medium / long
    goal: str                        # exam_prep / interview / course_study
    prior_courses: List[str]


class AgentState(TypedDict, total=False):
    """Shared state across all agents in the LangGraph workflow."""
    messages: Annotated[List, add_messages]
    student_id: str
    profile: StudentProfile
    current_topic_id: str
    current_topic_name: str
    intent: str                      # profile_building / resource_generation / tutoring / assessment
    learning_path: List[dict]
    generated_resources: List[dict]
    assessment_results: List[dict]
    quality_checks: List[dict]
    streaming_events: List[dict]     # SSE events to emit
    error: Optional[str]


class Intent(str, Enum):
    PROFILE_BUILDING = "profile_building"
    RESOURCE_GENERATION = "resource_generation"
    LEARNING_PATH = "learning_path"
    TUTORING = "tutoring"
    ASSESSMENT = "assessment"
    EXERCISE = "exercise"


# ========================
# Profile Extraction Function Schema
# ========================

PROFILE_EXTRACTION_FUNCTIONS = [
    {
        "name": "update_student_profile",
        "description": "从学生对话中提取学习画像维度。仅提取有明确证据的维度，对于不确定的维度不要猜测。",
        "parameters": {
            "type": "object",
            "properties": {
                "knowledge_foundation": {
                    "type": "object",
                    "description": "已知DSA知识点掌握程度映射，格式: {topic_name: 0-1 mastery}。仅当学生明确提及时填写。",
                    "additionalProperties": {"type": "number"}
                },
                "cognitive_style": {
                    "type": "string",
                    "enum": ["visual", "auditory", "kinesthetic", "reading"],
                    "description": "认知风格偏好"
                },
                "error_prone_areas": {
                    "type": "array", "items": {"type": "string"},
                    "description": "学生自述的易错知识点或概念"
                },
                "learning_pace": {
                    "type": "number",
                    "description": "学习速度预估（小时/知识点），保守估计"
                },
                "preferred_resource_types": {
                    "type": "array", "items": {"type": "string"},
                    "enum": ["video", "text", "exercise", "mindmap", "code"],
                    "description": "偏好的学习资源类型"
                },
                "motivation_level": {
                    "type": "string", "enum": ["high", "medium", "low"]
                },
                "attention_span": {
                    "type": "string", "enum": ["short", "medium", "long"]
                },
                "goal": {
                    "type": "string",
                    "enum": ["exam_prep", "interview", "course_study"],
                    "description": "学习目标"
                },
                "prior_courses": {
                    "type": "array", "items": {"type": "string"},
                    "description": "已修相关课程列表"
                },
                "confidence": {
                    "type": "number",
                    "description": "整体提取置信度 0-1。多数维度无明确证据时设为低值。"
                }
            },
            "required": ["confidence"]
        }
    }
]

PROFILE_SYSTEM_PROMPT = """你是一个学习分析专家，通过与学生对话来分析其学习画像。

请从学生的回答中提取以下维度的信息（仅提取有明确证据的维度）：
- knowledge_foundation: 学生提到过哪些数据结构与算法知识点？掌握程度如何？（{topic_name: 0-1 mastery}）
- cognitive_style: 学生更喜欢看图、听讲、动手实践还是阅读文本？
- error_prone_areas: 学生提到过哪些容易出错的知识点？
- learning_pace: 学生的学习节奏如何？
- preferred_resource_types: 学生偏好哪些资源类型？(video/text/exercise/mindmap/code)
- motivation_level: 学生的学习动力如何？(high/medium/low)
- attention_span: 学生注意力持续时间如何？(short/medium/long)
- goal: 学生的学习目标是什么？(exam_prep/interview/course_study)
- prior_courses: 学生之前学过哪些相关课程？

对于不确定的维度，不要强行猜测。confidence 应反映你整体的置信度。"""


def _merge_profile(existing: dict, new_data: dict) -> dict:
    """Merge extracted profile data into existing profile, with version tracking."""
    merged = dict(existing)
    confidence = new_data.get("confidence", 0.0)

    # Merge knowledge_foundation (dict merge)
    if "knowledge_foundation" in new_data and new_data["knowledge_foundation"]:
        kf = dict(merged.get("knowledge_foundation", {}))
        kf.update(new_data["knowledge_foundation"])
        merged["knowledge_foundation"] = kf

    # Merge list fields (union)
    for field in ["error_prone_areas", "preferred_resource_types", "prior_courses"]:
        if field in new_data and new_data[field]:
            existing_set = set(merged.get(field, []))
            existing_set.update(new_data[field])
            merged[field] = list(existing_set)

    # Scalar fields: update if confidence is reasonable
    scalar_fields = ["cognitive_style", "learning_pace", "motivation_level",
                     "attention_span", "goal"]
    for field in scalar_fields:
        if field in new_data and new_data[field] and confidence >= 0.4:
            merged[field] = new_data[field]

    return merged


# ========================
# Agent Node Implementations
# ========================

async def orchestrator_node(state: AgentState) -> AgentState:
    """Route user intent to the appropriate agent pipeline."""
    intent = state.get("intent", Intent.PROFILE_BUILDING)
    logger.info(f"Orchestrator routing intent: {intent}")

    state["streaming_events"] = state.get("streaming_events", [])
    state["streaming_events"].append({
        "event": "agent_thinking",
        "data": {"agent": "Orchestrator", "status": f"Routing to {intent} pipeline..."}
    })

    return state


async def profile_analyzer_node(state: AgentState) -> AgentState:
    """Analyze user dialogue to extract/update 6+ profile dimensions via Spark Pro function calling."""
    logger.info("Profile Analyzer: analyzing student profile...")

    messages = state.get("messages", [])
    last_user_msg = ""
    for msg in reversed(messages):
        role = msg.get("role", "") if isinstance(msg, dict) else getattr(msg, "type", "")
        content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
        if role in ("user", "human"):
            last_user_msg = content
            break

    if not last_user_msg:
        state["profile"] = state.get("profile", {})
        return state

    profile = state.get("profile", {})
    if not profile:
        profile = {
            "knowledge_foundation": {},
            "cognitive_style": "",
            "error_prone_areas": [],
            "learning_pace": 1.0,
            "preferred_resource_types": [],
            "motivation_level": "medium",
            "attention_span": "medium",
            "goal": "course_study",
            "prior_courses": [],
        }

    try:
        from app.services.spark_client import SparkProClient
        client = SparkProClient()
        spark_messages = [
            {"role": "system", "content": PROFILE_SYSTEM_PROMPT},
            {"role": "user", "content": last_user_msg},
        ]
        result = await client.chat_with_function_calling(
            spark_messages,
            functions=PROFILE_EXTRACTION_FUNCTIONS,
            temperature=settings.TEMPERATURE_FACTUAL,
        )

        if isinstance(result, dict) and "function_call" in result:
            args = result["function_call"].get("arguments", {})
            profile = _merge_profile(profile, args)
            logger.info(f"Profile updated with confidence: {args.get('confidence', 'N/A')}")
        elif isinstance(result, dict) and "raw_response" in result:
            logger.info(f"Profile extraction returned raw response (no function call)")
    except Exception as e:
        logger.error(f"Profile extraction failed: {e}")
        state["error"] = f"Profile extraction error: {str(e)}"

    state["profile"] = profile
    state["streaming_events"] = state.get("streaming_events", [])
    state["streaming_events"].append({
        "event": "profile_update",
        "data": {"agent": "ProfileAnalyzer", "dimensions_updated": list(profile.keys())}
    })
    return state


async def curriculum_planner_node(state: AgentState) -> AgentState:
    """Plan personalized learning path using DSA knowledge graph with profile-driven strategy."""
    logger.info("Curriculum Planner: generating learning path...")

    profile = state.get("profile", {})
    knowledge = profile.get("knowledge_foundation", {})
    goal = profile.get("goal", "course_study")

    try:
        from app.knowledge_graph.dsa_graph import get_knowledge_graph, PathStrategy

        kg = get_knowledge_graph()
        completed = [tid for tid, mastery in knowledge.items() if mastery > 0.8]

        # Select strategy based on goal
        strategy_map = {
            "exam_prep": PathStrategy.STANDARD,
            "interview": PathStrategy.DIFFICULTY_ASC,
            "course_study": PathStrategy.STANDARD,
        }
        strategy = strategy_map.get(goal, PathStrategy.STANDARD)

        path_nodes = kg.generate_learning_path(completed, strategy=strategy)
        learning_pace = profile.get("learning_pace", 1.0)

        learning_path = []
        for node in path_nodes:
            learning_path.append({
                "topic_id": node.topic_id,
                "topic_name": node.topic_name,
                "order": node.order,
                "difficulty": node.difficulty,
                "category": node.category,
                "status": node.status,
                "estimated_hours": round(node.estimated_hours / max(learning_pace, 0.1), 1),
            })

        state["learning_path"] = learning_path
        state["streaming_events"].append({
            "event": "progress",
            "data": {"agent": "CurriculumPlanner", "path_length": len(learning_path)}
        })
    except Exception as e:
        logger.error(f"Path planning failed: {e}")
        state["error"] = f"Path planning error: {str(e)}"
        state["learning_path"] = []

    return state


async def content_generator_node(state: AgentState) -> AgentState:
    """Generate lecture documents and extended reading via RAG + Spark Max."""
    logger.info("Content Generator: creating learning materials...")

    topic_id = state.get("current_topic_id", "")
    topic_name = state.get("current_topic_name", "")
    profile = state.get("profile", {})

    # RAG retrieval
    try:
        from app.services.rag_service import get_rag_service
        rag = await get_rag_service()
        query = f"{topic_name} {topic_id} 核心概念 算法原理 时间复杂度"
        context = await rag.retrieve_context(query, topic_id=topic_id, max_tokens=2000)
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}, continuing without context")
        context = ""

    # Build personalization instructions
    cognitive_style = profile.get("cognitive_style", "visual")
    style_instructions = {
        "visual": "多使用图表描述和空间类比，用文字描述可视化效果。多使用"例如"和场景化描述。",
        "auditory": "使用节奏感和口语化解释，多用"首先...然后...最后"的叙述方式。",
        "kinesthetic": "多提供动手练习建议和交互式思考题，强调实际操作步骤。",
        "reading": "提供详细的理论推导和严谨的文字描述，包含定义、定理、证明。",
    }.get(cognitive_style, "使用平衡的教学风格，结合图文并茂的讲解方式。")

    system_prompt = f"""你是一个数据结构与算法教学专家。请基于提供的参考资料，为「{topic_name}」生成一份高质量的学习讲义。

## 学生画像
- 认知风格: {cognitive_style}
- 学习目标: {profile.get('goal', 'course_study')}
- 当前掌握度: {profile.get('knowledge_foundation', {}).get(topic_id, 0.0)}

## 教学风格指导
{style_instructions}

## 参考资料
{context if context else '（无额外参考资料，请使用你的专业知识。）'}

## 输出要求
1. 使用 Markdown 格式，包含 LaTeX 数学公式（包裹在 $$ 或 $ 中）
2. 包含以下章节：概念定义、核心性质与原理、算法步骤（伪代码）、复杂度分析、Python 代码示例（```python```）、常见误区
3. 难度适中，适合大学生阅读
4. Python 代码必须是可运行的
5. 总长度控制在 1500-2500 字"""

    content = ""
    try:
        from app.services.spark_client import SparkMaxClient
        client = SparkMaxClient()
        content = await client.chat(
            [{"role": "system", "content": system_prompt}],
            temperature=settings.TEMPERATURE_FACTUAL,
            max_tokens=settings.MAX_GENERATION_TOKENS,
        )
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        state["error"] = f"Content generation error: {str(e)}"
        content = f"# {topic_name}\n\n内容生成失败，请重试。\n\n错误信息: {str(e)}"

    # Safety check
    quality = {"safety_score": 1.0, "hallucination_score": 1.0, "safety_issues": [], "hallucination_issues": []}
    try:
        from app.safety.content_filter import ContentSafetyFilter
        safety = ContentSafetyFilter()
        safety_result = safety.filter(content, resource_type="lecture")
        quality["safety_score"] = safety_result.score
        quality["safety_issues"] = safety_result.issues

        code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
        if code_blocks and settings.ENABLE_CODE_SANDBOX:
            from app.safety.hallucination_check import HallucinationChecker
            checker = HallucinationChecker(enable_sandbox=True)
            hallu_result = checker.check_all(content, resource_type="lecture", code_blocks=code_blocks)
            quality["hallucination_score"] = hallu_result.score
            quality["hallucination_issues"] = hallu_result.issues
    except Exception as e:
        logger.warning(f"Safety check failed: {e}")

    resource = {
        "id": f"res_{topic_id}_lecture_{int(time.time())}",
        "type": "lecture",
        "title": f"学习讲义: {topic_name}",
        "content": content,
        "personalization": {
            "cognitive_style": cognitive_style,
            "difficulty_adj": profile.get("learning_pace", 1.0),
        },
        "quality": quality,
        "rag_context_used": bool(context),
    }

    resources = state.get("generated_resources", [])
    resources.append(resource)
    state["generated_resources"] = resources

    state.setdefault("streaming_events", []).append({
        "event": "resource_ready",
        "data": {"type": "lecture", "id": resource["id"]}
    })
    return state


async def exercise_designer_node(state: AgentState) -> AgentState:
    """Design 5 types of practice questions via Spark Max structured output."""
    logger.info("Exercise Designer: creating practice questions...")

    topic_id = state.get("current_topic_id", "")
    topic_name = state.get("current_topic_name", "")
    profile = state.get("profile", {})
    error_areas = profile.get("error_prone_areas", [])

    question_types = ["multiple_choice", "true_false", "short_answer", "fill_blank", "coding"]

    system_prompt = f"""你是一个数据结构与算法练习题设计专家。请为「{topic_name}」生成练习题。

## 要求
- 生成 5 类题型，每类 2 道，共 10 道题
- 题型: multiple_choice / true_false / short_answer / fill_blank / coding
- 针对学生弱点领域多出题: {error_areas if error_areas else '无特殊要求'}
- 难度: 基础题6道(难度1-2)，进阶题4道(难度3-4)

## 输出格式（严格JSON数组，不要有其他内容）
```json
[
  {{
    "question_type": "multiple_choice",
    "difficulty": 2,
    "question_text": "题目标题",
    "options": [{{"key": "A", "value": "选项A"}}, {{"key": "B", "value": "选项B"}}, {{"key": "C", "value": "选项C"}}, {{"key": "D", "value": "选项D"}}],
    "correct_answer": "B",
    "explanation": "详细解析",
    "hints": ["渐进式提示1", "提示2"],
    "knowledge_points": ["知识点"],
    "bloom_level": "understand"
  }}
]
```"""

    questions = []
    try:
        from app.services.spark_client import SparkMaxClient
        client = SparkMaxClient()
        response = await client.chat(
            [{"role": "system", "content": system_prompt}],
            temperature=0.5,
            max_tokens=4096,
        )
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            questions = json_module.loads(json_match.group(0))
            logger.info(f"Generated {len(questions)} exercises for {topic_name}")
        else:
            logger.warning(f"Could not extract JSON from exercise response")
    except Exception as e:
        logger.error(f"Exercise generation failed: {e}")
        state["error"] = f"Exercise generation error: {str(e)}"

    resource = {
        "id": f"res_{topic_id}_exercise_{int(time.time())}",
        "type": "exercise",
        "topic_id": topic_id,
        "title": f"练习题: {topic_name}",
        "questions": questions,
        "total_questions": len(questions),
        "focus_areas": error_areas,
    }

    resources = state.get("generated_resources", [])
    resources.append(resource)
    state["generated_resources"] = resources
    return state


async def multimedia_creator_node(state: AgentState) -> AgentState:
    """Generate mind maps and diagrams using Spark + Mermaid.js."""
    logger.info("Multimedia Creator: generating visual content...")

    topic_id = state.get("current_topic_id", "")
    topic_name = state.get("current_topic_name", "")

    # Build mindmap from topic hierarchy
    try:
        from app.knowledge_graph.dsa_graph import get_knowledge_graph
        kg = get_knowledge_graph()
        topic = kg.get_topic(topic_id)

        mindmap_mermaid = "mindmap\n"
        if topic:
            mindmap_mermaid += f"  root(({topic['name']}))\n"
            # Add prerequisites
            prereqs = kg.get_prerequisites(topic_id)
            for i, p in enumerate(prereqs[:5]):
                mindmap_mermaid += f"    前置知识\n      {p['name']}\n"
            # Add learning objectives
            for obj in topic.get("learning_objectives", [])[:5]:
                mindmap_mermaid += f"    学习目标\n      {obj['objective'][:20]}...\n"
            # Add misconceptions
            for mc in topic.get("common_misconceptions", [])[:3]:
                mindmap_mermaid += f"    常见误区\n      {mc[:30]}...\n"
        else:
            from app.services.spark_client import SparkProClient
            client = SparkProClient()
            mermaid_prompt = f"为「{topic_name}」生成一个 Mermaid.js mindmap，包含概念定义、核心性质、操作和应用场景。只输出 ```mermaid ... ``` 代码块。"
            response = await client.chat(
                [{"role": "user", "content": mermaid_prompt}],
                temperature=0.3, max_tokens=1024,
            )
            mm_match = re.search(r'```mermaid\n(.*?)```', response, re.DOTALL)
            if mm_match:
                mindmap_mermaid = mm_match.group(1)
            else:
                mindmap_mermaid = f"mindmap\n  root(({topic_name}))\n    Concepts\n    Operations\n    Applications"
    except Exception as e:
        logger.warning(f"Mindmap generation failed: {e}")
        mindmap_mermaid = f"mindmap\n  root(({topic_name}))\n    概念\n    性质\n    应用"

    resource = {
        "id": f"res_{topic_id}_multimedia_{int(time.time())}",
        "type": "multimedia",
        "title": f"思维导图: {topic_name}",
        "mindmap": mindmap_mermaid,
        "diagram_url": f"/api/files/{topic_id}_diagram.png",
    }

    resources = state.get("generated_resources", [])
    resources.append(resource)
    state["generated_resources"] = resources
    return state


async def code_mentor_node(state: AgentState) -> AgentState:
    """Generate runnable code examples with sandbox verification."""
    logger.info("Code Mentor: creating code examples...")

    topic_id = state.get("current_topic_id", "")
    topic_name = state.get("current_topic_name", "")

    system_prompt = f"""你是一个数据结构与算法编程导师。请为「{topic_name}」生成一个完整的 Python 代码示例。

## 要求
1. 生成一个可运行的 Python 实现
2. 包含测试用例（至少3个）
3. 代码注释清晰
4. 输出格式（严格 JSON）：
```json
{{
  "starter_code": "带 # TODO 注释的初始代码",
  "solution": "完整可运行代码",
  "test_cases": [{{"input": "测试输入", "expected": "期望输出"}}],
  "hints": ["渐进提示1", "提示2", "提示3"]
}}
```"""

    code_data = {}
    try:
        from app.services.spark_client import SparkMaxClient
        client = SparkMaxClient()
        response = await client.chat(
            [{"role": "system", "content": system_prompt}],
            temperature=settings.TEMPERATURE_FACTUAL,
            max_tokens=3072,
        )
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            code_data = json_module.loads(json_match.group(0))
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        code_data = {"solution": f"# Error generating code: {e}"}

    # Sandbox verification
    verification = {"passed": False, "stdout": "", "stderr": ""}
    solution = code_data.get("solution", "")
    if solution and settings.ENABLE_CODE_SANDBOX:
        try:
            from app.safety.hallucination_check import CodeSandbox
            success, stdout, stderr = CodeSandbox.execute(solution)
            verification = {"passed": success, "stdout": stdout, "stderr": stderr}
            if not success:
                # Retry once with error feedback
                retry_prompt = f"The code had this error: {stderr}. Please fix it."
                response = await client.chat([
                    {"role": "system", "content": system_prompt},
                    {"role": "assistant", "content": response},
                    {"role": "user", "content": retry_prompt}
                ], temperature=0.3, max_tokens=3072)
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    code_data = json_module.loads(json_match.group(0))
                    solution = code_data.get("solution", solution)
                    success, stdout, stderr = CodeSandbox.execute(solution)
                    verification = {"passed": success, "stdout": stdout, "stderr": stderr}
        except Exception as e:
            logger.warning(f"Sandbox verification failed: {e}")

    resource = {
        "id": f"res_{topic_id}_code_{int(time.time())}",
        "type": "code",
        "title": f"代码实操: {topic_name}",
        "language": "python",
        "starter_code": code_data.get("starter_code", "# TODO: Implement solution"),
        "solution": solution,
        "test_cases": code_data.get("test_cases", []),
        "hints": code_data.get("hints", []),
        "verification": verification,
    }

    resources = state.get("generated_resources", [])
    resources.append(resource)
    state["generated_resources"] = resources
    return state


async def tutor_node(state: AgentState) -> AgentState:
    """Provide multi-modal tutoring response (text + diagram + audio)."""
    logger.info("Tutor Agent: preparing multi-modal response...")

    messages = state.get("messages", [])
    last_question = ""
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == "human":
            last_question = msg.content
            break

    # TODO: RAG retrieval for relevant knowledge
    # TODO: Generate text explanation (Spark Pro, streaming)
    # TODO: Generate diagram (Spark Image API)
    # TODO: Generate audio (讯飞 TTS)

    state["streaming_events"].append({
        "event": "content_chunk",
        "data": {"agent": "Tutor", "text": f"Answering: {last_question[:50]}..."}
    })

    return state


async def assessor_node(state: AgentState) -> AgentState:
    """Quality gate: run safety & hallucination checks on all generated resources."""
    logger.info("Assessor: reviewing content quality...")

    resources = state.get("generated_resources", [])

    try:
        from app.safety.content_filter import ContentSafetyFilter
        from app.safety.hallucination_check import HallucinationChecker

        safety = ContentSafetyFilter()
        checker = HallucinationChecker(enable_sandbox=settings.ENABLE_CODE_SANDBOX)

        quality_results = []
        for res in resources:
            content = res.get("content", "")
            if not content:
                # For non-text resources (exercise data, etc.)
                content = str(res.get("questions", res.get("mindmap", "")))

            if not content:
                quality_results.append({"resource_id": res.get("id"), "passed": True,
                    "score": 1.0, "issues": []})
                continue

            safety_result = safety.filter(content, resource_type=res.get("type", ""))
            code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL) if res.get("type") in ("lecture", "code") else None
            hallu_result = checker.check_all(content, resource_type=res.get("type"), code_blocks=code_blocks)

            passed = safety_result.passed and hallu_result.score > 0.5
            quality_results.append({
                "resource_id": res.get("id"),
                "passed": passed,
                "safety_score": safety_result.score,
                "hallucination_score": hallu_result.score,
                "safety_issues": safety_result.issues,
                "hallucination_issues": hallu_result.issues,
            })

        state["quality_checks"] = quality_results
        failed = [q for q in quality_results if not q["passed"]]
        state["streaming_events"] = state.get("streaming_events", [])
        state["streaming_events"].append({
            "event": "progress",
            "data": {"agent": "Assessor", "status": f"Quality check complete. Passed: {len(quality_results) - len(failed)}/{len(quality_results)}"}
        })
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        state["error"] = f"Assessment error: {str(e)}"
        state["quality_checks"] = []

    return state


# ========================
# Routing Functions
# ========================

def route_by_intent(state: AgentState) -> str:
    """Route to the appropriate pipeline based on intent."""
    intent = state.get("intent", Intent.PROFILE_BUILDING)

    routing_map = {
        Intent.PROFILE_BUILDING: "profile_analyzer",
        Intent.LEARNING_PATH: "curriculum_planner",
        Intent.RESOURCE_GENERATION: "content_generator",
        Intent.EXERCISE: "exercise_designer",
        Intent.TUTORING: "tutor",
        Intent.ASSESSMENT: "assessor",
    }

    return routing_map.get(intent, "profile_analyzer")


def should_continue_generation(state: AgentState) -> Literal["multimedia_creator", "assessor"]:
    """After content generation, continue to multimedia or go to assessment."""
    resources = state.get("generated_resources", [])
    has_multimedia = any(r.get("type") == "multimedia" for r in resources)
    if not has_multimedia:
        return "multimedia_creator"
    return "assessor"


# ========================
# Build the StateGraph
# ========================

def build_orchestrator_graph() -> StateGraph:
    """Build the complete multi-agent orchestration graph."""

    workflow = StateGraph(AgentState)

    # Add all agent nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("profile_analyzer", profile_analyzer_node)
    workflow.add_node("curriculum_planner", curriculum_planner_node)
    workflow.add_node("content_generator", content_generator_node)
    workflow.add_node("exercise_designer", exercise_designer_node)
    workflow.add_node("multimedia_creator", multimedia_creator_node)
    workflow.add_node("code_mentor", code_mentor_node)
    workflow.add_node("tutor", tutor_node)
    workflow.add_node("assessor", assessor_node)

    # Set entry point
    workflow.set_entry_point("orchestrator")

    # Conditional routing from orchestrator
    workflow.add_conditional_edges(
        "orchestrator",
        route_by_intent,
        {
            "profile_analyzer": "profile_analyzer",
            "curriculum_planner": "curriculum_planner",
            "content_generator": "content_generator",
            "exercise_designer": "exercise_designer",
            "tutor": "tutor",
            "assessor": "assessor",
        }
    )

    # Profile analyzer → curriculum planner (for path generation after profile update)
    workflow.add_edge("profile_analyzer", "curriculum_planner")

    # Curriculum planner → content generator (generate resources for first topic)
    workflow.add_edge("curriculum_planner", "content_generator")

    # Content generator → exercise designer
    workflow.add_edge("content_generator", "exercise_designer")

    # Exercise designer → code mentor (generate code examples)
    workflow.add_edge("exercise_designer", "code_mentor")

    # Code mentor → multimedia creator
    workflow.add_edge("code_mentor", "multimedia_creator")

    # Multimedia creator → assessor (quality review)
    workflow.add_edge("multimedia_creator", "assessor")

    # Assessor → END
    workflow.add_edge("assessor", END)

    # Tutor → assessor (review tutoring quality)
    workflow.add_edge("tutor", "assessor")

    return workflow


# ========================
# Orchestrator Class
# ========================

class MultiAgentOrchestrator:
    """Main orchestrator class for the multi-agent system."""

    def __init__(self):
        self.graph = build_orchestrator_graph()
        self.memory = MemorySaver()
        self.app = self.graph.compile(checkpointer=self.memory)

    async def run_profile_building(
        self, student_id: str, user_message: str, session_id: str = "default"
    ) -> AgentState:
        """Run the profile building pipeline."""
        initial_state: AgentState = {
            "messages": [{"role": "user", "content": user_message}],
            "student_id": student_id,
            "intent": Intent.PROFILE_BUILDING,
        }
        config = {"configurable": {"thread_id": session_id}}
        result = await self.app.ainvoke(initial_state, config)
        return result

    async def run_resource_generation(
        self, student_id: str, topic_id: str, topic_name: str, profile: StudentProfile,
        session_id: str = "default"
    ) -> AgentState:
        """Run the full resource generation pipeline for a topic."""
        initial_state: AgentState = {
            "student_id": student_id,
            "current_topic_id": topic_id,
            "current_topic_name": topic_name,
            "profile": profile,
            "intent": Intent.RESOURCE_GENERATION,
        }
        config = {"configurable": {"thread_id": session_id}}
        result = await self.app.ainvoke(initial_state, config)
        return result

    async def run_tutoring(
        self, student_id: str, question: str, topic_id: Optional[str] = None,
        session_id: str = "default"
    ) -> AgentState:
        """Run the tutoring pipeline."""
        initial_state: AgentState = {
            "messages": [{"role": "user", "content": question}],
            "student_id": student_id,
            "current_topic_id": topic_id or "",
            "intent": Intent.TUTORING,
        }
        config = {"configurable": {"thread_id": session_id}}
        result = await self.app.ainvoke(initial_state, config)
        return result

    async def get_state(self, session_id: str) -> Optional[AgentState]:
        """Get current state for a session."""
        config = {"configurable": {"thread_id": session_id}}
        state = await self.app.aget_state(config)
        return state.values if state else None
