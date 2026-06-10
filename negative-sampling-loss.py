#!/usr/bin/env python3
"""
CS224N L01 Word Vectors — Code Capsule: negative-sampling-loss (WP05)
======================================================================
Concept: 负采样目标函数 vs 全 softmax
Official anchor: Notes §3.5 (Eq.14-15, SGNS objective); R02 paper Section 3

Why this capsule matters:
  Notes §3.5 gives the SGNS formula (Eq.15) but doesn't explain WHY
  the logistic approximation is effective. This script demonstrates:
  1. Softmax loss requires summing over ALL vocabulary words (partition function)
  2. Negative sampling loss only needs k+1 terms (1 positive + k negative)
  3. Both losses push the model in the same direction on average
  4. Different k values trade off accuracy vs efficiency

Formulas (from Notes §3.5):
  Eq.14 (softmax):  P(o|c) = exp(u_o^T v_c) / Σ_w exp(u_w^T v_c)
  Eq.15 (SGNS):     L = log σ(u_o^T v_c) + Σ_{ℓ=1}^{k} log σ(-u_ℓ^T v_c)
"""

import numpy as np
import time
import json
import os

np.random.seed(42)

# ============================================================
# 1. Setup: Mini vocabulary with toy word vectors
# ============================================================
print("=" * 70)
print("CS224N L01 Code Capsule: negative-sampling-loss (WP05)")
print("=" * 70)

VOCAB = ["king", "queen", "man", "woman", "prince", "princess",
         "dog", "cat", "fish", "bird", "car", "tree"]
VOCAB_SIZE = len(VOCAB)
DIM = 4  # toy dimension for clarity

# Center word vectors (v_c) and context word vectors (u_o)
# Initialize small random values (typical word2vec init)
V_center = np.random.randn(VOCAB_SIZE, DIM) * 0.1
U_context = np.random.randn(VOCAB_SIZE, DIM) * 0.1

# Pick a (center, context) pair: "king" -> "queen" (semantically related)
center_idx = VOCAB.index("king")
context_idx = VOCAB.index("queen")

print(f"\n[Setup]")
print(f"  Vocabulary size |V| = {VOCAB_SIZE}")
print(f"  Vector dimension d = {DIM}")
print(f"  Center word: '{VOCAB[center_idx]}' (idx={center_idx})")
print(f"  Context word: '{VOCAB[context_idx]}' (idx={context_idx})")
print(f"  v_center shape: {V_center.shape}")
print(f"  U_context shape: {U_context.shape}")

# ============================================================
# 2. Softmax Loss (Eq.14 from Notes §3.5)
# ============================================================
print(f"\n{'=' * 70}")
print("[Part 1] Softmax Loss — requires partition function over ALL words")
print(f"{'=' * 70}")

v_c = V_center[center_idx]  # center word vector

# Compute scores for ALL words: u_w^T v_c for all w
scores_all = U_context @ v_c  # shape: (VOCAB_SIZE,)
print(f"\n  Scores u_w^T v_c for all w in V:")
for i, w in enumerate(VOCAB):
    marker = " <-- positive pair (king, queen)" if i == context_idx else ""
    print(f"    {w:>8s}: {scores_all[i]:+.4f}{marker}")

# Softmax probabilities (Eq.14)
# P(o|c) = exp(u_o^T v_c) / Σ_w exp(u_w^T v_c)
exp_scores = np.exp(scores_all - np.max(scores_all))  # numerical stability
probs = exp_scores / exp_scores.sum()

print(f"\n  Softmax probabilities P(o|c) = exp(u_o^T v_c) / Z:")
for i, w in enumerate(VOCAB):
    marker = " <-- P(queen|king)" if i == context_idx else ""
    print(f"    P({w:>8s}|king) = {probs[i]:.6f}{marker}")

