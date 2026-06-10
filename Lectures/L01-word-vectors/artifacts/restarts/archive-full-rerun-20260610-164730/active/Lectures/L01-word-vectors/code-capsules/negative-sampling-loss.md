## negative-sampling-loss — 负采样目标函数 vs 全 softmax {#negative-sampling-loss}

> [!info] 本 capsule 解决什么问题
> Notes §3.5 给出了 SGNS 公式（Eq.15）但没有解释**为什么 logistic 近似有效**。
> 这个 capsule 通过实际计算对比两种 loss 的值、梯度和效率，让你直观理解：
> 1. 全 [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 需要遍历整个词汇表（配分函数瓶颈）
> 2. 负采样只用 k+1 个二分类就绕过了这个瓶颈
> 3. 两者的正样本梯度形式相同——这是 logistic 近似有效的核心原因

**Waypoint**: WP05 | **Official anchor**: Notes §3.5 (Eq.14-15); R02 paper Section 3

**Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/negative-sampling-loss.ipynb)

---

### 核心公式对比

> [!tip] 中文扶手
> **全 softmax**：要算"这个词在所有词里的概率"→ 分母要加遍整个词汇表（|V| 次 exp）
> **负采样**：只问两个是非题——"(中心词, 上下文词) 是真搭配吗？"和 k 个"(中心词, 随机词) 是真搭配吗？"

| | 全 Softmax (Eq.14) | 负采样 (Eq.15) |
|---|---|---|
| **公式** | $P(c\|o) = \frac{\exp(u_c^\top v_o)}{\sum_w \exp(u_w^\top v_o)}$ | $J = -\log\sigma(u_o^\top v_c) - \sum_{\ell=1}^{k}\log\sigma(-u_\ell^\top v_c)$ |
| **每步计算** | \|V\| 次点积 + exp | k+1 次点积 + sigmoid |
| **梯度更新** | 所有 \|V\| 个输出向量 | 仅 k+1 个输出向量 |
| **复杂度** | O(\|V\| × d) | O(k × d) |

---

### 实际计算对比

> [!example] 运行结果（|V|=10000, d=50）

**全 softmax loss**:
- 配分函数 Z = 7541.361284
- P(context|center) = 0.00008174
- **Softmax loss = 9.411909**
- 需要计算 10000 个 exp()！

**负采样 loss（不同 k 值）**:

| k | NS Loss | 与 softmax 差值 | 点积次数 |
|---|---------|----------------|---------|
| 1 | 1.453606 | -7.9583 | 2 |
| 5 | 4.299113 | -5.1128 | 6 |
| 10 | 7.699720 | -1.7122 | 11 |
| 25 | 18.354336 | +8.9424 | 26 |

> [!warning] NS loss ≠ softmax loss
> 负采样 loss **不是** softmax loss 的近似——它是一个**不同的目标函数**（二分类 vs 多分类）。
> 但最小化 NS loss 会**隐式地**学到相似的向量表示。

---

### 为什么 logistic 近似有效？

> [!tip] 关键洞察：正样本梯度形式相同

**Softmax 正样本梯度**: $\frac{\partial L}{\partial u_o} = (P(c|o) - 1) \cdot v_c$

**NS 正样本梯度**: $\frac{\partial L}{\partial u_o} = (\sigma(u_o^\top v_c) - 1) \cdot v_c$

两者的**方向相同**（都沿 $v_c$ 方向推），**形式相同**（都是 "当前得分的函数 - 1"）。

区别在于：
- Softmax **同时**把所有其他 $u_w$ 稍微推远（通过分母效应）
- NS **只**把 k 个随机负样本推远

> "if we randomly push down a few words at each step, on average, things will work out." — Notes §3.5

![sigmoid 与梯度对比](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161834.png)
*左：σ(x) 和 σ(-x) 分别负责正/负样本的二分类。右：梯度强度——得分越高，正样本推力越小（已经够好了）；得分越低，负样本推力越小（已经够不同了）。*

