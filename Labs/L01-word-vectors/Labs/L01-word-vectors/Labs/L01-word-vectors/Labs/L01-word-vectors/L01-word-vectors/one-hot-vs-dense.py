#!/usr/bin/env python3
"""
Code Capsule: one-hot-vs-dense (WP02)
CS224N 2025 L01 — Word Vectors

Concept: One-hot orthogonality vs dense similarity
Official anchor: slides p19-p20 (one-hot and orthogonality problem);
                 slides p22-p23 (dense vectors and dot product similarity);
                 notes §2.2 Eq.1-Eq.2

Why this capsule: Students need to see numerically that one-hot vectors make
unrelated and semantically related words equally dissimilar (off-diagonal dot
products are 0), while dense toy embeddings can give similar words larger similarity.

This script uses only numpy (standard in Colab) for clarity.
"""

import numpy as np
import json
import sys

# ============================================================
# Part 1: One-hot encoding and its orthogonality problem
# ============================================================

# Small vocabulary with known semantic relationships
vocab = ["king", "queen", "cat", "dog", "bank", "river", "car", "banana"]
vocab_size = len(vocab)

# Build one-hot vectors: each word is a vector of size vocab_size
# with exactly one 1 at its index position
one_hot = {}
for i, word in enumerate(vocab):
    vec = np.zeros(vocab_size)
    vec[i] = 1.0
    one_hot[word] = vec

print("=" * 70)
print("PART 1: One-hot Vectors")
print("=" * 70)
print(f"\nVocabulary ({vocab_size} words): {vocab}")
print(f"One-hot vector dimension = vocabulary size = {vocab_size}")
print(f"\nExample: one_hot['king'] = {one_hot['king']}")
print(f"Example: one_hot['queen'] = {one_hot['queen']}")

# Compute all pairwise dot products for one-hot vectors
print("\n--- One-hot pairwise dot products ---")
print(f"{'Word A':<10} {'Word B':<10} {'Dot Product':>12} {'Same?':>6}")
print("-" * 42)

one_hot_results = []
pairs_to_show = [
    ("king", "queen"),    # semantically similar (royalty)
    ("cat", "dog"),       # semantically similar (pets)
    ("bank", "river"),    # different domains
    ("car", "banana"),    # unrelated
    ("king", "king"),     # self
]

for w1, w2 in pairs_to_show:
    dot = float(np.dot(one_hot[w1], one_hot[w2]))
    same = "yes" if w1 == w2 else "no"
    print(f"{w1:<10} {w2:<10} {dot:>12.1f} {same:>6}")
    one_hot_results.append({"word_a": w1, "word_b": w2, "dot_product": dot, "same": same})

print("\n>>> KEY OBSERVATION: ALL off-diagonal dot products are 0.0")
print(">>> One-hot vectors cannot distinguish 'king-queen' (similar) from 'car-banana' (unrelated)")
print(">>> This is the orthogonality problem (slides p20): 'There is no natural notion of similarity'")

# Full one-hot similarity matrix
one_hot_matrix = np.zeros((vocab_size, vocab_size))
for i, w1 in enumerate(vocab):
    for j, w2 in enumerate(vocab):
        one_hot_matrix[i, j] = np.dot(one_hot[w1], one_hot[w2])

print("\n--- Full one-hot dot product matrix ---")
header = "          " + "".join(f"{w:>8}" for w in vocab)
print(header)
for i, w in enumerate(vocab):
    row = f"{w:<10}" + "".join(f"{one_hot_matrix[i,j]:>8.0f}" for j in range(vocab_size))
    print(row)

# ============================================================
# Part 2: Dense vectors can encode similarity
# ============================================================

print("\n")
print("=" * 70)
print("PART 2: Dense Vectors (toy embeddings, 6-dimensional)")
print("=" * 70)

# Hand-crafted 6D dense vectors that encode semantic relationships
# Design principle: similar words get similar vectors; unrelated words point in
# very different directions. Using both positive and negative values so that
# cross-category pairs can have low or negative cosine similarity.
# Dimensions: [royalty, animate, finance, nature, mechanical, food]
dense_vectors = {
    "king":   np.array([ 0.9,  0.6,  0.1,  0.0, -0.1, -0.2]),  # royalty + animate
    "queen":  np.array([ 0.85, 0.55, 0.1,  0.0, -0.1, -0.15]), # royalty + animate (close to king)
    "cat":    np.array([-0.1, 0.8,  0.0,  0.3, -0.2,  0.1]),   # animate + nature
    "dog":    np.array([-0.05,0.75, 0.0,  0.25,-0.15, 0.1]),   # animate + nature (close to cat)
    "bank":   np.array([ 0.1, -0.3,  0.9, -0.2,  0.2, -0.1]),  # finance
    "river":  np.array([-0.1, 0.1, -0.2,  0.85, 0.0,  0.0]),   # nature
    "car":    np.array([-0.2, -0.2, 0.1, -0.3,  0.9,  0.0]),   # mechanical
    "banana": np.array([ 0.0,  0.2, -0.1,  0.3, -0.1,  0.85]), # food + nature
}

