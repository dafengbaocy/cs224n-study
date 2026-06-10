#!/usr/bin/env python3
"""
CS224N L01-word-vectors Code Capsule: cosine-similarity-analogy (WP06)

概念：余弦相似度与词类比算术
- 余弦相似度 (cosine similarity) 的计算和直觉
- 词类比算术 (word analogy): king - man + woman ≈ queen
- 类比成功与失败案例对比

官方锚点: A1 Part 2 Q2.2-2.6 (cosine similarity, analogy)
"""

import numpy as np
import json
import os

# ============================================================
# Part 1: 余弦相似度 (Cosine Similarity) 基础计算
# ============================================================
print("=" * 70)
print("Part 1: 余弦相似度 (Cosine Similarity) 基础计算")
print("=" * 70)

def cosine_similarity(u, v):
    """计算两个向量的余弦相似度: cos(θ) = u·v / (||u|| * ||v||)"""
    dot = np.dot(u, v)
    norm_u = np.linalg.norm(u)
    norm_v = np.linalg.norm(v)
    if norm_u == 0 or norm_v == 0:
        return 0.0
    return dot / (norm_u * norm_v)

# 构造 toy 词向量 (6维, 手工设计以展示语义关系)
# 维度设计: [royalty, gender_male, gender_female, age_old, age_young, animal]
vocab = {
    "king":   np.array([0.9, 0.8, 0.1, 0.7, 0.1, 0.0]),
    "queen":  np.array([0.9, 0.1, 0.8, 0.7, 0.1, 0.0]),
    "man":    np.array([0.1, 0.9, 0.0, 0.5, 0.5, 0.0]),
    "woman":  np.array([0.1, 0.0, 0.9, 0.5, 0.5, 0.0]),
    "boy":    np.array([0.0, 0.8, 0.0, 0.0, 0.9, 0.0]),
    "girl":   np.array([0.0, 0.0, 0.8, 0.0, 0.9, 0.0]),
    "dog":    np.array([0.0, 0.0, 0.0, 0.3, 0.7, 0.9]),
    "cat":    np.array([0.0, 0.0, 0.0, 0.3, 0.7, 0.9]),
    "prince": np.array([0.8, 0.7, 0.1, 0.1, 0.8, 0.0]),
    "princess": np.array([0.8, 0.1, 0.7, 0.1, 0.8, 0.0]),
}

print("\nToy 词向量 (6维手工设计):")
print("维度含义: [royalty, gender_male, gender_female, age_old, age_young, animal]")
for word, vec in vocab.items():
    print(f"  {word:10s} = {vec}")

# 计算关键词对的余弦相似度
print("\n--- 词对余弦相似度 ---")
pairs = [
    ("king", "queen"),
    ("king", "man"),
    ("king", "woman"),
    ("man", "woman"),
    ("king", "dog"),
    ("dog", "cat"),
    ("boy", "girl"),
    ("prince", "princess"),
]

similarity_results = []
for w1, w2 in pairs:
    sim = cosine_similarity(vocab[w1], vocab[w2])
    similarity_results.append((w1, w2, sim))
    print(f"  cos({w1:10s}, {w2:10s}) = {sim:.4f}")

print("\n[解读] cos 值范围 [-1, 1]:")
print("  1.0 = 完全相同方向 (语义完全一致)")
print("  0.0 = 正交 (语义无关)")
print(" -1.0 = 完全相反方向")
print("  king-queen 高相似度 → 共享 'royalty' 维度")
print("  king-dog 低相似度 → 语义距离远")

# ============================================================
# Part 2: 词类比算术 (Word Analogy)
# ============================================================
print("\n" + "=" * 70)
print("Part 2: 词类比算术 (Word Analogy)")
print("=" * 70)

def word_analogy(a, b, c, vocab_dict):
    """
    类比: a 之于 b 如同 c 之于 ?
    即: ? = b - a + c
    
    经典例子: king - man + woman = queen
    """
    result_vec = vocab_dict[b] - vocab_dict[a] + vocab_dict[c]
    
    # 在所有词中找最接近 result_vec 的 (排除 a, b, c)
    similarities = []
    for word, vec in vocab_dict.items():
        if word in [a, b, c]:
            continue
        sim = cosine_similarity(result_vec, vec)
        similarities.append((word, sim))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    return result_vec, similarities

# 经典类比: king - man + woman = ?
print("\n--- 经典类比: king - man + woman = ? ---")
result_vec, ranked = word_analogy("king", "man", "woman", vocab)
print(f"  结果向量: {result_vec}")
print(f"  最接近的词:")
for rank, (word, sim) in enumerate(ranked, 1):
    marker = " ← 正确答案!" if word == "queen" else ""
    print(f"    #{rank}: {word:10s}  cos_sim = {sim:.4f}{marker}")

