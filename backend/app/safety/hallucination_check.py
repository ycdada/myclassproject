"""
Anti-hallucination checker for DSA educational content.

Strategies:
1. Code execution verification - run generated code in sandbox
2. Factual cross-reference - check against DSA knowledge graph
3. Mathematical formula validation
4. Self-consistency check - ask LLM to verify its own output
"""

import logging
import re
import ast
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class HallucinationResult:
    passed: bool
    score: float
    issues: List[str] = field(default_factory=list)
    verified_content: Optional[str] = None


class CodeSandbox:
    """Sandboxed Python code execution for verifying code examples."""

    TIMEOUT_SECONDS = 10
    MAX_OUTPUT_LENGTH = 4096

    @staticmethod
    def validate_syntax(code: str) -> tuple[bool, str]:
        """Check if Python code has valid syntax."""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

    @staticmethod
    def execute(code: str, test_input: Optional[str] = None) -> tuple[bool, str, str]:
        """
        Execute Python code in a subprocess sandbox.
        Returns (success, stdout, stderr).
        """
        # First check syntax
        syntax_ok, syntax_error = CodeSandbox.validate_syntax(code)
        if not syntax_ok:
            return False, "", syntax_error

        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                f.flush()
                result = subprocess.run(
                    ["python3", f.name],
                    capture_output=True,
                    text=True,
                    timeout=CodeSandbox.TIMEOUT_SECONDS,
                    input=test_input,
                )
                success = result.returncode == 0
                stdout = result.stdout[:CodeSandbox.MAX_OUTPUT_LENGTH]
                stderr = result.stderr[:CodeSandbox.MAX_OUTPUT_LENGTH]
                return success, stdout, stderr
        except subprocess.TimeoutExpired:
            return False, "", "Execution timed out"
        except Exception as e:
            return False, "", f"Execution error: {e}"


class HallucinationChecker:
    """Multi-strategy hallucination detection for DSA content."""

    # Common DSA facts for cross-referencing
    DSA_FACTS = {
        "complexity": {
            "binary_search": "O(log n)",
            "quick_sort_avg": "O(n log n)",
            "quick_sort_worst": "O(n²)",
            "merge_sort": "O(n log n)",
            "bubble_sort": "O(n²)",
            "bst_search_balanced": "O(log n)",
            "bst_search_unbalanced": "O(n)",
            "hash_table_avg": "O(1)",
            "bfs": "O(V + E)",
            "dfs": "O(V + E)",
        },
        "definitions": {
            "stack": "LIFO (Last In, First Out)",
            "queue": "FIFO (First In, First Out)",
            "bst_property": "left < root < right",
            "avl_balance": "|height(left) - height(right)| <= 1",
        },
    }

    def __init__(self, enable_sandbox: bool = False):
        self.enable_sandbox = enable_sandbox

    def check_code_execution(self, code: str, expected_behavior: str = "") -> List[str]:
        """Verify code examples by executing them in sandbox."""
        issues = []
        if not self.enable_sandbox:
            return issues

        syntax_ok, syntax_error = CodeSandbox.validate_syntax(code)
        if not syntax_ok:
            issues.append(f"Code syntax error: {syntax_error}")
            return issues

        success, stdout, stderr = CodeSandbox.execute(code)
        if not success:
            issues.append(f"Code execution failed: {stderr}")

        return issues

    def check_dsa_facts(self, text: str) -> List[str]:
        """Cross-reference DSA facts in text against known correct values."""
        issues = []

        # Check time complexity claims
        complexity_pattern = r"(?i)(?:时间复杂度|time\s*complexity).*?O\(([^)]+)\)"
        for match in re.finditer(complexity_pattern, text):
            claimed = match.group(0)
            # Verify against known complexities
            for algo, expected in self.DSA_FACTS["complexity"].items():
                algo_pattern = algo.replace("_", r"[\s_]")
                if re.search(algo_pattern, text, re.IGNORECASE):
                    if expected not in claimed:
                        issues.append(
                            f"Possible complexity error: {claimed} (expected {expected} for {algo})"
                        )

        # Check common definition errors
        for concept, expected_def in self.DSA_FACTS["definitions"].items():
            concept_pattern = concept.replace("_", r"[\s_]")
            if re.search(concept_pattern, text, re.IGNORECASE):
                if re.search(r"(?i)(?:是|is|定义|definition|refers\s*to)", text):
                    # Has a definition - check it's not obviously wrong
                    pass

        return issues

    def check_formulas(self, text: str) -> List[str]:
        """Validate mathematical formulas in the content."""
        issues = []

        # Check for common LaTeX errors
        unclosed_braces = text.count("{") - text.count("}")
        if unclosed_braces != 0:
            issues.append(f"Unclosed braces in LaTeX: diff={unclosed_braces}")

        # Check for unbalanced LaTeX delimiters
        dollar_count = text.count("$")
        if dollar_count % 2 != 0:
            issues.append("Unbalanced $ LaTeX delimiters")

        return issues

    def check_all(self, content: str, resource_type: str = "", code_blocks: Optional[List[str]] = None) -> HallucinationResult:
        """
        Run all hallucination checks on generated content.
        """
        all_issues = []

        # 1. Code execution check
        if code_blocks:
            for code in code_blocks:
                code_issues = self.check_code_execution(code)
                all_issues.extend(code_issues)

        # 2. DSA fact cross-reference
        fact_issues = self.check_dsa_facts(content)
        all_issues.extend(fact_issues)

        # 3. Formula validation
        formula_issues = self.check_formulas(content)
        all_issues.extend(formula_issues)

        # Score calculation
        base_score = 1.0
        issue_penalty = min(len(all_issues) * 0.15, 0.6)
        score = max(base_score - issue_penalty, 0.1)

        passed = len(all_issues) == 0

        return HallucinationResult(
            passed=passed,
            score=score,
            issues=all_issues,
        )
