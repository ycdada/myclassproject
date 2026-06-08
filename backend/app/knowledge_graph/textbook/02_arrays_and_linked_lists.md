# 数组与链表

## 数组 (Array)

### 核心概念
数组是一块**连续内存**中存储的相同类型元素集合。通过索引可以在 $O(1)$ 时间内访问任意元素。

### 内存模型
- 数组在内存中占据连续地址空间
- 元素 `arr[i]` 的地址 = 基地址 + i × 元素大小
- 这解释了为什么数组支持随机访问

### 动态数组（如 Python list, Java ArrayList）

```python
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

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity
```

动态数组的尾插均摊复杂度为 $O(1)$。

### 时间复杂度总结

| 操作 | 数组（静态/动态） |
|------|-----------------|
| 按索引访问 | $O(1)$ |
| 按值搜索 | $O(n)$ |
| 末尾插入 | $O(1)^*$（动态数组均摊） |
| 中间插入 | $O(n)$ |
| 删除 | $O(n)$ |

## 链表 (Linked List)

### 核心概念
链表由一系列**节点**组成，每个节点包含数据和指向下一个节点的指针。节点在内存中不必连续。

### 单链表节点定义

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

### 单链表操作

**遍历** — $O(n)$：
```python
def traverse(head):
    curr = head
    while curr:
        print(curr.val)
        curr = curr.next
```

**插入** — 在指定位置后插入，$O(1)$（已知节点）：
```python
def insert_after(node, new_node):
    new_node.next = node.next
    node.next = new_node
```

**删除** — 删除指定节点的后继节点，$O(1)$：
```python
def delete_after(node):
    if node.next:
        node.next = node.next.next
```

### 双向链表

每个节点有两个指针：`prev` 和 `next`，可双向遍历。删除任意节点只需 $O(1)$（已知该节点）。

### 链表技巧

1. **快慢指针**（Floyd判圈算法）
```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

2. **哨兵节点（Dummy Node）**
简化边界条件处理，避免额外的头节点判断。

3. **递归处理**
链表天然支持递归：`reverseList(head) = reverseList(head.next) + 将head接到尾部`

### 数组 vs 链表

| 特性 | 数组 | 链表 |
|------|------|------|
| 内存 | 连续 | 分散 |
| 随机访问 | $O(1)$ | $O(n)$ |
| 插入/删除 | $O(n)$ | $O(1)$（已知位置） |
| 缓存友好 | 是 | 否 |
| 额外空间 | 无 | 每个节点需存指针 |
| 动态扩容 | 需要（均摊） | 天然动态 |

## 常见误区

- **误区**：链表插入和删除总是 $O(1)$。
  **正确**：仅在已知节点位置时是 $O(1)$；若需先搜索到该位置，则为 $O(n)$。

- **误区**：删除链表节点只需将其标记为删除即可。
  **正确**：需要更新前驱节点的指针，因此单链表删除后继比删除自身容易。

- **误区**：动态数组扩容每次都翻倍，空间浪费很大。
  **正确**：均摊分析表明，扩容操作的总体开销是可接受的。
