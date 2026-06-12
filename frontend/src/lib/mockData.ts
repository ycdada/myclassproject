/**
 * Mock data layer for demo mode and API fallback.
 *
 * Enable with: NEXT_PUBLIC_DEMO_MODE=true
 * All API calls automatically fall back to this data when the backend is unavailable.
 */

const isDemoMode = () =>
  typeof window !== "undefined" &&
  (process.env.NEXT_PUBLIC_DEMO_MODE === "true" || !process.env.NEXT_PUBLIC_API_URL);

// ========================
// MOCK TOPICS (DSA Knowledge Graph)
// ========================

export const MOCK_TOPICS = [
  { id: "dsa_intro", name: "数据结构与算法导论", difficulty_level: 1, category: "foundation" },
  { id: "complexity_analysis", name: "复杂度分析", difficulty_level: 2, category: "foundation" },
  { id: "arrays", name: "数组", difficulty_level: 1, category: "data_structure" },
  { id: "linked_lists", name: "链表", difficulty_level: 2, category: "data_structure" },
  { id: "stacks", name: "栈", difficulty_level: 2, category: "data_structure" },
  { id: "queues", name: "队列", difficulty_level: 2, category: "data_structure" },
  { id: "strings", name: "字符串", difficulty_level: 2, category: "data_structure" },
  { id: "trees_basic", name: "树的基本概念", difficulty_level: 2, category: "data_structure" },
  { id: "bst", name: "二叉搜索树", difficulty_level: 3, category: "data_structure" },
  { id: "avl_trees", name: "AVL树", difficulty_level: 4, category: "data_structure" },
  { id: "heap", name: "堆", difficulty_level: 3, category: "data_structure" },
  { id: "trie", name: "字典树", difficulty_level: 3, category: "data_structure" },
  { id: "graphs_basic", name: "图的基本概念", difficulty_level: 3, category: "data_structure" },
  { id: "graph_traversal", name: "图的遍历", difficulty_level: 3, category: "algorithm" },
  { id: "shortest_path", name: "最短路径算法", difficulty_level: 4, category: "algorithm" },
  { id: "mst", name: "最小生成树", difficulty_level: 3, category: "algorithm" },
  { id: "searching", name: "查找算法", difficulty_level: 2, category: "algorithm" },
  { id: "basic_sorting", name: "基础排序算法", difficulty_level: 2, category: "algorithm" },
  { id: "advanced_sorting", name: "高级排序算法", difficulty_level: 3, category: "algorithm" },
  { id: "hashing", name: "哈希表", difficulty_level: 3, category: "data_structure" },
  { id: "recursion", name: "递归", difficulty_level: 2, category: "technique" },
  { id: "divide_conquer", name: "分治法", difficulty_level: 3, category: "technique" },
  { id: "dynamic_programming", name: "动态规划", difficulty_level: 4, category: "technique" },
  { id: "greedy", name: "贪心算法", difficulty_level: 3, category: "technique" },
  { id: "backtracking", name: "回溯算法", difficulty_level: 3, category: "technique" },
];

// ========================
// MOCK RESOURCES
// ========================

