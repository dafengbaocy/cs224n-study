## co-occurrence-matrix — 共现矩阵 + SVD 降维 {#co-occurrence-matrix}

> **Waypoint**: WP02 · 分布语义学
> **概念**: 从语料构建共现矩阵并做 SVD 降维
> **官方锚点**: Notes §3.1 (co-occurrence matrices); A1 Part 1 Q1.1-1.3

### 为什么不能只看文字

Notes §3.1 描述了 co-occurrence matrix 的构建过程，但只有实际构建一个小矩阵并做 [[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]] 才能理解：
- 矩阵有多稀疏（15×15=225 格里只有 80 个非零 = 64.4% 稀疏）
- 窗口大小如何影响共现统计（window=1 vs 2 vs 4 差异明显）
- log 归一化为什么必要（Notes §3.1: "replace each count X_ij with log(1 + X_ij)"）
- SVD 降维后语义相近的词是否真的聚在一起（within-cluster cosine 0.99 vs cross-cluster 0.15）

### 概念

从离散词的共现次数出发：

1. 扫一遍语料，统计每个词在一定窗口内和哪些上下文词一起出现 → [[Lectures/L01-word-vectors/00-concept-glossary#co-occurrence-matrix|co-occurrence-matrix]]
2. 对计数做 log(1+x) 归一化，降低高频词的支配效应
3. 矩阵很稀疏、很高维 → 用 [[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]] 截断到低维（k=2）
4. 低维坐标变成 [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense vector]] → 可以用 [[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|cosine similarity]] 比较

### 运行

```bash
.venv/bin/python Labs/L01-word-vectors/co-occurrence-matrix.py
```

或在 Colab 打开：

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/co-occurrence-matrix.ipynb)

### 数据：小语料 → 共现矩阵

14 句话、15 个词的小语料，分两个语义簇 + 桥接句：

- **Finance 簇**: banking, money, finance, economy, market, invest
- **Nature 簇**: river, lake, forest, mountain, valley, ocean
- **桥接词**: the, flows, grows

以 `window_size=2`（左右各 2 个词）构建的 [[Lectures/L01-word-vectors/00-concept-glossary#co-occurrence-matrix|共现矩阵]]：

- 矩阵形状: (15, 15) = 225 entries
- 总共现次数: 140
- 非零元素: 80
- 稀疏度: 64.4%

![Co-occurrence matrix heatmap](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-162027.png)

> [!tip] 看图要点
> 左图是原始计数，右图是 log(1+x) 归一化。注意右图的颜色差异更均匀——log 归一化防止了高频词（如 `the`）支配整个矩阵。

### SVD 降维：15D → 2D

对 log 归一化后的矩阵做 [[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]]，取前 k=2 个奇异值：

- 奇异值: σ₁=5.898, σ₂=5.187
- 解释方差比: **75.3%**（仅 2 维就保留了 3/4 的信息）

![SVD 2D embeddings](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-162035.png)

> [!info] 关键观察
> Finance 词（红圆）和 Nature 词（绿方）在 2D 空间中**完全分开**！仅凭共现计数 + 线性降维，就自动发现了语义类别。

### Cosine Similarity 验证

| 对比类型 | 词对 | cosine |
|---|---|---|
| 同簇 (finance) | banking ↔ money | 0.9910 |
| 同簇 (finance) | banking ↔ finance | 0.9910 |
| 同簇 (finance) | money ↔ finance | 1.0000 |
| 同簇 (nature) | river ↔ lake | 0.9898 |
| 同簇 (nature) | river ↔ forest | 0.9999 |
| 同簇 (nature) | lake ↔ forest | 0.9875 |
| **跨簇** | banking ↔ river | 0.2805 |
| **跨簇** | banking ↔ lake | 0.1406 |
| **跨簇** | money ↔ forest | 0.1642 |

- **Mean within-cluster cosine: 0.9932**
- **Mean cross-cluster cosine: 0.1508**
- **Difference: 0.8424**

> [!tip] 直觉
> 同簇词的 cosine 接近 1（方向几乎相同），跨簇词接近 0（方向几乎正交）。这就是分布语义的核心：**语义相似的词在向量空间中方向相近**。

### 窗口大小的影响

![Window size comparison](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-162038.png)

| Window | Total count | Nonzero | Sparsity | Explained var (k=2) | cos(banking,finance) | cos(river,lake) | cos(banking,river) |
|---|---|---|---|---|---|---|---|
| 1 | 84 | 54 | 76.0% | 55.1% | 0.9920 | 0.9814 | 0.4004 |
| 2 | 140 | 80 | 64.4% | 75.3% | 0.9910 | 0.9898 | 0.2805 |
| 4 | 168 | 84 | 62.7% | 75.7% | 0.9908 | 0.9915 | 0.2597 |

> [!info] Notes §3.1 洞察
> - **小窗口** (w=1): 矩阵更稀疏（76%），解释方差更低（55%），但跨簇区分度还行（0.40）——捕获更多**局部/语法**信息
> - **大窗口** (w=4): 矩阵更密（63% 稀疏），解释方差更高（76%），跨簇区分更好（0.26）——捕获更多**全局/语义**信息
> - 这就是为什么 Notes §3.1 说："A small window will capture syntactic features... a large window will capture semantic features"

### 对应 Assignment

- **A1 Part 1 Q1.1**: 实现 `distinct_words` — 本脚本的 `build_vocab()` 做了同样的事
- **A1 Part 1 Q1.2**: 实现 `co_occurrence_matrix` — 本脚本的 `build_cooccurrence()` 是简化版
- **A1 Part 1 Q1.3**: 实现 `reduce_to_k_dim` (SVD) — 本脚本用 `scipy.linalg.svd` 做了同样的截断

numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T081828Z__t_64256cc7__co-occurrence-matrix
  stdout: Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt
  checked_values:
    - claim: "Matrix shape: (15, 15) = 225 entries"
      source: "stdout line: Matrix shape: (15, 15) = 225 entries"
      status: copied_from_output
    - claim: "Total co-occurrence count: 140"
      source: "stdout line: Total co-occurrence count: 140"
      status: copied_from_output
    - claim: "Nonzero entries: 80, Sparsity: 64.4%"
      source: "stdout line: Nonzero entries: 80 / Sparsity: 64.4%"
      status: copied_from_output
    - claim: "Explained variance ratio: 75.3%"
      source: "stdout line: Explained variance ratio: 75.3%"
      status: copied_from_output
    - claim: "Mean within-cluster cosine: 0.9932"
      source: "stdout line: Mean within-cluster cosine:  0.9932"
      status: copied_from_output
    - claim: "Mean cross-cluster cosine: 0.1508"
      source: "stdout line: Mean cross-cluster cosine:   0.1508"
      status: copied_from_output
    - claim: "cos(banking, money) = 0.9910"
      source: "stdout line: banking  money  0.9910"
      status: copied_from_output
    - claim: "cos(river, forest) = 0.9999"
      source: "stdout line: river  forest  0.9999"
      status: copied_from_output
    - claim: "Window size 1: explained var 55.1%"
      source: "stdout line: Window size = 1: ... Explained variance (k=2): 55.1%"
      status: copied_from_output
    - claim: "Window size 4: explained var 75.7%"
      source: "stdout line: Window size = 4: ... Explained variance (k=2): 75.7%"
      status: copied_from_output
