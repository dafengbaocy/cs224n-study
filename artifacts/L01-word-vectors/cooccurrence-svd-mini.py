#!/usr/bin/env python3
"""
cooccurrence-svd-mini.py
========================
CS224N L01 Word Vectors — Code Capsule: cooccurrence-svd-mini (WP02)

Concept: Co-occurrence matrix construction and low-dimensional projection via SVD.

Official anchor:
  - notes §3.1 (co-occurrence matrix construction and window size)
  - A1 Part 1 cells on co-occurrence matrix and SVD

What this script does:
  1. Defines a tiny corpus with two semantic clusters (language vs computation).
  2. Builds a vocabulary and a co-occurrence matrix with window size 1.
  3. Prints the co-occurrence matrix (showing sparsity and count patterns).
  4. Applies truncated SVD (k=2) to reduce the matrix to 2D.
  5. Prints the 2D coordinates for each word.
  6. Generates a scatter plot showing the 2D word embeddings.

Why not just text:
  A1 Part 1 asks students to build co-occurrence vectors and apply SVD;
  a tiny runnable example makes the count matrix, sparsity, and
  dimensionality reduction visible before assignment work.
"""

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── 1. Tiny corpus with two semantic clusters ──────────────────────────────
#
# Cluster A (language/linguistics): word, meaning, language, sentence, grammar
# Cluster B (ML/computation): model, train, data, loss, gradient
# Bridge words: learn, vector (appear in both contexts)

corpus = [
    "word carries meaning",
    "sentence has grammar",
    "language uses grammar",
    "word forms sentence",
    "meaning in language",
    "grammar in sentence",
    "model needs data",
    "train the model",
    "loss drives gradient",
    "gradient updates model",
    "data feeds train",
    "model minimizes loss",
    "learn from data",
    "learn vector meaning",
    "vector from model",
]

print("=" * 60)
print("CS224N L01 — Co-occurrence Matrix & SVD (mini)")
print("=" * 60)
print()
print("## Corpus")
for i, sent in enumerate(corpus):
    print(f"  [{i:2d}] {sent}")
print()

# ── 2. Build vocabulary ────────────────────────────────────────────────────

tokenized = [sent.lower().split() for sent in corpus]

vocab_set = set()
for tokens in tokenized:
    vocab_set.update(tokens)
vocab = sorted(vocab_set)
word_to_idx = {w: i for i, w in enumerate(vocab)}
V = len(vocab)

print(f"## Vocabulary (size = {V})")
print(f"  {vocab}")
print()

# ── 3. Build co-occurrence matrix (window size = 1) ────────────────────────

WINDOW_SIZE = 1

cooccurrence_matrix = [[0] * V for _ in range(V)]

for tokens in tokenized:
    for i, center_word in enumerate(tokens):
        center_idx = word_to_idx[center_word]
        start = max(0, i - WINDOW_SIZE)
        end = min(len(tokens), i + WINDOW_SIZE + 1)
        for j in range(start, end):
            if i == j:
                continue
            context_word = tokens[j]
            context_idx = word_to_idx[context_word]
            cooccurrence_matrix[center_idx][context_idx] += 1

print(f"## Co-occurrence Matrix (window_size = {WINDOW_SIZE})")
print()

col_w = max(8, max(len(w) for w in vocab) + 1)
header = " " * col_w + "".join(f"{w:>{col_w}s}" for w in vocab)
print(header)
for i, w in enumerate(vocab):
    row_str = f"{w:>{col_w}s}" + "".join(f"{cooccurrence_matrix[i][j]:{col_w}d}" for j in range(V))
    print(row_str)
print()

# Sparsity analysis
total_entries = V * V
nonzero_entries = sum(1 for i in range(V) for j in range(V) if cooccurrence_matrix[i][j] > 0)
zero_entries = total_entries - nonzero_entries
sparsity = zero_entries / total_entries * 100

print(f"## Sparsity Analysis")
print(f"  Matrix size: {V} x {V} = {total_entries} entries")
print(f"  Non-zero entries: {nonzero_entries}")
print(f"  Zero entries: {zero_entries}")
print(f"  Sparsity: {sparsity:.1f}%")
print()

# ── 4. SVD ─────────────────────────────────────────────────────────────────

M = np.array(cooccurrence_matrix, dtype=np.float64)

K = 2
U, S, Vt = np.linalg.svd(M, full_matrices=False)

U_k = U[:, :K]
S_k = S[:K]

# Word embeddings: U_k * diag(S_k)
word_embeddings = U_k * S_k[np.newaxis, :]

print(f"## Truncated SVD (k = {K})")
print(f"  Singular values: [{S_k[0]:.4f}, {S_k[1]:.4f}]")
energy_total = sum(S**2)
energy_kept = sum(S_k**2)
print(f"  Energy retained: {energy_kept/energy_total*100:.1f}% of total")
print()

