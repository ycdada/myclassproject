# 排序与查找

## 基础排序算法 ($O(n^2)$)

### 冒泡排序
每轮将最大元素"冒泡"到末尾。
```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
```
最优 $O(n)$（已有序），最坏 $O(n^2)$。

### 选择排序
每轮选择未排序部分的最小元素。
```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```
严格 $O(n^2)$（即使已有序也要比较每次）。

### 插入排序
将每个元素插入已排序部分的正确位置。
```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```
最优 $O(n)$（已有序），最坏 $O(n^2)$。对**小规模数据**和**基本有序数据**高效。

## 高级排序算法 ($O(n \log n)$)

### 快速排序

```python
def quick_sort(arr, low, high):
    if low < high:
        pivot = partition(arr, low, high)
        quick_sort(arr, low, pivot - 1)
        quick_sort(arr, pivot + 1, high)

def partition(arr, low, high):
    pivot = arr[high]  # 选择最后一个元素为基准
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```
平均 $O(n \log n)$，最坏 $O(n^2)$（每次选到最值）。随机化基准可规避最坏情况。

### 归并排序

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```
严格 $O(n \log n)$，但需 $O(n)$ 额外空间。适合**外部排序**（大数据量磁盘排序）。

### 堆排序

利用最大堆实现原地排序。建堆 $O(n)$ + $n$ 次删除 $O(n \log n)$ = $O(n \log n)$。不需要额外空间。

## 非比较排序

| 算法 | 时间复杂度 | 空间 | 适用条件 |
|------|-----------|------|---------|
| 计数排序 | $O(n+k)$ | $O(k)$ | $k$ 值域较小 |
| 基数排序 | $O(d(n+k))$ | $O(n)$ | 每位取值范围小 |
| 桶排序 | $O(n)$ 平均 | $O(n)$ | 数据均匀分布 |

**非比较排序的局限**：依赖数据分布或值域，无法处理任意类型（如自定义对象）。

## 查找算法

### 二分查找
在有序数组中查找目标值。
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```
使用 `left + (right - left) // 2` 避免 `(left + right)` 整数溢出。

### 二分查找变体
- 查找第一个等于 target 的位置
- 查找最后一个等于 target 的位置
- 查找第一个大于等于 target 的位置 (lower_bound)
- 查找第一个大于 target 的位置 (upper_bound)

## 常见误区

- **误区**：快排一定比归并排序快。
  **正确**：快排常数因子小，平均更快；但需要稳定排序或处理链表时，归并更好。

- **误区**：非比较排序因为 $O(n)$ 所以比 $O(n \log n)$ 好。
  **正确**：非比较排序有隐蔽开销（大空间、受限范围），不能替代通用比较排序。

- **误区**：二分查找实现很简单，不会出错。
  **正确**：1946 年提出，1962 年才有第一个无bug实现。边界条件容易出错。
