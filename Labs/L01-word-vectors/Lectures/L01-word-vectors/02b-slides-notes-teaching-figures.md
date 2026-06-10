# L01 Word Vectors — Slides & Notes 教学图索引

> 本文件由 Paper Tutor (slides/notes) 阶段生成。
> 所有图片来自 CS224N 2025 官方 slides PDF (36p) 和 notes PDF (13p) 的页面截图。
> 图片通过 `remote_url` 显示，本地路径仅在 registry 中记录。
> 源 PDF：`recovered/assets/official/l01/cs224n-2025-lecture01-wordvecs1.pdf`、`recovered/assets/official/l01/cs224n-2025-lecture01-notes.pdf`

---

## WP01 — Course Intro & NLP Landscape

> **Slides 覆盖**：p1-p15（课程介绍、NLP 应用展示）
> **Notes 覆盖**：§1 (p1-p3)（NLP 定义、人类语言、应用场景）

### 教学图 WP01-1：课程讲授计划

![L01 slides p2 lecture plan](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-170157.png)

- **来源**：Slides p2
- **先看哪里**：5 个讲授模块的时间分配——(1) 课程介绍 10min → (2) 词义 15min → (3) Word2Vec 引入 15min → (4) 目标函数与梯度 25min → (5) 优化基础 5min
- **中文扶手**：今天的核心学习目标是——**词义可以用实数向量来相当好地表示**（The astounding result that word meaning can be represented rather well by a vector of real numbers）

### 教学图 WP01-2：完整课堂计划（含"看词向量"环节）

![L01 slides p9 lecture plan with word vectors](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-170200.png)

- **来源**：Slides p9
- **先看哪里**：注意第 6 项 "Looking at word vectors (10 mins or less)"——这对应 WP05 的预训练向量可视化/类比
- **中文扶手**：这个环节在课堂上实际展示了预训练词向量的效果，但 slides 正文没有展开，需要结合 A1 作业来学

### 教学图 WP01-3：NLP 应用——机器翻译

> [!info] 图片带读
> Slides p11 展示了神经机器翻译的实际效果。页面包含一段 Kiswahili 新闻网站截图，说明 NMT 已经相当好用。
> - 关键英文：*"Trained on text data, neural machine translation is quite good!"*
> - 中文翻译：「在文本数据上训练后，神经机器翻译已经相当好了！」
> - **学习结论**：这是 NLP 最早期也最成功的应用之一，驱动了词表示研究的发展

### 教学图 WP01-4：NLP 应用——问答系统

> [!info] 图片带读
> Slides p12 展示了自由文本问答系统。示例：用户问 *"when did Kendrick Lamar's first album come out?"*，系统回答 *"July 2, 2011"*。
> - 关键英文：*"Free-text question answering: Next gen search"*
> - 中文翻译：「自由文本问答：下一代搜索」
> - **学习结论**：QA 是 NLP 的核心应用，需要模型理解词义和语义关系

### 教学图 WP01-5：NLP 应用——文本到图像

> [!info] 图片带读
> Slides p14 展示 DALL-E 2 根据文本描述生成图像。从 *"a train going over the Golden Gate bridge"* 到逐步添加修饰语（*"with the bay in the background"*, *"detailed pencil drawing"* 等），模型能精确响应每个语言修饰。
> - **学习结论**：语言模型学到的表示已经丰富到可以驱动跨模态生成，这一切的基础是词向量表示

---

## WP02 — One-hot vs Dense Vectors

> **Slides 覆盖**：p16-p23（词义表示、WordNet、one-hot、分布语义、dense vectors）
> **Notes 覆盖**：§2.1-§3.1 (p3-p7)（signifier/signified、one-hot Eq.1-2、WordNet/UniMorph、分布假说、共现矩阵）

### 教学图 WP02-1：词义——能指与所指

![L01 slides p16 signifier signified](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005738.png)

- **来源**：Slides p16
- **先看哪里**：核心公式 `signifier (symbol) ⟺ signified (idea or thing)` = denotational semantics
- **中文扶手**：
  - signifier（能指/符号）= 词本身，如 "tree"
  - signified（所指/概念）= 词代表的想法或事物
  - 这是语言学中最基础的词义理论，但计算机无法直接处理这种抽象对应

### 教学图 WP02-2：WordNet 示例

![L01 slides p17 WordNet example](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005742.png)

