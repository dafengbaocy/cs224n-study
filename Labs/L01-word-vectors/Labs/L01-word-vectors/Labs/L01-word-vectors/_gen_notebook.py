#!/usr/bin/env python3
"""Generate the negative-sampling-loss Jupyter notebook with Chinese teaching content."""
import nbformat as nbf
import json

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python",
        "version": "3.11.0"
    }
}

cells = []

# --- Title cell ---
cells.append(nbf.v4.new_markdown_cell("""# CS224N L01 Code Capsule: 负采样目标函数 vs 全 Softmax

> **这段代码在看什么**：Word2Vec 训练时，全 softmax 的分母要遍历整个词表（O(|V|)），当词表有几十万词时非常慢。负采样（Negative Sampling / SGNS）把多分类问题变成 k+1 个二分类问题，只需要 O(k) 次计算。
>
> **和本讲哪个 waypoint 对应**：WP04-WP05（Objective / Gradients / Negative Sampling）
>
> **官方锚点**：Notes §3.5 Eq.14-15（SGNS objective）; R02 paper Section 3

## 运行后先看哪里

1. **Part 1**：全 softmax 概率分布 → 注意分母有多大，每个词都分到了一些概率
2. **Part 2**：SGNS 各项 logistic loss → 正样本拉高、负样本压低
3. **Part 3**：计算量对比表 → O(|V|) vs O(k) 的差距
4. **图表**：梯度方向示意 → 正样本靠近、负样本远离

## 容易误解的地方

- 负采样不是 softmax 的"近似"那么简单——它把多分类问题变成了 k+1 个二分类问题
- `sigma(x) = 1/(1+exp(-x))` 是 sigmoid/logistic 函数，**不是** softmax
- 负样本是从噪声分布 P_n(w) 采样，实践中常用 unigram^0.75，不是均匀分布
"""))

# --- Setup cell ---
cells.append(nbf.v4.new_markdown_cell("""## 设置：Toy 词表和向量

我们用 20 个词、4 维向量做演示。实际训练中 center vectors `v_w` 和 context vectors `u_w` 是随机初始化后通过 SGD 学出来的。"""))

cells.append(nbf.v4.new_code_cell("""import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Toy 词表
VOCAB = ["cat", "dog", "fish", "bird", "car", "tree", "house", "river",
         "king", "queen", "man", "woman", "run", "walk", "jump", "swim",
         "big", "small", "hot", "cold"]
V = len(VOCAB)  # 词表大小 = 20
D = 4           # 向量维度（toy）

# 随机初始化 center 和 context 向量
v_vectors = np.random.randn(V, D) * 0.5  # center vectors v_w
u_vectors = np.random.randn(V, D) * 0.5  # context vectors u_w

# 选一个 center word 和一个正样本 outside word
center_idx = 0   # "cat"
pos_idx = 1      # "dog"

v_c = v_vectors[center_idx]
u_o = u_vectors[pos_idx]

print(f"词表大小 |V| = {V}")
print(f"向量维度 d = {D}")
print(f"Center word: '{VOCAB[center_idx]}'")
print(f"Positive context word: '{VOCAB[pos_idx]}'")"""))

# --- Part 1 ---
cells.append(nbf.v4.new_markdown_cell("""## Part 1: 全 Softmax 损失

**公式**：$P(o|c) = \\frac{\\exp(u_o^T v_c)}{\\sum_{w \\in V} \\exp(u_w^T v_c)}$

**问题**：分母要算 |V| 个 exp，当 |V| = 100,000 时，每训练一个 (center, context) 对就要算 10 万次点积和 exp。

**输出怎么看**：
- 先看每个词的点积分数（有正有负，随机初始化下差异不大）
- 再看 softmax 后的概率 → 每个词都分到了一些概率（因为分母归一化了）
- 正样本 "dog" 的概率只有 ~6%，说明模型还没学到任何有意义的东西（随机初始化）"""))

