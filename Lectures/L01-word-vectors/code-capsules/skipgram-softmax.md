## skipgram-softmax — Skip-gram Softmax 概率计算 P(o|c) {#skipgram-softmax}

> **Waypoint**: WP03 — Word2Vec / Skip-gram / Softmax
> **概念**：用 center word 的向量和所有 context words 的向量做点积，再经 softmax 归一化成概率分布
> **官方锚点**：Slides p27-30 (objective function, softmax); Notes §3.2 Eq.4-5

### 为什么不能只看文字

Slides p28-30 和 Notes §3.2 给出了 softmax 公式：

$$P(o|c) = \frac{\exp(u_o^T v_c)}{\sum_{w \in V} \exp(u_w^T v_c)}$$

但只看公式很难理解：
1. **分母的归一化到底在做什么**——它把 |V| 个 exp 值变成和为 1 的概率分布
2. **训练前后有什么区别**——随机初始化时所有概率几乎一样，训练后语义相关词的概率显著升高
3. **计算量问题**——分母要算 |V| 个 exp，这就是 WP04 引入 Negative Sampling 的原因

这个 capsule 用一个 8 词的小词汇表，把每一步都算出来给你看。

### 运行方式

**本地运行**：
```bash
cd /workspace/cs224n-study
.venv/bin/python Labs/L01-word-vectors/skipgram-softmax.py
```

**Colab 运行**：
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/skipgram-softmax.ipynb)

### 代码结构

脚本分为三部分：

**Part A: 随机初始化（训练前）**
- 随机生成 center 向量 V 和 context 向量 U（标准差 0.1）
- 选 "banking" 作为 center word
- 计算与所有 context words 的点积 → softmax
- **结果**：所有词的概率约 0.125（= 1/8），几乎没有区分

**Part B: 手工设计的"训练后"向量**
- 金融词（banking/money/credit/loan）在第 0 维有较大的正值
- 河流词（river/stream/water）在第 1 维有较大的正值
- bank（歧义词）在两维都有中等值
- **结果**：金融词概率显著升高（credit: 0.173），河流词显著降低（water: 0.072）

**Part C: 对比总结**
- 随机 vs 训练后的概率对比表
- 训练的目标（Notes Eq.5）就是调整 U、V 使真实 context word 的概率最大

### 输出图表

#### 图 1：训练后的概率分布

![skipgram-softmax-probability-bar](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174352.png)

**先看哪里**：x 轴是 context word，y 轴是概率 P(o|c)。虚线是均匀分布 1/8 = 0.125。

**关键观察**：
- 蓝色柱子（金融词：banking/money/credit/loan）明显高于虚线
- 绿色柱子（河流词：river/stream/water）明显低于虚线
- 橙色柱子（bank，歧义词）在中间

**课堂结论**：训练后的词向量让 softmax 能给语义相关的词分配更高的概率。

#### 图 2：点积 vs 概率对比

![skipgram-softmax-dotscore-vs-prob](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174401.png)

**先看哪里**：左图是点积分数（u_w^T v_c），右图是 softmax 后的概率。

**关键观察**：
- 点积越高 → exp 越大 → 概率越高
- softmax 的"放大"效果：点积的差异被指数化放大了

#### 图 3：随机 vs 训练后对比

![skipgram-softmax-random-vs-trained](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174404.png)

**先看哪里**：灰色柱子是随机初始化，蓝色柱子是训练后。

**关键观察**：
- 随机初始化：所有柱子几乎一样高（~0.125）
- 训练后：金融词升高，河流词降低
- 这就是训练的效果——让模型学会区分语义

### 关键数值（来自真实输出）

| Word | P_random | P_trained | Delta |
|------|----------|-----------|-------|
| banking | 0.1236 | 0.1948 | +0.0712 |
| money | 0.1249 | 0.1548 | +0.0299 |
| river | 0.1248 | 0.0717 | -0.0532 |
| bank | 0.1259 | 0.1158 | -0.0101 |
| stream | 0.1251 | 0.0784 | -0.0467 |
| credit | 0.1272 | 0.1728 | +0.0456 |
| loan | 0.1268 | 0.1401 | +0.0133 |
| water | 0.1217 | 0.0717 | -0.0500 |

**最高/最低比值**：
- 随机初始化：1.05x（几乎没区别）
- 训练后：2.72x（明显区分）

### 和课堂概念的对应

| 本 capsule | 官方材料 | Glossary |
|---|---|---|
| 点积 u_o^T v_c | Slides p28, Notes Eq.4 分子 | [[Lectures/L01-word-vectors/00-concept-glossary#dot-product\|dot product]] |
| Softmax 归一化 | Slides p30, Notes Eq.4 分母 | [[Lectures/L01-word-vectors/00-concept-glossary#softmax\|softmax]] |
| Center/context 向量 | Slides p25-26, p28 | [[Lectures/L01-word-vectors/00-concept-glossary#skip-gram\|skip-gram]] |
| 训练目标 | Notes Eq.5: min E[-log P(o\|c)] | [[Lectures/L01-word-vectors/00-concept-glossary#sgd\|SGD]] |
| 计算量问题 | → WP04 Negative Sampling | [[Lectures/L01-word-vectors/00-concept-glossary#negative-sampling\|negative sampling]] |

### 容易误解的地方

1. **Softmax 本身不"学习"**：它只是一个数学函数，把分数变成概率。真正在学习的是向量 U 和 V（通过梯度下降，见 WP04）。

2. **为什么每个词有两个向量**：v_w 是 center word 时的向量，u_w 是 context word 时的向量。这看起来浪费，但数学上方便（训练后可以合并或只用一套）。

3. **分母的计算量**：要算 |V| 个 exp。如果词汇表有 50000 个词，每次更新都要算 50000 个 exp——这就是为什么 WP04 要引入 Negative Sampling。

### 暂停复述

现在你应该能说出：
1. Softmax 的三步计算：点积 → 减 max → exp → 归一化
2. 训练前后概率分布的变化：从均匀到有区分
3. 分母的计算量问题：O(|V|)，引出 Negative Sampling

如果不确定，可以问 Hermes：
- "softmax 的分母为什么叫 partition function？"
- "为什么每个词需要两个向量而不是一个？"
- " Negative Sampling 怎么解决分母计算量的问题？"

### 数值来源证明

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T094936Z__t_9a2158c5__skipgram-softmax
  stdout: Labs/L01-word-vectors/outputs/skipgram-softmax-stdout.txt
  json: Labs/L01-word-vectors/outputs/skipgram-softmax-results.json
  checked_values:
    - claim: "随机初始化最高/最低比值 1.05x"
      source: "stdout Part A: Ratio: 1.05x"
      status: copied_from_output
    - claim: "训练后最高 P(banking|banking) = 0.194811"
      source: "stdout Part B: banking 0.194811"
      status: copied_from_output
    - claim: "训练后最低 P(water|banking) = 0.071667"
      source: "stdout Part B: water 0.071667"
      status: copied_from_output
    - claim: "训练后最高/最低比值 2.72x"
      source: "stdout Part B: Ratio: 2.72x"
      status: copied_from_output
    - claim: "对比表中 credit P_trained = 0.1728"
      source: "stdout Part C: credit 0.1728"
      status: copied_from_output
```
