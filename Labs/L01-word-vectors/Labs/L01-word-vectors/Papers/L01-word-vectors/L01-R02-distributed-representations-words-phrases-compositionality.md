---
title: "Distributed Representations of Words and Phrases and their Compositionality"
authors: ["Tomas Mikolov", "Ilya Sutskever", "Kai Chen", "Greg Corrado", "Jeffrey Dean"]
year: 2013
venue: NeurIPS 2013
reading_id: L01-R02
role: core
waypoints: [WP04, WP05]
canonical_url: "https://papers.nips.cc/paper_files/paper/2013/hash/9aa42b31882ec039965f3c4923ce901b-Abstract.html"
pdf_url: "https://papers.nips.cc/paper_files/paper/2013/file/9aa42b31882ec039965f3c4923ce901b-Paper.pdf"
local_pdf: "recovered/assets/papers/l01/L01-R02-mikolov-distributed-representations-neurips2013.pdf"
sha256: "9ee42f08c5e6325861ea22f3ef1174345a75fb696d1b27e659301aa88c996744"
pages: 9
---

# L01-R02: Distributed Representations of Words and Phrases and their Compositionality

> [!info] 本篇定位
> 这是 word2vec 的**第二篇论文**（NeurIPS 2013），紧接 R01（ICLR 2013 workshop）。R01 提出了 Skip-gram 和 CBOW 模型；**本篇的核心贡献是 Negative Sampling 和短语学习**。CS224N notes §3.5 的 SGNS 目标函数（Eq.14-Eq.15）直接来自本篇。

## 论文元信息

| 字段 | 值 |
|---|---|
| 标题 | Distributed Representations of Words and Phrases and their Compositionality |
| 作者 | Mikolov, Sutskever, Chen, Corrado, Dean（全 Google） |
| 发表 | NeurIPS 2013 |
| Canonical URL | https://papers.nips.cc/paper_files/paper/2013/hash/9aa42b31882ec039965f3c4923ce901b-Abstract.html |
| PDF URL | https://papers.nips.cc/paper_files/paper/2013/file/9aa42b31882ec039965f3c4923ce901b-Paper.pdf |
| 本地 PDF | `recovered/assets/papers/l01/L01-R02-mikolov-distributed-representations-neurips2013.pdf` |
| SHA256 | `9ee42f08c5e6325861ea22f3ef1174345a75fb696d1b27e659301aa88c996744` |
| 页数 | 9 |
| 提取方式 | PyMuPDF (fitz) 全文提取 |

---

## §1: Introduction（p1）— 论文想解决什么

> [!tip] 中文扶手
> 这篇论文在 R01 基础上做了**三件事**：
> 1. **加速训练**：用 Negative Sampling 替代 hierarchical softmax（§2.2）
> 2. **高频词下采样**：减少 "the"、"a" 等词的冗余训练（§2.3）
> 3. **短语学习**：把 "New York Times" 这样的固定搭配当成一个词来学（§4）
>
> 最后还发现了一个**惊喜**：向量加法可以组合词义（§5），比如 Russia + river ≈ Volga River。

**与 slides/notes 的关系**：
- slides p24-p30 讲的 Skip-gram 模型来自 R01；本篇 §2 从 Eq.1 重新形式化
- notes §3.5 说"SGNS 替代昂贵的 softmax 分母"——具体机制在本篇 §2.2
- notes 说 $p_{neg}$ "think of this like uniform"——本篇说 $U(w)^{3/4}/Z$ 最好

---

## Section 2: The Skip-gram Model（p2-3）

### Equation 1: Skip-gram 目标函数

$$\frac{1}{T} \sum_{t=1}^{T} \sum_{-c \leq j \leq c, j \neq 0} \log p(w_{t+j} | w_t)$$

**符号解释**：
- $T$：语料库总词数
- $w_t$：位置 $t$ 的中心词（center word）
- $c$：上下文窗口大小（可以是中心词的函数）
- $w_{t+j}$：位置 $t+j$ 的上下文词（context/outside word）
- $j \neq 0$：排除中心词自己

