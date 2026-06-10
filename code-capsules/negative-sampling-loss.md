## negative-sampling-loss — 负采样目标函数 vs 全 Softmax {#negative-sampling-loss}

> [!info] 这个 Capsule 在看什么
> **概念**：[[Lectures/L01-word-vectors/00-concept-glossary#skip-gram|Skip-gram]] 模型用 [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 计算 P(o|c) 时，分母需要遍历整个词表（|V| 个词），当词表有 10 万个词时，每一步训练都要算 10 万次 exp——这就是 **softmax 瓶颈**。负采样（Negative Sampling）用 logistic（sigmoid）二分类替代全词表归一化，只需要 k+1 个项而不是 |V| 个。
>
> **为什么不能只靠文字**：Notes §3.5 给出了 SGNS 公式 (Eq.15) 但没解释为什么 logistic 近似有效——它把问题从「预测哪个词」重新定义为「区分真假词对」，这个转换只有实际计算两种 loss 的数值和梯度才能理解。
>
> **官方锚点**：Notes §3.5 (Eq.14-15, SGNS objective); R02 paper Section 3

### 运行方式

**Colab 打开**（推荐）：[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/negative-sampling-loss.ipynb)

**本地运行**：
```bash
cd /workspace/cs224n-study
.venv/bin/python Labs/L01-word-vectors/negative-sampling-loss.py
```

### 这段代码在做什么

1. 用 6 个词的 toy 词表（和 skipgram-softmax capsule 一致）构建中心词/上下文向量
2. 计算全 [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] loss：$J = -u_o^T v_c + \log \sum_w \exp(u_w^T v_c)$，需要 |V| 次点积
3. 计算负采样 loss：$J_{NS} = -\log \sigma(u_o^T v_c) - \sum_{i=1}^{k} \log \sigma(-u_{w_i}^T v_c)$，只需 k+1 次点积
4. 对比不同 k 值的 loss、计算量、梯度行为
5. 展示真实词表大小（1K~100K）下的加速比

### 运行后先看哪里

> [!tip] 输出解读
> 1. **Softmax loss = 1.390153**：P(money|banking) = 0.249037，模型给目标词的概率只有 25%
> 2. **NS loss (k=5) = 1.564948**：比 softmax 略高，因为负样本贡献了额外的 loss 项
> 3. **计算量对比**：|V|=6 时两者都需要 6 次点积（k=5 时），看不出优势
> 4. **真实加速**：|V|=100,000, k=5 时，softmax 需要 100,000 次点积，NS 只需 6 次——快 16,667 倍

### 关键输出

**Softmax 概率分布**（center = "banking"）：

```
P(   banking|banking) = 0.540196  #####################
P(     money|banking) = 0.249037  ######### <-- 目标词
P(    crisis|banking) = 0.115551  ####
P(   turning|banking) = 0.054704  ##
P(  problems|banking) = 0.026782  #
P(      into|banking) = 0.013730  
```

**Loss 对比**（k=5）：

| 指标 | Softmax | NS (k=5) |
|------|---------|----------|
| Loss | 1.390153 | 1.564948 |
| 点积次数 | 6 | 6 |
| 梯度 \|\|dJ/dv_c\|\| | 0.068661 | 0.359927 |

**不同 k 值的效果**：

| k | NS Loss | 点积数 | 负样本 |
|---|---------|--------|--------|
| 1 | 1.032168 | 2 | turning |
| 2 | 1.104467 | 3 | turning, problems |
| 5 | 1.564948 | 6 | turning, problems, crisis, into, turning |
| 10 | 2.377998 | 11 | (10 个负样本) |
| 20 | 3.588154 | 21 | (20 个负样本) |

**为什么 Logistic 近似有效**：

```
正样本 (banking, money):
  sigmoid(u_money^T v_banking) = sigmoid(-0.3607) = 0.410789
  目标: -> 1.0

负样本 (k=5):
  sigmoid(u_turning^T v_banking)  = 0.132806  -> 0.0 ✓
  sigmoid(u_problems^T v_banking) = 0.069747  -> 0.0 ✓
  sigmoid(u_crisis^T v_banking)   = 0.244421  -> 0.0 ✓
  sigmoid(u_into^T v_banking)     = 0.037015  -> 0.0 ✓
```

负采样把「多分类」转化为「二分类」——不需要精确归一化，只需区分真假词对。

**真实场景加速**：

| \|V\| | Softmax 点积 | NS 点积 (k=5) | 加速比 |
|-------|-------------|--------------|--------|
| 1,000 | 1,000 | 6 | 167x |
| 10,000 | 10,000 | 6 | 1,667x |
| 50,000 | 50,000 | 6 | 8,333x |
| 100,000 | 100,000 | 6 | 16,667x |

### Loss 与计算量对比图

![Loss 与计算量对比](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181803.png)

> [!tip] 读图指南
> - **左图**（Loss）：红色柱是 softmax loss (1.390)，蓝色柱是不同 k 的 NS loss。k 增大时 NS loss 增大（更多负样本项贡献），但这不意味着更差——NS 的 loss 定义本身就包含更多项
> - **右图**（计算量）：红色柱是 softmax（|V|=6 次点积），绿色柱是 NS（k+1 次）。|V|=6 时差异不大，但真实词表差异巨大

### 真实场景 Scaling 图

![Scaling 对比](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181807.png)

> [!tip] 读图指南
> - **蓝色柱**：softmax 需要的点积数 = |V|，随词表线性增长
> - **红色折线**：NS (k=5) 的加速比，|V|=100K 时达到 16,667x
> - **关键结论**：这就是为什么实际 Word2Vec 训练都用负采样而不是 softmax

### 梯度分析图

![梯度分析](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181810.png)

> [!tip] 读图指南
> - **左图**（梯度幅值）：softmax 梯度范数 0.069，NS (k=5) 梯度范数 0.360——NS 梯度更大，因为它是随机近似，方差更高
> - **右图**（softmax 概率分布）：banking 自身概率最高 (0.540)，目标词 money 排第二 (0.249)——toy 向量的特性
> - **注意**：梯度余弦相似度 = -0.919，说明 NS 和 softmax 的梯度方向差异很大——这是 toy 数据和小 k 的特性，实际训练中随着向量学习到位，方向会趋于一致

### 和课堂内容的对应

| 课堂材料 | 对应内容 |
|----------|----------|
| Notes §3.5 | "the objective is to use logistic regression to maximize the probability of the true pair..." |
| Notes Eq.14 | Softmax 分母 $\sum_w \exp(u_w^T v_c)$ 的归一化问题 |
| Notes Eq.15 | SGNS 目标函数：$J_{NS} = -\log\sigma(u_o^T v_c) - \sum \log\sigma(-u_{w_i}^T v_c)$ |
| R02 Section 3 | 负采样分布 $P(w)$ 的选择（unigram$^{0.75}$）；k 的经验值 |
| Slides p27-30 | Softmax 目标函数前置知识 |

### 容易误解的地方

> [!warning] 注意
> 1. **NS loss 和 softmax loss 不直接可比**：它们的 loss 定义不同（NS 包含 k 个额外的负样本项），不能简单说谁「更好」
> 2. **k 不是越大越好**：k 太大会增加计算量，且当 k→|V| 时退化成 softmax。R02 论文建议小数据集 k=5，大数据集 k=20
> 3. **梯度方向差异大是正常的**：NS 是 softmax 梯度的无偏但高方差的随机近似。单次比较的余弦相似度 = -0.919，但期望方向是正确的
> 4. **负采样分布 $P(w)$ 很重要**：本例用均匀分布做演示，实际 R02 论文用 unigram$^{0.75}$——让低频词有更多机会被选为负样本
> 5. **本例 |V|=6 时 k=5 的点积数 = 6 = |V|**：看不出计算优势。真正的优势在 |V|=100K 时才明显

### 数字来源证明

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T102037Z__t_9ab44084__negative-sampling-loss
  stdout: Labs/L01-word-vectors/outputs/negative-sampling-loss-stdout.txt
  checked_values:
    - claim: "Softmax loss = 1.390153"
      source: "stdout: 'Softmax loss = 1.390153'"
      status: copied_from_output
    - claim: "P(money|banking) = 0.249037"
      source: "stdout: 'P(     money|banking) = 0.249037'"
      status: copied_from_output
    - claim: "NS loss (k=5) = 1.564948"
      source: "stdout: 'Total NS loss = 1.564948'"
      status: copied_from_output
    - claim: "NS loss (k=2) = 1.104467"
      source: "stdout: 'Total NS loss = 1.104467'"
      status: copied_from_output
    - claim: "NS loss (k=10) = 2.377998"
      source: "stdout: 'Total NS loss = 2.377998'"
      status: copied_from_output
    - claim: "sigmoid(u_money^T v_banking) = 0.410789"
      source: "stdout: 'sigmoid(u_money^T v_banking) = sigmoid(-0.3607) = 0.410789'"
      status: copied_from_output
    - claim: "Gradient ||dJ/dv_c|| softmax = 0.068661"
      source: "stdout: 'Gradient ||dJ/dv_c||  0.068661'"
      status: copied_from_output
    - claim: "Gradient ||dJ/dv_c|| NS k=5 = 0.359927"
      source: "stdout: 'Gradient ||dJ/dv_c||  0.359927'"
      status: copied_from_output
    - claim: "Gradient cosine similarity = -0.919196"
      source: "stdout: 'Gradient cosine similarity  -0.919196'"
      status: copied_from_output
    - claim: "|V|=100,000 speedup = 16,667x"
      source: "stdout: '100,000  100,000  6  16667x'"
      status: copied_from_output
```
