## skipgram-softmax — Skip-gram [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] P(o|c) 概率计算 {#skipgram-softmax}

> [!info] 本 capsule 解释什么
> **Waypoint WP03**：用中心词预测上下文词时，[[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 如何把"相似度分数"变成"概率分布" P(o|c)。
> **官方锚点**：Slides p27-30（objective function, [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]]）；Notes §3.2（Eq.4 [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]]，Eq.5 cross-entropy loss）。

### 为什么不能只看文字？

Slides p28 给出了 [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 公式：

$$P(o|c) = \frac{\exp(u_o^\top v_c)}{\sum_{w \in V} \exp(u_w^\top v_c)}$$

但只看公式，你很难感受到：
1. **分母 Z 要遍历整个词汇表**——当 |V|=50,000 时，每算一个 P(o|c) 要做 50,000 次点积+指数运算
2. **语义相似的词确实得到更高概率**——需要看到具体数字才能建立直觉
3. **三步分解（点积→指数→归一化）**——每步对数值的影响需要可视化

> [!tip] 中文扶手
> 把 [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 想成"考试排名转百分比"：
> 1. **点积** = 原始分数（越高越像）
> 2. **指数** = 把负分转正、拉大差距
> 3. **除以总分** = 变成加起来=100% 的百分比

### 代码：mini vocabulary 上的完整计算

> **运行方式**：
> - 本地：`.venv/bin/python Labs/L01-word-vectors/skipgram-softmax.py`
> - Colab：点击下方链接直接打开

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/Labs/L01-word-vectors/skipgram-softmax.ipynb)

```python
import numpy as np

np.random.seed(42)

# 6 个词的 mini 词汇表，d=4 维向量（toy example）
vocab = ["banking", "money", "river", "bank", "crisis", "water"]
V = len(vocab)
d = 4

# 每个词有两个向量：v_w（center）和 u_w（context）
V_matrix = np.array([
    [ 0.5,  0.8, -0.2,  0.3],   # banking
    [ 0.4,  0.7, -0.1,  0.2],   # money
    [-0.3,  0.1,  0.9,  0.6],   # river
    [ 0.2,  0.5,  0.4,  0.5],   # bank
    [-0.5,  0.6, -0.3,  0.1],   # crisis
    [-0.2,  0.0,  0.8,  0.7],   # water
])

U_matrix = np.array([
    [ 0.6,  0.7, -0.3,  0.2],   # banking
    [ 0.5,  0.8, -0.2,  0.1],   # money
    [-0.4,  0.2,  0.8,  0.5],   # river
    [ 0.3,  0.6,  0.3,  0.4],   # bank
    [-0.6,  0.5, -0.4,  0.0],   # crisis
    [-0.3,  0.1,  0.7,  0.6],   # water
])

# 中心词 = "banking"
v_c = V_matrix[0]

# Step 1: 点积
dot_products = U_matrix @ v_c
# Step 2: 指数
exp_scores = np.exp(dot_products)
# Step 3: 归一化
Z = np.sum(exp_scores)
probs = exp_scores / Z
```

### 真实输出

> [!example] Step 1：点积 u_w^T · v_c
> ```
> u_banking^T · v_banking =  0.980000
> u_money^T   · v_banking =  0.960000
> u_river^T   · v_banking = -0.050000
> u_bank^T    · v_banking =  0.690000
> u_crisis^T  · v_banking =  0.180000
> u_water^T   · v_banking = -0.030000
> ```
> banking 和 money 的点积最高（0.98, 0.96）——因为它们的向量方向最接近。

> [!example] Step 2：指数化
> ```
> exp(0.980000) = 2.664456
> exp(0.960000) = 2.611696
> exp(-0.050000) = 0.951229
> exp(0.690000) = 1.993716
> exp(0.180000) = 1.197217
> exp(-0.030000) = 0.970446
> ```

> [!example] Step 3：归一化（除以 Z）
> ```
> Z = 10.388761
> P(banking|banking) = 0.256475  ████████████
> P(money|banking)   = 0.251396  ████████████
> P(river|banking)   = 0.091563  ████
> P(bank|banking)    = 0.191911  █████████
> P(crisis|banking)  = 0.115242  █████
> P(water|banking)   = 0.093413  ████
> Sum = 1.0000000000
> ```

### 关键发现

> [!tip] 语义相似性 → 更高概率
> 当 c='banking' 时：
> - P(**money**|banking) = **0.251396**（语义相似：金融相关）
> - P(**river**|banking) = **0.091563**（语义不同：自然水体）
> - **比值 = 2.75x**
>
> 这是因为 v_banking 和 u_money 方向接近 → 点积大 → exp 大 → 概率高。

![skipgram-softmax-prob-distribution](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161016.png)
> 不同中心词（banking/river/crisis）的概率分布对比。注意每个中心词的"最高概率词"不同——banking 给 money 最高，river 给 river 自己和 water 最高。

### Softmax 三步可视化

![skipgram-softmax-three-steps](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161019.png)
> 同一个例子（c='banking'）的三步分解：① 点积（原始相似度）→ ② 指数（转正+放大）→ ③ 归一化（÷Z=10.389 得到概率）。

### 计算瓶颈：为什么需要负采样？

> [!warning] 分母 Z 是效率杀手
> Z = Σ_{w∈V} exp(u_w^T v_c) 需要遍历**整个词汇表**。
> - |V|=50,000 时，每步 50,000 次点积
> - T=10M tokens 的语料，一个 epoch = 5×10¹¹ 次运算
>
> 这就是 WP05 **负采样**要解决的问题：用 k 个二分类替代全词表 [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]]，把 O(|V|) 降到 O(k)。

