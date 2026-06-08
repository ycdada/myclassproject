# 图的基本概念与遍历

## 图的定义

图 $G = (V, E)$ 由顶点集 $V$ 和边集 $E$ 组成。边可以是有向或无向的，可以带权重或不带权重。

### 基本术语

| 术语 | 定义 |
|------|------|
| 度 (degree) | 与该顶点相连的边数（有向图分为入度和出度） |
| 路径 (path) | 顶点序列 $v_1, v_2, ..., v_k$，其中相邻顶点间有边 |
| 简单路径 | 路径中顶点不重复 |
| 环 (cycle) | 起点和终点相同的路径 |
| 连通图 | 任意两顶点间存在路径（有向图为强连通） |
| 连通分量 | 极大连通子图 |
| 生成树 | 包含所有顶点的无环连通子图 |

### 图的存储

**邻接矩阵** — $O(|V|^2)$ 空间，适合稠密图：
```python
adj_matrix = [[0] * n for _ in range(n)]
# 添加边 u→v 权重 w
adj_matrix[u][v] = w
```

**邻接表** — $O(|V| + |E|)$ 空间，适合稀疏图：
```python
adj_list = [[] for _ in range(n)]
# 添加边 u→v 权重 w
adj_list[u].append((v, w))
```

| 操作 | 邻接矩阵 | 邻接表 |
|------|---------|--------|
| 判断 $(u,v)$ 是否存在 | $O(1)$ | $O(\deg(u))$ |
| 遍历所有边 | $O(|V|^2)$ | $O(|V|+|E|)$ |
| 空间 | $O(|V|^2)$ | $O(|V|+|E|)$ |

## 深度优先搜索 (DFS)

DFS 尽可能深地搜索图的分支。使用递归或显式栈实现。

```python
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

DFS 的时间复杂度：$O(|V| + |E|)$（邻接表）。

## 广度优先搜索 (BFS)

BFS 按层遍历图。使用队列实现，求无权图最短路径。

```python
from collections import deque

def bfs(graph, start):
    visited = set([start])
    q = deque([start])
    while q:
        node = q.popleft()
        print(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                q.append(neighbor)
```

BFS 的时间复杂度也是 $O(|V| + |E|)$。

## 拓扑排序

针对**有向无环图 (DAG)**，将顶点排序使得对每条有向边 $(u, v)$，$u$ 在排序中出现在 $v$ 之前。

### Kahn 算法（BFS）

```python
from collections import deque

def topological_sort(n, edges):
    in_degree = [0] * n
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1

    q = deque([i for i in range(n) if in_degree[i] == 0])
    result = []

    while q:
        u = q.popleft()
        result.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                q.append(v)

    return result if len(result) == n else []  # 若存在环则为空
```

### 应用
- 课程安排（先修课约束）
- 构建系统（依赖管理）
- 任务调度

## 常见误区

- **误区**：DFS 递归实现总是更好的。
  **正确**：深层图递归可能栈溢出，需用迭代或增大递归深度限制。

- **误区**：BFS 求最短路径适用于所有图。
  **正确**：BFS 只能求无权图的最短路径（按边数），带权图需用 Dijkstra 等算法。

- **误区**：邻接矩阵在稀疏图只是浪费空间。
  **正确**：空间浪费 $O(|V|^2)$ vs $O(|V|+|E|)$，但 $O(1)$ 的边查询在稠密图有优势。
