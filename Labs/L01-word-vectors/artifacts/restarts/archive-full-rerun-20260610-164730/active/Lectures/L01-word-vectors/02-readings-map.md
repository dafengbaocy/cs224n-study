# L01-word-vectors Readings Map

> **阶段产物**：Reading Triage
> **日期**：2026-06-10
> **状态**：review-passed（reviewer: `t_bfe987ff`）
> **本文件角色**：下游所有阶段（Paper Tutor / Code Capsules / DeepResearch / Lecture Weaver）的唯一配置来源。

---

## 1. 官方 Anchors 概览

| 源 | 本地路径 | 关键内容 |
|---|---|---|
| Schedule row | `recovered/evidence/l01/l01-schedule-row.txt` | Week 1 Tue Jan 7, Word Vectors, Suggested Readings: R01 + R02, A1 out |
| Slides (43 pages) | `recovered/assets/official/l01/cs224n-2025-lecture01-wordvecs1.pdf` / `recovered/evidence/l01/slides-extracted-text.txt` | 5 段：course(10min), human language(15min), word2vec intro(15min), gradients(25min), optimization(5min), looking at word vectors(≤10min) |
| Notes (13 pages + refs) | `recovered/assets/official/l01/cs224n-2025-lecture01-notes.pdf` / `recovered/evidence/l01/notes-extracted-text.txt` | §1 Intro, §2 Representing words, §3 Distributional semantics & Word2vec (3.1-3.5), Appendix A (CBOW/SVD placeholder) |
| Assignment A1 | `recovered/assets/official/l01/a1.zip` / `recovered/evidence/l01/a1-notebook-extracted-text.txt` | Part 1: Co-occurrence (Q1.1-1.5), Part 2: GloVe exploration (Q2.1-2.9) |
| R01 PDF | `recovered/assets/papers/l01/L01-R01-mikolov-efficient-estimation-1301.3781.pdf` | word2vec 原始论文 |
| R02 PDF | `recovered/assets/papers/l01/L01-R02-mikolov-distributed-representations-neurips2013.pdf` | negative sampling 论文 |

---

## 2. Reading Roles 表

| ID | 标题 | Role | 判定证据 |
|---|---|---|---|
| L01-R01 | Efficient Estimation of Word Representations in Vector Space (Mikolov et al. 2013) | **core** | Schedule row 明确列为 "Suggested Readings: original word2vec paper"；Slides p24 cite "Mikolov et al. 2013" for Word2vec/Skip-gram；Notes references lines 813-814 cite CoRR abs/1301.3781 |
| L01-R02 | Distributed Representations of Words and Phrases and their Compositionality (Mikolov et al. 2013) | **core** | Schedule row 明确列为 "negative sampling paper"；Notes §3.5 Skipgram-negative-sampling 解释 SGNS objective 作为 softmax partition function 的效率替代 |
| L01-R03 | GloVe: Global Vectors for Word Representation (Pennington et al. 2014) | **support** | Notes §3.1 line 364-366 cite GloVe as co-occurrence-based algorithm working as well as word2vec；A1 notebook Part 2 (cell 28, line 407) links Stanford GloVe PDF and loads glove-wiki-gigaword-200 |
| L01-R04 | word2vec Parameter Learning Explained (Rong 2014) | **support** | Notes references lines 817-818 cite CoRR abs/1411.2738；补充 word2vec 梯度推导细节 |
| L01-R05 | Applications of General Linguistics (Firth 1957) | **support** | Notes §3 line 293-294 引用 Firth 的 distributional hypothesis 名言 "You shall know a word by the company it keeps"；Slides p21 同样引用 |
| L01-R06 | WordNet: A Lexical Database for English (Miller 1995) | **optional** | Notes §2.3 line 241 cite WordNet as annotated semantic relation resource；Slides p17-18 展示 WordNet 作为旧方法 |
| L01-R07 | UniMorph 4.0: Universal Morphology (Batsuren et al. 2022) | **optional** | Notes §2.3 line 242-243 cite UniMorph as morphology annotation resource |
| L01-R08 | Human Language Understanding & Reasoning (Manning 2022) | **optional** | Notes §1.1 line 27 cite for language and intelligence motivation |
| L01-R09 | A Neural Probabilistic Language Model (Bengio et al. 2003) | **optional** | Notes references lines 804-805；historical neural language model background |
| L01-R10 | Natural Language Processing (Almost) from Scratch (Collobert et al. 2011) | **optional** | Notes references lines 806-808；historical neural NLP background |
| L01-R11 | Statistical Inference for Probabilistic Functions of Finite State Markov Chains (Baum & Petrie 1966) | **optional** | Notes references lines 801-803；no direct L01 waypoint anchor |
| L01-R12 | Learning representations by back-propagating errors (Rumelhart et al. 1986) | **optional** | Notes references lines 819-820；optimization/backpropagation historical background |

