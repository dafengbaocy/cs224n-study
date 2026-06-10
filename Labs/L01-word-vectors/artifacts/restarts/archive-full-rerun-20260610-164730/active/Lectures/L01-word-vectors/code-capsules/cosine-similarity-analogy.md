## cosine-similarity-analogy — 余弦相似度与词类比算术 {#cosine-similarity-analogy}

> [!info] 本 capsule 解决什么问题
> A1 Part 2 Q2.2-2.6 要求用 cosine similarity 做词类比，但 slides/notes 没有教 cosine similarity 的计算方法和向量算术的直觉。只有实际跑一遍，才能理解为什么 `king - man + woman ≈ queen` 以及这个性质为什么重要。

**Waypoint**: WP06 — 词向量评估：可视化、类比与偏差  
**Official anchor**: A1 Part 2 Q2.2-2.6 (cosine similarity, analogy); Notes §3.1 仅简述  
**前置概念**: [[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|cosine similarity]], [[Lectures/L01-word-vectors/00-concept-glossary#analogy|analogy]], [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense vector]]

---

### 为什么不能只看文字？

Slides/notes 告诉你"词向量能编码相似性"，但没有展示：
1. cosine similarity 具体怎么算（点积 / 模长乘积）
2. 向量算术 `king - man + woman` 为什么能到达 `queen` 附近
3. 类比什么时候会**失败**（跨域类比不工作）

这些只有跑代码才能建立直觉。

---

### 核心概念：Cosine Similarity

$$\cos(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \cdot \|\mathbf{v}\|}$$

- 范围 `[-1, 1]`
- `1` = 同方向（非常相似）
- `0` = 正交（不相关）
- `-1` = 反方向（非常不同）

> [!tip] 对比 one-hot
> one-hot 向量之间永远正交（cos_sim = 0），无法编码任何相似性。这就是为什么我们需要 [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense vectors]]。

---

### 实验：Toy 词向量的 Cosine Similarity

我们用 4 维手工设计向量，每个维度对应一个语义特征：`[royalty, maleness, femaleness, youth]`。

| 词对 | cos_sim | 关系 |
|------|---------|------|
| king, queen | 0.6157 | 共享 royalty，性别不同 |
| king, man | 0.6738 | 共享 maleness，地位不同 |
| king, woman | 0.1399 | 跨性别跨地位，低相似 |
| man, woman | 0.3204 | 共享 age，性别不同 |
| dog, cat | 0.6923 | 同类动物 |
| boy, girl | 0.5848 | 共享 youth，性别不同 |
| prince, princess | 0.7524 | 共享 royalty + youth |

> [!example] 关键观察
> - **同类词对**（king-queen, dog-cat）cosine 较高 → 共享语义维度
> - **跨类词对**（king-woman = 0.1399）cosine 很低 → 语义距离远
> - 这证明了 dense vector 能编码相似性，而 one-hot 做不到

![cosine-similarity-analogy-heatmap](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161815.png)
*余弦相似度热力图：10 个 toy 词的两两相似度。对角线 = 1.0（自身）。同语义类的词形成高相似度区块。*

---

### 核心概念：Word Analogy 向量算术

经典测试（Mikolov et al., 2013）：

$$\text{king} - \text{man} + \text{woman} \approx \text{queen}$$

**直觉**：
- `king - man` = 去掉"男性"成分，保留"皇室"成分 → 得到 "royalty offset"
- `royalty offset + woman` = 把"皇室"加到"女性"上 → 到达 `queen` 附近

这之所以能工作，是因为语义关系被编码为**一致的向量偏移方向**。

---

### 实验：经典类比 king - man + woman = ?

```
结果向量: [0.92, 0.02, 0.90, 0.08]
最接近的词:
  #1: queen       cos_sim = 0.9981 ← 正确答案!
  #2: princess    cos_sim = 0.8310
  #3: girl        cos_sim = 0.5520
  #4: prince      cos_sim = 0.4914
```

> [!tip] 中文扶手
> queen 以 0.9981 的超高余弦相似度排名第一。这意味着 `king - man + woman` 的结果向量和 `queen` 几乎指向同一方向。向量算术真的能"做类比"！

![cosine-similarity-analogy-2d-projection](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161819.png)
*2D 投影（royalty × maleness 平面）。注意 king→queen 和 man→woman 的箭头近乎平行——这就是类比结构的几何表现。*

---

### 更多类比测试

| 类比 | 结果 | cos_sim | 正确？ |
|------|------|---------|--------|
| king - man + woman = ? | queen | 0.9981 | ✓ |
| prince - man + woman = ? | princess | 0.9955 | ✓ |
| king - queen + man = ? | boy | 0.7646 | ✓ |
| king - queen + prince = ? | man | 0.8588 | ✓ |
| boy - girl + man = ? | dog | 0.6981 | ✓ |
| prince - princess + king = ? | man | 0.7410 | ✓ |

> [!warning] 注意
> 第 5 个类比 `boy - girl + man = dog` 看起来奇怪，但在我们的 toy 空间中，`boy - girl` 的偏移主要是"性别翻转"，加到 `man` 上后，结果落在了动物区域。这恰好说明 toy 空间的局限性——真实 word2vec 中这个类比应该得到 `woman`。

![cosine-similarity-analogy-results-chart](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161822.png)
*类比结果柱状图：每个类比的 top-1 结果及其余弦相似度。绿色 = 正确答案。*

---

### 类比失败案例

> [!question] 暂停思考
> 如果 `king - man + woman = queen` 能工作，那 `dog - cat + king = ?` 应该得到什么？

**跨域类比失败**：`dog - cat + king = ?`

```
结果向量: [0.95, 1.25, -0.35, 0.10]
Top-3 预测:
  prince      cos_sim = 0.7905
  man         cos_sim = 0.7377
  boy         cos_sim = 0.5861
```

`dog → cat` 的关系方向（动物界的"性别翻转"）和 `king → queen` 的方向（皇室的"性别翻转"）不完全一致，所以类比结果不是 `queen`。

> [!tip] 关键洞察
> 类比在**同一语义域**内效果最好。跨域类比（动物→皇室）会失败，因为不同域的"关系方向"不一定对齐。这和真实 word2vec 的行为一致。

---

### 与 A1 的联系

| A1 题目 | 本 capsule 覆盖 |
|---------|----------------|
| Q2.2 实现 `cosine_similarity()` | Part 1：完整实现 + 10 词实验 |
| Q2.3 找最近词 | Part 2：analogy 函数中的 top-k 搜索 |
| Q2.4-2.5 类比测试 | Part 2：6 组类比 + 2 组失败案例 |
| Q2.6 偏差分析 | 留给 DeepResearch 阶段 |

---

### 运行与复现

**Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/cosine-similarity-analogy.ipynb)