**中文直觉**：把所有"中心词-上下文词"配对的对数概率加起来求平均。模型越好，这些配对的概率越高，目标值越大。

**最小例子**：句子 "the cat sits on the mat"，$c=1$，中心词 "cat" 的配对是 ("cat","the") 和 ("cat","sits")。目标就是让 $p(\text{the}|\text{cat})$ 和 $p(\text{sits}|\text{cat})$ 都尽量大。

**对应位置**：
- notes §3.2 Eq.4-Eq.5 的 Skip-gram 概率和交叉熵目标
- slides p24-p30 的 Word2Vec 训练直觉

---

### Equation 2: Softmax 定义 ⚠️ WP04 关键瓶颈

$$p(w_O | w_I) = \frac{\exp(v'_{w_O}^\top v_{w_I})}{\sum_{w=1}^{W} \exp(v'_w{}^\top v_{w_I})}$$

**符号解释**：
- $v_w$：词 $w$ 的**输入向量**（input vector），维度 $d$
- $v'_w$：词 $w$ 的**输出向量**（output vector），维度 $d$
- $W$：词表大小（通常 $10^5$-$10^7$）
- 分子：中心词 $w_I$ 和上下文词 $w_O$ 的点积经指数变换
- 分母：**对所有 $W$ 个词**求和——这就是瓶颈！

**中文直觉**：
- 分子衡量"这两个词有多配"
- 分母是"归一化常数"——要和**整个词表**的每个词都比较一遍
- 词表 100 万个词 → 每次梯度更新要算 100 万次指数 → **太慢了**

> [!warning] 这就是 Negative Sampling 要解决的问题
> notes §3.5 说"the partition function pushes down all other words"——指的就是这个分母。
> 本篇 §2.2 的 Negative Sampling 用**二分类 logistic loss** 完全绕开了这个分母。

**对应位置**：
- **notes Eq.14** = 本篇 Eq.2（softmax 概率）
- slides p28-p30 的 softmax 分解
- R01 的原始 Skip-gram 公式

---

### Figure 1: Skip-gram 模型架构（p2）

![L01-R02 Figure 1 Skip-gram model architecture](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005626.png)

> 来源：R02 Figure 1 官方 PDF page 2 截图 访问日期：2026-06-10
> local_path: `Assets/L01-word-vectors/papers/L01-R02-p02-figure1-skipgram-architecture.png`

> [!info] 图片文字带读
> **原文关键词**：`The Skip-gram model architecture` / `training objective is to learn word vector representations that are good at predicting the nearby words`
>
> **中文翻译**：Skip-gram 模型架构。训练目标是学习词向量表示，使其能很好地预测附近的词。
>
> **这张图想说明什么**：中心词 $w(t)$ 的向量作为输入，经过一个线性层，输出层对每个上下文位置 $w(t-2)$ 到 $w(t+2)$ 做 softmax 预测。注意**每个位置共享同一套权重**（都是 $W \times d$ 的输出矩阵）。
>
> **不要被哪些英文干扰**：图中 $w(t-2)$ 到 $w(t+2)$ 的 one-hot 表示只是示意输出结构，不需要纠结 one-hot 细节。

---

### Section 2.1: Hierarchical Softmax（p3）

> [!tip] 中文扶手
> Hierarchical softmax 是 Negative Sampling 之前的"加速方案"。它用一棵**二叉 Huffman 树**把 $O(W)$ 的 softmax 变成 $O(\log W)$。
> 但实际使用中，**Negative Sampling 更简单、更快、效果更好**，所以现在主流都用 NEG。

### Equation 3: Hierarchical Softmax 定义

