## skipgram-softmax — Skip-gram Softmax 概率计算 P(o|c) {#skipgram-softmax}

> [!info] 这个 Capsule 在看什么
> **概念**：[[Lectures/L01-word-vectors/00-concept-glossary#skip-gram|Skip-gram]] 模型用中心词 c 的向量 $v_c$ 和每个候选上下文词 w 的向量 $u_w$ 做点积，再通过 [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 归一化成概率分布 P(o|c)。
>
> **为什么不能只靠文字**：Slides p28-30 和 Notes §3.2 给出了 softmax 公式，但只有实际计算一个 mini vocabulary 的 P(o|c)，才能理解分母归一化需要遍历全词表的计算量——这正是 WP05 负采样要解决的瓶颈。
>
> **官方锚点**：Slides p27-30 (objective function, softmax); Notes §3.2 (Eq.4-5)

### 运行方式

**Colab 打开**（推荐）：[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/skipgram-softmax.ipynb)

**本地运行**：
```bash
cd /workspace/cs224n-study
python3 Labs/L01-word-vectors/skipgram-softmax.py
```

### 这段代码在做什么

1. 定义 6 词 mini vocabulary（banking, money, crisis, turning, problems, into），每词两个 3 维向量（中心向量 V + 上下文向量 U）
2. 选 "banking" 作为中心词 c，计算 $u_w^T v_c$（点积）
3. 对每个点积取 exp → 得到正数分数
4. 除以所有 exp 之和 Z（partition function）→ 归一化成概率 P(o|c)
5. 观察：softmax 如何把「分数」变成「概率分布」，以及分母 O(|V|) 的计算代价

### 运行后先看哪里

> [!tip] 输出解读
> 1. **点积**：banking 自己最高（+0.4136），money 次之（-0.3607），其他词更负。
> 2. **exp 之后**：所有值变成正数——banking = 1.512252，into 最小 = 0.038438。
> 3. **归一化**：P(banking|banking) = 0.540191 最高，P(into|banking) = 0.013730 最低。概率总和 = 1.0。
> 4. **排名**：banking > money > crisis > turning > problems > into——语义越相关，概率越高。

### 关键输出

**Softmax 三步计算**（center = "banking"）：

```
Step 1: Dot products  u_w^T v_c
  u_   banking^T v_banking = +0.4136
  u_     money^T v_banking = -0.3607
  u_    crisis^T v_banking = -1.1286
  u_   turning^T v_banking = -1.8764
  u_  problems^T v_banking = -2.5906
  u_      into^T v_banking = -3.2587

Step 2: Exponentiation  exp(u_w^T v_c)
  exp(+0.4136) = 1.512252
  exp(-0.3607) = 0.697188
  exp(-1.1286) = 0.323486
  exp(-1.8764) = 0.153140
  exp(-2.5906) = 0.074975
  exp(-3.2587) = 0.038438

Step 3: Z = 2.799479 (遍历全部 6 个词)

Step 4: P(o|c) = exp(u_o^T v_c) / Z
  P(   banking | banking) = 0.540191
  P(     money | banking) = 0.249042
  P(    crisis | banking) = 0.115552
  P(   turning | banking) = 0.054703
  P(  problems | banking) = 0.026782
  P(      into | banking) = 0.013730
  sum = 1.000000
```

**排名**：

| 排名 | 词 | P(o\|c) | 说明 |
|------|-----|---------|------|
| 1 | banking | 0.540191 | 中心词自己，概率最高 |
| 2 | money | 0.249042 | 语义相关（金融），第二高 |
| 3 | crisis | 0.115552 | 主题相关 |
| 4 | turning | 0.054703 | 弱相关 |
| 5 | problems | 0.026782 | 弱相关 |
| 6 | into | 0.013730 | 功能词，概率最低 |

### Softmax 三步可视化

![Softmax 三步：Dot product → Exponentiation → Normalize](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181650.png)

> [!tip] 读图指南
> - **左图（Dot products）**：绿色柱表示每个词和中心词 "banking" 的点积。banking 自己最高（+0.41），其他词都是负数——说明在这个 toy 向量空间里，"banking" 和自己的上下文向量最对齐。
> - **中图（Exponentiation）**：取 exp 后所有值变成正数。注意 exp 放大了差异——最高值 1.51 是最低值 0.04 的约 39 倍，而原始点积差异只有 3.67。
> - **右图（Normalize）**：除以 Z=2.80 后变成概率分布，所有柱加起来恰好 = 1.0。

### 概率分布图

![Skip-gram Softmax P(o|c) 概率分布](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181644.png)

> [!tip] 读图指南
> - 红色柱 = 中心词自己（banking），蓝色柱 = 语义相关词（money），灰色 = 其他词。
> - banking 自己占 54%，money 占 25%——两者合计 79%，说明 softmax 成功把概率集中到了语义相关的词上。
> - into 只有 1.4%——和功能词的共现概率最低。

### Partition Function 计算代价

![Partition Function O(|V|) 计算代价](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181653.png)

> [!tip] 读图指南
> - 横轴是词汇表大小 |V|，纵轴是计算一次 softmax 分母需要的时间。
> - 我们的 mini vocab（|V|=6）只需 0.006 ms——几乎不花时间。
> - 真实 word2vec（|V| ≈ 50K-100K）每步需要 50-100 ms——**每一步训练**都要算这么多次 exp！
> - 这就是 WP05 负采样要解决的问题：用 logistic 二分类替代全词表 softmax。

### 和课堂内容的对应

| 课堂材料 | 对应内容 |
|----------|----------|
| Slides p28 | 公式：$\hat{y} = \text{softmax}(W^T v_c)$，每个词有两个向量 |
| Slides p30 | Softmax 三步：① dot product → ② exponentiation → ③ normalize |
| Notes §3.2 Eq.4 | $P(o\|c) = \frac{\exp(u_o^T v_c)}{\sum_{w \in V} \exp(u_w^T v_c)}$ |
| Notes §3.2 Eq.5 | 交叉熵损失 $L = -\log P(o\|c)$；本例中若观察词为 money，$L = -\log(0.249042) = 1.390$ |

### 容易误解的地方

> [!warning] 注意
> 1. **每个词有两个向量**：v（中心向量）和 u（上下文向量）。它们在训练中会学到不同的东西。最终取词向量时通常只用 v 或取平均。
> 2. **这里的向量是 toy 数据**：真实 word2vec 的向量由大量语料训练得到，维度通常 100-300。这里用 3 维 sin 函数生成的向量只演示计算过程。
> 3. **softmax 分母是瓶颈**：我们只有 6 个词，分母算 6 次 exp。真实 |V| ≈ 50,000+，每步训练都要算 50,000+ 次 exp——这就是 WP05 负采样的动机。
> 4. **概率最高的是中心词自己**：P(banking|banking) = 0.54。这不是 bug——在 toy 向量中中心词和自身上下文向量最对齐。真实语料中，上下文窗口里的词才是「正确答案」。
> 5. **交叉熵损失**：若实际观察到的上下文词是 "money"，损失 = $-\log(0.249042) = 1.390$。训练目标是最小化这个损失。

### 数字来源证明

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T102104Z__t_1b2d033e__skipgram-softmax
  stdout: Labs/L01-word-vectors/outputs/skipgram-softmax-stdout.txt
  checked_values:
    - claim: "u_banking^T v_banking = +0.4136"
      source: "stdout: 'u_banking^T v_banking = 0.4136'"
      status: copied_from_output
    - claim: "Z = 2.799479"
      source: "stdout: 'Step 3: Z = 2.799479'"
      status: copied_from_output
    - claim: "P(banking|banking) = 0.540191"
      source: "stdout: 'P(   banking | banking) = 1.512252 / 2.799479 = 0.540191'"
      status: copied_from_output
    - claim: "P(money|banking) = 0.249042"
      source: "stdout: 'P(     money | banking) = 0.697188 / 2.799479 = 0.249042'"
      status: copied_from_output
    - claim: "P(into|banking) = 0.013730"
      source: "stdout: 'P(      into | banking) = 0.038438 / 2.799479 = 0.013730'"
      status: copied_from_output
    - claim: "sum = 1.000000"
      source: "stdout: 'sum = 1.000000'"
      status: copied_from_output
    - claim: "ranking: banking > money > crisis > turning > problems > into"
      source: "stdout: ranking section lines 52-57"
      status: copied_from_output
```