export const MOCK_RESOURCES = [
  {
    id: "res_array_lecture",
    topic_id: "arrays",
    resource_type: "lecture",
    title: "学习讲义: 数组",
    content: `# 数组 (Array)

## 概念定义

数组是一块**连续内存**中存储的相同类型元素集合。通过索引可以在 $O(1)$ 时间内访问任意元素。

## 核心性质

- 数组在内存中占据连续地址空间
- 元素 \`arr[i]\` 的地址 = 基地址 + i × 元素大小
- 支持**随机访问**（Random Access）

## 算法步骤

### 动态数组扩容

\`\`\`python
class DynamicArray:
    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.data = [None] * self.capacity

    def append(self, value):
        if self.size == self.capacity:
            self._resize(2 * self.capacity)
        self.data[self.size] = value
        self.size += 1
\`\`\`

## 复杂度分析

| 操作 | 时间复杂度 |
|------|-----------|
| 按索引访问 | $O(1)$ |
| 按值搜索 | $O(n)$ |
| 末尾插入 (均摊) | $O(1)$ |
| 中间插入 | $O(n)$ |

## 常见误区

- **误区**: 数组插入和删除总是 O(n)
- **纠正**: 末尾插入在动态数组中均摊为 O(1)
`,
    metadata: { difficulty: 1, estimated_time: "20 min" },
    created_at: new Date().toISOString(),
  },
  {
    id: "res_array_mindmap",
    topic_id: "arrays",
    resource_type: "mindmap",
    title: "思维导图: 数组",
    content: `mindmap
  root((数组))
    基本概念
      连续内存
      索引访问
      定长 vs 变长
    操作
      访问 O(1)
      搜索 O(n)
      插入 O(n)
      删除 O(n)
    动态数组
      扩容机制
      均摊分析
    应用
      哈希表底层
      矩阵运算
      缓存实现`,
    metadata: { difficulty: 1 },
    created_at: new Date().toISOString(),
  },
  {
    id: "res_array_exercise",
    topic_id: "arrays",
    resource_type: "exercise",
    title: "练习题: 数组",
    content: "",
    metadata: { question_count: 10 },
    created_at: new Date().toISOString(),
  },
  {
    id: "res_linkedlist_lecture",
    topic_id: "linked_lists",
    resource_type: "lecture",
    title: "学习讲义: 链表",
    content: `# 链表 (Linked List)

## 概念定义

链表由一系列**节点**组成，每个节点包含数据和指向下一个节点的指针。节点在内存中不必连续。

## 核心性质

- 动态数据结构，无需预分配空间
- 插入和删除在已知位置时仅需 $O(1)$
- 不支持随机访问，查找需要 $O(n)$

## 代码示例

\`\`\`python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):
    prev = None
    curr = head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev
\`\`\`

## 常见误区

- **误区**: 链表插入删除始终是 O(1)
- **纠正**: 仅在已知节点位置时是 O(1)，需要先搜索到该位置则 O(n)
`,
    metadata: { difficulty: 2, estimated_time: "25 min" },
    created_at: new Date().toISOString(),
  },
  {
    id: "res_stack_lecture",
    topic_id: "stacks",
    resource_type: "lecture",
    title: "学习讲义: 栈与队列",
    content: `# 栈与队列

## 栈 (Stack)

**后进先出 (LIFO)** 的线性数据结构。

### 应用场景
- 括号匹配
- 表达式求值（中缀→后缀）
- 函数调用栈
- 单调栈（求下一个更大元素）

\`\`\`python
class Stack:
    def __init__(self):
        self.data = []
    def push(self, x):
        self.data.append(x)
    def pop(self):
        return self.data.pop()
    def peek(self):
        return self.data[-1]
\`\`\`

## 队列 (Queue)

**先进先出 (FIFO)** 的线性数据结构。

### 应用场景
- BFS 遍历
- 任务调度
- 滑动窗口（单调队列）
`,
    metadata: { difficulty: 2, estimated_time: "30 min" },
    created_at: new Date().toISOString(),
  },
  {
    id: "res_sorting_code",
    topic_id: "advanced_sorting",
    resource_type: "code",
    title: "代码实操: 快速排序",
    content: `# 快速排序实现
\`\`\`python
def quick_sort(arr, low, high):
    if low < high:
        pivot = partition(arr, low, high)
        quick_sort(arr, low, pivot - 1)
        quick_sort(arr, pivot + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
\`\`\`
平均时间复杂度 $O(n \\log n)$，原地排序。`,
    metadata: { language: "python", difficulty: 3 },
    created_at: new Date().toISOString(),
  },
  {
    id: "res_dp_reading",
    topic_id: "dynamic_programming",
    resource_type: "reading",
    title: "拓展阅读: 动态规划进阶",
    content: `## 动态规划的核心思想

动态规划通过将原问题分解为重叠子问题，利用记忆化避免重复计算。

### 经典问题

1. **0-1 背包**: $dp[i][w] = \\max(dp[i-1][w], dp[i-1][w-w_i] + v_i)$
2. **最长公共子序列**: 二维 DP 表格
3. **编辑距离**: Levenshtein 距离算法

### 优化技巧
- 滚动数组降低空间复杂度
- 状态压缩（位运算）
- 斜率优化（决策单调性）`,
    metadata: { difficulty: 4, estimated_time: "40 min" },
    created_at: new Date().toISOString(),
  },
];

