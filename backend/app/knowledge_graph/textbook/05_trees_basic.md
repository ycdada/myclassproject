# 树的基本概念

## 树的定义

树是 $n (n \ge 0)$ 个节点的有限集合：
- 当 $n=0$ 时为空树
- 当 $n>0$ 时，有且仅有一个**根节点 (root)**，其余节点可分为 $m$ 个互不相交的有限集合，每个集合本身又是一棵树，称为根的**子树 (subtree)**

### 基本术语

| 术语 | 定义 |
|------|------|
| 度 (degree) | 节点的子树个数 |
| 叶子 (leaf) | 度为0的节点 |
| 深度 (depth) | 从根到该节点的路径长度（根深度为0） |
| 高度 (height) | 从该节点到最深叶子的路径长度 |
| 层 (level) | 深度相同的节点属于同一层 |
| 森林 (forest) | $m$ 棵互不相交的树的集合 |

## 二叉树 (Binary Tree)

每个节点最多有两个子树（左子树和右子树），有左右之分。

### 二叉树性质
1. 第 $i$ 层最多有 $2^i$ 个节点（根为第0层）
2. 深度为 $k$ 的二叉树最多有 $2^{k+1} - 1$ 个节点
3. 对任何二叉树，若叶子数为 $n_0$，度为2的节点数为 $n_2$，则 $n_0 = n_2 + 1$

### 特殊二叉树
- **满二叉树**：深度为 $k$ 且有 $2^{k+1} - 1$ 个节点
- **完全二叉树**：从上到下、从左到右依次填充，与满二叉树的前 $n$ 个节点对应

### 二叉树遍历

**前序遍历**（根 → 左 → 右）：
```python
def preorder(root):
    if not root:
        return
    print(root.val)
    preorder(root.left)
    preorder(root.right)
```

**中序遍历**（左 → 根 → 右）：
```python
def inorder(root):
    if not root:
        return
    inorder(root.left)
    print(root.val)
    inorder(root.right)
```

**后序遍历**（左 → 右 → 根）：
```python
def postorder(root):
    if not root:
        return
    postorder(root.left)
    postorder(root.right)
    print(root.val)
```

**层序遍历（BFS）**：
```python
from collections import deque

def level_order(root):
    if not root:
        return
    q = deque([root])
    while q:
        node = q.popleft()
        print(node.val)
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
```

### 递归转非递归

前序遍历（迭代）：
```python
def preorder_iterative(root):
    stack = [root]
    while stack:
        node = stack.pop()
        if node:
            print(node.val)
            stack.append(node.right)  # 右先入栈
            stack.append(node.left)   # 左后入栈
```

中序遍历（迭代）：
```python
def inorder_iterative(root):
    stack = []
    curr = root
    while stack or curr:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        print(curr.val)
        curr = curr.right
```

### 树的存储结构

1. **二叉链表**：每个节点存 `val`, `left`, `right`
2. **数组表示**：对完全二叉树，$i$ 的左子为 $2i+1$，右子为 $2i+2$，父为 $(i-1)/2$
3. **三叉链表**：在二叉链表基础上增加 `parent` 指针

## 常见误区

- **误区**：树的深度和高度定义相同。
  **正确**：深度是从根向下（根深为0），高度是从叶向上。不同教材定义可能不同。

- **误区**：递归遍历一定比迭代慢。
  **正确**：尾递归优化后差别不大，但递归可能栈溢出。迭代使用显式栈，内存由堆管理。

- **误区**：完全二叉树一定是满二叉树。
  **正确**：完全二叉树只要求最后一层左对齐填充，不一定所有层都满。