---

## 3. Waypoints 表

| WP | 标题 | 一句话概念 | 官方 Anchors | Assignment 关联 |
|---|---|---|---|---|
| WP01 | 为什么需要词向量？ | 从离散符号（one-hot）到密集向量的动机：one-hot 无法编码语义相似性 | Slides p16-20（meaning, WordNet, one-hot problems）；Notes §2.1-2.3（signifier/signified, one-hot, annotated properties） | A1 Part 1 隐含使用 one-hot → co-occurrence 的对比 |
| WP02 | 分布语义学 | "You shall know a word by the company it keeps"——用上下文定义词义 | Slides p21-23（Firth quote, context window, dense vectors）；Notes §3 intro + §3.1（distributional hypothesis, co-occurrence matrices, window size effects） | A1 Part 1 Q1.1-1.5 实现 co-occurrence matrix + SVD |
| WP03 | Word2vec Skip-gram 模型 | 用中心词预测上下文词：每词两向量，softmax 输出概率 | Slides p24-30（skip-gram overview, windows, objective, two vectors per word, softmax）；Notes §3.2（probabilistic model, Eq.4 softmax, Eq.5 cross-entropy loss） | A1 Part 2 引导"revisit class notes/slides for word2vec" |
| WP04 | 梯度与优化 | "Observed minus expected"梯度直觉 + SGD 随机优化 | Slides p31-35（training, gradient descent, SGD）；Notes §3.3（empirical loss Eq.6, gradient step Eq.7, stochastic gradients Eq.8）+ §3.4（full gradient derivation Eq.9-13, "observed minus expected"） | A1 不直接考梯度推导，但理解优化是后续课程基础 |
| WP05 | 负采样 (Skip-gram Negative Sampling) | 用 logistic 二分类替代 softmax 全词表归一化，解决计算效率瓶颈 | Notes §3.5（partition function bottleneck, Eq.14 softmax, Eq.15 SGNS objective, logistic approximation）；Slides p27-30 作为 softmax 前置 | A1 Part 2 引导"revisit class notes/slides"；R02 论文有更多细节 |
| WP06 | 词向量评估：可视化、类比与偏差 | 用 cosine similarity 量化词相似性，向量算术做类比，发现嵌入偏差 | A1 Part 1 Q1.5 + Part 2 Q2.1-2.9（cosine similarity, analogy arithmetic, bias analysis）；Notes §3.1（co-occurrence + SVD 简述）；Notes Appendix A.2（SVD placeholder, 无内容） | A1 全部 Part 1 + Part 2 直接对应此 waypoint |

---

## 4. 配置字段

### A. core_readings

```yaml
core_readings:
  - slug: L01-R01
    title: "Efficient Estimation of Word Representations in Vector Space"
    role: core
    canonical_url: "https://arxiv.org/abs/1301.3781"
    paper_url: "https://arxiv.org/pdf/1301.3781.pdf"
    local_pdf: "recovered/assets/papers/l01/L01-R01-mikolov-efficient-estimation-1301.3781.pdf"
    official_anchor: "Schedule row: Suggested Readings (original word2vec paper); Slides p24 cite Mikolov et al. 2013; Notes references lines 813-814"
    waypoint_focus: [WP03, WP04]
    paper_tutor_focus: "Skip-gram 模型架构、CBOW 对比、训练效率技巧（hierarchical softmax / subsampling）"
  - slug: L01-R02
    title: "Distributed Representations of Words and Phrases and their Compositionality"
    role: core
    canonical_url: "https://papers.nips.cc/paper_files/paper/2013/hash/9aa42b31882ec039965f3c4923ce901b-Abstract.html"
    paper_url: "https://papers.nips.cc/paper_files/paper/2013/file/9aa42b31882ec039965f3c4923ce901b-Paper.pdf"
    local_pdf: "recovered/assets/papers/l01/L01-R02-mikolov-distributed-representations-neurips2013.pdf"
    official_anchor: "Schedule row: Suggested Readings (negative sampling paper); Notes §3.5 SGNS objective"
    waypoint_focus: [WP05, WP06]
    paper_tutor_focus: "负采样目标函数推导、负采样分布选择（unigram^0.75）、短语学习、组合性实验"
```

