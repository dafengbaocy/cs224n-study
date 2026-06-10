#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: negative-sampling-loss

Concept: Negative Sampling objective (SGNS) vs full softmax
Official anchor: Notes §3.5 (Eq.14-15, SGNS objective); R02 paper Section 3

This script demonstrates:
1. Full softmax loss: requires summing over ALL vocabulary words (expensive)
2. Negative sampling loss: replaces softmax with k binary logistic classifications
3. Loss comparison: how NS loss relates to softmax loss
4. Effect of k (number of negative samples) on loss and gradient behavior
5. Computational efficiency: O(k) vs O(|V|) per gradient update

References:
- Notes Eq.14: P(c|o) = exp(u_c^T v_o) / Σ_w exp(u_w^T v_o)
- Notes Eq.15: J_NS = -log σ(u_o^T v_c) - Σ_{ℓ=1}^{k} log σ(-u_ℓ^T v_c)
- σ is the logistic/sigmoid function
- u_ℓ are negative samples drawn from p_neg (noise distribution)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import os

np.random.seed(42)

# ============================================================
# Setup: small vocabulary with word vectors
# ============================================================
VOCAB_SIZE = 10000  # Realistic vocabulary size
DIM = 50            # Embedding dimension

U = np.random.randn(VOCAB_SIZE, DIM) * 0.1  # output vectors (context)
V = np.random.randn(VOCAB_SIZE, DIM) * 0.1  # input vectors (center)

center_idx = 42
context_idx = 100
v_c = V[center_idx]
u_o = U[context_idx]

print("=" * 70)
print("CS224N L01 Code Capsule: Negative Sampling Loss vs Full Softmax")
print("=" * 70)
print(f"\nSetup:")
print(f"  Vocabulary size |V| = {VOCAB_SIZE}")
print(f"  Embedding dimension = {DIM}")
print(f"  Center word index = {center_idx}")
print(f"  Context word index = {context_idx}")
print(f"  ||v_c|| = {np.linalg.norm(v_c):.4f}")
print(f"  ||u_o|| = {np.linalg.norm(u_o):.4f}")
print(f"  u_o^T v_c = {np.dot(u_o, v_c):.4f}")

# ============================================================
# Part 1: Full Softmax Loss (Eq.14)
# ============================================================
print("\n" + "=" * 70)
print("Part 1: Full Softmax Loss (Notes Eq.14)")
print("=" * 70)
print("\nEq.14: P(c|o) = exp(u_c^T v_o) / Σ_w exp(u_w^T v_o)")
print("The denominator (partition function) sums over ALL |V| words.")

scores = U @ v_c
scores_shifted = scores - np.max(scores)
exp_scores = np.exp(scores_shifted)
partition_function = np.sum(exp_scores)
softmax_probs = exp_scores / partition_function
softmax_loss = -np.log(softmax_probs[context_idx] + 1e-10)

print(f"\n  Score for observed context word (u_o^T v_c): {scores[context_idx]:.6f}")
print(f"  Partition function Z = Σ_w exp(u_w^T v_c): {partition_function:.6f}")
print(f"  P(context|center) under softmax: {softmax_probs[context_idx]:.8f}")
print(f"  Softmax loss = -log P(c|o): {softmax_loss:.6f}")
print(f"  Number of exp() evaluations: {VOCAB_SIZE} (entire vocabulary!)")

grad_u_o_softmax = (softmax_probs[context_idx] - 1.0) * v_c
print(f"\n  Gradient ∂L/∂u_o (softmax):")
print(f"    = (P(c|o) - 1) · v_c")
print(f"    = ({softmax_probs[context_idx]:.8f} - 1) · v_c")
print(f"    ||∂L/∂u_o|| = {np.linalg.norm(grad_u_o_softmax):.6f}")
print(f"    NOTE: Computing this gradient required ALL {VOCAB_SIZE} probabilities!")

# ============================================================
# Part 2: Negative Sampling Loss (Eq.15)
# ============================================================
print("\n" + "=" * 70)
print("Part 2: Negative Sampling Loss (Notes Eq.15)")
print("=" * 70)
print("\nEq.15: J_NS = -log σ(u_o^T v_c) - Σ_{ℓ=1}^{k} log σ(-u_ℓ^T v_c)")
print("Only k+1 dot products needed instead of |V|!")

def sigmoid(x):
    """Numerically stable sigmoid."""
    return np.where(x >= 0,
                    1.0 / (1.0 + np.exp(-x)),
                    np.exp(x) / (1.0 + np.exp(x)))

