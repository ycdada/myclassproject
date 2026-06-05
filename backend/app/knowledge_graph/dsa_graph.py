"""
DSA Knowledge Graph - graph operations and traversal algorithms.

Provides:
- Topological sorting for learning path generation
- Prerequisite chain resolution
- Difficulty-weighted path planning
- Personalized topic ordering based on student profile
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.knowledge_graph.seed_data import (
    DSA_TOPICS,
    get_topic_by_id,
    get_prerequisite_chain,
    topological_order,
    build_adjacency_list,
)


class PathStrategy(str, Enum):
    STANDARD = "standard"           # Topological order
    DIFFICULTY_ASC = "difficulty_asc"    # Easiest first
    DEPTH_FIRST = "depth_first"     # Follow one branch deep first
    GOAL_ORIENTED = "goal_oriented"  # Fastest path to goal topic


@dataclass
class PathNode:
    topic_id: str
    topic_name: str
    difficulty: int
    category: str
    order: int
    prerequisites_met: bool
    estimated_hours: float
    status: str  # locked / available / in_progress / completed


class DSAKnowledgeGraph:
    """DSA Knowledge Graph with path planning capabilities."""

    def __init__(self):
        self.topics = {t["id"]: t for t in DSA_TOPICS}
        self.adjacency = build_adjacency_list()

    def get_topic(self, topic_id: str) -> Optional[dict]:
        return self.topics.get(topic_id)

    def get_all_topics(self) -> List[dict]:
        return list(self.topics.values())

    def get_topics_by_category(self, category: str) -> List[dict]:
        return [t for t in self.topics.values() if t["category"] == category]

    def get_topological_order(self) -> List[str]:
        """Get topics in topologically sorted order."""
        return topological_order()

    def get_prerequisites(self, topic_id: str) -> List[dict]:
        """Get all prerequisites for a topic, recursively."""
        topic = self.get_topic(topic_id)
        if not topic:
            return []
        result = []
        for prereq in topic.get("prerequisites", []):
            prereq_topic = self.get_topic(prereq["topic_id"])
            if prereq_topic:
                result.append({
                    "topic_id": prereq["topic_id"],
                    "name": prereq_topic["name"],
                    "importance": prereq["importance"],
                })
                # Recursively get prerequisites of prerequisites
                sub_prereqs = self.get_prerequisites(prereq["topic_id"])
                result.extend(sub_prereqs)
        return result

    def get_dependents(self, topic_id: str) -> List[str]:
        """Get topics that depend on this topic."""
        return self.adjacency.get(topic_id, [])

    def get_available_topics(self, completed_topics: List[str]) -> List[dict]:
        """
        Get topics that are available to learn given completed topics.
        A topic is available if all its 'required' prerequisites are completed.
        """
        available = []
        for topic in self.topics.values():
            tid = topic["id"]
            if tid in completed_topics:
                continue  # Already completed

            required_prereqs = [
                p for p in topic.get("prerequisites", [])
                if p["importance"] == "required"
            ]
            recommended_prereqs = [
                p for p in topic.get("prerequisites", [])
                if p["importance"] == "recommended"
            ]

            required_met = all(p["topic_id"] in completed_topics for p in required_prereqs)
            if required_met:
                recommended_met = sum(1 for p in recommended_prereqs if p["topic_id"] in completed_topics)
                available.append({
                    **topic,
                    "prerequisites_met": True,
                    "recommended_completed": recommended_met,
                    "recommended_total": len(recommended_prereqs),
                })

        return available

    def generate_learning_path(
        self,
        completed_topics: List[str],
        strategy: PathStrategy = PathStrategy.STANDARD,
        goal_topic: Optional[str] = None,
        max_topics: int = 30,
    ) -> List[PathNode]:
        """
        Generate a personalized learning path.

        Args:
            completed_topics: List of already-completed topic IDs
            strategy: Path ordering strategy
            goal_topic: Optional target topic for goal-oriented path
            max_topics: Maximum number of topics in path

        Returns ordered list of PathNode objects.
        """
        if strategy == PathStrategy.GOAL_ORIENTED and goal_topic:
            return self._goal_oriented_path(completed_topics, goal_topic)
        elif strategy == PathStrategy.DIFFICULTY_ASC:
            return self._difficulty_asc_path(completed_topics, max_topics)
        else:
            return self._standard_path(completed_topics, max_topics)

    def _standard_path(self, completed: List[str], max_topics: int) -> List[PathNode]:
        """Standard topological order path."""
        ordered = topological_order()
        path = []
        completed_set = set(completed)

        for idx, topic_id in enumerate(ordered):
            if topic_id in completed_set:
                continue
            topic = self.topics.get(topic_id)
            if not topic:
                continue

            required = [p for p in topic.get("prerequisites", []) if p["importance"] == "required"]
            prereqs_met = all(p["topic_id"] in completed_set for p in required)

            path.append(PathNode(
                topic_id=topic_id,
                topic_name=topic["name"],
                difficulty=topic["difficulty_level"],
                category=topic["category"],
                order=idx + 1,
                prerequisites_met=prereqs_met,
                estimated_hours=topic["difficulty_level"] * 2.0,
                status="available" if prereqs_met else "locked",
            ))

            if len(path) >= max_topics:
                break

        return path

    def _difficulty_asc_path(self, completed: List[str], max_topics: int) -> List[PathNode]:
        """Path ordered by increasing difficulty while respecting prerequisites."""
        path = self._standard_path(completed, max_topics)
        # Sort: locked first, then by difficulty within each group
        path.sort(key=lambda n: (0 if n.prerequisites_met else 1, n.difficulty))
        # Re-number
        for i, node in enumerate(path):
            node.order = i + 1
        return path

    def _goal_oriented_path(self, completed: List[str], goal: str) -> List[PathNode]:
        """Shortest prerequisite chain from current knowledge to goal topic."""
        goal_topic = self.topics.get(goal)
        if not goal_topic:
            return []

        # Get all prerequisites for the goal
        prereq_chain = get_prerequisite_chain(goal)
        needed_ids = {p["topic_id"] for p in prereq_chain if p["importance"] == "required"}
        needed_ids.add(goal)

        completed_set = set(completed)
        remaining = [tid for tid in topological_order() if tid in needed_ids and tid not in completed_set]

        path = []
        for idx, topic_id in enumerate(remaining):
            topic = self.topics.get(topic_id)
            if not topic:
                continue
            path.append(PathNode(
                topic_id=topic_id,
                topic_name=topic["name"],
                difficulty=topic["difficulty_level"],
                category=topic["category"],
                order=idx + 1,
                prerequisites_met=True,
                estimated_hours=topic["difficulty_level"] * 2.0,
                status="available",
            ))

        return path

    def estimate_path_duration(self, path: List[PathNode], learning_pace: float = 1.0) -> float:
        """Estimate total hours for a learning path given student pace."""
        total = sum(node.estimated_hours for node in path)
        return total / max(learning_pace, 0.1)

    def get_next_recommended_topic(
        self,
        completed: List[str],
        profile: Optional[dict] = None,
    ) -> Optional[PathNode]:
        """Get the single best next topic recommendation."""
        available = self.get_available_topics(completed)
        if not available:
            return None

        # Sort by difficulty (prefer easier if no profile)
        if profile and profile.get("motivation_level") == "high":
            # High motivation → can tackle harder topics
            available.sort(key=lambda t: (-t["difficulty_level"], t["name"]))
        else:
            # Default: prefer easier first
            available.sort(key=lambda t: (t["difficulty_level"], t["name"]))

        best = available[0]
        return PathNode(
            topic_id=best["id"],
            topic_name=best["name"],
            difficulty=best["difficulty_level"],
            category=best["category"],
            order=0,
            prerequisites_met=True,
            estimated_hours=best["difficulty_level"] * 2.0,
            status="available",
        )


# Singleton
_graph: Optional[DSAKnowledgeGraph] = None


def get_knowledge_graph() -> DSAKnowledgeGraph:
    """Get or create the DSA knowledge graph singleton."""
    global _graph
    if _graph is None:
        _graph = DSAKnowledgeGraph()
    return _graph