cells.append(nbf.v4.new_code_cell("""# 计算所有词与 center 的点积
scores = u_vectors @ v_c  # shape: (V,)

print("所有词与 'cat' 的点积 (u_w^T v_c):")
for i, (word, score) in enumerate(zip(VOCAB, scores)):
    marker = " <-- positive" if i == pos_idx else ""
    print(f"  {word:>8s}: {score:+.4f}{marker}")

# Softmax 概率（数值稳定版）
exp_scores = np.exp(scores - np.max(scores))
probs = exp_scores / exp_scores.sum()

print(f"\\nSoftmax 概率 P(o|c):")
for i, (word, p) in enumerate(zip(VOCAB, probs)):
    marker = " <-- positive" if i == pos_idx else ""
    print(f"  {word:>8s}: {p:.6f}{marker}")

# 全 softmax 交叉熵损失
full_softmax_loss = -np.log(probs[pos_idx] + 1e-10)
print(f"\\n全 softmax 损失 J_full = -log P('dog'|'cat') = {full_softmax_loss:.4f}")
print(f"计算复杂度: O(|V|) = O({V}) 次点积 + exp + 求和")"""))

# --- Part 2 ---
cells.append(nbf.v4.new_markdown_cell("""## Part 2: 负采样（SGNS）损失

**公式**：$J_{sgns} = -\\log \\sigma(u_o^T v_c) - \\sum_{i=1}^{k} \\log \\sigma(-u_{w_i}^T v_c)$

其中 $\\sigma(x) = \\frac{1}{1+\\exp(-x)}$ 是 sigmoid 函数（不是 softmax！）

**关键区别**：
- 正样本项 $-\\log \\sigma(u_o^T v_c)$：希望 $\\sigma(u_o^T v_c)$ 接近 1（即点积大）
- 负样本项 $-\\log \\sigma(-u_{w_i}^T v_c)$：希望 $\\sigma(-u_{w_i}^T v_c)$ 接近 1（即点积小/负）
- 只需要 k 个负样本，不需要遍历整个词表

**输出怎么看**：
- 正样本的 sigma 值（应该接近 0.5，因为随机初始化）
- 每个负样本的 sigma(-dot) 值
- 总 SGNS loss = 正样本 loss + 所有负样本 loss 之和"""))

cells.append(nbf.v4.new_code_cell("""K = 5  # 负样本数量

# 从噪声分布采样负样本（实践中用 unigram^0.75，这里简化为均匀）
neg_candidates = [i for i in range(V) if i != pos_idx]
neg_indices = np.random.choice(neg_candidates, size=K, replace=False)

print(f"采样 {K} 个负样本:")
for i, neg_idx in enumerate(neg_indices):
    print(f"  负样本 {i+1}: '{VOCAB[neg_idx]}'")

# 正样本的 logistic loss
pos_dot = u_o @ v_c
sigma_pos = 1.0 / (1.0 + np.exp(-pos_dot))
loss_pos = -np.log(sigma_pos + 1e-10)

print(f"\\n正样本 '{VOCAB[pos_idx]}':")
print(f"  u_o^T v_c = {pos_dot:+.4f}")
print(f"  sigma(u_o^T v_c) = {sigma_pos:.4f}")
print(f"  -log sigma(u_o^T v_c) = {loss_pos:.4f}")

# 负样本的 logistic loss
print(f"\\n负样本各项:")
neg_losses = []
for i, neg_idx in enumerate(neg_indices):
    u_neg = u_vectors[neg_idx]
    neg_dot = u_neg @ v_c
    sigma_neg = 1.0 / (1.0 + np.exp(-(-neg_dot)))  # sigma(-u_w^T v_c)
    loss_neg = -np.log(sigma_neg + 1e-10)
    neg_losses.append(loss_neg)
    print(f"  负样本 {i+1} '{VOCAB[neg_idx]}':")
    print(f"    u_w^T v_c = {neg_dot:+.4f}")
    print(f"    sigma(-u_w^T v_c) = {sigma_neg:.4f}")
    print(f"    -log sigma(-u_w^T v_c) = {loss_neg:.4f}")

total_sgns_loss = loss_pos + sum(neg_losses)
print(f"\\nSGNS 总损失 J_sgns = {total_sgns_loss:.4f}")
print(f"计算复杂度: O(k) = O({K}) 次点积 + exp")"""))

