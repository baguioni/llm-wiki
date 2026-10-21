---
type: Method
title: Structured Pruning
description: Model compression that removes whole groups of parameters (layers, attention heads, neurons, embedding channels) so that the result is a smaller dense model, usually followed by retraining.
tags: [structured-pruning, model-compression, small-language-models, draft-model]
sources:
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# Structured Pruning

## Overview

Structured pruning removes groups of model parameters to compress models and accelerate inference.[^xiaShearedLLaMAAccelerating2024] Muralidharan et al. define it as pruning where blocks of nonzero elements are removed at once from model weights, with neuron, attention head, convolutional filter, and depth pruning as examples.[^muralidharanCompactLanguageModels2024]

Unstructured pruning, in contrast, prunes individual neurons instead of structured blocks. It usually achieves higher compression rates but is not practical for model speedup.[^xiaShearedLLaMAAccelerating2024] Wanda-type semi-structured pruning gives an inference speedup over the source model, but is not as fast as small dense models, and the speedup is only feasible when the sparsity is at $50\%$.[^xiaShearedLLaMAAccelerating2024]

## How it works

Two steps recur across the papers: decide what to remove, then retrain.

- **Deciding what to remove.**
  - *Learned masks.* [Sheared-LLaMA](../methods/sheared-llama.md) learns masking variables at four granularities (layers, hidden dimensions, attention heads, intermediate dimensions) and constrains the pruned model to a pre-specified target shape.[^xiaShearedLLaMAAccelerating2024]
  - *Activation-based importance.* Muralidharan et al. compute importance for all axes (depth, neuron, head, embedding channel) with a small calibration dataset of 1024 samples and only forward propagation passes, rank the elements of each axis, and trim the corresponding weight matrices directly.[^muralidharanCompactLanguageModels2024]
  - *Depth metrics.* For layers, Muralidharan et al. use perplexity (PPL) and Block Importance (BI).[^muralidharanCompactLanguageModels2024]
- **Retraining.** Pruning is often accompanied by retraining for accuracy recovery, a phase that is extremely expensive in modern LLMs.[^muralidharanCompactLanguageModels2024] Sheared-LLaMA continues pre-training with a language modeling objective on 50 billion tokens.[^xiaShearedLLaMAAccelerating2024] Muralidharan et al. retrain with [knowledge distillation](../methods/knowledge-distillation.md) from the unpruned model.[^muralidharanCompactLanguageModels2024]

## Variants

- **Depth pruning vs width pruning.** Muralidharan et al. classify structured LLM pruning work into methods that prune only depth (layers) and methods that prune width (attention heads, MLP intermediate dimension, etc.) and/or depth.[^muralidharanCompactLanguageModels2024]
- **Target-shape pruning.** Sheared-LLaMA's targeted structured pruning prunes to a specified target architecture taken from existing pre-trained models.[^xiaShearedLLaMAAccelerating2024]
- **Non-uniform pruning.** CoFiPruning produces models with non-uniform layer configurations (e.g., different numbers of heads across layers), which incurs inference overhead compared to uniform layer configurations.[^xiaShearedLLaMAAccelerating2024]
- **[LLM-Pruner](../methods/llm-pruner.md).** A structured pruning method used as a baseline by both Xia et al. and Muralidharan et al.[^xiaShearedLLaMAAccelerating2024][^muralidharanCompactLanguageModels2024]
- **Pruning plus architecture search.** Muralidharan et al. enumerate the feasible architectures that meet a parameter budget and apply lightweight retraining ($\sim$1.8B tokens) to stabilize candidate rankings.[^muralidharanCompactLanguageModels2024]
- **Wide, shallow drafts.** Yan et al. use the Sheared-LLaMa pruning scheme to build [speculative decoding](../methods/speculative-decoding.md) draft models that trade depth for width.[^yanDecodingSpeculativeDecoding2025]

## Papers using it

