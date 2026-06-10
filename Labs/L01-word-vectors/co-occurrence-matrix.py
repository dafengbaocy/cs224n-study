#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: co-occurrence-matrix
=============================================================
概念：从语料构建共现矩阵（co-occurrence matrix）并用 SVD 降维。
对应：Notes §3.1 (co-occurrence matrices); A1 Part 1 Q1.1-1.3
Waypoint: WP02

这段代码在看什么：
  1. 用一个极小语料（6 句话）统计词与词在窗口内共同出现的次数
  2. 得到一个 V×V 的共现矩阵（V = 词汇量）
  3. 用 SVD（奇异值分解）把高维稀疏矩阵降到 2 维
  4. 在 2D 散点图上观察：语义相近的词是否聚在一起

运行后先看哪里：
  - 共现矩阵表格：注意哪些词对计数 > 0，哪些是 0
  - SVD 2D 坐标表：看语义相近的词（如 cat/dog）坐标是否接近
  - 散点图：直观看到降维后的词向量分布

输出怎么解释：
  - 共现矩阵的每个元素 M[i][j] = 词 i 和词 j 在窗口内共同出现的次数
  - SVD 把 V 维向量压缩到 2 维，保留最大的两个奇异值对应的方向
  - 如果两个词的上下文相似，它们在 2D 图上会靠在一起

和本讲哪个 waypoint 对应：WP02 — One-hot vs Dense Vectors
  - Notes §3.1 说"构建共现矩阵 → SVD 降维 → 得到 dense vector"
  - 这个 capsule 把整个过程跑一遍

容易误解的地方：
  - 共现矩阵是对称的（无向窗口），但如果是定向窗口（只看右边）则不对称
  - SVD 降维后坐标的符号可能翻转（因为奇异向量方向不唯一），但相对距离不变
  - toy 语料太小，2D 图只是示意；真实场景需要大语料 + 更高维度
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
import json
import sys
import os

# ============================================================
# 第 1 步：定义极小语料
# ============================================================
# 选择语义相关的词对：cat/dog（动物），bank/river（自然），bank/money（金融）
corpus = [
    "the cat sat on the mat",
    "the dog sat on the log",
    "the cat and the dog played in the park",
    "the bank is near the river",
    "the river flows to the sea",
    "money from the bank helps the economy",
]

print("=" * 60)
print("CS224N L01 Code Capsule: Co-occurrence Matrix + SVD")
print("=" * 60)
print()
print("Corpus:")
for i, sent in enumerate(corpus):
    print(f"  [{i}] {sent}")
print()

# ============================================================
# 第 2 步：构建词汇表
# ============================================================
all_words = []
for sent in corpus:
    all_words.extend(sent.lower().split())

vocab = sorted(set(all_words))
word_to_idx = {w: i for i, w in enumerate(vocab)}
V = len(vocab)

print(f"Vocabulary size V = {V}")
print(f"Vocab: {vocab}")
print()

# ============================================================
# 第 3 步：构建共现矩阵（窗口大小 = 1）
# ============================================================
def build_cooccurrence_matrix(corpus, word_to_idx, window_size=1):
    """Build co-occurrence matrix. For each center word, count words within window."""
    V = len(word_to_idx)
    matrix = np.zeros((V, V), dtype=int)
    for sent in corpus:
        words = sent.lower().split()
        for i, word in enumerate(words):
            ci = word_to_idx[word]
            for j in range(max(0, i - window_size), i):
                matrix[ci][word_to_idx[words[j]]] += 1
            for j in range(i + 1, min(len(words), i + window_size + 1)):
                matrix[ci][word_to_idx[words[j]]] += 1
    return matrix

window_size = 1
cooc_matrix = build_cooccurrence_matrix(corpus, word_to_idx, window_size)

print(f"Co-occurrence matrix (window={window_size})")
print(f"  Shape: {cooc_matrix.shape} ({V}x{V})")
print()

def abbreviate(w, maxlen=6):
    return w[:maxlen] if len(w) <= maxlen else w[:maxlen-1] + "."

header = "       " + "".join(f"{abbreviate(w):>7}" for w in vocab)
print(header)
for i, w in enumerate(vocab):
    row = f"{abbreviate(w):>6} " + "".join(f"{cooc_matrix[i][j]:>7}" for j in range(V))
    print(row)
print()

nnz = np.count_nonzero(cooc_matrix)
total = V * V
sparsity = 1.0 - nnz / total
print(f"  Non-zero: {nnz}/{total} = {nnz/total:.1%}")
print(f"  Sparsity: {sparsity:.1%}")
print()

# ============================================================
# 第 4 步：SVD 降维到 2D
# ============================================================
print("SVD reduction to k=2")
U, S, Vt = np.linalg.svd(cooc_matrix.astype(float))
k = 2
coords_2d = U[:, :k] * S[:k]