def negative_sampling_loss(v_c, u_o, U_neg, k):
    """Compute negative sampling loss."""
    pos_score = np.dot(u_o, v_c)
    pos_loss = -np.log(sigmoid(pos_score) + 1e-10)
    neg_scores = U_neg @ v_c
    neg_loss = -np.sum(np.log(sigmoid(-neg_scores) + 1e-10))
    return pos_loss + neg_loss

k_values = [1, 5, 10, 25]
print(f"\n{'k':>4} | {'NS Loss':>10} | {'Softmax Loss':>13} | {'Diff':>8} | {'Dot products':>13}")
print("-" * 60)
print(f"{'—':>4} | {'—':>10} | {softmax_loss:>13.6f} | {'—':>8} | {VOCAB_SIZE:>13}")

for k in k_values:
    neg_indices = np.random.choice(VOCAB_SIZE, size=k, replace=False)
    while context_idx in neg_indices:
        neg_indices = np.random.choice(VOCAB_SIZE, size=k, replace=False)
    U_neg = U[neg_indices]
    ns_loss = negative_sampling_loss(v_c, u_o, U_neg, k)
    diff = ns_loss - softmax_loss
    print(f"{k:>4} | {ns_loss:>10.6f} | {softmax_loss:>13.6f} | {diff:>+8.4f} | {k+1:>13}")

print(f"\n  Key insight: NS loss does NOT equal softmax loss.")
print(f"  NS is a DIFFERENT objective — binary classification:")
print(f"    'Is (center, context) a real pair?' → label 1")
print(f"    'Is (center, noise_ℓ) a real pair?' → label 0")

# ============================================================
# Part 3: Gradient Direction Comparison
# ============================================================
print("\n" + "=" * 70)
print("Part 3: Gradient Direction Comparison")
print("=" * 70)
print("\n  For the POSITIVE sample term:")
print("  Softmax: ∂L/∂u_o includes (P(c|o) - 1) · v_c")
print("  NS:      ∂L/∂u_o = (σ(u_o^T v_c) - 1) · v_c")
print("  The positive term gradient is IDENTICAL in form!")
print("  The difference: softmax updates ALL other u_w; NS only updates k negatives.")

# ============================================================
# Part 4: Effect of k on Loss Variance
# ============================================================
print("\n" + "=" * 70)
print("Part 4: Effect of k on Loss Variance")
print("=" * 70)

n_trials = 100
k_for_variance = [1, 2, 5, 10, 20, 50]

print(f"\n{'k':>4} | {'Mean Loss':>10} | {'Std Loss':>10} | {'CV (%)':>8}")
print("-" * 42)

means_data = []
stds_data = []
for k in k_for_variance:
    losses = []
    for _ in range(n_trials):
        neg_indices = np.random.choice(VOCAB_SIZE, size=k, replace=False)
        while context_idx in neg_indices:
            neg_indices = np.random.choice(VOCAB_SIZE, size=k, replace=False)
        U_neg = U[neg_indices]
        ns_loss = negative_sampling_loss(v_c, u_o, U_neg, k)
        losses.append(ns_loss)
    m, s = np.mean(losses), np.std(losses)
    cv = (s / m * 100) if m > 0 else 0
    means_data.append(m)
    stds_data.append(s)
    print(f"{k:>4} | {m:>10.4f} | {s:>10.4f} | {cv:>8.2f}")

# ============================================================
# Part 5: Computational Efficiency — gradient computation
# ============================================================
print("\n" + "=" * 70)
print("Part 5: Computational Efficiency (gradient computation)")
print("=" * 70)
print("\n  Softmax gradient: O(|V| × d) — must update ALL output vectors.")
print("  NS gradient: O(k × d) — only k+1 vectors updated.")

n_iterations = 50
vocab_sizes = [1000, 10000, 50000, 100000]
t_softmax_grad = {}
t_ns_grad = {}

