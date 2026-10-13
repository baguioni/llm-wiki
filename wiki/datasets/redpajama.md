---
type: Dataset
title: RedPajama
description: Replicated pre-training dataset of the LLaMA1 models with seven domains, used in the wiki's papers as the data for structured pruning and continued pre-training.
tags: [dataset, pre-training-data, pruning, structured-pruning]
sources:
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
---

# RedPajama

## Overview

RedPajama is a replicated pre-training dataset of the LLaMA1 models.[^xiaShearedLLaMAAccelerating2024] Xia et al. use it for pruning and continued pre-training because the training data for LLaMA2 is not publicly accessible.[^xiaShearedLLaMAAccelerating2024] Yan et al. sample pruning tokens from it to build draft models for [speculative decoding](../methods/speculative-decoding.md).[^yanDecodingSpeculativeDecoding2025]

## Composition

Seven domains: CommonCrawl, C4, Github, Wikipedia, Books, ArXiv, and StackExchange.[^xiaShearedLLaMAAccelerating2024]

| | CC | GitHub | Book | StackExchange | Wiki | ArXiv | [C4](c4.md) |
|---|---|---|---|---|---|---|---|
| RedPajama (Original) proportion | $67.0\%$ | $4.5\%$ | $4.5\%$ | $2.0\%$ | $4.5\%$ | $2.5\%$ | $15.0\%$ |

All values: [^xiaShearedLLaMAAccelerating2024]

The total size is not stated in the wiki's papers.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Xia et al. 2024](../papers/xiaShearedLLaMAAccelerating2024.md) | Pruning and continued pre-training of [Sheared-LLaMA](../methods/sheared-llama.md); per-domain validation loss | LLaMA2-7B source, 0.4 billion tokens for pruning, 50 billion tokens for continued pre-training, sequence length 4,096 | See the tables below[^xiaShearedLLaMAAccelerating2024] |
| [Yan et al. 2025](../papers/yanDecodingSpeculativeDecoding2025.md) | Pruning data for NoFT draft models | LLaMa-7B source, 0.4B tokens, no fine-tuning | $0.8\%$ of the Sheared-LLaMa-1.3B training tokens[^yanDecodingSpeculativeDecoding2025] |

### How the papers use it

- Xia et al. build a held-out validation set with 2 million tokens for each domain, equivalent to 500 sequences of 4,096 tokens. They allocate 0.4 billion tokens to the pruning phase and 50 billion tokens to continued pre-training.[^xiaShearedLLaMAAccelerating2024]
- Continued pre-training on RedPajama reduces loss at different rates across domains compared to pre-training from scratch. The pruned model's loss on GitHub is better than the reference loss, and significantly worse than the reference loss on C4.[^xiaShearedLLaMAAccelerating2024]
- Dynamic batch loading changes the domain mix during training. It loads more data from the Book and C4 subsets:[^xiaShearedLLaMAAccelerating2024]

| | CC | GitHub | Book | StackExchange | Wiki | ArXiv | C4 |
|---|---|---|---|---|---|---|---|
| RedPajama (Original) | $67.0\%$ | $4.5\%$ | $4.5\%$ | $2.0\%$ | $4.5\%$ | $2.5\%$ | $15.0\%$ |
| Dynamic Batch Loading | $36.1\%$ | $0.8\%$ | $9.1\%$ | $1.0\%$ | $3.1\%$ | $0.7\%$ | $49.2\%$ |

All rows: [^xiaShearedLLaMAAccelerating2024]

- Pruned models trained with dynamic batch loading achieve better downstream performance than when trained on the original RedPajama distribution. The result is shown only in a figure.[^xiaShearedLLaMAAccelerating2024]
- Xia et al. state that dynamic batch loading can train an LLM to match any reference model's performance with open-source pre-training datasets like RedPajama, even without knowing the reference model's exact training data.[^xiaShearedLLaMAAccelerating2024]
- Yan et al. prune their models from LLaMa-7B using 0.4B tokens sampled from RedPajama, following Sheared-LLaMa, and skip the fine-tuning step on 50B more tokens, which gives the name NoFT.[^yanDecodingSpeculativeDecoding2025] Their NoFT-Wide-796M draft uses only $0.8\%$ of the training tokens of Sheared-LLaMA-1.3B.[^yanDecodingSpeculativeDecoding2025]

