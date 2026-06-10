#!/usr/bin/env python3
"""
Supplementary visualization for negative-sampling-demo capsule.
Generates gradient-direction and scaling comparison charts.
Requires: numpy, matplotlib (both available in Colab by default).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

np.random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Same setup as the main script for consistency
VOCAB = ["banking", "problems", "crises", "money", "loans",
         "river", "tree", "banana", "dog", "music",
         "thought", "flow"]
VOCAB_SIZE = len(VOCAB)
EMBED_DIM = 4

v_c = np.random.randn(EMBED_DIM) * 0.3
U = np.random.randn(VOCAB_SIZE, EMBED_DIM) * 0.3

center_idx = 0  # "banking"
positive_idx = 3  # "money"

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

# Full softmax probabilities
dot_products = U @ v_c
max_score = np.max(dot_products)
exp_scores = np.exp(dot_products - max_score)
partition_Z = np.sum(exp_scores)
probs = exp_scores / partition_Z

# SGNS negative samples
K = 5
neg_candidates = [i for i in range(VOCAB_SIZE) if i != positive_idx]
negative_indices = np.random.choice(neg_candidates, size=K, replace=False)

# Full softmax gradient: observed - expected
grad_full = U[positive_idx] - probs @ U

# SGNS gradient: positive pull + negative pushes
pos_dot = U[positive_idx] @ v_c
grad_pos = (sigmoid(pos_dot) - 1.0) * U[positive_idx]
grad_neg = np.zeros(EMBED_DIM)
for neg_idx in negative_indices:
    grad_neg += sigmoid(U[neg_idx] @ v_c) * U[neg_idx]
grad_sgns = grad_pos + grad_neg

# ============================================================
# Chart 1: Gradient direction comparison (2D projection)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Full softmax gradient
ax = axes[0]
for i, word in enumerate(VOCAB):
    is_pos = (i == positive_idx)
    is_neg = (i in negative_indices)
    color = '#2ecc71' if is_pos else ('#e74c3c' if is_neg else '#bdc3c7')
    marker = '*' if is_pos else ('x' if is_neg else 'o')
    size = 200 if is_pos else (120 if is_neg else 60)
    ax.scatter(U[i, 0], U[i, 1], c=color, marker=marker, s=size, zorder=5,
               edgecolors='black', linewidths=0.5)
    ax.annotate(word, (U[i, 0], U[i, 1]), fontsize=8, ha='center', va='bottom',
                xytext=(0, 5), textcoords='offset points',
                fontweight='bold' if (is_pos or is_neg) else 'normal')

# Draw gradient arrow
scale = 5
ax.annotate('', xy=(v_c[0] + grad_full[0]*scale, v_c[1] + grad_full[1]*scale),
            xytext=(v_c[0], v_c[1]),
            arrowprops=dict(arrowstyle='->', color='#2980b9', lw=2.5))
ax.scatter(v_c[0], v_c[1], c='#2980b9', marker='s', s=120, zorder=6,
           edgecolors='black', linewidths=1, label="v_c (center: banking)")
ax.set_title('Full Softmax Gradient\n∂J/∂v_c = u_o − Σ P(w|c)·u_w\n(subtracts expected over ALL |V| words)',
             fontsize=11, fontweight='bold')
ax.set_xlabel('embedding dim 0')
ax.set_ylabel('embedding dim 1')
ax.legend(fontsize=9, loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

# Right: SGNS gradient
ax = axes[1]
for i, word in enumerate(VOCAB):
    is_pos = (i == positive_idx)
    is_neg = (i in negative_indices)
    color = '#2ecc71' if is_pos else ('#e74c3c' if is_neg else '#ecf0f1')
    marker = '*' if is_pos else ('x' if is_neg else 'o')
    size = 200 if is_pos else (120 if is_neg else 40)
    alpha = 1.0 if (is_pos or is_neg) else 0.3
    ax.scatter(U[i, 0], U[i, 1], c=color, marker=marker, s=size, zorder=5,
               alpha=alpha, edgecolors='black', linewidths=0.5)
    if is_pos or is_neg:
        ax.annotate(word, (U[i, 0], U[i, 1]), fontsize=9, ha='center', va='bottom',
                    xytext=(0, 5), textcoords='offset points', fontweight='bold')

ax.annotate('', xy=(v_c[0] + grad_sgns[0]*scale, v_c[1] + grad_sgns[1]*scale),
            xytext=(v_c[0], v_c[1]),
            arrowprops=dict(arrowstyle='->', color='#e67e22', lw=2.5))
ax.scatter(v_c[0], v_c[1], c='#2980b9', marker='s', s=120, zorder=6,
           edgecolors='black', linewidths=1, label="v_c (center: banking)")
ax.set_title(f'SGNS Gradient (k={K})\n∂J/∂v_c ≈ (σ⁺−1)·u_o + Σ σ⁻·u_ℓ\n(only pushes k={K} sampled negatives)',
             fontsize=11, fontweight='bold')
ax.set_xlabel('embedding dim 0')
ax.set_ylabel('embedding dim 1')
ax.legend(fontsize=9, loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

plt.tight_layout()
path1 = os.path.join(OUTPUT_DIR, "negative-sampling-gradient-direction.png")
plt.savefig(path1, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {path1}")

# ============================================================
# Chart 2: Scaling comparison (log-log)
# ============================================================
fig, ax = plt.subplots(figsize=(9, 5))

vocab_sizes = np.array([100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000])
ax.loglog(vocab_sizes, vocab_sizes, 'b-o', linewidth=2, markersize=6, label='Full Softmax O(|V|)')
ax.loglog(vocab_sizes, np.full_like(vocab_sizes, 6), 'r--s', linewidth=2, markersize=6, label='SGNS k=5 (6 dot products)')
ax.loglog(vocab_sizes, np.full_like(vocab_sizes, 21), 'g--^', linewidth=2, markersize=6, label='SGNS k=20 (21 dot products)')

ax.set_xlabel('Vocabulary size |V|', fontsize=12)
ax.set_ylabel('Dot products per training step', fontsize=12)
ax.set_title('Computational Cost: Full Softmax vs Negative Sampling\n(log-log scale)',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=10, loc='upper left')
ax.grid(True, alpha=0.3, which='both')

# Annotate speedup
ax.annotate('~333,000x fewer\ndot products', xy=(1000000, 6), xytext=(50000, 2000),
            fontsize=10, fontweight='bold', color='#e74c3c',
            arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffeaa7', edgecolor='#e74c3c', alpha=0.8))

plt.tight_layout()
path2 = os.path.join(OUTPUT_DIR, "negative-sampling-scaling-comparison.png")
plt.savefig(path2, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {path2}")

# ============================================================
# Chart 3: Loss decomposition (positive + negatives)
# ============================================================
fig, ax = plt.subplots(figsize=(8, 5))

pos_loss = -np.log(sigmoid(pos_dot) + 1e-10)
neg_losses = []
neg_words = []
for neg_idx in negative_indices:
    neg_dot = U[neg_idx] @ v_c
    neg_losses.append(-np.log(sigmoid(-neg_dot) + 1e-10))
    neg_words.append(VOCAB[neg_idx])

labels = ['positive\n(banking-money)'] + [f'neg {j+1}\n({VOCAB[negative_indices[j]]})' for j in range(K)]
losses = [pos_loss] + neg_losses
colors = ['#2ecc71'] + ['#e74c3c'] * K

bars = ax.bar(labels, losses, color=colors, edgecolor='black', linewidth=0.8)
for bar, loss in zip(bars, losses):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
            f'{loss:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.axhline(y=pos_loss + sum(neg_losses), color='blue', linestyle='--', linewidth=1.5,
           label=f'Total SGNS loss = {pos_loss + sum(neg_losses):.3f}')
ax.set_ylabel('Binary logistic loss (-log σ)', fontsize=11)
ax.set_title(f'Negative Sampling Loss Decomposition (k={K})\nGreen = pull positive closer; Red = push negative away',
             fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.set_ylim(0, max(losses) * 1.3)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
path3 = os.path.join(OUTPUT_DIR, "negative-sampling-loss-decomposition.png")
plt.savefig(path3, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: {path3}")

print(f"\nAll 3 charts saved to {OUTPUT_DIR}")
