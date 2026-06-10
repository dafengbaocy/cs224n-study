#!/usr/bin/env python3
"""
CS224N L01 Code Capsule: one-hot-vs-dense
==========================================
Demonstrates why one-hot vectors cannot encode word similarity,
and how dense word vectors solve this problem.

Official anchor: Slides p19-22; Notes §2.2 (one-hot vectors, Eq.1-2)

Key insight from slides p20:
  "There is no natural notion of similarity for one-hot vectors!"
  → motel and hotel are orthogonal under one-hot (dot product = 0)

This script:
1. Builds one-hot vectors for a tiny vocabulary
2. Computes pairwise dot products → all zero
3. Shows dense embeddings where similar words have high similarity
4. Visualizes the contrast
"""

import numpy as np
import json
import sys

# ============================================================
# Part 1: One-hot encoding
# ============================================================
# Tiny vocabulary from CS224N slides examples
vocab = ["hotel", "motel", "book", "Seattle", "Seattle_motel"]
# Note: "Seattle_motel" represents the query "Seattle motel" concept
vocab_size = len(vocab)

print("=" * 60)
print("Part 1: One-hot Vectors")
print("=" * 60)
print(f"\nVocabulary ({vocab_size} words): {vocab}")
print(f"Each one-hot vector has dimension = vocab_size = {vocab_size}")
print()

# Build one-hot matrix: each row is a one-hot vector
one_hot = np.eye(vocab_size)

for i, word in enumerate(vocab):
    print(f"  {word:15s} → {one_hot[i].tolist()}")

print(f"\nOne-hot matrix shape: {one_hot.shape}")
print(f"Non-zero entries per vector: {int(one_hot.sum(axis=1)[0])}")
print(f"Sparsity: {(1 - one_hot.sum() / one_hot.size) * 100:.1f}% zeros")

# ============================================================
# Part 2: Dot products between one-hot vectors
# ============================================================
print("\n" + "=" * 60)
print("Part 2: Pairwise Dot Products (One-hot)")
print("=" * 60)
print("\nKey question: How similar is 'hotel' to 'motel'?")
print("Under one-hot: dot(e_hotel, e_motel) = ?")

dot_matrix_onehot = one_hot @ one_hot.T

print(f"\nDot product matrix (one-hot):")
print(f"{'':15s}", end="")
for w in vocab:
    print(f"{w:>15s}", end="")
print()
for i, wi in enumerate(vocab):
    print(f"{wi:15s}", end="")
    for j, wj in enumerate(vocab):
        val = dot_matrix_onehot[i, j]
        print(f"{val:15.1f}", end="")
    print()

# Critical observation
hotel_idx = vocab.index("hotel")
motel_idx = vocab.index("motel")
dot_hotel_motel = dot_matrix_onehot[hotel_idx, motel_idx]
print(f"\n⚠️  dot(hotel, motel) = {dot_hotel_motel:.1f}")
print(f"⚠️  ALL off-diagonal dot products = 0.0")
print(f"    → One-hot vectors are ALL mutually orthogonal!")
print(f"    → The model cannot tell 'hotel' and 'motel' apart at all.")

# Cosine similarity (for one-hot, cos = dot / (|a|*|b|) = 0/1 = 0)
norms = np.linalg.norm(one_hot, axis=1)
cos_matrix_onehot = dot_matrix_onehot / np.outer(norms, norms)
print(f"\nCosine similarity matrix (one-hot):")
print(f"{'':15s}", end="")
for w in vocab:
    print(f"{w:>15s}", end="")
print()
for i, wi in enumerate(vocab):
    print(f"{wi:15s}", end="")
    for j, wj in enumerate(vocab):
        val = cos_matrix_onehot[i, j]
        print(f"{val:15.1f}", end="")
    print()

print(f"\n⚠️  cos(hotel, motel) = {cos_matrix_onehot[hotel_idx, motel_idx]:.1f}")
print(f"    → No natural notion of similarity (Slides p20)")

# ============================================================
# Part 3: Dense embeddings (illustrative)
# ============================================================
print("\n" + "=" * 60)
print("Part 3: Dense Word Vectors (illustrative, dim=3)")
print("=" * 60)
print("\nIn reality, dense vectors are learned from data (Word2Vec, etc.)")
print("Here we use hand-crafted 3D vectors to show the IDEA:")
print("  - Similar words → similar vectors → high dot product / cosine")

# Hand-crafted dense vectors that encode semantic relationships
# Dimension is just 3 for visualization; real models use 50-300+
dense_vectors = np.array([
    [0.9,  0.1,  0.2],   # hotel:    high accommodation dimension
    [0.8,  0.2,  0.1],   # motel:    similar to hotel (accommodation)
    [0.1,  0.9,  0.3],   # book:     very different (object/action)
    [0.2,  0.3,  0.9],   # Seattle:  location dimension
    [0.5,  0.2,  0.6],   # Seattle_motel: mix of location + accommodation
])