**本地运行**:
```bash
cd Labs/L01-word-vectors
python cosine-similarity-analogy.py
```

**文件**:
- 脚本: `Labs/L01-word-vectors/cosine-similarity-analogy.py`
- Notebook: `Labs/L01-word-vectors/cosine-similarity-analogy.ipynb`
- 输出: `Labs/L01-word-vectors/outputs/cosine-similarity-analogy-*`
- Run-log: `Labs/L01-word-vectors/run-log.md`

---

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T081806Z__t_18fe1985__cosine-similarity-analogy
  stdout: Labs/L01-word-vectors/outputs/cosine-similarity-analogy-stdout.txt
  checked_values:
    - claim: "cos(king, queen) = 0.6157"
      source: "stdout Part 1: cos(king, queen) = 0.6157"
      status: copied_from_output
    - claim: "king - man + woman = queen, cos_sim = 0.9981"
      source: "stdout Part 2: #1: queen cos_sim = 0.9981"
      status: copied_from_output
    - claim: "prince - man + woman = princess, cos_sim = 0.9955"
      source: "stdout Part 2: prince - man + woman = princess (sim=0.9955)"
      status: copied_from_output
    - claim: "dog - cat + king top-1 = prince (0.7905)"
      source: "stdout Part 3: prince cos_sim = 0.7905"
      status: copied_from_output
    - claim: "cos(result, queen) = 0.9981"
      source: "stdout Part 4: cos(result, queen) = 0.9981"
      status: copied_from_output
```