![skipgram-softmax-computation-cost](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161022.png)
> 词汇量 vs 计算量（对数坐标）。|V|=100,000 时，一个 epoch 需要 10¹² 次运算——这在 2013 年是不可接受的。

### 对应 Slides / Notes 位置

| 本 capsule 概念 | Slides | Notes |
|---|---|---|
| 每词两向量 v_w, u_w | p28 上方 | §3.2 开头 |
| [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 公式 | p28 公式 | Eq.4 |
| 交叉熵损失 | p27 | Eq.5 |
| 三步分解 | p30 | — |
| 计算瓶颈 → 负采样动机 | p28 warning | §3.5 开头 |

### 现在应该能说出

1. [[Lectures/L01-word-vectors/00-concept-glossary#skip-gram|skip-gram]] 模型的目标是什么？（用中心词预测上下文词）
2. 为什么每个词需要两个向量？（作中心词和作上下文词时的角色不同）
3. [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 的三步是什么？（点积→指数→归一化）
4. 为什么分母 Z 是计算瓶颈？（要遍历全词表）
5. 这个瓶颈怎么解决？（→ WP05 负采样）

> [!question] 暂停复述
> 不看上面的输出，你能说出 P(money|banking) 和 P(river|banking) 哪个更大、为什么吗？
> 如果说不出来，回去看 Step 1 的点积部分。

---

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T080907Z__t_832bffea__skipgram-softmax
  stdout: Labs/L01-word-vectors/outputs/skipgram-softmax-stdout.txt
  checked_values:
    - claim: "P(money|banking) = 0.251396"
      source: "stdout line 'P(   money | banking) = 0.251396'"
      status: copied_from_output
    - claim: "P(river|banking) = 0.091563"
      source: "stdout line 'P(   river | banking) = 0.091563'"
      status: copied_from_output
    - claim: "Ratio = 2.75x"
      source: "stdout line 'Ratio = 2.75x'"
      status: copied_from_output
    - claim: "Z = 10.388761"
      source: "stdout line 'Partition function Z = ... = 10.388761'"
      status: copied_from_output
    - claim: "dot(banking) = 0.980000"
      source: "stdout line 'u_ banking^T · v_banking = 0.980000'"
      status: copied_from_output
    - claim: "Sum of probabilities = 1.0"
      source: "stdout line 'Sum of all probabilities = 1.0000000000'"
      status: copied_from_output
```