embed_dim = dense_vectors.shape[1]
print(f"\nDense embedding dimension: {embed_dim}")
print(f"(Real models: 50-300+ dimensions)")
print()

for i, word in enumerate(vocab):
    vec_str = ", ".join(f"{v:.1f}" for v in dense_vectors[i])
    print(f"  {word:15s} → [{vec_str}]")

# Dot products for dense vectors
dot_matrix_dense = dense_vectors @ dense_vectors.T
norms_dense = np.linalg.norm(dense_vectors, axis=1)
cos_matrix_dense = dot_matrix_dense / np.outer(norms_dense, norms_dense)

print(f"\nDot product matrix (dense):")
print(f"{'':15s}", end="")
for w in vocab:
    print(f"{w:>15s}", end="")
print()
for i, wi in enumerate(vocab):
    print(f"{wi:15s}", end="")
    for j, wj in enumerate(vocab):
        val = dot_matrix_dense[i, j]
        print(f"{val:15.3f}", end="")
    print()

print(f"\nCosine similarity matrix (dense):")
print(f"{'':15s}", end="")
for w in vocab:
    print(f"{w:>15s}", end="")
print()
for i, wi in enumerate(vocab):
    print(f"{wi:15s}", end="")
    for j, wj in enumerate(vocab):
        val = cos_matrix_dense[i, j]
        print(f"{val:15.3f}", end="")
    print()

cos_hotel_motel_dense = cos_matrix_dense[hotel_idx, motel_idx]
cos_hotel_book_dense = cos_matrix_dense[hotel_idx, vocab.index("book")]
print(f"\n✅ cos(hotel, motel) = {cos_hotel_motel_dense:.3f}  (HIGH — similar words)")
print(f"✅ cos(hotel, book)  = {cos_hotel_book_dense:.3f}  (LOW  — different words)")
print(f"\n   Dense vectors CAN distinguish similar from dissimilar words!")

# ============================================================
# Part 4: Summary comparison
# ============================================================
print("\n" + "=" * 60)
print("Part 4: Summary Comparison")
print("=" * 60)
print(f"\n{'Pair':30s} {'One-hot cos':>12s} {'Dense cos':>12s}")
print("-" * 56)
pairs = [
    ("hotel ↔ motel", hotel_idx, motel_idx),
    ("hotel ↔ book", hotel_idx, vocab.index("book")),
    ("hotel ↔ Seattle", hotel_idx, vocab.index("Seattle")),
    ("motel ↔ book", motel_idx, vocab.index("book")),
]
for label, i, j in pairs:
    oh_val = cos_matrix_onehot[i, j]
    dn_val = cos_matrix_dense[i, j]
    print(f"{label:30s} {oh_val:12.1f} {dn_val:12.3f}")

print(f"\n{'Vocabulary size':30s} {vocab_size:12d} {vocab_size:12d}")
print(f"{'Vector dimension':30s} {vocab_size:12d} {embed_dim:12d}")
print(f"{'Sparsity':30s} {'100.0%':>12s} {'0.0%':>12s}")
print(f"{'Storage per word (floats)':30s} {vocab_size:12d} {embed_dim:12d}")

print("\n" + "=" * 60)
print("Takeaway (Slides p21-22):")
print("  'We will build a dense vector for each word'")
print("  → Low-dimensional, learned from data, encodes similarity")
print("  → This is the foundation of Word2Vec (next capsule)")
print("=" * 60)

# ============================================================
# Part 5: Save structured output for provenance
# ============================================================
output_data = {
    "capsule": "one-hot-vs-dense",
    "vocab": vocab,
    "vocab_size": vocab_size,
    "embed_dim": embed_dim,
    "one_hot_cosine": {
        "hotel_motel": float(cos_matrix_onehot[hotel_idx, motel_idx]),
        "hotel_book": float(cos_matrix_onehot[hotel_idx, vocab.index("book")]),
        "hotel_Seattle": float(cos_matrix_onehot[hotel_idx, vocab.index("Seattle")]),
        "motel_book": float(cos_matrix_onehot[motel_idx, vocab.index("book")]),
    },
    "dense_cosine": {
        "hotel_motel": float(cos_matrix_dense[hotel_idx, motel_idx]),
        "hotel_book": float(cos_matrix_dense[hotel_idx, vocab.index("book")]),
        "hotel_Seattle": float(cos_matrix_dense[hotel_idx, vocab.index("Seattle")]),
        "motel_book": float(cos_matrix_dense[motel_idx, vocab.index("book")]),
    },
    "key_finding": "All one-hot pairwise cosine similarities are 0.0; dense vectors encode meaningful similarity.",
}

with open("Labs/L01-word-vectors/outputs/one-hot-vs-dense-results.json", "w") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)
print(f"\nResults saved to Labs/L01-word-vectors/outputs/one-hot-vs-dense-results.json")

