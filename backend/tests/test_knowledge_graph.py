"""Tests for DSA Knowledge Graph."""

import pytest
from app.knowledge_graph.seed_data import (
    DSA_TOPICS, get_topic_by_id, get_topics_by_category,
    get_prerequisite_chain, topological_order, build_adjacency_list,
)
from app.knowledge_graph.dsa_graph import DSAKnowledgeGraph, PathStrategy


class TestSeedData:
    def test_all_topics_have_required_fields(self):
        for topic in DSA_TOPICS:
            assert "id" in topic
            assert "name" in topic
            assert "category" in topic
            assert "difficulty_level" in topic
            assert 1 <= topic["difficulty_level"] <= 5
            assert "learning_objectives" in topic

    def test_get_topic_by_id_returns_correct_topic(self):
        topic = get_topic_by_id("arrays")
        assert topic is not None
        assert topic["name"] == "数组"
        assert topic["category"] == "data_structure"

    def test_get_topic_by_id_returns_none_for_missing(self):
        assert get_topic_by_id("nonexistent") is None

    def test_get_topics_by_category(self):
        data_structures = get_topics_by_category("data_structure")
        assert len(data_structures) > 0
        assert all(t["category"] == "data_structure" for t in data_structures)

        algorithms = get_topics_by_category("algorithm")
        assert len(algorithms) > 0
        assert all(t["category"] == "algorithm" for t in algorithms)

    def test_topological_order_no_duplicates(self):
        ordered = topological_order()
        assert len(ordered) == len(set(ordered))
        assert len(ordered) == 25  # Exactly 25 topics in seed data

    def test_topological_order_respects_prerequisites(self):
        """Every prerequisite must appear before the topic that depends on it."""
        ordered = topological_order()
        positions = {tid: idx for idx, tid in enumerate(ordered)}

        for topic in DSA_TOPICS:
            for prereq in topic.get("prerequisites", []):
                if prereq["importance"] == "required":
                    assert positions[prereq["topic_id"]] < positions[topic["id"]], (
                        f"Prerequisite {prereq['topic_id']} must come before {topic['id']}"
                    )

    def test_prerequisite_chain(self):
        chain = get_prerequisite_chain("bst")
        prereq_ids = {p["topic_id"] for p in chain}
        assert "trees_basic" in prereq_ids

    def test_adjacency_dependents(self):
        adj = build_adjacency_list()
        dependents = adj.get("trees_basic", [])
        assert "bst" in dependents


class TestDSAKnowledgeGraph:
    def setup_method(self):
        self.kg = DSAKnowledgeGraph()

    def test_get_prerequisites_recursive(self):
        prereqs = self.kg.get_prerequisites("bst")
        prereq_ids = {p["topic_id"] for p in prereqs}
        assert "trees_basic" in prereq_ids

    def test_get_dependents(self):
        deps = self.kg.get_dependents("trees_basic")
        assert "bst" in deps

    def test_get_available_topics_none_completed(self):
        available = self.kg.get_available_topics([])
        assert len(available) > 0
        # Topics with no required prerequisites should be available
        for t in available:
            required = [p for p in t.get("prerequisites", []) if p["importance"] == "required"]
            assert len(required) == 0

    def test_get_available_topics_some_completed(self):
        available = self.kg.get_available_topics(["dsa_intro", "arrays"])
        available_ids = {a["id"] for a in available}
        # linked_lists requires arrays (completed), should be available
        assert "linked_lists" in available_ids

    def test_standard_path_strategy(self):
        path = self.kg.generate_learning_path([], strategy=PathStrategy.STANDARD)
        assert len(path) > 0
        assert path[0].topic_id == "dsa_intro"
        assert all(node.order > 0 for node in path)

    def test_difficulty_asc_strategy(self):
        path = self.kg.generate_learning_path([], strategy=PathStrategy.DIFFICULTY_ASC)
        assert len(path) > 0
        # First few should be easy topics (difficulty 1-2)
        for node in path[:5]:
            assert node.difficulty <= 3

    def test_goal_oriented_path(self):
        path = self.kg.generate_learning_path(
            [], strategy=PathStrategy.GOAL_ORIENTED, goal_topic="dynamic_programming"
        )
        path_ids = {node.topic_id for node in path}
        assert "dynamic_programming" in path_ids
        assert "recursion" in path_ids

    def test_completed_topics_excluded(self):
        completed = ["dsa_intro", "complexity_analysis"]
        path = self.kg.generate_learning_path(completed)
        path_ids = {node.topic_id for node in path}
        assert "dsa_intro" not in path_ids
        assert "complexity_analysis" not in path_ids

    def test_estimate_path_duration(self):
        path = self.kg.generate_learning_path([], max_topics=5)
        duration = self.kg.estimate_path_duration(path, learning_pace=1.0)
        assert duration > 0

    def test_next_recommended_topic(self):
        next_topic = self.kg.get_next_recommended_topic([])
        assert next_topic is not None
        assert next_topic.topic_id == "dsa_intro"

    def test_next_recommended_with_completed(self):
        next_topic = self.kg.get_next_recommended_topic(["dsa_intro"])
        assert next_topic is not None
        assert next_topic.topic_id != "dsa_intro"
