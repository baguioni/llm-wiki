---
type: Method
title: Medusa
description: Speculative decoding approach that attaches extra decoding heads to the target model, which predict several draft tokens in parallel from the same hidden state without a separate draft model.
tags: [speculative-decoding, draft-heads, parallel-drafting, llm-inference, baseline]
sources:
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: gaoCollaborativeSpeculativeInference
    resource: zotero://select/items/@gaoCollaborativeSpeculativeInference
    title: Collaborative Speculative Inference for Efficient LLM Inference Serving
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# Medusa

## Overview

Medusa (written MEDUSA in some papers) attaches parallel decoding heads to the target model's final layer, which predict draft tokens independently from each other.[^samarinLKLossesDirect2026] It adds new sampling heads to the target LLM that produce the speculations without a speculative model.[^gaoCollaborativeSpeculativeInference] The wiki has no Paper page for Medusa itself. Everything here comes from papers that describe it, train it, or measure it as a baseline for [speculative decoding](../methods/speculative-decoding.md).

## How it works

- The heads are lightweight and run in parallel with the standard LM head. Generating candidate tokens costs nearly the same walltime as generating one, because the additional MLPs are small and executed concurrently with the backbone.[^liSpecForgeFlexibleEfficient2026]
- The heads reuse the target model's features, which avoids a separate KV-cache.[^liSpecForgeFlexibleEfficient2026] The features are the top-layer features, immediately before the LM head.[^liEAGLE3ScalingInference2025]
- Each head is an MLP layer. The heads predict all positions in parallel from the same hidden state without token-level autoregression, and each speculative position has its own fully independent head.[^samarinLKLossesDirect2026]
- Verification is performed in a single forward pass with tree attention, where a masked attention structure constrains each candidate token to attend only to its ancestors.[^liSpecForgeFlexibleEfficient2026] The draft tree is predefined, static, and context-independent.[^liEAGLE3ScalingInference2025]
- For training, Medusa suggests mixing the KL loss with the LM objective for the target model, to address the discrepancy between its distribution and static training data.[^samarinLKLossesDirect2026]
- Under non-greedy settings Medusa relaxes the acceptance conditions, which does not guarantee lossless acceleration.[^liEAGLE3ScalingInference2025]

## Variants

- Hydra is a baseline in the EAGLE-3 paper, listed with Medusa among the methods that reuse the features of the target model.[^liEAGLE3ScalingInference2025]
- The multi-stage MLP speculator of Wertheimer et al. extends MEDUSA heads with the principles from recurrent networks.[^samarinLKLossesDirect2026]
- SpecForge calls Medusa's approach "multi-token prediction heads" and places it as the second stage of draft model design, between independent draft models and [EAGLE](../methods/eagle.md).[^liSpecForgeFlexibleEfficient2026] The native module of DeepSeek-V3 is covered under [multi-token prediction](../methods/multi-token-prediction.md).
- DSpark lists Medusa with P-EAGLE, PARD, DART, and [DFlash](../methods/dflash.md) as parallel or blockwise generation methods that remove the sequential bottleneck of drafting.[^chengDSparkConfidenceScheduledSpeculative2026]

## Papers using it

### EAGLE-3 paper (Li et al. 2025)

Medusa is a baseline with default settings and the officially released weights. Vicuna 13B, temperature 0, speedup over vanilla autoregressive decoding / average acceptance length $\tau$. It is not compared at temperature 1, because of the relaxed acceptance conditions.[^liEAGLE3ScalingInference2025]

| Method | MT-bench | HumanEval | GSM8K | Alpaca | CNN/DM | Mean |
|---|---|---|---|---|---|---|
| Medusa | 2.07x / 2.59 | 2.50x / 2.78 | 2.23x / 2.64 | 2.08x / 2.45 | 1.71x / 2.09 | 2.12x / 2.51 |
| Hydra | 2.88x / 3.65 | 3.28x / 3.87 | 2.93x / 3.66 | 2.86x / 3.53 | 2.05x / 2.81 | 2.80x / 3.50 |
| EAGLE | 3.07x / 3.98 | 3.58x / 4.39 | 3.08x / 3.97 | 3.03x / 3.95 | 2.49x / 3.52 | 3.05x / 3.96 |
| EAGLE-3 | 5.58x / 6.65 | 6.47x / 7.54 | 5.32x / 6.29 | 5.16x / 6.17 | 5.01x / 6.47 | 5.51x / 6.62 |

All rows: [^liEAGLE3ScalingInference2025]

### LK losses (Samarin et al. 2026)

The authors train MEDUSA heads from scratch for Llama-3.1-8B-Instruct with $K=6$ heads, and compare KL training with their LK losses. MEDUSA uses $\eta=10$ because its acceptance rates improve slower during training than those of recurrent architectures. Evaluation uses chain sampling in [vLLM](../methods/vllm.md). Values are average acceptance length $\tau$.[^samarinLKLossesDirect2026]

| Loss | T=0 MT-Bench | T=0 HumanEval | T=0 GSM8K | T=1 MT-Bench | T=1 HumanEval | T=1 GSM8K |
|---|---|---|---|---|---|---|
| KL | 2.05 | 2.41 | 2.11 | 1.72 | 2.02 | 1.81 |
| $\mathcal{L}_{\text{LK}}^{\alpha}$ | 2.06 | 2.42 | 2.11 | 1.78 | 2.09 | 1.85 |
| $\mathcal{L}_{\text{LK}}^{\lambda},\eta=10$ | 2.07 | 2.44 | 2.13 | 1.85 | 2.22 | 1.92 |