print(f"## 2D Word Embeddings (from SVD)")
print(f"  {'Word':>14s}  {'dim_0':>10s}  {'dim_1':>10s}")
print(f"  {'-'*14}  {'-'*10}  {'-'*10}")
for i, w in enumerate(vocab):
    print(f"  {w:>14s}  {word_embeddings[i, 0]:10.4f}  {word_embeddings[i, 1]:10.4f}")
print()

# ── 5. Cosine similarity of selected pairs ─────────────────────────────────

def cosine_sim(a, b):
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return float(dot / (norm_a * norm_b))

pairs = [
    ("word", "meaning", "same cluster (language)"),
    ("word", "sentence", "same cluster (language)"),
    ("model", "train", "same cluster (computation)"),
    ("loss", "gradient", "same cluster (computation)"),
    ("data", "model", "same cluster (computation)"),
    ("word", "model", "cross cluster"),
    ("grammar", "loss", "cross cluster"),
    ("sentence", "gradient", "cross cluster"),
]

print(f"## Cosine Similarities (from SVD 2D embeddings)")
print(f"  {'Pair':>26s}  {'cos_sim':>8s}  Note")
print(f"  {'-'*26}  {'-'*8}  {'-'*30}")
for w1, w2, note in pairs:
    i1 = word_to_idx[w1]
    i2 = word_to_idx[w2]
    sim = cosine_sim(word_embeddings[i1], word_embeddings[i2])
    print(f"  ({w1}, {w2}){' '*(26-len(f'({w1}, {w2})'))}{sim:8.4f}  {note}")
print()

# ── 6. Scatter plot ────────────────────────────────────────────────────────

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(output_dir, exist_ok=True)

fig, ax = plt.subplots(1, 1, figsize=(12, 9))

language_words = {"word", "meaning", "language", "sentence", "grammar"}
compute_words = {"model", "train", "data", "loss", "gradient"}
bridge_words = {"learn", "vector"}

for i, w in enumerate(vocab):
    x, y = word_embeddings[i, 0], word_embeddings[i, 1]
    if w in language_words:
        color, marker = '#2196F3', 'o'
    elif w in compute_words:
        color, marker = '#FF5722', 's'
    else:
        color, marker = '#4CAF50', '^'
    ax.scatter(x, y, s=120, c=color, marker=marker, zorder=5, edgecolors='black', linewidths=0.5)
    ax.annotate(w, (x, y), textcoords="offset points", xytext=(8, 5),
                fontsize=10, fontweight='bold')

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#2196F3', markersize=10, label='Language/Meaning'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#FF5722', markersize=10, label='Computation/Model'),
    Line2D([0], [0], marker='^', color='w', markerfacecolor='#4CAF50', markersize=10, label='Bridge words'),
]
ax.legend(handles=legend_elements, loc='best', fontsize=10)

ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='--')
ax.axvline(x=0, color='gray', linewidth=0.5, linestyle='--')

ax.set_xlabel("SVD Dimension 0", fontsize=12)
ax.set_ylabel("SVD Dimension 1", fontsize=12)
ax.set_title("Co-occurrence SVD: 2D Word Embeddings (window=1, k=2)\nCS224N L01 Code Capsule: cooccurrence-svd-mini",
             fontsize=13)
ax.grid(True, alpha=0.3)

plt.tight_layout()

plot_path = os.path.join(output_dir, "cooccurrence-svd-mini-scatter-2d.png")
fig.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.close(fig)

print(f"## Output Files")
print(f"  Scatter plot: {plot_path}")

# ── 7. Save structured output as JSON for provenance ───────────────────────

output_data = {
    "capsule": "cooccurrence-svd-mini",
    "waypoint": "WP02",
    "corpus": corpus,
    "vocab": vocab,
    "vocab_size": V,
    "window_size": WINDOW_SIZE,
    "svd_k": K,
    "singular_values": [round(float(s), 6) for s in S_k],
    "energy_retained_pct": round(float(energy_kept / energy_total * 100), 1),
    "cooccurrence_matrix": {
        "rows": vocab,
        "cols": vocab,
        "data": cooccurrence_matrix,
    },
    "sparsity": {
        "total_entries": total_entries,
        "nonzero_entries": nonzero_entries,
        "zero_entries": zero_entries,
        "sparsity_pct": round(sparsity, 1),
    },
    "word_embeddings_2d": {
        w: [round(float(word_embeddings[i, 0]), 6), round(float(word_embeddings[i, 1]), 6)]
        for i, w in enumerate(vocab)
    },
    "cosine_similarities": {
        f"({w1},{w2})": {
            "value": round(float(cosine_sim(word_embeddings[word_to_idx[w1]], word_embeddings[word_to_idx[w2]])), 6),
            "note": note
        }
        for w1, w2, note in pairs
    },
    "plot_path": plot_path,
}

json_path = os.path.join(output_dir, "cooccurrence-svd-mini-output.json")
with open(json_path, "w") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"  JSON output: {json_path}")
print()
print("Done.")
