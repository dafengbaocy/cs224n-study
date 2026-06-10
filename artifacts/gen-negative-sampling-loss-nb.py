#!/usr/bin/env python3
"""Generate the negative-sampling-loss.ipynb notebook with Chinese teaching content."""
import json

cells = []

def md(source):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": source.split("\n")})

def code(source):
    cells.append({"cell_type": "code", "metadata": {}, "source": source.split("\n"),
                  "execution_count": None, "outputs": []})

# ============================================================
# Title and intro
# ============================================================
md("""# 负采样目标函数 vs 全 Softmax — CS224N L01 WP05

## 这段代码在看什么

本 notebook 对应 **CS224N Lecture 01 Waypoint 05**：负采样（Negative Sampling）目标函数。

**核心问题**：Skip-gram 模型用 [[softmax]] 计算 P(o|c) 时，分母需要遍历整个词表（|V| 个词），当词表有 10 万个词时，每一步训练都要算 10 万次 exp——太慢了。

**负采样的解决方案**：不再做全词表归一化，而是把问题转化为 **二分类**——「这个词对是真实的上下文，还是随机噪声？」用 logistic（sigmoid）函数代替 softmax，只需要计算 k+1 个项（k 个负样本 + 1 个正样本），而不是 |V| 个。

**官方锚点**：Notes §3.5 (Eq.14-15, SGNS objective); R02 paper Section 3""")

# ============================================================
# Setup
# ============================================================
md("""## 1. 准备工作：toy 词表和向量

我们用 6 个词的小词表做演示（和 skipgram-softmax capsule 一致）。实际词表通常有数万到数十万词。""")

code("""import math
import json
import random

# 词表和向量维度
VOCAB = ["banking", "money", "crisis", "turning", "problems", "into"]
DIM = 3

# 确定性生成 toy 向量（可复现）
def make_vectors(vocab, dim, seed):
    vectors = {}
    for i, word in enumerate(vocab):
        vec = [round(math.sin(seed * (i+1) * 7.3 + (d+1) * 13.7) * 2.0, 4) for d in range(dim)]
        vectors[word] = vec
    return vectors

V = make_vectors(VOCAB, DIM, 42)   # 中心词向量
U = make_vectors(VOCAB, DIM, 99)   # 上下文词向量

def dot(a, b):
    return sum(ai*bi for ai, bi in zip(a, b))

def sigmoid(x):
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    else:
        ez = math.exp(x)
        return ez / (1.0 + ez)

print(f"词表: {VOCAB}")
print(f"|V| = {len(VOCAB)}, d = {DIM}")
print()
for w in VOCAB:
    print(f"  v_{w} = {V[w]}")
    print(f"  u_{w} = {U[w]}")""")

# ============================================================
# Softmax loss
# ============================================================
md("""## 2. 全 Softmax Loss（Notes Eq.14）

**公式**：

$$J_{\\text{softmax}} = -\\log P(o|c) = -u_o^T v_c + \\log \\sum_{w \\in V} \\exp(u_w^T v_c)$$

**关键**：分母的 $\\sum_w$ 要求对词表中**每一个词**都计算 $\\exp(u_w^T v_c)$。

这就是计算瓶颈——词表越大，每一步训练越慢。""")

code("""center = "banking"
output = "money"

print(f"中心词 c = '{center}', 上下文词 o = '{output}'")
print()

# 计算所有词和中心词的点积
print("Step 1: 计算所有 u_w^T v_c：")
scores = {}
for w in VOCAB:
    s = dot(U[w], V[center])
    scores[w] = round(s, 4)
    marker = " <-- 目标词" if w == output else ""
    print(f"  u_{w}^T v_{center} = {s:.4f}{marker}")
print()

# Softmax 概率
print("Step 2: Softmax 归一化 -> P(w|c)：")
max_s = max(scores.values())
exp_scores = {w: math.exp(s - max_s) for w, s in scores.items()}  # log-sum-exp trick
total_exp = sum(exp_scores.values())
probs = {w: e / total_exp for w, e in exp_scores.items()}

for w in VOCAB:
    bar = "#" * int(probs[w] * 40)
    marker = " <-- 目标词" if w == output else ""
    print(f"  P({w:>10}|{center}) = {probs[w]:.6f}  {bar}{marker}")
print()

# Loss
softmax_loss = -math.log(probs[output])
print(f"Softmax loss = -log(P('{output}'|'{center}')) = -log({probs[output]:.6f}) = {softmax_loss:.6f}")
print(f"需要计算的点积数: {len(VOCAB)} (= |V|)")""")