# Cross-entropy loss = -log P(o|c)
softmax_loss = -np.log(probs[context_idx])
print(f"\n  Softmax loss = -log P(queen|king) = -log({probs[context_idx]:.6f}) = {softmax_loss:.6f}")
print(f"  Partition function Z = Σ_w exp(u_w^T v_c) = {exp_scores.sum():.6f}")
print(f"  Terms computed: {VOCAB_SIZE} (ALL vocabulary words)")

# ============================================================
# 3. Negative Sampling Loss (Eq.15 from Notes §3.5)
# ============================================================
print(f"\n{'=' * 70}")
print("[Part 2] Negative Sampling Loss — only k+1 terms needed")
print(f"{'=' * 70}")

def sigmoid(x):
    """Numerically stable sigmoid."""
    return np.where(x >= 0,
                    1 / (1 + np.exp(-x)),
                    np.exp(x) / (1 + np.exp(x)))

def negative_sampling_loss(v_c, u_positive, u_negatives):
    """
    Eq.15: L_NS = log σ(u_o^T v_c) + Σ_{ℓ=1}^{k} log σ(-u_ℓ^T v_c)
    
    We want to MAXIMIZE this, so the loss for gradient descent is -L_NS.
    """
    # Positive term: log σ(u_o^T v_c)
    pos_score = u_positive @ v_c
    pos_term = np.log(sigmoid(pos_score))
    
    # Negative terms: Σ log σ(-u_ℓ^T v_c)
    neg_scores = u_negatives @ v_c  # shape: (k,)
    neg_terms = np.log(sigmoid(-neg_scores))
    
    total = pos_term + neg_terms.sum()
    return total, pos_term, neg_terms

# Try different k values
K_VALUES = [2, 5, 10, 20]

for k in K_VALUES:
    # Sample k negative words (excluding the positive context word)
    # Use replace=True if k > available negatives (toy vocab may be small)
    available_negs = [i for i in range(VOCAB_SIZE) if i != context_idx]
    actual_k = min(k, len(available_negs))
    use_replace = k > len(available_negs)
    neg_indices = np.random.choice(
        available_negs,
        size=actual_k, replace=use_replace
    )
    u_positive = U_context[context_idx]
    u_negatives = U_context[neg_indices]
    
    ns_loss, pos_term, neg_terms = negative_sampling_loss(v_c, u_positive, u_negatives)
    
    print(f"\n  k = {k}:")
    print(f"    Positive term: log σ(u_queen^T v_king) = log σ({u_positive @ v_c:+.4f}) = {pos_term:.6f}")
    print(f"    Negative terms ({k} sampled):")
    for j, neg_idx in enumerate(neg_indices):
        print(f"      log σ(-u_{VOCAB[neg_idx]:>8s}^T v_king) = log σ({-(u_negatives[j] @ v_c):+.4f}) = {neg_terms[j]:+.6f}")
    print(f"    NS objective = {ns_loss:.6f}")
    print(f"    NS loss (for minimization) = {-ns_loss:.6f}")
    print(f"    Terms computed: {k + 1} (1 positive + {k} negative)")

# ============================================================
# 4. Direct comparison: Softmax vs NS (same k=5)
# ============================================================
print(f"\n{'=' * 70}")
print("[Part 3] Direct comparison — same (king, queen) pair")
print(f"{'=' * 70}")

k_compare = 5
np.random.seed(123)  # reproducible negative samples
neg_indices_cmp = np.random.choice(
    [i for i in range(VOCAB_SIZE) if i != context_idx],
    size=k_compare, replace=False
)
u_pos_cmp = U_context[context_idx]
u_neg_cmp = U_context[neg_indices_cmp]

ns_val, pos_t, neg_ts = negative_sampling_loss(v_c, u_pos_cmp, u_neg_cmp)

print(f"\n  Softmax loss:  {softmax_loss:.6f}  (uses all {VOCAB_SIZE} words)")
print(f"  NS loss (k={k_compare}): {-ns_val:.6f}  (uses {k_compare+1} words)")
print(f"\n  Key insight: NS loss is NOT the same value as softmax loss.")
print(f"  But both gradients push v_king toward u_queen and away from negatives.")
print(f"  On average over many steps, NS approximates the softmax gradient.")

