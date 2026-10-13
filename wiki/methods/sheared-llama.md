---
type: Method
title: Sheared-LLaMA
description: LLM-shearing prunes LLaMA2-7B to a pre-specified 1.3B or 2.7B architecture with targeted structured pruning and continues pre-training with dynamic batch loading; the name covers both the method and the resulting models.
tags: [structured-pruning, model-compression, small-language-models, draft-model, speculative-decoding]
sources:
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
---

# Sheared-LLaMA

## Overview

Sheared-LLaMA is a series of models obtained by pruning LLaMA2-7B down to 1.3B and 2.7B parameters.[^xiaShearedLLaMAAccelerating2024] The approach, [structured pruning](../methods/structured-pruning.md) to a specified target shape followed by continued pre-training, uses two techniques: targeted structured pruning and dynamic batch loading.[^xiaShearedLLaMAAccelerating2024] The authors report that the models outperform open-source models of equivalent sizes while requiring only $3\%$ of the compute of training such models from scratch.[^xiaShearedLLaMAAccelerating2024]

## How it works

The process has two stages: prune the source model into the target model, then continue pre-training the pruned model with a language modeling objective.[^xiaShearedLLaMAAccelerating2024]

- **Targeted structured pruning.** The method prunes a source model to a specified target architecture by removing layers, heads, and intermediate and hidden dimensions end to end.[^xiaShearedLLaMAAccelerating2024] Masking variables $z$ are learned to control whether a substructure is pruned ($z=0$) or retained ($z=1$).[^xiaShearedLLaMAAccelerating2024] After pruning, the highest-scoring components of each substructure are kept.[^xiaShearedLLaMAAccelerating2024]
- **Pruning cost.** The pruning stage is roughly 5$\times$ slower than standard LM training and the learned masks often converge fast, so only a limited budget is allocated to pruning.[^xiaShearedLLaMAAccelerating2024]
- **Dynamic batch loading.** The composition of sampled data in each training batch is updated dynamically, based on varying losses across domains.[^xiaShearedLLaMAAccelerating2024]
- **Data and budget.** Pruning and continued pre-training use [RedPajama](../datasets/redpajama.md), with 0.4 billion tokens for the pruning phase and 50 billion tokens for continued pre-training.[^xiaShearedLLaMAAccelerating2024]
- **Head dimension.** The shearing algorithm inherits the head dimension of the source model. The target number of heads is the target hidden dimension divided by the head dimension of the source model.[^xiaShearedLLaMAAccelerating2024]

Yan et al. summarize the method as a framework that prunes larger models to a specified smaller configuration by learning which layers, attention heads, and neurons to mask.[^yanDecodingSpeculativeDecoding2025]

## Variants

Model configurations:[^xiaShearedLLaMAAccelerating2024]

| Model | #Param | #Layers | Hidden | Intermediate | #Heads | Head Dim |
|---|---|---|---|---|---|---|
| Sheared-LLaMA-1.3B | 1.3B | 24 | 2048 | 5504 | 16 | 128 |
| Sheared-LLaMA-2.7B | 2.7B | 32 | 2560 | 6912 | 20 | 128 |
| LLaMA2-7B (source) | 6.7B | 32 | 4096 | 11008 | 32 | 128 |

Draft-model variants pruned from LLaMa-7B with the Sheared-LLaMa scheme, using 0.4B tokens from RedPajama and skipping the fine-tuning step on 50B more tokens (hence NoFT). l is the number of layers, h the number of attention heads, $d_{\text{inter}}$ the intermediate size, $d_{\text{model}}$ the model dimension:[^yanDecodingSpeculativeDecoding2025]

| Model | l | h | $d_{\text{inter}}$ | $d_{\text{model}}$ |
|---|---|---|---|---|
| NoFT-1.3B | 24 | 16 | 5504 | 2048 |
| NoFT-Wide-1.3B | 12 | 20 | 9280 | 2560 |
| NoFT-Wide-796M | 5 | 32 | 11008 | 4096 |
| NoFT-Wide-543M | 3 | 32 | 11008 | 4096 |
| NoFT-Wide-290M | 1 | 32 | 11008 | 4096 |

NoFT-1.3B uses the configuration provided by the Sheared-LLaMa authors. NoFT-Wide-796M, 543M, and 290M keep the attention heads, intermediate size, and model dimension of LLaMa-7B, which is the widest configuration possible with the Sheared-LLaMa pruning scheme.[^yanDecodingSpeculativeDecoding2025]

## Papers using it

### Sheared LLaMA (proposes it)

[Sheared LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) reports the average over 11 downstream tasks (Table 2). The number in parentheses is the training token count:[^xiaShearedLLaMAAccelerating2024]

