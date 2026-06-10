## negative-sampling-loss — 负采样目标函数 vs 全 Softmax {#negative-sampling-loss}

> [!info] 这个 Capsule 在看什么
> **概念**：[[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 在每一步需要遍历整个词汇表计算归一化常数（partition function），复杂度 O(|V|)；负采样（SGNS）用 k 个随机负例替代分母，把多分类变成 k+1 个二分类，复杂度降到 O(k)。
>
> **为什么不能只靠文字**：Notes §3.5 Eq.14-15 给出了 SGNS 公式但没有解释为什么 logistic 近似有效；需要实际对比两种 loss 的计算和梯度行为，才能理解负采样如何在保持「拉近正样本、推远负样本」梯度方向的同时实现 20,000x 加速。
>
> **官方锚点**：Notes §3.5 (Eq.14-15, SGNS objective); R02 paper Section 3

### 运行方式

**Colab 打开**（推荐）：[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/negative-sampling-loss.ipynb)

**本地运行**：
```bash
cd /workspace/cs224n-study/Labs/L01-word-vectors
/workspace/cs224n-study/.venv/bin/python negative-sampling-loss.py
```

### 这段代码在做什么

1. 用 10 个词构建小型词汇表，随机初始化 center/outside 向量矩阵
2. 对 (bank, river) 词对，分别计算[[Lectures/L01-word-vectors/00-concept-glossary#softmax|全 softmax]] 损失和负采样损失
3. 对比两种方法的计算量、损失值、梯度方向
4. 训练模拟：展示正样本 cosine 上升（拉近）、负样本 cosine 下降（推远）

### 运行后先看哪里

> [!tip] 输出解读
> 1. **Part A 概率表**：全 softmax 给每个词分配的概率几乎一样（~10%），损失 = 2.294274
> 2. **Part B sigmoid 值**：所有 σ(-u^T v) 接近 0.5——初始时模型无法区分正负
> 3. **Part C 对比**：|V|=10 时加速 2x；|V|=100,000 时加速 20,000x
> 4. **Part E 训练曲线**：正样本 cos 0.7617→0.9438（拉近），负样本 cos -0.0221→-0.6993（推远）

### 关键输出

**损失对比**：

| Method | Loss | Terms | Complexity |
|--------|------|-------|------------|
| Full Softmax | 2.294274 | 10 | O(\|V\|)=O(10) |
| Neg. Sampling | 4.152770 | 6 | O(k)=O(6) |

> [!warning] 损失值不能直接比较
> 负采样损失（4.152770）大于全 softmax（2.294274）——不是 bug。两个损失函数定义不同。

**训练模拟**（100 步，lr=0.05, k=5）：

| Step | cos(pos) | avg cos(neg) |
|------|----------|-------------|
| 0 | 0.7617 | -0.0221 |
| 20 | 0.8342 | -0.1985 |
| 40 | 0.8796 | -0.3621 |
| 60 | 0.9093 | -0.5046 |
| 80 | 0.9295 | -0.6166 |
| 100 | 0.9438 | -0.6993 |

### 对比图

![负采样 vs 全 Softmax 对比图](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181751.png)

> [!tip] 读图指南
> - **左图**（Softmax 概率）：红色 = 正样本 river，蓝色 = 负样本，灰色 = 其他。初始概率接近均匀（~10%）。
> - **中图**（损失分解）：Full SM = 全 softmax；SGNS pos/neg/total = 负采样各部分。
> - **右图**（训练动态）：红线上升 = 正样本拉近；蓝线下降 = 负样本推远。

### 梯度方向图

![梯度方向对比](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-181756.png)

> [!tip] 读图指南
> - **左图**（梯度）：softmax 和 SGNS 梯度在各维度的值不同，方向大致一致。
> - **右图**（更新方向 = -梯度）：都指向「让 v_c 靠近 u_pos、远离 u_neg」的方向。
> - **关键区别**：softmax 涉及全部 10 个 outside 向量；SGNS 只涉及 6 个。

### 和课堂内容的对应

| 课堂材料 | 对应内容 |
|----------|----------|
| Notes §3.5 Eq.14 | softmax 分子（affinity）和分母（partition function） |
| Notes §3.5 Eq.15 | SGNS = log σ(u_o^T v_c) + Σ log σ(-u_ℓ^T v_c) |
| Notes §3.4 | "observed minus expected" 梯度直觉 |
| R02 Section 3 | 负采样机制和噪声分布 |

### 容易误解的地方

> [!warning] 注意
> 1. **负采样不是近似 softmax**——它是完全不同的二分类目标
> 2. **σ(x) 是 sigmoid，不是 softmax**
> 3. **损失值不能直接比较**：定义不同，绝对值大小无意义
> 4. **SGNS 梯度只更新 k+2 个向量**，全 softmax 更新所有 |V| 个
> 5. **本 capsule 用 toy 数据**：|V|=10, d=4；实际用 |V|≈100k, d≈300

### 数字来源证明

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T102241Z__t_d42c43e7__negative-sampling-loss
  stdout: Labs/L01-word-vectors/outputs/negative-sampling-loss-stdout.txt
  checked_values:
    - claim: "Full Softmax loss = 2.294274"
      source: "stdout: 'Full Softmax loss = -log P(river|bank) = -log(0.100835) = 2.294274'"
      status: copied_from_output
    - claim: "SGNS loss = 4.152770"
      source: "stdout: 'SGNS loss = 0.688336 + 3.464433 = 4.152770'"
      status: copied_from_output
    - claim: "Positive cos: 0.7617 -> 0.9438"
      source: "stdout: 'Positive cos: 0.7617 -> 0.9438 (UP (closer))'"
      status: copied_from_output
    - claim: "Negative avg cos: -0.0221 -> -0.6993"
      source: "stdout: 'Negative avg cos: -0.0221 -> -0.6993 (DOWN (apart))'"
      status: copied_from_output
```