# ============================================================
# 5. Gradient comparison
# ============================================================
print(f"\n{'=' * 70}")
print("[Part 4] Gradient comparison — direction of update to v_c")
print(f"{'=' * 70}")

# Softmax gradient: ∂L/∂v_c = Σ_w P(w|c) * u_w - u_o  (Notes §3.4 Eq.13)
# This is "expected minus observed" (or "observed minus expected" for -∂L)
softmax_grad = probs @ U_context - u_pos_cmp
print(f"\n  Softmax gradient ∂L/∂v_c (observed - expected):")
print(f"    = u_queen - Σ_w P(w|king) * u_w")
print(f"    = {softmax_grad}")
print(f"    norm = {np.linalg.norm(softmax_grad):.6f}")

# NS gradient: ∂L_NS/∂v_c = (σ(-u_o^T v_c) - 1) * u_o + Σ_ℓ σ(u_ℓ^T v_c) * u_ℓ
# Wait, let's be careful. We want gradient of the NEGATIVE objective (loss to minimize).
# L = -log σ(u_o^T v_c) - Σ log σ(-u_ℓ^T v_c)
# ∂L/∂v_c = -(1 - σ(u_o^T v_c)) * u_o + Σ_ℓ (1 - σ(-u_ℓ^T v_c)) * (-u_ℓ)
#          = -(1 - σ(pos)) * u_o + Σ (σ(neg_score)) * (-u_ℓ)
# Wait, let me redo this more carefully.

# Loss to minimize: J = -[log σ(u_o^T v_c) + Σ log σ(-u_ℓ^T v_c)]
# ∂J/∂v_c = -(1 - σ(u_o^T v_c)) * u_o  -  Σ (1 - σ(-u_ℓ^T v_c)) * (-u_ℓ)
#          = -(1 - σ(pos_score)) * u_o  +  Σ (1 - σ(-neg_score_j)) * u_neg_j
# Hmm, let me be more careful with the chain rule.

# For positive term: -log σ(u_o^T v_c)
# ∂/∂v_c = -(1/σ(u_o^T v_c)) * σ(u_o^T v_c) * (1 - σ(u_o^T v_c)) * u_o
#         = -(1 - σ(u_o^T v_c)) * u_o
#         = (σ(u_o^T v_c) - 1) * u_o

# For negative term: -log σ(-u_ℓ^T v_c)
# ∂/∂v_c = -(1/σ(-u_ℓ^T v_c)) * σ(-u_ℓ^T v_c) * (1 - σ(-u_ℓ^T v_c)) * (-u_ℓ)
#         = (1 - σ(-u_ℓ^T v_c)) * u_ℓ
#         = σ(u_ℓ^T v_c) * u_ℓ

pos_score_val = u_pos_cmp @ v_c
neg_scores_val = u_neg_cmp @ v_c

ns_grad = (sigmoid(pos_score_val) - 1) * u_pos_cmp
for j in range(k_compare):
    ns_grad += sigmoid(neg_scores_val[j]) * u_neg_cmp[j]

print(f"\n  NS gradient ∂J/∂v_c (k={k_compare}):")
print(f"    = (σ(u_queen^T v_king) - 1) * u_queen + Σ σ(u_neg^T v_king) * u_neg")
print(f"    = {ns_grad}")
print(f"    norm = {np.linalg.norm(ns_grad):.6f}")

# Cosine similarity between gradients
cos_sim = np.dot(softmax_grad, ns_grad) / (np.linalg.norm(softmax_grad) * np.linalg.norm(ns_grad))
print(f"\n  Cosine similarity between softmax grad and NS grad: {cos_sim:.4f}")
print(f"  (Not identical — but both point roughly in the 'toward queen, away from negatives' direction)")

