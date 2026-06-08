# 栈与队列

## 栈 (Stack)

### 核心概念
栈是一种**后进先出 (LIFO)** 的线性数据结构。只能在栈顶进行插入（push）和删除（pop）操作。

### 基本操作

| 操作 | 描述 | 时间复杂度 |
|------|------|-----------|
| `push(x)` | 将 x 压入栈顶 | $O(1)$ |
| `pop()` | 移除并返回栈顶元素 | $O(1)$ |
| `peek()` / `top()` | 返回栈顶元素但不移除 | $O(1)$ |
| `isEmpty()` | 判断栈是否为空 | $O(1)$ |

### 实现方式

**数组实现**：
```python
class ArrayStack:
    def __init__(self):
        self.data = []

    def push(self, x):
        self.data.append(x)

    def pop(self):
        if self.isEmpty():
            raise IndexError("Stack is empty")
        return self.data.pop()

    def peek(self):
        if self.isEmpty():
            raise IndexError("Stack is empty")
        return self.data[-1]

    def isEmpty(self):
        return len(self.data) == 0
```

**链表实现**（链表头作为栈顶，避免尾部遍历）：
```python
class LinkedStack:
    def __init__(self):
        self.head = None

    def push(self, x):
        new_node = ListNode(x)
        new_node.next = self.head
        self.head = new_node

    def pop(self):
        if not self.head:
            raise IndexError("Stack is empty")
        val = self.head.val
        self.head = self.head.next
        return val
```

### 经典应用

1. **括号匹配**：使用栈验证 `([{}])` 是否匹配
2. **表达式求值**：中缀→后缀（逆波兰），再计算后缀表达式
3. **函数调用栈**：递归隐式使用系统调用栈
4. **撤销操作**：编辑器中的 Ctrl+Z
5. **单调栈**：求下一个更大元素

```python
def next_greater_element(nums):
    """单调递减栈求下一个更大元素"""
    stack = []
    result = [-1] * len(nums)
    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            result[stack.pop()] = num
        stack.append(i)
    return result
```

## 队列 (Queue)

### 核心概念
队列是一种**先进先出 (FIFO)** 的线性数据结构。在队尾插入（enqueue），在队头删除（dequeue）。

### 基本操作

| 操作 | 描述 | 时间复杂度 |
|------|------|-----------|
| `enqueue(x)` | 将 x 加入队尾 | $O(1)$ |
| `dequeue()` | 移除并返回队头元素 | $O(1)$ |
| `front()` | 返回队头元素 | $O(1)$ |
| `isEmpty()` | 判断队列是否为空 | $O(1)$ |

### 循环队列

使用固定大小数组 + 两个指针 `front` 和 `rear` 实现。通过取模运算实现循环。

```python
class CircularQueue:
    def __init__(self, k):
        self.data = [None] * k
        self.front = 0
        self.rear = 0
        self.size = 0
        self.capacity = k

    def enqueue(self, x):
        if self.isFull():
            return False
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.capacity
        self.size += 1
        return True

    def dequeue(self):
        if self.isEmpty():
            return False
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return True
```

### 双端队列 (Deque)

允许在两端进行插入和删除。Python 的 `collections.deque` 是双向链表实现，两端操作均为 $O(1)$。

### 优先队列

元素按优先级出队，而非按入队顺序。通常用**堆（Heap）**实现，插入和删除均为 $O(\log n)$。

### 经典应用

1. **BFS**：图的广度优先遍历使用队列
2. **任务调度**：操作系统进程调度
3. **消息队列**：异步处理、解耦系统
4. **滑动窗口**：使用双端队列维护窗口最值

```python
from collections import deque

def max_sliding_window(nums, k):
    """单调队列求滑动窗口最大值"""
    dq = deque()
    result = []
    for i, num in enumerate(nums):
        while dq and nums[dq[-1]] < num:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

## 常见误区

- **误区**：栈只能使用数组实现。
  **正确**：链表也可以，且天然不需要扩容。选择取决于具体需求（随机访问 vs 频繁扩容）。

- **误区**：队列和栈可以互相替代。
  **正确**：虽然可以用两个栈模拟队列（反之亦然），但会有额外开销，应根据语义选择合适结构。

- **误区**：优先队列就是排序后的队列。
  **正确**：优先队列基于堆实现，每次出队取最值（$O(\log n)$），而非维护全局有序。
