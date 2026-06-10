#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: pretrained-analogy (WP05)

Demonstrates pretrained word vector properties using a hand-crafted toy
embedding (d=10, 24 words) where semantic relationships are encoded as
vector directions — mimicking how real pretrained vectors (GloVe, word2vec)
capture relational structure.

Sections:
  1. Build toy embedding with relational structure
  2. Cosine similarity between word pairs
  3. Word analogy via vector arithmetic (king - man + woman ≈ queen)
  4. Nearest-neighbor queries
  5. Failure / bias case
  6. 2D PCA visualization

Official anchor: A1 Part 2 (GloVe vectors, cosine similarity, analogy
and bias questions); slides p9 "Looking at word vectors"; R02 compositionality.

Usage:
  python pretrained-analogy.py

Outputs saved to: outputs/
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
import json
import sys

np.random.seed(42)
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

# =============================================================================
# 1. Build a toy embedding where relational structure exists
# =============================================================================
# Design: each word = base_concept + gender_offset + royalty_offset + ...
# This mimics how real pretrained vectors encode linear relational structure.

DIM = 10
words_list = [
    # (word, base_vec_seed, gender, royalty, family, animacy)
    # gender: -1=female, 0=neutral, +1=male
    # royalty: 0=no, 1=yes
    # family: 0=no, 1=yes
    # animacy: 0=object/concept, 1=animate
    ("man",      0,  1, 0, 0, 1),
    ("woman",    0, -1, 0, 0, 1),
    ("king",     1,  1, 1, 0, 1),
    ("queen",    1, -1, 1, 0, 1),
    ("boy",      2,  1, 0, 1, 1),
    ("girl",     2, -1, 0, 1, 1),
    ("father",   3,  1, 0, 1, 1),
    ("mother",   3, -1, 0, 1, 1),
    ("uncle",    4,  1, 0, 1, 1),
    ("aunt",     4, -1, 0, 1, 1),
    ("prince",   5,  1, 1, 1, 1),
    ("princess", 5, -1, 1, 1, 1),
    ("dog",      6,  0, 0, 0, 1),
    ("cat",      7,  0, 0, 0, 1),
    ("fish",     8,  0, 0, 0, 1),
    ("car",      9,  0, 0, 0, 0),
    ("truck",   10,  0, 0, 0, 0),
    ("bicycle", 11,  0, 0, 0, 0),
    ("paris",   12,  0, 0, 0, 0),
    ("london",  13,  0, 0, 0, 0),
    ("tokyo",   14,  0, 0, 0, 0),
    ("apple",   15,  0, 0, 0, 0),
    ("banana",  16,  0, 0, 0, 0),
    ("orange",  17,  0, 0, 0, 0),
]

# Build base vectors from seeds (random but deterministic)
base_vectors = {}
for w, seed, *_ in words_list:
    r = np.random.RandomState(seed * 7 + 13)
    base_vectors[w] = r.randn(DIM) * 0.5