# ============================================================
# 6. Efficiency comparison: computation time
# ============================================================
print(f"\n{'=' * 70}")
print("[Part 5] Efficiency — computation time scaling")
print(f"{'=' * 70}")

# Simulate larger vocabularies
VOCAB_SIZES = [100, 1000, 10000, 50000, 100000]
DIM_EFF = 300  # realistic dimension
N_TRIALS = 50

print(f"\n  Dimension d = {DIM_EFF}, trials per size = {N_TRIALS}")
print(f"  {'|V|':>10s} | {'Softmax (ms)':>14s} | {'NS k=5 (ms)':>14s} | {'Speedup':>10s}")
print(f"  {'-'*10} | {'-'*14} | {'-'*14} | {'-'*10}")

efficiency_results = []
for vs in VOCAB_SIZES:
    V_big = np.random.randn(vs, DIM_EFF) * 0.1
    v_c_big = np.random.randn(DIM_EFF) * 0.1
    neg_big = np.random.choice(vs, size=5, replace=False)
    
    # Softmax: compute all scores
    t0 = time.perf_counter()
    for _ in range(N_TRIALS):
        scores = V_big @ v_c_big
        scores -= scores.max()
        exp_s = np.exp(scores)
        prob = exp_s / exp_s.sum()
        loss = -np.log(prob[0])
    t_softmax = (time.perf_counter() - t0) / N_TRIALS * 1000  # ms
    
    # NS k=5: compute only 6 scores
    t0 = time.perf_counter()
    for _ in range(N_TRIALS):
        pos_s = V_big[0] @ v_c_big
        neg_s = V_big[neg_big] @ v_c_big
        loss_ns = np.log(sigmoid(pos_s)) + np.log(sigmoid(-neg_s)).sum()
    t_ns = (time.perf_counter() - t0) / N_TRIALS * 1000  # ms
    
    speedup = t_softmax / t_ns if t_ns > 0 else float('inf')
    print(f"  {vs:>10,d} | {t_softmax:>14.4f} | {t_ns:>14.4f} | {speedup:>10.1f}x")
    efficiency_results.append({
        "vocab_size": vs,
        "softmax_ms": round(t_softmax, 6),
        "ns_k5_ms": round(t_ns, 6),
        "speedup": round(speedup, 1)
    })

# ============================================================
# 7. Effect of k on NS loss stability
# ============================================================
print(f"\n{'=' * 70}")
print("[Part 6] Effect of k on NS objective variance")
print(f"{'=' * 70}")

K_RANGE = [1, 2, 5, 10, 20, 50]
N_SAMPLES = 100  # number of random negative sample sets per k

print(f"\n  For each k, compute NS objective {N_SAMPLES} times with different negative samples.")
print(f"  {'k':>5s} | {'Mean':>10s} | {'Std':>10s} | {'Min':>10s} | {'Max':>10s}")
print(f"  {'-'*5} | {'-'*10} | {'-'*10} | {'-'*10} | {'-'*10}")

k_effect_results = []
for k in K_RANGE:
    objectives = []
    for _ in range(N_SAMPLES):
        available_negs_k = [i for i in range(VOCAB_SIZE) if i != context_idx]
        actual_k_k = min(k, len(available_negs_k))
        use_replace_k = k > len(available_negs_k)
        neg_idx = np.random.choice(
            available_negs_k,
            size=actual_k_k, replace=use_replace_k
        )
        val, _, _ = negative_sampling_loss(v_c, u_pos_cmp, U_context[neg_idx])
        objectives.append(val)
    objectives = np.array(objectives)
    print(f"  {k:>5d} | {objectives.mean():>+10.4f} | {objectives.std():>10.4f} | {objectives.min():>+10.4f} | {objectives.max():>+10.4f}")
    k_effect_results.append({
        "k": k,
        "mean": round(float(objectives.mean()), 4),
        "std": round(float(objectives.std()), 4),
        "min": round(float(objectives.min()), 4),
        "max": round(float(objectives.max()), 4)
    })

