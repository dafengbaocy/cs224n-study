#!/usr/bin/env python3
"""Generate skipgram-softmax.ipynb from the .py script."""
import nbformat as nbf
import os

nb = nbf.v4.new_notebook()
nb.metadata = {
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
        "name": "skipgram-softmax.ipynb"
    }
}

cells = []

# Cell 1: Markdown intro
cells.append(nbf.v4.new_markdown_cell("""# CS224N L01 — Code Capsule: Skip-gram Softmax P(o|c)

**Waypoint**: WP03 — Word2vec Skip-gram 模型
**Official anchors**: Slides p27-30 (objective function, softmax); Notes §3.2 (Eq.4-5)

## 核心公式

$$P(o|c) = \\frac{\\exp(u_o^\\top v_c)}{\\sum_{w \\in V} \\exp(u_w^\\top v_c)}$$

- **分子**: 目标词 $o$ 和中心词 $c$ 的相似度（点积 → 指数）
- **分母**: 全词表归一化（遍历所有 $w \\in V$）—— 这就是计算瓶颈！

## 本 notebook 做什么

1. 定义一个 mini vocabulary（10 词，4 维向量）
2. 逐步计算 softmax P(o|c)：点积 → 指数 → 归一化
3. 可视化概率分布和点积热力图
4. 演示分母（partition function）的计算代价"""))

# Cell 2: Imports
cells.append(nbf.v4.new_markdown_cell("## 1. 导入与设置"))
cells.append(nbf.v4.new_code_cell("""import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
print("numpy:", np.__version__)
print("matplotlib:", plt.matplotlib.__version__)"""))

# Cell 3: Vocabulary
cells.append(nbf.v4.new_markdown_cell("""## 2. Mini Vocabulary

我们用 10 个词的小词汇表，模拟 Slides p25 的 "banking" 上下文窗口示例。
每个词有**两个向量**：$v_w$（作中心词时）和 $u_w$（作上下文词时）。"""))
cells.append(nbf.v4.new_code_cell("""VOCAB = [
    "banking",      # 0 - center word
    "crises",       # 1
    "into",         # 2
    "turning",      # 3
    "problems",     # 4
    "money",        # 5
    "economy",      # 6
    "policy",       # 7
    "cat",          # 8 - unrelated
    "dog",          # 9 - unrelated
]

VOCAB_SIZE = len(VOCAB)
DIM = 4

# Center vectors V (v_w when word is center)
V = np.array([
    [ 0.8,  0.6, -0.3,  0.1],   # banking
    [ 0.5,  0.7, -0.5,  0.2],   # crises
    [ 0.3,  0.2,  0.8, -0.1],   # into
    [ 0.4,  0.3,  0.6,  0.3],   # turning
    [ 0.6,  0.8, -0.4,  0.1],   # problems
    [ 0.7,  0.5, -0.2,  0.3],   # money
    [ 0.9,  0.4, -0.1,  0.2],   # economy
    [ 0.6,  0.3,  0.1,  0.4],   # policy
    [-0.8, -0.7,  0.5, -0.3],   # cat
    [-0.7, -0.9,  0.4, -0.2],   # dog
], dtype=np.float64)

# Context vectors U (u_w when word is context) — DIFFERENT from V!
U = np.array([
    [ 0.7,  0.5, -0.2,  0.2],   # banking
    [ 0.6,  0.8, -0.6,  0.1],   # crises
    [ 0.2,  0.1,  0.7, -0.2],   # into
    [ 0.3,  0.4,  0.5,  0.2],   # turning
    [ 0.5,  0.9, -0.3,  0.0],   # problems
    [ 0.8,  0.4, -0.1,  0.3],   # money
    [ 0.9,  0.3,  0.0,  0.1],   # economy
    [ 0.5,  0.2,  0.2,  0.5],   # policy
    [-0.9, -0.6,  0.4, -0.4],   # cat
    [-0.6, -0.8,  0.3, -0.1],   # dog
], dtype=np.float64)

print(f"Vocabulary: {VOCAB_SIZE} words, dimension: {DIM}")
print(f"Center vector v_banking = {V[0]}")
print(f"Context vector u_banking = {U[0]}")
print("Note: v_banking ≠ u_banking — each word has TWO vectors!")"""))

