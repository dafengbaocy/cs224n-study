#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: one-hot-vs-dense
=========================================================
Demonstrates why one-hot vectors cannot encode word similarity,
and how dense vectors solve this problem.

Official anchor: Slides p19-22; Notes §2.2 (one-hot vectors, Eq.1-2)

This script uses only numpy + matplotlib (pre-installed in Google Colab).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import json
import os

# ============================================================
# 1. Define a small vocabulary (6 words)
# ============================================================
vocab = ["hotel", "motel", "book", "cat", "dog", "fish"]
vocab_size = len(vocab)

print("=" * 60)
print("CS224N L01 Code Capsule: One-hot vs Dense Vectors")
print("=" * 60)
print(f"\nVocabulary ({vocab_size} words): {vocab}")

# ============================================================
# 2. Build one-hot vectors
# ============================================================
one_hot = {}
for i, word in enumerate(vocab):
    vec = [0] * vocab_size
    vec[i] = 1
    one_hot[word] = vec

print("\n--- One-hot Encoding ---")
for word, vec in one_hot.items():
    print(f"  {word:>6s} = {vec}")

print(f"\nOne-hot vector dimension = vocab_size = {vocab_size}")
print(f"Each vector has exactly 1 non-zero entry.")

# ============================================================
# 3. Show the fatal problem: all dot products are 0
# ============================================================
print("\n--- Dot Products (One-hot) ---")
print("If one-hot encoded similarity, similar words should have high dot product.")
print()

pairs = [
    ("hotel", "motel", "synonyms — should be similar"),
    ("cat", "dog", "both animals — should be somewhat similar"),
    ("book", "fish", "unrelated — should be dissimilar"),
]

oh_dot_products = {}
for w1, w2, desc in pairs:
    v1 = np.array(one_hot[w1])
    v2 = np.array(one_hot[w2])
    dot = float(np.dot(v1, v2))
    oh_dot_products[f"{w1}-{w2}"] = dot
    print(f"  {w1:>6s} · {w2:<6s} = {dot:.1f}   ({desc})")

print("\n⚠️  ALL dot products are 0.0 — one-hot vectors are orthogonal!")
print("   The model cannot tell 'hotel·motel' from 'book·fish'.")

# ============================================================
# 4. Dense vectors (learned embeddings, 2D for visualization)
# ============================================================
# These are hand-crafted to illustrate the CONCEPT.
# In real word2vec, these would be learned from data.
# We place semantically similar words close together.
dense_2d = {
    "hotel": [0.8, 0.7],
    "motel": [0.7, 0.75],   # close to hotel but not collinear
    "book":  [-0.5, 0.3],
    "cat":   [0.1, -0.8],
    "dog":   [0.3, -0.6],   # closer to cat than to fish
    "fish":  [-0.2, -0.9],
}

print("\n--- Dense Vectors (2D illustration) ---")
print("These represent what LEARNED embeddings look like:")
for word, vec in dense_2d.items():
    print(f"  {word:>6s} = [{vec[0]:+.2f}, {vec[1]:+.2f}]")

# ============================================================
# 5. Cosine similarity on dense vectors
# ============================================================
def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

print("\n--- Cosine Similarity (Dense Vectors) ---")
dense_similarities = {}
for w1, w2, desc in pairs:
    sim = cosine_similarity(dense_2d[w1], dense_2d[w2])
    dense_similarities[f"{w1}-{w2}"] = round(sim, 4)
    print(f"  cos({w1}, {w2}) = {sim:.4f}   ({desc})")

print("\n✅ Dense vectors encode similarity: hotel≈motel (high), cat≈dog (medium), book≠fish (low)")

# ============================================================
# 6. Summary table
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY: One-hot vs Dense")
print("=" * 60)
print(f"{'Pair':<20s} {'One-hot dot':>12s} {'Dense cosine':>14s}")
print("-" * 48)
for w1, w2, desc in pairs:
    key = f"{w1}-{w2}"
    print(f"{w1} vs {w2:<12s} {oh_dot_products[key]:>12.1f} {dense_similarities[key]:>14.4f}")

