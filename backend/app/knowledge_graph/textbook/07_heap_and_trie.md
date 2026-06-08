# 堆与字典树

## 堆 (Heap)

### 定义
堆是一棵**完全二叉树**，每个节点的值不小于（最大堆）或不大于（最小堆）其子节点的值。

### 存储方式
使用数组存储完全二叉树：
- 节点 $i$ 的左子：$2i + 1$
- 节点 $i$ 的右子：$2i + 2$
- 节点 $i$ 的父：$(i-1) // 2$

### 核心操作

**上浮 (sift-up)** — 插入时用：
```python
def sift_up(heap, i):
    while i > 0:
        parent = (i - 1) // 2
        if heap[i] < heap[parent]:  # 最小堆
            heap[i], heap[parent] = heap[parent], heap[i]
            i = parent
        else:
            break
```

**下沉 (sift-down)** — 删除时用：
```python
def sift_down(heap, i, size):
    while True:
        smallest = i
        left, right = 2 * i + 1, 2 * i + 2
        if left < size and heap[left] < heap[smallest]:
            smallest = left
        if right < size and heap[right] < heap[smallest]:
            smallest = right
        if smallest == i:
            break
        heap[i], heap[smallest] = heap[smallest], heap[i]
        i = smallest
```

**建堆 (heapify)** — 从最后一个非叶节点向前建堆，时间复杂度 $O(n)$：
```python
def heapify(arr):
    for i in range(len(arr) // 2 - 1, -1, -1):
        sift_down(arr, i, len(arr))
```

**建堆复杂度 $O(n)$ 的证明**：每个节点的下沉代价与其高度成正比。高度为 $h$ 的节点数不超过 $n/2^{h+1}$，总时间为 $\sum_{h=0}^{\log n} n/2^{h+1} \cdot O(h) = O(n)$。

### 应用

1. **优先队列**：插入/删除最小值 $O(\log n)$
2. **堆排序**：建堆 $O(n)$ + $n$ 次删除 $O(n \log n)$，总 $O(n \log n)$，原地排序
3. **Top-K 问题**：维护大小为 K 的最小堆，$O(n \log k)$

```python
import heapq

def top_k(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap
```

## 字典树 (Trie)

### 定义
Trie 是一种树形结构，用于高效地存储和检索字符串集合中的键。每个节点代表一个字符，从根到节点的路径构成该节点对应的前缀。

### 节点定义

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.count = 0  # 以该节点结尾的单词数
```

### 基本操作

```python
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
        node.count += 1

    def search(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True
```

### 复杂度
- 插入/查找：$O(L)$，$L$ 为字符串长度
- 空间：$O(N \times L)$，在最坏情况下可能很大

### 应用
- 自动补全（autocomplete）
- 拼写检查
- IP 路由的最长前缀匹配
- 异或最大值（二进制 Trie）

## 常见误区

- **误区**：建堆的复杂度是 $O(n \log n)$。
  **正确**：Floyd 建堆法从下往上 sift-down，总复杂度为 $O(n)$。

- **误区**：Trie 的空间消耗可以忽略。
  **正确**：Trie 可能占用大量空间，尤其是字符集较大时。可用压缩 Trie 或三叉搜索树优化。