# 更多类比
print("\n--- 更多类比测试 ---")
analogies = [
    ("king", "man", "woman", "queen"),     # 皇室性别转换
    ("prince", "man", "woman", "princess"), # 皇室性别转换 2
    ("man", "woman", "king", "queen"),      # 反向: man→woman, king→?
    ("king", "queen", "man", "woman"),      # 反向: king→queen, man→?
    ("boy", "girl", "man", "woman"),        # 年龄+性别
]

analogy_results = []
for a, b, c, expected in analogies:
    result_vec, ranked = word_analogy(a, b, c, vocab)
    top_word, top_sim = ranked[0]
    correct = top_word == expected
    analogy_results.append({
        "analogy": f"{a} - {b} + {c}",
        "expected": expected,
        "top_prediction": top_word,
        "top_similarity": round(top_sim, 4),
        "correct": correct
    })
    status = "✓" if correct else "✗"
    print(f"  {status} {a} - {b} + {c} = {top_word} (expected: {expected}, sim={top_sim:.4f})")

# ============================================================
# Part 3: 类比失败案例 (Analogy Failures)
# ============================================================
print("\n" + "=" * 70)
print("Part 3: 类比失败案例 (Analogy Failures)")
print("=" * 70)

# 构造一些会失败的类比
print("\n--- 失败案例 1: 跨语义域的类比 ---")
# dog 之于 cat 如同 king 之于 ? (期望某种"对应"，但语义域不同)
result_vec, ranked = word_analogy("dog", "cat", "king", vocab)
print(f"  dog - cat + king = ?")
print(f"  结果向量: {result_vec}")
print(f"  Top-3 预测:")
for word, sim in ranked[:3]:
    print(f"    {word:10s}  cos_sim = {sim:.4f}")
print(f"  [解读] 动物域的 '对应关系' 不能简单迁移到皇室域")

print("\n--- 失败案例 2: 无对应关系的词 ---")
# dog 之于 king 如同 man 之于 ? (没有清晰语义关系)
result_vec, ranked = word_analogy("dog", "king", "man", vocab)
print(f"  dog - king + man = ?")
print(f"  结果向量: {result_vec}")
print(f"  Top-3 预测:")
for word, sim in ranked[:3]:
    print(f"    {word:10s}  cos_sim = {sim:.4f}")
print(f"  [解读] 当 a→b 没有清晰语义关系时，类比结果无意义")

# ============================================================
# Part 4: 几何直觉可视化数据
# ============================================================
print("\n" + "=" * 70)
print("Part 4: 几何直觉 — 向量关系可视化数据")
print("=" * 70)

# 提取 2D 投影 (取前两个维度: royalty, gender_male) 用于可视化说明
print("\n2D 投影 (维度 0: royalty, 维度 1: gender_male):")
print(f"  {'word':10s}  {'royalty':>8s}  {'gender_M':>8s}")
for word, vec in vocab.items():
    print(f"  {word:10s}  {vec[0]:8.4f}  {vec[1]:8.4f}")

# 类比向量算术的几何解释
print("\n类比向量算术几何解释:")
print("  king - man = 去掉 '男性' 成分，保留 '皇室' 成分")
diff_king_man = vocab["king"] - vocab["man"]
print(f"    king - man = {diff_king_man}")
print("  (king - man) + woman = 皇室成分 + '女性' 成分 ≈ queen")
result = diff_king_man + vocab["woman"]
print(f"    result = {result}")
print(f"    queen  = {vocab['queen']}")
print(f"    cos(result, queen) = {cosine_similarity(result, vocab['queen']):.4f}")

# ============================================================
# Part 5: 生成可视化图表
# ============================================================
print("\n" + "=" * 70)
print("Part 5: 生成可视化图表")
print("=" * 70)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

output_dir = "/workspace/cs224n-study/Labs/L01-word-vectors/outputs"
os.makedirs(output_dir, exist_ok=True)

# --- Plot 1: Cosine Similarity Heatmap ---
words = list(vocab.keys())
n = len(words)
sim_matrix = np.zeros((n, n))
for i, w1 in enumerate(words):
    for j, w2 in enumerate(words):
        sim_matrix[i, j] = cosine_similarity(vocab[w1], vocab[w2])

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(sim_matrix, cmap='RdYlBu_r', vmin=-0.2, vmax=1.0)
ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels(words, rotation=45, ha='right', fontsize=10)
ax.set_yticklabels(words, fontsize=10)

