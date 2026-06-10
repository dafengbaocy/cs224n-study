#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: softmax-probability (WP03)

Demonstrates the softmax probability computation from:
  - slides p28-p30: P(o|c) = exp(u_o^T v_c) / sum_w exp(u_w^T v_c)
  - notes §3.2 Eq.4-Eq.5

Why this capsule matters:
  The denominator over the whole vocabulary is easy to gloss over in formulas.
  Running it on a tiny vocabulary shows dot product scores, exponentials,
  normalization, and probability mass — making the "soft" in softmax visible.

Official anchor:
  slides p28: two vectors per word (v_w center, u_w outside/context)
  slides p30: three-step breakdown — dot product → exponentiate → normalize
  notes p8 Eq.4: P(O=o|C=c) = exp(u_o^T v_c) / sum_{w in V} exp(u_w^T v_c)
"""

import numpy as np
import json
import os

# ─────────────────────────────────────────────────────────
# Setup: tiny vocabulary with d=4 dimensional vectors
# ─────────────────────────────────────────────────────────
vocab = ["bank", "river", "money", "food", "cat"]
vocab_size = len(vocab)
d = 4

np.random.seed(42)

V = np.array([
    [0.8,  0.3, -0.1,  0.5],   # bank
    [0.7,  0.5, -0.2,  0.3],   # river
    [0.1, -0.6,  0.9, -0.3],   # money
    [-0.5, 0.2,  0.1,  0.8],   # food
    [-0.3, 0.1, -0.4,  0.6],   # cat
])

U = np.array([
    [0.6,  0.4,  0.0,  0.3],   # bank
    [0.5,  0.6, -0.1,  0.2],   # river
    [0.2, -0.5,  0.8, -0.2],   # money
    [-0.4, 0.3,  0.2,  0.7],   # food
    [-0.2, 0.0, -0.3,  0.5],   # cat
])

# ─────────────────────────────────────────────────────────
# Step 1: Choose center word, compute dot products
# ─────────────────────────────────────────────────────────
center_word = "bank"
center_idx = vocab.index(center_word)
v_c = V[center_idx]

print("=" * 70)
print("CS224N L01 — Code Capsule: softmax-probability (WP03)")
print("=" * 70)
print()
print(f"Center word: '{center_word}'")
print(f"Center vector v_c = {v_c.tolist()}")
print(f"Embedding dimension d = {d}")
print(f"Vocabulary size |V| = {vocab_size}")
print()

print("-" * 70)
print("Step 1: Dot product scores  u_w^T v_c  (slides p28, p30 step 1)")
print("-" * 70)
print(f"{'Word':<10} {'u_w · v_c':>10}")
print("-" * 25)

dot_scores = []
for i, w in enumerate(vocab):
    score = np.dot(U[i], v_c)
    dot_scores.append(score)
    print(f"{w:<10} {score:>10.4f}")

dot_scores = np.array(dot_scores)
print()
print(f"Raw scores vector: {dot_scores.tolist()}")
print()

# ─────────────────────────────────────────────────────────
# Step 2: Exponentiate
# ─────────────────────────────────────────────────────────
print("-" * 70)
print("Step 2: Exponentiate  exp(u_w^T v_c)  (slides p30 step 2)")
print("-" * 70)
print(f"{'Word':<10} {'u_w · v_c':>10} {'exp(score)':>12}")
print("-" * 35)

exp_scores = np.exp(dot_scores)
for i, w in enumerate(vocab):
    print(f"{w:<10} {dot_scores[i]:>10.4f} {exp_scores[i]:>12.4f}")

Z = np.sum(exp_scores)
print()
print(f"Sum of exp scores (partition function Z) = {Z:.4f}")
print()
print("Note: The partition function Z = sum_w exp(u_w^T v_c) requires")
print("scoring against EVERY word in the vocabulary. For real vocabularies")
print("of 500,000+ words, this is extremely expensive -> motivates negative")
print("sampling (WP04).")
print()

# ─────────────────────────────────────────────────────────
# Step 3: Normalize to probabilities
# ─────────────────────────────────────────────────────────
print("-" * 70)
print("Step 3: Normalize  P(o|c) = exp(u_o^T v_c) / Z  (slides p30 step 3)")
print("-" * 70)
print(f"{'Word':<10} {'exp(score)':>12} {'P(o|c)':>10}")
print("-" * 35)

probs = exp_scores / Z
for i, w in enumerate(vocab):
    bar = "█" * int(probs[i] * 50)
    print(f"{w:<10} {exp_scores[i]:>12.4f} {probs[i]:>10.4f}  {bar}")

print()
print(f"Sum of all probabilities = {np.sum(probs):.6f} (must be 1.0)")
print()

# ─────────────────────────────────────────────────────────
# Interpretation
# ─────────────────────────────────────────────────────────
print("-" * 70)
print("Interpretation")
print("-" * 70)
print()

sorted_indices = np.argsort(-probs)
print("Top-3 most probable context words for center='bank':")
for rank, idx in enumerate(sorted_indices[:3], 1):
    print(f"  {rank}. {vocab[idx]:<10} P = {probs[idx]:.4f}")
print()

print("Key observations:")
print(f"  P(river|bank)  = {probs[vocab.index('river')]:.4f}  (semantically related — nature sense)")
print(f"  P(money|bank)  = {probs[vocab.index('money')]:.4f}  (semantically related — financial sense)")
print(f"  P(food|bank)   = {probs[vocab.index('food')]:.4f}   (unrelated)")
print(f"  P(cat|bank)    = {probs[vocab.index('cat')]:.4f}   (unrelated)")
print()

# ─────────────────────────────────────────────────────────
# Connection to slides p30
# ─────────────────────────────────────────────────────────
print("-" * 70)
print("Connection to slides p30: three-step softmax breakdown")
print("-" * 70)
print()
print("1. Compare similarity: dot product u_o^T v_c")
print(f"   -> highest raw score: '{vocab[np.argmax(dot_scores)]}' = {np.max(dot_scores):.4f}")
print()
print("2. Exponentiate: exp(score) -> all positive, amplifies differences")
print(f"   -> max exp score: '{vocab[np.argmax(exp_scores)]}' = {np.max(exp_scores):.4f}")
print(f"   -> min exp score: '{vocab[np.argmin(exp_scores)]}' = {np.min(exp_scores):.4f}")
ratio = np.max(exp_scores) / np.min(exp_scores)
print(f"   -> ratio max/min = {ratio:.1f}x (exponentiation amplifies differences)")
print()
print("3. Normalize: divide by Z -> valid probability distribution")
print(f"   -> Z = {Z:.4f}")
print(f"   -> all P(o|c) sum to {np.sum(probs):.6f}")
print()

# ─────────────────────────────────────────────────────────
# Save outputs
# ─────────────────────────────────────────────────────────
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(output_dir, exist_ok=True)

output_data = {
    "center_word": center_word,
    "center_vector": v_c.tolist(),
    "vocabulary": vocab,
    "embedding_dim": d,
    "dot_scores": {w: float(dot_scores[i]) for i, w in enumerate(vocab)},
    "exp_scores": {w: float(exp_scores[i]) for i, w in enumerate(vocab)},
    "partition_function_Z": float(Z),
    "probabilities": {w: float(probs[i]) for i, w in enumerate(vocab)},
    "probability_sum": float(np.sum(probs)),
}

json_path = os.path.join(output_dir, "softmax-probability-results.json")
with open(json_path, "w") as f:
    json.dump(output_data, f, indent=2)
print(f"Structured results saved to: {json_path}")

# ─────────────────────────────────────────────────────────
# Generate plots
# ─────────────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    colors = ["#2196F3"] * vocab_size
    ax1 = axes[0]
    bars1 = ax1.bar(vocab, dot_scores, color=colors, edgecolor="black", linewidth=0.5)
    ax1.set_title("Step 1: Dot Product Scores\n$u_w^T v_c$", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Score")
    ax1.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)
    for bar, score in zip(bars1, dot_scores):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f"{score:.3f}", ha="center", va="bottom", fontsize=9)

    ax2 = axes[1]
    bars2 = ax2.bar(vocab, exp_scores, color=["#4CAF50"] * vocab_size, edgecolor="black", linewidth=0.5)
    ax2.set_title("Step 2: Exponentiated\n$exp(u_w^T v_c)$", fontsize=12, fontweight="bold")
    ax2.set_ylabel("exp(score)")
    for bar, escore in zip(bars2, exp_scores):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                f"{escore:.2f}", ha="center", va="bottom", fontsize=9)

    ax3 = axes[2]
    highlight_colors = ["#FF9800" if w in ["river", "money"] else "#9E9E9E" for w in vocab]
    bars3 = ax3.bar(vocab, probs, color=highlight_colors, edgecolor="black", linewidth=0.5)
    ax3.set_title("Step 3: Softmax Probabilities\n$P(o|c=bank)$", fontsize=12, fontweight="bold")
    ax3.set_ylabel("P(o|c)")
    ax3.set_ylim(0, max(probs) * 1.3)
    for bar, prob in zip(bars3, probs):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.005,
                f"{prob:.3f}", ha="center", va="bottom", fontsize=9)

    fig.suptitle(f"Softmax Probability Computation — Center word: '{center_word}' (d={d}, |V|={vocab_size})",
                fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()

    plot_path = os.path.join(output_dir, "softmax-probability-bar-chart.png")
    fig.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Bar chart saved to: {plot_path}")

    # Second plot: grouped comparison
    fig2, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(vocab_size)
    width = 0.25
    dot_norm = (dot_scores - dot_scores.min()) / (dot_scores.max() - dot_scores.min() + 1e-10)
    exp_norm = exp_scores / exp_scores.max()
    prob_norm = probs / probs.max()

    ax.bar(x - width, dot_norm, width, label="Dot product (normalized)", color="#2196F3", alpha=0.85, edgecolor="black", linewidth=0.5)
    ax.bar(x, exp_norm, width, label="exp(score) (normalized)", color="#4CAF50", alpha=0.85, edgecolor="black", linewidth=0.5)
    bars_c = ax.bar(x + width, prob_norm, width, label="P(o|c) (normalized)", color="#FF9800", alpha=0.85, edgecolor="black", linewidth=0.5)

    ax.set_xlabel("Outside word $w$", fontsize=12)
    ax.set_ylabel("Normalized value", fontsize=12)
    ax.set_title(f"Softmax Three-Step Breakdown\nCenter word: '{center_word}' | d={d} | |V|={vocab_size}", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(vocab)
    ax.legend(loc="upper right")
    ax.set_ylim(0, 1.15)

    for i, pn in enumerate(prob_norm):
        ax.text(i + width, pn + 0.03, f"{probs[i]:.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    plot2_path = os.path.join(output_dir, "softmax-probability-breakdown.png")
    fig2.savefig(plot2_path, dpi=150, bbox_inches="tight")
    plt.close(fig2)
    print(f"Breakdown chart saved to: {plot2_path}")

except ImportError:
    print("matplotlib not available — skipping plot generation")

print()
print("Done. All outputs in:", output_dir)
