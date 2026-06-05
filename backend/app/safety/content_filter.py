"""
Content safety filter for generated educational resources.

Implements multi-layer filtering:
1. Keyword/profanity blocklist
2. Topic relevance check
3. Academic content quality heuristics
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SafetyResult:
    passed: bool
    score: float  # 0.0 - 1.0
    issues: List[str] = field(default_factory=list)
    category: str = ""


class ContentSafetyFilter:
    """Content safety filter with multiple check layers."""

    # Sensitive content patterns (simplified - expand for production)
    SENSITIVE_PATTERNS = [
        r"(?i)(violence|hate\s?speech|discrimination)",
        r"(?i)(illegal|fraudulent|malicious)",
        r"(?i)(personal\s*attack|harassment)",
    ]

    # Off-topic detection: DSA-related keywords
    DSA_KEYWORDS = {
        "data_structure", "algorithm", "array", "linked_list", "stack", "queue",
        "tree", "graph", "sort", "search", "hash", "recursion", "dynamic_programming",
        "complexity", "big_o", "binary", "traversal", "pointer", "node",
        "数据结构", "算法", "数组", "链表", "栈", "队列", "树", "图",
        "排序", "查找", "哈希", "递归", "动态规划", "复杂度",
    }

    def __init__(self, enable_profanity: bool = True, enable_relevance: bool = True):
        self.enable_profanity = enable_profanity
        self.enable_relevance = enable_relevance

    def check_sensitive_content(self, text: str) -> List[str]:
        """Check for sensitive/inappropriate content patterns."""
        issues = []
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, text):
                issues.append(f"Sensitive content detected matching pattern: {pattern}")
        return issues

    def check_relevance(self, text: str) -> float:
        """Check if content is relevant to DSA topics. Returns relevance score 0-1."""
        if not text:
            return 0.0
        text_lower = text.lower()
        matches = sum(1 for kw in self.DSA_KEYWORDS if kw.lower() in text_lower)
        # Score based on keyword density with a cap
        score = min(matches / max(len(self.DSA_KEYWORDS) * 0.05, 1), 1.0)
        return max(score, 0.1)  # Minimum baseline to avoid overly strict filtering

    def check_content_quality(self, text: str) -> List[str]:
        """Basic content quality heuristics."""
        issues = []

        # Check for minimum content length
        if len(text.strip()) < 50:
            issues.append("Content too short (< 50 chars)")

        # Check for excessive repetition
        words = text.split()
        if len(words) > 20:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                issues.append(f"Low word diversity (ratio: {unique_ratio:.2f})")

        # Check for code block presence in technical content
        if "```" not in text and any(kw in text.lower() for kw in ["code", "function", "algorithm"]):
            # Not necessarily an issue, just note
            pass

        return issues

    def filter(self, text: str, resource_type: str = "") -> SafetyResult:
        """
        Run all safety checks on generated content.

        Returns SafetyResult with pass/fail and issues list.
        """
        all_issues = []

        # Layer 1: Sensitive content
        if self.enable_profanity:
            sensitive_issues = self.check_sensitive_content(text)
            all_issues.extend(sensitive_issues)

        # Layer 2: Topic relevance
        relevance_score = 1.0
        if self.enable_relevance:
            relevance_score = self.check_relevance(text)
            if relevance_score < 0.2:
                all_issues.append(f"Low DSA relevance score: {relevance_score:.2f}")

        # Layer 3: Content quality
        quality_issues = self.check_content_quality(text)
        all_issues.extend(quality_issues)

        # Calculate overall score
        score = relevance_score
        if all_issues:
            score *= 0.7  # Penalty for issues

        passed = len([i for i in all_issues if "sensitive" in i.lower() or "violence" in i.lower()]) == 0

        return SafetyResult(
            passed=passed,
            score=max(0.0, min(score, 1.0)),
            issues=all_issues,
            category=resource_type,
        )