# ============================================================
# Negative sampling loss
# ============================================================
md("""## 3. 负采样 Loss（Notes Eq.15 / R02 Section 3）

**公式**：

$$J_{\\text{NS}} = -\\log \\sigma(u_o^T v_c) - \\sum_{i=1}^{k} \\mathbb{E}_{w_i \\sim P(w)} [\\log \\sigma(-u_{w_i}^T v_c)]$$

**直觉**：
- **正样本部分**：推高 $\\sigma(u_o^T v_c)$，让模型认为 (banking, money) 是真实词对
- **负样本部分**：推低 $\\sigma(u_{w_i}^T v_c)$，让模型认为 (banking, 随机词) 不是真实词对

**只需要 k+1 个点积**，而不是 |V| 个！""")

code("""def negative_sampling_loss(U, V, center, output, vocab, k, rng):
    \"\"\"负采样 loss 计算\"\"\"
    vc = V[center]
    uo = U[output]

    # 正样本: -log(sigmoid(u_o^T v_c))
    pos_score = dot(uo, vc)
    pos_loss = -math.log(sigmoid(pos_score) + 1e-10)

    # 采样 k 个负样本（排除目标词）
    candidates = [w for w in vocab if w != output]
    neg_words = [rng.choice(candidates) for _ in range(k)]

    # 负样本 loss: sum -log(sigmoid(-u_w^T v_c))
    neg_loss = 0.0
    for nw in neg_words:
        neg_score = dot(U[nw], vc)
        neg_loss += -math.log(sigmoid(-neg_score) + 1e-10)

    return pos_loss + neg_loss, neg_words, pos_loss, neg_loss

rng = random.Random(2024)

for k in [2, 5, 10]:
    rng_k = random.Random(2024)
    ns_loss, neg_words, pos_l, neg_l = negative_sampling_loss(U, V, center, output, VOCAB, k, rng_k)
    print(f"--- k = {k} ---")
    print(f"  正样本 loss: -log(sigmoid(u_o^T v_c)) = {pos_l:.6f}")
    print(f"  负样本 loss: sum -log(sigmoid(-u_w^T v_c)) = {neg_l:.6f}")
    print(f"  总 NS loss = {ns_loss:.6f}")
    print(f"  负样本词: {neg_words}")
    print(f"  需要点积数: {1 + k} (= 1 + k)")
    print()""")

# ============================================================
# Comparison
# ============================================================
md("""## 4. 直接对比：Softmax vs 负采样 (k=5)

> ### 运行后先看哪里
> 1. **Loss 值**：两者不一定相等——NS 是 softmax 的随机近似，不是精确替代
> 2. **点积数**：这才是关键差异——NS 只需要 k+1 次计算
> 3. **梯度方向**：余弦相似度衡量两者更新方向是否一致""")

code("""# 详细对比 k=5
rng5 = random.Random(2024)
ns_loss_5, neg_words_5, pos_l_5, neg_l_5 = negative_sampling_loss(U, V, center, output, VOCAB, 5, rng5)

print(f"{'指标':<35} {'Softmax':>12} {'NS (k=5)':>12}")
print(f"{'-'*35} {'-'*12} {'-'*12}")
print(f"{'Loss':<35} {softmax_loss:>12.6f} {ns_loss_5:>12.6f}")
print(f"{'点积次数':<35} {len(VOCAB):>12} {6:>12}")
print(f"{'计算比例 (NS/Softmax)':<35} {'':>12} {6/len(VOCAB):>11.0%}")
print()
print("注意：本例 |V|=6 太小，看不出计算优势。")
print("真正的优势在大词表上——见后面的 scaling 分析。")""")