- **来源**：Slides p17
- **先看哪里**：两段 NLTK 代码——(1) 查 "good" 的同义词集 (2) 查 "panda" 的上位词链
- **图片文字带读**：
  - 上方代码输出 `good` 的多个词性和同义词：`noun: good, goodness; adj: good, just, upright...`
  - 下方代码输出 `panda` 的上位词链：`panda → procyonid → carnivore → placental → mammal → ... → entity`
  - **中文翻译**：WordNet 是一个人工标注的同义词集和上位词（"是一种"）关系数据库
  - **学习结论**：WordNet 提供了结构化的词义关系，但有严重缺陷（见下页）

### 教学图 WP02-3：One-hot 向量表示

![L01 slides p19 one-hot vectors](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005756.png)

- **来源**：Slides p19
- **先看哪里**：`motel = [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0]`，`hotel = [0 0 0 0 0 0 0 1 0 0 0 0 0 0 0]`
- **图片文字带读**：
  - 关键英文：*"In traditional NLP, we regard words as discrete symbols"*
  - 中文翻译：「在传统 NLP 中，我们把词看作离散符号」
  - *"Vector dimension = number of words in vocabulary (e.g., 500,000+)"*
  - 中文翻译：「向量维度 = 词汇表大小（例如 50 万+）」
  - **学习结论**：one-hot 编码让每个词成为正交基向量，维度等于词汇量

### 教学图 WP02-4：One-hot 的正交问题

![L01 slides p20 one-hot orthogonality problem](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005759.png)

- **来源**：Slides p20
- **先看哪里**：搜索 "Seattle motel" 应匹配 "Seattle hotel"，但 one-hot 下两个向量**正交**
- **图片文字带读**：
  - 关键英文：*"These two vectors are orthogonal. There is no natural notion of similarity for one-hot vectors!"*
  - 中文翻译：「这两个向量是正交的。one-hot 向量没有自然的相似度概念！」
  - 解决方案提示：*"learn to encode similarity in the vectors themselves"*
  - 中文翻译：「学习把相似度编码到向量本身中」
  - **学习结论**：这是 one-hot 表示的致命缺陷——语义相近的词（motel/hotel）和完全无关的词距离一样

### 教学图 WP02-5：Notes——One-hot 向量的数学论证

![L01 notes p4 one-hot vectors equation](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005916.png)

- **来源**：Notes p4, §2.2 Eq.1-2
- **先看哪里**：Eq.1 定义 one-hot 向量 v_tea = e₃, v_coffee = eⱼ；Eq.2 证明 v_tea^T v_coffee = v_tea^T v_the = 0
- **图片文字带读**：
  - 关键英文：*"all words are equally dissimilar from each other"*
  - 中文翻译：「所有词彼此之间同等不相似」
  - **学习结论**：点积为 0 意味着 tea-coffee 和 tea-the 的"距离"完全一样——这显然不符合语言事实

### 教学图 WP02-6：分布语义假说

![L01 slides p21 distributional semantics](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005803.png)

- **来源**：Slides p21
- **先看哪里**：Firth 名言 *"You shall know a word by the company it keeps"* (J.R. Firth 1957)
- **图片文字带读**：
  - 关键英文：*"Distributional semantics: A word's meaning is given by the words that frequently appear close-by"*
  - 中文翻译：「分布语义学：一个词的意义由经常出现在它附近的词决定」
  - 示例：banking 的上下文包含 government, debt, crises, Europe, unified, regulation...
  - **学习结论**：这是现代词向量最核心的思想——用上下文定义词义

### 教学图 WP02-7：Notes——分布假说与共现

![L01 notes p6 distributional hypothesis](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005919.png)

- **来源**：Notes p6, §3
- **先看哪里**：callout 框中的分布假说定义 + Firth 引用 + tea 的上下文示例
- **图片文字带读**：
  - tea 的上下文：drank, the, pot, kettle, bag, delicious, oolong, hot, steam...
  - **学习结论**：与 tea 相似的词（如 coffee）会有相似的上下文分布——这就是"分布相似 = 语义相似"

### 教学图 WP02-8：Notes——共现矩阵与窗口大小

![L01 notes p7 co-occurrence matrix and windows](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005924.png)

- **来源**：Notes p7, §3.1
- **先看哪里**：窗口大小对比——短窗口（1 词）编码语法，长窗口编码语义/主题
- **图片文字带读**：
  - 关键英文：*"Larger notions of co-occurrence lead to more semantic or topic-encoding representations; shorter windows lead to more syntax-encoding representations"*
  - 中文翻译：「更大的共现范围产生更偏语义/主题的表示；更短的窗口产生更偏语法的表示」
  - **学习结论**：窗口大小是一个关键超参数，决定了学到的向量捕捉什么类型的信息