print(f"\nDense vector dimension: 6 (vs one-hot dimension: {vocab_size})")
print("\nExample dense vectors:")
for word in vocab:
    print(f"  {word:<10} = {dense_vectors[word]}")

# Compute cosine similarity for dense vectors
def cosine_similarity(v1, v2):
    """Cosine similarity = dot(v1,v2) / (||v1|| * ||v2||)"""
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

print("\n--- Dense vector pairwise similarities ---")
print(f"{'Word A':<10} {'Word B':<10} {'Dot Prod':>10} {'Cosine Sim':>12} {'Relationship':<25}")
print("-" * 72)

dense_results = []
relationships = {
    ("king", "queen"): "similar (royalty)",
    ("cat", "dog"): "similar (pets)",
    ("bank", "river"): "different domains",
    ("car", "banana"): "unrelated",
    ("king", "king"): "self",
}

for w1, w2 in pairs_to_show:
    dot = float(np.dot(dense_vectors[w1], dense_vectors[w2]))
    cos = cosine_similarity(dense_vectors[w1], dense_vectors[w2])
    rel = relationships.get((w1, w2), "")
    print(f"{w1:<10} {w2:<10} {dot:>10.4f} {cos:>12.4f} {rel:<25}")
    dense_results.append({
        "word_a": w1, "word_b": w2,
        "dot_product": round(dot, 4),
        "cosine_similarity": round(cos, 4),
        "relationship": rel
    })

print("\n>>> KEY OBSERVATION: Dense vectors give HIGH similarity to semantically similar pairs")
print(">>> king-queen cosine = {:.4f}, cat-dog cosine = {:.4f}".format(
    cosine_similarity(dense_vectors["king"], dense_vectors["queen"]),
    cosine_similarity(dense_vectors["cat"], dense_vectors["dog"])
))
print(">>> vs car-banana cosine = {:.4f} (lower, as expected for unrelated concepts)".format(
    cosine_similarity(dense_vectors["car"], dense_vectors["banana"])
))

# Full dense cosine similarity matrix
dense_matrix = np.zeros((vocab_size, vocab_size))
for i, w1 in enumerate(vocab):
    for j, w2 in enumerate(vocab):
        dense_matrix[i, j] = cosine_similarity(dense_vectors[w1], dense_vectors[w2])

print("\n--- Full dense cosine similarity matrix ---")
header = "          " + "".join(f"{w:>8}" for w in vocab)
print(header)
for i, w in enumerate(vocab):
    row = f"{w:<10}" + "".join(f"{dense_matrix[i,j]:>8.4f}" for j in range(vocab_size))
    print(row)

# ============================================================
# Part 3: Side-by-side comparison
# ============================================================

print("\n")
print("=" * 70)
print("PART 3: Side-by-side comparison")
print("=" * 70)
print(f"\n{'Pair':<20} {'One-hot Dot':>12} {'Dense Cosine':>14} {'Dense Dot':>12}")
print("-" * 60)

comparison_results = []
for w1, w2 in pairs_to_show:
    oh_dot = float(np.dot(one_hot[w1], one_hot[w2]))
    d_cos = cosine_similarity(dense_vectors[w1], dense_vectors[w2])
    d_dot = float(np.dot(dense_vectors[w1], dense_vectors[w2]))
    pair_label = f"{w1}-{w2}"
    print(f"{pair_label:<20} {oh_dot:>12.1f} {d_cos:>14.4f} {d_dot:>12.4f}")
    comparison_results.append({
        "pair": pair_label,
        "one_hot_dot": oh_dot,
        "dense_cosine": round(d_cos, 4),
        "dense_dot": round(d_dot, 4)
    })

print("\n>>> SUMMARY:")
print(">>> One-hot: ALL non-self pairs = 0.0 (cannot encode ANY similarity)")
print(">>> Dense:   similar words > unrelated words (learns to encode meaning)")
print(">>> This is why CS224N moves from one-hot to dense representations (slides p22)")

