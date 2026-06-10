## co-occurrence-matrix — 从语料构建共现矩阵并做 SVD 降维 {#co-occurrence-matrix}

> [!info] 这个 Capsule 在看什么
> **概念**：[[Lectures/L01-word-vectors/00-concept-glossary#co-occurrence-matrix|共现矩阵]] 统计每个词在窗口内和哪些词一起出现过；[[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]] 把高维共现矩阵降维到低维词向量空间。
>
> **为什么不能只靠文字**：Notes §3.1 描述了共现矩阵的构建过程，但只有实际构建一个小矩阵并做 SVD，才能理解窗口大小和降维的效果——为什么 cat 和 dog 的向量接近，而 cat 和 book 的向量正交。
>
> **官方锚点**：Notes §3.1 (co-occurrence matrices); A1 Part 1 Q1.1-1.3

### 运行方式

**Colab 打开**（推荐）：

> ⚠️ **Colab 链接暂不可用**：GitHub push 因多 worker 并发冲突失败。本地 `.ipynb` 已生成，可手动上传或等待冲突解决后重试。
> 本地路径：`Labs/L01-word-vectors/co-occurrence-matrix.ipynb`

**本地运行**：
```bash
cd /workspace/cs224n-study
.venv/bin/python Labs/L01-word-vectors/co-occurrence-matrix.py
```

### 这段代码在做什么

1. 定义 15 个小句子，分三个主题（动物：cat/dog/play/chase；科技：book/tech/read/code；自然：fish/water/swim/ocean）
2. 构建词汇表（V=30 个词）
3. 用 window=1 构建 [[Lectures/L01-word-vectors/00-concept-glossary#co-occurrence-matrix|共现矩阵]] M（30×30）
4. 对 M 做 [[Lectures/L01-word-vectors/00-concept-glossary#svd|SVD]]，取前 2 个奇异向量降维到 2D
5. 计算降维后词对的 [[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|余弦相似度]]
6. 对比 window=1/2/3 对共现矩阵的影响

### 运行后先看哪里

> [!tip] 输出解读
> 1. **共现矩阵**：M[cat,dog]=4（动物词高频共现），M[book,tech]=3（科技词高频共现），M[cat,book]=0（不同主题不共现）
> 2. **SVD 奇异值**：前 2 奇异值占总能量 41.7%——2D 能捕获主要结构但丢弃不少信息
> 3. **降维后向量**：动物词在 x 轴负方向，科技词在 y 轴负方向——SVD 自动发现了两个主题维度
> 4. **余弦相似度**：cat-dog=1.0000（同类），book-tech=1.0000（同主题），cat-book=-0.0000（不同主题正交）

### 关键输出

**共现计数 (window=1)**：

```
M[cat, dog] = 4     (动物词高频共现)
M[book, tech] = 3   (科技词高频共现)
M[fish, swim] = 2   (自然搭配)
M[cat, book] = 0    (不同主题，零共现)
M[fish, book] = 0   (不同主题，零共现)
```

**SVD 降维后余弦相似度**：

| 词对 | cos_sim | 关系 |
|------|---------|------|
| cat-dog | 1.0000 | 同类动物（共享上下文 play/chase） |
| book-tech | 1.0000 | 同主题（共享上下文 read/code） |
| fish-water | 1.0000 | 强搭配（总一起出现） |
| cat-book | -0.0000 | 不同主题（动物 vs 科技） |
| dog-tech | 0.0000 | 不同主题（动物 vs 科技） |
| fish-cat | 1.0000 | 部分共享上下文（cat watches fish） |
| fish-book | -0.0000 | 几乎无共享上下文 |

**窗口大小对比**：

| window | 总计数 | 非零元素 | M[cat,dog] | M[cat,fish] | M[book,tech] |
|--------|--------|----------|------------|-------------|--------------|
| 1 | 90 | 74/900 | 4 | 0 | 3 |
| 2 | 150 | 110/900 | 5 | 1 | 5 |
| 3 | 180 | 136/900 | 5 | 1 | 5 |

### 共现矩阵热力图

![Co-occurrence Matrix Heatmap](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-182108.png)

> [!tip] 读图指南
> - 红色越深表示共现次数越多
> - 可以看到明显的**块状结构**：左上动物词块、中间科技词块、右下自然词块
> - 块与块之间几乎为 0——不同主题的词不共现

### SVD 2D 词向量可视化

![SVD 2D Embeddings](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-182111.png)

> [!tip] 读图指南
> - **红圆（Animal）**：cat, dog, play, chase 等聚集在 x 轴负方向
> - **蓝方（Tech）**：book, tech, read, code 等聚集在 y 轴负方向
> - **绿三角（Water/Nature）**：fish, water, swim 等散布
> - SVD 自动发现了两个正交的主题维度——这就是降维的威力

### 余弦相似度对比

![Cosine Similarity](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-182114.png)

> [!tip] 读图指南
> - 绿色柱（>0.8）：同主题词对，余弦接近 1.0
> - 红色柱（≈0）：不同主题词对，余弦接近 0（向量正交）
> - 注意 cat-book = -0.0000：不是「有点不相似」，而是完全不相关

### 窗口大小影响

![Window Comparison](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-182117.png)

> [!tip] 读图指南
> - window=1：只有直接相邻的词才算共现，矩阵稀疏（74/900 非零）
> - window=2：间隔一个词也算共现，非零元素增加到 110/900
> - window=3：更多词对被认为共现，136/900 非零
> - 对应 Notes §3.1：短窗口捕获语法关系，长窗口捕获语义关系

### 和课堂内容的对应

| 课堂材料 | 对应内容 |
|----------|----------|
| Slides p21 | Firth 名言 "You shall know a word by the company it keeps" |
| Slides p22-23 | Context window 和 dense vectors 的概念 |
| Notes §3.1 | Co-occurrence matrix 构建、window size effects、log frequency weighting |
| A1 Part 1 Q1.1-1.3 | 实现 co-occurrence matrix + SVD（本 capsule 的简化版） |

### 容易误解的地方

> [!warning] 注意
> 1. **cosine = 1.0 不代表真实情况**：toy 语料主题分离太完美。真实语料中 cat-dog 的 cosine 约 0.7-0.8。
> 2. **2D 降维太激进**：前 2 奇异值只解释 41.7% 能量。实际中用 50-300 维。
> 3. **fish 被归入动物 cluster**：因为 fish 和 cat/dog 有少量共现。更高维空间中 fish 会有自己的维度。
> 4. **SVD vs Word2Vec**：SVD 是计数方法（先统计共现再降维）；Word2Vec 是预测方法（直接训练神经网络）。两者思路不同但都能得到有意义的词向量。
> 5. **共现矩阵的稀疏性**：30×30 矩阵只有 8.2% 非零。真实语料更稀疏，这就是为什么需要降维。

### 数字来源证明

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T182000Z__t_6ff7c879__co-occurrence-matrix
  stdout: Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt
  checked_values:
    - claim: "M[cat, dog] = 4"
      source: "stdout: 'M[cat, dog] = 4'"
      status: copied_from_output
    - claim: "M[book, tech] = 3"
      source: "stdout: 'M[book, tech] = 3'"
      status: copied_from_output
    - claim: "M[cat, book] = 0"
      source: "stdout: 'M[cat, book] = 0'"
      status: copied_from_output
    - claim: "前 2 奇异值占总能量 41.7%"
      source: "stdout: '前 2 奇异值占总能量: 41.7%'"
      status: copied_from_output
    - claim: "cat-dog cos_sim = 1.0000"
      source: "stdout: 'cat-dog       1.0000  同类动物'"
      status: copied_from_output
    - claim: "cat-book cos_sim = -0.0000"
      source: "stdout: 'cat-book     -0.0000  不同主题'"
      status: copied_from_output
    - claim: "window=1 总计数=90, 非零=74/900"
      source: "stdout: 'window=1: 总计数=90, 非零元素=74/900'"
      status: copied_from_output
    - claim: "window=2 总计数=150, 非零=110/900"
      source: "stdout: 'window=2: 总计数=150, 非零元素=110/900'"
      status: copied_from_output
```
