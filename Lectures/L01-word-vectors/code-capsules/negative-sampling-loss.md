## negative-sampling-loss — 负采样目标函数 vs 全 Softmax {#negative-sampling-loss}

> **Waypoint**: WP05（对应 WP04-WP05 的 Objective / Gradients / Negative Sampling）
>
> **官方锚点**: Notes §3.5 Eq.14-15（SGNS objective）; R02 paper Section 3
>
> **为什么不能只看文字**: Notes §3.5 给出了 SGNS 公式但没有解释为什么 logistic 近似有效；需要实际对比两种 loss 的计算和梯度行为

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/negative-sampling-loss.ipynb)

### 这段代码在看什么

Word2Vec 训练时，[[Lectures/L01-word-vectors/00-concept-glossary#softmax|softmax]] 的分母要遍历整个词表（O(|V|)），当词表有几十万词时非常慢。[[Lectures/L01-word-vectors/00-concept-glossary#negative-sampling|负采样]]（SGNS）把多分类问题变成 k+1 个二分类问题，只需要 O(k) 次计算。

这个 capsule 用 toy 数据（20 词、4 维向量）实际运行两种 loss，让你看到：

1. **全 softmax 的概率分布**：每个词都分到了一些概率，正样本 "dog" 只占 ~6%（随机初始化下）
2. **SGNS 的各项 logistic loss**：正样本一项 + k 个负样本项
3. **计算量对比**：|V|=100,000 时加速 ~20,000 倍
4. **梯度方向图**：正样本拉近、负样本推远

### 运行后先看哪里

- **Part 1 输出**：全 softmax 概率分布 → 注意分母归一化后每个词都有概率
- **Part 2 输出**：SGNS 各项 logistic loss → 正样本 sigma=0.5474，负样本 sigma 各不相同
- **Part 3 输出**：计算量对比表 → O(|V|) vs O(k) 的差距
- **图表**：左边是梯度方向示意（绿色=拉近，红/橙/紫=推远，蓝色=总梯度），右边是 loss 柱状图

![负采样梯度方向与 loss 对比](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-174103.png)

*图：左边 2D 示意 SGNS 梯度方向——正样本 (dog) 梯度把 center vector 拉向 positive context vector，负样本 (car/tree/king) 梯度把 center vector 推离各 negative context vector。右边对比全 softmax 和 SGNS 的 loss 值。*

### 输出怎么解释

| 指标 | 值 | 来源 |
|------|------|------|
| 全 softmax 损失 J_full | 2.7730 | stdout: `-log P('dog'|'cat') = 2.7730` |
| SGNS 损失 J_sgns | 4.0589 | stdout: `J_sgns = 0.6025 + 0.8763 + 0.5216 + 0.8549 + 0.5950 + 0.6086 = 4.0589` |
| 正样本 sigma(u_o^T v_c) | 0.5474 | stdout: `sigma(u_o^T v_c) = 0.5474` |
| 负样本数 k | 5 | 代码设置 |
| 加速比 (|V|=100,000) | ~20,000x | stdout: `加速比 (|V|=100000, k=5): ~20000x` |

**注意**：SGNS loss (4.0589) 比全 softmax loss (2.7730) 大，这是正常的——它们是不同目标的 loss，不能直接比绝对值。全 softmax 最小化的是 -log P(o|c)（多分类交叉熵），SGNS 最小化的是 k+1 个二分类 logistic loss 之和。

### 容易误解的地方

- **sigma 不是 softmax**：`sigma(x) = 1/(1+exp(-x))` 是 sigmoid/logistic 函数，输出 0-1 之间的标量；softmax 是把一组分数归一化成概率分布
- **负采样不是 softmax 的"近似"**：它把多分类问题重新定义成了 k+1 个二分类问题（正样本 vs 每个负样本）
- **噪声分布 P_n(w)**：实践中用 unigram^0.75（高频词被适度压低），不是均匀分布。本 capsule 为简化用了均匀采样
- **loss 绝对值不可比**：全 softmax loss 和 SGNS loss 是不同目标函数，不能直接比大小

### 和课堂概念的对应

| 课堂概念 | 代码中的体现 |
|---------|------------|
| Notes §3.5 Eq.14 | Part 2 的 `J_sgns = -log sigma(u_o^T v_c) - sum log sigma(-u_w^T v_c)` |
| Notes §3.5 Eq.15 | sigma 函数实现 `1/(1+exp(-x))` |
| 全 softmax 效率问题 | Part 1 vs Part 3 的 O(\|V\|) vs O(k) 对比 |
| 梯度直觉 | Part 4 的箭头图：正拉负推 |
| R02 paper Section 3 | 负样本采样机制和 noise distribution |

### 相关文件

- 脚本: `Labs/L01-word-vectors/negative-sampling-loss.py`
- Notebook: `Labs/L01-word-vectors/negative-sampling-loss.ipynb`
- 输出: `Labs/L01-word-vectors/outputs/negative-sampling-loss-*.png/.json/.txt`
- Run-log: `Labs/L01-word-vectors/run-log.md`

```yaml
numeric_provenance:
  run_log: Labs/L01-word-vectors/run-log.md#run_id 20260610T094508Z__t_87d53a54__negative-sampling-loss
  stdout: Labs/L01-word-vectors/outputs/negative-sampling-loss-stdout.txt
  checked_values:
    - claim: "全 softmax 损失 J_full = 2.7730"
      source: "stdout line: 全 softmax 损失 J_full = -log P('dog'|'cat') = 2.7730"
      status: copied_from_output
    - claim: "SGNS 总损失 J_sgns = 4.0589"
      source: "stdout line: SGNS 总损失 J_sgns = 0.6025 + 0.8763 + 0.5216 + 0.8549 + 0.5950 + 0.6086 = 4.0589"
      status: copied_from_output
    - claim: "正样本 sigma(u_o^T v_c) = 0.5474"
      source: "stdout line: sigma(u_o^T v_c) = 0.5474"
      status: copied_from_output
    - claim: "加速比 ~20000x"
      source: "stdout line: 加速比 (|V|=100000, k=5): ~20000x"
      status: copied_from_output
```
