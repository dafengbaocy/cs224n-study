## one-hot-vs-dense — One-hot 向量 vs Dense 向量 {#one-hot-vs-dense}

> [!info] 这个 Capsule 在看什么
> **概念**：[[Lectures/L01-word-vectors/00-concept-glossary#one-hot-encoding|one-hot encoding]] 让每个词成为正交基向量，所有不同词的点积都是 0，无法编码相似度；[[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense vector]] 把词映射到低维连续空间，语义相近的词方向接近，可以用[[Lectures/L01-word-vectors/00-concept-glossary#cosine-similarity|余弦相似度]]衡量。
>
> **为什么不能只靠文字**：Slides p19-22 展示了 one-hot 和 dense 的概念，但只有亲手算[[Lectures/L01-word-vectors/00-concept-glossary#dot-product|点积]]、看数字，才能真正理解为什么 one-hot 的 hotel·motel = book·fish = 0——这个「所有词等距」的问题有多致命。
>
> **官方锚点**：Slides p19-p22; Notes §2.2 Eq.1-2

### 运行方式

**Colab 打开**（推荐）：[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dafengbaocy/cs224n-study/blob/main/L01-word-vectors/one-hot-vs-dense.ipynb)

**本地运行**：
```bash
cd /workspace/cs224n-study
.venv/bin/python one-hot-vs-dense.py
```

### 这段代码在做什么

1. 用 6 个词（hotel, motel, book, cat, dog, fish）构建 [[Lectures/L01-word-vectors/00-concept-glossary#one-hot-encoding|one-hot]] 向量
2. 计算 one-hot [[Lectures/L01-word-vectors/00-concept-glossary#dot-product|点积]]——所有词对都是 0
3. 构建 toy [[Lectures/L01-word-vectors/00-concept-glossary#dense-vector|dense vector]]（2 维，模拟训练后结果）
4. 计算 dense 余弦相似度——近义词 hotel-motel = 0.9980，无关词 book-fish = -0.2195

### 运行后先看哪里

> [!tip] 输出解读
> 1. **One-hot 点积**：hotel·motel = 0.0, cat·dog = 0.0, book·fish = 0.0——全部是 0，无论词对关系如何。
> 2. **Dense 余弦相似度**：hotel-motel = 0.9980（近义），cat-dog = 0.9979（同类），book-fish = -0.2195（无关）。
> 3. **对比图**：左图 one-hot 编码，所有柱都是 0；右图 dense 向量，近义柱高、无关柱低甚至为负。

### 关键输出

**One-hot 点积**（所有不同词对 = 0）：

```
   hotel · motel  = 0.0   (synonyms — should be similar)
     cat · dog    = 0.0   (both animals — should be somewhat similar)
    book · fish   = 0.0   (unrelated — should be dissimilar)
```

⚠️ 所有点积都是 0.0——one-hot 向量完全正交，模型无法区分近义词和无关词。

**Dense 余弦相似度**（反映语义关系）：

```
  cos(hotel, motel) = 0.9980   (synonyms — should be similar)
  cos(cat, dog) = 0.9979       (both animals — should be somewhat similar)
  cos(book, fish) = -0.2195    (unrelated — should be dissimilar)
```

**关键对比**：

| 词对 | 关系 | One-hot 点积 | Dense cos_sim |
|------|------|-------------|---------------|
| hotel-motel | 近义词 | 0.0 | 0.9980 |
| cat-dog | 同类动物 | 0.0 | 0.9979 |
| book-fish | 无关 | 0.0 | -0.2195 |

### 对比图

![One-hot vs Dense 对比图](https://raw.githubusercontent.com/dafengbaocy/obsidian-image/main/img/2026/06/10/20260610-180800.png)

> [!tip] 读图指南
> - **左图**（One-hot）：三组词对的点积全是 0（蓝色柱），无论它们是近义词还是无关词。
> - **右图**（Dense）：近义词 hotel-motel 余弦相似度接近 1.0（红色柱最高），同类 cat-dog 也接近 1.0，无关词 book-fish 为负值。
> - **关键结论**：dense vector 成功把「语义相近 = 方向接近」编码进了向量空间，而 one-hot 完全做不到。

### 和课堂内容的对应

| 课堂材料 | 对应内容 |
|----------|----------|
| Slides p19 | One-hot 向量展示：`motel = [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0]` |
| Slides p20 | 正交问题："There is no natural notion of similarity for one-hot vectors!" |
| Slides p22 | Dense vector："We will build a dense vector for each word...measuring similarity as the vector dot product" |
| Notes §2.2 Eq.1-2 | 数学论证：$v_{tea}^T v_{coffee} = v_{tea}^T v_{the} = 0$，"all words are equally dissimilar" |

### 容易误解的地方

> [!warning] 注意
> 1. **Dense 向量的值不是手动设计的**——实际中由模型（如 Word2Vec）训练得到。这里的 toy 向量只是为了演示「训练后应该有的效果」。
> 2. **2 维只是演示**。实际词向量通常 100-300 维。维度越高，能编码的语义信息越丰富。
> 3. **余弦相似度 vs 点积**：点积受向量长度影响；余弦相似度归一化了长度，只看方向。one-hot 向量长度都是 1，所以两者等价。
> 4. **One-hot 不是完全没用**。在分类任务的输出层，one-hot 仍然用作标签表示。它的问题是作为**输入表示**时无法编码相似度。
> 5. **book-fish 余弦为负**：负值表示两个向量方向几乎相反，比 0 更「不相似」。实际训练的词向量中，反义词经常出现负相似度。

### 数字来源证明

```yaml
numeric_provenance:
  run_log: run-log.md#run_id 20260610T100536Z__t_ec7c208c__one-hot-vs-dense
  stdout: outputs/one-hot-vs-dense-stdout.txt
  checked_values:
    - claim: "hotel·motel one-hot dot = 0.0"
      source: "stdout: 'hotel · motel  = 0.0   (synonyms — should be similar)'"
      status: copied_from_output
    - claim: "cat·dog one-hot dot = 0.0"
      source: "stdout: 'cat · dog    = 0.0   (both animals — should be somewhat similar)'"
      status: copied_from_output
    - claim: "book·fish one-hot dot = 0.0"
      source: "stdout: 'book · fish   = 0.0   (unrelated — should be dissimilar)'"
      status: copied_from_output
    - claim: "cos(hotel, motel) = 0.9980"
      source: "stdout: 'cos(hotel, motel) = 0.9980   (synonyms — should be similar)'"
      status: copied_from_output
    - claim: "cos(cat, dog) = 0.9979"
      source: "stdout: 'cos(cat, dog) = 0.9979   (both animals — should be somewhat similar)'"
      status: copied_from_output
    - claim: "cos(book, fish) = -0.2195"
      source: "stdout: 'cos(book, fish) = -0.2195   (unrelated — should be dissimilar)'"
      status: copied_from_output
```