for vs in vocab_sizes:
    U_test = np.random.randn(vs, DIM) * 0.1
    
    t_start = time.perf_counter()
    for _ in range(n_iterations):
        scores = U_test @ v_c
        scores_shifted = scores - np.max(scores)
        exp_s = np.exp(scores_shifted)
        Z = np.sum(exp_s)
        probs = exp_s / Z
        grad_all = probs[:, np.newaxis] * v_c
    t_softmax_grad[vs] = (time.perf_counter() - t_start) / n_iterations
    
    k = 5
    t_start = time.perf_counter()
    for _ in range(n_iterations):
        neg_indices = np.random.choice(vs, size=k, replace=False)
        U_neg = U_test[neg_indices]
        u_pos = U_test[context_idx % vs]
        pos_score = np.dot(u_pos, v_c)
        neg_scores = U_neg @ v_c
        sig_pos = sigmoid(pos_score)
        sig_neg = sigmoid(-neg_scores)
        grad_v_c = (sig_pos - 1.0) * u_pos
        for i in range(k):
            grad_v_c += (1.0 - sig_neg[i]) * U_neg[i]
    t_ns_grad[vs] = (time.perf_counter() - t_start) / n_iterations

print(f"\n  {'|V|':>10} | {'Softmax grad':>14} | {'NS grad (k=5)':>14} | {'Speedup':>8}")
print(f"  {'-'*55}")
for vs in vocab_sizes:
    speedup = t_softmax_grad[vs] / t_ns_grad[vs]
    print(f"  {vs:>10} | {t_softmax_grad[vs]*1000:>11.3f} ms | {t_ns_grad[vs]*1000:>11.3f} ms | {speedup:>6.1f}x")

print(f"\n  At |V|=100K: softmax gradient is ~{t_softmax_grad[100000]/t_ns_grad[100000]:.0f}x slower than NS(k=5).")

# ============================================================
# Part 6: Visualization
# ============================================================
print("\n" + "=" * 70)
print("Part 6: Generating Plots")
print("=" * 70)

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(output_dir, exist_ok=True)

# --- Plot 1: Loss comparison across k values ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].errorbar(k_for_variance, means_data, yerr=stds_data, fmt='o-', capsize=4,
                 color='#2196F3', linewidth=2, markersize=8)
axes[0].axhline(y=softmax_loss, color='#F44336', linestyle='--', linewidth=2,
                label=f'Softmax loss = {softmax_loss:.4f}')
axes[0].set_xlabel('Number of negative samples (k)', fontsize=12)
axes[0].set_ylabel('Loss', fontsize=12)
axes[0].set_title('Negative Sampling Loss vs k\n(with ±1 std band over 100 random draws)', fontsize=13)
axes[0].legend(fontsize=11)
axes[0].set_xscale('log')
axes[0].grid(True, alpha=0.3)

# Right: Computational efficiency
vs_eff = vocab_sizes
t_sm_eff = [t_softmax_grad[vs] * 1000 for vs in vs_eff]
t_ns_eff = [t_ns_grad[vs] * 1000 for vs in vs_eff]
x_pos = np.arange(len(vs_eff))
width = 0.35
axes[1].bar(x_pos - width/2, t_sm_eff, width, label='Softmax gradient', color='#F44336', alpha=0.8)
axes[1].bar(x_pos + width/2, t_ns_eff, width, label='NS gradient (k=5)', color='#4CAF50', alpha=0.8)
axes[1].set_xlabel('Vocabulary size |V|', fontsize=12)
axes[1].set_ylabel('Time per gradient step (ms)', fontsize=12)
axes[1].set_title('Gradient Computation: Softmax vs NS\n(scales O(|V|·d) vs O(k·d))', fontsize=13)
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels(['1K', '10K', '50K', '100K'])
axes[1].legend(fontsize=11)
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plot1_path = os.path.join(output_dir, "negative-sampling-loss-comparison.png")
plt.savefig(plot1_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot1_path}")

# --- Plot 2: Sigmoid visualization ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

x = np.linspace(-5, 5, 200)
axes[0].plot(x, sigmoid(x), 'b-', linewidth=2, label='σ(x) = P(real pair | positive)')
axes[0].plot(x, sigmoid(-x), 'r-', linewidth=2, label='σ(-x) = P(not pair | negative)')
axes[0].axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
axes[0].axvline(x=0.0, color='gray', linestyle=':', alpha=0.5)
axes[0].set_xlabel('Score (u^T v)', fontsize=12)
axes[0].set_ylabel('σ(score)', fontsize=12)
axes[0].set_title('Negative Sampling: Two Logistic Classifications\n' +
                  r'$J = -\log\,\sigma(u_o^\top v_c) - \sum_{\ell=1}^{k}\log\,\sigma(-u_\ell^\top v_c)$', fontsize=12)
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3)
axes[0].annotate('Want σ → 1\n(high score)', xy=(3, 0.95), fontsize=10,
                ha='center', color='blue', alpha=0.7)
