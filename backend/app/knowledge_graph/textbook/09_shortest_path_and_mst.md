# 最短路径与最小生成树

## Dijkstra 算法

求**非负权图**中单源最短路径。使用优先队列贪心选择当前距离最小的未确定顶点。

```python
import heapq

def dijkstra(graph, start, n):
    dist = [float('inf')] * n
    dist[start] = 0
    pq = [(0, start)]  # (距离, 顶点)

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue  # 跳过已更新的旧记录
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))

    return dist
```
时间复杂度：$O((V+E) \log V)$（使用二叉堆）。

**Dijkstra 不能处理负权边的原因**：一旦顶点被弹出优先队列，其最短距离就被认为已确定。若有负权边，之后可能出现更短路径。

## Bellman-Ford 算法

可以处理**负权边**，并能检测**负权环**。进行 $|V|-1$ 次松弛操作。

```python
def bellman_ford(edges, start, n):
    dist = [float('inf')] * n
    dist[start] = 0

    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break  # 提前终止优化

    # 检测负权环
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return None  # 存在负权环

    return dist
```
时间复杂度：$O(V \cdot E)$。

## Floyd-Warshall 算法

求**所有点对**最短路径。动态规划：$dist[i][j] = \min(dist[i][j], dist[i][k] + dist[k][j])$。

```python
def floyd_warshall(graph, n):
    dist = [[float('inf')] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u in range(n):
        for v, w in graph[u]:
            dist[u][v] = w

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist
```
时间复杂度 $O(n^3)$。适合 $n \le 500$ 的稠密图。

## 最小生成树 (MST)

### Prim 算法

类似 Dijkstra，维护一个不断生长的 MST。

```python
def prim(graph, n):
    visited = [False] * n
    pq = [(0, 0, -1)]  # (权重, 当前顶点, 父节点)
    mst_cost = 0

    while pq:
        w, u, parent = heapq.heappop(pq)
        if visited[u]:
            continue
        visited[u] = True
        mst_cost += w
        for v, weight in graph[u]:
            if not visited[v]:
                heapq.heappush(pq, (weight, v, u))

    return mst_cost
```

### Kruskal 算法

按边权升序排列，用并查集判断是否形成环。

```python
def kruskal(edges, n):
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False
        if rank[px] < rank[py]:
            parent[px] = py
        elif rank[px] > rank[py]:
            parent[py] = px
        else:
            parent[py] = px
            rank[px] += 1
        return True

    edges.sort(key=lambda e: e[2])  # 按权重排序
    mst = []
    for u, v, w in edges:
        if union(u, v):
            mst.append((u, v, w))
        if len(mst) == n - 1:
            break

    return mst
```
时间复杂度 $O(E \log E)$（主要来自排序）。

| 特性 | Prim | Kruskal |
|------|------|---------|
| 适合图类型 | 稠密图 | 稀疏图 |
| 数据结构 | 优先队列 | 并查集 |
| 时间复杂度 | $O((V+E) \log V)$ | $O(E \log E)$ |

## 常见误区

- **误区**：Dijkstra 加一个偏移量就能处理负权边。
  **正确**：给所有边加相同偏移量会改变最短路径的实际结果。

- **误区**：MST 是唯一的。
  **正确**：当存在相同权重的边时，MST 可能不唯一（但最小总权重唯一）。
