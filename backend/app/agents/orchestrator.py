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
from typing import TypedDict, List, Optional, Annotated, Literal
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)


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
    """Analyze user dialogue to extract/update 6+ profile dimensions."""
    logger.info("Profile Analyzer: analyzing student profile...")

    # Extract profile from conversation messages
    messages = state.get("messages", [])
    last_user_msg = ""
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == "human":
            last_user_msg = msg.content
            break

    profile = state.get("profile", {})

    # Initialize empty profile if needed
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

    # TODO: Integrate Spark Pro for NL feature extraction via function calling
    # This would analyze last_user_msg and update profile dimensions

    state["profile"] = profile
    state["streaming_events"].append({
        "event": "profile_update",
        "data": {"agent": "ProfileAnalyzer", "dimensions_updated": list(profile.keys())}
    })

    return state


async def curriculum_planner_node(state: AgentState) -> AgentState:
    """Plan personalized learning path using DSA knowledge graph."""
    logger.info("Curriculum Planner: generating learning path...")

    profile = state.get("profile", {})
    knowledge = profile.get("knowledge_foundation", {})
    goal = profile.get("goal", "course_study")

    # TODO: Traverse DSA knowledge graph with topological sort
    # Weight edges by: difficulty, student mastery, goal relevance, pace

    from app.knowledge_graph.seed_data import topological_order, get_topic_by_id

    ordered_topics = topological_order()
    learning_path = []

    for idx, topic_id in enumerate(ordered_topics):
        topic = get_topic_by_id(topic_id)
        if topic:
            current_mastery = knowledge.get(topic_id, 0.0)
            learning_path.append({
                "topic_id": topic_id,
                "topic_name": topic["name"],
                "order": idx + 1,
                "difficulty": topic["difficulty_level"],
                "category": topic["category"],
                "current_mastery": current_mastery,
                "status": "completed" if current_mastery > 0.8 else "pending",
                "estimated_hours": topic["difficulty_level"] * 2.0,
            })

    state["learning_path"] = learning_path
    state["streaming_events"].append({
        "event": "progress",
        "data": {"agent": "CurriculumPlanner", "path_length": len(learning_path)}
    })

    return state


async def content_generator_node(state: AgentState) -> AgentState:
    """Generate lecture documents and extended reading materials."""
    logger.info("Content Generator: creating learning materials...")

    topic_id = state.get("current_topic_id", "")
    profile = state.get("profile", {})

    # TODO: Use Spark Max + RAG to generate personalized content
    # 1. Retrieve relevant DSA textbook context via pgvector
    # 2. Build prompt with profile personalization (e.g., visual learner → more diagrams)
    # 3. Generate Markdown with LaTeX formulas
    # 4. Run through safety filter

    resource = {
        "id": f"res_{topic_id}_lecture",
        "type": "lecture",
        "title": f"Lecture: {state.get('current_topic_name', topic_id)}",
        "content": "Generated lecture content placeholder...",
        "personalization": {
            "cognitive_style": profile.get("cognitive_style", "visual"),
            "difficulty_adj": profile.get("learning_pace", 1.0),
        },
    }

    resources = state.get("generated_resources", [])
    resources.append(resource)
    state["generated_resources"] = resources

    return state


async def exercise_designer_node(state: AgentState) -> AgentState:
    """Design 5 types of practice questions with calibrated difficulty."""
    logger.info("Exercise Designer: creating practice questions...")

    topic_id = state.get("current_topic_id", "")
    profile = state.get("profile", {})
    error_areas = profile.get("error_prone_areas", [])

    question_types = ["multiple_choice", "true_false", "short_answer", "fill_blank", "coding"]

    # TODO: Use Spark Max to generate questions targeting weak areas
    # Each question tagged with: knowledge_point, difficulty, bloom_level

    exercise = {
        "id": f"ex_{topic_id}",
        "topic_id": topic_id,
        "question_types": question_types,
        "total_questions": len(question_types) * 3,  # 3 per type
        "focus_areas": error_areas,
    }

    resources = state.get("generated_resources", [])
    resources.append({"id": f"res_{topic_id}_exercise", "type": "exercise", "data": exercise})
    state["generated_resources"] = resources

    return state


async def multimedia_creator_node(state: AgentState) -> AgentState:
    """Generate mind maps, diagrams, and video/animation scripts."""
    logger.info("Multimedia Creator: generating visual content...")

    topic_id = state.get("current_topic_id", "")
    topic_name = state.get("current_topic_name", "")

    # TODO: Generate Mermaid.js mind map from topic hierarchy
    # TODO: Generate diagram via Spark Image API
    # TODO: Generate Manim animation script for algorithm visualization
    # TODO: Generate TTS narration script

    mindmap_mermaid = f"""mindmap
  root(({topic_name}))
    ::id: {topic_id}
    Basic Concepts
      Definition
      Properties
    Operations
      Insert
      Delete
      Search
    Applications
      Real-world use cases
      Related algorithms"""

    resource = {
        "id": f"res_{topic_id}_multimedia",
        "type": "multimedia",
        "title": f"Visual Guide: {topic_name}",
        "mindmap": mindmap_mermaid,
        "diagram_url": f"/api/files/{topic_id}_diagram.png",
        "video_script": f"Animation script for {topic_name}...",
    }

    resources = state.get("generated_resources", [])
    resources.append(resource)
    state["generated_resources"] = resources

    return state


async def code_mentor_node(state: AgentState) -> AgentState:
    """Generate runnable code examples with tests and progressive hints."""
    logger.info("Code Mentor: creating code examples...")

    topic_id = state.get("current_topic_id", "")
    topic_name = state.get("current_topic_name", "")

    # TODO: Generate language-appropriate code examples
    # TODO: Include test cases
    # TODO: Progressive hints (hint_1, hint_2, solution)
    # TODO: Execute in sandbox to verify correctness

    code_example = {
        "id": f"res_{topic_id}_code",
        "type": "code",
        "title": f"Hands-on: {topic_name}",
        "language": "python",
        "starter_code": f"# TODO: Implement {topic_name}\ndef solution():\n    pass\n",
        "test_cases": [],
        "hints": ["Hint 1: Consider the base case first", "Hint 2: Think about the recursive structure"],
        "solution": "# Complete solution placeholder",
    }

    resources = state.get("generated_resources", [])
    resources.append(code_example)
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
    """Quality gate: review generated content and assess learning outcomes."""
    logger.info("Assessor: reviewing content quality...")

    resources = state.get("generated_resources", [])

    # TODO: Run hallucination checks
    # TODO: Content safety filter
    # TODO: Difficulty calibration check
    # TODO: Score each resource

    quality_results = []
    for res in resources:
        quality_results.append({
            "resource_id": res.get("id"),
            "passed": True,
            "score": 0.9,
            "issues": [],
        })

    state["quality_checks"] = quality_results
    state["streaming_events"].append({
        "event": "progress",
        "data": {"agent": "Assessor", "status": "Quality check complete", "resources_reviewed": len(resources)}
    })

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