### 教学图 WP02-9：Dense 词向量

![L01 slides p22 dense word vectors](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005806.png)

- **来源**：Slides p22
- **先看哪里**：banking 和 monetary 的 dense vector 对比——每个维度都是实数
- **图片文字带读**：
  - 关键英文：*"We will build a dense vector for each word, chosen so that it is similar to vectors of words that appear in similar contexts, measuring similarity as the vector dot product"*
  - 中文翻译：「我们将为每个词构建一个稠密向量，使得出现在相似上下文中的词具有相似的向量，用向量点积衡量相似度」
  - **学习结论**：dense vector 解决了 one-hot 的所有问题——低维、有相似度、可计算

### 教学图 WP02-10：词向量可视化

![L01 slides p23 word vector visualization](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005809.png)

- **来源**：Slides p23
- **先看哪里**：banking 的 8 维向量可视化展示——每个维度是一个实数值
- **学习结论**：这就是"embedding"——把高维离散符号压缩到低维连续空间

---

## WP03 — Word2Vec / Skip-gram / Softmax

> **Slides 覆盖**：p24-p30（Word2Vec 框架、窗口示例、两向量、softmax）
> **Notes 覆盖**：§3.2 (p7-p8)（skipgram 模型 Eq.4-5、交叉熵目标）

### 教学图 WP03-1：Word2Vec 概述

![L01 slides p24 Word2Vec overview](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005824.png)

- **来源**：Slides p24
- **先看哪里**：5 步流程——(1) 大语料 (2) 每词一向量 (3) 遍历每个位置 t，有 center word c 和 context words o (4) 用 c、o 向量相似度算 P(o|c) (5) 调整向量最大化概率
- **图片文字带读**：
  - 关键英文：*"Word2vec is a framework for learning word vectors (Mikolov et al. 2013)"*
  - 右下角标注：*"Skip-gram model (Mikolov et al. 2013)"*
  - **学习结论**：Word2Vec 不是一个算法，而是一个框架；Skip-gram 是其中一种具体模型

### 教学图 WP03-2：窗口示例——center 和 context

![L01 slides p25 Word2Vec window example](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005827.png)

- **来源**：Slides p25
- **先看哪里**：以 "banking" 为中心词，窗口大小 2，4 个 context words：turning, problems, into, crises
- **图片文字带读**：
  - 需要计算的 4 个概率：P(w_{t+1}|w_t), P(w_{t+2}|w_t), P(w_{t-1}|w_t), P(w_{t-2}|w_t)
  - 中文翻译：给定中心词 banking，预测窗口内每个位置出现各词的概率
  - **学习结论**：Skip-gram 的核心操作——从一个中心词预测周围所有词

### 教学图 WP03-3：每个词两个向量 + Softmax 公式

![L01 slides p28 two vectors per word softmax](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005833.png)

- **来源**：Slides p28
- **先看哪里**：
  - ① v_w 当 w 是 center word
  - ② u_w 当 w 是 context word
  - ③ P(o|c) = exp(u_o^T v_c) / Σ_w exp(u_w^T v_c)
- **图片文字带读**：
  - 上方重复了目标函数 J(θ) = -1/T Σ Σ log P(w_{t+j}|w_t; θ)
  - 关键提问：*"How to calculate P(w_{t+j}|w_t; θ)?"*
  - 中文翻译：「如何计算给定中心词时上下文词的条件概率？」
  - **学习结论**：每个词有两套向量——作为中心词时的 v 和作为上下文词时的 u。这看起来浪费，但数学上方便

### 教学图 WP03-4：用向量计算的具体示例

![L01 slides p29 Word2Vec with vectors](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005836.png)

- **来源**：Slides p29
- **先看哪里**：中心词 "into" (v_into)，4 个 context 的概率计算
- **图片文字带读**：
  - P(u_problems | v_into) 简写为 P(problems | into; u_problems, v_into, θ)
  - 4 个概率：P(u_banking|v_into), P(u_crisis|v_into), P(u_turning|v_into), P(u_problems|v_into)
  - **学习结论**：这就是用点积 + softmax 把"词对"转化为概率的具体过程

### 教学图 WP03-5：Softmax 函数详解

![L01 slides p30 softmax prediction function](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005848.png)

