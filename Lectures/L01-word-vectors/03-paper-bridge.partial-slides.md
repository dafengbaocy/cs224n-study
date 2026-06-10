# Paper Bridge (partial-slides) — L01 Word Vectors

> 本文件由 Paper Tutor (slides/notes) 阶段生成。
> 映射教学图 → waypoint，供 Lecture Weaver 合并时引用。
> wikilink 使用 vault-root 路径。
> 教学图详情见 `Lectures/L01-word-vectors/02b-slides-notes-teaching-figures.md`。

---

## WP01 — Course Intro & NLP Landscape

| 教学图 | 来源 | 内容摘要 |
|---|---|---|
| WP01-1 | Slides p2 | 5 个讲授模块时间分配，核心学习目标 |
| WP01-2 | Slides p9 | 完整计划含 "Looking at word vectors" 环节 → WP05 预告 |
| WP01-3 | Slides p11 | NLP 应用：机器翻译示例（文字带读，图片上传 pending） |
| WP01-4 | Slides p12 | NLP 应用：问答系统示例（文字带读，图片上传 pending） |
| WP01-5 | Slides p14 | NLP 应用：DALL-E 文本到图像（文字带读，图片上传 pending） |

**Slides/Notes 覆盖度**：✅ 充分。Slides p1-p15 完整覆盖课程介绍和 NLP 应用展示。Notes §1 (p1-p3) 提供 NLP 定义和应用分类。WP01 不需要额外可视化补充。

---

## WP02 — One-hot vs Dense Vectors

| 教学图 | 来源 | 内容摘要 |
|---|---|---|
| WP02-1 | Slides p16 | signifier ⟺ signified，denotational semantics |
| WP02-2 | Slides p17 | WordNet 同义词集和上位词链 NLTK 代码示例 |
| WP02-3 | Slides p19 | one-hot 向量定义，维度 = 词汇量 |
| WP02-4 | Slides p20 | one-hot 正交 → 无自然相似度概念 |
| WP02-5 | Notes p4 Eq.1-2 | v_tea^T v_coffee = 0 的数学证明 |
| WP02-6 | Slides p21 | Firth 名言 + 分布语义学定义 |
| WP02-7 | Notes p6 | 分布假说 + tea 上下文示例 |
| WP02-8 | Notes p7 | 窗口大小 vs 语法/语义编码 |
| WP02-9 | Slides p22 | dense vector 定义 + banking/monetary 示例 |
| WP02-10 | Slides p23 | banking 的 8 维向量可视化 |

**Slides/Notes 覆盖度**：✅ 充分。从 one-hot 的问题 → 分布假说 → dense vectors 的完整逻辑链在 slides p16-p23 和 notes §2-§3.1 中有清晰展示。Code capsule `one-hot-vs-dense` 和 `cooccurrence-svd-mini` 补充数值实验。

---

## WP03 — Word2Vec / Skip-gram / Softmax

| 教学图 | 来源 | 内容摘要 |
|---|---|---|
| WP03-1 | Slides p24 | Word2Vec 框架 5 步流程 + Skip-gram 标注 |
| WP03-2 | Slides p25 | banking 为中心词，窗口 2，4 个 context |
| WP03-3 | Slides p28 | v_w/u_w 两套向量 + softmax 公式 |
| WP03-4 | Slides p29 | "into" 为中心词的概率计算示例 |
| WP03-5 | Slides p30 | softmax 三步分解：点积→指数→归一化 |
| WP03-6 | Notes p8 Eq.4-5 | 概率模型 Eq.4 + 交叉熵目标 Eq.5 |

**Slides/Notes 覆盖度**：✅ 充分。Slides p24-p30 和 notes §3.2 完整覆盖 skip-gram 模型。Code capsule `softmax-probability` 和 `skip-gram-shapes` 补充数值计算和形状理解。

---

## WP04 — Objective / Gradients / Negative Sampling

| 教学图 | 来源 | 内容摘要 |
|---|---|---|
| WP04-1 | Slides p27 | 数据似然 L(θ) + 负对数似然 J(θ) |
| WP04-2 | Slides p31 | 参数向量 θ + 梯度下降直觉图 |
| WP04-3 | Slides p33 | GD 核心思想 + 非凸注释 |
| WP04-4 | Slides p34 | 矩阵/单参数更新公式 + 学习率 α |
| WP04-5 | Slides p35 | 全梯度昂贵 → SGD 采样窗口更新 |
| WP04-6 | Notes p9 Eq.6-7 | 三层求和经验损失 + 梯度更新 |
| WP04-7 | Notes p11-12 | 梯度 = u_o - E[u_w] = observed - expected |
| WP04-8 | Notes p12 Eq.14-15 | softmax 分区函数 + SGNS logistic 目标 |

**Slides/Notes 覆盖度**：⚠️ 部分充分。Slides p27-p35 和 notes §3.3-§3.4 覆盖目标函数、梯度推导和 GD/SGD。负采样 (Eq.14-15) 有公式但 p_neg 未定义——notes 明确写 "a distribution we haven't defined"。DeepResearch 需要补充实际噪声分布和 NCE 关系。Code capsule `negative-sampling-demo` 补充数值对比。

---

## WP05 — Pretrained Vectors / Analogy / Visualization

**Slides/Notes 覆盖度**：❌ 不足。

Slides p9 列出 "Looking at word vectors (10 mins or less)" 但 slides 正文 (p1-p36) 没有对应的可视化/类比内容页。Notes 附录 A.1 CBOW / A.2 SVD 只有标题无正文。

**需要的补充来源**：
- A1 Part 2（GloVe 向量加载、cosine similarity、analogy 问题、bias 探索）
- R02 原论文（compositionality / phrase vectors / analogy examples）
- DeepResearch 产物（PCA/t-SNE 可视化解释、失败案例、bias 分析）

此 waypoint 的教学图需要等 Code Capsules (`pretrained-analogy`) 和 DeepResearch 完成后由 Lecture Weaver 整合。