# Cell 4: Softmax
cells.append(nbf.v4.new_markdown_cell("""## 3. Softmax 三步（Slides p30）

① **Dot product**: 计算 $u_w^\\top v_c$（相似度）
② **Exponentiation**: $\\exp(u_w^\\top v_c)$（转正）
③ **Normalize**: 除以 $Z = \\sum_w \\exp(u_w^\\top v_c)$（归一化）"""))
cells.append(nbf.v4.new_code_cell("""def softmax(scores):
    \"\"\"Numerically stable softmax.\"\"\"
    scores = scores - np.max(scores)
    exp_scores = np.exp(scores)
    return exp_scores / np.sum(exp_scores)

# Center word: "banking" (index 0)
center_idx = 0
v_c = V[center_idx]

# Step 1: Dot products
dot_products = np.array([np.dot(U[i], v_c) for i in range(VOCAB_SIZE)])

# Step 2 & 3: Softmax
probs = softmax(dot_products)

# Display
print(f"{'Word':>12s}  {'u_w^T v_c':>10s}  {'P(o|c)':>10s}")
print("-" * 38)
for i, word in enumerate(VOCAB):
    print(f"{word:>12s}  {dot_products[i]:>+10.6f}  {probs[i]:>10.6f}")
print(f"\\nSum = {np.sum(probs):.10f}")"""))

# Cell 5: Visualization 1
cells.append(nbf.v4.new_markdown_cell("## 4. 概率分布可视化"))
cells.append(nbf.v4.new_code_cell("""fig, ax = plt.subplots(figsize=(12, 6))
context_idx = [1, 2, 3, 4]
related_idx = [5, 6, 7]
colors = ['#2ecc71' if i in context_idx else 
          '#3498db' if i in related_idx else 
          '#e74c3c' for i in range(VOCAB_SIZE)]
bars = ax.bar(range(VOCAB_SIZE), probs, color=colors, edgecolor='black', linewidth=0.5)

ax.set_xlabel('Output word w', fontsize=12)
ax.set_ylabel('P(w | "banking")', fontsize=12)
ax.set_title('Skip-gram Softmax: P(o|c) for center word "banking"\\n'
             '(Green=context, Blue=related, Red=unrelated)', fontsize=13, fontweight='bold')
ax.set_xticks(range(VOCAB_SIZE))
ax.set_xticklabels(VOCAB, rotation=45, ha='right')

for bar, prob in zip(bars, probs):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.003,
            f'{prob:.4f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor='#2ecc71', label='Context window'),
                   Patch(facecolor='#3498db', label='Related'),
                   Patch(facecolor='#e74c3c', label='Unrelated')], loc='upper right')
plt.tight_layout()
plt.show()"""))

# Cell 6: Visualization 2
cells.append(nbf.v4.new_markdown_cell("## 5. 点积热力图"))
cells.append(nbf.v4.new_code_cell("""fig, ax = plt.subplots(figsize=(10, 8))
full_dots = U @ V.T
im = ax.imshow(full_dots, cmap='RdYlBu_r', aspect='auto', vmin=-1.5, vmax=1.5)
ax.set_xticks(range(VOCAB_SIZE))
ax.set_xticklabels(VOCAB, rotation=45, ha='right', fontsize=9)
ax.set_yticks(range(VOCAB_SIZE))
ax.set_yticklabels(VOCAB, fontsize=9)
ax.set_xlabel('Center word c (v_c)', fontsize=11)
ax.set_ylabel('Context word o (u_o)', fontsize=11)
ax.set_title('Dot Products u_o^T v_c for All (center, context) Pairs', fontsize=12, fontweight='bold')

for i in range(VOCAB_SIZE):
    for j in range(VOCAB_SIZE):
        val = full_dots[i, j]
        color = 'white' if abs(val) > 0.8 else 'black'
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=7, color=color)

plt.colorbar(im, ax=ax, label='u_o^T v_c', shrink=0.8)
plt.tight_layout()
plt.show()"""))

