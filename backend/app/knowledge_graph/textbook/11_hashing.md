# 哈希表

## 核心概念

哈希表通过哈希函数将键映射到数组索引，实现平均 $O(1)$ 的查找、插入和删除。

### 哈希函数

好的哈希函数应满足：
1. **确定性**：相同键产生相同哈希值
2. **均匀性**：哈希值在值域内均匀分布
3. **高效性**：计算速度快

常见哈希函数：
- 除留余数法：$h(k) = k \bmod m$（$m$ 选素数效果好）
- 乘法哈希法：$h(k) = \lfloor m \cdot (kA \bmod 1) \rfloor$
- Python 的 `hash()` 和 Java 的 `hashCode()`

## 冲突解决

### 链地址法 (Chaining)

每个桶存储一个链表/树。所有哈希到同一位置的元素链在一起。

```python
class ChainingHashMap:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def _hash(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[idx]):
            if k == key:
                self.buckets[idx][i] = (key, value)
                return
        self.buckets[idx].append((key, value))
        self.size += 1

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        raise KeyError(key)
```

### 开放寻址法 (Open Addressing)

所有元素存储在数组中，冲突时按探测序列寻找下一个空位。

**线性探测**：$h(k, i) = (h'(k) + i) \bmod m$
- 优点：缓存友好
- 缺点：一次聚集（primary clustering）

**二次探测**：$h(k, i) = (h'(k) + c_1 i + c_2 i^2) \bmod m$
- 缓解一次聚集
- 可能导致二次聚集

**双重哈希**：$h(k, i) = (h_1(k) + i \cdot h_2(k)) \bmod m$
- 有效避免聚集
- 需 $h_2(k)$ 与 $m$ 互质

### 删除问题

开放寻址中直接删除元素会破坏探测链。使用**惰性删除**（标记墓碑）。

## 负载因子与 Rehash

**负载因子** $\alpha = n / m$（$n$ 为元素数，$m$ 为容量）。

当 $\alpha$ 超过阈值（通常 0.75），进行 **rehash**：新建更大数组，重新插入所有元素。

```python
def check_and_rehash(self):
    if self.size / self.capacity > 0.75:
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)
```

## 时间复杂度

| 操作 | 平均 | 最坏 |
|------|------|------|
| 查找 | $O(1)$ | $O(n)$ |
| 插入 | $O(1)$ | $O(n)$ |
| 删除 | $O(1)$ | $O(n)$ |

最坏情况发生在大量冲突时（所有键映射到同一位置）。

## 常见误区

- **误区**：哈希表总是 $O(1)$。
  **正确**：最坏退化为 $O(n)$。Java HashMap 在链表过长时转为红黑树（$O(\log n)$）来缓解。

- **误区**：负载因子越小越好。
  **正确**：低负载因子减少冲突但浪费空间。需要在时空之间平衡。

- **误区**：哈希函数只需将键转为整数即可。
  **正确**：还需保证低碰撞率和均匀分布。Python `hash()` 对整数返回自身，不适合直接取模。