$$p(w | w_I) = \prod_{j=1}^{L(w)-1} \sigma\left([[n(w,j+1) = ch(n(w,j))]] \cdot v'_{n(w,j)}{}^\top v_{w_I}\right)$$

**符号解释**：
- $n(w,j)$：从根到词 $w$ 路径上的第 $j$ 个节点
- $L(w)$：路径长度
- $ch(n)$：节点 $n$ 的某个固定子节点
- $[[x]]$：指示函数，$x$ 为真时 =1，否则 =-1
- $\sigma(x) = 1/(1+e^{-x})$：sigmoid 函数
- $v'_{n}$：树内部节点 $n$ 的向量（注意：这里每个内部节点有自己的向量，不是每个词）

**中文直觉**：从根到目标词的路径上，每个分叉点做一次二分类（走左还是走右），所有二分类概率连乘 = 到达目标词的概率。路径平均长度 $\leq \log W$。

**对应位置**：notes §3.5 提到 hierarchical softmax 但没有展开公式。

---

## Section 2.2: Negative Sampling（p3-4）⭐ WP04 核心

> [!info] 这是本篇最重要的贡献
> Negative Sampling 把"预测上下文词"的多分类问题，变成了"区分正样本和噪声样本"的**二分类问题**。
> 不再需要对全词表求 softmax 分母。

### Equation 4: Negative Sampling 目标 ⭐

$$\log \sigma(v'_{w_O}{}^\top v_{w_I}) + \sum_{i=1}^{k} \mathbb{E}_{w_i \sim P_n(w)} \left[\log \sigma(-v'_{w_i}{}^\top v_{w_I})\right]$$

**符号解释**：
- $\sigma(x) = 1/(1+e^{-x})$：sigmoid 函数
- $v_{w_I}$：中心词的输入向量
- $v'_{w_O}$：**正样本**（真正的上下文词）的输出向量
- $v'_{w_i}$：**负样本**（从噪声分布 $P_n$ 中采样的词）的输出向量
- $k$：负样本数量（论文建议小数据集 $k=5$-$20$，大数据集 $k=2$-$5$）
- $P_n(w)$：噪声分布（论文发现 $U(w)^{3/4}/Z$ 最好）

**中文直觉**：
- **第一项**：让正样本对的向量点积尽量大 → $\sigma$ 输出接近 1 → $\log$ 接近 0
- **第二项**：让负样本对的向量点积尽量小（取负号）→ $\sigma(-小值)$ 接近 1 → $\log$ 接近 0
- 直觉就是：**拉近正样本对，推远负样本对**

> [!tip] 和 notes 的对应
> **notes Eq.15** = 本篇 Eq.4
> notes 说 $p_{neg}$ "think of this like uniform"——但论文原文说 $U(w)^{3/4}/Z$ 比均匀分布好得多。
> 这个差异在 Lecture Weaver 阶段需要向学生说明。