### B. code_capsules

```yaml
code_capsules:
  - slug: one-hot-vs-dense
    waypoint: WP01
    concept: "One-hot 向量 vs 密集词向量的对比"
    why_not_text: "Slides p19-22 展示了 one-hot 和 dense vector 的概念，但只有看实际向量维度和点积计算才能理解为什么 one-hot 无法编码相似性"
    official_anchor: "Slides p19-22; Notes §2.2 (one-hot vectors, Eq.1-2)"
    expected_output: ["one-hot 向量构建及点积=0 的演示", "dense embedding 可视化对比"]
  - slug: co-occurrence-matrix
    waypoint: WP02
    concept: "从语料构建共现矩阵并做 SVD 降维"
    why_not_text: "Notes §3.1 描述了 co-occurrence matrix 的构建过程，但只有实际构建一个小矩阵并做 SVD 才能理解窗口大小和降维的效果"
    official_anchor: "Notes §3.1 (co-occurrence matrices); A1 Part 1 Q1.1-1.3"
    expected_output: ["小语料共现矩阵", "SVD 降维后的 2D 词向量", "scatter plot 可视化"]
  - slug: skipgram-softmax
    waypoint: WP03
    concept: "Skip-gram softmax 概率计算 P(o|c)"
    why_not_text: "Slides p28-30 和 Notes §3.2 给出了 softmax 公式，但只有实际计算一个 mini vocabulary 的 P(o|c) 才能理解分母归一化的计算量"
    official_anchor: "Slides p27-30 (objective function, softmax); Notes §3.2 (Eq.4-5)"
    expected_output: ["mini vocabulary 的 P(o|c) 计算", "softmax 分母遍历全词表的代价演示"]
  - slug: negative-sampling-loss
    waypoint: WP05
    concept: "负采样目标函数 vs 全 softmax"
    why_not_text: "Notes §3.5 给出了 SGNS 公式但没解释为什么 logistic 近似有效；需要实际对比两种 loss 的计算和梯度行为"
    official_anchor: "Notes §3.5 (Eq.14-15, SGNS objective); R02 paper Section 3"
    expected_output: ["softmax loss vs negative sampling loss 对比", "不同负采样数 k 的效果"]
  - slug: cosine-similarity-analogy
    waypoint: WP06
    concept: "余弦相似度与词类比算术"
    why_not_text: "A1 Q2.2-2.6 要求用 cosine similarity 做类比，但 slides/notes 没有教 cosine similarity 的计算和向量算术的直觉；需要实际跑才能理解"
    official_anchor: "A1 Part 2 Q2.2-2.6 (cosine similarity, analogy); Notes §3.1 仅简述"
    expected_output: ["cosine similarity 计算示例", "king-man+woman=queen 类比演示", "类比失败案例"]
```

### C. deepresearch_waypoints

