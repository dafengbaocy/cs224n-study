#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


TERM_ALIASES = {
    "one hot": "one-hot-encoding",
    "one-hot": "one-hot-encoding",
    "orthogonality": "orthogonality",
    "dense": "dense-vector",
    "dot product": "dot-product",
    "cosine": "cosine-similarity",
    "similarity": "cosine-similarity",
    "co-occurrence": "co-occurrence-matrix",
    "cooccurrence": "co-occurrence-matrix",
    "sparse": "sparse-matrix",
    "svd": "svd",
    "softmax": "softmax",
    "skip-gram": "skip-gram",
    "skipgram": "skip-gram",
    "negative sampling": "negative-sampling",
    "sigmoid": "sigmoid",
    "sgd": "sgd",
    "stochastic gradient descent": "sgd",
    "cross entropy": "cross-entropy-loss",
    "cross-entropy": "cross-entropy-loss",
    "pretrained": "pretrained-word-vectors",
    "word vector": "word-vector",
    "analogy": "analogy",
    "pca": "pca",
    "embedding": "embedding",
}

TERM_LABELS = {
    "analogy": "Analogy",
    "co-occurrence-matrix": "Co-occurrence Matrix",
    "cosine-similarity": "Cosine Similarity",
    "cross-entropy-loss": "Cross-Entropy Loss",
    "dense-vector": "Dense Vector",
    "dot-product": "Dot Product",
    "embedding": "Embedding",
    "negative-sampling": "Negative Sampling",
    "one-hot-encoding": "One-hot Encoding",
    "orthogonality": "Orthogonality",
    "pca": "PCA",
    "pretrained-word-vectors": "Pretrained Word Vectors",
    "sgd": "SGD",
    "sigmoid": "Sigmoid",
    "skip-gram": "Skip-gram",
    "softmax": "Softmax",
    "sparse-matrix": "Sparse Matrix",
    "svd": "SVD",
    "word-vector": "Word Vector",
}

TERM_DESCRIPTIONS = {
    "analogy": "用向量关系表达 A:B::C:? 这类问题的检查方式。",
    "co-occurrence-matrix": "统计词和上下文一起出现次数的矩阵，是理解分布语义的计数版入口。",
    "cosine-similarity": "用向量夹角衡量方向相似度，常用于比较词向量。",
    "cross-entropy-loss": "把正确答案概率变高、错误答案概率变低的常见分类损失。",
    "dense-vector": "低维、连续、每个维度通常都有数值的向量表示。",
    "dot-product": "两个向量对应维相乘再求和，word2vec 中常作为相似度分数。",
    "embedding": "把离散对象映射成连续向量的表示方法。",
    "negative-sampling": "每次只抽少量负样本训练，避免 full softmax 扫完整个词表。",
    "one-hot-encoding": "每个词一个位置为 1、其余为 0 的离散表示。",
    "orthogonality": "向量点积为 0 的关系；one-hot 词向量之间通常两两正交。",
    "pca": "把高维向量投影到低维空间用于可视化或分析的线性降维方法。",
    "pretrained-word-vectors": "已经在大语料上训练好的词向量，可以直接加载用于相似度和类比实验。",
    "sgd": "每次用一个或一小批样本更新参数的优化方法。",
    "sigmoid": "把实数压到 0 到 1 的函数，负采样里用于二分类目标。",
    "skip-gram": "用中心词预测上下文词的 word2vec 训练任务。",
    "softmax": "把一组分数归一化成概率分布的函数。",
    "sparse-matrix": "大多数位置为 0 的矩阵；共现计数矩阵常很稀疏。",
    "svd": "把矩阵分解成低维结构的线性代数工具，A1 会用它做降维。",
    "word-vector": "表示词含义或用法的连续向量。",
}


def slugify(value: str) -> str:
    raw = value.lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return raw or "term"


def load_capsules(root: Path, lecture: str) -> list[dict]:
    parser = root / "scripts" / "parse_readings_map.py"
    readings = root / "Lectures" / lecture / "02-readings-map.md"
    python = root / ".venv" / "bin" / "python"
    python_cmd = str(python) if python.exists() else sys.executable
    result = subprocess.run(
        [python_cmd, str(parser), str(readings), "--field", "code_capsules", "--json"],
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(result.stdout)
    if not isinstance(data, list):
        raise SystemExit("code_capsules is not a list")
    return [item for item in data if isinstance(item, dict)]


def detect_terms(capsules: list[dict]) -> set[str]:
    terms: set[str] = set()
    for item in capsules:
        haystack = " ".join(str(item.get(key, "")) for key in ("slug", "concept", "why_not_text", "official_anchor"))
        lower = haystack.lower()
        for needle, term in TERM_ALIASES.items():
            if needle in lower:
                terms.add(term)
    for item in capsules:
        concept = str(item.get("concept", "")).strip()
        if concept:
            terms.add(slugify(concept))
    return terms


def existing_body(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    marker = "<!-- glossary-seed: generated terms end -->"
    if marker in text:
        return text.split(marker, 1)[1].lstrip()
    return "\n\n<!-- existing glossary content preserved below -->\n\n" + text


def main() -> int:
    ap = argparse.ArgumentParser(description="Seed a stable concept glossary before Code Capsules.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--lecture", required=True)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = root / "Lectures" / args.lecture / "00-concept-glossary.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    capsules = load_capsules(root, args.lecture)
    terms = sorted(detect_terms(capsules))

    lines = [
        f"# {args.lecture} Concept Glossary",
        "",
        "<!-- glossary-seed: generated terms start -->",
        "",
        "> 本文件由 `scripts/seed_concept_glossary.py` 在 Code Capsules 前生成 seed。",
        "> Code / DeepResearch 可以链接这些稳定 heading；Lecture Weaver 后续负责补全、去重和美化。",
        "",
    ]
    for term in terms:
        label = TERM_LABELS.get(term, term.replace("-", " ").title())
        desc = TERM_DESCRIPTIONS.get(term, "本词条由当前讲次 code capsule 配置预留；后续阶段补全精确定义和链接。")
        lines.extend([
            f"## {term}",
            "",
            f"**{label}**：{desc}",
            "",
            "- 来源：`02-readings-map.md` 的 `code_capsules` 配置或本讲已通过产物。",
            "- 状态：seed；可被上游产物稳定链接，最终解释由 Lecture Weaver 收口。",
            "",
        ])
    lines.append("<!-- glossary-seed: generated terms end -->")
    tail = existing_body(out)
    if tail:
        lines.append("")
        lines.append(tail.rstrip())
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"glossary={out.relative_to(root).as_posix()}")
    print(f"terms={len(terms)}")
    for term in terms:
        print(f"- {term}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
