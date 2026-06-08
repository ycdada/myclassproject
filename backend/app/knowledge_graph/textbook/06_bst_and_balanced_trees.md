# 二叉搜索树与平衡树

## 二叉搜索树 (BST)

### 定义
二叉搜索树满足：对任意节点，左子树所有节点值 < 该节点值 < 右子树所有节点值。中序遍历BST可以得到有序序列。

### 基本操作

**查找** — $O(h)$（$h$ 为树高）：
```python
def search(root, target):
    if not root or root.val == target:
        return root
    if target < root.val:
        return search(root.left, target)
    return search(root.right, target)
```

**插入** — $O(h)$：
```python
def insert(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root
```

**删除** — $O(h)$，分为三种情况：
1. 叶节点：直接删除
2. 只有一个子节点：用子节点替代
3. 有两个子节点：用**后继节点**（中序后继，即右子树的最小节点）替代

```python
def delete(root, key):
    if not root:
        return None
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:
        # 情况1和2
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        # 情况3：有两个子节点
        successor = find_min(root.right)
        root.val = successor.val
        root.right = delete(root.right, successor.val)
    return root
```

### BST的退化问题
如果按升序插入（如 1,2,3,4,5），BST 退化为链表，高度 $h = n$。平衡树解决此问题。

## AVL 树

### 定义
任何节点的左右子树高度差不超过 1（平衡因子 ∈ {-1, 0, 1}）。

### 旋转操作

**四种旋转情况**：
- **LL**：左子树的左子树过高 → 右旋
- **RR**：右子树的右子树过高 → 左旋
- **LR**：左子树的右子树过高 → 先左旋后右旋
- **RL**：右子树的左子树过高 → 先右旋后左旋

```python
def right_rotate(y):
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    # 更新高度
    y.height = max(height(y.left), height(y.right)) + 1
    x.height = max(height(x.left), height(x.right)) + 1
    return x  # x成为新根

def left_rotate(x):
    y = x.right
    T2 = y.left
    y.left = x
    x.right = T2
    x.height = max(height(x.left), height(x.right)) + 1
    y.height = max(height(y.left), height(y.right)) + 1
    return y
```

插入后从插入点向上回溯，检查每个祖先的平衡因子，对第一个不平衡节点执行旋转。

## 红黑树

### 五条性质
1. 节点是红色或黑色
2. 根节点是黑色
3. 叶节点（NIL）是黑色
4. 红色节点的两个子节点都是黑色（无连续红色）
5. 从任一节点到其每个叶子的所有路径包含相同数量的黑色节点

这些性质保证：最长路径 ≤ 2 × 最短路径，树高为 $O(\log n)$。

### 与 AVL 树比较
- AVL 更严格平衡 → 查找更快，但插入删除需要更多旋转
- 红黑树插入删除旋转次数更少 → 适合频繁修改场景（如 Java TreeMap, C++ std::map）

## 常见误区

- **误区**：BST删除节点时直接用左子或右子替代即可。
  **正确**：双子树情况需要用中序后继/前驱替代并调整树结构。

- **误区**：AVL树双旋转与两次单旋转等价。
  **正确**：LR = 先对左子左旋，再对根右旋，两次旋转的旋转中心不同，效果也不同。