// ========================
// MOCK QUESTIONS
// ========================

export const MOCK_QUESTIONS = [
  {
    id: "q_001",
    question_type: "multiple_choice",
    difficulty: 1,
    question_text: "在长度为 n 的数组中按值查找元素，最坏时间复杂度是多少？",
    options: [
      { key: "A", value: "O(1)" },
      { key: "B", value: "O(log n)" },
      { key: "C", value: "O(n)" },
      { key: "D", value: "O(n²)" },
    ],
    hints: ["思考是否需要遍历所有元素", "二分查找的前提是有序数组"],
    topic: "数组",
  },
  {
    id: "q_002",
    question_type: "true_false",
    difficulty: 1,
    question_text: "链表的插入和删除操作时间复杂度始终为 O(1)。",
    hints: ["O(1)的前提是已知插入位置", "如果需要先搜索到指定位置呢？"],
    topic: "链表",
  },
  {
    id: "q_003",
    question_type: "short_answer",
    difficulty: 2,
    question_text: "请解释栈和队列的主要区别，并各举一个实际应用场景。",
    hints: ["考虑 LIFO vs FIFO", "现实生活中的类比"],
    topic: "栈与队列",
  },
  {
    id: "q_004",
    question_type: "fill_blank",
    difficulty: 2,
    question_text: "二叉搜索树的中序遍历得到的序列是______的。（请填写：有序/无序/随机）",
    hints: ["回顾 BST 的性质：左<根<右"],
    topic: "树",
  },
  {
    id: "q_005",
    question_type: "coding",
    difficulty: 3,
    question_text: "实现一个函数，判断给定的单链表是否有环。请使用快慢指针法。",
    hints: [
      "使用两个指针：fast 每次走两步，slow 每次走一步",
      "如果有环，fast 和 slow 最终会相遇",
    ],
    topic: "链表",
  },
  {
    id: "q_006",
    question_type: "multiple_choice",
    difficulty: 2,
    question_text: "下列哪个不是平衡二叉搜索树？",
    options: [
      { key: "A", value: "AVL 树" },
      { key: "B", value: "红黑树" },
      { key: "C", value: "普通二叉搜索树" },
      { key: "D", value: "B 树" },
    ],
    hints: ["平衡树能保证 O(log n) 的查找时间"],
    topic: "树",
  },
  {
    id: "q_007",
    question_type: "multiple_choice",
    difficulty: 3,
    question_text: "Dijkstra 算法不能处理哪种情况？",
    options: [
      { key: "A", value: "有向图" },
      { key: "B", value: "无向图" },
      { key: "C", value: "负权边" },
      { key: "D", value: "稠密图" },
    ],
    hints: ["Dijkstra 基于贪心策略，一旦确定最短距离就不会再更新"],
    topic: "图算法",
  },
  {
    id: "q_008",
    question_type: "coding",
    difficulty: 4,
    question_text: "实现一个函数，返回数组中第 K 大的元素。要求时间复杂度优于 O(n log n)。",
    hints: [
      "考虑使用快速选择算法（QuickSelect）",
      "也可以使用大小为 K 的最小堆",
    ],
    topic: "排序",
  },
];

// ========================
// MOCK LEARNING PATH
// ========================

export const MOCK_LEARNING_PATH = [
  { topic_id: "dsa_intro", topic_name: "数据结构与算法导论", order: 1, difficulty: 1, status: "completed", estimated_hours: 1.0 },
  { topic_id: "complexity_analysis", topic_name: "复杂度分析", order: 2, difficulty: 2, status: "completed", estimated_hours: 2.0 },
  { topic_id: "arrays", topic_name: "数组", order: 3, difficulty: 1, status: "in_progress", estimated_hours: 1.5 },
  { topic_id: "linked_lists", topic_name: "链表", order: 4, difficulty: 2, status: "available", estimated_hours: 2.0 },
  { topic_id: "stacks", topic_name: "栈", order: 5, difficulty: 2, status: "available", estimated_hours: 1.5 },
  { topic_id: "queues", topic_name: "队列", order: 6, difficulty: 2, status: "locked", estimated_hours: 1.5 },
  { topic_id: "trees_basic", topic_name: "树的基本概念", order: 7, difficulty: 2, status: "locked", estimated_hours: 2.5 },
  { topic_id: "bst", topic_name: "二叉搜索树", order: 8, difficulty: 3, status: "locked", estimated_hours: 3.0 },
  { topic_id: "heap", topic_name: "堆", order: 9, difficulty: 3, status: "locked", estimated_hours: 2.0 },
  { topic_id: "graphs_basic", topic_name: "图的基本概念", order: 10, difficulty: 3, status: "locked", estimated_hours: 2.0 },
];