# ============================================================
# 8. Visualization
# ============================================================
print(f"\n{'=' * 70}")
print("[Part 7] Generating plots")
print(f"{'=' * 70}")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

output_dir = "Labs/L01-word-vectors/outputs"
os.makedirs(output_dir, exist_ok=True)

# Plot 1: Softmax probabilities bar chart
fig, ax = plt.subplots(figsize=(10, 5))
colors = ['#e74c3c' if i == context_idx else '#3498db' for i in range(VOCAB_SIZE)]
bars = ax.bar(range(VOCAB_SIZE), probs, color=colors, edgecolor='black', linewidth=0.5)
ax.set_xticks(range(VOCAB_SIZE))
ax.set_xticklabels(VOCAB, rotation=45, ha='right', fontsize=9)
ax.set_ylabel('P(o | king)', fontsize=12)
ax.set_title('Softmax Probabilities P(o | center="king")\nEq.14: P(o|c) = exp(u_oᵀv_c) / Σ_w exp(u_wᵀv_c)', fontsize=13)
ax.axhline(y=1/VOCAB_SIZE, color='gray', linestyle='--', alpha=0.5, label=f'Uniform (1/|V|={1/VOCAB_SIZE:.4f})')
ax.legend(fontsize=9)
# Annotate the positive pair
ax.annotate(f'P(queen|king)={probs[context_idx]:.4f}',
            xy=(context_idx, probs[context_idx]),
            xytext=(context_idx + 1.5, probs[context_idx] + 0.05),
            arrowprops=dict(arrowstyle='->', color='red'),
            fontsize=10, color='red', fontweight='bold')
plt.tight_layout()
plot1_path = os.path.join(output_dir, "negative-sampling-loss-softmax-probs.png")
fig.savefig(plot1_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot1_path}")

# Plot 2: Efficiency scaling (log-log)
fig, ax = plt.subplots(figsize=(8, 5))
vs_list = [r["vocab_size"] for r in efficiency_results]
sm_list = [r["softmax_ms"] for r in efficiency_results]
ns_list = [r["ns_k5_ms"] for r in efficiency_results]
ax.loglog(vs_list, sm_list, 'o-', label='Softmax (all |V|)', color='#e74c3c', linewidth=2, markersize=8)
ax.loglog(vs_list, ns_list, 's-', label='NS k=5 (constant)', color='#2ecc71', linewidth=2, markersize=8)
ax.set_xlabel('Vocabulary size |V|', fontsize=12)
ax.set_ylabel('Time per step (ms)', fontsize=12)
ax.set_title('Computation Time: Softmax vs Negative Sampling (k=5)\nSoftmax scales O(|V|); NS scales O(k) — independent of |V|', fontsize=13)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
# Annotate speedups
for r in efficiency_results:
    if r["vocab_size"] in [1000, 100000]:
        ax.annotate(f'{r["speedup"]:.0f}x', xy=(r["vocab_size"], r["softmax_ms"]),
                    xytext=(r["vocab_size"]*1.5, r["softmax_ms"]*0.5),
                    arrowprops=dict(arrowstyle='->', color='gray'),
                    fontsize=9, color='gray')
plt.tight_layout()
plot2_path = os.path.join(output_dir, "negative-sampling-loss-efficiency-scaling.png")
fig.savefig(plot2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot2_path}")

# Plot 3: k effect on NS objective
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left: mean ± std
ks = [r["k"] for r in k_effect_results]
means = [r["mean"] for r in k_effect_results]
stds = [r["std"] for r in k_effect_results]
axes[0].errorbar(ks, means, yerr=stds, fmt='o-', capsize=5, color='#2980b9', linewidth=2, markersize=8)
axes[0].set_xlabel('Number of negative samples k', fontsize=12)
axes[0].set_ylabel('NS objective value', fontsize=12)
axes[0].set_title('Mean NS Objective ± Std\n(more k → more stable estimate)', fontsize=12)
axes[0].grid(True, alpha=0.3)