# ============================================================
# Save structured output for provenance
# ============================================================

output_data = {
    "capsule": "one-hot-vs-dense",
    "waypoint": "WP02",
    "vocab": vocab,
    "vocab_size": vocab_size,
    "dense_dim": 6,
    "one_hot_results": one_hot_results,
    "dense_results": dense_results,
    "comparison_results": comparison_results,
    "one_hot_matrix": one_hot_matrix.tolist(),
    "dense_cosine_matrix": dense_matrix.tolist(),
}

with open("Labs/L01-word-vectors/outputs/one-hot-vs-dense-data.json", "w") as f:
    json.dump(output_data, f, indent=2)

print("\n[Saved structured data to Labs/L01-word-vectors/outputs/one-hot-vs-dense-data.json]")

# ============================================================
# Generate comparison heatmap
# ============================================================

import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: One-hot dot product matrix
im1 = axes[0].imshow(one_hot_matrix, cmap='Blues', vmin=0, vmax=1)
axes[0].set_xticks(range(vocab_size))
axes[0].set_yticks(range(vocab_size))
axes[0].set_xticklabels(vocab, rotation=45, ha='right', fontsize=9)
axes[0].set_yticklabels(vocab, fontsize=9)
axes[0].set_title("One-hot Dot Product Matrix\n(all off-diagonal = 0)", fontsize=12, fontweight='bold')
for i in range(vocab_size):
    for j in range(vocab_size):
        axes[0].text(j, i, f"{one_hot_matrix[i,j]:.0f}",
                    ha="center", va="center", fontsize=9,
                    color="white" if one_hot_matrix[i,j] > 0.5 else "black")
plt.colorbar(im1, ax=axes[0], shrink=0.8)

# Right: Dense cosine similarity matrix
im2 = axes[1].imshow(dense_matrix, cmap='YlOrRd', vmin=-0.5, vmax=1)
axes[1].set_xticks(range(vocab_size))
axes[1].set_yticks(range(vocab_size))
axes[1].set_xticklabels(vocab, rotation=45, ha='right', fontsize=9)
axes[1].set_yticklabels(vocab, fontsize=9)
axes[1].set_title("Dense Cosine Similarity Matrix\n(similar words = higher values)", fontsize=12, fontweight='bold')
for i in range(vocab_size):
    for j in range(vocab_size):
        axes[1].text(j, i, f"{dense_matrix[i,j]:.3f}",
                    ha="center", va="center", fontsize=8,
                    color="white" if dense_matrix[i,j] > 0.7 else "black")
plt.colorbar(im2, ax=axes[1], shrink=0.8)

plt.suptitle("Code Capsule: One-hot vs Dense Vectors (WP02)\nCS224N 2025 L01",
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig("Labs/L01-word-vectors/outputs/one-hot-vs-dense-similarity-heatmap.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("[Saved heatmap to Labs/L01-word-vectors/outputs/one-hot-vs-dense-similarity-heatmap.png]")

# ============================================================
# Generate bar chart comparison
# ============================================================

fig2, ax2 = plt.subplots(figsize=(10, 5))

pair_labels = [f"{r['pair']}" for r in comparison_results]
one_hot_vals = [r['one_hot_dot'] for r in comparison_results]
dense_cos_vals = [r['dense_cosine'] for r in comparison_results]

x = np.arange(len(pair_labels))
width = 0.35

bars1 = ax2.bar(x - width/2, one_hot_vals, width, label='One-hot Dot Product', color='#4472C4', alpha=0.8)
bars2 = ax2.bar(x + width/2, dense_cos_vals, width, label='Dense Cosine Similarity', color='#ED7D31', alpha=0.8)

ax2.set_xlabel('Word Pair', fontsize=11)
ax2.set_ylabel('Similarity Score', fontsize=11)
ax2.set_title('Code Capsule: One-hot vs Dense Similarity (WP02)\nCS224N 2025 L01', fontsize=13, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(pair_labels, fontsize=10)
ax2.legend(fontsize=10)
ax2.set_ylim(-0.5, 1.2)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
             f'{height:.1f}', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
             f'{height:.3f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig("Labs/L01-word-vectors/outputs/one-hot-vs-dense-bar-comparison.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("[Saved bar chart to Labs/L01-word-vectors/outputs/one-hot-vs-dense-bar-comparison.png]")

print("\n[DONE] All outputs saved successfully.")
sys.exit(0)