- **来源**：Slides p30
- **先看哪里**：三步分解——① 点积比较相似度 ② 指数化使其为正 ③ 归一化为概率分布
- **图片文字带读**：
  - softmax(x_i) = exp(x_i) / Σ_j exp(x_j) = p_i
  - *"max" because amplifies probability of largest x_i*
  - *"soft" because still assigns some probability to smaller x_i*
  - 中文翻译：「'max' 因为它放大最大 x_i 的概率；'soft' 因为它仍给较小的 x_i 分配一些概率」
  - **学习结论**：softmax 是深度学习中极常用的函数——把任意实数分数转化为概率分布

### 教学图 WP03-6：Notes——Skipgram 模型公式

![L01 notes p8 skipgram model equation](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005927.png)

- **来源**：Notes p8, §3.2 Eq.4-5
- **先看哪里**：
  - Eq.4：p_{U,V}(o|c) = exp(u_o^T v_c) / Σ_w exp(u_w^T v_c)
  - Eq.5：min_{U,V} E_{o,c}[-log p_{U,V}(o|c)]
- **图片文字带读**：
  - U ∈ R^{|V|×d} 和 V ∈ R^{|V|×d}——两个参数矩阵
  - 每个词关联 U 的一行和 V 的一行
  - Eq.5 读法：「最小化参数 U、V 关于真实分布的交叉熵损失」
  - **学习结论**：Notes 用随机变量 C（中心词）和 O（上下文词）更严格地定义了同一个模型

---

## WP04 — Objective / Gradients / Negative Sampling

> **Slides 覆盖**：p27-p35（目标函数、梯度、GD、SGD）
> **Notes 覆盖**：§3.3-§3.5 (p8-p12)（经验损失 Eq.6、梯度 Eq.7-13、负采样 Eq.14-15）

### 教学图 WP04-1：目标函数——数据似然与损失

![L01 slides p27 objective function](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005830.png)

- **来源**：Slides p27
- **先看哪里**：
  - 数据似然 L(θ) = Π_{t=1}^{T} Π_{-m≤j≤m, j≠0} P(w_{t+j}|w_t; θ)
  - 损失函数 J(θ) = -1/T log L(θ)（平均负对数似然）
- **图片文字带读**：
  - 关键等式：*"Minimizing objective function ⟺ Maximizing predictive accuracy"*
  - 中文翻译：「最小化目标函数 ⟺ 最大化预测准确度」
  - θ 是所有待优化参数；有时称为 cost 或 loss function
  - **学习结论**：整个 Word2Vec 训练就是最小化这个 J(θ)

### 教学图 WP04-2：训练——调整参数最小化损失

![L01 slides p31 loss minimization and gradient](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005852.png)

- **来源**：Slides p31
- **先看哪里**：参数向量 θ 包含所有词的所有向量（每词两个 d 维向量，|V| 个词）
- **图片文字带读**：
  - 关键英文：*"We optimize these parameters by walking down the gradient"*
  - 中文翻译：「我们通过沿梯度下行来优化这些参数」
  - *"We compute all vector gradients!"*
  - **学习结论**：右侧图展示了损失曲面和梯度下降的直觉——沿最陡方向走

### 教学图 WP04-3：梯度下降算法

![L01 slides p33 gradient descent](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005855.png)

- **来源**：Slides p33
- **先看哪里**：GD 的核心思想——计算梯度，沿负梯度方向走小步，重复
- **图片文字带读**：
  - 关键英文：*"calculate gradient of J(θ), then take small step in direction of negative gradient. Repeat."*
  - 中文翻译：「计算 J(θ) 的梯度，然后沿负梯度方向走一小步。重复。」
  - 注释：*"Our objectives may not be convex like this, but life turns out to be okay"*
  - 中文翻译：「我们的目标函数可能不像这样是凸的，但结果发现没关系」
  - **学习结论**：虽然 Word2Vec 的损失不是凸函数，但 SGD 在实践中效果很好

### 教学图 WP04-4：GD 更新公式

![L01 slides p34 gradient descent update equation](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005859.png)

- **来源**：Slides p34
- **先看哪里**：矩阵形式 θ ← θ - α∇_θ J(θ)；单参数形式 θ_i ← θ_i - α ∂J/∂θ_i
- **图片文字带读**：
  - α = step size or learning rate（步长/学习率）
  - **学习结论**：学习率 α 控制每步走多远——太大会震荡，太小会慢

### 教学图 WP04-5：随机梯度下降 (SGD)

![L01 slides p35 stochastic gradient descent](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005902.png)

