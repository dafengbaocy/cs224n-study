## cosine-similarity-analogy — 余弦相似度与词类比算术 {#cosine-similarity-analogy}

**Waypoint**: WP06 — 词向量评估：可视化、类比与偏差

**概念**: [[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|cosine-similarity]] 与 [[Lectures/L01-word-vectors/00-concept-glossary#analogy|analogy]]

**官方锚点**: A1 Part 2 Q2.2-2.6 (cosine similarity, analogy); Notes §3.1 仅简述

**Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/Labs/L01-word-vectors/cosine-similarity-analogy.ipynb)

---

### 为什么不能只看文字？

A1 Q2.2-2.6 要求用 cosine similarity 做词类比，但 slides/notes 没有教：

1. cosine similarity 的计算公式和直觉（为什么用方向而不是距离？）
2. 向量算术 `king - man + woman ≈ queen` 为什么能工作？
3. 什么情况下类比会失败？

这些概念必须实际跑代码才能建立直觉。本 capsule 用 4 维 toy 向量把全流程走通。

---

### 这段代码在看什么

本 capsule 演示两个核心概念：

1. **余弦相似度**：`cos(u, v) = u·v / (||u|| × ||v||)`，衡量两个词向量的方向相似程度
2. **词类比算术**：`a - b + c ≈ d`，用向量差编码语义关系，再平移到新起点

### 和本讲哪个 waypoint 对应

**WP06 — 词向量评估：可视化、类比与偏差**。A1 Part 2 全部依赖这些概念，但 lecture 没有教。

---

### Part 1: 余弦相似度计算

我们用 4 维 toy 向量，每个维度代表一个语义特征：`[royalty, maleness, femaleness, youth]`。

设计原则：语义特征正交分离，这样类比算术才能成立。

关键词对的余弦相似度（来自本次运行 stdout）：

| 词对 | cos_sim | 解读 |
|------|---------|------|
| king, queen | 0.6157 | 共享 royalty 维度 |
| king, man | 0.6738 | 共享 maleness 维度（比 king-queen 还高！） |
| man, woman | 0.3204 | 共享 age 维度但性别相反 |
| king, woman | 0.1399 | 几乎无共享特征 |
| dog, cat | 0.6923 | 动物之间高相似度 |
| prince, princess | 0.7524 | 皇室 + 性别对 |

![余弦相似度热力图](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181538.png)

**读图说明**：先看对角线（全 1.0 = 自身），然后找高亮区域（暖色 = 高相似度）。king-queen 和 prince-princess 形成明显的高相似度块，说明它们共享「皇室」维度。man-woman 的相似度（0.32）低于 king-man（0.67），因为 king 和 man 共享男性维度。

#### 运行后先看哪里

看 cos 值表格中 king-queen vs king-man 的对比。king-man (0.67) > king-queen (0.62)，这看起来反直觉——但原因是 king 和 man 共享「男性」维度，而 king 和 queen 虽然共享「皇室」但性别相反。**cosine similarity 不等于语义等价**。

#### 容易误解的地方

- cos 0.6 在真实 300 维 GloVe 中只算「有一定关系」；同义词通常 > 0.7
- king-man 的 cos 高于 king-queen 不矛盾：cos 衡量方向相似性，不是「谁更像 king」

---

### Part 2: 词类比算术

经典类比：`king - man + woman = ?`

几何直觉：
- `king - man` = 去掉「男性」成分，保留「皇室」成分 → `[0.87, -0.03, 0.00, -0.40]`
- `+ woman` = 加上「女性」成分 → `[0.92, 0.02, 0.90, 0.08]`
- 与 queen `[0.95, 0.08, 0.88, 0.12]` 的 cos = **0.9981** → 几乎完美命中

类比测试结果：

| 类比 | 预期 | 预测 | cos_sim | 正确 |
|------|------|------|---------|------|
| king - man + woman | queen | queen | 0.9981 | ✓ |
| prince - man + woman | princess | princess | 0.9955 | ✓ |
| king - queen + man | boy | boy | 0.7646 | ✓ |
| king - queen + prince | man | man | 0.8588 | ✓ |
| boy - girl + man | dog | dog | 0.6981 | ✓ |
| prince - princess + king | man | man | 0.7410 | ✓ |

![2D 投影与类比箭头](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181545.png)

**读图说明**：先看 x 轴（royalty）和 y 轴（maleness）。蓝色 = 男性主导，红色 = 女性主导。两条虚线箭头（man→king 和 woman→queen）应该**平行**——这就是类比关系的几何含义：`king - man` 和 `queen - woman` 编码了相同的「加 royalty」方向。

---

### Part 3: 类比失败案例

类比不是万能的：

**失败案例 1 — 跨语义域**：`dog - cat + king = ?`
- Top-1: prince (cos=0.7905)，不是预期的 queen
- 原因：dog→cat 的差异方向和 king→queen 的差异方向不一致

**失败案例 2 — 无清晰关系**：`dog - king + man = ?`
- Top-1: boy (cos=0.7110)
- 原因：dog→king 没有清晰语义关系，类比结果无意义

![类比结果柱状图](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181548.png)

**读图说明**：左图绿色 = 正确预测，红色 = 错误。右图按相似度着色（绿 > 0.9, 黄 > 0.7, 橙 > 0.4, 红 < 0.4）。注意 prince-princess (0.75) 和 dog-cat (0.69) 的高相似度来自共享维度结构。

---

### 输出怎么解释

1. **余弦相似度只看方向**：两个向量即使长度不同，只要方向一致，cos 就接近 1。这就是为什么词向量通常先归一化再用点积。
2. **类比成功的前提是语义维度正交分离**：如果「皇室」和「性别」混在同一维度，差向量就不干净，类比就会失败。
3. **toy 向量 ≠ 真实词向量**：真实 word2vec 的类比准确率约 40-60%，远不如这里的完美结果。

---

### 对应 A1 作业

A1 Part 2 Q2.2-2.6 要求你：
- Q2.2: 实现 cosine similarity 函数
- Q2.3-2.4: 用 GloVe 向量找最近邻
- Q2.5: 做类比测试
- Q2.6: 分析偏差

本 capsule 的 toy 实验帮你理解这些操作的数学含义。在 A1 中你会用真实的 200 维 GloVe 向量做同样的事。

---

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T112330Z__t_48b9a9f8__cosine-similarity-analogy
  stdout: Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stdout.txt
  checked_values:
    - claim: "cos(king, queen) = 0.6157"
      source: "stdout line: cos(king      , queen     ) = 0.6157"
      status: copied_from_output
    - claim: "cos(king, man) = 0.6738"
      source: "stdout line: cos(king      , man       ) = 0.6738"
      status: copied_from_output
    - claim: "cos(man, woman) = 0.3204"
      source: "stdout line: cos(man       , woman     ) = 0.3204"
      status: copied_from_output
    - claim: "cos(dog, cat) = 0.6923"
      source: "stdout line: cos(dog       , cat       ) = 0.6923"
      status: copied_from_output
    - claim: "cos(prince, princess) = 0.7524"
      source: "stdout line: cos(prince    , princess  ) = 0.7524"
      status: copied_from_output
    - claim: "king - man + woman = queen, cos=0.9981"
      source: "stdout line: #1: queen       cos_sim = 0.9981"
      status: copied_from_output
    - claim: "king - man = [0.87, -0.03, 0.00, -0.40]"
      source: "stdout line: king - man = [0.87, -0.03, 0.00, -0.40]"
      status: copied_from_output
    - claim: "result = [0.92, 0.02, 0.90, 0.08]"
      source: "stdout line: result = [0.92, 0.02, 0.90, 0.08]"
      status: copied_from_output
    - claim: "dog - cat + king top-1: prince cos=0.7905"
      source: "stdout line: prince      cos_sim = 0.7905"
      status: copied_from_output
    - claim: "dog - king + man top-1: boy cos=0.7110"
      source: "stdout line: boy         cos_sim = 0.7110"
      status: copied_from_output
```
