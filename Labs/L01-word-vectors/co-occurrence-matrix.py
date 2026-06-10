#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: co-occurrence-matrix
Waypoint: WP02 (Distributional Semantics)
Official anchor: Notes §3.1 (co-occurrence matrices); A1 Part 1 Q1.1-1.3

Demonstrates:
1. Building a co-occurrence matrix from a small toy corpus
2. Log-frequency weighting (Notes §3.1: "replace each count X_ij with log(1 + X_ij)")
3. SVD dimensionality reduction (truncated to k=2)
4. Visualization of co-occurrence matrix and 2D embeddings
5. Effect of window size on co-occurrence statistics
6. Cosine similarity between word vectors after SVD

All computations use numpy/scipy (no PyTorch/TensorFlow needed).
"""

import json
import os
import sys
import numpy as np
from collections import Counter, defaultdict

# ─────────────────────────────────────────────────────────────
# 1. TOY CORPUS — two semantic clusters
# ─────────────────────────────────────────────────────────────

CORPUS = [
    # Finance cluster
    "banking money finance economy",
    "money market invest finance",
    "banking invest market economy",
    "finance economy market money",
    "invest banking economy finance",
    "market economy banking money",
    # Nature cluster
    "river lake forest mountain",
    "lake ocean valley forest",
    "forest mountain river valley",
    "mountain valley ocean river",
    "ocean river lake mountain",
    "valley forest ocean lake",
    # Bridge sentences (share function words)
    "the banking river flows",
    "the forest economy grows",
]

print("=" * 70)
print("CS224N L01 — Code Capsule: co-occurrence-matrix (WP02)")
print("=" * 70)
print()
print(f"Corpus: {len(CORPUS)} sentences")
for i, sent in enumerate(CORPUS):
    print(f"  [{i:2d}] {sent}")
print()

# ─────────────────────────────────────────────────────────────
# 2. BUILD VOCABULARY
# ─────────────────────────────────────────────────────────────

def build_vocab(corpus):
    """Build sorted vocabulary from corpus."""
    counter = Counter()
    for sent in corpus:
        counter.update(sent.split())
    vocab = sorted(counter.keys())
    word2idx = {w: i for i, w in enumerate(vocab)}
    return vocab, word2idx, counter

vocab, word2idx, word_freq = build_vocab(CORPUS)
V = len(vocab)
print(f"Vocabulary size |V| = {V}")
print(f"Words: {vocab}")
print()

# ─────────────────────────────────────────────────────────────
# 3. BUILD CO-OCCURRENCE MATRIX
# ─────────────────────────────────────────────────────────────

def build_cooccurrence(corpus, word2idx, vocab_size, window_size=2):
    """
    Build co-occurrence matrix with given window size.
    X[i][j] = number of times word j appears within window_size of word i.
    Symmetric: we count both directions.
    """
    X = np.zeros((vocab_size, vocab_size), dtype=np.float64)
    
    for sent in corpus:
        tokens = sent.split()
        for center_pos, center_word in enumerate(tokens):
            if center_word not in word2idx:
                continue
            c_idx = word2idx[center_word]
            # Look at context window
            start = max(0, center_pos - window_size)
            end = min(len(tokens), center_pos + window_size + 1)
            for ctx_pos in range(start, end):
                if ctx_pos == center_pos:
                    continue
                ctx_word = tokens[ctx_pos]
                if ctx_word not in word2idx:
                    continue
                x_idx = word2idx[ctx_word]
                X[c_idx][x_idx] += 1.0
    
    return X

# Build with default window_size=2
WINDOW_SIZE = 2
X_raw = build_cooccurrence(CORPUS, word2idx, V, window_size=WINDOW_SIZE)

print(f"--- Co-occurrence Matrix (window_size={WINDOW_SIZE}) ---")
print(f"Matrix shape: ({V}, {V}) = {V*V} entries")
total_count = X_raw.sum()
nonzero = np.count_nonzero(X_raw)
sparsity = 1.0 - nonzero / (V * V)
print(f"Total co-occurrence count: {total_count:.0f}")
print(f"Nonzero entries: {nonzero}")
print(f"Sparsity: {sparsity:.1%}")
print()

# Print matrix as table
print("Co-occurrence matrix (raw counts):")
header = "         " + "".join(f"{w:>10s}" for w in vocab)
print(header)
for i, w in enumerate(vocab):
    row = f"{w:>8s}" + "".join(f"{X_raw[i][j]:10.0f}" for j in range(V))
    print(row)
print()

# ─────────────────────────────────────────────────────────────
# 4. LOG NORMALIZATION (Notes §3.1)
# ─────────────────────────────────────────────────────────────

X_log = np.log1p(X_raw)  # log(1 + x)

print("--- Log normalization: X_log = log(1 + X) ---")
print("(Notes §3.1: 'replace each count X_ij with log(1 + X_ij)')")
print(f"Max raw count: {X_raw.max():.0f}")
print(f"Max log count: {X_log.max():.4f}")
print(f"Example: raw count 5 -> log(1+5) = {np.log1p(5):.4f}")
print(f"Example: raw count 1 -> log(1+1) = {np.log1p(1):.4f}")
print()

# ─────────────────────────────────────────────────────────────
# 5. SVD DIMENSIONALITY REDUCTION
# ─────────────────────────────────────────────────────────────

from scipy.linalg import svd

K = 2  # target dimensions

U, s, Vt = svd(X_log, full_matrices=False)

# Truncate to k dimensions
U_k = U[:, :K]
s_k = s[:K]

# Word vectors = U_k * diag(s_k)  (each row is a word's k-dim vector)
word_vectors = U_k * s_k[np.newaxis, :]

print(f"--- SVD: {V}D -> {K}D ---")
print(f"Singular values (all): {s[:min(8, len(s))]}")
print(f"Top-{K} singular values: {s_k}")
print()

# Explained variance
total_var = np.sum(s**2)
explained_var = np.sum(s_k**2)
explained_ratio = explained_var / total_var
print(f"Total variance (sum of all sigma^2): {total_var:.4f}")
print(f"Top-{K} variance: {explained_var:.4f}")
print(f"Explained variance ratio: {explained_ratio:.1%}")
print()

# Print 2D coordinates
print(f"--- 2D Word Embeddings (after SVD, k={K}) ---")
print(f"{'Word':>12s}  {'dim0':>10s}  {'dim1':>10s}  {'norm':>10s}")
print("-" * 46)
for i, w in enumerate(vocab):
    vec = word_vectors[i]
    norm = np.linalg.norm(vec)
    print(f"{w:>12s}  {vec[0]:10.4f}  {vec[1]:10.4f}  {norm:10.4f}")
print()

# ─────────────────────────────────────────────────────────────
# 6. COSINE SIMILARITY
# ─────────────────────────────────────────────────────────────

def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return np.dot(a, b) / (norm_a * norm_b)

print("--- Cosine Similarities (after SVD k=2) ---")
print()

# Define semantic clusters for comparison
finance_words = ["banking", "money", "finance", "economy", "market", "invest"]
nature_words = ["river", "lake", "forest", "mountain", "valley", "ocean"]

# Filter to words actually in vocab
finance_words = [w for w in finance_words if w in word2idx]
nature_words = [w for w in nature_words if w in word2idx]

print("Within-cluster similarities (should be HIGH):")
print(f"{'Word A':>12s}  {'Word B':>12s}  {'cosine':>8s}")
print("-" * 36)
within_sims = []
for i in range(min(3, len(finance_words))):
    for j in range(i+1, min(3, len(finance_words))):
        w1, w2 = finance_words[i], finance_words[j]
        sim = cosine_sim(word_vectors[word2idx[w1]], word_vectors[word2idx[w2]])
        within_sims.append(sim)
        print(f"{w1:>12s}  {w2:>12s}  {sim:8.4f}")

for i in range(min(3, len(nature_words))):
    for j in range(i+1, min(3, len(nature_words))):
        w1, w2 = nature_words[i], nature_words[j]
        sim = cosine_sim(word_vectors[word2idx[w1]], word_vectors[word2idx[w2]])
        within_sims.append(sim)
        print(f"{w1:>12s}  {w2:>12s}  {sim:8.4f}")
print()

print("Cross-cluster similarities (should be LOWER):")
print(f"{'Word A':>12s}  {'Word B':>12s}  {'cosine':>8s}")
print("-" * 36)
cross_sims = []
for w1 in finance_words[:3]:
    for w2 in nature_words[:3]:
        sim = cosine_sim(word_vectors[word2idx[w1]], word_vectors[word2idx[w2]])
        cross_sims.append(sim)
        print(f"{w1:>12s}  {w2:>12s}  {sim:8.4f}")
print()

if within_sims and cross_sims:
    print(f"Mean within-cluster cosine:  {np.mean(within_sims):.4f}")
    print(f"Mean cross-cluster cosine:   {np.mean(cross_sims):.4f}")
    print(f"Difference:                  {np.mean(within_sims) - np.mean(cross_sims):.4f}")
    print()
    if np.mean(within_sims) > np.mean(cross_sims):
        print(">>> KEY OBSERVATION: Within-cluster similarity > Cross-cluster similarity")
        print(">>> Co-occurrence + SVD captures semantic clusters from raw counts alone!")
    else:
        print(">>> NOTE: With this tiny corpus, cluster separation may be weak.")
        print(">>> This is expected -- real corpora have thousands of sentences.")
print()

# ─────────────────────────────────────────────────────────────
# 7. WINDOW SIZE COMPARISON
# ─────────────────────────────────────────────────────────────

print("--- Window Size Comparison ---")
print()
for ws in [1, 2, 4]:
    X_ws = build_cooccurrence(CORPUS, word2idx, V, window_size=ws)
    nonzero_ws = np.count_nonzero(X_ws)
    sparsity_ws = 1.0 - nonzero_ws / (V * V)
    total_ws = X_ws.sum()
    
    # SVD on log-normalized
    X_log_ws = np.log1p(X_ws)
    U_ws, s_ws, Vt_ws = svd(X_log_ws, full_matrices=False)
    wv_ws = U_ws[:, :K] * s_ws[:K][np.newaxis, :]
    explained_ws = np.sum(s_ws[:K]**2) / np.sum(s_ws**2)
    
    # Sample cosine
    sim_finance = cosine_sim(wv_ws[word2idx["banking"]], wv_ws[word2idx["finance"]])
    sim_nature = cosine_sim(wv_ws[word2idx["river"]], wv_ws[word2idx["lake"]])
    sim_cross = cosine_sim(wv_ws[word2idx["banking"]], wv_ws[word2idx["river"]])
    
    print(f"Window size = {ws}:")
    print(f"  Total count: {total_ws:.0f}, Nonzero: {nonzero_ws}, Sparsity: {sparsity_ws:.1%}")
    print(f"  Explained variance (k=2): {explained_ws:.1%}")
    print(f"  cos(banking, finance) = {sim_finance:.4f}")
    print(f"  cos(river, lake)      = {sim_nature:.4f}")
    print(f"  cos(banking, river)   = {sim_cross:.4f}")
    print()

print(">>> Notes 3.1 insight: smaller window -> more syntactic info;")
print(">>> larger window -> more semantic/topic info.")
print()

# ─────────────────────────────────────────────────────────────
# 8. SAVE OUTPUTS
# ─────────────────────────────────────────────────────────────

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "outputs")
os.makedirs(output_dir, exist_ok=True)

# Save 2D coordinates as JSON
coords = {}
for i, w in enumerate(vocab):
    coords[w] = {
        "dim0": float(word_vectors[i, 0]),
        "dim1": float(word_vectors[i, 1]),
        "cluster": "finance" if w in finance_words else ("nature" if w in nature_words else "bridge")
    }

coords_path = os.path.join(output_dir, "co-occurrence-matrix-svd-coordinates.json")
with open(coords_path, "w") as f:
    json.dump({
        "window_size": WINDOW_SIZE,
        "vocab_size": V,
        "k": K,
        "explained_variance_ratio": float(explained_ratio),
        "singular_values_top_k": s_k.tolist(),
        "coordinates": coords,
        "matrix_stats": {
            "total_count": float(total_count),
            "nonzero_entries": int(nonzero),
            "sparsity": float(sparsity)
        }
    }, f, indent=2, ensure_ascii=False)
print(f"Saved coordinates: {coords_path}")

# ─────────────────────────────────────────────────────────────
# 9. VISUALIZATION
# ─────────────────────────────────────────────────────────────

import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt

# --- Plot 1: Co-occurrence matrix heatmap ---
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Raw counts
im1 = axes[0].imshow(X_raw, cmap='YlOrRd', aspect='auto')
axes[0].set_xticks(range(V))
axes[0].set_yticks(range(V))
axes[0].set_xticklabels(vocab, rotation=45, ha='right', fontsize=8)
axes[0].set_yticklabels(vocab, fontsize=8)
axes[0].set_title(f'Raw Co-occurrence Matrix (window={WINDOW_SIZE})\nTotal={total_count:.0f}, nonzero={nonzero}, sparsity={sparsity:.1%}')
plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)

# Log-normalized
im2 = axes[1].imshow(X_log, cmap='YlOrRd', aspect='auto')
axes[1].set_xticks(range(V))
axes[1].set_yticks(range(V))
axes[1].set_xticklabels(vocab, rotation=45, ha='right', fontsize=8)
axes[1].set_yticklabels(vocab, fontsize=8)
axes[1].set_title(f'Log-normalized: log(1 + X)\nmax raw={X_raw.max():.0f} -> max log={X_log.max():.4f}')
plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)

plt.tight_layout()
plot1_path = os.path.join(output_dir, "co-occurrence-matrix-heatmap.png")
fig.savefig(plot1_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved heatmap: {plot1_path}")

# --- Plot 2: 2D SVD embeddings scatter ---
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# Color by cluster
cluster_colors = {"finance": "#e74c3c", "nature": "#2ecc71", "bridge": "#95a5a6"}
cluster_markers = {"finance": "o", "nature": "s", "bridge": "^"}

for i, w in enumerate(vocab):
    cluster = coords[w]["cluster"]
    color = cluster_colors.get(cluster, "#333333")
    marker = cluster_markers.get(cluster, "o")
    ax.scatter(word_vectors[i, 0], word_vectors[i, 1], 
               c=color, marker=marker, s=100, zorder=5, edgecolors='white', linewidth=0.5)
    ax.annotate(w, (word_vectors[i, 0], word_vectors[i, 1]),
                fontsize=9, ha='center', va='bottom',
                xytext=(0, 8), textcoords='offset points')

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', markersize=10, label='Finance'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#2ecc71', markersize=10, label='Nature'),
    Line2D([0], [0], marker='^', color='w', markerfacecolor='#95a5a6', markersize=10, label='Bridge'),
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

ax.set_xlabel(f'Dimension 0 (s1={s_k[0]:.4f})', fontsize=11)
ax.set_ylabel(f'Dimension 1 (s2={s_k[1]:.4f})', fontsize=11)
ax.set_title(f'SVD 2D Embeddings (k={K}, explained variance={explained_ratio:.1%})\nCo-occurrence + log(1+x) + truncated SVD', fontsize=12)
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='--')
ax.axvline(x=0, color='gray', linewidth=0.5, linestyle='--')

plt.tight_layout()
plot2_path = os.path.join(output_dir, "co-occurrence-matrix-2d-embeddings.png")
fig.savefig(plot2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved 2D embeddings plot: {plot2_path}")

# --- Plot 3: Window size comparison ---
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, ws in enumerate([1, 2, 4]):
    X_ws = build_cooccurrence(CORPUS, word2idx, V, window_size=ws)
    X_log_ws = np.log1p(X_ws)
    U_ws, s_ws, Vt_ws = svd(X_log_ws, full_matrices=False)
    wv_ws = U_ws[:, :K] * s_ws[:K][np.newaxis, :]
    explained_ws = np.sum(s_ws[:K]**2) / np.sum(s_ws**2)
    
    ax = axes[idx]
    for i, w in enumerate(vocab):
        cluster = coords[w]["cluster"]
        color = cluster_colors.get(cluster, "#333333")
        marker = cluster_markers.get(cluster, "o")
        ax.scatter(wv_ws[i, 0], wv_ws[i, 1],
                   c=color, marker=marker, s=60, zorder=5, edgecolors='white', linewidth=0.3)
        ax.annotate(w, (wv_ws[i, 0], wv_ws[i, 1]),
                    fontsize=7, ha='center', va='bottom',
                    xytext=(0, 5), textcoords='offset points')
    
    ax.set_title(f'window={ws}\nexplained var={explained_ws:.1%}')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='--')
    ax.axvline(x=0, color='gray', linewidth=0.5, linestyle='--')

plt.suptitle('Effect of Window Size on SVD 2D Embeddings', fontsize=13, y=1.02)
plt.tight_layout()
plot3_path = os.path.join(output_dir, "co-occurrence-matrix-window-comparison.png")
fig.savefig(plot3_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved window comparison plot: {plot3_path}")

print()
print("=" * 70)
print("DONE -- All outputs saved to Labs/L01-word-vectors/outputs/")
print("=" * 70)