axes[0].annotate('Want σ(-x) → 1\n(low/neg score)', xy=(-3, 0.95), fontsize=10,
                ha='center', color='red', alpha=0.7)

score_range = np.linspace(-4, 4, 100)
grad_positive = 1 - sigmoid(score_range)
grad_negative = 1 - sigmoid(-score_range)
axes[1].plot(score_range, grad_positive, 'b-', linewidth=2,
             label='Positive: 1 - σ(u_o^T v_c)\n(push u_o toward v_c)')
axes[1].plot(score_range, grad_negative, 'r-', linewidth=2,
             label='Negative: 1 - σ(-u_ℓ^T v_c)\n(push u_ℓ away from v_c)')
axes[1].set_xlabel('Score (u^T v)', fontsize=12)
axes[1].set_ylabel('Gradient magnitude', fontsize=12)
axes[1].set_title('Gradient Strength: When Does Each Sample Push Hard?', fontsize=12)
axes[1].legend(fontsize=9)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plot2_path = os.path.join(output_dir, "negative-sampling-loss-sigmoid-gradients.png")
plt.savefig(plot2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot2_path}")

# --- Plot 3: Loss landscape ---
fig, ax = plt.subplots(figsize=(10, 6))

dot_products_range = np.linspace(-2, 2, 100)
softmax_losses_list = []
ns_losses_k5_list = []
ns_losses_k1_list = []

for dot_val in dot_products_range:
    u_scaled = v_c * dot_val / (np.dot(v_c, v_c) + 1e-10)
    
    scores_scaled = U @ u_scaled
    scores_shifted = scores_scaled - np.max(scores_scaled)
    exp_s = np.exp(scores_shifted)
    probs = exp_s / np.sum(exp_s)
    cos_sim = U @ u_scaled / (np.linalg.norm(U, axis=1) * np.linalg.norm(u_scaled) + 1e-10)
    best_idx = np.argmax(cos_sim)
    softmax_losses_list.append(-np.log(probs[best_idx] + 1e-10))
    
    neg_idx = np.random.choice(VOCAB_SIZE, size=5, replace=False)
    ns_losses_k5_list.append(negative_sampling_loss(u_scaled, U[best_idx], U[neg_idx], 5))
    
    neg_idx_1 = np.random.choice(VOCAB_SIZE, size=1, replace=False)
    ns_losses_k1_list.append(negative_sampling_loss(u_scaled, U[best_idx], U[neg_idx_1], 1))

ax.plot(dot_products_range, softmax_losses_list, 'r-', linewidth=2.5, label='Softmax loss')
ax.plot(dot_products_range, ns_losses_k5_list, 'b-', linewidth=2, label='NS loss (k=5)')
ax.plot(dot_products_range, ns_losses_k1_list, 'g--', linewidth=1.5, label='NS loss (k=1)')
ax.set_xlabel('u_o^T v_c (dot product)', fontsize=12)
ax.set_ylabel('Loss', fontsize=12)
ax.set_title('Loss Landscape: How Loss Changes with Vector Similarity\n' +
             'Both objectives decrease as positive pair similarity increases', fontsize=13)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plot3_path = os.path.join(output_dir, "negative-sampling-loss-landscape.png")
plt.savefig(plot3_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot3_path}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print(f"""
1. Full softmax loss = {softmax_loss:.6f}
   - Requires computing exp() for ALL {VOCAB_SIZE} words
   - Partition function Z = {partition_function:.6f}

2. Negative sampling loss (k=5):
   - Only needs k+1 = 6 dot products
   - Loss = binary classification: real pair vs noise

3. Gradient speedup at |V|=100K: softmax {t_softmax_grad[100000]*1000:.3f}ms vs NS(k=5) {t_ns_grad[100000]*1000:.3f}ms
   = {t_softmax_grad[100000]/t_ns_grad[100000]:.1f}x faster per gradient step

4. Why logistic approximation works:
   - Positive sample gradient has SAME form: (σ(score) - 1) · v_c
   - Negative samples push noise away: (1 - σ(-score)) · u_ℓ
   - "If we randomly push down a few words at each step,
     on average, things will work out." — Notes §3.5

5. Practical k: Mikolov et al. (2013) recommend k=5-20
""")

print(f"Output files:")
print(f"  - {plot1_path}")
print(f"  - {plot2_path}")
print(f"  - {plot3_path}")
