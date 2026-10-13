---
type: Method
title: LLM-Pruner
description: A structured pruning method for LLMs that the wiki's papers use only as a comparison baseline for Sheared-LLaMA and Minitron.
tags: [structured-pruning, model-compression, baseline]
sources:
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
---

# LLM-Pruner

## Overview

LLM-Pruner is a [structured pruning](../methods/structured-pruning.md) method for LLMs (Ma et al., 2023).[^xiaShearedLLaMAAccelerating2024] No paper in this wiki proposes it or describes its algorithm in detail. Two papers use it as a baseline, and this page records only what they state.

## How it works

The wiki's papers give only short characterizations:

- Muralidharan et al. cite it for a gradient/Taylor importance metric, and group it with width-pruning work that uses learnable masks combined with an Augmented Lagrangian loss formulation.[^muralidharanCompactLanguageModels2024]
- Xia et al. state that it does not specify a targeted structure, and that the algorithm is unable to prune the hidden dimension and layers.[^xiaShearedLLaMAAccelerating2024]

## Papers using it

### Sheared LLaMA (baseline)

[Sheared LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) compares its targeted structured pruning with LLM-Pruner. The non-embedding parameter count is matched to roughly that of the final Sheared-LLaMA model (1.23B), the total number of tokens for pruning and continued pre-training is the same for both, and RedPajama data is used without dynamic batch loading.[^xiaShearedLLaMAAccelerating2024]

Model structure (Table 11):[^xiaShearedLLaMAAccelerating2024]

| | Layers | Heads | Head size | Intermediate size | Hidden size | Params |
|---|---|---|---|---|---|---|
| Pythia-1.4B | 24 | 16 | 128 | 8192 | 2048 | 1.4B |
| LLM-pruner (1.6B) | 32 | 7 | 128 | 2201 | 4096 | 1.6B |
| Sheared-LLaMA (1.3B) | 24 | 16 | 128 | 5504 | 2048 | 1.3B |

Training throughput, generation speed, and perplexity after around 6B tokens (Table 12):[^xiaShearedLLaMAAccelerating2024]

| | Generation Speed | Training Throughput | PPL |
|---|---|---|---|
| LLM-Pruner | 43 tokens/s | 83K tokens/s | 7.09 |
| Sheared-LLaMA | 58 tokens/s | 139K tokens/s | 6.85 |

Inference speed in tokens/s on an A100 GPU, generating up to 2048 tokens with a batch size of 1 (Table 16). Here LLM-Pruner produces a model with the same number of non-embedding parameters as Sheared-LLaMA:[^xiaShearedLLaMAAccelerating2024]

| Model | 7B | 1.3B | 2.7B |
|---|---|---|---|
| LLaMA-7B | 37 | n/a | n/a |
| LLM Pruner | n/a | 41 | 40 |
| Sheared-LLaMA | n/a | 62 | 47 |

- The loss of targeted structured pruning during continued pre-training is lower than that of LLM-Pruner at the same amount of data (shown in a figure).[^xiaShearedLLaMAAccelerating2024]
- The training throughput of the LLM-Pruner architecture is around $60\%$ of Sheared-LLaMA's, measured with 16 A100 80GB GPUs.[^xiaShearedLLaMAAccelerating2024]

### Compact Language Models via Pruning and Knowledge Distillation (baseline)

[Muralidharan et al.](../papers/muralidharanCompactLanguageModels2024.md) list LLMPruner among depth- and width-pruned baselines for Minitron (Table 4):[^muralidharanCompactLanguageModels2024]

| Target | Model | # Parameters | # Non-Emb. Params | [MMLU](../datasets/mmlu.md) (5) acc | [hellaswag](../datasets/hellaswag.md) (10) acc_norm |
|---|---|---|---|---|---|
| 8 Billion | LLMPruner | 9.8B | 9.5B | 25.2 | 67.8 |
| 8 Billion | Minitron | 8.3B | 6.2B | 63.8 | 80.7 |
| 4 Billion | LLMPruner | 4.8B | 4.5B | 23.33 | 56.46 |
| 4 Billion | Minitron | 4.2B | 2.6B | 58.6 | 75 |

The table does not name the base model of the LLMPruner entries in the extracted text.

## Strengths & Limitations

- The LLM-Pruner model in Xia et al.'s comparison has an intermediate size (2201) smaller than its hidden size (4096). Xia et al. call this an unconventional architecture, attribute it to the algorithm's inability to prune the hidden dimension and layers, and note that it goes against transformer designs where the intermediate size is at least 3-4 times the hidden size.[^xiaShearedLLaMAAccelerating2024]
- Xia et al. report that structured pruning with LLM-Pruner, like unstructured and semi-structured pruning, leads to significant performance drops on LLMs even at a modest sparsity.[^xiaShearedLLaMAAccelerating2024]
- Muralidharan et al. state that learnable-mask methods of this group need compute and memory-intensive gradient computations and a considerable amount of data and fine-tuning to arrive at reasonable masks.[^muralidharanCompactLanguageModels2024]

# Contradictions

**Generation speed within Xia et al.** Table 12 gives 43 tokens/s for LLM-Pruner (1.6B) and 58 tokens/s for Sheared-LLaMA (1.3B); the accompanying text says a single A100 GPU generating up to 2048 tokens. Table 16 gives 41 tokens/s for LLM Pruner and 62 tokens/s for Sheared-LLaMA at 1.3B, on an A100 GPU generating up to 2048 tokens with a batch size of 1.[^xiaShearedLLaMAAccelerating2024] Both passages say the LLM-Pruner model is matched to Sheared-LLaMA in non-embedding parameters. The paper does not explain the difference between the two tables.

## Related

- [Structured pruning](../methods/structured-pruning.md)
- [Sheared-LLaMA](../methods/sheared-llama.md)
- Datasets: [MMLU](../datasets/mmlu.md), [HellaSwag](../datasets/hellaswag.md)

[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
