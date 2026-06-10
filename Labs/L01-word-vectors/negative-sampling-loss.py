#!/usr/bin/env python3
"""
<<<<<<< HEAD
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
=======
CS224N L01 Code Capsule: negative-sampling-loss
================================================
概念：负采样目标函数 vs 全 softmax（WP05 / Notes §3.5 Eq.14-15）

这段代码在看什么：
  1. 全 softmax 损失：对一个 (center, outside) 对，分母要遍历整个词表 → O(|V|)
  2. 负采样（SGNS）损失：只采样 k 个负样本，用 logistic 回归近似 → O(k)
  3. 对比两种损失的数值、梯度方向

运行后先看哪里：
  - 第一部分输出：全 softmax 概率分布 → 看分母有多大
  - 第二部分输出：SGNS 各项 logistic loss → 看正样本拉高、负样本压低
  - 第三部分输出：计算量对比表 → O(|V|) vs O(k)
  - 图表：梯度方向示意图（正样本靠近、负样本远离）

和本讲哪个 waypoint 对应：WP04-WP05（Objective / Gradients / Negative Sampling）

容易误解的地方：
  - 负采样不是 softmax 的"近似"那么简单——它把多分类问题变成了 k+1 个二分类问题
  - sigma(x) = 1/(1+exp(-x))，不是 softmax
  - 负样本是从噪声分布 P_n(w) 采样，不是均匀分布（实践中常用 unigram^0.75）
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
>>>>>>> cf728cf (Add negative-sampling-loss capsule (WP05))
import json
import os

np.random.seed(42)

# ============================================================
<<<<<<< HEAD
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
=======
# 设置：toy 词表和向量
# ============================================================
VOCAB = ["cat", "dog", "fish", "bird", "car", "tree", "house", "river",
         "king", "queen", "man", "woman", "run", "walk", "jump", "swim",
         "big", "small", "hot", "cold"]
V = len(VOCAB)  # 词表大小 = 20
D = 4           # 向量维度（toy）

# 随机初始化 center 和 context 向量（实际训练中这些是学出来的）
v_vectors = np.random.randn(V, D) * 0.5  # center vectors v_w
u_vectors = np.random.randn(V, D) * 0.5  # context vectors u_w

# 选一个 center word 和一个正样本 outside word
center_idx = 0   # "cat"
pos_idx = 1      # "dog"（假设是 context 中的词）

v_c = v_vectors[center_idx]  # center 向量
u_o = u_vectors[pos_idx]     # 正样本 context 向量

print("=" * 60)
print("CS224N L01 Code Capsule: negative-sampling-loss")
print("=" * 60)
print(f"\n词表大小 |V| = {V}")
print(f"向量维度 d = {D}")
print(f"Center word: '{VOCAB[center_idx]}'")
print(f"Positive context word: '{VOCAB[pos_idx]}'")

# ============================================================
# Part 1: 全 softmax 损失计算
# ============================================================
print("\n" + "=" * 60)
print("Part 1: 全 Softmax 损失")
print("=" * 60)
print("\n公式: P(o|c) = exp(u_o^T v_c) / sum_w exp(u_w^T v_c)")
print("问题: 分母要算 |V| 个 exp，当 |V|=100000 时非常慢\n")

# 计算所有词与 center 的点积
scores = u_vectors @ v_c  # shape: (V,)
print(f"所有词与 '{VOCAB[center_idx]}' 的点积 (u_w^T v_c):")
for i, (word, score) in enumerate(zip(VOCAB, scores)):
    marker = " <-- positive" if i == pos_idx else ""
    print(f"  {word:>8s}: {score:+.4f}{marker}")

# softmax 概率
exp_scores = np.exp(scores - np.max(scores))  # 数值稳定
probs = exp_scores / exp_scores.sum()

print(f"\nSoftmax 概率 P(o|c):")
for i, (word, p) in enumerate(zip(VOCAB, probs)):
    marker = " <-- positive" if i == pos_idx else ""
    print(f"  {word:>8s}: {p:.6f}{marker}")

# 全 softmax 交叉熵损失: J = -log P(o|c)
full_softmax_loss = -np.log(probs[pos_idx] + 1e-10)
print(f"\n全 softmax 损失 J_full = -log P('{VOCAB[pos_idx]}'|'{VOCAB[center_idx]}') = {full_softmax_loss:.4f}")
print(f"计算复杂度: O(|V|) = O({V}) 次点积 + exp + 求和")

# ============================================================
# Part 2: 负采样（SGNS）损失计算
# ============================================================
print("\n" + "=" * 60)
print("Part 2: 负采样（SGNS）损失")
print("=" * 60)
print("\n公式: J_sgns = -log sigma(u_o^T v_c) - sum_{i=1}^{k} log sigma(-u_{w_i}^T v_c)")
print("sigma(x) = 1 / (1 + exp(-x))  ← 这是 logistic/sigmoid，不是 softmax")
print("只需要 k 个负样本，不需要遍历整个词表\n")

K = 5  # 负样本数量

# 从噪声分布采样负样本（实践中用 unigram^0.75，这里简化为均匀）
# 排除正样本
neg_candidates = [i for i in range(V) if i != pos_idx]
neg_indices = np.random.choice(neg_candidates, size=K, replace=False)

print(f"采样 {K} 个负样本:")
for i, neg_idx in enumerate(neg_indices):
    print(f"  负样本 {i+1}: '{VOCAB[neg_idx]}'")

# 正样本的 logistic loss: -log sigma(u_o^T v_c)
pos_dot = u_o @ v_c
sigma_pos = 1.0 / (1.0 + np.exp(-pos_dot))
loss_pos = -np.log(sigma_pos + 1e-10)

print(f"\n正样本 '{VOCAB[pos_idx]}':")
print(f"  u_o^T v_c = {pos_dot:+.4f}")
print(f"  sigma(u_o^T v_c) = {sigma_pos:.4f}")
print(f"  -log sigma(u_o^T v_c) = {loss_pos:.4f}")

# 负样本的 logistic loss: -log sigma(-u_{w_i}^T v_c)
print(f"\n负样本各项:")
neg_losses = []
for i, neg_idx in enumerate(neg_indices):
    u_neg = u_vectors[neg_idx]
    neg_dot = u_neg @ v_c
    sigma_neg = 1.0 / (1.0 + np.exp(-(-neg_dot)))  # sigma(-u_w^T v_c)
    loss_neg = -np.log(sigma_neg + 1e-10)
    neg_losses.append(loss_neg)
    print(f"  负样本 {i+1} '{VOCAB[neg_idx]}':")
    print(f"    u_w^T v_c = {neg_dot:+.4f}")
    print(f"    sigma(-u_w^T v_c) = {sigma_neg:.4f}")
    print(f"    -log sigma(-u_w^T v_c) = {loss_neg:.4f}")

total_sgns_loss = loss_pos + sum(neg_losses)
print(f"\nSGNS 总损失 J_sgns = {loss_pos:.4f} + {' + '.join(f'{l:.4f}' for l in neg_losses)} = {total_sgns_loss:.4f}")
print(f"计算复杂度: O(k) = O({K}) 次点积 + exp")

# ============================================================
# Part 3: 计算量对比
# ============================================================
print("\n" + "=" * 60)
print("Part 3: 计算量对比")
print("=" * 60)

print(f"\n{'方法':<20s} {'每对计算量':<15s} {'|V|=10000 时':<20s} {'|V|=100000 时':<20s}")
print("-" * 75)
print(f"{'Full Softmax':<20s} {'O(|V|)':<15s} {'~10,000 ops':<20s} {'~100,000 ops':<20s}")
print(f"{'SGNS (k=' + str(K) + ')':<20s} {'O(k)':<15s} {f'~{K} ops':<20s} {f'~{K} ops':<20s}")
print(f"\n加速比 (|V|=100000, k={K}): ~{100000//K}x")

# ============================================================
# Part 4: 梯度方向示意
# ============================================================
print("\n" + "=" * 60)
print("Part 4: 梯度方向（正样本靠近，负样本远离）")
print("=" * 60)

# 简化 2D 可视化
# 梯度: dJ/d(v_c) for positive = -(1 - sigma(u_o^T v_c)) * u_o  → 把 v_c 推向 u_o
# 梯度: dJ/d(v_c) for negative_i = -(sigma(-u_{w_i}^T v_c) - 1) * (-u_{w_i})
#        = (1 - sigma(-u_{w_i}^T v_c)) * u_{w_i}  → 把 v_c 推离 u_{w_i}

# 用 2D 向量做示意
np.random.seed(123)
v_2d = np.array([0.0, 0.0])  # center vector
u_pos_2d = np.array([2.0, 1.5])  # positive context
u_neg_2ds = [
    np.array([-1.5, 2.0]),
    np.array([1.0, -2.0]),
    np.array([-2.0, -1.0]),
]
neg_words_2d = ["car", "tree", "king"]

# 计算梯度
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

# 正样本梯度贡献: -(1 - sigma(u_o . v)) * u_o
dot_pos = np.dot(u_pos_2d, v_2d)
grad_pos = -(1 - sigmoid(dot_pos)) * u_pos_2d

# 负样本梯度贡献: (1 - sigma(-u_w . v)) * u_w
grad_negs = []
for u_neg in u_neg_2ds:
    dot_neg = np.dot(u_neg, v_2d)
    grad_neg = (1 - sigmoid(-dot_neg)) * u_neg
    grad_negs.append(grad_neg)

# 总梯度
grad_total = grad_pos + sum(grad_negs)

print(f"\nCenter vector v_c = [{v_2d[0]:.1f}, {v_2d[1]:.1f}]")
print(f"正样本 u_o = [{u_pos_2d[0]:.1f}, {u_pos_2d[1]:.1f}]")
for i, (u_neg, word) in enumerate(zip(u_neg_2ds, neg_words_2d)):
    print(f"负样本 u_{word} = [{u_neg[0]:.1f}, {u_neg[1]:.1f}]")

print(f"\n梯度贡献:")
print(f"  正样本方向 (拉近 v_c → u_o): [{grad_pos[0]:+.3f}, {grad_pos[1]:+.3f}]")
for i, (grad_neg, word) in enumerate(zip(grad_negs, neg_words_2d)):
    print(f"  负样本 '{word}' 方向 (推离 v_c ← u_w): [{grad_neg[0]:+.3f}, {grad_neg[1]:+.3f}]")
print(f"  总梯度方向: [{grad_total[0]:+.3f}, {grad_total[1]:+.3f}]")
print(f"\n结论: 正样本梯度把 v_c 拉向 u_o，负样本梯度把 v_c 推离各 u_w")
print("这就是为什么 SGNS 能学到有意义的词向量——语义相近的词共享 context，")
print("被拉近；语义远的词被推远。")

# ============================================================
# 画图
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# --- 图1: 梯度方向示意图 ---
ax1 = axes[0]
ax1.set_xlim(-3.5, 3.5)
ax1.set_ylim(-3.5, 3.5)
ax1.set_aspect('equal')
ax1.grid(True, alpha=0.3)
ax1.set_title("Gradient Direction in SGNS\n(正样本拉近, 负样本推远)", fontsize=12)

# 画 center vector
ax1.plot(v_2d[0], v_2d[1], 'ko', markersize=10, zorder=5)
ax1.annotate('v_c (center)', (v_2d[0], v_2d[1]),
             textcoords="offset points", xytext=(10, 5), fontsize=10, fontweight='bold')

# 画正样本
ax1.plot(u_pos_2d[0], u_pos_2d[1], 'g^', markersize=10, zorder=5)
ax1.annotate(f'u_o ({VOCAB[pos_idx]})', (u_pos_2d[0], u_pos_2d[1]),
             textcoords="offset points", xytext=(10, 5), fontsize=10, color='green')

# 画负样本
colors_neg = ['red', 'orange', 'purple']
for u_neg, word, color in zip(u_neg_2ds, neg_words_2d, colors_neg):
    ax1.plot(u_neg[0], u_neg[1], 'v', color=color, markersize=10, zorder=5)
    ax1.annotate(f'u_{word}', (u_neg[0], u_neg[1]),
                 textcoords="offset points", xytext=(10, -10), fontsize=9, color=color)

# 画梯度箭头
ax1.annotate('', xy=v_2d + grad_pos * 3, xytext=v_2d,
             arrowprops=dict(arrowstyle='->', color='green', lw=2.5))
ax1.text(v_2d[0] + grad_pos[0]*1.5 - 0.5, v_2d[1] + grad_pos[1]*1.5 + 0.3,
         'pull toward\npositive', fontsize=8, color='green', ha='center')

for grad_neg, word, color in zip(grad_negs, neg_words_2d, colors_neg):
    ax1.annotate('', xy=v_2d + grad_neg * 3, xytext=v_2d,
                 arrowprops=dict(arrowstyle='->', color=color, lw=1.5, alpha=0.7))

# 总梯度
ax1.annotate('', xy=v_2d + grad_total * 2, xytext=v_2d,
             arrowprops=dict(arrowstyle='->', color='blue', lw=3))
ax1.text(v_2d[0] + grad_total[0]*2 + 0.2, v_2d[1] + grad_total[1]*2,
         'total grad', fontsize=8, color='blue', fontweight='bold')

ax1.set_xlabel("Dimension 1")
ax1.set_ylabel("Dimension 2")

# --- 图2: Loss 对比柱状图 ---
ax2 = axes[1]
labels = ['Full Softmax\nO(|V|)'] + [f'SGNS\nO(k={K})']
values = [full_softmax_loss, total_sgns_loss]
colors = ['steelblue', 'coral']
bars = ax2.bar(labels, values, color=colors, width=0.5, edgecolor='black', linewidth=0.8)

# 在柱子上标数值
for bar, val in zip(bars, values):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05,
             f'{val:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax2.set_ylabel('Loss value', fontsize=11)
ax2.set_title(f'Loss Comparison\nFull Softmax ({full_softmax_loss:.3f}) vs SGNS ({total_sgns_loss:.3f})',
              fontsize=12)
ax2.set_ylim(0, max(values) * 1.3)

# 添加计算量注释
ax2.text(0.5, 0.95, f'|V|={V}, k={K}\n加速比: ~{V//K}x (this toy)\n~20000x (|V|=100000)',
         transform=ax2.transAxes, ha='center', va='top',
         fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
output_dir = "Labs/L01-word-vectors/outputs"
os.makedirs(output_dir, exist_ok=True)
fig_path = os.path.join(output_dir, "negative-sampling-loss-gradient-and-comparison.png")
plt.savefig(fig_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"\n图表已保存: {fig_path}")

# ============================================================
# Part 5: 汇总输出 JSON（供 downstream 使用）
# ============================================================
summary = {
    "capsule": "negative-sampling-loss",
    "waypoint": "WP05",
    "vocab_size": V,
    "embedding_dim": D,
    "num_negatives": K,
    "full_softmax_loss": round(full_softmax_loss, 4),
    "sgns_loss": round(total_sgns_loss, 4),
    "positive_word": VOCAB[pos_idx],
    "positive_dot_product": round(pos_dot, 4),
    "positive_sigma": round(sigma_pos, 4),
    "negative_words": [VOCAB[i] for i in neg_indices],
    "negative_dot_products": [round(u_vectors[i] @ v_c, 4) for i in neg_indices],
    "speedup_toy": V // K,
    "speedup_real_10k": 10000 // K,
    "speedup_real_100k": 100000 // K,
    "gradient_positive": [round(x, 3) for x in grad_pos.tolist()],
    "gradient_total": [round(x, 3) for x in grad_total.tolist()],
    "figure": fig_path,
}

summary_path = os.path.join(output_dir, "negative-sampling-loss-summary.json")
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(f"汇总 JSON 已保存: {summary_path}")

print("\n" + "=" * 60)
print("运行完成。")
print("=" * 60)
>>>>>>> cf728cf (Add negative-sampling-loss capsule (WP05))