# ============================================================
# Part 6: Visualization
# ============================================================
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left panel: One-hot similarity heatmap
im1 = axes[0].imshow(cos_matrix_onehot, cmap='RdYlBu_r', vmin=-0.2, vmax=1.0)
axes[0].set_title("One-hot Cosine Similarity\n(All off-diagonal = 0)", fontsize=13, fontweight='bold')
axes[0].set_xticks(range(vocab_size))
axes[0].set_yticks(range(vocab_size))
axes[0].set_xticklabels(vocab, rotation=45, ha='right', fontsize=9)
axes[0].set_yticklabels(vocab, fontsize=9)
for i in range(vocab_size):
    for j in range(vocab_size):
        axes[0].text(j, i, f"{cos_matrix_onehot[i,j]:.1f}",
                    ha="center", va="center", fontsize=10,
                    color="white" if cos_matrix_onehot[i,j] > 0.5 else "black")
plt.colorbar(im1, ax=axes[0], shrink=0.8)

# Right panel: Dense similarity heatmap
im2 = axes[1].imshow(cos_matrix_dense, cmap='RdYlBu_r', vmin=-0.2, vmax=1.0)
axes[1].set_title("Dense Vector Cosine Similarity\n(Similar words = high similarity)", fontsize=13, fontweight='bold')
axes[1].set_xticks(range(vocab_size))
axes[1].set_yticks(range(vocab_size))
axes[1].set_xticklabels(vocab, rotation=45, ha='right', fontsize=9)
axes[1].set_yticklabels(vocab, fontsize=9)
for i in range(vocab_size):
    for j in range(vocab_size):
        axes[1].text(j, i, f"{cos_matrix_dense[i,j]:.3f}",
                    ha="center", va="center", fontsize=9,
                    color="white" if cos_matrix_dense[i,j] > 0.6 else "black")
plt.colorbar(im2, ax=axes[1], shrink=0.8)

plt.suptitle("CS224N L01: One-hot vs Dense Word Vectors\n"
             "Slides p19-22 | Why one-hot fails to encode similarity",
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig("Labs/L01-word-vectors/outputs/one-hot-vs-dense-similarity-heatmap.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("Plot saved to Labs/L01-word-vectors/outputs/one-hot-vs-dense-similarity-heatmap.png")

# Second plot: 2D projection of dense vectors
fig2, ax2 = plt.subplots(figsize=(8, 7))
# Use first 2 dimensions for 2D scatter
colors = ['#e74c3c', '#e67e22', '#2ecc71', '#3498db', '#9b59b6']
markers = ['o', 's', '^', 'D', 'v']

for i, word in enumerate(vocab):
    ax2.scatter(dense_vectors[i, 0], dense_vectors[i, 1],
               c=colors[i], marker=markers[i], s=200, zorder=5,
               edgecolors='black', linewidth=1.5)
    ax2.annotate(word, (dense_vectors[i, 0], dense_vectors[i, 1]),
                textcoords="offset points", xytext=(10, 8),
                fontsize=11, fontweight='bold')

# Draw similarity lines
# hotel-motel (should be close)
ax2.plot([dense_vectors[0,0], dense_vectors[1,0]],
         [dense_vectors[0,1], dense_vectors[1,1]],
         'g--', linewidth=2, alpha=0.7, label=f'hotel↔motel (cos={cos_hotel_motel_dense:.3f})')
# hotel-book (should be far)
ax2.plot([dense_vectors[0,0], dense_vectors[2,0]],
         [dense_vectors[0,1], dense_vectors[2,1]],
         'r--', linewidth=2, alpha=0.7, label=f'hotel↔book (cos={cos_hotel_book_dense:.3f})')

ax2.set_xlabel("Dimension 1", fontsize=12)
ax2.set_ylabel("Dimension 2", fontsize=12)
ax2.set_title("CS224N L01: Dense Word Vectors in 2D\n"
              "Similar words cluster together (hotel ≈ motel)",
              fontsize=13, fontweight='bold')
ax2.legend(fontsize=10, loc='upper right')
ax2.grid(True, alpha=0.3)
ax2.set_aspect('equal')

# Add margin
margin = 0.2
x_min, x_max = dense_vectors[:,0].min() - margin, dense_vectors[:,0].max() + margin
y_min, y_max = dense_vectors[:,1].min() - margin, dense_vectors[:,1].max() + margin
ax2.set_xlim(x_min, x_max)
ax2.set_ylim(y_min, y_max)

plt.tight_layout()
plt.savefig("Labs/L01-word-vectors/outputs/one-hot-vs-dense-2d-projection.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("Plot saved to Labs/L01-word-vectors/outputs/one-hot-vs-dense-2d-projection.png")

print("\n✅ All outputs generated successfully.")