// ========================
// MOCK ASSESSMENT
// ========================

export const MOCK_ASSESSMENT = {
  report: {
    student_id: "demo",
    overall_mastery: 0.25,
    topic_assessments: [
      { topic_id: "dsa_intro", mastery: 0.6 },
      { topic_id: "complexity_analysis", mastery: 0.5 },
      { topic_id: "arrays", mastery: 0.3 },
    ],
    strengths: ["基础概念理解清晰", "编程能力强"],
    weaknesses: [
      { topic: "复杂度分析", gap_description: "对均摊分析掌握不足" },
      { topic: "动态规划", gap_description: "状态转移方程设计有困难" },
    ],
    recommendations: [
      { action: "review", resource_type: "lecture", priority: "high" },
      { action: "practice", resource_type: "exercise", priority: "high" },
    ],
    learning_velocity: 0.8,
    engagement_score: 0.6,
  },
  dashboard: {
    student_id: "demo",
    topics_completed: 2,
    total_topics: 30,
    exercises_attempted: 8,
    exercises_correct: 5,
    resources_generated: 4,
    total_study_time_minutes: 85,
    recent_activities: [
      { type: "answer", resource_id: "q_003", duration_seconds: 180, score: 0.5, created_at: "2026-06-08T14:30:00" },
      { type: "view", resource_id: "res_array_lecture", duration_seconds: 600, score: null, created_at: "2026-06-08T13:45:00" },
      { type: "answer", resource_id: "q_001", duration_seconds: 45, score: 1.0, created_at: "2026-06-08T13:20:00" },
      { type: "view", resource_id: "res_linkedlist_lecture", duration_seconds: 420, score: null, created_at: "2026-06-07T16:00:00" },
      { type: "answer", resource_id: "q_005", duration_seconds: 600, score: 0.0, created_at: "2026-06-07T15:30:00" },
    ],
    mastery_radar: {
      "复杂度分析": 0.5,
      "数组": 0.3,
      "链表": 0.15,
      "栈与队列": 0.05,
      "树结构": 0.0,
      "图算法": 0.0,
      "排序": 0.0,
      "哈希表": 0.0,
    },
    weekly_progress: [],
  },
};

// ========================
// MOCK PROFILE
// ========================

export const MOCK_PROFILE = {
  knowledge_foundation: {
    dsa_intro: 0.6,
    complexity_analysis: 0.5,
    arrays: 0.3,
  },
  cognitive_style: "visual",
  error_prone_areas: ["递归边界条件", "指针操作"],
  learning_pace: 1.2,
  preferred_resource_types: ["video", "exercise", "code"],
  motivation_level: "high",
  attention_span: "medium",
  goal: "course_study",
  prior_courses: ["C语言程序设计", "Python程序设计"],
};

// ========================
// MOCK CHAT RESPONSES (profile building conversation)
// ========================

