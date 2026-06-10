#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: co-occurrence-matrix
Waypoint: WP02 (Distributional Semantics)
Concept: Build a co-occurrence matrix from a small corpus, then apply SVD
         to obtain low-dimensional word vectors. Visualize the result.

Official anchor: Notes §3.1 (co-occurrence matrices); A1 Part 1 Q1.1-1.3

This script demonstrates:
1. Building a vocabulary from a toy corpus
2. Constructing a co-occurrence matrix with a sliding window
3. Applying Truncated SVD to reduce dimensionality
4. Visualizing the 2D embeddings
5. Comparing window size effects (short → syntax, long → semantics)
"""

import numpy as np
from collections import Counter, defaultdict
import json
import sys

# ============================================================
# 1. Toy Corpus
# ============================================================
# A small corpus with clear semantic clusters:
#   - Finance cluster: banking, money, finance, economy
#   - Nature cluster: river, lake, forest, mountain
#   - Common words: the, a, is, in, of, and

CORPUS = [
    "the banking system manages money and finance",
    "the economy depends on banking and finance",
    "money flows through the banking system",
    "the economy and finance are connected",
    "the river flows through the forest",
    "the lake is near the mountain and forest",
    "a mountain rises above the lake and river",
    "the forest surrounds the lake and river",
    "the river and lake are in the forest",
    "a mountain overlooks the river",
]

print("=" * 60)
print("CS224N L01 — Code Capsule: co-occurrence-matrix")
print("Waypoint WP02: Distributional Semantics")
print("=" * 60)
print()

# ============================================================
# 2. Build Vocabulary
# ============================================================
def tokenize(text):
    """Simple whitespace + lowercase tokenizer."""
    return text.lower().split()

all_tokens = []
for sent in CORPUS:
    all_tokens.extend(tokenize(sent))

vocab_set = sorted(set(all_tokens))
word2idx = {w: i for i, w in enumerate(vocab_set)}
idx2word = {i: w for w, i in word2idx.items()}
V = len(vocab_set)

print(f"Corpus: {len(CORPUS)} sentences, {len(all_tokens)} tokens")
print(f"Vocabulary size |V| = {V}")
print(f"Vocabulary: {vocab_set}")
print()

# ============================================================
# 3. Build Co-occurrence Matrix
# ============================================================
def build_cooccurrence(corpus, word2idx, window_size):
    """
    Build a symmetric co-occurrence matrix.
    For each center word, count words within `window_size` positions.
    """
    V = len(word2idx)
    cooc = np.zeros((V, V), dtype=int)
    
    for sent in corpus:
        tokens = tokenize(sent)
        for i, center in enumerate(tokens):
            c_idx = word2idx[center]
            # Look at context within window
            start = max(0, i - window_size)
            end = min(len(tokens), i + window_size + 1)
            for j in range(start, end):
                if i == j:
                    continue
                ctx = tokens[j]
                ctx_idx = word2idx[ctx]
                cooc[c_idx, ctx_idx] += 1
    
    return cooc

# Build with window=1 (captures syntax: nearby function words)
print("--- Co-occurrence Matrix (window=1) ---")
cooc_w1 = build_cooccurrence(CORPUS, word2idx, window_size=1)

# Print matrix with labels
print(f"Shape: {cooc_w1.shape}")
print()

# Print as a readable table
header = "          " + "".join(f"{w:>10s}" for w in vocab_set[:10])
if V > 10:
    header += "".join(f"{w:>10s}" for w in vocab_set[10:])
print(header)
for i, w in enumerate(vocab_set):
    row = f"{w:>10s}" + "".join(f"{cooc_w1[i,j]:10d}" for j in range(V))
    print(row)
print()

# Show non-zero entries for key content words
print("Non-zero co-occurrences for content words (window=1):")
content_words = [w for w in vocab_set if w not in {'the', 'a', 'is', 'in', 'of', 'and'}]
for w in content_words:
    idx = word2idx[w]
    neighbors = [(idx2word[j], cooc_w1[idx, j]) for j in range(V) if cooc_w1[idx, j] > 0]
    neighbors.sort(key=lambda x: -x[1])
    print(f"  {w:>10s}: {neighbors}")
print()

# ============================================================
# 4. SVD Dimensionality Reduction
# ============================================================
def svd_reduce(matrix, k=2):
    """
    Truncated SVD: keep top-k singular values/vectors.
    Returns reduced matrix of shape (V, k).
    """
    U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
    # Truncate to k components
    reduced = U[:, :k] * S[:k]  # (V, k)
    return reduced, S

k = 2
embeddings_w1, singular_values = svd_reduce(cooc_w1.astype(float), k=k)

print(f"--- SVD Reduction to {k}D ---")
print(f"Singular values (top 6): {singular_values[:6].round(3)}")
print(f"Explained variance ratio: {(singular_values[:k]**2 / (singular_values**2).sum() * 100).round(1)}%")
print()

print(f"2D Embeddings (window=1):")
for i, w in enumerate(vocab_set):
    print(f"  {w:>10s}: [{embeddings_w1[i, 0]:8.4f}, {embeddings_w1[i, 1]:8.4f}]")
print()

# ============================================================
# 5. Cosine Similarity
# ============================================================
def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return np.dot(a, b) / (norm_a * norm_b)

print("--- Cosine Similarities (window=1, 2D SVD) ---")
pairs = [
    ("banking", "finance"),
    ("banking", "money"),
    ("river", "lake"),
    ("river", "forest"),
    ("banking", "river"),     # cross-cluster (should be lower)
    ("finance", "mountain"),  # cross-cluster (should be lower)
    ("the", "a"),             # function words
]
for w1, w2 in pairs:
    sim = cosine_sim(embeddings_w1[word2idx[w1]], embeddings_w1[word2idx[w2]])
    print(f"  sim({w1:>10s}, {w2:>10s}) = {sim:.4f}")
print()

# ============================================================
# 6. Window Size Comparison
# ============================================================
print("--- Window Size Comparison ---")
for ws in [1, 2, 3]:
    cooc_ws = build_cooccurrence(CORPUS, word2idx, window_size=ws)
    emb_ws, sv_ws = svd_reduce(cooc_ws.astype(float), k=k)
    
    # Key comparisons
    sim_bf = cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["forest"]])
    sim_bm = cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["money"]])
    sim_rl = cosine_sim(emb_ws[word2idx["river"]], emb_ws[word2idx["lake"]])
    
    print(f"  Window={ws}: sim(banking,money)={sim_bm:.4f}  sim(river,lake)={sim_rl:.4f}  sim(banking,forest)={sim_bf:.4f}")

print()

# ============================================================
# 7. Visualization
# ============================================================
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt

# 7a. Co-occurrence matrix heatmap
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Heatmap of co-occurrence matrix (window=1)
im = axes[0].imshow(cooc_w1, cmap='YlOrRd', aspect='auto')
axes[0].set_title('Co-occurrence Matrix (window=1)', fontsize=12)
axes[0].set_xticks(range(V))
axes[0].set_yticks(range(V))
axes[0].set_xticklabels(vocab_set, rotation=90, fontsize=7)
axes[0].set_yticklabels(vocab_set, fontsize=7)
plt.colorbar(im, ax=axes[0], fraction=0.046)

# 7b. 2D embedding scatter plot
for i, w in enumerate(vocab_set):
    x, y = embeddings_w1[i, 0], embeddings_w1[i, 1]
    # Color by cluster
    if w in ['banking', 'money', 'finance', 'economy']:
        color = '#e74c3c'  # red for finance
        marker = 'o'
    elif w in ['river', 'lake', 'forest', 'mountain']:
        color = '#2ecc71'  # green for nature
        marker = 's'
    else:
        color = '#95a5a6'  # gray for function words
        marker = '^'
    axes[1].scatter(x, y, c=color, marker=marker, s=80, zorder=5)
    axes[1].annotate(w, (x, y), fontsize=8, ha='center', va='bottom',
                     xytext=(0, 5), textcoords='offset points')

axes[1].set_title(f'SVD 2D Embeddings (window=1, k={k})', fontsize=12)
axes[1].set_xlabel(f'Component 1')
axes[1].set_ylabel(f'Component 2')
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=0, color='k', linewidth=0.5, linestyle='--')
axes[1].axvline(x=0, color='k', linewidth=0.5, linestyle='--')

# 7c. Window size comparison: bar chart of similarities
window_sizes = [1, 2, 3]
sim_bank_money = []
sim_river_lake = []
sim_cross = []
for ws in window_sizes:
    cooc_ws = build_cooccurrence(CORPUS, word2idx, window_size=ws)
    emb_ws, _ = svd_reduce(cooc_ws.astype(float), k=k)
    sim_bank_money.append(cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["money"]]))
    sim_river_lake.append(cosine_sim(emb_ws[word2idx["river"]], emb_ws[word2idx["lake"]]))
    sim_cross.append(cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["forest"]]))

x_pos = np.arange(len(window_sizes))
width = 0.25
axes[2].bar(x_pos - width, sim_bank_money, width, label='banking-money\n(same cluster)', color='#e74c3c', alpha=0.8)
axes[2].bar(x_pos, sim_river_lake, width, label='river-lake\n(same cluster)', color='#2ecc71', alpha=0.8)
axes[2].bar(x_pos + width, sim_cross, width, label='banking-forest\n(cross cluster)', color='#3498db', alpha=0.8)
axes[2].set_title('Window Size Effect on Similarity', fontsize=12)
axes[2].set_xlabel('Window Size')
axes[2].set_ylabel('Cosine Similarity')
axes[2].set_xticks(x_pos)
axes[2].set_xticklabels([f'w={ws}' for ws in window_sizes])
axes[2].legend(fontsize=8)
axes[2].set_ylim(-0.2, 1.1)
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('Labs/L01-word-vectors/outputs/co-occurrence-matrix-overview.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: Labs/L01-word-vectors/outputs/co-occurrence-matrix-overview.png")

# 7d. Detailed 2D scatter with cluster highlighting
fig2, ax2 = plt.subplots(figsize=(10, 8))

# Draw convex hulls / ellipses for clusters
from matplotlib.patches import Ellipse

finance_words = ['banking', 'money', 'finance', 'economy']
nature_words = ['river', 'lake', 'forest', 'mountain']

# Finance cluster
fin_pts = np.array([embeddings_w1[word2idx[w]] for w in finance_words])
fin_center = fin_pts.mean(axis=0)
fin_std = fin_pts.std(axis=0)
ellipse_fin = Ellipse(fin_center, fin_std[0]*4, fin_std[1]*4, alpha=0.15, color='#e74c3c', label='Finance cluster')
ax2.add_patch(ellipse_fin)

# Nature cluster
nat_pts = np.array([embeddings_w1[word2idx[w]] for w in nature_words])
nat_center = nat_pts.mean(axis=0)
nat_std = nat_pts.std(axis=0)
ellipse_nat = Ellipse(nat_center, nat_std[0]*4, nat_std[1]*4, alpha=0.15, color='#2ecc71', label='Nature cluster')
ax2.add_patch(ellipse_nat)

# Plot all words
for i, w in enumerate(vocab_set):
    x, y = embeddings_w1[i, 0], embeddings_w1[i, 1]
    if w in finance_words:
        color, marker, sz = '#e74c3c', 'o', 120
    elif w in nature_words:
        color, marker, sz = '#2ecc71', 's', 120
    else:
        color, marker, sz = '#95a5a6', '^', 60
    ax2.scatter(x, y, c=color, marker=marker, s=sz, zorder=5, edgecolors='black', linewidth=0.5)
    ax2.annotate(w, (x, y), fontsize=10, fontweight='bold', ha='center', va='bottom',
                 xytext=(0, 8), textcoords='offset points')

ax2.set_title('Co-occurrence + SVD: 2D Word Embeddings (window=1)\nFinance cluster (red) vs Nature cluster (green)', fontsize=13)
ax2.set_xlabel('SVD Component 1', fontsize=11)
ax2.set_ylabel('SVD Component 2', fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='k', linewidth=0.5, linestyle='--')
ax2.axvline(x=0, color='k', linewidth=0.5, linestyle='--')
ax2.legend(fontsize=10, loc='upper right')

plt.tight_layout()
plt.savefig('Labs/L01-word-vectors/outputs/co-occurrence-matrix-2d-embeddings.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: Labs/L01-word-vectors/outputs/co-occurrence-matrix-2d-embeddings.png")

# ============================================================
# 8. Summary statistics for provenance
# ============================================================
print()
print("=" * 60)
print("SUMMARY STATISTICS")
print("=" * 60)
print(f"Matrix shape: {cooc_w1.shape}")
print(f"Matrix total count: {cooc_w1.sum()}")
print(f"Matrix nonzero entries: {np.count_nonzero(cooc_w1)}")
print(f"Singular values (all): {singular_values.round(4)}")
print(f"Top-{k} explained variance: {(singular_values[:k]**2 / (singular_values**2).sum() * 100).round(1)}%")
print()
print("Key cosine similarities (window=1, 2D SVD):")
for w1, w2 in pairs:
    sim = cosine_sim(embeddings_w1[word2idx[w1]], embeddings_w1[word2idx[w2]])
    print(f"  cos({w1}, {w2}) = {sim:.4f}")
print()
print("Window size effect:")
for ws in window_sizes:
    print(f"  w={ws}: banking-money={sim_bank_money[ws-1]:.4f}, river-lake={sim_river_lake[ws-1]:.4f}, banking-forest={sim_cross[ws-1]:.4f}")
print()
print("DONE")
