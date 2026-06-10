#!/usr/bin/env python3
"""
CS224N L01 Word Vectors - Code Capsule: negative-sampling-demo
Waypoint WP04: Negative sampling vs full softmax

Concept:
  Full softmax in skip-gram requires computing P(o|c) over the ENTIRE vocabulary
  for every training step: P(o|c) = exp(u_o^T v_c) / sum_w exp(u_w^T v_c).
  When |V| is large (e.g., 500,000), this denominator is extremely expensive.

  Negative sampling (Mikolov et al., 2013, "Distributed Representations of Words
  and Phrases and their Compositionality") replaces the full softmax with k binary
  classification problems: push the positive pair together, push k negative pairs
  apart. Each step costs O(k) instead of O(|V|).

Official anchors:
  - notes 3.5 Eq.14-Eq.15 (softmax partition function and SGNS)
  - slides p35 (SGD cost motivation)
  - R02: Mikolov et al. 2013, negative sampling paper
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime, timezone

# ============================================================
# Setup: tiny vocabulary with random embeddings
# ============================================================
np.random.seed(42)

VOCAB = [
    "bank", "river", "money", "loan", "stock",
    "market", "water", "flow", "stream", "deposit",
    "invest", "trade", "lake", "current", "fund",
    "credit", "bridge", "shore", "rate", "bond"
]
VOCAB_SIZE = len(VOCAB)
EMBED_DIM = 8
WORD2IDX = {w: i for i, w in enumerate(VOCAB)}

V = np.random.randn(VOCAB_SIZE, EMBED_DIM) * 0.5
U = np.random.randn(VOCAB_SIZE, EMBED_DIM) * 0.5

CENTER_WORD = "bank"
POS_CONTEXT = "river"
CENTER_IDX = WORD2IDX[CENTER_WORD]
POS_IDX = WORD2IDX[POS_CONTEXT]
v_c = V[CENTER_IDX]

print("=" * 70)
print("CS224N L01 - Code Capsule: negative-sampling-demo")
print("=" * 70)
print(f"\nVocabulary size |V| = {VOCAB_SIZE}")
print(f"Embedding dimension d = {EMBED_DIM}")
print(f"Center word: '{CENTER_WORD}' (index {CENTER_IDX})")
print(f"Positive context: '{POS_CONTEXT}' (index {POS_IDX})")

# ============================================================
# Part 1: Full Softmax
# ============================================================
print("\n" + "=" * 70)
print("PART 1: Full Softmax - P(o|c) over entire vocabulary")
print("=" * 70)

dot_scores = U @ v_c
print(f"\nDot product scores u_w^T v_c for all {VOCAB_SIZE} words:")
print(f"  Shape: {dot_scores.shape}")
print(f"  Min: {dot_scores.min():.4f}, Max: {dot_scores.max():.4f}, Mean: {dot_scores.mean():.4f}")

dot_scores_shifted = dot_scores - dot_scores.max()
exp_scores = np.exp(dot_scores_shifted)
partition_Z = exp_scores.sum()
probs = exp_scores / partition_Z

print(f"\nPartition function Z = sum_w exp(u_w^T v_c) = {partition_Z:.4f}")
print(f"Number of exp() calls needed: {VOCAB_SIZE} (one per vocabulary word)")

print(f"\nFull softmax probabilities P(o|c='{CENTER_WORD}'):")
print(f"{'Word':<12} {'dot score':>10} {'exp(score)':>12} {'P(o|c)':>10}")
print("-" * 48)
sorted_indices = np.argsort(-probs)
for rank, idx in enumerate(sorted_indices):
    marker = " <-- positive" if idx == POS_IDX else ""
    print(f"{VOCAB[idx]:<12} {dot_scores[idx]:>10.4f} {exp_scores[idx]:>12.4f} {probs[idx]:>10.6f}{marker}")

full_softmax_loss = -np.log(probs[POS_IDX])
print(f"\nFull softmax loss = -log P('{POS_CONTEXT}'|'{CENTER_WORD}') = -log({probs[POS_IDX]:.6f}) = {full_softmax_loss:.4f}")
print(f"Computational cost: {VOCAB_SIZE} dot products + {VOCAB_SIZE} exp() + 1 sum = O(|V|) = O({VOCAB_SIZE})")

# ============================================================
# Part 2: Negative Sampling
# ============================================================
print("\n" + "=" * 70)
print("PART 2: Negative Sampling - k=5 binary classifiers")
print("=" * 70)

K = 5
np.random.seed(123)

neg_candidates = [i for i in range(VOCAB_SIZE) if i != POS_IDX]
neg_indices = np.random.choice(neg_candidates, size=K, replace=False)

print(f"\nNumber of negative samples k = {K}")
print(f"Positive pair: ('{CENTER_WORD}', '{POS_CONTEXT}')")
print(f"Negative pairs:")
for i, neg_idx in enumerate(neg_indices):
    print(f"  {i+1}. ('{CENTER_WORD}', '{VOCAB[neg_idx]}')")

def sigmoid(x):
    return np.where(x >= 0,
                    1.0 / (1.0 + np.exp(-x)),
                    np.exp(x) / (1.0 + np.exp(x)))

print(f"\nBinary logistic losses:")
print(f"{'Type':<12} {'Word':<12} {'u^T v':>10} {'sigma':>10} {'-log(sigma)':>12}")
print("-" * 60)

pos_dot = float(U[POS_IDX] @ v_c)
pos_sigma = float(sigmoid(np.array(pos_dot)))
pos_loss = -np.log(pos_sigma)
print(f"{'positive':<12} {POS_CONTEXT:<12} {pos_dot:>10.4f} {pos_sigma:>10.6f} {pos_loss:>12.4f}")

total_neg_loss = 0.0
neg_dots = []
for neg_idx in neg_indices:
    neg_dot = float(U[neg_idx] @ v_c)
    neg_sigma = float(sigmoid(np.array(-neg_dot)))
    neg_loss_i = -np.log(neg_sigma)
    total_neg_loss += neg_loss_i
    neg_dots.append(neg_dot)
    print(f"{'negative':<12} {VOCAB[neg_idx]:<12} {neg_dot:>10.4f} {neg_sigma:>10.6f} {neg_loss_i:>12.4f}")

sgns_loss = pos_loss + total_neg_loss
print(f"\nTotal SGNS loss = {pos_loss:.4f} + {total_neg_loss:.4f} = {sgns_loss:.4f}")
print(f"Computational cost: {K+1} dot products + {K+1} sigmoid = O(k) = O({K+1})")

# ============================================================
# Part 3: Cost comparison
# ============================================================
print("\n" + "=" * 70)
print("PART 3: Computational Cost Comparison")
print("=" * 70)

neg_label = f"Neg sampling (k={K})"
print(f"\n{'Method':<25} {'Dot products':>14} {'Exp/sigmoid':>14} {'Total ops':>12}")
print("-" * 68)
print(f"{'Full softmax':<25} {VOCAB_SIZE:>14} {VOCAB_SIZE:>14} {2*VOCAB_SIZE:>12}")
print(f"{neg_label:<25} {K+1:>14} {K+1:>14} {2*(K+1):>12}")
print(f"\nSpeedup factor: {2*VOCAB_SIZE / (2*(K+1)):.1f}x for |V|={VOCAB_SIZE}, k={K}")
print(f"With real |V|=500,000 and k=5: speedup = {500000 // 6:,}x")

# ============================================================
# Part 4: Gradient direction
# ============================================================
print("\n" + "=" * 70)
print("PART 4: Gradient Direction - Pull vs Push")
print("=" * 70)

grad_coeff_pos = -(1 - pos_sigma)
grad_from_pos = grad_coeff_pos * U[POS_IDX]

print(f"\nGradient contribution to v_c (center='{CENTER_WORD}'):")
print(f"\nFrom positive pair ('{POS_CONTEXT}'):")
print(f"  Coefficient: -(1 - sigma(u_o^T v_c)) = -(1 - {pos_sigma:.4f}) = {grad_coeff_pos:.4f}")
print(f"  Direction: coefficient is NEGATIVE => v_c is PUSHED TOWARD u_{POS_CONTEXT}")
print(f"  Gradient vector norm: {np.linalg.norm(grad_from_pos):.4f}")

grad_from_neg_total = np.zeros(EMBED_DIM)
print(f"\nFrom negative pairs (summed):")
for i, neg_idx in enumerate(neg_indices):
    neg_sigma_val = float(sigmoid(np.array(-neg_dots[i])))
    grad_coeff_neg = (1 - neg_sigma_val)
    grad_neg_i = grad_coeff_neg * U[neg_idx]
    grad_from_neg_total += grad_neg_i
    print(f"  {VOCAB[neg_idx]:<12}: coeff = (1 - sigma(-u^T v)) = {grad_coeff_neg:.4f} => v_c PUSHED AWAY from u_{VOCAB[neg_idx]}")

print(f"\n  Total negative gradient norm: {np.linalg.norm(grad_from_neg_total):.4f}")
print(f"  Net gradient norm: {np.linalg.norm(grad_from_pos + grad_from_neg_total):.4f}")
print(f"\n  Interpretation: v_c is pulled toward u_{POS_CONTEXT} and pushed away from")
print(f"  the {K} negative context vectors simultaneously.")

# ============================================================
# Part 5: Generate plots
# ============================================================
print("\n" + "=" * 70)
print("PART 5: Generating plots")
print("=" * 70)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Plot 1: Full softmax probability distribution
fig, ax = plt.subplots(figsize=(12, 5))
colors = ['#e74c3c' if idx == POS_IDX else '#3498db' for idx in sorted_indices]
bars = ax.bar(range(VOCAB_SIZE), probs[sorted_indices], color=colors, edgecolor='white', linewidth=0.5)
ax.set_xticks(range(VOCAB_SIZE))
ax.set_xticklabels([VOCAB[i] for i in sorted_indices], rotation=45, ha='right', fontsize=9)
ax.set_ylabel('P(o | c = "bank")', fontsize=11)
ax.set_title('Full Softmax: P(o|c) over entire vocabulary (|V|=20)\nRed = positive context word "river"', fontsize=12)
ax.set_xlabel('Context words (sorted by probability)', fontsize=10)
pos_rank = list(sorted_indices).index(POS_IDX)
ax.annotate(f'P(river|bank) = {probs[POS_IDX]:.6f}',
            xy=(pos_rank, probs[POS_IDX]),
            xytext=(pos_rank + 3, probs[POS_IDX] + 0.05),
            arrowprops=dict(arrowstyle='->', color='red'),
            fontsize=9, color='red', fontweight='bold')
plt.tight_layout()
plot1_path = os.path.join(OUTPUT_DIR, "negative-sampling-demo-full-softmax-probs.png")
plt.savefig(plot1_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot1_path}")

# Plot 2: Cost comparison
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
methods = ['Full Softmax', f'SGNS (k={K})']
dot_counts = [VOCAB_SIZE, K + 1]
colors_cost = ['#e74c3c', '#2ecc71']
bars = axes[0].bar(methods, dot_counts, color=colors_cost, edgecolor='white', width=0.5)
for bar, count in zip(bars, dot_counts):
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                 str(count), ha='center', va='bottom', fontweight='bold', fontsize=12)
axes[0].set_ylabel('Number of dot products', fontsize=11)
axes[0].set_title('Dot Products per Training Step', fontsize=12)
axes[0].set_ylim(0, max(dot_counts) * 1.2)

vocab_sizes = [100, 1000, 10000, 50000, 500000]
speedups = [vs / (K + 1) for vs in vocab_sizes]
axes[1].bar(range(len(vocab_sizes)), speedups, color='#3498db', edgecolor='white', width=0.5)
axes[1].set_xticks(range(len(vocab_sizes)))
axes[1].set_xticklabels([f'{vs:,}' for vs in vocab_sizes], fontsize=9)
for i, sp in enumerate(speedups):
    axes[1].text(i, sp + max(speedups) * 0.02, f'{sp:.0f}x',
                 ha='center', va='bottom', fontweight='bold', fontsize=10)
axes[1].set_xlabel('Vocabulary size |V|', fontsize=11)
axes[1].set_ylabel('Speedup factor', fontsize=11)
axes[1].set_title(f'Speedup of SGNS (k={K}) over Full Softmax', fontsize=12)
axes[1].set_yscale('log')
plt.tight_layout()
plot2_path = os.path.join(OUTPUT_DIR, "negative-sampling-demo-cost-comparison.png")
plt.savefig(plot2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot2_path}")

# Plot 3: Gradient direction
fig, ax = plt.subplots(figsize=(8, 8))
v_c_2d = np.array([1.0, 0.0])
u_pos_2d = np.array([np.cos(np.pi/6), np.sin(np.pi/6)]) * 1.5
neg_angles = [np.pi * 0.6, np.pi * 0.85, np.pi * 1.1, np.pi * 1.4, np.pi * 1.7]
neg_2d = [np.array([np.cos(a), np.sin(a)]) * 1.3 for a in neg_angles]
neg_words = [VOCAB[i] for i in neg_indices]

ax.annotate('', xy=v_c_2d * 1.2, xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', lw=2.5, color='#2c3e50'))
ax.text(v_c_2d[0] * 1.3, v_c_2d[1] * 1.3, f'v_"bank"',
        fontsize=11, fontweight='bold', color='#2c3e50', ha='center')
ax.annotate('', xy=u_pos_2d, xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', lw=2.5, color='#e74c3c'))
ax.text(u_pos_2d[0] * 1.15, u_pos_2d[1] * 1.15, f'u_"river"',
        fontsize=11, fontweight='bold', color='#e74c3c', ha='center')
pull_dir = u_pos_2d - v_c_2d * 0.5
pull_dir = pull_dir / np.linalg.norm(pull_dir) * 0.6
ax.annotate('', xy=v_c_2d + pull_dir, xytext=v_c_2d,
            arrowprops=dict(arrowstyle='->', lw=2, color='#e74c3c', linestyle='dashed'))
ax.text(v_c_2d[0] + pull_dir[0] + 0.1, v_c_2d[1] + pull_dir[1] + 0.05,
        'pull\ncloser', fontsize=9, color='#e74c3c', ha='left')

for i, (n2d, word) in enumerate(zip(neg_2d, neg_words)):
    ax.annotate('', xy=n2d, xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='#3498db', alpha=0.7))
    ax.text(n2d[0] * 1.15, n2d[1] * 1.15, f'u_"{word}"',
            fontsize=8, color='#3498db', ha='center')
    push_dir = v_c_2d - n2d
    push_dir = push_dir / np.linalg.norm(push_dir) * 0.35
    ax.annotate('', xy=v_c_2d + push_dir * 0.5, xytext=v_c_2d,
                arrowprops=dict(arrowstyle='->', lw=1.2, color='#3498db', linestyle='dotted'))

ax.text(-0.6, -0.5, 'push\napart', fontsize=9, color='#3498db', ha='center')
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_aspect('equal')
ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='--')
ax.axvline(x=0, color='gray', linewidth=0.5, linestyle='--')
ax.set_title('Gradient Direction: Positive Pull vs Negative Push\n(on v_"bank" in projected 2D space)',
             fontsize=12)
ax.set_xlabel('Dimension 1 (schematic)', fontsize=10)
ax.set_ylabel('Dimension 2 (schematic)', fontsize=10)
plt.tight_layout()
plot3_path = os.path.join(OUTPUT_DIR, "negative-sampling-demo-gradient-direction.png")
plt.savefig(plot3_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot3_path}")

# ============================================================
# Part 6: Save structured results JSON
# ============================================================
results = {
    "vocabulary_size": VOCAB_SIZE,
    "embed_dim": EMBED_DIM,
    "center_word": CENTER_WORD,
    "positive_context": POS_CONTEXT,
    "partition_Z": round(float(partition_Z), 4),
    "p_positive": round(float(probs[POS_IDX]), 6),
    "full_softmax_loss": round(float(full_softmax_loss), 4),
    "k_negative_samples": K,
    "negative_words": [VOCAB[i] for i in neg_indices],
    "sgns_total_loss": round(float(sgns_loss), 4),
    "positive_loss": round(float(pos_loss), 4),
    "negative_loss_sum": round(float(total_neg_loss), 4),
    "speedup_toy": round(2*VOCAB_SIZE / (2*(K+1)), 1),
    "speedup_real": 500000 // (K+1),
    "grad_coeff_positive": round(float(grad_coeff_pos), 4),
    "grad_norm_positive": round(float(np.linalg.norm(grad_from_pos)), 4),
    "grad_norm_negative_total": round(float(np.linalg.norm(grad_from_neg_total)), 4),
    "grad_norm_net": round(float(np.linalg.norm(grad_from_pos + grad_from_neg_total)), 4),
}
results_path = os.path.join(OUTPUT_DIR, "negative-sampling-demo-results.json")
with open(results_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"  Saved: {results_path}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
Full softmax:
  - Computes P(o|c) for ALL {VOCAB_SIZE} vocabulary words
  - Partition function Z = {partition_Z:.4f} (requires {VOCAB_SIZE} exp() calls)
  - Loss = -log P('{POS_CONTEXT}'|'{CENTER_WORD}') = {full_softmax_loss:.4f}
  - Cost: O(|V|) = O({VOCAB_SIZE})

Negative sampling (k={K}):
  - 1 positive pair + {K} negative pairs
  - Each pair: binary logistic loss (sigmoid, not softmax)
  - Total loss = {sgns_loss:.4f}
  - Cost: O(k) = O({K+1})

Speedup: {2*VOCAB_SIZE / (2*(K+1)):.1f}x for |V|={VOCAB_SIZE}; {500000 // (K+1):,}x for |V|=500,000

Gradient intuition:
  - Positive pair: v_c is PULLED TOWARD u_o (coefficient = {grad_coeff_pos:.4f})
  - Negative pairs: v_c is PUSHED AWAY from each u_neg
  - Net effect: learn to distinguish true context from noise
""")

print(f"Script completed at {datetime.now(timezone.utc).isoformat()}")
print(f"Exit code: 0")