```yaml
deepresearch_waypoints:
  - waypoint: WP01
    title: "为什么需要词向量？"
    needs_deepresearch: false
    official_anchor: "Slides p16-20; Notes §2.1-2.3"
    research_question: ""
    reason: "Slides p16-20 完整覆盖了 signifier/signified → WordNet → one-hot → one-hot 问题的递进逻辑；Notes §2.1-2.3 补充了 type/token 区分和 annotated properties 的细节。概念链条完整，无跳跃。"
  - waypoint: WP02
    title: "分布语义学"
    needs_deepresearch: false
    official_anchor: "Slides p21-23; Notes §3 intro + §3.1"
    research_question: ""
    reason: "Slides p21 给出 Firth 名言和分布语义核心思想；Notes §3.1 详细解释了 co-occurrence matrix 构建、窗口大小选择（短窗口→语法，长窗口→语义，文档级→主题）、log 频率修正。概念完整，有具体例子。"
  - waypoint: WP03
    title: "Word2vec Skip-gram 模型"
    needs_deepresearch: false
    official_anchor: "Slides p24-30; Notes §3.2"
    research_question: ""
    reason: "Slides p24-30 完整展示 skip-gram 思想、context window、两向量 per word、softmax 公式、softmax 的三步分解（dot product → exp → normalize）；Notes §3.2 给出概率模型 Eq.4 和交叉熵损失 Eq.5。模型定义和目标函数完整。"
  - waypoint: WP04
    title: "梯度与优化"
    needs_deepresearch: false
    official_anchor: "Slides p31-35; Notes §3.3-3.4"
    research_question: ""
    reason: "Slides p33-35 覆盖 gradient descent 和 SGD；Notes §3.3 给出 empirical loss (Eq.6)、gradient step (Eq.7)、stochastic approximation (Eq.8)；Notes §3.4 完整推导 ∂L/∂v_c 的 Part A + Part B，得出 'observed minus expected' 直觉 (uo - E[uw])。推导完整，有逐步标注。"
  - waypoint: WP05
    title: "负采样 (Skip-gram Negative Sampling)"
    needs_deepresearch: true
    official_anchor: "Notes §3.5 (Eq.14-15); R02 paper Section 3"
    research_question: "负采样的理论动机是什么？为什么 logistic 近似能替代 softmax 归一化？负采样分布 pneg 为什么选 unigram^0.75 而不是均匀分布？负采样数 k 的选择依据？"
    reason: "Slides 没有独立的负采样章节（只有 softmax 目标）；Notes §3.5 给出 SGNS 公式 (Eq.15) 和直觉，但 (1) pneg 未定义（notes 原文 'a distribution we haven\\'t defined'），(2) 没有解释为什么 logistic 近似在理论上合理，(3) 没有解释 k 的选择和 unigram^0.75 的经验依据。这些细节只在 R02 原论文中。"
  - waypoint: WP06
    title: "词向量评估：可视化、类比与偏差"
    needs_deepresearch: true
    official_anchor: "A1 Part 1 Q1.5 + Part 2 Q2.1-2.9; Notes §3.1 (co-occurrence + SVD); Notes Appendix A.2 (SVD placeholder, empty)"
    research_question: "SVD 降维的数学直觉是什么（为什么取 top-k 奇异值能保留语义关系）？cosine similarity 和 L2 distance 的区别和适用场景？词类比算术 (king-man+woman≈queen) 的几何直觉？词向量偏差的来源和缓解方法？"
    reason: "Slides 几乎没有覆盖此主题（p36 只是 recap）；Notes §3.1 提到 co-occurrence + SVD 但没有推导；Notes Appendix A.2 'Singular Value Decomposition' 只有标题没有内容；cosine similarity、向量类比算术、偏差分析在 slides/notes 中均未教授，但 A1 Part 2 Q2.1-2.9 全部依赖这些概念。官方材料有明显缺口。"
```

---

## 5. needs_deepresearch 判定汇总

| WP | needs_deepresearch | 判定依据 |
|---|---|---|
| WP01 | false | Slides p16-20 + Notes §2.1-2.3 完整覆盖 one-hot → dense 的动机链 |
| WP02 | false | Slides p21-23 + Notes §3.1 完整覆盖分布语义 + co-occurrence |
| WP03 | false | Slides p24-30 + Notes §3.2 完整覆盖 skip-gram 模型 + softmax 目标 |
| WP04 | false | Slides p33-35 + Notes §3.3-3.4 完整覆盖梯度推导 + SGD |
| WP05 | **true** | Notes §3.5 给出公式但 pneg 未定义、理论动机不足、k 选择无依据；需 R02 论文补充 |
| WP06 | **true** | Slides/Notes 几乎未覆盖 cosine similarity / SVD / analogy / bias；A1 全部依赖这些概念但 lecture 没教 |
