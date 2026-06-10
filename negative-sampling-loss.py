#!/usr/bin/env python3
"""
Negative Sampling Loss vs Full Softmax — CS224N L01 WP05

Concept: Notes §3.5 (Eq.14-15, SGNS objective); R02 paper Section 3
Why code is needed: Notes gives the SGNS formula but doesn't explain WHY
the logistic approximation works. We need to actually compare the two
loss functions' computation cost, gradient behavior, and how k affects results.

Pure stdlib for core computation (Colab-ready). matplotlib only for plots.
"""
import math
import json
import os
import random

# ============================================================
# 1. Setup: small toy vocabulary (consistent with skipgram-softmax capsule)
# ============================================================

VOCAB = ["banking", "money", "crisis", "turning", "problems", "into"]
DIM = 3
SEED_V = 42
SEED_U = 99

def make_vectors(vocab, dim, seed):
    """Deterministic toy vectors for reproducibility."""
    vectors = {}
    for i, word in enumerate(vocab):
        vec = [round(math.sin(seed * (i + 1) * 7.3 + (d + 1) * 13.7) * 2.0, 4)
               for d in range(dim)]
        vectors[word] = vec
    return vectors

def dot(a, b):
    return sum(ai * bi for ai, bi in zip(a, b))

def sigmoid(x):
    """Numerically stable sigmoid."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    else:
        ez = math.exp(x)
        return ez / (1.0 + ez)

# ============================================================
# 2. Full Softmax Loss (Eq.14 from Notes)
# ============================================================

def softmax_loss(U, V, center, output, vocab):
    """
    Full softmax cross-entropy loss:
    J_softmax = -log( exp(u_o^T v_c) / sum_w exp(u_w^T v_c) )
              = -u_o^T v_c + log( sum_w exp(u_w^T v_c) )
    """
    vc = V[center]
    uo = U[output]
    scores = {}
    for w in vocab:
        scores[w] = dot(U[w], vc)
    max_score = max(scores.values())
    log_sum_exp = max_score + math.log(sum(math.exp(s - max_score) for s in scores.values()))
    loss = -dot(uo, vc) + log_sum_exp
    total_exp = sum(math.exp(s) for s in scores.values())
    probs = {w: math.exp(scores[w]) / total_exp for w in vocab}
    grad_vc = [0.0] * DIM
    for d in range(DIM):
        for w in vocab:
            grad_vc[d] += probs[w] * U[w][d]
        grad_vc[d] -= uo[d]
    n_dot_products = len(vocab)
    return loss, probs, grad_vc, n_dot_products

# ============================================================
# 3. Negative Sampling Loss (Eq.15 from Notes / R02 Section 3)
# ============================================================

def negative_sampling_loss(U, V, center, output, vocab, k, rng):
    """
    Negative sampling loss (SGNS):
    J_NS = -log(sigmoid(u_o^T v_c)) - sum_{i=1}^{k} E_{w~P(w)}[log(sigmoid(-u_w^T v_c))]
    """
    vc = V[center]
    uo = U[output]
    pos_score = dot(uo, vc)
    pos_loss = -math.log(sigmoid(pos_score) + 1e-10)
    candidates = [w for w in vocab if w != output]
    neg_words = [rng.choice(candidates) for _ in range(k)]
    neg_loss = 0.0
    neg_grad_vc = [0.0] * DIM
    for nw in neg_words:
        unw = U[nw]
        neg_score = dot(unw, vc)
        sig_neg = sigmoid(-neg_score)
        neg_loss += -math.log(sig_neg + 1e-10)
        sig_pos = sigmoid(neg_score)
        for d in range(DIM):
            neg_grad_vc[d] += sig_pos * unw[d]
    total_loss = pos_loss + neg_loss
    sig_pos_score = sigmoid(pos_score)
    grad_vc = [0.0] * DIM
    for d in range(DIM):
        grad_vc[d] = -(1.0 - sig_pos_score) * uo[d] + neg_grad_vc[d]
    n_dot_products = 1 + k
    return total_loss, neg_words, grad_vc, n_dot_products, pos_loss, neg_loss

# ============================================================
# 4. Comparison experiments
# ============================================================

def run_comparison():
    rng = random.Random(2024)
    V = make_vectors(VOCAB, DIM, SEED_V)
    U = make_vectors(VOCAB, DIM, SEED_U)
    center = "banking"
    output = "money"

    print("=" * 60)
    print("Negative Sampling Loss vs Full Softmax — CS224N L01 WP05")
    print("=" * 60)
    print()
    print(f"Vocabulary: {VOCAB}")
    print(f"|V| = {len(VOCAB)}, d = {DIM}")
    print(f"Center word c = '{center}', Output word o = '{output}'")
    print()

    print("-- Center vectors V --")
    for w in VOCAB:
        print(f"  v_{w} = {V[w]}")
    print("-- Context vectors U --")
    for w in VOCAB:
        print(f"  u_{w} = {U[w]}")
    print()

    # --- Full Softmax ---
    print("=" * 60)
    print("PART 1: Full Softmax Loss (Notes Eq.14)")
    print("=" * 60)
    print()
    print(f"Formula: J = -u_o^T v_c + log(sum_w exp(u_w^T v_c))")
    print(f"Must compute scores for ALL |V| = {len(VOCAB)} words")
    print()

    sm_loss, sm_probs, sm_grad, sm_dots = softmax_loss(U, V, center, output, VOCAB)

    print(f"Dot products u_w^T v_{center}:")
    for w in VOCAB:
        s = dot(U[w], V[center])
        marker = " <-- output word" if w == output else ""
        print(f"  u_{w}^T v_{center} = {s:.4f}{marker}")
    print()

    print(f"P(w|'{center}') under softmax:")
    for w in VOCAB:
        bar = "#" * int(sm_probs[w] * 40)
        marker = " <-- output" if w == output else ""
        print(f"  P({w:>10}|{center}) = {sm_probs[w]:.6f}  {bar}{marker}")
    print()

    print(f"Softmax loss = {sm_loss:.6f}")
    print(f"  = -log(P('{output}'|'{center}')) = -log({sm_probs[output]:.6f}) = {-math.log(sm_probs[output]):.6f}")
    print(f"Dot products needed: {sm_dots} (= |V|)")
    print(f"Gradient dJ/dv_c = [{', '.join(f'{g:.4f}' for g in sm_grad)}]")
    print()

    # --- Negative Sampling ---
    print("=" * 60)
    print("PART 2: Negative Sampling Loss (Notes Eq.15 / R02 Section 3)")
    print("=" * 60)
    print()
    print(f"Formula: J = -log(sigmoid(u_o^T v_c)) - sum_i log(sigmoid(-u_wi^T v_c))")
    print(f"Only needs k+1 dot products instead of |V|")
    print()

    for k in [2, 5, 10]:
        rng_k = random.Random(2024)
        ns_loss, neg_words, ns_grad, ns_dots, pos_l, neg_l = \
            negative_sampling_loss(U, V, center, output, VOCAB, k, rng_k)
        print(f"--- k = {k} ---")
        print(f"  Positive pair: ({center}, {output})")
        print(f"  Negative samples: {neg_words}")
        print(f"  Positive loss: -log(sigmoid(u_o^T v_c)) = {pos_l:.6f}")
        print(f"  Negative loss: sum -log(sigmoid(-u_w^T v_c)) = {neg_l:.6f}")
        print(f"  Total NS loss = {ns_loss:.6f}")
        print(f"  Dot products needed: {ns_dots} (= 1 + k)")
        print(f"  Gradient dJ/dv_c = [{', '.join(f'{g:.4f}' for g in ns_grad)}]")
        print()

    # --- Detailed k=5 comparison ---
    print("=" * 60)
    print("PART 3: Detailed Comparison (k=5)")
    print("=" * 60)
    print()

    rng5 = random.Random(2024)
    ns_loss_5, neg_words_5, ns_grad_5, ns_dots_5, pos_l_5, neg_l_5 = \
        negative_sampling_loss(U, V, center, output, VOCAB, 5, rng5)

    print(f"{'Metric':<35} {'Softmax':>12} {'NS (k=5)':>12}")
    print(f"{'-'*35} {'-'*12} {'-'*12}")
    print(f"{'Loss':<35} {sm_loss:>12.6f} {ns_loss_5:>12.6f}")
    print(f"{'Dot products':<35} {sm_dots:>12} {ns_dots_5:>12}")
    print(f"{'Computation ratio (NS/Softmax)':<35} {'':>12} {ns_dots_5/sm_dots:>11.0%}")
    print()

    sm_grad_norm = math.sqrt(sum(g**2 for g in sm_grad))
    ns_grad_norm = math.sqrt(sum(g**2 for g in ns_grad_5))
    print(f"{'Gradient ||dJ/dv_c||':<35} {sm_grad_norm:>12.6f} {ns_grad_norm:>12.6f}")
    print()

    dot_grad = sum(a * b for a, b in zip(sm_grad, ns_grad_5))
    if sm_grad_norm > 0 and ns_grad_norm > 0:
        grad_cos = dot_grad / (sm_grad_norm * ns_grad_norm)
    else:
        grad_cos = 0.0
    print(f"{'Gradient cosine similarity':<35} {grad_cos:>12.6f}")
    print()

    # --- Effect of k ---
    print("=" * 60)
    print("PART 4: Effect of k on Loss and Computation")
    print("=" * 60)
    print()

    k_values = [1, 2, 5, 10, 20, 50]
    results_k = []
    for k in k_values:
        rng_k = random.Random(2024)
        ns_l, nw, ns_g, ns_d, pos_l_k, neg_l_k = \
            negative_sampling_loss(U, V, center, output, VOCAB, k, rng_k)
        ns_g_norm = math.sqrt(sum(g**2 for g in ns_g))
        results_k.append({
            "k": k,
            "loss": round(ns_l, 6),
            "pos_loss": round(pos_l_k, 6),
            "neg_loss": round(neg_l_k, 6),
            "dot_products": ns_d,
            "grad_norm": round(ns_g_norm, 6),
            "neg_words": nw
        })
        print(f"  k={k:>3}: loss={ns_l:.6f}  dots={ns_d:>3}  grad_norm={ns_g_norm:.6f}  neg={nw}")

    print()
    print(f"  Softmax loss (reference): {sm_loss:.6f}")
    print(f"  Softmax dots (reference): {sm_dots}")
    print()

    # --- Why logistic approximation works ---
    print("=" * 60)
    print("PART 5: Why Logistic Approximation Works")
    print("=" * 60)
    print()
    print("Key insight: Negative sampling reframes word prediction as")
    print("BINARY CLASSIFICATION — 'is this a real (context, center) pair?'")
    print()
    print("  Positive pair (c, o):    maximize log(sigmoid(u_o^T v_c))")
    print("    -> push sigmoid(u_o^T v_c) toward 1.0")
    print()
    pos_sig = sigmoid(dot(U[output], V[center]))
    print(f"    Current: sigmoid(u_{output}^T v_{center}) = sigmoid({dot(U[output], V[center]):.4f}) = {pos_sig:.6f}")
    print()
    print("  Negative pair (c, w_i):  maximize log(sigmoid(-u_wi^T v_c))")
    print("    -> push sigmoid(u_wi^T v_c) toward 0.0")
    print()
    for nw in neg_words_5:
        neg_sig = sigmoid(dot(U[nw], V[center]))
        print(f"    sigmoid(u_{nw}^T v_{center}) = sigmoid({dot(U[nw], V[center]):.4f}) = {neg_sig:.6f}")
    print()
    print("This is a NOISE CONTRASTIVE ESTIMATION (NCE) approximation:")
    print("  Instead of normalizing over ALL |V| words (expensive),")
    print("  we just learn to distinguish the true pair from k noise samples.")
    print()

    # --- Real-world scaling ---
    print("=" * 60)
    print("PART 6: Real-world Scaling")
    print("=" * 60)
    print()
    real_V_sizes = [1000, 10000, 50000, 100000]
    print(f"{'|V|':>10} {'Softmax dots':>15} {'NS dots (k=5)':>15} {'Speedup':>10}")
    print(f"{'-'*10} {'-'*15} {'-'*15} {'-'*10}")
    for vs in real_V_sizes:
        speedup = vs / 6.0
        print(f"{vs:>10,} {vs:>15,} {6:>15} {speedup:>9,.0f}x")
    print()
    print(f"With |V|=100,000 and k=5: softmax needs 100,000 dots, NS needs only 6.")
    print(f"That's a {100000//6:,}x speedup per training step!")
    print()

    # --- Save structured output ---
    output_data = {
        "vocab": VOCAB,
        "dim": DIM,
        "center": center,
        "output": output,
        "softmax": {
            "loss": round(sm_loss, 6),
            "probs": {w: round(p, 6) for w, p in sm_probs.items()},
            "grad": [round(g, 6) for g in sm_grad],
            "dot_products": sm_dots
        },
        "negative_sampling_k5": {
            "loss": round(ns_loss_5, 6),
            "pos_loss": round(pos_l_5, 6),
            "neg_loss": round(neg_l_5, 6),
            "neg_words": neg_words_5,
            "grad": [round(g, 6) for g in ns_grad_5],
            "dot_products": ns_dots_5,
            "grad_cosine_vs_softmax": round(grad_cos, 6)
        },
        "k_sweep": results_k,
        "gradient_comparison": {
            "softmax_grad_norm": round(sm_grad_norm, 6),
            "ns_k5_grad_norm": round(ns_grad_norm, 6),
            "cosine_similarity": round(grad_cos, 6)
        }
    }

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "negative-sampling-loss-output.json")
    with open(out_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"Structured output saved: {out_path}")
    return output_data

if __name__ == "__main__":
    run_comparison()
