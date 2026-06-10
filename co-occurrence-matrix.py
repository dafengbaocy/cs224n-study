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
3. Applying log normalization (Notes §3.1: "Taking the log... is much more useful")
4. Applying Truncated SVD to reduce dimensionality
5. Visualizing the 2D embeddings — showing cluster separation
6. Comparing window size effects (short → syntax, long → semantics)
"""

import numpy as np
from collections import Counter
import sys

# ============================================================
# 1. Toy Corpus — two clear semantic clusters
# ============================================================
# Finance cluster: banking, money, finance, economy, market, invest
# Nature cluster:  river, lake, forest, mountain, valley, ocean
# Function words: the, a, is, in, of, and, to, with

CORPUS = [
    # Finance sentences (6)
    "the banking system manages money and finance",
    "the economy depends on banking and finance",
    "money flows through the banking system",
    "the economy and finance are connected to the market",
    "invest in the banking market and finance",
    "the market economy depends on money and invest",
    # Nature sentences (6)
    "the river flows through the forest and valley",
    "the lake is near the mountain and forest",
    "a mountain rises above the lake and valley",
    "the forest surrounds the lake and river",
    "the river and lake are in the valley",
    "a mountain overlooks the river and ocean",
    # Bridge sentences (2) — share "flows" across clusters
    "the river flows like money through the economy",
    "invest in the ocean and the market",
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
            start = max(0, i - window_size)
            end = min(len(tokens), i + window_size + 1)
            for j in range(start, end):
                if i == j:
                    continue
                ctx = tokens[j]
                ctx_idx = word2idx[ctx]
                cooc[c_idx, ctx_idx] += 1
    
    return cooc

# Build with window=2 (standard for small corpora)
WINDOW = 2
print(f"--- Co-occurrence Matrix (window={WINDOW}) ---")
cooc_raw = build_cooccurrence(CORPUS, word2idx, window_size=WINDOW)

print(f"Shape: {cooc_raw.shape}")
print(f"Total co-occurrence count: {cooc_raw.sum()}")
print(f"Nonzero entries: {np.count_nonzero(cooc_raw)}")
print()

# Print compact matrix for content words only
content_words = [w for w in vocab_set if w not in {'the', 'a', 'is', 'in', 'of', 'and', 'to', 'with'}]
cw_indices = [word2idx[w] for w in content_words]

print("Co-occurrence sub-matrix (content words only):")
header = "          " + "".join(f"{w:>10s}" for w in content_words)
print(header)
for i, w in enumerate(content_words):
    row_vals = [cooc_raw[cw_indices[i], cw_indices[j]] for j in range(len(content_words))]
    row = f"{w:>10s}" + "".join(f"{v:10d}" for v in row_vals)
    print(row)
print()

# Show non-zero co-occurrences for key content words
print(f"Non-zero co-occurrences for key words (window={WINDOW}, all vocab):")
key_words = ['banking', 'money', 'finance', 'economy', 'river', 'lake', 'forest', 'mountain']
for w in key_words:
    idx = word2idx[w]
    neighbors = [(idx2word[j], cooc_raw[idx, j]) for j in range(V) if cooc_raw[idx, j] > 0]
    neighbors.sort(key=lambda x: -x[1])
    print(f"  {w:>10s}: {neighbors}")
print()

# ============================================================
# 4. Log Normalization (Notes §3.1)
# ============================================================
# Notes §3.1: "Taking the log token frequency ends up being much more useful"
# Standard approach: X_ij = log(1 + X_ij) to dampen high-frequency words
cooc_log = np.log1p(cooc_raw.astype(float))

print("--- Log Normalization ---")
print("Before log: max =", cooc_raw.max(), ", mean (nonzero) =", 
      f"{cooc_raw[cooc_raw > 0].mean():.2f}")
print("After log:  max =", f"{cooc_log.max():.4f}", ", mean (nonzero) =",
      f"{cooc_log[cooc_log > 0].mean():.4f}")
print()

# ============================================================
# 5. SVD Dimensionality Reduction
# ============================================================
def svd_reduce(matrix, k=2):
    """
    Truncated SVD: keep top-k singular values/vectors.
    Returns reduced matrix of shape (V, k).
    """
    U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
    reduced = U[:, :k] * S[:k]  # (V, k)
    return reduced, S

k = 2
embeddings_raw, sv_raw = svd_reduce(cooc_raw.astype(float), k=k)
embeddings_log, sv_log = svd_reduce(cooc_log, k=k)

print(f"--- SVD Reduction to {k}D ---")
print(f"Raw co-occurrence singular values (top 6): {sv_raw[:6].round(3)}")
print(f"  Top-{k} explained variance: {(sv_raw[:k]**2 / (sv_raw**2).sum() * 100).round(1)}%")
print(f"Log-normalized singular values (top 6): {sv_log[:6].round(3)}")
print(f"  Top-{k} explained variance: {(sv_log[:k]**2 / (sv_log**2).sum() * 100).round(1)}%")
print()

# Use log-normalized embeddings for the main analysis
print(f"2D Embeddings (log-normalized, window={WINDOW}):")
for w in content_words:
    i = word2idx[w]
    print(f"  {w:>10s}: [{embeddings_log[i, 0]:8.4f}, {embeddings_log[i, 1]:8.4f}]")
print()

# ============================================================
# 6. Cosine Similarity
# ============================================================
def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

print("--- Cosine Similarities (log-normalized SVD, 2D) ---")
pairs = [
    ("banking", "finance",   "same cluster (finance)"),
    ("banking", "money",     "same cluster (finance)"),
    ("banking", "economy",   "same cluster (finance)"),
    ("river",   "lake",      "same cluster (nature)"),
    ("river",   "forest",    "same cluster (nature)"),
    ("lake",    "valley",    "same cluster (nature)"),
    ("banking", "river",     "CROSS cluster"),
    ("finance", "mountain",  "CROSS cluster"),
    ("money",   "ocean",     "CROSS cluster"),
]
for w1, w2, label in pairs:
    sim = cosine_sim(embeddings_log[word2idx[w1]], embeddings_log[word2idx[w2]])
    print(f"  sim({w1:>10s}, {w2:>10s}) = {sim:.4f}  [{label}]")
print()

# ============================================================
# 7. Window Size Comparison
# ============================================================
print("--- Window Size Comparison (log-normalized SVD) ---")
print(f"  {'Window':>6s}  {'banking-money':>14s}  {'river-lake':>14s}  {'banking-forest':>15s}")
window_sizes = [1, 2, 3]
all_sims = {}
for ws in window_sizes:
    cooc_ws = build_cooccurrence(CORPUS, word2idx, window_size=ws)
    cooc_ws_log = np.log1p(cooc_ws.astype(float))
    emb_ws, _ = svd_reduce(cooc_ws_log, k=k)
    
    sim_bm = cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["money"]])
    sim_rl = cosine_sim(emb_ws[word2idx["river"]], emb_ws[word2idx["lake"]])
    sim_bf = cosine_sim(emb_ws[word2idx["banking"]], emb_ws[word2idx["forest"]])
    all_sims[ws] = (sim_bm, sim_rl, sim_bf)
    
    print(f"  {ws:>6d}  {sim_bm:>14.4f}  {sim_rl:>14.4f}  {sim_bf:>15.4f}")

print()
print("Interpretation:")
print("  - Short window (1): captures syntactic context → words in similar grammatical roles cluster")
print("  - Medium window (2): balances syntax and semantics → clear cluster separation")
print("  - Large window (3+): captures topic/semantics → more words share broad topic context")
print()

# ============================================================
# 8. Visualization
# ============================================================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

finance_words = ['banking', 'money', 'finance', 'economy', 'market', 'invest']
nature_words = ['river', 'lake', 'forest', 'mountain', 'valley', 'ocean']

# 8a. Overview: matrix heatmap + 2D scatter + window comparison
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Heatmap of co-occurrence matrix (content words only)
sub_matrix = cooc_raw[np.ix_(cw_indices, cw_indices)]
im = axes[0].imshow(sub_matrix, cmap='YlOrRd', aspect='auto')
axes[0].set_title(f'Co-occurrence Matrix (window={WINDOW}, content words)', fontsize=11)
axes[0].set_xticks(range(len(content_words)))
axes[0].set_yticks(range(len(content_words)))
axes[0].set_xticklabels(content_words, rotation=90, fontsize=8)
axes[0].set_yticklabels(content_words, fontsize=8)
plt.colorbar(im, ax=axes[0], fraction=0.046)

# 2D embedding scatter plot (log-normalized)
for w in content_words:
    i = word2idx[w]
    x, y = embeddings_log[i, 0], embeddings_log[i, 1]
    if w in finance_words:
        color, marker = '#e74c3c', 'o'
    elif w in nature_words:
        color, marker = '#2ecc71', 's'
    else:
        color, marker = '#f39c12', 'D'
    axes[1].scatter(x, y, c=color, marker=marker, s=100, zorder=5, edgecolors='black', linewidth=0.5)
    axes[1].annotate(w, (x, y), fontsize=9, fontweight='bold', ha='center', va='bottom',
                     xytext=(0, 6), textcoords='offset points')

axes[1].set_title(f'SVD 2D Embeddings (log-normalized, window={WINDOW})', fontsize=11)
axes[1].set_xlabel('SVD Component 1')
axes[1].set_ylabel('SVD Component 2')
axes[1].grid(True, alpha=0.3)
axes[1].axhline(y=0, color='k', linewidth=0.5, linestyle='--')
axes[1].axvline(x=0, color='k', linewidth=0.5, linestyle='--')

# Add legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', markersize=10, label='Finance'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#2ecc71', markersize=10, label='Nature'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='#f39c12', markersize=10, label='Other'),
]
axes[1].legend(handles=legend_elements, fontsize=9, loc='upper right')

# Window size comparison bar chart
x_pos = np.arange(len(window_sizes))
width = 0.25
sim_bank_money = [all_sims[ws][0] for ws in window_sizes]
sim_river_lake = [all_sims[ws][1] for ws in window_sizes]
sim_cross = [all_sims[ws][2] for ws in window_sizes]

axes[2].bar(x_pos - width, sim_bank_money, width, label='banking-money\n(same cluster)', color='#e74c3c', alpha=0.8)
axes[2].bar(x_pos, sim_river_lake, width, label='river-lake\n(same cluster)', color='#2ecc71', alpha=0.8)
axes[2].bar(x_pos + width, sim_cross, width, label='banking-forest\n(cross cluster)', color='#3498db', alpha=0.8)
axes[2].set_title('Window Size Effect on Cosine Similarity', fontsize=11)
axes[2].set_xlabel('Window Size')
axes[2].set_ylabel('Cosine Similarity')
axes[2].set_xticks(x_pos)
axes[2].set_xticklabels([f'w={ws}' for ws in window_sizes])
axes[2].legend(fontsize=8)
axes[2].set_ylim(-0.5, 1.1)
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('Labs/L01-word-vectors/outputs/co-occurrence-matrix-overview.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: Labs/L01-word-vectors/outputs/co-occurrence-matrix-overview.png")

# 8b. Detailed 2D scatter with cluster regions
fig2, ax2 = plt.subplots(figsize=(10, 8))

from matplotlib.patches import Ellipse

# Finance cluster ellipse
fin_pts = np.array([embeddings_log[word2idx[w]] for w in finance_words])
fin_center = fin_pts.mean(axis=0)
fin_std = fin_pts.std(axis=0) + 0.3
ellipse_fin = Ellipse(fin_center, fin_std[0]*4, fin_std[1]*4, alpha=0.12, color='#e74c3c', label='Finance cluster')
ax2.add_patch(ellipse_fin)

# Nature cluster ellipse
nat_pts = np.array([embeddings_log[word2idx[w]] for w in nature_words])
nat_center = nat_pts.mean(axis=0)
nat_std = nat_pts.std(axis=0) + 0.3
ellipse_nat = Ellipse(nat_center, nat_std[0]*4, nat_std[1]*4, alpha=0.12, color='#2ecc71', label='Nature cluster')
ax2.add_patch(ellipse_nat)

# Plot all content words
for w in content_words:
    i = word2idx[w]
    x, y = embeddings_log[i, 0], embeddings_log[i, 1]
    if w in finance_words:
        color, marker, sz = '#e74c3c', 'o', 120
    elif w in nature_words:
        color, marker, sz = '#2ecc71', 's', 120
    else:
        color, marker, sz = '#f39c12', 'D', 80
    ax2.scatter(x, y, c=color, marker=marker, s=sz, zorder=5, edgecolors='black', linewidth=0.5)
    ax2.annotate(w, (x, y), fontsize=10, fontweight='bold', ha='center', va='bottom',
                 xytext=(0, 8), textcoords='offset points')

ax2.set_title(f'Co-occurrence + SVD: 2D Word Embeddings\n(log-normalized, window={WINDOW}, k={k})\nFinance (red) vs Nature (green) — clusters separate!', fontsize=13)
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
# 9. Summary statistics for provenance
# ============================================================
print()
print("=" * 60)
print("SUMMARY STATISTICS")
print("=" * 60)
print(f"Corpus: {len(CORPUS)} sentences, {len(all_tokens)} tokens, |V|={V}")
print(f"Matrix shape: {cooc_raw.shape}")
print(f"Matrix total count: {cooc_raw.sum()}")
print(f"Matrix nonzero entries: {np.count_nonzero(cooc_raw)}")
print(f"Log-normalized SVD singular values (top 6): {sv_log[:6].round(4)}")
print(f"Top-{k} explained variance: {(sv_log[:k]**2 / (sv_log**2).sum() * 100).round(1)}%")
print()
print("Key cosine similarities (log-normalized, window=2, 2D SVD):")
for w1, w2, label in pairs:
    sim = cosine_sim(embeddings_log[word2idx[w1]], embeddings_log[word2idx[w2]])
    print(f"  cos({w1}, {w2}) = {sim:.4f}  [{label}]")
print()
print("Window size effect (log-normalized):")
for ws in window_sizes:
    bm, rl, bf = all_sims[ws]
    print(f"  w={ws}: banking-money={bm:.4f}, river-lake={rl:.4f}, banking-forest={bf:.4f}")
print()
print("DONE")