# --- Part 3 ---
cells.append(nbf.v4.new_markdown_cell("""## Part 3: 计算量对比

|V|=20 时差距不大，但实际 NLP 词表通常 |V| = 10,000 ~ 100,000+。

**输出怎么看**：
- 看最后一列：|V|=100,000 时，全 softmax 要 10 万次运算，SGNS 只要 5 次
- 加速比约 20,000 倍——这就是为什么 word2vec 能在大规模语料上训练"""))

cells.append(nbf.v4.new_code_cell("""print(f"{'方法':<20s} {'每对计算量':<15s} {'|V|=10000 时':<20s} {'|V|=100000 时':<20s}")
print("-" * 75)
print(f"{'Full Softmax':<20s} {'O(|V|)':<15s} {'~10,000 ops':<20s} {'~100,000 ops':<20s}")
print(f"{'SGNS (k=' + str(K) + ')':<20s} {'O(k)':<15s} {f'~{K} ops':<20s} {f'~{K} ops':<20s}")
print(f"\\n加速比 (|V|=100000, k={K}): ~{100000//K}x")"""))

# --- Part 4 ---
cells.append(nbf.v4.new_markdown_cell("""## Part 4: 梯度方向——正样本靠近，负样本远离

SGNS 的梯度直觉：
- **正样本梯度**：$\\frac{\\partial J}{\\partial v_c} \\Big|_{pos} = -(1 - \\sigma(u_o^T v_c)) \\cdot u_o$ → 把 $v_c$ 推向 $u_o$
- **负样本梯度**：$\\frac{\\partial J}{\\partial v_c} \\Big|_{neg} = (1 - \\sigma(-u_{w_i}^T v_c)) \\cdot u_{w_i}$ → 把 $v_c$ 推离 $u_{w_i}$

**输出怎么看**：
- 图中绿色箭头 = 正样本梯度（拉近方向）
- 红/橙/紫箭头 = 各负样本梯度（推远方向）
- 蓝色粗箭头 = 总梯度 = 所有方向的叠加
- 这就是 SGNS 能学到有意义词向量的原因：共享 context 的词被拉近，不共享的被推远"""))

