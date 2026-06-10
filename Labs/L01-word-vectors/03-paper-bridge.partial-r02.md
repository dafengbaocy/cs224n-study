<!-- 03-paper-bridge.partial-r02.md -->
<!-- Producer: L01-R02 Paper Tutor -->
<!-- Coverage: WP04, WP05 -->
<!-- Date: 2026-06-10 -->

## L01-R02 Bridge: WP04 & WP05 → Paper Note

### WP04: Objective / Gradients / Negative Sampling

**推荐阅读顺序**：

1. 先看 full softmax 的瓶颈：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Equation 2: Softmax 定义 ⚠️ WP04 关键瓶颈|Eq.2 — 分母要对全词表 W 个词求和，O(W) 太慢]]
2. 进入负采样核心动机：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Section 2.2: Negative Sampling（p3-4）⭐ WP04 核心|§2.2 — 用二分类 logistic loss 替代 softmax 分母]]
3. 看负采样目标函数详细拆解：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Equation 4: Negative Sampling 目标 ⭐|Eq.4 — log σ(正样本) + Σ log σ(-负样本)，pull up + push down]]
4. 理解噪声分布选择：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#^noise-distribution-choice|U(w)^3/4 为什么比均匀分布和 unigram 分布都好]]
5. 高频词下采样加速：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Section 2.3: Subsampling of Frequent Words（p4-5）|§2.3 — Eq.5 下采样公式，2x-10x 加速]]
6. 看实验证据：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Table 1: 各方法准确率对比 ⭐|Table 1 — NEG-15+subsample 61% vs HS 47%，训练时间还更短]]

**与 notes/slides 的精确对应**：
- notes Eq.14 = 论文 Eq.2（softmax 概率定义）→ [[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Equation 2: Softmax 定义 ⚠️ WP04 关键瓶颈|notes Eq.14 的论文原文]]
- notes Eq.15 = 论文 Eq.4（负采样目标函数）→ [[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Equation 4: Negative Sampling 目标 ⭐|notes Eq.15 的论文原文]]
- notes 说 $p_{neg}$ "think of this like uniform" → 论文原文说 $U(w)^{3/4}/Z$ 最好 → [[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#^noise-distribution-choice|噪声分布的选择]]
- slides p31-p35 讲 SGD 和梯度直觉 → 论文 §2.2 提供具体目标函数和 $k$ 值建议

**回 readings-map 锚点**：`notes §3.5 Eq.14-Eq.15; slides p31-p35; R02 negative sampling paper`

---

### WP05: Pretrained Vectors / Analogy / Visualization

**推荐阅读顺序**：

1. 先看可视化证据：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Figure 2: PCA 可视化（p4）⭐ WP05|Figure 2 — PCA 国家-首都聚类，训练时无监督]]
2. 短语学习动机和方法：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Section 4: Learning Phrases（p5-6）⭐ WP05|§4 — Eq.6 短语打分 + 为什么需要短语表示]]
3. 短语类比示例：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Table 2: 短语类比示例（p6）⭐ WP05|Table 2 — 5 类短语类比：报纸、球队、航空公司、高管]]
4. 向量加法组合性：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Section 5: Additive Compositionality（p7）⭐ WP05|§5 — Russia + river ≈ Volga River]]
5. 加法示例表：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Table 5: 向量加法的组合性（p7）⭐ WP05|Table 5 — 5 个加法组合例子 + 最近邻结果]]
6. 为什么加法有效（AND 直觉）：[[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#为什么加法有效？（论文解释）|论文解释 — 上下文分布的乘积 = AND 操作]]

**与 A1 Part 2 的精确对应**：
- A1 让学生加载 GloVe 向量做 cosine similarity → R02 Figure 2 是这类 PCA 可视化的原始论文版本 → [[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Figure 2: PCA 可视化（p4）⭐ WP05|Figure 2]]
- A1 analogy 问题（king-man+woman≈queen）→ R02 Table 5 的加法组合性是理论基础 → [[Papers/L01-word-vectors/L01-R02-distributed-representations-words-phrases-compositionality#Table 5: 向量加法的组合性（p7）⭐ WP05|Table 5]]
- A1 的 bias 探索 → R02 展示了向量空间编码了语义关系（包括可能的偏见）

**回 readings-map 锚点**：`A1 Part 2 vector relationship exploration; R02 compositionality examples`