# ============================================================
# 7. Visualization
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# --- Left: One-hot heatmap ---
ax = axes[0]
oh_matrix = np.array([one_hot[w] for w in vocab])
im = ax.imshow(oh_matrix, cmap='Blues', aspect='auto', vmin=0, vmax=1)
ax.set_xticks(range(vocab_size))
ax.set_xticklabels(vocab, rotation=45, ha='right', fontsize=9)
ax.set_yticks(range(vocab_size))
ax.set_yticklabels(vocab, fontsize=9)
ax.set_title("One-hot Vectors (6×6 identity matrix)\nAll pairs orthogonal: dot product = 0", fontsize=11)
ax.set_xlabel("Word index")
ax.set_ylabel("Word")
# Add text annotations
for i in range(vocab_size):
    for j in range(vocab_size):
        val = oh_matrix[i, j]
        color = "white" if val > 0.5 else "black"
        ax.text(j, i, str(int(val)), ha="center", va="center", fontsize=9, color=color)
plt.colorbar(im, ax=ax, shrink=0.8)

# --- Right: Dense vectors in 2D space ---
ax = axes[1]
colors_map = {
    "hotel": "#e74c3c", "motel": "#e67e22",  # warm colors for lodging
    "book": "#3498db",                          # blue for object
    "cat": "#2ecc71", "dog": "#27ae60", "fish": "#1abc9c",  # greens for animals
}

for word, vec in dense_2d.items():
    ax.scatter(vec[0], vec[1], s=200, c=colors_map[word], zorder=5, edgecolors='black', linewidth=0.5)
    ax.annotate(word, (vec[0], vec[1]), fontsize=10, fontweight='bold',
                xytext=(5, 5), textcoords='offset points')

# Draw similarity arcs for key pairs
from matplotlib.patches import FancyArrowPatch
pair_styles = [
    ("hotel", "motel", "#e74c3c", 0.8, "similar"),
    ("cat", "dog", "#27ae60", 0.6, "somewhat similar"),
]
for w1, w2, color, alpha, label in pair_styles:
    v1, v2 = dense_2d[w1], dense_2d[w2]
    ax.plot([v1[0], v2[0]], [v1[1], v2[1]], '--', color=color, alpha=alpha, linewidth=1.5)
    mid_x = (v1[0] + v2[0]) / 2
    mid_y = (v1[1] + v2[1]) / 2
    sim_val = dense_similarities[f"{w1}-{w2}"]
    ax.text(mid_x, mid_y + 0.05, f"cos={sim_val:.3f}", fontsize=8, ha='center',
            color=color, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=color, alpha=0.8))

ax.set_title("Dense Vectors (2D illustration)\nSimilar words are close together", fontsize=11)
ax.set_xlabel("Dimension 1")
ax.set_ylabel("Dimension 2")
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='-')
ax.axvline(x=0, color='gray', linewidth=0.5, linestyle='-')

plt.tight_layout()
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(output_dir, exist_ok=True)
fig_path = os.path.join(output_dir, "one-hot-vs-dense-comparison.png")
plt.savefig(fig_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nFigure saved: {fig_path}")

# ============================================================
# 8. Save structured output as JSON for provenance
# ============================================================
output_data = {
    "capsule": "one-hot-vs-dense",
    "vocab": vocab,
    "vocab_size": vocab_size,
    "one_hot_dot_products": oh_dot_products,
    "dense_cosine_similarities": dense_similarities,
    "key_finding": "All one-hot dot products are 0.0 (orthogonal); dense cosine similarities reflect semantic relatedness.",
}
json_path = os.path.join(output_dir, "one-hot-vs-dense-results.json")
with open(json_path, "w") as f:
    json.dump(output_data, f, indent=2)
print(f"Results JSON saved: {json_path}")

print("\nDone.")