### Models pre-trained on RedPajama

| Model | Pre-training data | #Tokens | Reported by |
|---|---|---|---|
| INCITE-Base | RedPajama | 800B | [^xiaShearedLLaMAAccelerating2024] |
| OpenLLaMA v1 | RedPajama | 1T | [^xiaShearedLLaMAAccelerating2024] |
| OpenLLaMA v2 | a mixture of RefinedWeb, StarCoder, and part of RedPajama | 1T | [^xiaShearedLLaMAAccelerating2024] |
| Sheared-LLaMA | RedPajama | 50B | [^xiaShearedLLaMAAccelerating2024] |

### Task quality: downstream average of models trained on RedPajama

Average over the 11 downstream tasks of Table 2 of Xia et al. The setting column gives the training token count.[^xiaShearedLLaMAAccelerating2024]

| Model | Setting | Average | Reported by |
|---|---|---|---|
| Sheared-LLaMA-1.3B | 50B tokens, pruned from LLaMA2-7B | 51.0 | [^xiaShearedLLaMAAccelerating2024] |
| INCITE-Base-3B | 800B tokens | 54.7 | [^xiaShearedLLaMAAccelerating2024] |
| Open-LLaMA-3B-v1 | 1T tokens | 55.1 | [^xiaShearedLLaMAAccelerating2024] |
| Sheared-LLaMA-2.7B | 50B tokens, pruned from LLaMA2-7B | 56.7 | [^xiaShearedLLaMAAccelerating2024] |

Per-task values for [MMLU](mmlu.md) and [HellaSwag](hellaswag.md) are on those pages.

### Task quality: per-domain loss

Estimated reference loss of hypothetical LLaMA2 models, from a scaling function fitted per domain:[^xiaShearedLLaMAAccelerating2024]

| Model | Setting | CC | GitHub | Book | StackExchange | Wiki | ArXiv | C4 |
|---|---|---|---|---|---|---|---|---|
| LLaMA2-1.3B | estimated reference loss | 1.964 | 0.746 | 2.139 | 1.612 | 1.759 | 1.445 | 2.125 |
| LLaMA2-2.7B | estimated reference loss | 1.871 | 0.688 | 2.033 | 1.535 | 1.630 | 1.356 | 2.033 |

All rows: [^xiaShearedLLaMAAccelerating2024]

Pruning LLaMA1-13B to a 7B model with a composite of $40\%$ CC, $40\%$ C4, $10\%$ Books and $10\%$ Wikipedia, then continuing pre-training on RedPajama:[^xiaShearedLLaMAAccelerating2024]

| Model | Setting | CC | GitHub | Book | StackExchange | Wikipedia | ArXiv | C4 |
|---|---|---|---|---|---|---|---|---|
| LLaMA1-13B | source model | 1.7585 | 0.6673 | 1.9499 | 1.4207 | 1.4331 | 1.3855 | 1.8619 |
| LLaMA1-7B | reference | 1.8366 | 0.7108 | 2.0322 | 1.5112 | 1.5291 | 1.4340 | 1.9331 |
| Pruned model | pruned without three domains | 2.1849 | 1.0971 | 2.3726 | 1.9080 | 2.1151 | 1.7542 | 2.3187 |
| Pruned model | continued pre-training with RedPajama | 1.8344 | 0.6325 | 2.0984 | 1.4542 | 1.4549 | 1.4460 | 2.0395 |

All rows: [^xiaShearedLLaMAAccelerating2024]

After continued pre-training on all seven domains, the difference from LLaMA1-7B is -0.0783 on GitHub and 0.1064 on C4, so excluding the easy domains during pruning does not resolve the imbalance.[^xiaShearedLLaMAAccelerating2024]

### Speed

No speed metric is measured on RedPajama itself. Drafts pruned on RedPajama tokens are timed on other prompt sets; see the speed tables on [MMLU](mmlu.md) and [HellaSwag](hellaswag.md).[^yanDecodingSpeculativeDecoding2025]

## Related

- Datasets: [C4](c4.md), [MMLU](mmlu.md), [HellaSwag](hellaswag.md)
- Methods: [Sheared-LLaMA](../methods/sheared-llama.md), [Structured pruning](../methods/structured-pruning.md), [Speculative decoding](../methods/speculative-decoding.md)

[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