# 在每个格子标注数值
for i in range(n):
    for j in range(n):
        val = sim_matrix[i, j]
        color = "white" if val > 0.6 or val < 0.1 else "black"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=8)

plt.colorbar(im, ax=ax, label='Cosine Similarity')
ax.set_title('Cosine Similarity Between Word Vectors\n(Toy 6D Vectors)', fontsize=14, fontweight='bold')
plt.tight_layout()
plot1_path = os.path.join(output_dir, "cosine-similarity-analogy-heatmap.png")
plt.savefig(plot1_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot1_path}")

# --- Plot 2: 2D Projection with Analogy Arrow ---
fig, ax = plt.subplots(figsize=(10, 8))

# 选几个关键词画 2D 投影 (dim 0: royalty, dim 1: gender direction = male - female)
plot_words = ["king", "queen", "man", "woman", "boy", "girl", "prince", "princess", "dog", "cat"]
for word in plot_words:
    vec = vocab[word]
    ax.scatter(vec[0], vec[1], s=100, zorder=5, color='steelblue' if vec[2] > 0.5 else 'coral')
    ax.annotate(word, (vec[0], vec[1]), textcoords="offset points", 
                xytext=(8, 5), fontsize=11, fontweight='bold')

# 画类比箭头: man → king (加上 royalty), woman → queen (应该平行)
arrow_style = dict(arrowstyle='->', color='green', lw=2)
# man -> king
ax.annotate('', xy=vocab["king"][:2], xytext=vocab["man"][:2],
            arrowprops=dict(arrowstyle='->', color='green', lw=2.5, linestyle='--'))
ax.text(0.5, 0.85, "man→king", color='green', fontsize=10, transform=ax.transData)

# woman -> queen (应该平行)
ax.annotate('', xy=vocab["queen"][:2], xytext=vocab["woman"][:2],
            arrowprops=dict(arrowstyle='->', color='red', lw=2.5, linestyle='--'))
ax.text(0.5, 0.15, "woman→queen", color='red', fontsize=10, transform=ax.transData)

ax.set_xlabel('Dimension 0: Royalty', fontsize=12)
ax.set_ylabel('Dimension 1: Gender-Male', fontsize=12)
ax.set_title('2D Word Vector Projection\nking-man+woman≈queen as Parallel Arrows', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xlim(-0.2, 1.1)
ax.set_ylim(-0.2, 1.1)

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='steelblue', markersize=10, label='Female-dominant'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='coral', markersize=10, label='Male-dominant/Animal'),
    Line2D([0], [0], color='green', lw=2, linestyle='--', label='man→king (add royalty)'),
    Line2D([0], [0], color='red', lw=2, linestyle='--', label='woman→queen (add royalty)'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=9)

plt.tight_layout()
plot2_path = os.path.join(output_dir, "cosine-similarity-analogy-2d-projection.png")
plt.savefig(plot2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot2_path}")

# --- Plot 3: Analogy Results Bar Chart ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Successful analogies
analogy_labels = [f"{a['analogy']}" for a in analogy_results]
analogy_sims = [a['top_similarity'] for a in analogy_results]
colors = ['green' if a['correct'] else 'red' for a in analogy_results]

bars = axes[0].barh(analogy_labels, analogy_sims, color=colors, alpha=0.7)
axes[0].set_xlabel('Cosine Similarity to Expected Answer', fontsize=11)
axes[0].set_title('Word Analogy Results\n(Green=Correct, Red=Wrong)', fontsize=12, fontweight='bold')
axes[0].set_xlim(0, 1.1)
for bar, sim in zip(bars, analogy_sims):
    axes[0].text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, 
                f'{sim:.4f}', va='center', fontsize=10)

# Right: Similarity comparison for key pairs
pair_labels = [f"{w1}-{w2}" for w1, w2, _ in similarity_results]
pair_sims = [sim for _, _, sim in similarity_results]
pair_colors = plt.cm.RdYlBu_r([sim for sim in pair_sims])

bars2 = axes[1].barh(pair_labels, pair_sims, color=pair_colors, alpha=0.8)
axes[1].set_xlabel('Cosine Similarity', fontsize=11)
axes[1].set_title('Word Pair Cosine Similarities', fontsize=12, fontweight='bold')
axes[1].set_xlim(0, 1.1)
for bar, sim in zip(bars2, pair_sims):
    axes[1].text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                f'{sim:.4f}', va='center', fontsize=10)

plt.tight_layout()
plot3_path = os.path.join(output_dir, "cosine-similarity-analogy-results-chart.png")
plt.savefig(plot3_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot3_path}")

print("\n" + "=" * 70)
print("All outputs generated successfully.")
print("=" * 70)