# Cell 7: Partition function cost
cells.append(nbf.v4.new_markdown_cell("""## 6. 分母（Partition Function）的计算代价

分母 $Z = \\sum_{w \\in V} \\exp(u_w^\\top v_c)$ 需要遍历**整个词汇表**。
真实 word2vec 的 $|V| \\approx 50{,}000\\text{-}100{,}000$，每步都要算这么多 exp()！

这就是 WP05 负采样要解决的问题。"""))
cells.append(nbf.v4.new_code_cell("""vocab_sizes = [10, 100, 1000, 10000, 50000, 100000]
time_per_exp_us = 1.0
total_time_ms = [v * time_per_exp_us / 1000 for v in vocab_sizes]

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(range(len(vocab_sizes)), total_time_ms, color='#9b59b6', edgecolor='black', linewidth=0.5)
ax.set_xticks(range(len(vocab_sizes)))
ax.set_xticklabels([f'{v:,}' for v in vocab_sizes])
ax.set_xlabel('Vocabulary size |V|', fontsize=12)
ax.set_ylabel('Time for one softmax (ms)', fontsize=12)
ax.set_title('Partition Function Cost: O(|V|) per Training Step', fontsize=12, fontweight='bold')

for i, t in enumerate(total_time_ms):
    ax.text(i, t + 0.5, f'{t:.1f} ms', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.annotate('Real word2vec\\n|V| ≈ 50K-100K', 
            xy=(4, total_time_ms[4]), xytext=(3, total_time_ms[4] + 15),
            fontsize=10, ha='center',
            arrowprops=dict(arrowstyle='->', color='red'),
            color='red', fontweight='bold')
plt.tight_layout()
plt.show()"""))

# Cell 8: Cross-entropy loss
cells.append(nbf.v4.new_markdown_cell("""## 7. 交叉熵损失（Notes Eq.5）

$$\\min_{U,V} \\; \\mathbb{E}_{o,c}\\left[-\\log p_{U,V}(o|c)\\right]$$

对于单个观察到的 (center, context) 对，损失就是 $-\\log P(o|c)$。"""))
cells.append(nbf.v4.new_code_cell("""observed_idx = 4  # "problems"
observed_word = VOCAB[observed_idx]
loss = -np.log(probs[observed_idx])

print(f"Observed context word: '{observed_word}'")
print(f"P('{observed_word}' | 'banking') = {probs[observed_idx]:.6f}")
print(f"L = -log P = -log({probs[observed_idx]:.6f}) = {loss:.6f}")
print()
print("Goal of training: adjust V and U to make this loss small")
print("→ push P(observed_context | center) closer to 1")"""))

# Cell 9: Summary
cells.append(nbf.v4.new_markdown_cell("""## 总结

| 概念 | 公式/值 |
|------|---------|
| Softmax 概率 | $P(o\\|c) = \\exp(u_o^\\top v_c) / \\sum_w \\exp(u_w^\\top v_c)$ |
| 每词两向量 | $v_w$ (center), $u_w$ (context) |
| 分母代价 | $O(\\|V\\|)$ — 每步遍历全词表 |
| 交叉熵损失 | $-\\log P(o\\|c)$ |

**关键洞察**: 分母需要遍历整个词汇表 → 这就是为什么负采样 (WP05) 用 logistic 二分类替代全 softmax。

> **Next**: [负采样 capsule]({{negative-sampling-loss}}) — 用 $k$ 个负样本替代 $|V|$ 次 exp() 计算。"""))

nb.cells = cells

output_path = "Labs/L01-word-vectors/skipgram-softmax.ipynb"
with open(output_path, 'w') as f:
    nbf.write(nb, f)
print(f"Notebook written: {output_path}")
