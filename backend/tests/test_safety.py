"""Tests for content safety and hallucination checker."""

import pytest
from app.safety.content_filter import ContentSafetyFilter
from app.safety.hallucination_check import HallucinationChecker, CodeSandbox


class TestContentSafetyFilter:
    def setup_method(self):
        self.filter = ContentSafetyFilter()

    def test_normal_dsa_content_passes(self):
        result = self.filter.filter(
            "数组是一种连续内存的数据结构，支持随机访问，时间复杂度为 O(1)。",
            resource_type="lecture",
        )
        assert result.passed is True
        assert result.score > 0.3

    def test_short_content_flagged(self):
        result = self.filter.filter("数组", resource_type="lecture")
        assert any("too short" in issue.lower() for issue in result.issues)

    def test_relevance_score_high_for_dsa(self):
        score = self.filter.check_relevance(
            "二叉树的前序遍历可以通过递归或栈实现，时间复杂度为 O(n)，"
            "空间复杂度为 O(h)，其中 h 为树的高度。在平衡二叉树中 h = O(log n)。"
        )
        assert score > 0.1

    def test_relevance_score_low_for_non_dsa(self):
        score = self.filter.check_relevance("今天天气真好，适合出去玩。")
        assert score < 0.3

    def test_sensitive_content_detected(self):
        result = self.filter.filter(
            "violence is the answer to everything and we should attack everyone",
            resource_type="lecture",
        )
        assert len(result.issues) > 0

    def test_filter_returns_safety_result_structure(self):
        result = self.filter.filter("二分查找的时间复杂度是 O(log n)", resource_type="lecture")
        assert hasattr(result, "passed")
        assert hasattr(result, "score")
        assert hasattr(result, "issues")
        assert isinstance(result.passed, bool)
        assert 0.0 <= result.score <= 1.0


class TestCodeSandbox:
    def test_valid_syntax(self):
        ok, err = CodeSandbox.validate_syntax("print('hello world')")
        assert ok is True
        assert err == ""

    def test_invalid_syntax(self):
        ok, err = CodeSandbox.validate_syntax("print 'hello'")
        assert ok is False
        assert "Syntax error" in err

    def test_execute_valid_code(self):
        success, stdout, stderr = CodeSandbox.execute("print('hello')")
        assert success is True
        assert "hello" in stdout

    def test_execute_runtime_error(self):
        success, stdout, stderr = CodeSandbox.execute("1/0")
        assert success is False
        assert "ZeroDivisionError" in stderr

    def test_execute_with_variables(self):
        success, stdout, stderr = CodeSandbox.execute("x = sum([1, 2, 3])\nprint(x)")
        assert success is True
        assert "6" in stdout

    def test_execute_algorithm_code(self):
        code = """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Test
arr = [1, 3, 5, 7, 9]
assert binary_search(arr, 7) == 3
assert binary_search(arr, 2) == -1
print("All tests passed!")
"""
        success, stdout, stderr = CodeSandbox.execute(code)
        assert success is True
        assert "All tests passed!" in stdout


class TestHallucinationChecker:
    def setup_method(self):
        self.checker = HallucinationChecker()

    def test_correct_dsa_content_passes(self):
        result = self.checker.check_all(
            "二叉搜索树的中序遍历可以得到有序序列。"
            "在平衡的情况下，二叉搜索树的查找时间复杂度为 O(log n)。",
            resource_type="lecture",
        )
        assert isinstance(result.score, float)

    def test_formula_validation_unbalanced_braces(self):
        result = self.checker.check_all(
            "时间复杂度为 $O(n$ （缺少闭合括号）",
            resource_type="lecture",
        )
        assert any("LaTeX" in issue for issue in result.issues)

    def test_formula_validation_balanced(self):
        result = self.checker.check_all(
            "时间复杂度为 $O(n \\log n)$，空间复杂度为 $O(1)$。",
            resource_type="lecture",
        )
        assert not any("LaTeX" in issue for issue in result.issues)

    def test_check_all_returns_structured_result(self):
        result = self.checker.check_all("数组是基础数据结构", resource_type="lecture")
        assert hasattr(result, "passed")
        assert hasattr(result, "score")
        assert hasattr(result, "issues")
        assert 0.0 <= result.score <= 1.0


class TestProfileMerge:
    """Test the _merge_profile function from orchestrator."""

    def test_merge_empty_profile(self):
        from app.agents.orchestrator import _merge_profile
        existing = {}
        new_data = {
            "cognitive_style": "visual",
            "learning_pace": 1.5,
            "confidence": 0.8,
        }
        merged = _merge_profile(existing, new_data)
        assert merged["cognitive_style"] == "visual"
        assert merged["learning_pace"] == 1.5

    def test_merge_low_confidence_skipped(self):
        from app.agents.orchestrator import _merge_profile
        existing = {"cognitive_style": "reading"}
        new_data = {"cognitive_style": "visual", "confidence": 0.2}
        merged = _merge_profile(existing, new_data)
        # Low confidence -> scalar values not updated
        assert merged["cognitive_style"] == "reading"

    def test_merge_knowledge_foundation_accumulates(self):
        from app.agents.orchestrator import _merge_profile
        existing = {"knowledge_foundation": {"arrays": 0.5}}
        new_data = {"knowledge_foundation": {"linked_lists": 0.3}, "confidence": 0.7}
        merged = _merge_profile(existing, new_data)
        assert "arrays" in merged["knowledge_foundation"]
        assert "linked_lists" in merged["knowledge_foundation"]
        assert merged["knowledge_foundation"]["arrays"] == 0.5
        assert merged["knowledge_foundation"]["linked_lists"] == 0.3

    def test_merge_list_fields_union(self):
        from app.agents.orchestrator import _merge_profile
        existing = {"error_prone_areas": ["递归"], "preferred_resource_types": ["video"]}
        new_data = {
            "error_prone_areas": ["指针"],
            "preferred_resource_types": ["code"],
            "confidence": 0.6,
        }
        merged = _merge_profile(existing, new_data)
        assert "递归" in merged["error_prone_areas"]
        assert "指针" in merged["error_prone_areas"]
        assert "video" in merged["preferred_resource_types"]
        assert "code" in merged["preferred_resource_types"]

    def test_merge_no_duplicates_in_lists(self):
        from app.agents.orchestrator import _merge_profile
        existing = {"error_prone_areas": ["递归"], "preferred_resource_types": [], "prior_courses": []}
        new_data = {"error_prone_areas": ["递归", "指针"], "confidence": 0.9}
        merged = _merge_profile(existing, new_data)
        assert merged["error_prone_areas"].count("递归") == 1