All rows: [^samarinLKLossesDirect2026]

- With stochastic sampling, MEDUSA shows an average improvement of $7.8\%$ across domains from the LK loss, against $3.8\%$ for [EAGLE-3](../methods/eagle-3.md). The authors read this as low-capacity draft models benefiting more from direct optimization of the acceptance rate.[^samarinLKLossesDirect2026]
- In the same table, an EAGLE-3 head trained with KL has $\tau$ of 3.75, 4.82, and 4.50 at $T=0$ on MT-Bench, HumanEval, and GSM8K.[^samarinLKLossesDirect2026]
- MEDUSA is evaluated with $K=6$ because weights are not shared between decoding heads, so generation cannot be extended to longer drafts.[^samarinLKLossesDirect2026]

### CoSine (Gao et al.) and SDFP (Wei et al. 2026)

- CoSine discusses Medusa as a self-speculation method in related work and does not benchmark it.[^gaoCollaborativeSpeculativeInference]
- SDFP excludes Medusa and EAGLE from its comparison, because they require additional auxiliary networks or fine-tuning.[^weiSDFPSpeculativeDecoding2026]

### HAT (Xie et al. 2025)

- [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md) runs Medusa inside U-shaped device-cloud inference as the U-Medusa baseline: 4 heads on the device with the input and output submodels, and tree verification of size 8. The heads are trained on ShareGPT.[^xieNovelHatShapedDeviceCloud2025]
- With speculative decoding alone on one device, U-Medusa has 591M trained parameters, an accept length of 1.89, and a 1.41× speedup over U-shape on SpecBench (Vicuna-7B), against 67M, 2.06, and 1.65× for HAT. On CNN/DM (Vicuna-13B) the values are 760M, 1.75, and 1.45× against 105M, 1.98, and 1.60×.[^xieNovelHatShapedDeviceCloud2025]
- As the request rate rises from 4 to 9 requests/s on SpecBench, U-Medusa's TBT rises by 64.5%, which the paper attributes to tree verification overloading the server.[^xieNovelHatShapedDeviceCloud2025]

### PARD (An et al. 2025)

PARD classes Medusa as target-dependent, because it feeds target features into the drafter, so a separate drafter must be trained for every target.[^anPARDAcceleratingLLM2025]

### HyCo ([HyCo](../papers/baeHyCoHybridDrafting2026.md))

HyCo describes Medusa's typical acceptance as testing the target's raw softmax against an entropy-adaptive threshold taken from $\eta$-sampling, a lossy acceptance rule. On HyCo's hybrid tree on UC-val, typical acceptance at its defaults falls below the lossless judge-score range (58.7–63.0), and HyCo uses its own $\epsilon$-threshold rule instead. See [Lossy acceptance rules](lossy-acceptance.md).[^baeHyCoHybridDrafting2026]

## Strengths & Limitations

- Strength: no independent draft model and no second KV-cache.[^liSpecForgeFlexibleEfficient2026]
- Limitation: its non-autoregressive MLP heads struggle to capture long-range dependencies.[^liSpecForgeFlexibleEfficient2026]
- Limitation: the heads need training, and the draft length is fixed by the number of heads.[^samarinLKLossesDirect2026]
- Limitation: acceptance is lower than for feature-level autoregressive drafters in both papers that measure it (mean $\tau$ 2.51 vs 3.96 for EAGLE on Vicuna 13B; 2.05 vs 3.75 for a KL-trained EAGLE-3 head on Llama-3.1-8B MT-Bench).[^liEAGLE3ScalingInference2025][^samarinLKLossesDirect2026]
- Limitation: not lossless under non-greedy decoding with its relaxed acceptance conditions.[^liEAGLE3ScalingInference2025]

Caveat on the numbers: the two sets of Medusa measurements use different targets (Vicuna 13B vs Llama-3.1-8B-Instruct), different weights (officially released vs trained from scratch by the LK losses authors), and different drafts (tree vs chain), so they are not measurements of the same setting.[^liEAGLE3ScalingInference2025][^samarinLKLossesDirect2026]

# Contradictions

**Does Medusa need training?** CoSine's related-work section first says that self-speculation methods like lookahead decoding and Medusa work "without requiring additional fine-tuning or draft models", and two sentences later says that Medusa requires training new sampling heads for the target LLM.[^gaoCollaborativeSpeculativeInference] SDFP states that Medusa requires additional auxiliary networks or fine-tuning.[^weiSDFPSpeculativeDecoding2026] LK losses trains the MEDUSA heads from scratch for 10 epochs.[^samarinLKLossesDirect2026] The first CoSine statement conflicts with the other three. The likely reading is that it refers to the absence of a separate draft model, not to the absence of training.

## Related

- [Lossy acceptance rules](lossy-acceptance.md) (typical acceptance), [HyCo](hyco.md)

- Parent concept: [Speculative decoding](../methods/speculative-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- Other drafters that reuse target features: [EAGLE](../methods/eagle.md), [EAGLE-2](../methods/eagle-2.md), [EAGLE-3](../methods/eagle-3.md), [Multi-token prediction](../methods/multi-token-prediction.md)
- Parallel drafters: [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md)
- Datasets: [MT-Bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md)

[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^gaoCollaborativeSpeculativeInference]: Gao et al. (year not stated)
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