# ============================================================
# Why logistic works
# ============================================================
md("""## 5. 为什么 Logistic 近似有效？

> ### 输出怎么解释
> 负采样把「预测哪个词」变成了「区分真假词对」——这是 **噪声对比估计（NCE）** 的核心思想。
>
> - 正样本：让 $\\sigma(u_o^T v_c) \\to 1.0$（「这是真词对！」）
> - 负样本：让 $\\sigma(u_{w_i}^T v_c) \\to 0.0$（「这是噪声！」）
>
> 不需要知道每个词的精确概率，只需要能区分真假就够了。""")

code("""print("负采样把问题转化为二分类：")
print()

# 正样本
pos_sig = sigmoid(dot(U[output], V[center]))
print(f"  正样本 (banking, money):")
print(f"    sigmoid(u_money^T v_banking) = sigmoid({dot(U[output], V[center]):.4f}) = {pos_sig:.6f}")
print(f"    目标: -> 1.0 (当前还差得远)")
print()

# 负样本
print(f"  负样本 (k=5):")
for nw in neg_words_5:
    neg_sig = sigmoid(dot(U[nw], V[center]))
    print(f"    sigmoid(u_{nw}^T v_banking) = sigmoid({dot(U[nw], V[center]):.4f}) = {neg_sig:.6f}")
print(f"    目标: -> 0.0 (已经比较低了，因为 toy 向量的点积本身偏负)")
print()
print("关键洞察：")
print("  Softmax 要求精确归一化（所有概率之和=1）-> 必须遍历全词表")
print("  负采样只要求区分真假 -> 只需看正样本 + k 个负样本")
print("  这是 NCE (Noise Contrastive Estimation) 的思想")""")

# ============================================================
# Effect of k
# ============================================================
md("""## 6. 负采样数 k 的影响

> ### 容易误解的地方
> 1. **k 不是越大越好**：k 太大会增加计算量，而且当 k 接近 |V| 时，负采样就退化成 softmax 了
> 2. **经验值 k=5~20**：R02 论文建议小数据集 k=5，大数据集 k=20
> 3. **k 影响梯度方差**：k 越大，负样本的期望估计越准确，梯度方差越小""")

code("""k_values = [1, 2, 5, 10, 20, 50]
print(f"{'k':>4} {'NS Loss':>10} {'点积数':>8} {'负样本数':>8}")
print(f"{'-'*4} {'-'*10} {'-'*8} {'-'*8}")

for k in k_values:
    rng_k = random.Random(2024)
    ns_l, nw, _, _ = negative_sampling_loss(U, V, center, output, VOCAB, k, rng_k)
    print(f"{k:>4} {ns_l:>10.6f} {1+k:>8} {k:>8}")

print()
print(f"Softmax loss (参考): {softmax_loss:.6f}")
print(f"Softmax 点积数: {len(VOCAB)}")
print()
print("观察：k 增大时 loss 增大（因为更多负样本贡献了更多 -log(sigmoid(-...)) 项）")
print("但每增加一个负样本的计算量是 O(1)，而 softmax 需要 O(|V|)。")""")

# ============================================================
# Real-world scaling
# ============================================================
md("""## 7. 真实场景的计算优势

> ### 和课堂内容的对应
> | 课堂材料 | 对应内容 |
> |----------|----------|
> | Notes §3.5 | "the objective is to use logistic regression..." |
> | Notes Eq.14 | softmax 分母的归一化问题 |
> | Notes Eq.15 | SGNS 目标函数 |
> | R02 Section 3 | 负采样分布 P(w) 的选择 |

这就是为什么实际训练 Word2Vec 时都用负采样而不是 softmax——在 |V|=100,000 时，每步训练快了 **16,667 倍**！""")

code("""# 真实词表大小下的计算对比
vocab_sizes = [1000, 10000, 50000, 100000]
k = 5

print(f"{'|V|':>10} {'Softmax 点积':>15} {'NS 点积 (k=5)':>15} {'加速比':>10}")
print(f"{'-'*10} {'-'*15} {'-'*15} {'-'*10}")
for vs in vocab_sizes:
    speedup = vs / (k + 1)
    print(f"{vs:>10,} {vs:>15,} {k+1:>15} {speedup:>9,.0f}x")

print()
print(f"|V|=100,000 时，softmax 每步需要 100,000 次点积")
print(f"负采样 (k=5) 只需要 6 次——快了 {100000//6:,} 倍！")""")

