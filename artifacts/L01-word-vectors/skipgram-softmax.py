#!/usr/bin/env python3
"""
Skip-gram softmax P(o|c) - CS224N L01 WP03
Pure stdlib. Colab-ready.
"""
import math, json, os

def make_vectors(vocab, dim, seed):
    vectors = {}
    for i, word in enumerate(vocab):
        vec = [round(math.sin(seed*(i+1)*7.3 + (d+1)*13.7)*2.0, 4) for d in range(dim)]
        vectors[word] = vec
    return vectors

def dot(a, b):
    return sum(ai*bi for ai, bi in zip(a, b))

def main():
    vocab = ["banking", "money", "crisis", "turning", "problems", "into"]
    dim = 3
    V = make_vectors(vocab, dim, 42)
    U = make_vectors(vocab, dim, 99)

    print(f"=== Skip-gram Softmax P(o|c) ===")
    print(f"vocab: {vocab}")
    print(f"|V| = {len(vocab)}, d = {dim}")
    print()
    print("-- Center vectors V --")
    for w in vocab: print(f"  v_{w} = {V[w]}")
    print("-- Context vectors U --")
    for w in vocab: print(f"  u_{w} = {U[w]}")
    print()

    c = "banking"
    print(f"=== center c = '{c}' ===")
    print(f"  v_c = {V[c]}")
    print()

    print("-- Step 1: dot products --")
    scores = {}
    for w in vocab:
        s = dot(U[w], V[c])
        scores[w] = round(s, 4)
        print(f"  u_{w}^T v_{c} = {s:.4f}")
    print()

    print("-- Step 2: exp(score) --")
    exps = {}
    for w in vocab:
        exps[w] = round(math.exp(scores[w]), 6)
        print(f"  exp({scores[w]:>8.4f}) = {exps[w]:.6f}")
    print()

    Z = sum(exps.values())
    print(f"-- Step 3: Z = {Z:.6f} --")
    print()

    print("-- Step 4: P(o|c) --")
    probs = {}
    for w in vocab:
        probs[w] = round(exps[w] / Z, 6)
        print(f"  P({w:>10s} | {c}) = {exps[w]:.6f} / {Z:.6f} = {probs[w]:.6f}")
    print()
    print(f"sum = {sum(probs.values()):.6f}")
    print()

    ranked = sorted(probs.items(), key=lambda x: -x[1])
    print("-- ranking --")
    for i, (w, p) in enumerate(ranked, 1):
        print(f"  {i}. {w:>10s}: {p:.6f}  {'#'*int(p*50)}")

    out = {
        "vocab": vocab, "vocab_size": len(vocab), "dim": dim,
        "center_word": c, "center_vector": V[c],
        "scores": scores,
        "exp_scores": {k: round(v,6) for k,v in exps.items()},
        "partition_function": round(Z, 6),
        "probabilities": probs, "prob_sum": round(sum(probs.values()), 6),
        "ranking": [{"rank": i+1, "word": w, "probability": p} for i,(w,p) in enumerate(ranked)],
        "top_word": ranked[0][0], "top_prob": ranked[0][1],
    }
    odir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(odir, exist_ok=True)
    jp = os.path.join(odir, "skipgram-softmax-output.json")
    with open(jp, "w") as f: json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nJSON: {jp}")
    print("=== done ===")

if __name__ == "__main__":
    main()
