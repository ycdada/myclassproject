# 字符串

## 基本概念

字符串是字符的有序序列，在大多编程语言中通常实现为不可变字符数组。

## 字符串匹配算法

### 暴力匹配

```python
def brute_force(text, pattern):
    n, m = len(text), len(pattern)
    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pattern[j]:
            j += 1
        if j == m:
            return i  # 匹配成功
    return -1
```
时间复杂度 $O(n \cdot m)$，最坏情况出现在如 `text="aaaaab"`, `pattern="aaab"` 的场景。

### KMP 算法

核心思想：利用已匹配部分的信息，避免主串指针回溯。

**next 数组**：记录模式串中每个位置的最长相等前后缀长度。

```python
def build_next(pattern):
    m = len(pattern)
    next_arr = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = next_arr[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        next_arr[i] = j
    return next_arr

def kmp_search(text, pattern):
    next_arr = build_next(pattern)
    j = 0
    for i, ch in enumerate(text):
        while j > 0 and ch != pattern[j]:
            j = next_arr[j - 1]
        if ch == pattern[j]:
            j += 1
        if j == len(pattern):
            return i - j + 1
    return -1
```
时间复杂度 $O(n + m)$。KMP 算法的 next 数组构建和匹配过程均只线性扫描一次。

### Boyer-Moore 算法

从模式串末尾向前匹配，利用坏字符规则和好后缀规则跳过尽可能多的位置。在实际应用中通常比 KMP 更快，平均可达到亚线性时间复杂度。

## 字符串哈希 (Rabin-Karp)

将字符串映射为整数值，通过比较哈希值来快速判断相等。

```python
def rabin_karp(text, pattern):
    n, m = len(text), len(pattern)
    base, mod = 256, 10**9 + 7
    # 计算 pattern 的哈希值
    pattern_hash = 0
    for ch in pattern:
        pattern_hash = (pattern_hash * base + ord(ch)) % mod

    # 滚动哈希
    text_hash = 0
    power = pow(base, m - 1, mod)
    for i in range(n):
        if i >= m:
            text_hash = (text_hash - ord(text[i - m]) * power) % mod
        text_hash = (text_hash * base + ord(text[i])) % mod
        if i >= m - 1 and text_hash == pattern_hash:
            if text[i - m + 1:i + 1] == pattern:
                return i - m + 1
    return -1
```

## 常见误区

- **误区**：KMP 一定比暴力匹配快。
  **正确**：对于短模式串或无重复模式，暴力匹配的常数因子可能更小。

- **误区**：字符串哈希碰撞可以忽略。
  **正确**：在比赛中，单哈希可能被构造数据卡掉，需要使用双哈希或更大模数。