- [Sheared LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) prunes LLaMA2-7B to 1.3B and 2.7B parameters with 0.4 billion tokens for pruning and 50 billion tokens for continued pre-training on [RedPajama](../datasets/redpajama.md).[^xiaShearedLLaMAAccelerating2024] Sheared-LLaMA-2.7B needs 1/32 (3%) of the budget to reach on-par performance with OpenLLaMA-3B-v2.[^xiaShearedLLaMAAccelerating2024] Against CoFiPruning at the same sparsity, targeted pruning is faster (58 vs 51 tokens/s at 1.3B, 43 vs 37 at 2.7B) with higher perplexity (10.3 vs 9.1, 7.7 vs 7.0).[^xiaShearedLLaMAAccelerating2024]
- [Compact Language Models via Pruning and Knowledge Distillation](../papers/muralidharanCompactLanguageModels2024.md) prunes Nemotron-4 15B along four axes (neurons in feed-forward layers, attention heads, embedding channels, and model depth) to produce Minitron 8B and 4B, which need up to 40$\times$ fewer training tokens than training from scratch.[^muralidharanCompactLanguageModels2024]
  - Pruning Nemotron-4 15B to the Nemotron-3 8B size, after retraining with 1.8B tokens (Table 10):[^muralidharanCompactLanguageModels2024]

    | Model | Parameters | LM Loss |
    |---|---|---|
    | Minitron 8B Depth (PPL) | 9.39B | 2.155 |
    | Minitron 8B Depth (BI) | 9.39B | 2.177 |
    | Minitron 8B Width | 7.74B | 2.049 |
    | Minitron 8B Depth + Width | 7.91B | 2.062 |

  - Width pruning outperforms depth, but only after retraining.[^muralidharanCompactLanguageModels2024]
  - Best practices include: prefer width pruning over depth for the model scales considered ($\leq$ 15B); use single-shot importance estimation, since iterative provides no benefit; prune a model closest to the target size.[^muralidharanCompactLanguageModels2024]
  - Two-step pruning (15B to 8B, then 8B to 4B) achieves a 12% improvement in [MMLU](../datasets/mmlu.md) scores compared to the one-shot strategy.[^muralidharanCompactLanguageModels2024]
  - Against other pruned models at the 4B target (Table 4), Minitron 4B scores 58.6 on MMLU (5), against 23.33 for LLMPruner, 28.92 for SliceGPT, 26.45 for LaCo, 43.96 for ShortGPT, and 26.4 for Sheared LLaMa.[^muralidharanCompactLanguageModels2024]
- [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md) prunes LLaMa-7B with Sheared-LLaMa using 0.4B tokens from RedPajama and skips the fine-tuning step on 50B more tokens.[^yanDecodingSpeculativeDecoding2025]
  - At 1.3B parameters on MMLU, the 12-layer NoFT-Wide-1.3B has TAR 3.70, latency 6.69 ms, and throughput 32.59 tokens/s, against TAR 3.81, 13.13 ms, and 23.10 tokens/s for the 24-layer NoFT-1.3B.[^yanDecodingSpeculativeDecoding2025]
  - The 5-layer NoFT-Wide-796M achieves $97.7\%$ to $111.8\%$ higher throughput than Sheared-LLaMA-1.3B with temperature sampling.[^yanDecodingSpeculativeDecoding2025]
  - Below 5 layers the draft's alignment capability drops dramatically.[^yanDecodingSpeculativeDecoding2025]
  - For LLaMa-3, pruning layers had a larger impact on TAR, and the pruned Wide-829M draft is distilled over 1 million tokens to recover it.[^yanDecodingSpeculativeDecoding2025]
