# 算法技巧：递归、分治、动态规划、贪心、回溯

## 递归

### 三要素
1. **边界条件**（停止递归）：不含递归调用的简单情况
2. **递归关系**：如何将大问题分解为小问题
3. **向边界收敛**：每次递归使问题规模减小

```python
def factorial(n):
    if n <= 1:          # 边界条件
        return 1
    return n * factorial(n - 1)  # 递归关系 + 收敛
```

### 尾递归优化
若递归调用是函数的最后一步操作，编译器/解释器可复用当前栈帧，避免栈溢出。

## 分治 (Divide and Conquer)

### 三步骤
1. **分解 (Divide)**：将问题分为若干子问题
2. **解决 (Conquer)**：递归解决子问题
3. **合并 (Combine)**：将子问题解合并为原问题解

### 经典应用：归并排序、快速排序、二分查找、大整数乘法 (Karatsuba)

### 主定理分析
$$
T(n) = a \cdot T\!\left(\frac{n}{b}\right) + f(n)
$$
- 若 $f(n) = O(n^{\log_b a - \epsilon})$ → $T(n) = \Theta(n^{\log_b a})$
- 若 $f(n) = \Theta(n^{\log_b a})$ → $T(n) = \Theta(n^{\log_b a} \log n)$
- 若 $f(n) = \Omega(n^{\log_b a + \epsilon})$ 且 $af(n/b) \le cf(n)$ → $T(n) = \Theta(f(n))$

## 动态规划 (DP)

### 两个必要条件
1. **最优子结构**：最优解包含子问题的最优解
2. **重叠子问题**：子问题被重复计算

### 实现方式

**记忆化搜索（自顶向下）**：
```python
def fib_memo(n, memo={}):
    if n <= 1:
        return n
    if n not in memo:
        memo[n] = fib_memo(n - 1) + fib_memo(n - 2)
    return memo[n]
```

**自底向上 DP（迭代填表）**：
```python
def fib_dp(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]
```

### 经典问题

1. **0-1 背包**：$dp[i][w] = \max(dp[i-1][w], dp[i-1][w-w_i] + v_i)$
2. **最长公共子序列 (LCS)**：
   $$dp[i][j] = \begin{cases} dp[i-1][j-1] + 1 & a_i = b_j \\ \max(dp[i-1][j], dp[i][j-1]) & a_i \neq b_j \end{cases}$$
3. **最长递增子序列 (LIS)**：$dp[i] = \max_{j < i, arr[j] < arr[i]}(dp[j] + 1)$
4. **编辑距离**：
   $$dp[i][j] = \min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1] + (a_i \neq b_j))$$

### 状态压缩
当 $dp[i]$ 仅依赖 $dp[i-1]$ 时，可用**滚动数组**将空间从 $O(n^2)$ 降至 $O(n)$。

## 贪心 (Greedy)

### 基本思想
每步做局部最优选择，期望最终获得全局最优。

### 适用条件
需要证明**贪心选择性质**（局部最优能构成全局最优）和最优子结构。

### 经典应用
- 活动选择问题
- 哈夫曼编码
- 最小生成树（Kruskal, Prim）
- Dijkstra 最短路径
- 找零问题（特定面额体系）

## 回溯 (Backtracking)

### 基本思想
系统地搜索解空间树。当发现当前路径不可能是有效解时，"回溯"到上一步尝试其他分支。

### 剪枝优化
- **可行性剪枝**：当前状态不可能产生有效解
- **最优性剪枝**：当前状态不可能优于已知最优解

### 经典问题：N皇后

```python
def solve_n_queens(n):
    board = [['.'] * n for _ in range(n)]
    cols = set()
    diag1 = set()  # r + c
    diag2 = set()  # r - c

    def backtrack(row):
        if row == n:
            return [[''.join(r) for r in board]]
        result = []
        for col in range(n):
            if col in cols or (row + col) in diag1 or (row - col) in diag2:
                continue
            board[row][col] = 'Q'
            cols.add(col)
            diag1.add(row + col)
            diag2.add(row - col)
            result.extend(backtrack(row + 1))
            board[row][col] = '.'
            cols.remove(col)
            diag1.remove(row + col)
            diag2.remove(row - col)
        return result

    return backtrack(0)
```

## 算法选择指南

| 问题特征 | 推荐算法 |
|---------|---------|
| 最优子结构 + 重叠子问题 | 动态规划 |
| 局部最优 = 全局最优 | 贪心 |
| 需要搜索所有解 | 回溯 |
| 可分解为独立子问题 | 分治 |
| 问题规模指数级但可剪枝 | 分支限界 |

## 常见误区

- **误区**：DP 和贪心可以互相替代。
  **正确**：贪心需要更严格的条件（贪心选择性质），DP 适用范围更广但更复杂。

- **误区**：记忆化搜索和自底向上 DP 完全相同。
  **正确**：记忆化是惰性求值（可能跳过不需要的子问题），自底向上是严格按拓扑序计算。各有适用场景。

- **误区**：回溯就是暴力搜索。
  **正确**：加上有效剪枝后，回溯可大幅缩小搜索空间。好的剪枝策略是关键。