print(f"  Top-{k} singular values: {S[:k]}")
print(f"  All singular values: {S}")
print()

print("2D coordinates (SVD):")
print(f"  {'word':>10}  {'x':>8}  {'y':>8}")
print(f"  {'-'*10}  {'-'*8}  {'-'*8}")
for i, w in enumerate(vocab):
    print(f"  {w:>10}  {coords_2d[i, 0]:>8.4f}  {coords_2d[i, 1]:>8.4f}")
print()

# ============================================================
# 第 5 步：散点图
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(10, 7))
ax.scatter(coords_2d[:, 0], coords_2d[:, 1], c='steelblue', s=60, zorder=5)
for i, w in enumerate(vocab):
    ax.annotate(w, (coords_2d[i, 0], coords_2d[i, 1]),
                fontsize=9, ha='center', va='bottom',
                xytext=(0, 5), textcoords='offset points')

highlight_pairs = [
    ("cat", "dog", "red"),
    ("bank", "river", "green"),
    ("bank", "money", "orange"),
]
for w1, w2, color in highlight_pairs:
    if w1 in word_to_idx and w2 in word_to_idx:
        i1, i2 = word_to_idx[w1], word_to_idx[w2]
        ax.plot([coords_2d[i1, 0], coords_2d[i2, 0]],
                [coords_2d[i1, 1], coords_2d[i2, 1]],
                '--', color=color, alpha=0.7, linewidth=1.5)
        mid_x = (coords_2d[i1, 0] + coords_2d[i2, 0]) / 2
        mid_y = (coords_2d[i1, 1] + coords_2d[i2, 1]) / 2
        dist = np.sqrt((coords_2d[i1, 0] - coords_2d[i2, 0])**2 +
                       (coords_2d[i1, 1] - coords_2d[i2, 1])**2)
        ax.annotate(f"{w1}-{w2}\nd={dist:.3f}",
                    (mid_x, mid_y), fontsize=8, color=color,
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor=color, alpha=0.8))

ax.set_xlabel("SVD Dimension 1 (largest singular value)", fontsize=11)
ax.set_ylabel("SVD Dimension 2 (2nd largest singular value)", fontsize=11)
ax.set_title("CS224N L01: Co-occurrence Matrix -> SVD 2D Projection\n"
             f"Corpus: {len(corpus)} sentences, V={V}, window={window_size}",
             fontsize=12)
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='-')
ax.axvline(x=0, color='gray', linewidth=0.5, linestyle='-')
plt.tight_layout()
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(output_dir, exist_ok=True)
plot_path = os.path.join(output_dir, "co-occurrence-matrix-svd-2d.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Plot saved: {plot_path}")
print()

# ============================================================
# 第 6 步：对比不同窗口大小
# ============================================================
print("Window size comparison:")
print("  Larger window -> more semantic/topic; smaller -> more syntactic")
print()
for ws in [1, 2, 3]:
    M = build_cooccurrence_matrix(corpus, word_to_idx, ws)
    nnz_ws = np.count_nonzero(M)
    print(f"  window={ws}: non-zero {nnz_ws}/{V*V} = {nnz_ws/(V*V):.1%}, sum={M.sum()}")
print()

cooc_w2 = build_cooccurrence_matrix(corpus, word_to_idx, window_size=2)
print(f"Co-occurrence matrix (window=2)")
header2 = "       " + "".join(f"{abbreviate(w):>7}" for w in vocab)
print(header2)
for i, w in enumerate(vocab):
    row = f"{abbreviate(w):>6} " + "".join(f"{cooc_w2[i][j]:>7}" for j in range(V))
    print(row)
print()

U2, S2, Vt2 = np.linalg.svd(cooc_w2.astype(float))
coords_w2 = U2[:, :k] * S2[:k]

print("2D coordinates (window=2):")
print(f"  {'word':>10}  {'x':>8}  {'y':>8}")
print(f"  {'-'*10}  {'-'*8}  {'-'*8}")
for i, w in enumerate(vocab):
    print(f"  {w:>10}  {coords_w2[i, 0]:>8.4f}  {coords_w2[i, 1]:>8.4f}")
print()

# Window 2 plot
fig2, ax2 = plt.subplots(1, 1, figsize=(10, 7))
ax2.scatter(coords_w2[:, 0], coords_w2[:, 1], c='darkgreen', s=60, zorder=5)
for i, w in enumerate(vocab):
    ax2.annotate(w, (coords_w2[i, 0], coords_w2[i, 1]),
                 fontsize=9, ha='center', va='bottom',
                 xytext=(0, 5), textcoords='offset points')