# Right: std vs k
axes[1].plot(ks, stds, 'D-', color='#e67e22', linewidth=2, markersize=8)
axes[1].set_xlabel('Number of negative samples k', fontsize=12)
axes[1].set_ylabel('Standard deviation', fontsize=12)
axes[1].set_title('Variance of NS Objective vs k\n(larger k → lower variance → more stable gradient)', fontsize=12)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plot3_path = os.path.join(output_dir, "negative-sampling-loss-k-effect.png")
fig.savefig(plot3_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot3_path}")

# Plot 4: Gradient comparison visualization
fig, ax = plt.subplots(figsize=(8, 6))
# Project gradients to 2D for visualization (use first 2 dims)
grad_types = {
    'Softmax grad': softmax_grad[:2],
    f'NS grad (k={k_compare})': ns_grad[:2],
}
colors_grad = {'Softmax grad': '#e74c3c', f'NS grad (k={k_compare})': '#2ecc71'}
for label, vec in grad_types.items():
    ax.annotate('', xy=vec, xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=colors_grad[label], lw=2.5))
    ax.text(vec[0]*1.15, vec[1]*1.15, label, fontsize=11, color=colors_grad[label], fontweight='bold')

ax.axhline(y=0, color='gray', linewidth=0.5)
ax.axvline(x=0, color='gray', linewidth=0.5)
ax.set_xlabel('Gradient dimension 0', fontsize=12)
ax.set_ylabel('Gradient dimension 1', fontsize=12)
ax.set_title(f'Gradient Direction Comparison (first 2 dims)\ncosine similarity = {cos_sim:.4f}', fontsize=13)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plot4_path = os.path.join(output_dir, "negative-sampling-loss-gradient-comparison.png")
fig.savefig(plot4_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {plot4_path}")

# ============================================================
# 9. Summary
# ============================================================
print(f"\n{'=' * 70}")
print("[Summary]")
print(f"{'=' * 70}")
print(f"""
  1. Softmax loss needs ALL |V|={VOCAB_SIZE} words for partition function Z.
     For real vocab (|V|=50,000+), this is prohibitively expensive.

  2. Negative sampling (Eq.15) replaces Z with k negative samples:
     L_NS = log σ(u_oᵀv_c) + Σ_{{ℓ=1}}^{{k}} log σ(-u_ℓᵀv_c)
     Only k+1 terms needed — independent of |V|.

  3. At |V|=100,000, softmax is ~{efficiency_results[-1]['speedup']:.0f}x slower than NS (k=5).

  4. Larger k → lower variance in gradient estimate, but diminishing returns.
     Typical choices: k=5-20 for large vocabularies (R02 paper recommends k=5-20).

  5. NS gradient and softmax gradient are NOT identical, but point in
     similar directions (cosine sim = {cos_sim:.4f} in this example).
     On average over many training steps, NS approximates softmax well.

  Key takeaway: Negative sampling trades exact normalization for
  massive efficiency, while preserving the essential learning signal.
""")

# Save structured output for provenance
output_data = {
    "softmax_loss": round(float(softmax_loss), 6),
    "softmax_prob_queen_king": round(float(probs[context_idx]), 6),
    "partition_function_Z": round(float(exp_scores.sum()), 6),
    "vocab_size": VOCAB_SIZE,
    "dim": DIM,
    "gradient_cosine_similarity": round(float(cos_sim), 4),
    "efficiency": efficiency_results,
    "k_effect": k_effect_results,
    "plots": [plot1_path, plot2_path, plot3_path, plot4_path]
}

json_path = os.path.join(output_dir, "negative-sampling-loss-summary.json")
with open(json_path, 'w') as f:
    json.dump(output_data, f, indent=2)
print(f"  Saved structured output: {json_path}")
print(f"\nDone.")