- [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) prunes a pretrained small LM by depth to build a drafter body: Qwen3-4B keeps 2 of its blocks and LayerSkip-Llama3.2-1B keeps 4, with the embedding, LM head, and final norm. The pruned model is then pretrained on FineWeb before per-target adaptation.[^bieOspreyTargetagnosticPretraining2026]
- My experiment [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md) prunes Qwen3-14B in one Minitron step, by depth and width together, to the Qwen3-0.6B shape (28 of 40 layers, hidden 1024 of 5120, 16 of 40 query heads, FFN 3,072 of 17,408), keeping 5.1% of the parameters.[^minitron-pard-qwen3-14b]
  - Depth importance is the LM-loss increase when a layer is replaced by the identity. Layer 0 dominates (9.37 nats), then layer 6 (0.97) and layer 39 (0.54); the 12 dropped layers cost 0.022–0.033 nats each.[^minitron-pard-qwen3-14b]
  - Zero-shot, the pruned model's SlimPajama validation loss is 9.60 nats/token against 1.907 for Qwen3-14B, and as a draft it has top-1 0.038 and MAT 1.04 on Spec-Bench. After forward-KL recovery on 57M tokens of the target's answers it reaches top-1 0.572 and MAT 2.17 at γ=5.[^minitron-pard-qwen3-14b]
  - The pruning step took 64 min on a DGX Spark GB10.[^minitron-pard-qwen3-14b]

## Strengths & Limitations

- Structured pruning yields a compact, dense model, which gives inference speedup.[^xiaShearedLLaMAAccelerating2024]
- For general-purpose LLMs, pruning results in performance degradation compared to the original models, especially without significant compute invested after pruning.[^xiaShearedLLaMAAccelerating2024]
- Existing structured pruning approaches often result in unconventional model configurations that deviate from popular architectures.[^xiaShearedLLaMAAccelerating2024]
- Muralidharan et al. state that learnable-mask methods with an Augmented Lagrangian loss require compute and memory-intensive gradient computations and a considerable amount of data and fine-tuning to arrive at reasonable masks.[^muralidharanCompactLanguageModels2024] Xia et al. report that their mask-learning pruning stage is roughly 5$\times$ slower than standard LM training, that the masks converge fast, and that they spend 0.4 billion tokens on it.[^xiaShearedLLaMAAccelerating2024]
- **Depth vs width depends on the goal.** Muralidharan et al. prefer width pruning over depth pruning, judged by LM loss and downstream accuracy at scales $\leq$ 15B.[^muralidharanCompactLanguageModels2024] Yan et al. remove depth and keep width, judged by speculative decoding throughput, because draft latency scales with depth and not with width.[^yanDecodingSpeculativeDecoding2025] The two criteria are different, so the recommendations do not conflict.

# Contradictions

**Retraining objective after pruning.** Sheared LLaMA states that distilling from a teacher is less cost-effective than pruning and continued training because of the teacher's inference cost, and it continues pre-training with a language modeling objective.[^xiaShearedLLaMAAccelerating2024] Muralidharan et al. measure, under iso-compute settings, that retraining a pruned 4B model with distillation scores 37.81 on MMLU at 100B tokens against 24.57 for conventional training at 150B tokens, and recommend retraining exclusively with distillation loss.[^muralidharanCompactLanguageModels2024] The Sheared LLaMA statement rests on cited prior work and concerns distillation as a pre-training approach; the Muralidharan et al. result compares two retraining objectives on the same pruned model. Details are on the [knowledge distillation](../methods/knowledge-distillation.md) page.

## Related

- [Target-aware recovery of compressed drafters](../analyses/target-aware-recovery-of-compressed-drafters.md)
- [Does recovering a pruned drafter against the target beat recovering it against its parent?](../questions/target-aware-recovery-of-pruned-drafters.md)
- [Does choosing what to prune by target agreement beat LM-loss importance?](../questions/target-agreement-pruning-criteria.md)
- [Building a parallel drafter for on-device use without training it from scratch](../analyses/building-parallel-drafters-for-on-device-use.md)
- [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md), [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)
- [Sheared-LLaMA](../methods/sheared-llama.md), [LLM-Pruner](../methods/llm-pruner.md)
- [Knowledge distillation](../methods/knowledge-distillation.md)
- [Speculative decoding](../methods/speculative-decoding.md)
- Datasets: [RedPajama](../datasets/redpajama.md), [MMLU](../datasets/mmlu.md)

[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