| Model | [HellaSwag](../datasets/hellaswag.md) (10) | [MMLU](../datasets/mmlu.md) (5) | Average |
|---|---|---|---|
| Sheared-LLaMA-1.3B (50B) | 60.7 | 25.7 | 51.0 |
| Sheared-LLaMA-2.7B (50B) | 70.8 | 26.4 | 56.7 |

- Sheared-LLaMA-2.7B needs 1/32 (3%) of the budget to reach on-par performance with OpenLLaMA-3B-v2.[^xiaShearedLLaMAAccelerating2024]
- Sheared-LLaMA-1.3B outperforms TinyLlama-1.1B, which was pre-trained on 3T tokens.[^xiaShearedLLaMAAccelerating2024]
- [GSM8K](../datasets/gsm8k.md) (8-shot) EM is 2.7 for Sheared-LLaMA-2.7B (Source) and 2.4 for Sheared-LLaMA-2.7B (Scaling). [HumanEval](../datasets/humaneval.md) Pass@1 is 3.7 and 4.9 (Table 13).[^xiaShearedLLaMAAccelerating2024]
- Against CoFiPruning with a 0.4B pruning budget (Table 4): targeted pruning has PPL 10.3 and 58 tokens/s at 1.3B, against 9.1 and 51 for CoFiPruning; at 2.7B, 7.7 and 43 against 7.0 and 37.[^xiaShearedLLaMAAccelerating2024]
- Against [LLM-Pruner](../methods/llm-pruner.md) (1.6B) at around 6B tokens (Table 12): Sheared-LLaMA (1.3B) has generation speed 58 tokens/s, training throughput 139K tokens/s, and PPL 6.85, against 43 tokens/s, 83K tokens/s, and 7.09.[^xiaShearedLLaMAAccelerating2024]
- Inference speed on an A100 GPU, generating up to 2048 tokens with a batch size of 1 (Table 16): Sheared-LLaMA 62 tokens/s at 1.3B and 47 at 2.7B; LLaMA-7B 37.[^xiaShearedLLaMAAccelerating2024]

### Decoding Speculative Decoding (uses the pruning scheme, and the released model as a baseline draft)

[Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md) chooses Sheared-LLaMa-1.3B as the reference draft model because it achieves the highest [speculative decoding](../methods/speculative-decoding.md) throughput among the existing models in its benchmark.[^yanDecodingSpeculativeDecoding2025] It then uses the pruning scheme to build wider, shallower drafts without the continued pre-training stage.[^yanDecodingSpeculativeDecoding2025]

Speculative decoding throughput in tokens/s with temperature sampling (Table 2). The Speedup row is NoFT-Wide-796M over Sheared-LLaMA-1.3B:[^yanDecodingSpeculativeDecoding2025]

| Draft Model | MMLU (T=1.0) | Hellaswag (T=1.0) | Chatbot Arena (T=1.0) | MMLU (T=0.5) | Hellaswag (T=0.5) | Chatbot Arena (T=0.5) |
|---|---|---|---|---|---|---|
| NoFT-Wide-796M | 24.32 | 24.32 | 24.18 | 29.64 | 26.91 | 25.76 |
| Sheared-LLaMA-1.3B | 12.06 | 12.30 | 11.45 | 14.60 | 13.45 | 12.66 |
| Speedup | 101.6% | 97.7% | 111.8% | 103.0% | 100.0% | 103.5% |

- NoFT-Wide-796M uses only $0.8\%$ of the training tokens of Sheared-LLaMA-1.3B.[^yanDecodingSpeculativeDecoding2025]
- With greedy decoding, NoFT-Wide-1.3B achieves up to $30\%$ higher speculative decoding throughput than Sheared-LLaMa-1.3B, and NoFT-Wide-796M up to 60$\%$ higher (from figures).[^yanDecodingSpeculativeDecoding2025]
- [KV cache](../methods/kv-cache.md) at context length 1024 is 192MB for Sheared-LLaMa-1.3B and 120MB for the wide 1.3B design. The Table 4 caption gives the reduction as $37\%$, and the body text as more than $37\%$.[^yanDecodingSpeculativeDecoding2025]
- Per-step autoregressive decoding latency at batch size 1 is 0.018 s for Sheared-LLaMA-1.3B and 0.0097 s for LLaMA-NoFT-Wide-1.3B (Table 5).[^yanDecodingSpeculativeDecoding2025]

### Compact Language Models via Pruning and Knowledge Distillation (baseline)

[Muralidharan et al.](../papers/muralidharanCompactLanguageModels2024.md) list Sheared LLaMa (2.7B parameters, 2.5B non-embedding) as a pruning baseline for Minitron 4B (4.2B parameters, 2.6B non-embedding) in Table 4:[^muralidharanCompactLanguageModels2024]