# Semantic direction vectors (shared across words with that attribute)
gender_dir = np.array([1.8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
royalty_dir = np.array([0.0, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
family_dir = np.array([0.0, 0.0, 1.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
animacy_dir = np.array([0.0, 0.0, 0.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

# Category cluster offsets (so animals cluster, vehicles cluster, etc.)
category_offsets = {
    "animal": np.array([0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "vehicle": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0]),
    "city": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0]),
    "fruit": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0]),
}

word_to_category = {
    "dog": "animal", "cat": "animal", "fish": "animal",
    "man": "animal", "woman": "animal", "king": "animal", "queen": "animal",
    "boy": "animal", "girl": "animal", "father": "animal", "mother": "animal",
    "uncle": "animal", "aunt": "animal", "prince": "animal", "princess": "animal",
    "car": "vehicle", "truck": "vehicle", "bicycle": "vehicle",
    "paris": "city", "london": "city", "tokyo": "city",
    "apple": "fruit", "banana": "fruit", "orange": "fruit",
}

# Build final vectors
embeddings = {}
word_order = []
for w, _, gender, royalty, family, animacy in words_list:
    vec = base_vectors[w].copy()
    vec += gender * gender_dir
    vec += royalty * royalty_dir
    vec += family * family_dir
    vec += animacy * animacy_dir
    cat = word_to_category.get(w)
    if cat and cat in category_offsets:
        vec += category_offsets[cat]
    embeddings[w] = vec
    word_order.append(w)

# Build matrix: shape (n_words, dim)
vocab = word_order
emb_matrix = np.array([embeddings[w] for w in vocab])

print("=" * 70)
print("CS224N L01 — Code Capsule: pretrained-analogy (WP05)")
print("=" * 70)
print(f"\nVocabulary size: {len(vocab)}")
print(f"Embedding dimension: {DIM}")
print(f"Words: {vocab}")
print()

# =============================================================================
# Helper functions
# =============================================================================

def cosine_similarity(a, b):
    """Cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def cosine_sim_matrix(matrix):
    """Pairwise cosine similarity matrix."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    normalized = matrix / norms
    return normalized @ normalized.T

def nearest_neighbors(word, matrix, vocab, k=5):
    """Find k nearest neighbors by cosine similarity (excluding the word itself)."""
    idx = vocab.index(word)
    sims = cosine_sim_matrix(matrix)[idx]
    # Exclude self
    sims_copy = sims.copy()
    sims_copy[idx] = -999
    top_k = np.argsort(sims_copy)[::-1][:k]
    return [(vocab[i], sims[i]) for i in top_k]

def analogy(a, b, c, matrix, vocab, k=5):
    """Solve analogy a:b :: c:?  →  result = vec(b) - vec(a) + vec(c)"""
    target = matrix[vocab.index(b)] - matrix[vocab.index(a)] + matrix[vocab.index(c)]
    # Compute cosine similarity between target and each word
    target_norm = np.linalg.norm(target)
    sims = np.array([np.dot(target, matrix[i]) / (target_norm * np.linalg.norm(matrix[i]))
                     for i in range(len(vocab))])
    # Exclude a, b, c
    exclude = {vocab.index(w) for w in [a, b, c] if w in vocab}
    sims_copy = sims.copy()
    for i in exclude:
        sims_copy[i] = -999
    top_k = np.argsort(sims_copy)[::-1][:k]
    return [(vocab[i], sims[i]) for i in top_k], target

# =============================================================================
# 2. Cosine similarity between word pairs
# =============================================================================
print("=" * 70)
print("SECTION 2: Cosine Similarity Between Word Pairs")
print("=" * 70)

sim_pairs = [
    ("king", "queen"),      # royalty + gender difference
    ("man", "woman"),       # gender difference only
    ("king", "man"),        # royalty difference
    ("dog", "cat"),         # same category (animals)
    ("car", "truck"),       # same category (vehicles)
    ("apple", "banana"),    # same category (fruits)
    ("paris", "london"),    # same category (cities)
    ("king", "car"),        # very different
    ("man", "apple"),       # very different
    ("dog", "paris"),       # very different
]

print(f"\n{'Word A':<12} {'Word B':<12} {'Cosine Sim':>12}")
print("-" * 38)
sim_results = []
for w1, w2 in sim_pairs:
    sim = cosine_similarity(embeddings[w1], embeddings[w2])
    sim_results.append((w1, w2, sim))
    print(f"{w1:<12} {w2:<12} {sim:>12.4f}")

# Save similarity table
with open(OUT / "pretrained-analogy-cosine-similarity.txt", "w") as f:
    f.write("Word A\tWord B\tCosine Similarity\n")
    for w1, w2, sim in sim_results:
        f.write(f"{w1}\t{w2}\t{sim:.6f}\n")

# =============================================================================
# 3. Word analogy via vector arithmetic
# =============================================================================
print(f"\n{'=' * 70}")
print("SECTION 3: Word Analogy via Vector Arithmetic")
print("=" * 70)

analogies = [
    ("man", "woman", "king"),       # expect: queen
    ("man", "woman", "boy"),        # expect: girl
    ("man", "woman", "father"),     # expect: mother
    ("man", "woman", "uncle"),      # expect: aunt
    ("man", "woman", "prince"),     # expect: princess
    ("king", "queen", "man"),       # expect: woman (reverse)
    ("paris", "london", "tokyo"),   # expect: another city
]

print(f"\n{'Analogy':<30} {'Top-1':<12} {'Sim':>8}  {'Top-2':<12} {'Sim':>8}  {'Top-3':<12} {'Sim':>8}")
print("-" * 100)

analogy_results = []
for a, b, c in analogies:
    results, target_vec = analogy(a, b, c, emb_matrix, vocab, k=3)
    analogy_str = f"{a}:{b} :: {c}:?"
    analogy_results.append({
        "analogy": analogy_str,
        "a": a, "b": b, "c": c,
        "top_results": results,
    })
    top3_str = "  ".join([f"{w:<12} {s:>8.4f}" for w, s in results])
    print(f"{analogy_str:<30} {top3_str}")

# Save analogy results
with open(OUT / "pretrained-analogy-results.txt", "w") as f:
    for ar in analogy_results:
        f.write(f"Analogy: {ar['analogy']}\n")
        for rank, (w, s) in enumerate(ar['top_results'], 1):
            f.write(f"  #{rank}: {w} (cosine sim = {s:.6f})\n")
        f.write("\n")

# =============================================================================
# 4. Nearest-neighbor queries
# =============================================================================
print(f"\n{'=' * 70}")
print("SECTION 4: Nearest-Neighbor Queries")
print("=" * 70)

nn_words = ["king", "queen", "dog", "car", "paris", "apple"]
nn_results = {}
for w in nn_words:
    neighbors = nearest_neighbors(w, emb_matrix, vocab, k=5)
    nn_results[w] = neighbors
    print(f"\n  Nearest neighbors of '{w}':")
    for rank, (nw, sim) in enumerate(neighbors, 1):
        print(f"    #{rank}: {nw:<12} cosine sim = {sim:.4f}")

# Save nearest neighbor results
with open(OUT / "pretrained-analogy-nearest-neighbors.txt", "w") as f:
    for w in nn_words:
        f.write(f"Nearest neighbors of '{w}':\n")
        for rank, (nw, sim) in enumerate(nn_results[w], 1):
            f.write(f"  #{rank}: {nw} (cosine sim = {sim:.6f})\n")
        f.write("\n")

# =============================================================================
# 5. Cosine similarity heatmap
# =============================================================================
print(f"\n{'=' * 70}")
print("SECTION 5: Cosine Similarity Heatmap")
print("=" * 70)

# Select a subset for the heatmap
heatmap_words = ["king", "queen", "man", "woman", "boy", "girl",
                 "dog", "cat", "car", "truck", "paris", "london"]
heatmap_indices = [vocab.index(w) for w in heatmap_words]
heatmap_matrix = emb_matrix[heatmap_indices]
sim_matrix = cosine_sim_matrix(heatmap_matrix)

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(sim_matrix, cmap='RdYlBu_r', vmin=-0.2, vmax=1.0)
ax.set_xticks(range(len(heatmap_words)))
ax.set_yticks(range(len(heatmap_words)))
ax.set_xticklabels(heatmap_words, rotation=45, ha='right', fontsize=10)
ax.set_yticklabels(heatmap_words, fontsize=10)
ax.set_title("Cosine Similarity Heatmap — Toy Pretrained Word Vectors\n(WP05: Pretrained Vectors / Analogy / Visualization)",
             fontsize=12, fontweight='bold')

# Add text annotations
for i in range(len(heatmap_words)):
    for j in range(len(heatmap_words)):
        val = sim_matrix[i, j]
        color = "white" if val > 0.6 or val < 0.1 else "black"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                color=color, fontsize=7)

plt.colorbar(im, ax=ax, label="Cosine Similarity")
plt.tight_layout()
heatmap_path = OUT / "pretrained-analogy-cosine-heatmap.png"
plt.savefig(heatmap_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {heatmap_path}")
print(f"  Observation: same-category words (king/queen, man/woman, dog/cat)")
print(f"  show high similarity; cross-category pairs show lower similarity.")

# =============================================================================
# 6. Failure / bias case
# =============================================================================
print(f"\n{'=' * 70}")
print("SECTION 6: Failure / Bias Case")
print("=" * 70)

# In our toy embedding, the gender direction is perfectly linear,
# so analogies always work. But let's show what happens when we
# probe with words that DON'T have a clear analogy relationship.
# This demonstrates that analogy is a PROBE of vector structure,
# not a guarantee.

print("\n  Probing weak analogies (no clear relational structure):")
weak_analogies = [
    ("apple", "banana", "dog"),     # fruit:fruit :: dog:? → no clear answer
    ("car", "bicycle", "king"),     # vehicle:vehicle :: king:? → no clear answer
    ("fish", "cat", "paris"),       # animal:animal :: paris:? → no clear answer
]

weak_results = []
for a, b, c in weak_analogies:
    results, _ = analogy(a, b, c, emb_matrix, vocab, k=5)
    analogy_str = f"{a}:{b} :: {c}:?"
    weak_results.append({"analogy": analogy_str, "results": results})
    print(f"\n  {analogy_str}")
    for rank, (w, s) in enumerate(results, 1):
        print(f"    #{rank}: {w:<12} cosine sim = {s:.4f}")

print("\n  Key insight: when the analogy has no clear relational structure,")
print("  the top results are arbitrary — they just happen to be nearest to")
print("  the computed vector, not semantically meaningful answers.")
print("  This is why analogy results should be treated as PROBE outputs,")
print("  not as proof that the model 'understands' language.")

# Save failure case results
with open(OUT / "pretrained-analogy-failure-cases.txt", "w") as f:
    for wr in weak_results:
        f.write(f"Weak analogy: {wr['analogy']}\n")
        for rank, (w, s) in enumerate(wr['results'], 1):
            f.write(f"  #{rank}: {w} (cosine sim = {s:.6f})\n")
        f.write("\n")

# =============================================================================
# 7. 2D PCA visualization
# =============================================================================
print(f"\n{'=' * 70}")
print("SECTION 7: 2D PCA Visualization")
print("=" * 70)

# Center the data
mean = emb_matrix.mean(axis=0)
centered = emb_matrix - mean

# Covariance matrix and eigendecomposition
cov = np.cov(centered.T)
eigenvalues, eigenvectors = np.linalg.eigh(cov)

# Sort by decreasing eigenvalue
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

# Project onto top 2 principal components
projected = centered @ eigenvectors[:, :2]

print(f"\n  PCA explained variance ratio:")
total_var = eigenvalues.sum()
for i in range(min(5, len(eigenvalues))):
    ratio = eigenvalues[i] / total_var
    print(f"    PC{i+1}: {ratio:.4f} ({ratio*100:.1f}%)")

print(f"\n  2D coordinates (PC1, PC2):")
pca_coords = {}
for i, w in enumerate(vocab):
    pca_coords[w] = (projected[i, 0], projected[i, 1])
    print(f"    {w:<12} PC1={projected[i,0]:>8.3f}  PC2={projected[i,1]:>8.3f}")

# Plot
fig, ax = plt.subplots(figsize=(12, 9))

# Color by category
category_colors = {
    "animal": "#e74c3c",
    "vehicle": "#3498db",
    "city": "#2ecc71",
    "fruit": "#f39c12",
}

for i, w in enumerate(vocab):
    cat = word_to_category.get(w, "other")
    color = category_colors.get(cat, "#95a5a6")
    ax.scatter(projected[i, 0], projected[i, 1], c=color, s=80, zorder=5,
               edgecolors='black', linewidth=0.5)
    ax.annotate(w, (projected[i, 0], projected[i, 1]),
                fontsize=8, ha='left', va='bottom',
                xytext=(5, 5), textcoords='offset points')

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=c, edgecolor='black', label=cat)
                   for cat, c in category_colors.items()]
ax.legend(handles=legend_elements, loc='best', fontsize=9)

ax.set_xlabel(f"PC1 ({eigenvalues[0]/total_var*100:.1f}% variance)", fontsize=11)
ax.set_ylabel(f"PC2 ({eigenvalues[1]/total_var*100:.1f}% variance)", fontsize=11)
ax.set_title("2D PCA Projection of Toy Word Vectors\n(WP05: Pretrained Vectors / Analogy / Visualization)\n"
             "⚠️ PCA projection loses information — clusters may overlap in 2D",
             fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
pca_path = OUT / "pretrained-analogy-pca-2d.png"
plt.savefig(pca_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"\n  Saved: {pca_path}")
print(f"  Caveat: 2D PCA is a lossy projection. In the original d={DIM} space,")
print(f"  categories are better separated. PC1+PC2 capture only")
print(f"  {(eigenvalues[0]+eigenvalues[1])/total_var*100:.1f}% of total variance.")

# Save PCA coordinates
with open(OUT / "pretrained-analogy-pca-coordinates.txt", "w") as f:
    f.write("Word\tPC1\tPC2\tCategory\n")
    for i, w in enumerate(vocab):
        cat = word_to_category.get(w, "other")
        f.write(f"{w}\t{projected[i,0]:.6f}\t{projected[i,1]:.6f}\t{cat}\n")

# =============================================================================
# 8. Summary JSON for provenance
# =============================================================================
summary = {
    "capsule": "pretrained-analogy",
    "waypoint": "WP05",
    "concept": "Pretrained word vectors, cosine similarity, and analogies",
    "vocab_size": len(vocab),
    "embedding_dim": DIM,
    "sections_run": [
        "cosine_similarity",
        "word_analogy",
        "nearest_neighbors",
        "cosine_heatmap",
        "failure_bias_case",
        "pca_2d_visualization",
    ],
    "key_findings": {
        "analogy_king_man_woman": analogy_results[0]["top_results"][0][0],
        "analogy_king_man_woman_sim": round(analogy_results[0]["top_results"][0][1], 4),
        "man_woman_cosine_sim": round(sim_results[1][2], 4),
        "king_car_cosine_sim": round(sim_results[7][2], 4),
        "pca_pc1_variance_pct": round(eigenvalues[0]/total_var*100, 1),
        "pca_pc2_variance_pct": round(eigenvalues[1]/total_var*100, 1),
    },
    "output_files": [
        "pretrained-analogy-cosine-similarity.txt",
        "pretrained-analogy-results.txt",
        "pretrained-analogy-nearest-neighbors.txt",
        "pretrained-analogy-failure-cases.txt",
        "pretrained-analogy-cosine-heatmap.png",
        "pretrained-analogy-pca-2d.png",
        "pretrained-analogy-pca-coordinates.txt",
        "pretrained-analogy-summary.json",
    ],
}

with open(OUT / "pretrained-analogy-summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n{'=' * 70}")
print("SUMMARY")
print("=" * 70)
print(f"  Analogy 'man:woman :: king:?' → top result: "
      f"{analogy_results[0]['top_results'][0][0]} "
      f"(sim={analogy_results[0]['top_results'][0][1]:.4f})")
print(f"  man↔woman cosine sim: {sim_results[1][2]:.4f}")
print(f"  king↔car cosine sim:  {sim_results[7][2]:.4f}")
print(f"  PCA PC1 variance: {eigenvalues[0]/total_var*100:.1f}%")
print(f"  PCA PC2 variance: {eigenvalues[1]/total_var*100:.1f}%")
print(f"\nAll outputs saved to: {OUT}")
print("Done.")
