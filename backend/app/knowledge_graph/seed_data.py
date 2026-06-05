"""
DSA Knowledge Graph Seed Data

Covers the standard Data Structures & Algorithms curriculum with:
- 30+ topics organized hierarchically
- Prerequisite relationships
- Difficulty levels (1-5)
- Learning objectives at various Bloom's taxonomy levels
- Categories: data_structure, algorithm, technique, fundamental
"""

DSA_TOPICS = [
    # ========================
    # FOUNDATIONS
    # ========================
    {
        "id": "dsa_intro",
        "name": "数据结构与算法导论",
        "category": "fundamental",
        "difficulty_level": 1,
        "parent_id": None,
        "prerequisites": [],
        "learning_objectives": [
            {"objective": "理解数据结构与算法的基本概念", "bloom_level": "understand"},
            {"objective": "掌握时间复杂度和空间复杂度的分析方法", "bloom_level": "apply"},
            {"objective": "理解大O表示法的含义和使用", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "认为时间复杂度越低越好，忽略实际场景的常数因子",
            "混淆最坏情况和平均情况复杂度",
        ],
    },
    {
        "id": "complexity_analysis",
        "name": "复杂度分析",
        "category": "fundamental",
        "difficulty_level": 2,
        "parent_id": "dsa_intro",
        "prerequisites": [{"topic_id": "dsa_intro", "importance": "required"}],
        "learning_objectives": [
            {"objective": "能够分析常见算法的时间复杂度", "bloom_level": "analyze"},
            {"objective": "理解递归算法的时间复杂度分析（主定理）", "bloom_level": "apply"},
            {"objective": "掌握均摊分析的基本思想", "bloom_level": "understand"},
        ],
        "common_misconceptions": [
            "递归算法的时间复杂度一定比迭代高",
        ],
    },

    # ========================
    # LINEAR DATA STRUCTURES
    # ========================
    {
        "id": "arrays",
        "name": "数组",
        "category": "data_structure",
        "difficulty_level": 1,
        "parent_id": None,
        "prerequisites": [{"topic_id": "dsa_intro", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "理解数组的连续内存存储特性", "bloom_level": "understand"},
            {"objective": "掌握数组的插入、删除、查找操作及复杂度", "bloom_level": "apply"},
            {"objective": "能够实现动态数组（如ArrayList）", "bloom_level": "create"},
        ],
        "common_misconceptions": [
            "认为数组插入和删除总是O(n)",
            "忽略动态数组扩容的均摊复杂度",
        ],
    },
    {
        "id": "linked_lists",
        "name": "链表",
        "category": "data_structure",
        "difficulty_level": 2,
        "parent_id": None,
        "prerequisites": [{"topic_id": "arrays", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "理解链表与数组在内存存储上的本质区别", "bloom_level": "understand"},
            {"objective": "掌握单链表、双向链表、循环链表的实现与操作", "bloom_level": "apply"},
            {"objective": "能够使用快慢指针等技巧解决链表问题", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "忽略链表操作中的指针丢失问题",
            "删除节点时忘记处理头尾边界",
        ],
    },
    {
        "id": "stacks",
        "name": "栈",
        "category": "data_structure",
        "difficulty_level": 2,
        "parent_id": None,
        "prerequisites": [{"topic_id": "arrays", "importance": "required"}],
        "learning_objectives": [
            {"objective": "理解栈的LIFO特性及其应用场景", "bloom_level": "understand"},
            {"objective": "掌握栈在括号匹配、表达式求值中的应用", "bloom_level": "apply"},
            {"objective": "能够实现单调栈解决相关问题", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "忽略栈在递归中的隐式使用",
        ],
    },
    {
        "id": "queues",
        "name": "队列",
        "category": "data_structure",
        "difficulty_level": 2,
        "parent_id": None,
        "prerequisites": [{"topic_id": "arrays", "importance": "required"}],
        "learning_objectives": [
            {"objective": "理解队列的FIFO特性及其应用场景", "bloom_level": "understand"},
            {"objective": "掌握循环队列、双端队列的实现", "bloom_level": "apply"},
            {"objective": "理解优先队列的概念和应用", "bloom_level": "understand"},
        ],
        "common_misconceptions": [
            "混淆队列和栈的应用场景",
        ],
    },
    {
        "id": "strings",
        "name": "字符串",
        "category": "data_structure",
        "difficulty_level": 2,
        "parent_id": None,
        "prerequisites": [{"topic_id": "arrays", "importance": "required"}],
        "learning_objectives": [
            {"objective": "掌握常见字符串匹配算法（KMP、Boyer-Moore）", "bloom_level": "apply"},
            {"objective": "理解字符串哈希及其应用", "bloom_level": "apply"},
        ],
        "common_misconceptions": [],
    },

    # ========================
    # TREE STRUCTURES
    # ========================
    {
        "id": "trees_basic",
        "name": "树的基本概念",
        "category": "data_structure",
        "difficulty_level": 2,
        "parent_id": None,
        "prerequisites": [{"topic_id": "linked_lists", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "理解树的定义、术语和基本性质", "bloom_level": "understand"},
            {"objective": "掌握二叉树的存储结构和遍历方式", "bloom_level": "apply"},
            {"objective": "能够实现二叉树的递归和非递归遍历", "bloom_level": "create"},
        ],
        "common_misconceptions": [
            "混淆树的深度和高度的定义",
            "递归遍历的栈溢出问题",
        ],
    },
    {
        "id": "bst",
        "name": "二叉搜索树（BST）",
        "category": "data_structure",
        "difficulty_level": 3,
        "parent_id": "trees_basic",
        "prerequisites": [{"topic_id": "trees_basic", "importance": "required"}],
        "learning_objectives": [
            {"objective": "理解BST的性质和约束条件", "bloom_level": "understand"},
            {"objective": "掌握BST的插入、删除、查找操作", "bloom_level": "apply"},
            {"objective": "理解BST退化为链表的问题", "bloom_level": "understand"},
        ],
        "common_misconceptions": [
            "BST删除节点时的三种情况处理",
            "中序遍历BST得到有序序列的证明",
        ],
    },
    {
        "id": "avl_trees",
        "name": "AVL树（平衡二叉树）",
        "category": "data_structure",
        "difficulty_level": 4,
        "parent_id": "bst",
        "prerequisites": [{"topic_id": "bst", "importance": "required"}],
        "learning_objectives": [
            {"objective": "理解平衡因子的概念和AVL树的定义", "bloom_level": "understand"},
            {"objective": "掌握四种旋转操作（LL、RR、LR、RL）", "bloom_level": "apply"},
            {"objective": "能够分析AVL树的复杂度并实现基本操作", "bloom_level": "create"},
        ],
        "common_misconceptions": [
            "混淆双旋转与两次单旋转的区别",
        ],
    },
    {
        "id": "red_black_trees",
        "name": "红黑树",
        "category": "data_structure",
        "difficulty_level": 5,
        "parent_id": "bst",
        "prerequisites": [{"topic_id": "avl_trees", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "理解红黑树的5条性质和平衡保证", "bloom_level": "understand"},
            {"objective": "掌握红黑树的旋转和重新着色操作", "bloom_level": "apply"},
            {"objective": "理解红黑树在实际系统中的应用", "bloom_level": "evaluate"},
        ],
        "common_misconceptions": [
            "红黑树不是严格平衡的，但保证了O(log n)",
        ],
    },
    {
        "id": "heap",
        "name": "堆（Heap）",
        "category": "data_structure",
        "difficulty_level": 3,
        "parent_id": "trees_basic",
        "prerequisites": [{"topic_id": "trees_basic", "importance": "required"}],
        "learning_objectives": [
            {"objective": "理解堆的定义和性质（最大堆、最小堆）", "bloom_level": "understand"},
            {"objective": "掌握堆的插入、删除和建堆操作", "bloom_level": "apply"},
            {"objective": "能够使用堆解决Top-K问题和实现优先队列", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "建堆的时间复杂度是O(n)而非O(n log n)",
        ],
    },
    {
        "id": "trie",
        "name": "字典树（Trie）",
        "category": "data_structure",
        "difficulty_level": 3,
        "parent_id": "trees_basic",
        "prerequisites": [{"topic_id": "trees_basic", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "理解Trie的结构和前缀匹配特性", "bloom_level": "understand"},
            {"objective": "掌握Trie的插入、查找、删除操作", "bloom_level": "apply"},
            {"objective": "能够使用Trie解决自动补全和拼写检查问题", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "Trie的空间复杂度可能很高，需要了解优化方法",
        ],
    },

    # ========================
    # GRAPH STRUCTURES
    # ========================
    {
        "id": "graphs_basic",
        "name": "图的基本概念",
        "category": "data_structure",
        "difficulty_level": 3,
        "parent_id": None,
        "prerequisites": [
            {"topic_id": "trees_basic", "importance": "recommended"},
            {"topic_id": "queues", "importance": "recommended"},
        ],
        "learning_objectives": [
            {"objective": "理解图的基本术语和表示方法（邻接矩阵、邻接表）", "bloom_level": "understand"},
            {"objective": "掌握图的存储结构的选择策略", "bloom_level": "evaluate"},
        ],
        "common_misconceptions": [
            "邻接矩阵在稀疏图中的空间浪费",
        ],
    },
    {
        "id": "graph_traversal",
        "name": "图的遍历",
        "category": "algorithm",
        "difficulty_level": 3,
        "parent_id": "graphs_basic",
        "prerequisites": [
            {"topic_id": "graphs_basic", "importance": "required"},
            {"topic_id": "stacks", "importance": "recommended"},
            {"topic_id": "queues", "importance": "required"},
        ],
        "learning_objectives": [
            {"objective": "掌握DFS和BFS的原理、实现和应用", "bloom_level": "apply"},
            {"objective": "能够使用DFS/BFS解决连通性、路径查找等问题", "bloom_level": "apply"},
            {"objective": "理解拓扑排序的原理和Kahn算法", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "DFS递归实现可能导致栈溢出",
            "BFS求最短路径仅适用于无权图",
        ],
    },
    {
        "id": "shortest_path",
        "name": "最短路径算法",
        "category": "algorithm",
        "difficulty_level": 4,
        "parent_id": "graph_traversal",
        "prerequisites": [{"topic_id": "graph_traversal", "importance": "required"}],
        "learning_objectives": [
            {"objective": "掌握Dijkstra算法的原理和实现", "bloom_level": "apply"},
            {"objective": "理解Bellman-Ford算法处理负权边", "bloom_level": "understand"},
            {"objective": "掌握Floyd-Warshall算法的多源最短路径", "bloom_level": "apply"},
            {"objective": "能够根据场景选择合适的最短路径算法", "bloom_level": "evaluate"},
        ],
        "common_misconceptions": [
            "Dijkstra不能处理负权边的原因",
        ],
    },
    {
        "id": "mst",
        "name": "最小生成树",
        "category": "algorithm",
        "difficulty_level": 3,
        "parent_id": "graph_traversal",
        "prerequisites": [{"topic_id": "graph_traversal", "importance": "required"}],
        "learning_objectives": [
            {"objective": "掌握Prim算法的原理和实现", "bloom_level": "apply"},
            {"objective": "掌握Kruskal算法及并查集的应用", "bloom_level": "apply"},
            {"objective": "能够比较两种MST算法的适用场景", "bloom_level": "evaluate"},
        ],
        "common_misconceptions": [
            "MST不一定是唯一的",
        ],
    },

    # ========================
    # SEARCHING & SORTING
    # ========================
    {
        "id": "searching",
        "name": "查找算法",
        "category": "algorithm",
        "difficulty_level": 2,
        "parent_id": None,
        "prerequisites": [{"topic_id": "arrays", "importance": "required"}],
        "learning_objectives": [
            {"objective": "掌握线性查找和二分查找的原理和实现", "bloom_level": "apply"},
            {"objective": "理解二分查找的变体（查找第一个/最后一个等于target的位置）", "bloom_level": "apply"},
            {"objective": "能够分析各种查找算法的时空复杂度", "bloom_level": "analyze"},
        ],
        "common_misconceptions": [
            "二分查找的实现中的整数溢出和边界条件",
        ],
    },
    {
        "id": "basic_sorting",
        "name": "基础排序算法",
        "category": "algorithm",
        "difficulty_level": 2,
        "parent_id": None,
        "prerequisites": [{"topic_id": "arrays", "importance": "required"}],
        "learning_objectives": [
            {"objective": "掌握冒泡排序、选择排序、插入排序的原理", "bloom_level": "apply"},
            {"objective": "能够分析O(n²)排序算法的时空复杂度", "bloom_level": "analyze"},
            {"objective": "理解插入排序在小规模数据上的优势", "bloom_level": "evaluate"},
        ],
        "common_misconceptions": [
            "不同排序算法在不同场景下各有优势",
        ],
    },
    {
        "id": "advanced_sorting",
        "name": "高级排序算法",
        "category": "algorithm",
        "difficulty_level": 3,
        "parent_id": "basic_sorting",
        "prerequisites": [{"topic_id": "basic_sorting", "importance": "required"}],
        "learning_objectives": [
            {"objective": "掌握快速排序和归并排序的原理与实现", "bloom_level": "apply"},
            {"objective": "理解分治思想在排序中的应用", "bloom_level": "understand"},
            {"objective": "掌握堆排序及其与优先队列的关系", "bloom_level": "apply"},
            {"objective": "能够分析和比较O(n log n)排序算法的适用场景", "bloom_level": "evaluate"},
        ],
        "common_misconceptions": [
            "快排最坏O(n²)但实际性能通常最好",
            "归并排序需要O(n)额外空间",
        ],
    },
    {
        "id": "non_comparison_sorting",
        "name": "非比较排序",
        "category": "algorithm",
        "difficulty_level": 3,
        "parent_id": "advanced_sorting",
        "prerequisites": [{"topic_id": "advanced_sorting", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "掌握计数排序、基数排序和桶排序的原理", "bloom_level": "apply"},
            {"objective": "理解非比较排序的前提条件和局限性", "bloom_level": "evaluate"},
        ],
        "common_misconceptions": [
            "非比较排序虽然O(n)但空间开销大，只适用于特定场景",
        ],
    },

    # ========================
    # HASHING
    # ========================
    {
        "id": "hashing",
        "name": "哈希表",
        "category": "data_structure",
        "difficulty_level": 3,
        "parent_id": None,
        "prerequisites": [{"topic_id": "arrays", "importance": "required"}, {"topic_id": "linked_lists", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "理解哈希函数的设计原则", "bloom_level": "understand"},
            {"objective": "掌握冲突解决方法（链地址法、开放寻址法）", "bloom_level": "apply"},
            {"objective": "理解负载因子和rehash机制", "bloom_level": "understand"},
            {"objective": "能够分析哈希表操作的平均和均摊复杂度", "bloom_level": "analyze"},
        ],
        "common_misconceptions": [
            "哈希表不是真正的O(1)，最坏情况可退化为O(n)",
        ],
    },

    # ========================
    # ALGORITHM TECHNIQUES
    # ========================
    {
        "id": "recursion",
        "name": "递归",
        "category": "technique",
        "difficulty_level": 2,
        "parent_id": None,
        "prerequisites": [{"topic_id": "stacks", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "掌握递归的基本思想和三要素", "bloom_level": "apply"},
            {"objective": "理解递归调用栈的工作机制", "bloom_level": "understand"},
            {"objective": "能够使用递归解决分形、树遍历等问题", "bloom_level": "apply"},
            {"objective": "掌握递归转迭代的方法", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "递归不一定比迭代慢（尾递归优化）",
        ],
    },
    {
        "id": "divide_conquer",
        "name": "分治法",
        "category": "technique",
        "difficulty_level": 3,
        "parent_id": None,
        "prerequisites": [{"topic_id": "recursion", "importance": "required"}],
        "learning_objectives": [
            {"objective": "理解分治法的三个步骤：分解、解决、合并", "bloom_level": "understand"},
            {"objective": "掌握归并排序、快速排序中的分治思想", "bloom_level": "apply"},
            {"objective": "能够使用主定理分析分治算法复杂度", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "分治与动态规划的区别",
        ],
    },
    {
        "id": "dynamic_programming",
        "name": "动态规划",
        "category": "technique",
        "difficulty_level": 4,
        "parent_id": None,
        "prerequisites": [
            {"topic_id": "recursion", "importance": "required"},
            {"topic_id": "divide_conquer", "importance": "recommended"},
        ],
        "learning_objectives": [
            {"objective": "理解最优子结构和重叠子问题的概念", "bloom_level": "understand"},
            {"objective": "掌握记忆化搜索和自底向上DP两种实现方式", "bloom_level": "apply"},
            {"objective": "能够解决经典DP问题（背包、LCS、LIS、编辑距离）", "bloom_level": "apply"},
            {"objective": "掌握状态压缩DP和滚动数组优化", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "DP不是万能的，需要满足最优子结构",
            "混淆DP和贪心算法的适用条件",
        ],
    },
    {
        "id": "greedy",
        "name": "贪心算法",
        "category": "technique",
        "difficulty_level": 3,
        "parent_id": None,
        "prerequisites": [{"topic_id": "basic_sorting", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "理解贪心算法的基本思想和适用条件", "bloom_level": "understand"},
            {"objective": "掌握活动选择、哈夫曼编码、最小生成树中的贪心策略", "bloom_level": "apply"},
            {"objective": "能够证明贪心选择的正确性", "bloom_level": "evaluate"},
        ],
        "common_misconceptions": [
            "贪心策略的正确性需要严格证明",
        ],
    },
    {
        "id": "backtracking",
        "name": "回溯算法",
        "category": "technique",
        "difficulty_level": 3,
        "parent_id": None,
        "prerequisites": [{"topic_id": "recursion", "importance": "required"}],
        "learning_objectives": [
            {"objective": "理解回溯算法的搜索树模型和剪枝策略", "bloom_level": "understand"},
            {"objective": "掌握N皇后、排列组合、子集生成等经典问题", "bloom_level": "apply"},
            {"objective": "能够设计有效的剪枝策略减少搜索空间", "bloom_level": "create"},
        ],
        "common_misconceptions": [
            "回溯和DFS的关系：回溯是DFS在解空间树上的应用",
        ],
    },

    # ========================
    # ADVANCED TOPICS
    # ========================
    {
        "id": "union_find",
        "name": "并查集（Disjoint Set Union）",
        "category": "data_structure",
        "difficulty_level": 3,
        "parent_id": None,
        "prerequisites": [{"topic_id": "arrays", "importance": "required"}, {"topic_id": "trees_basic", "importance": "recommended"}],
        "learning_objectives": [
            {"objective": "理解并查集的数据结构和操作原理", "bloom_level": "understand"},
            {"objective": "掌握路径压缩和按秩合并的优化技术", "bloom_level": "apply"},
            {"objective": "能够使用并查集解决连通性和等价类问题", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "路径压缩+按秩合并后的近似O(1)复杂度（逆阿克曼函数）",
        ],
    },
    {
        "id": "segment_tree",
        "name": "线段树",
        "category": "data_structure",
        "difficulty_level": 5,
        "parent_id": None,
        "prerequisites": [
            {"topic_id": "trees_basic", "importance": "required"},
            {"topic_id": "divide_conquer", "importance": "recommended"},
        ],
        "learning_objectives": [
            {"objective": "理解线段树的构建和区间查询原理", "bloom_level": "understand"},
            {"objective": "掌握线段树的区间更新和懒标记技术", "bloom_level": "apply"},
            {"objective": "了解线段树在区间问题中的应用", "bloom_level": "apply"},
        ],
        "common_misconceptions": [
            "线段树的空间复杂度是4n而非2n",
        ],
    },
    {
        "id": "bit",
        "name": "树状数组（Fenwick Tree）",
        "category": "data_structure",
        "difficulty_level": 4,
        "parent_id": None,
        "prerequisites": [{"topic_id": "arrays", "importance": "required"}],
        "learning_objectives": [
            {"objective": "理解树状数组的原理和lowbit操作", "bloom_level": "understand"},
            {"objective": "掌握树状数组的单点更新和前缀查询", "bloom_level": "apply"},
            {"objective": "能够比较树状数组和线段树的适用场景", "bloom_level": "evaluate"},
        ],
        "common_misconceptions": [
            "树状数组不支持区间更新（需配合差分使用）",
        ],
    },
]

# Topic adjacency: prerequisite relationships for graph construction
# Derived from the 'prerequisites' field in each topic above

def build_adjacency_list():
    """Build adjacency list for the DSA knowledge graph."""
    adj = {}
    for topic in DSA_TOPICS:
        tid = topic["id"]
        if tid not in adj:
            adj[tid] = []
        for prereq in topic.get("prerequisites", []):
            prereq_id = prereq["topic_id"]
            if prereq_id not in adj:
                adj[prereq_id] = []
            adj[prereq_id].append(tid)
    return adj


def get_topic_by_id(topic_id: str) -> dict | None:
    """Get a topic by its ID."""
    for topic in DSA_TOPICS:
        if topic["id"] == topic_id:
            return topic
    return None


def get_topics_by_category(category: str) -> list:
    """Get all topics in a given category."""
    return [t for t in DSA_TOPICS if t["category"] == category]


def get_prerequisite_chain(topic_id: str) -> list:
    """Get the full prerequisite chain for a topic (recursive)."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        return []
    chain = []
    for prereq in topic.get("prerequisites", []):
        chain.extend(get_prerequisite_chain(prereq["topic_id"]))
        chain.append({
            "topic_id": prereq["topic_id"],
            "name": get_topic_by_id(prereq["topic_id"])["name"] if get_topic_by_id(prereq["topic_id"]) else "",
            "importance": prereq["importance"],
        })
    return chain


def topological_order() -> list:
    """Topological sort of all DSA topics based on prerequisites."""
    in_degree = {t["id"]: 0 for t in DSA_TOPICS}
    adj = {t["id"]: [] for t in DSA_TOPICS}

    for topic in DSA_TOPICS:
        for prereq in topic.get("prerequisites", []):
            adj[prereq["topic_id"]].append(topic["id"])
            in_degree[topic["id"]] += 1

    queue = [tid for tid, deg in in_degree.items() if deg == 0]
    result = []

    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result
