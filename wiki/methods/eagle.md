---
type: Method
title: EAGLE
description: Speculative sampling method whose draft model performs autoregression at the feature level, reusing the target model's top-layer features and LM head; predecessor of EAGLE-2 and EAGLE-3.
tags: [speculative-decoding, draft-model, feature-level-autoregression, llm-inference]
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models
  - id: huAdaSPECSelectiveKnowledge2025
    resource: zotero://select/items/@huAdaSPECSelectiveKnowledge2025
    title: "AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders"
---

# EAGLE

## Overview

EAGLE is a [speculative decoding](../methods/speculative-decoding.md) method that performs autoregression at the feature level. It reuses the top-layer features of the target model (the features before the LM head), trains the draft model to predict the next feature autoregressively, and then uses the target model's LM head to obtain the draft token.[^liEAGLE3ScalingInference2025] The wiki has no Paper page for EAGLE itself. Everything here comes from papers that describe it or measure it as a baseline.

## How it works

- Vanilla speculative sampling uses a separate, smaller LLM as the draft model, which operates independently of the target. EAGLE instead leverages the target's top-layer features as additional information.[^liEAGLE3ScalingInference2025]
- Feature-level autoregression hides the sampling results at the token layer, which introduces uncertainty. EAGLE addresses this by feeding the token sequence from the previous time step into the draft model.[^liEAGLE3ScalingInference2025]
- EAGLE generates multiple draft tokens at the same position, which gives a tree-like draft, and verifies the draft tree in parallel with tree attention. The structure of the draft tree is predefined, static, and context-independent.[^liEAGLE3ScalingInference2025]
- The loss has two components: a feature prediction loss $l_{fea}$ and a token prediction loss $l_{token}$. The feature prediction loss lets a draft model trained only at Step 1 adapt to Step 2.[^liEAGLE3ScalingInference2025]
- SpecForge describes the draft model as a lightweight single-layer Transformer that autoregressively predicts future feature representations, which are projected through a linear layer to obtain the token logits. It places EAGLE as the third stage of draft model design, after independent draft models and [Medusa](../methods/medusa.md)-style heads.[^liSpecForgeFlexibleEfficient2026]
- SSD describes EAGLE as allowing the draft model to take as input the representations from the target model for the current prefix.[^kumarSpeculativeSpeculativeDecoding2026]

## Variants

- [EAGLE-2](../methods/eagle-2.md) replaces the static draft tree with a context-aware dynamic draft tree.[^liEAGLE3ScalingInference2025]
- [EAGLE-3](../methods/eagle-3.md) removes the feature prediction loss, predicts tokens directly, and fuses low-, mid-, and high-level target features.[^liEAGLE3ScalingInference2025]
- The EAGLE-3 paper lists HASS and Falcon as later methods that also predict the next feature from the current feature sequence.[^liEAGLE3ScalingInference2025]

## Papers using it

### EAGLE-3 paper (Li et al. 2025)

EAGLE is a baseline. Speedup over vanilla autoregressive decoding / average acceptance length $\tau$ on Vicuna 13B, using the officially released weights:[^liEAGLE3ScalingInference2025]

| Temp. | MT-bench | HumanEval | GSM8K | Alpaca | CNN/DM | Mean |
|---|---|---|---|---|---|---|
| 0 | 3.07x / 3.98 | 3.58x / 4.39 | 3.08x / 3.97 | 3.03x / 3.95 | 2.49x / 3.52 | 3.05x / 3.96 |
| 1 | 2.32x / 3.20 | 2.65x / 3.63 | 2.57x / 3.60 | 2.45x / 3.57 | 2.23x / 3.26 | 2.44x / 3.45 |

All rows: [^liEAGLE3ScalingInference2025]

Throughput improvement over the serving engine without speculative sampling, LLaMA-Instruct 3.1 8B on MT-Bench, chain draft (no tree). [SGLang](../methods/sglang.md) v0.4.4 on a single H100 with chain length 3, and [vLLM](../methods/vllm.md) with maximum chain length 2:[^liEAGLE3ScalingInference2025]

| Engine | 2 | 4 | 8 | 16 | 24 | 32 | 48 | 56 | 64 |
|---|---|---|---|---|---|---|---|---|---|
| SGLang | 1.40x | 1.38x | 1.23x | 1.02x | 0.93x | 0.94x | 0.88x | 0.99x | 0.99x |
| vLLM | 1.30x | 1.25x | 1.21x | 1.10x | 1.03x | 0.93x | 0.82x | 0.71x | not measured |

Columns are batch sizes. All rows: [^liEAGLE3ScalingInference2025]