---

### k 值的选择

![loss vs k](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161831.png)
*左：不同 k 值的 NS loss（±1 std，100 次随机采样）。k 越大方差越小，但 mean loss 也越大（更多负样本项之和）。右：梯度计算效率——softmax 随 |V| 线性增长，NS(k=5) 几乎不变。*

| k | Mean Loss | Std Loss | CV (%) |
|---|-----------|----------|--------|
| 1 | 1.4906 | 0.0374 | 2.51 |
| 5 | 4.2621 | 0.0771 | 1.81 |
| 10 | 7.7275 | 0.1299 | 1.68 |
| 20 | 14.6788 | 0.1684 | 1.15 |
| 50 | 35.4808 | 0.2454 | 0.69 |

> [!tip] 实践建议
> Mikolov et al. (2013) 推荐 **k = 5-20**。
> - k 小（1-5）：快但方差高
> - k 中（5-25）：平衡
> - k 大（50+）：稳定但收益递减

---

### 效率对比

在 |V|=100,000 时：
- Softmax 梯度：**12.538 ms**/步
- NS(k=5) 梯度：**1.586 ms**/步
- **加速比：7.9x**

这个差距随 |V| 增大而线性增长。真实 NLP 任务 |V| 常达百万级，softmax 完全不可行。

![loss landscape](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-161838.png)
*两种 loss 都随向量相似度增加而下降——虽然数值不同，但优化方向一致。*

---

### 代码与运行

- **Python 脚本**: `Labs/L01-word-vectors/negative-sampling-loss.py`
- **Jupyter Notebook**: `Labs/L01-word-vectors/negative-sampling-loss.ipynb`
- **运行命令**: `.venv/bin/python Labs/L01-word-vectors/negative-sampling-loss.py`
- **纯标准库 + numpy + matplotlib**，Colab 无额外安装

> [!question] 暂停复述
> 不看笔记，试着回答：
> 1. 为什么全 softmax 在大词汇表上不可行？（提示：配分函数）
> 2. 负采样的正样本梯度和 softmax 的正样本梯度有什么相同点？
> 3. k=5 和 k=50 各有什么优缺点？
> 想不出来？问 Hermes：*"负采样为什么能用二分类替代多分类？梯度角度解释"*

---

### 术语链接

- [[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] — 归一化指数函数
- [[Lectures/L01-word-vectors/00-concept-glossary#skip-gram|skip-gram]] — 用中心词预测上下文
- [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense vector]] — 低维连续向量

---

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T082213Z__t_45780d20__negative-sampling-loss
  stdout: Labs/L01-word-vectors/outputs/negative-sampling-loss-stdout.txt
  checked_values:
    - claim: "Softmax loss = 9.411909"
      source: "stdout Part 1: 'Softmax loss = -log P(c|o): 9.411909'"
      status: copied_from_output
    - claim: "Partition function Z = 7541.361284"
      source: "stdout Part 1: 'Partition function Z = Σ_w exp(u_w^T v_c): 7541.361284'"
      status: copied_from_output
    - claim: "P(context|center) = 0.00008174"
      source: "stdout Part 1: 'P(context|center) under softmax: 0.00008174'"
      status: copied_from_output
    - claim: "NS loss k=5: 4.299113"
      source: "stdout Part 2: '5 | 4.299113'"
      status: copied_from_output
    - claim: "NS loss k=1: 1.453606"
      source: "stdout Part 2: '1 | 1.453606'"
      status: copied_from_output
    - claim: "Gradient speedup 7.9x at |V|=100K"
      source: "stdout Part 5: '100000 | 12.538 ms | 1.586 ms | 7.9x'"
      status: copied_from_output
    - claim: "k=5 mean loss 4.2621, std 0.0771"
      source: "stdout Part 4: '5 | 4.2621 | 0.0771 | 1.81'"
      status: copied_from_output
```