export const MOCK_CHAT_SCRIPTS = [
  {
    user: "你好",
    assistant: "你好！👋 我是你的AI学习助手。让我们通过对话来了解你的学习情况，为你构建个性化的学习画像。\n\n首先，请告诉我：你之前学过哪些编程或算法相关的课程呢？",
  },
  {
    user: "我学过C语言和Python，对基本的数据结构有一些了解，但算法方面比较薄弱",
    assistant: "很棒！你已经有了不错的编程基础。C语言让你对指针和内存有深入理解，Python则提供了简洁的算法表达方式。\n\n你平时更喜欢哪种学习方式呢？看教学视频、阅读教材、动手写代码练习，还是画思维导图来整理知识？",
  },
  {
    user: "我喜欢看视频教程，然后跟着写代码。动手实践对我来说最重要",
    assistant: "我理解你的学习风格了！你是典型的**视觉+动手实践型**学习者。这很适合 DSA 学习——先通过视频理解概念，再用代码巩固。\n\n你的学习目标是什么呢？是为了通过期末考试、准备技术面试、还是纯粹对算法感兴趣想深入掌握？",
  },
  {
    user: "我在准备明年的实习面试，想系统掌握数据结构与算法",
    assistant: "目标很明确！实习面试通常侧重以下方面：\n\n- 📝 **手写代码**能力（白板编程）\n- 🧠 **算法思维**（复杂度分析、优化）\n- 💡 **常见题型**（数组、链表、树、动态规划等）\n\n我已经为你提取了以下学习画像：\n\n| 维度 | 评估 |\n|------|------|\n| 学习风格 | 视觉+动手实践 |\n| 基础知识 | 有编程基础，算法较薄弱 |\n| 学习目标 | 面试准备 |\n| 学习节奏 | 中等偏快 |\n\n接下来我为你规划个性化学习路径，从基础数据结构开始逐步深入。准备好了吗？🚀",
  },
];

// ========================
// Factory Functions
// ========================

export function getMockTopics(category?: string) {
  if (category && category !== "all") {
    return MOCK_TOPICS.filter((t) => t.category === category);
  }
  return MOCK_TOPICS;
}

export function getMockResources(topicId?: string, resourceType?: string) {
  let filtered = MOCK_RESOURCES;
  if (topicId) filtered = filtered.filter((r) => r.topic_id === topicId);
  if (resourceType && resourceType !== "all") filtered = filtered.filter((r) => r.resource_type === resourceType);
  return filtered;
}

export function getMockQuestions(topicId?: string, questionType?: string) {
  let filtered = MOCK_QUESTIONS;
  if (topicId) filtered = filtered.filter((q) => q.topic === topicId);
  if (questionType && questionType !== "all") filtered = filtered.filter((q) => q.question_type === questionType);
  return filtered;
}

export function getMockLearningPath() {
  return MOCK_LEARNING_PATH;
}

export function getMockAssessment() {
  return MOCK_ASSESSMENT;
}

export function getMockProfile() {
  return { ...MOCK_PROFILE };
}

export function getMockChatScript() {
  return MOCK_CHAT_SCRIPTS;
}