for w1, w2, color in highlight_pairs:
    if w1 in word_to_idx and w2 in word_to_idx:
        i1, i2 = word_to_idx[w1], word_to_idx[w2]
        ax2.plot([coords_w2[i1, 0], coords_w2[i2, 0]],
                 [coords_w2[i1, 1], coords_w2[i2, 1]],
                 '--', color=color, alpha=0.7, linewidth=1.5)
        mid_x = (coords_w2[i1, 0] + coords_w2[i2, 0]) / 2
        mid_y = (coords_w2[i1, 1] + coords_w2[i2, 1]) / 2
        dist = np.sqrt((coords_w2[i1, 0] - coords_w2[i2, 0])**2 +
                       (coords_w2[i1, 1] - coords_w2[i2, 1])**2)
        ax2.annotate(f"{w1}-{w2}\nd={dist:.3f}",
                     (mid_x, mid_y), fontsize=8, color=color,
                     ha='center', va='center',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                               edgecolor=color, alpha=0.8))
ax2.set_xlabel("SVD Dimension 1", fontsize=11)
ax2.set_ylabel("SVD Dimension 2", fontsize=11)
ax2.set_title("CS224N L01: Co-occurrence Matrix -> SVD 2D Projection (window=2)\n"
              f"Corpus: {len(corpus)} sentences, V={V}, window=2",
              fontsize=12)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='gray', linewidth=0.5, linestyle='-')
ax2.axvline(x=0, color='gray', linewidth=0.5, linestyle='-')
plt.tight_layout()
plot_w2_path = os.path.join(output_dir, "co-occurrence-matrix-svd-2d-window2.png")
plt.savefig(plot_w2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Plot saved: {plot_w2_path}")
print()

# ============================================================
# 第 7 步：距离对比
# ============================================================
print("Distance comparison (Euclidean in 2D SVD space):")
print(f"  {'pair':>15}  {'window=1':>10}  {'window=2':>10}")
print(f"  {'-'*15}  {'-'*10}  {'-'*10}")
for w1, w2, _ in highlight_pairs:
    if w1 in word_to_idx and w2 in word_to_idx:
        i1, i2 = word_to_idx[w1], word_to_idx[w2]
        d1 = np.sqrt(np.sum((coords_2d[i1] - coords_2d[i2])**2))
        d2 = np.sqrt(np.sum((coords_w2[i1] - coords_w2[i2])**2))
        print(f"  {w1+'-'+w2:>15}  {d1:>10.4f}  {d2:>10.4f}")
w1, w2 = "cat", "money"
i1, i2 = word_to_idx[w1], word_to_idx[w2]
d1 = np.sqrt(np.sum((coords_2d[i1] - coords_2d[i2])**2))
d2 = np.sqrt(np.sum((coords_w2[i1] - coords_w2[i2])**2))
print(f"  {w1+'-'+w2:>15}  {d1:>10.4f}  {d2:>10.4f}")
print()

# ============================================================
# 第 8 步：JSON 摘要
# ============================================================
summary = {
    "corpus_size": len(corpus),
    "vocab_size": V,
    "vocab": vocab,
    "window_1": {
        "window_size": 1,
        "nonzero": int(nnz),
        "total": int(total),
        "sparsity": round(float(sparsity), 4),
        "singular_values_k2": [round(float(s), 6) for s in S[:k]],
        "coords_2d": {w: [round(float(coords_2d[i, 0]), 6),
                           round(float(coords_2d[i, 1]), 6)]
                      for i, w in enumerate(vocab)},
        "distances": {}
    },
    "window_2": {
        "window_size": 2,
        "nonzero": int(np.count_nonzero(cooc_w2)),
        "total": int(total),
        "singular_values_k2": [round(float(s), 6) for s in S2[:k]],
        "coords_2d": {w: [round(float(coords_w2[i, 0]), 6),
                           round(float(coords_w2[i, 1]), 6)]
                      for i, w in enumerate(vocab)},
        "distances": {}
    }
}
for w1, w2, _ in highlight_pairs:
    if w1 in word_to_idx and w2 in word_to_idx:
        i1, i2 = word_to_idx[w1], word_to_idx[w2]
        d1 = float(np.sqrt(np.sum((coords_2d[i1] - coords_2d[i2])**2)))
        d2 = float(np.sqrt(np.sum((coords_w2[i1] - coords_w2[i2])**2)))
        key = f"{w1}-{w2}"
        summary["window_1"]["distances"][key] = round(d1, 6)
        summary["window_2"]["distances"][key] = round(d2, 6)
w1, w2 = "cat", "money"
i1, i2 = word_to_idx[w1], word_to_idx[w2]
d1 = float(np.sqrt(np.sum((coords_2d[i1] - coords_2d[i2])**2)))
d2 = float(np.sqrt(np.sum((coords_w2[i1] - coords_w2[i2])**2)))
summary["window_1"]["distances"][f"{w1}-{w2}"] = round(d1, 6)
summary["window_2"]["distances"][f"{w1}-{w2}"] = round(d2, 6)

summary_path = os.path.join(output_dir, "co-occurrence-matrix-summary.json")
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(f"Summary saved: {summary_path}")
print()
print("Done. Exit 0.")
