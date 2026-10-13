---
type: Open Question
title: Why do reported EAGLE-3 numbers differ so much between papers?
description: EAGLE-3 speedup and acceptance length for the same target model differ widely across the papers that re-measure it.
tags: [speculative-decoding, eagle-3, reproducibility]
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
---

# Why do reported EAGLE-3 numbers differ so much between papers?

## Question

The same drafter, EAGLE-3, is reported with very different speedup and acceptance length (τ) for the same target model. Which numbers are the fair baseline?

## Why it matters

Most newer drafters in this wiki ([DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), LK losses, Learning to Draft, DPara) state their gain relative to [EAGLE-3](../methods/eagle-3.md). The size of the gain depends on which EAGLE-3 number is used.

## Evidence so far

LLaMA-3.1-8B, temperature 0, GSM8K:

| Reported by | Speedup | τ | Setting stated |
|---|---|---|---|
| [EAGLE-3 paper](../papers/liEAGLE3ScalingInference2025.md) | 4.48x | 6.23 | tree drafting[^liEAGLE3ScalingInference2025] |
| [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md) | 3.58 | 6.44 | official weights[^zhangLearningDraftAdaptive2026] |
| [LK losses](../papers/samarinLKLossesDirect2026.md) | 2.65 | 3.84 | public checkpoint, chain drafting, vLLM[^samarinLKLossesDirect2026] |

Qwen3-8B, GSM8K, temperature 1, τ only:

| Reported by | EAGLE-3 τ | Setting stated |
|---|---|---|
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | 3.12 | AngelSlim checkpoint, tree drafting[^chenDFlashBlockDiffusion2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | 5.30 | retrained, chain drafting[^chengDSparkConfidenceScheduledSpeculative2026] |

## Conflicting claims

- The DFlash paper reports its drafter far ahead of EAGLE-3 on Qwen3-8B (τ 5.98 against 3.12 on GSM8K at temperature 1).[^chenDFlashBlockDiffusion2026]
- The DSpark paper retrains EAGLE-3 and measures τ 5.30 against 5.33 for DFlash in the same column.[^chengDSparkConfidenceScheduledSpeculative2026]

See the Contradictions section of [EAGLE-3](../methods/eagle-3.md) for the full set of values.

## What would resolve it

One run of EAGLE-3 per target model with the checkpoint, drafting mode (tree or chain), draft-token budget, serving stack, and hardware all stated, and the same settings used for the competing drafter.

## Related

- [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [Speculative decoding](../methods/speculative-decoding.md)
- [GSM8K](../datasets/gsm8k.md)
- [Does speculative decoding still help at large batch sizes?](speculative-decoding-at-large-batch.md)
- [DFlash, DSpark, and EAGLE-3: how they draft and what they report on Qwen3-8B](../analyses/dflash-dspark-eagle-3-drafting-comparison.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