- **来源**：Slides p35
- **先看哪里**：问题——J(θ) 依赖语料库所有窗口（可能数十亿），梯度计算极贵
- **图片文字带读**：
  - 关键英文：*"Problem: J(θ) is a function of all windows in the corpus (potentially billions!)"*
  - 中文翻译：「问题：J(θ) 是语料库中所有窗口的函数（可能有数十亿！）」
  - 解决方案：*"Repeatedly sample windows, and update after each one"*
  - 中文翻译：「反复采样窗口，每个窗口后更新一次」
  - **学习结论**：SGD 是训练 Word2Vec 的实际算法——每次只用一个窗口（或小 batch）近似梯度

### 教学图 WP04-6：Notes——经验损失公式

![L01 notes p9 empirical loss](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005931.png)

- **来源**：Notes p9, §3.3 Eq.6-7
- **先看哪里**：
  - Eq.6：L(U,V) = Σ_d Σ_{i=1}^{m} Σ_{j=1}^{k} -log p_{U,V}(w_{i-j}^{(d)} | w_i^{(d)})
  - Eq.7：U^{(i+1)} = U^{(i)} - α∇_U L(U^{(i)}, V^{(i)})
- **图片文字带读**：
  - Eq.6 的三层求和：(1) 所有文档 (2) 文档中所有词 (3) 窗口中所有词
  - Eq.7 读法：「U 在第 i+1 次迭代 = 第 i 次的值 减去 α 乘以损失对 U 的梯度」
  - **学习结论**：Notes 把 slides 的直觉严格化为三层求和的经验损失

### 教学图 WP04-7：Notes——"Observed minus Expected" 梯度直觉

![L01 notes p11 observed minus expected](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005935.png)

> [!warning] 注意：此图在前次 registry 中标为 notes p11，实际对应 PDF p12 上半部分
> 本 run 已渲染正确的 notes p11 (gradient Part B) 和 p12 (negative sampling)，但上传因 MCP SSL 故障 pending

- **来源**：Notes p11-12, §3.4
- **先看哪里**：梯度推导的最终结果 ∇_{v_c} = u_o - E[u_w] = "observed" - "expected"
- **图片文字带读**：
  - 关键英文：*"the vector for the word actually observed: u_o. We subtract from that the vector that the model expected"*
  - 中文翻译：「实际观察到的词的向量 u_o，减去模型预期的向量」
  - **学习结论**：梯度的直觉极其优美——把中心词向量推向实际出现的上下文词，远离模型预期的词

### 教学图 WP04-8：Notes——负采样目标函数

> [!tip] 此图使用前次上传的 URL（notes p12 内容，前次标为 p11）

![L01 notes p12 negative sampling](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/09/20260609-005935.png)

- **来源**：Notes p12, §3.5 Eq.14-15
- **先看哪里**：
  - Eq.14：softmax 的分子（affinity）和分母（partition function）
  - Eq.15：SGNS 目标 = log σ(u_o^T v_c) + Σ_{ℓ=1}^{k} log σ(-u_ℓ^T v_c)
- **图片文字带读**：
  - 关键英文：*"The partition function 'pushes down' on all the words other than the observed words"*
  - 中文翻译：「分区函数把除观察词以外的所有词都往下压」
  - p_neg 说明：*"a distribution we haven't defined, called p_neg. Think of this for now like the uniform distribution over V"*
  - 中文翻译：「一个我们还没定义的分布 p_neg。暂时可以把它想象成 V 上的均匀分布」
  - **学习结论**：负采样用 k 个随机负例替代了昂贵的全词汇表归一化，是 Word2Vec 实用的关键
  - **⚠️ 注意**：Notes 明确说 p_neg 未定义，实际使用的噪声分布需要看 R02 原论文（DeepResearch 范围）

---

## Blockers & Gaps

> [!warning] WP05 在 slides/notes 中无可视化证据
> Slides p9 列出 "Looking at word vectors (10 mins or less)" 但 slides 正文没有对应内容页。Notes 附录 A.1 CBOW / A.2 SVD 只有标题无正文。WP05 的预训练向量可视化、类比、PCA/t-SNE 需要依赖 A1 作业和 DeepResearch 产物来补充。

> [!warning] 6 张图片上传 pending
> slides p11 (NLP translation)、p12 (QA)、p14 (image gen) 和 notes p5 (annotated vectors)、p10 (gradient derivation)、p11 (observed-expected) 因 MCP 上传服务 SSL 故障暂无法上传。这些是补充性图片，核心教学内容已由其他 25 张图覆盖。WP01 的 NLP 应用示例和 WP02/WP04 的 notes 中间推导页在文档中用文字带读替代。