// Mock session-generated resources (simulates multi-agent output)
export function getMockSessionResources(topicId?: string) {
  const prefix = topicId || "arrays";
  return [
    {
      id: `res_${prefix}_lecture_demo`,
      topic_id: topicId || "arrays",
      resource_type: "lecture",
      title: `学习讲义: ${topicId === "linked_lists" ? "链表" : topicId === "bst" ? "二叉搜索树" : topicId === "stacks" ? "栈与队列" : topicId === "dynamic_programming" ? "动态规划" : "数组"}`,
      content: topicId === "linked_lists"
        ? "# 链表 (Linked List)\n\n## 概念定义\n\n链表由一系列**节点**组成，每个节点包含数据和指向下一个节点的指针。节点在内存中不必连续。\n\n## 核心性质\n\n- 动态数据结构，无需预分配空间\n- 插入和删除在已知位置时仅需 $O(1)$\n- 不支持随机访问，查找需要 $O(n)$\n\n## 算法步骤\n\n### 反转链表\n\n\\`\\`\\`python\nclass ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_list(head):\n    prev = None\n    curr = head\n    while curr:\n        next_node = curr.next\n        curr.next = prev\n        prev = curr\n        curr = next_node\n    return prev\n\\`\\`\\`\n\n## 复杂度分析\n\n| 操作 | 时间复杂度 |\n|------|----------|\n| 按索引访问 | $O(n)$ |\n| 头部插入/删除 | $O(1)$ |\n| 中间插入/删除 | $O(n)$（需要先搜索）|\n\n## 常见误区\n\n- **误区**: 链表插入删除始终是 O(1)\n- **纠正**: 仅在已知节点位置时是 O(1)，需要先搜索到该位置则 O(n)"
        : "# 数组 (Array)\n\n## 概念定义\n\n数组是一块**连续内存**中存储的相同类型元素集合。通过索引可以在 $O(1)$ 时间内访问任意元素。\n\n## 核心性质\n\n- 数组在内存中占据连续地址空间\n- 元素 `arr[i]` 的地址 = 基地址 + i × 元素大小\n- 支持**随机访问**\n\n## 算法步骤\n\n### 动态数组扩容\n\n\\`\\`\\`python\nclass DynamicArray:\n    def __init__(self):\n        self.capacity = 1\n        self.size = 0\n        self.data = [None] * self.capacity\n\n    def append(self, value):\n        if self.size == self.capacity:\n            self._resize(2 * self.capacity)\n        self.data[self.size] = value\n        self.size += 1\n\n    def _resize(self, new_capacity):\n        new_data = [None] * new_capacity\n        for i in range(self.size):\n            new_data[i] = self.data[i]\n        self.data = new_data\n        self.capacity = new_capacity\n\\`\\`\\`\n\n## 复杂度分析\n\n| 操作 | 时间复杂度 |\n|------|----------|\n| 按索引访问 | $O(1)$ |\n| 按值搜索 | $O(n)$ |\n| 末尾插入 (均摊) | $O(1)$ |\n| 中间插入 | $O(n)$ |\n\n## 常见误区\n\n- **误区**: 数组插入和删除总是 O(n)\n- **纠正**: 末尾插入在动态数组中均摊为 O(1)",
    },
    {
      id: `res_${prefix}_mindmap_demo`,
      topic_id: topicId || "arrays",
      resource_type: "mindmap",
      title: `思维导图: ${topicId === "linked_lists" ? "链表" : "数组"}`,
      mindmap: `mindmap\n  root((${topicId === "linked_lists" ? "链表" : "数组"}))\n    基本概念\n      定义与特点\n      内存模型\n    核心操作\n      查找\n      插入\n      删除\n      遍历\n    进阶技术\n      快慢指针\n      反转链表\n      合并有序链表\n    应用场景\n      LRU缓存\n      多项式加法\n      图的邻接表`,
    },
    {
      id: `res_${prefix}_exercise_demo`,
      topic_id: topicId || "arrays",
      resource_type: "exercise",
      title: `练习题: ${topicId === "linked_lists" ? "链表" : "数组"} (5种题型)`,
      questions: [
        { question_type: "multiple_choice", difficulty: 1, question_text: topicId === "linked_lists" ? "链表不支持以下哪种操作？" : "数组的随机访问时间复杂度是多少？", options: [{ key: "A", value: "O(1)" }, { key: "B", value: "O(log n)" }, { key: "C", value: "O(n)" }, { key: "D", value: "O(n²)" }], hints: ["回顾数组的定义"] },
        { question_type: "true_false", difficulty: 1, question_text: topicId === "linked_lists" ? "链表的插入和删除时间复杂度始终为 O(1)。" : "动态数组的尾插均摊复杂度为 O(1)。", hints: ["思考是否需要先定位"] },
        { question_type: "coding", difficulty: 3, question_text: topicId === "linked_lists" ? "实现函数，检测单链表是否有环（快慢指针法）" : "实现一个动态数组类，支持 append 和自动扩容", hints: ["快指针每次2步，慢指针每次1步"] },
      ],
    },
    {
      id: `res_${prefix}_code_demo`,
      topic_id: topicId || "arrays",
      resource_type: "code",
      title: `代码实操: ${topicId === "linked_lists" ? "链表操作" : "动态数组"}`,
      solution: topicId === "linked_lists"
        ? "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef has_cycle(head):\n    slow = fast = head\n    while fast and fast.next:\n        slow = slow.next\n        fast = fast.next.next\n        if slow == fast:\n            return True\n    return False"
        : "class DynamicArray:\n    def __init__(self):\n        self.capacity = 1\n        self.size = 0\n        self.data = [None] * self.capacity\n    def append(self, val):\n        if self.size == self.capacity:\n            self._resize(2 * self.capacity)\n        self.data[self.size] = val\n        self.size += 1",
      test_cases: [{ input: "", expected: "" }],
      verification: { passed: true },
    },
  ];
}

export { isDemoMode };