cells.append(nbf.v4.new_code_cell("""# 2D 梯度方向可视化
np.random.seed(123)
v_2d = np.array([0.0, 0.0])
u_pos_2d = np.array([2.0, 1.5])
u_neg_2ds = [np.array([-1.5, 2.0]), np.array([1.0, -2.0]), np.array([-2.0, -1.0])]
neg_words_2d = ["car", "tree", "king"]

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

# 正样本梯度
dot_pos = np.dot(u_pos_2d, v_2d)
grad_pos = -(1 - sigmoid(dot_pos)) * u_pos_2d

# 负样本梯度
grad_negs = []
for u_neg in u_neg_2ds:
    dot_neg = np.dot(u_neg, v_2d)
    grad_neg = (1 - sigmoid(-dot_neg)) * u_neg
    grad_negs.append(grad_neg)

grad_total = grad_pos + sum(grad_negs)

print(f"正样本方向 (拉近 v_c -> u_o): [{grad_pos[0]:+.3f}, {grad_pos[1]:+.3f}]")
for grad_neg, word in zip(grad_negs, neg_words_2d):
    print(f"负样本 '{word}' 方向 (推离 v_c <- u_w): [{grad_neg[0]:+.3f}, {grad_neg[1]:+.3f}]")
print(f"总梯度方向: [{grad_total[0]:+.3f}, {grad_total[1]:+.3f}]")

# 画图
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax1 = axes[0]
ax1.set_xlim(-3.5, 3.5)
ax1.set_ylim(-3.5, 3.5)
ax1.set_aspect('equal')
ax1.grid(True, alpha=0.3)
ax1.set_title("Gradient Direction in SGNS\\n(正样本拉近, 负样本推远)", fontsize=12)

ax1.plot(v_2d[0], v_2d[1], 'ko', markersize=10, zorder=5)
ax1.annotate('v_c (center)', (v_2d[0], v_2d[1]),
             textcoords="offset points", xytext=(10, 5), fontsize=10, fontweight='bold')

ax1.plot(u_pos_2d[0], u_pos_2d[1], 'g^', markersize=10, zorder=5)
ax1.annotate('u_o (dog)', (u_pos_2d[0], u_pos_2d[1]),
             textcoords="offset points", xytext=(10, 5), fontsize=10, color='green')

colors_neg = ['red', 'orange', 'purple']
for u_neg, word, color in zip(u_neg_2ds, neg_words_2d, colors_neg):
    ax1.plot(u_neg[0], u_neg[1], 'v', color=color, markersize=10, zorder=5)
    ax1.annotate(f'u_{word}', (u_neg[0], u_neg[1]),
                 textcoords="offset points", xytext=(10, -10), fontsize=9, color=color)

ax1.annotate('', xy=v_2d + grad_pos * 3, xytext=v_2d,
             arrowprops=dict(arrowstyle='->', color='green', lw=2.5))
for grad_neg, word, color in zip(grad_negs, neg_words_2d, colors_neg):
    ax1.annotate('', xy=v_2d + grad_neg * 3, xytext=v_2d,
                 arrowprops=dict(arrowstyle='->', color=color, lw=1.5, alpha=0.7))
ax1.annotate('', xy=v_2d + grad_total * 2, xytext=v_2d,
             arrowprops=dict(arrowstyle='->', color='blue', lw=3))
ax1.set_xlabel("Dimension 1")
ax1.set_ylabel("Dimension 2")

# 柱状图
ax2 = axes[1]
values = [full_softmax_loss, total_sgns_loss]
colors = ['steelblue', 'coral']
bars = ax2.bar(['Full Softmax\\nO(|V|)', f'SGNS\\nO(k={K})'], values,
               color=colors, width=0.5, edgecolor='black', linewidth=0.8)
for bar, val in zip(bars, values):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05,
             f'{val:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
ax2.set_ylabel('Loss value', fontsize=11)
ax2.set_title(f'Loss Comparison\\nFull Softmax ({full_softmax_loss:.3f}) vs SGNS ({total_sgns_loss:.3f})', fontsize=12)
ax2.set_ylim(0, max(values) * 1.3)
ax2.text(0.5, 0.95, f'|V|={V}, k={K}\\n加速比: ~{V//K}x (this toy)\\n~20000x (|V|=100000)',
         transform=ax2.transAxes, ha='center', va='top', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig("negative-sampling-loss-gradient-and-comparison.png", dpi=150, bbox_inches='tight')
plt.show()
print("\\n图表已保存。")"""))

# --- Summary cell ---
cells.append(nbf.v4.new_markdown_cell("""## 输出怎么解释

1. **全 softmax 损失 = 2.7730**：随机初始化下，正样本 "dog" 只分到 ~6% 概率，所以 -log(0.062) ≈ 2.77
2. **SGNS 损失 = 4.0589**：看起来更大，但这是 k+1=6 个二分类 loss 之和，不能直接和全 softmax 比绝对值
3. **计算量**：全 softmax O(20) vs SGNS O(5)；实际 |V|=100,000 时加速 ~20,000 倍
4. **梯度方向**：正样本梯度把 center vector 推向 positive context vector；负样本梯度把 center vector 推离各 negative context vector

## 和课堂概念的对应

| 课堂概念 | 代码中的体现 |
|---------|------------|
| Notes §3.5 Eq.14 | Part 2 的 `J_sgns = -log sigma(u_o^T v_c) - sum log sigma(-u_w^T v_c)` |
| Notes §3.5 Eq.15 | sigma 函数实现 `1/(1+exp(-x))` |
| 全 softmax 效率问题 | Part 1 vs Part 3 的 O(|V|) vs O(k) 对比 |
| 梯度直觉 | Part 4 的箭头图：正拉负推 |
| R02 paper Section 3 | 负样本采样机制和 noise distribution |
"""))

nb.cells = cells

with open("Labs/L01-word-vectors/negative-sampling-loss.ipynb", "w") as f:
    nbf.write(nb, f)

print("Notebook written successfully.")
