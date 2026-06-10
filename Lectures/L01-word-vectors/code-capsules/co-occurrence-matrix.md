## co-occurrence-matrix — 从语料构建共现矩阵并做 SVD 降维 {#co-occurrence-matrix}

> [!info] 本 capsule 解释什么
> Notes §3.1 描述了 co-occurrence matrix 的构建过程，但只有实际构建一个小矩阵并做 SVD 才能理解窗口大小和降维的效果。
> 本 capsule 用一个 6 句话的 toy corpus，完整演示：构建共现矩阵 → SVD 降维到 2D → 散点图可视化。

**Waypoint**: WP02 — One-hot vs Dense Vectors
**Official anchor**: Notes §3.1 (co-occurrence matrices); A1 Part 1 Q1.1-1.3

---

### 这段代码在看什么

1. 用极小语料（6 句话，22 个词）统计词与词在窗口内共同出现的次数
2. 得到一个 22×22 的共现矩阵——**88.4% 的位置是 0**（非常稀疏）
3. 用 SVD 把 22 维向量压缩到 2 维
4. 在 2D 散点图上观察：语义相近的词（cat/dog、bank/river）是否聚在一起

### 运行后先看哪里

**共现矩阵**（窗口大小 = 1）：

```
非零元素: 56/484 = 11.6%
稀疏度:   88.4%
```

- "the" 行/列最密（因为它和几乎所有词相邻）
- 语义相关词对（如 cat-dog）有非零共现计数

**SVD 2D 坐标**（前 2 个奇异值：5.988, 5.754）：

| word | x | y |
|------|------|------|
| cat | -1.6688 | -1.4725 |
| dog | -1.5758 | -1.6164 |
| bank | -1.5435 | -1.3321 |
| river | -1.3852 | -1.4114 |
| money | -0.1139 | 0.1206 |

**散点图**（window=1）：

![Co-occurrence matrix SVD 2D projection window=1](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174805.png)

> [!tip] 读图说明
> - 红色虚线：cat-dog（动物对），距离 d=0.1713
> - 绿色虚线：bank-river（自然对），距离 d=0.1771
> - 橙色虚线：bank-money（金融对），距离 d=2.0382
> - 灰色虚线：cat-money（不相关对），距离 d=2.2262
> - **关键观察**：相关对的距离（0.17）远小于不相关对的距离（2.23）

### 窗口大小的影响

Notes §3.1 指出：大窗口捕捉语义/主题，小窗口捕捉语法。

| window | non-zero | sparsity |
|--------|----------|----------|
| 1 | 56/484 = 11.6% | 88.4% |
| 2 | 92/484 = 19.0% | 81.0% |
| 3 | 113/484 = 23.3% | 76.7% |

**距离对比**：

| pair | window=1 | window=2 |
|------|----------|----------|
| cat-dog | 0.1713 | 1.0407 |
| bank-river | 0.1771 | 0.9898 |
| bank-money | 2.0382 | 2.0619 |
| cat-money (对照) | 2.2262 | 2.2063 |

**散点图**（window=2）：

![Co-occurrence matrix SVD 2D projection window=2](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174808.png)

> [!tip] 窗口 2 读图说明
> - cat-dog 距离从 0.17 增大到 1.04（窗口变大，更多词进入上下文，区分度变化）
> - bank-river 距离从 0.18 增大到 0.99
> - 但相关对仍然比不相关对（cat-money=2.21）更近
> - 这说明**即使窗口改变，语义聚类的基本结构仍然保持**

### 容易误解的地方

> [!warning]
> - 共现矩阵非常稀疏（88%+ 是 0），直接用 raw counts 效果不好
> - 真实场景会用 log-frequency weighting（`log(1 + X_ij)`）或加权方案
> - SVD 坐标的**符号可能翻转**（奇异向量方向不唯一），但**相对距离不变**
> - toy 语料太小，2D 图只是示意；真实词向量需要大语料 + 更高维度
> - 现代方法（word2vec / GloVe）不用 raw co-occurrence + SVD，但这是理解"为什么需要 dense vector"的最佳起点

### 和 glossary 的链接

- [[Lectures/L01-word-vectors/00-concept-glossary#co-occurrence-matrix|co-occurrence-matrix]]
- [[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]]
- [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense-vector]]
- [[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|cosine-similarity]]

### 在 Colab 中打开

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/co-occurrence-matrix.ipynb)

---

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T094147Z__t_4443cc6a__co-occurrence-matrix
  stdout: Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt
  checked_values:
    - claim: "V=22, non-zero 56/484 = 11.6%, sparsity 88.4%"
      source: "stdout line: 'Non-zero: 56/484 = 11.6%' and 'Sparsity: 88.4%'"
      status: copied_from_output
    - claim: "Top-2 singular values: [5.98767047, 5.75406514]"
      source: "stdout line: 'Top-2 singular values: [5.98767047 5.75406514]'"
      status: copied_from_output
    - claim: "cat-dog distance window=1: 0.1713"
      source: "stdout line: 'cat-dog      0.1713      1.0407'"
      status: copied_from_output
    - claim: "bank-river distance window=1: 0.1771"
      source: "stdout line: 'bank-river      0.1771      0.9898'"
      status: copied_from_output
    - claim: "bank-money distance window=1: 2.0382"
      source: "stdout line: 'bank-money      2.0382      2.0619'"
      status: copied_from_output
    - claim: "cat-money distance window=1: 2.2262"
      source: "stdout line: 'cat-money      2.2262      2.2063'"
      status: copied_from_output
    - claim: "window=2: non-zero 92/484 = 19.0%"
      source: "stdout line: 'window=2: non-zero 92/484 = 19.0%'"
      status: copied_from_output
    - claim: "cat 2D coords: (-1.6688, -1.4725)"
      source: "stdout line: 'cat   -1.6688   -1.4725'"
      status: copied_from_output
    - claim: "dog 2D coords: (-1.5758, -1.6164)"
      source: "stdout line: 'dog   -1.5758   -1.6164'"
      status: copied_from_output
```