**最小例子**：
- 中心词 "cat"，正样本 "sits"，$k=2$ 个负样本 "airplane"、"philosophy"
- 目标：$\log\sigma(v'_{sits} \cdot v_{cat}) + \log\sigma(-v'_{airplane} \cdot v_{cat}) + \log\sigma(-v'_{philosophy} \cdot v_{cat})$
- 训练效果：cat 和 sits 的向量靠近，cat 和 airplane/philosophy 的向量远离

**对应位置**：
- **notes Eq.15**（SGNS 目标函数）
- slides p31-p35（SGD 优化和梯度直觉）
- readings-map WP04 核心公式

---

### 噪声分布 $P_n(w)$ 的选择 ^noise-distribution-choice

> [!warning] 关键细节
> 论文测试了三种噪声分布：
> 1. **均匀分布** $U(w) = 1/W$
> 2. **unigram 分布** $U(w) = \text{count}(w) / \text{total}$
> 3. **unigram^{3/4} 分布** $U(w)^{3/4}/Z$（$Z$ 是归一化常数）
>
> **结论**：$U(w)^{3/4}/Z$ 在**所有任务**上都显著优于其他两种。

**中文直觉**：
- 均匀分布：每个词被选为负样本的概率相同 → 低频词被过度采样
- unigram 分布：按词频采样 → 高频词（"the"、"a"）被过度采样
- $U(w)^{3/4}$：**折中方案**——压缩了高频词的概率，提升了低频词的概率
- 例如：如果 "the" 占词频 5%，在 $U^{3/4}$ 下大约只占 2-3%

**对应位置**：notes §3.5 说 "a distribution we haven't defined, called $p_{neg}$"——这里就是答案。

---

## Section 2.3: Subsampling of Frequent Words（p4-5）

### Equation 5: 高频词下采样公式

$$P(w_i) = 1 - \sqrt{\frac{t}{f(w_i)}}$$

**符号解释**：
- $f(w_i)$：词 $w_i$ 在语料库中的频率（出现次数 / 总词数）
- $t$：阈值，通常 $\approx 10^{-5}$
- $P(w_i)$：词 $w_i$ 被**丢弃**的概率

**中文直觉**：
- 如果 $f(w_i) \gg t$（高频词如 "the"），$P(w_i)$ 接近 1 → 几乎一定被丢弃
- 如果 $f(w_i) \approx t$（中频词），$P(w_i)$ 接近 0 → 几乎一定保留
- 如果 $f(w_i) < t$（低频词），公式无意义（$P < 0$），实际实现中 $P = 0$ → 一定保留

**最小例子**：$t = 10^{-5}$
- "the" 频率 $f = 0.05$（5%）→ $P = 1 - \sqrt{10^{-5}/0.05} = 1 - \sqrt{0.0002} \approx 1 - 0.014 = 0.986$ → 98.6% 概率丢弃
- "cat" 频率 $f = 10^{-5}$ → $P = 1 - 1 = 0$ → 保留

**为什么有效**：
1. **加速**：丢掉高频词 → 训练样本减少 → 训练更快（论文说 2x-10x）
2. **提升质量**："France" 和 "the" 共现信息量低，丢掉后 "France" 和 "Paris" 的相对权重更高

**对应位置**：notes 没有专门讲 subsampling，这是 R02 的独有贡献。

---

## Section 3: Empirical Results（p5）⭐ WP04 实验证据

### Table 1: 各方法准确率对比 ⭐

![L01-R02 Table 1 NEG vs HS vs NCE accuracy](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005636.png)

> 来源：R02 Table 1 官方 PDF page 5 截图 访问日期：2026-06-10
> local_path: `Assets/L01-word-vectors/papers/L01-R02-p05-table1-neg-vs-hs-accuracy.png`

> [!info] 图片文字带读 — 实验性能表
> **原文关键行列**：
>
> | Method | Time [min] | Syntactic [%] | Semantic [%] | Total [%] |
> |---|---|---|---|---|
> | NEG-5 | 38 | 63 | 54 | 59 |
> | NEG-15 | 97 | 63 | 58 | **61** |
> | HS-Huffman | 41 | 53 | 40 | 47 |
> | NCE-5 | 38 | 60 | 45 | 53 |
> | **NEG-5 + subsample** | **14** | 61 | 58 | 60 |
> | **NEG-15 + subsample** | **36** | 61 | 61 | **61** |
> | HS-Huffman + subsample | 21 | 52 | 59 | 55 |
>
> **中文翻译**：
> - NEG = Negative Sampling，HS = Hierarchical Softmax，NCE = Noise Contrastive Estimation
> - 数字 = 类比推理任务（"Germany":"Berlin"::"France":?）的准确率
> - Syntactic = 语法类比（如 quick:quickly），Semantic = 语义类比（如国家:首都）
>
> **这张表想说明什么**（WP04 核心证据）：
> 1. **NEG 全面优于 HS**：NEG-15 总准确率 61% vs HS 47%，差距 14 个百分点
> 2. **NEG 也优于 NCE**：61% vs 53%（相同 $k=5$ 时）
> 3. **Subsampling 大幅加速**：NEG-5 从 38 分钟降到 14 分钟（2.7x），准确率还从 59% 升到 60%
> 4. **最佳组合**：NEG-15 + subsampling = 61% 准确率，36 分钟
>
> **不要被哪些英文干扰**：训练数据是 10 亿词的新闻语料，vocabulary 692K，这些数字只需知道"大规模"即可。

**结论**：Negative Sampling + Subsampling = 更快训练 + 更好向量。这就是 CS224N notes §3.5 推荐的实践方案。

---

## Section 4: Learning Phrases（p5-6）⭐ WP05

> [!tip] 中文扶手
> 词向量有一个**天然局限**：它把每个词当成独立单元，无法表达"New York Times"这种整体含义不等于各词之和的短语。
> 本篇 §4 提出了一种**简单但有效**的方法：用数据统计找出固定搭配，把它们当成一个"大词"来训练。

### Equation 6: 短语打分公式

$$\text{score}(w_i, w_j) = \frac{\text{count}(w_i w_j) - \delta}{\text{count}(w_i) \times \text{count}(w_j)}$$

**符号解释**：
- $\text{count}(w_i w_j)$：$w_i$ 和 $w_j$ 作为相邻 bigram 出现的次数
- $\text{count}(w_i)$、$\text{count}(w_j)$：各自的 unigram 频率
- $\delta$：折扣系数，防止太低频的词被错误合并

**中文直觉**：
- 如果两个词经常**一起出现**但**很少单独出现** → score 高 → 合并为短语
- 类似 PMI（点互信息）的思路：共现频率 vs 独立出现频率的比值
- 例："New York" 经常一起出现，但 "New" 和 "York" 也各自常出现 → score 中等
- "Air Canada" 几乎总是一起出现 → score 高 → 合并

**训练流程**：跑 2-4 遍数据，每遍降低阈值，逐步合并更长的短语。

---

### Table 2: 短语类比示例（p6）⭐ WP05

![L01-R02 Table 2 phrase analogy examples](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005645.png)

> 来源：R02 Table 2 官方 PDF page 6 截图 访问日期：2026-06-10
> local_path: `Assets/L01-word-vectors/papers/L01-R02-p06-table2-phrase-analogy-examples.png`

> [!info] 图片文字带读 — 短语类比测试集示例
> **原文关键词**：5 个类别的类比对
>
> | 类别 | 示例 |
> |---|---|
> | Newspapers（报纸） | New York : New York Times :: Baltimore : Baltimore Sun |
> | NHL Teams（冰球队） | Montreal : Montreal Canadiens :: Toronto : Toronto Maple Leafs |
> | NBA Teams（篮球队） | Detroit : Detroit Pistons :: Oakland : Golden State Warriors |
> | Airlines（航空公司） | Austria : Austrian Airlines :: Spain : Spainair |
> | Company executives（公司高管） | Steve Ballmer : Microsoft :: Larry Page : Google |
>
> **中文翻译**：
> - 类比任务格式：A : B :: C : ?（A 对 B 的关系 = C 对 ? 的关系）
> - 例如：Montreal（城市）→ Montreal Canadiens（球队），那 Toronto → ?（答案：Toronto Maple Leafs）
>
> **这张表想说明什么**（WP05）：
> - 短语向量也能做类比推理，不只是单词
> - 完整测试集有 3218 个例子，最佳模型准确率 72%
> - 这扩展了 A1 Part 2 的单词类比到短语层面
>
> **不要被哪些英文干扰**：具体队名/公司名不需要记住，理解类比格式即可。

---

### Table 3: 短语 Skip-gram 结果（p6-7）

> [!example] Table 3 关键数据转写
>
> | Method | Dimensionality | No subsampling [%] | $10^{-5}$ subsampling [%] |
> |---|---|---|---|
> | NEG-5 | 300 | 24 | 27 |
> | NEG-15 | 300 | 27 | **42** |
> | HS-Huffman | 300 | 19 | **47** |
>
> **结论**：
> - 短语任务上，**HS + subsampling 反超 NEG**（47% vs 42%）
> - 这和 Table 1 的单词任务结论不同——说明**不同任务有不同最优超参**
> - 论文 §7 Conclusion 也强调："The choice of the training algorithm and the hyper-parameter selection is a task specific decision"

---

## Figure 2: PCA 可视化（p4）⭐ WP05

![L01-R02 Figure 2 PCA projection countries and capitals](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005633.png)

> 来源：R02 Figure 2 官方 PDF page 4 截图 访问日期：2026-06-10
> local_path: `Assets/L01-word-vectors/papers/L01-R02-p04-figure2-pca-countries-capitals.png`

> [!info] 图片文字带读
> **原文关键词**：`Two-dimensional PCA projection of the 1000-dimensional Skip-gram vectors of countries and their capital cities` / `The figure illustrates ability of the model to automatically organize concepts and learn implicitly the relationships between them`
>
> **中文翻译**：1000 维 Skip-gram 向量的二维 PCA 投影，展示国家和首都。图说明了模型能自动组织概念并隐式学习它们之间的关系——训练时没有提供任何关于"首都"含义的监督信息。
>
> **这张图想说明什么**（WP05 核心可视化）：
> - 国家（China, Japan, France...）和首都（Beijing, Tokyo, Paris...）在二维空间里**自动聚类**
> - 每个国家和它的首都**紧挨着**
> - 地理上相近的国家也倾向聚在一起（欧洲国家在一侧，亚洲国家在另一侧）
> - 这就是 A1 Part 2 让学生做的 PCA/t-SNE 可视化的**原始论文版本**
>
> **不要被哪些英文干扰**：PCA 是降维方法，具体投影坐标不需要记住，重点看聚类模式。

---

## Section 5: Additive Compositionality（p7）⭐ WP05

> [!tip] 中文扶手
> 除了类比推理（$vec(B) - vec(A) + vec(C) \approx vec(D)$），论文还发现**向量加法**本身就有意义：
> - $vec(\text{Russia}) + vec(\text{river})$ 的最近邻是 "Volga River"
> - $vec(\text{Germany}) + vec(\text{capital})$ 的最近邻是 "Berlin"
>
> 这和类比的差别：类比是 $A:B::C:D$ 的**差值平移**；加法是**直接合并两个概念**。

### 为什么加法有效？（论文解释）

> [!info] 论文原文解释
> "The word vectors are in a linear relationship with the inputs to the softmax nonlinearity. As the word vectors are trained to predict the surrounding words in the sentence, the vectors can be seen as representing the distribution of the context in which a word appears. These values are related logarithmically to the probabilities computed by the output layer, so **the sum of two word vectors is related to the product of the two context distributions**. The product works here as the **AND function**: words that are assigned high probabilities by both word vectors will have high probability, and the other words will have low probability."

**中文翻译**：
- 词向量线性地关联到 softmax 输入
- 词向量代表"这个词出现的上下文分布"
- 两个向量相加 ≈ 两个上下文分布**相乘**
- 乘法相当于 **AND 操作**：两个词都高概率预测的上下文词，相加后仍然高概率

**最小例子**：
- "Russian" 的上下文：常和 "Moscow"、"Vodka"、"Russia" 共现
- "river" 的上下文：常和 "Volga"、"Nile"、"flows" 共现
- 两者 AND：同时和两边共现的词 → "Volga River"（既在俄罗斯语境又在河流语境中出现）

---

### Table 5: 向量加法的组合性（p7）⭐ WP05

![L01-R02 Table 5 vector addition compositionality](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005649.png)

> 来源：R02 Table 5 官方 PDF page 7 截图 访问日期：2026-06-10
> local_path: `Assets/L01-word-vectors/papers/L01-R02-p07-table5-vector-addition-compositionality.png`

> [!info] 图片文字带读 — 向量加法示例表
> **原文关键行列**：
>
> | 输入 A + B | 最近邻 #1 | 最近邻 #2 | 最近邻 #3 | 最近邻 #4 |
> |---|---|---|---|---|
> | Czech + currency | koruna | Check crown | Polish zolty | CTK |
> | Vietnam + capital | Hanoi | Ho Chi Minh City | Viet Nam | Vietnamese |
> | German + airlines | airline Lufthansa | carrier Lufthansa | flag carrier Lufthansa | Lufthansa |
> | Russian + river | Moscow | Volga River | upriver | Russia |
> | French + actress | Juliette Binoche | Vanessa Paradis | Charlotte Gainsbourg | Cecile De |
>
> **中文翻译**：
> - Czech + currency → koruna（捷克克朗）✓
> - Vietnam + capital → Hanoi（河内）✓
> - German + airlines → airline Lufthansa（汉莎航空）✓
> - Russian + river → Moscow / Volga River（莫斯科/伏尔加河）— 部分正确
> - French + actress → Juliette Binoche（法国女演员）✓
>
> **这张表想说明什么**（WP05）：
> - 简单的向量加法能产生**语义上有意义**的结果
> - 不是 100% 精确（Russian + river 的第一个结果是 Moscow 不是 Volga River），但前 4 近邻里通常有正确答案
> - 这支持了论文的核心论点：词向量空间编码了**组合性语义**
>
> **不要被哪些英文干扰**：具体人名/地名不需要记住，重点看"加法能工作"这个现象。

---

## Section 6: Comparison to Published Word Representations（p7-8）

> [!example] Table 6 关键对比（简要）
> 论文把 Skip-Phrase（30B 词训练，1000 维，1 天）和 Collobert（2 个月）、Turian（几周）、Mnih（7 天）的向量做最近邻对比。
>
> 例：输入 "graffiti"
> - Collobert 50d 的最近邻：cheesecake, gossip, rearm（不相关）
> - Skip-Phrase 1000d 的最近邻：spray paint, graffiti, martial arts, taggers（语义相关）
>
> **结论**：大数据 + Skip-gram 的向量质量远超先前模型。

---

## Section 7: Conclusion（p8）— 关键贡献总结

> [!info] 论文自述贡献
> 1. **Skip-gram 训练词和短语向量**，展示线性结构支持精确类比推理
> 2. **Negative Sampling**：极简训练方法，对高频词学到准确表示
> 3. **Subsampling**：加速训练 + 提升低频词质量
> 4. **短语学习**：数据驱动方法识别短语，训练规模达 33B 词
> 5. **加法组合性**：向量加法能合并词义（AND 操作直觉）
> 6. **开源代码**：code.google.com/p/word2vec

---

## 三大抽取类检查

### 实验性能表 ✅
- Table 1（p5）：NEG vs HS vs NCE 在类比推理任务的准确率 → 已转写关键行列
- Table 3（p6-7）：短语类比任务结果 → 已转写

### 参数/消融表 ✅
- Table 1 同时包含 subsampling 的消融（有/无 subsampling 对比）
- 论文提到 $k=5$-$20$ 对小数据集好，$k=2$-$5$ 对大数据集好

### Main Result 可视化 ✅
- Figure 2（p4）：PCA 国家-首都聚类 → 已截图上传

---

## 与 CS224N 课程的完整对应

| 论文内容 | CS224N 对应 | Waypoint |
|---|---|---|
| Eq.2 Softmax 瓶颈 | notes Eq.14 | WP04 |
| Eq.4 Negative Sampling | notes Eq.15 | WP04 |
| $U(w)^{3/4}$ 噪声分布 | notes "think of this like uniform" | WP04 |
| Eq.5 Subsampling | notes 未覆盖 | WP04 |
| Table 1 实验对比 | notes §3.5 结论 | WP04 |
| Figure 2 PCA 可视化 | A1 Part 2 visualization | WP05 |
| §4 短语学习 | A1 Part 2 analogy 扩展 | WP05 |
| Table 5 加法组合性 | A1 Part 2 cosine similarity | WP05 |
| §5 加法解释（AND） | notes 未覆盖 | WP05 |