| Benchmark (shots) | Metric | Sheared LLaMa | Minitron 4B |
|---|---|---|---|
| winogrande (5) | acc | 64.2 | 74 |
| arc_challenge (25) | acc_norm | 41.2 | 50.9 |
| MMLU (5) | acc | 26.4 | 58.6 |
| hellaswag (10) | acc_norm | 70.8 | 75 |
| gsm8k (5) | acc | 23.96 | 24.1 |

The paper groups Sheared LLaMa with the width-pruning work that uses learnable masks combined with an Augmented Lagrangian loss formulation, and states that at LLM scale this strategy requires compute and memory-intensive gradient computations and a considerable amount of data and fine-tuning to arrive at reasonable masks.[^muralidharanCompactLanguageModels2024]

## Strengths & Limitations

- The pruned model has a pre-specified, uniform shape, which gives higher inference speed than the non-uniform CoFiPruning model at the same sparsity.[^xiaShearedLLaMAAccelerating2024]
- Targeted pruning has a slightly higher perplexity than CoFiPruning and needs about 0.5B more tokens in continued pre-training to match it.[^xiaShearedLLaMAAccelerating2024]
- The math ability of 3B models including Sheared-LLaMA is far below that of larger models, and Sheared-LLaMA's coding ability lags behind models trained on more code data.[^xiaShearedLLaMAAccelerating2024]
- As a speculative decoding draft, the released 1.3B configuration is deep (24 layers), and Yan et al. find that draft latency is bottlenecked by depth: the 12-layer NoFT-Wide-1.3B reduces draft latency by $49\%$ against NoFT-1.3B at a $3\%$ lower TAR.[^yanDecodingSpeculativeDecoding2025]
- The learnable-mask approach needs gradient computation, which Muralidharan et al. avoid with activation-based importance estimated from forward passes only.[^muralidharanCompactLanguageModels2024]

# Contradictions

**GSM8K score of Sheared-LLaMA-2.7B.**

- Xia et al. report GSM8K (8-shot) EM of 2.7 (source reference) and 2.4 (scaling reference) for Sheared-LLaMA-2.7B, and 13.7 for the source model LLaMA2-7B.[^xiaShearedLLaMAAccelerating2024]
- Muralidharan et al. list gsm8k (5-shot) acc of 23.96 for Sheared LLaMa (2.7B) in Table 4, and 14 for Llama-2 (6.7B) in Table 2.[^muralidharanCompactLanguageModels2024]

The settings differ in shot count (8 vs 5) and metric name (EM vs acc). The other four Sheared LLaMa values in Muralidharan et al.'s Table 4 (64.2, 41.2, 26.4, 70.8) equal the Sheared-LLaMA-2.7B values in Xia et al.'s Table 2 for WinoGrande, ARC-C, MMLU, and HellaSwag.[^xiaShearedLLaMAAccelerating2024][^muralidharanCompactLanguageModels2024] The 23.96 value is above both papers' scores for the unpruned LLaMA2-7B source model.[^xiaShearedLLaMAAccelerating2024][^muralidharanCompactLanguageModels2024] Muralidharan et al. do not state how the Sheared LLaMa column was obtained.

**Generation speed of Sheared-LLaMA-1.3B within Xia et al.** Table 12 gives 58 tokens/s for Sheared-LLaMA (1.3B) and 43 tokens/s for LLM-Pruner (1.6B), and the accompanying text says a single A100 GPU generating up to 2048 tokens. Table 16 gives 62 tokens/s for Sheared-LLaMA 1.3B and 41 for LLM Pruner 1.3B, on an A100 GPU generating up to 2048 tokens with a batch size of 1. Table 4 gives 58 for targeted pruning at 1.3B on an A100 (80G) generating up to 512 tokens.[^xiaShearedLLaMAAccelerating2024]

## Related

- [Structured pruning](../methods/structured-pruning.md), [LLM-Pruner](../methods/llm-pruner.md), [Knowledge distillation](../methods/knowledge-distillation.md)
- [Speculative decoding](../methods/speculative-decoding.md), [KV cache](../methods/kv-cache.md)
- Datasets: [RedPajama](../datasets/redpajama.md), [MMLU](../datasets/mmlu.md), [HellaSwag](../datasets/hellaswag.md), [GSM8K](../datasets/gsm8k.md), [HumanEval](../datasets/humaneval.md)

## Open questions and results

- [What is the GSM8K score of Sheared-LLaMA 2.7B?](../questions/sheared-llama-gsm8k-discrepancy.md)

[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