- The paper observes that scaling up training data gives limited improvement for EAGLE, and attributes this to the feature prediction constraint.[^liEAGLE3ScalingInference2025]
- On MT-bench with LLaMA-Instruct 3.1 8B, EAGLE's acceptance rate drops significantly as more of the input comes from the draft model itself (figure only).[^liEAGLE3ScalingInference2025]
- The paper states that EAGLE inspired the multi-token prediction technique used in the pre-training of DeepSeek-v3 ([multi-token prediction](../methods/multi-token-prediction.md)).[^liEAGLE3ScalingInference2025]
- For the EAGLE baseline, the LLaMA3-Instruct draft model is trained on the [ShareGPT](../datasets/sharegpt.md) dataset.[^liEAGLE3ScalingInference2025]

### SuffixDecoding (Oliaro et al. 2024)

EAGLE is a baseline run through the Spec-Bench codebase with Llama-3.1-8B-Instruct on a single H100 GPU at batch size 1.[^oliaroSuffixDecodingExtremeSpeculative2024]

| Workload | Speedup over vanilla | Mean accepted tokens (tokens/step) | Time per output token (ms) | Speculation time per generated token (ms) | Mean acceptance rate |
|---|---|---|---|---|---|
| [Spec-Bench](../benchmarks/spec-bench.md) | 1.752 | 3.065 | 14.925 | 2.289 | 0.083 |
| AgenticSQL | 1.595 | 2.851 | 17.887 | 2.700 | 0.074 |

All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

### SDFP (Wei et al. 2026)

SDFP excludes EAGLE and Medusa from its comparison, because they require additional auxiliary networks or fine-tuning.[^weiSDFPSpeculativeDecoding2026]

### PARD (An et al. 2025)

Official EAGLE checkpoint on LLaMA3.1-8B, vLLM, A100-40GB: 136.05 tokens/s / 1.86 on HumanEval, 110.81 / 1.51 on GSM8K, and 100.11 / 1.38 on SpecBench. Acceptance rate at the first draft position is 0.83 on HumanEval and 0.79 on GSM8K.[^anPARDAcceleratingLLM2025] Speedup on HumanEval falls from 1.86 at batch size 1 to 1.19 at batch size 16.[^anPARDAcceleratingLLM2025]

### HAT (Xie et al. 2025)

HAT trains its on-device adapter with the EAGLE loss: Smooth L1 on the hidden state before the head plus cross-entropy, weighted $w_{ce}=0.1$.[^xieNovelHatShapedDeviceCloud2025]

### AdaSPEC (Hu et al. 2025)

[AdaSPEC](../methods/adaspec.md) applies its token-selective distillation inside the EAGLE recipe: Vicuna-7B-v1.3 target, 3 epochs on [ShareGPT](../datasets/sharegpt.md), evaluated on [MT-Bench](../datasets/mt-bench.md). Training first-token accuracy rises from 75.3% to 76.3%, time per sentence falls from 8.85 s to 8.06 s, and throughput rises from 63.48 to 68.21 tokens/s.[^huAdaSPECSelectiveKnowledge2025]

## Strengths & Limitations

- Strength: by using the target model's features, EAGLE achieves better acceleration than vanilla speculative sampling. On Vicuna 13B at temperature 0 its mean speedup is 3.05x against 1.92x for standard speculative sampling with a Vicuna-68M draft.[^liEAGLE3ScalingInference2025]
- Limitation: the feature prediction loss limits the expressiveness of the draft model and makes it difficult to benefit from more training data.[^liEAGLE3ScalingInference2025]
- Limitation: the static draft tree can waste resources, because the difficulty of drafting depends on the context.[^liEAGLE3ScalingInference2025]
- Limitation: under batching the gain disappears. In SGLang the improvement is below 1.00x from batch size 24 upward, and in vLLM from batch size 32 upward.[^liEAGLE3ScalingInference2025]
- Limitation: it needs a trained auxiliary network, which SDFP counts as limiting general applicability.[^weiSDFPSpeculativeDecoding2026]

Caveat on the numbers: the EAGLE-3 paper's EAGLE row is for Vicuna 13B, and SuffixDecoding's is for Llama-3.1-8B-Instruct on different workloads, so the two sets are not measurements of the same setting.[^liEAGLE3ScalingInference2025][^oliaroSuffixDecodingExtremeSpeculative2024]

## Related

- Successors: [EAGLE-2](../methods/eagle-2.md), [EAGLE-3](../methods/eagle-3.md)
- Parent concept: [Speculative decoding](../methods/speculative-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- Other drafters that reuse target features: [Medusa](../methods/medusa.md), [Multi-token prediction](../methods/multi-token-prediction.md)
- Benchmarks: [Spec-Bench](../benchmarks/spec-bench.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^huAdaSPECSelectiveKnowledge2025]: Hu et al. 2025
