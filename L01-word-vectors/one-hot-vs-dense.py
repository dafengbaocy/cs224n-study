#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: one-hot-vs-dense
Demonstrates why one-hot vectors cannot encode word similarity,
while dense vectors can.

Official anchor: Slides p19-22; Notes §2.2 Eq.1-2
"""

import json
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================
# 1. Define a tiny vocabulary
# ============================================================
# 6 words: 2 near-synonyms (hotel/motel), 2 animals (cat/dog), 2 unrelated (book/fish)
vocab = ["hotel", "motel", "book", "cat", "dog", "fish"]
word_to_idx = {w: i for i, w in enumerate(vocab)}
V = len(vocab)  # vocabulary size = 6

print("=" * 60)
print("CS224N L01 — One-hot vs Dense Word Vectors")
print("=" * 60)
print(f"\nVocabulary ({V} words): {vocab}")

# ============================================================
# 2. Build one-hot vectors
# ============================================================
# one-hot: each word is a basis vector e_i in R^V
one_hot = np.eye(V)

print("\n--- One-hot Encoding ---")
for w in vocab:
    vec = one_hot[word_to_idx[w]]
    print(f"  {w:>6s} = {vec.astype(int).tolist()}")

# ============================================================
# 3. Compute one-hot dot products for selected pairs
# ============================================================
# Key insight: for one-hot vectors, dot product = 1 if same word, 0 otherwise
# This means ALL different words are equally dissimilar!

pairs = [
    ("hotel", "motel", "synonyms — should be similar"),
    ("cat", "dog", "both animals — should be somewhat similar"),
    ("book", "fish", "unrelated — should be dissimilar"),
]

print("\n--- One-hot Dot Products ---")
print("  (For one-hot vectors, dot product = 0 for ALL different words)")
print()

onehot_results = []
for w1, w2, label in pairs:
    v1 = one_hot[word_to_idx[w1]]
    v2 = one_hot[word_to_idx[w2]]
    dot = float(np.dot(v1, v2))
    onehot_results.append({"pair": f"{w1}-{w2}", "label": label, "dot_product": dot})
    print(f"  {w1:>6s} · {w2:<6s} = {dot:.1f}   ({label})")

print()
print("  ⚠️  ALL dot products are 0.0 — one-hot vectors are orthogonal.")
print("  The model cannot distinguish synonyms from unrelated words!")

# ============================================================
# 4. Build toy dense vectors (2D, simulating trained embeddings)
# ============================================================
# These are hand-crafted to show what TRAINED vectors should look like:
# - hotel and motel are close (near-synonyms)
# - cat and dog are close (both animals)
# - book and fish are far apart (unrelated)
#
# NOTE: In practice, these vectors are learned by models like Word2Vec/GloVe.
# Here we use toy values just to demonstrate the concept.

dense_vectors = {
    "hotel": np.array([0.9,  0.1]),
    "motel": np.array([0.85, 0.15]),
    "cat":   np.array([-0.3, 0.9]),
    "dog":   np.array([-0.25, 0.95]),
    "book":  np.array([0.1, -0.9]),
    "fish":  np.array([-0.9, 0.1]),
}

print("\n--- Dense Vectors (2D toy embeddings) ---")
print("  (In practice, these are learned by Word2Vec/GloVe, not hand-crafted)")
print()
for w in vocab:
    vec = dense_vectors[w]
    print(f"  {w:>6s} = [{vec[0]:+.2f}, {vec[1]:+.2f}]")

# ============================================================
# 5. Compute cosine similarities for dense vectors
# ============================================================
def cosine_similarity(v1, v2):
    """Compute cosine similarity between two vectors."""
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))

print("\n--- Dense Cosine Similarities ---")
print("  (cos_sim = 1: identical direction; 0: orthogonal; -1: opposite)")
print()

dense_results = []
for w1, w2, label in pairs:
    v1 = dense_vectors[w1]
    v2 = dense_vectors[w2]
    cos_sim = cosine_similarity(v1, v2)
    dense_results.append({"pair": f"{w1}-{w2}", "label": label, "cosine_similarity": round(cos_sim, 4)})
    print(f"  cos({w1}, {w2}) = {cos_sim:.4f}   ({label})")

# ============================================================
# 6. Summary comparison table
# ============================================================
print("\n" + "=" * 60)
print("COMPARISON SUMMARY")
print("=" * 60)
print()
print(f"  {'Pair':<16s} {'Relation':<36s} {'One-hot dot':>12s} {'Dense cos':>12s}")
print(f"  {'-'*16} {'-'*36} {'-'*12} {'-'*12}")
for i, (w1, w2, label) in enumerate(pairs):
    oh_dot = onehot_results[i]["dot_product"]
    d_cos = dense_results[i]["cosine_similarity"]
    print(f"  {w1}-{w2:<10s} {label:<36s} {oh_dot:>12.1f} {d_cos:>12.4f}")

print()
print("KEY CONCLUSION:")
print("  One-hot: ALL different word pairs have dot product = 0")
print("  Dense:   Similar words have high cosine similarity, unrelated words have low/negative")
print("  → Dense vectors successfully encode semantic similarity!")

# ============================================================
# 7. Generate comparison plot
# ============================================================
outputs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(outputs_dir, exist_ok=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

pair_labels = [f"{w1}\n{w2}" for w1, w2, _ in pairs]
oh_values = [r["dot_product"] for r in onehot_results]
dense_values = [r["cosine_similarity"] for r in dense_results]

# Left: One-hot dot products
colors_oh = ['#3498db'] * len(oh_values)
bars1 = ax1.bar(pair_labels, oh_values, color=colors_oh, edgecolor='#2c3e50', linewidth=0.8)
ax1.set_title('One-hot Dot Products\n(all different words = 0)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Dot Product', fontsize=10)
ax1.set_ylim(-0.2, 1.2)
ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
for bar, val in zip(bars1, oh_values):
    ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
             f'{val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Right: Dense cosine similarities
colors_dense = ['#e74c3c' if v > 0.5 else '#f39c12' if v > 0 else '#95a5a6' for v in dense_values]
bars2 = ax2.bar(pair_labels, dense_values, color=colors_dense, edgecolor='#2c3e50', linewidth=0.8)
ax2.set_title('Dense Cosine Similarities\n(similar words ≈ 1, unrelated < 0)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Cosine Similarity', fontsize=10)
ax2.set_ylim(-0.5, 1.2)
ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
for bar, val in zip(bars2, dense_values):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
             f'{val:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plot_path = os.path.join(outputs_dir, "one-hot-vs-dense-comparison.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nPlot saved: {plot_path}")

# ============================================================
# 8. Save results as JSON
# ============================================================
results = {
    "vocabulary": vocab,
    "vocabulary_size": V,
    "one_hot_results": onehot_results,
    "dense_results": dense_results,
    "dense_vectors": {k: v.tolist() for k, v in dense_vectors.items()},
}

json_path = os.path.join(outputs_dir, "one-hot-vs-dense-results.json")
with open(json_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"Results saved: {json_path}")

print("\n✅ Done. All outputs in outputs/")