# ============================================================
# Plot
# ============================================================
md("""## 8. 可视化

> ### 输出怎么解释
> - **左图**：不同 k 值下 NS loss 和 softmax loss 的对比。注意 NS loss 随 k 增大而增大（更多负样本项）
> - **右图**：点积次数对比。|V|=6 时差异不大，但真实词表（10万+）差异巨大""")

code("""import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左图: Loss 对比
k_vals = [1, 2, 5, 10, 20]
ns_losses_plot = []
for k in k_vals:
    rng_k = random.Random(2024)
    ns_l, _, _, _ = negative_sampling_loss(U, V, center, output, VOCAB, k, rng_k)
    ns_losses_plot.append(ns_l)

x = np.arange(len(k_vals) + 1)
bars_data = [softmax_loss] + ns_losses_plot
colors = ['#e74c3c'] + ['#3498db'] * len(k_vals)
labels = ['Softmax\\n(full)'] + [f'NS\\nk={k}' for k in k_vals]

bars = axes[0].bar(x, bars_data, 0.6, color=colors, alpha=0.85, edgecolor='white')
axes[0].set_xticks(x)
axes[0].set_xticklabels(labels, fontsize=9)
axes[0].set_ylabel('Loss value')
axes[0].set_title('Loss: Softmax vs Negative Sampling')
for bar, val in zip(bars, bars_data):
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.03,
                f'{val:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
axes[0].set_ylim(0, max(bars_data) * 1.25)

# 右图: 点积次数
dots_data = [len(VOCAB)] + [k+1 for k in k_vals]
colors2 = ['#e74c3c'] + ['#2ecc71'] * len(k_vals)
bars2 = axes[1].bar(x, dots_data, 0.6, color=colors2, alpha=0.85, edgecolor='white')
axes[1].set_xticks(x)
axes[1].set_xticklabels(labels, fontsize=9)
axes[1].set_ylabel('Dot products needed')
axes[1].set_title('Computation Cost: Dot Products per Step')
for bar, val in zip(bars2, dots_data):
    axes[1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
                f'{val}', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('negative-sampling-loss-comparison.png', dpi=150, bbox_inches='tight')
plt.show()
print("图表已保存: negative-sampling-loss-comparison.png")""")

# ============================================================
# Summary
# ============================================================
md("""## 9. 总结

> ### 和本讲哪个 waypoint 对应
> 本 notebook 对应 **WP05: 负采样 (Skip-gram Negative Sampling)**
>
> | 概念 | 对应公式/材料 |
> |------|--------------|
> | Softmax 瓶颈 | Notes Eq.14, 分母 $\\sum_w \\exp(u_w^T v_c)$ 需要 O(|V|) |
> | 负采样目标 | Notes Eq.15, $J_{NS} = -\\log\\sigma(u_o^T v_c) - \\sum \\log\\sigma(-u_{w_i}^T v_c)$ |
> | NCE 思想 | R02 Section 3, 用二分类代替多分类 |
> | k 的选择 | R02 经验: 小数据集 k=5, 大数据集 k=20 |

### 关键收获

1. **Softmax 的计算瓶颈**：分母需要遍历全词表，|V|=100K 时每步 10 万次运算
2. **负采样的解决方案**：用 k+1 个 logistic 项代替 |V| 个 softmax 项
3. **为什么有效**：把多分类问题转化为二分类（真词对 vs 噪声），不需要精确归一化
4. **k 的权衡**：k 太小→梯度方差大；k 太大→计算量增加，接近 softmax
5. **实际加速**：|V|=100K, k=5 时，每步训练快 16,667 倍""")

# Build notebook
nb = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.13.5"
        },
        "colab": {
            "provenance": [],
            "name": "negative-sampling-loss.ipynb"
        }
    },
    "cells": cells
}

# Fix source fields - each should be a list of lines with \n
for cell in nb["cells"]:
    src = cell["source"]
    if isinstance(src, str):
        lines = src.split("\n")
        cell["source"] = [line + "\n" for line in lines[:-1]] + [lines[-1]] if lines else []

out_path = "/workspace/cs224n-study/Labs/L01-word-vectors/negative-sampling-loss.ipynb"
with open(out_path, "w") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print(f"Notebook written: {out_path}")
