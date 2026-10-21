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
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: wangLeverSpeculativeLLM2026a
    resource: zotero://select/items/@wangLeverSpeculativeLLM2026a
    title: "Lever: Speculative LLM Inference on Smartphones"
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
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
| [PARD](../papers/anPARDAcceleratingLLM2025.md) | 2.62 | not reported | official checkpoint, vLLM, A100-40GB, temperature not stated[^anPARDAcceleratingLLM2025] |
| [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md) | 2.80 | 3.97 | official checkpoint, chain of 8, no tree, vLLM, A100-40GB[^anPARD2TargetAlignedParallel2026] |

Qwen3-8B, GSM8K, temperature 1, τ only:

| Reported by | EAGLE-3 τ | Setting stated |
|---|---|---|
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | 3.12 | AngelSlim checkpoint, tree drafting[^chenDFlashBlockDiffusion2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | 5.30 | retrained, chain drafting[^chengDSparkConfidenceScheduledSpeculative2026] |

Qwen3-8B at temperature 0, two more measurements:

- PARD-2 measures the AngelSlim checkpoint as a chain of 8 on vLLM at 1.98 / 2.44 on GSM8K (speedup / $\tau$) and 1.93 / 2.37 on average.[^anPARD2TargetAlignedParallel2026]
- Osprey trains a 1-layer EAGLE-3 from scratch for each of five domains, and measures it in SGLang with 6 draft tokens. The mean AL over the 25 train-evaluate pairs is 3.176, and the math-trained drafter reaches 5.058 on math.[^bieOspreyTargetagnosticPretraining2026]

Qwen3-8B, throughput only: I-DLM runs the third-party `Tengyunw/qwen3_8b_eagle3` draft in SGLang on one H100 with steps=3, topk=1 (a chain of 3 speculations) at temperature 1, and measures 238 tok/s per request on MATH-500 at concurrency 1, against 341 for I-DLM-8B. It reports no speedup over autoregressive decoding and no τ for EAGLE-3.[^yuIntrospectiveDiffusionLanguage2026]

LLaMA-3.3-70B-Instruct: Osprey measures the official checkpoint at a mean AL of 2.33 against 2.45 for its own reproduction, and on math at 2.47 against 3.41.[^bieOspreyTargetagnosticPretraining2026] So the official checkpoint is not always the strongest version of EAGLE-3.

## Conflicting claims

- The DFlash paper reports its drafter far ahead of EAGLE-3 on Qwen3-8B (τ 5.98 against 3.12 on GSM8K at temperature 1).[^chenDFlashBlockDiffusion2026]
- The DSpark paper retrains EAGLE-3 and measures τ 5.30 against 5.33 for DFlash in the same column.[^chengDSparkConfidenceScheduledSpeculative2026]
- The PARD-2 paper measures EAGLE-3 at τ 2.44 on Qwen3-8B GSM8K at temperature 0, against 5.39 for DFlash and 7.68 for PARD-2.[^anPARD2TargetAlignedParallel2026] With the AngelSlim checkpoint as a chain, this is the lowest EAGLE-3 value in the wiki for this cell.

- On phones the order of EAGLE-3 and a Qwen3-0.6B draft flips between setups. Lever measures its EAGLE3 draft at 1.206 tokens/s against 0.840 for Qwen3-0.6B (8-token chain, flash-resident Qwen3-8B verified on the phone).[^wangLeverSpeculativeLLM2026a] [My drafter evaluation](../experiments/drafter-evaluation-qwen3-14b.md) measures the DeepSpec ttt7 EAGLE-3 checkpoint at 13.0 tok/s against 15.6 for Qwen3-0.6B (chain of 7, Qwen3-14B-FP8 verified on a server).[^drafter-evaluation] With both drafting on the server GPU instead, the order holds: 17.2 against 20.4 tok/s.[^drafter-evaluation-server-only-chain]

See the Contradictions section of [EAGLE-3](../methods/eagle-3.md) for the full set of values.

## What would resolve it

One run of EAGLE-3 per target model with the checkpoint, drafting mode (tree or chain), draft-token budget, serving stack, and hardware all stated, and the same settings used for the competing drafter.

## Related

- [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [PARD](../methods/pard.md), [Osprey](../methods/osprey.md), [Speculative decoding](../methods/speculative-decoding.md)
- [GSM8K](../datasets/gsm8k.md)
- [Does speculative decoding still help at large batch sizes?](speculative-decoding-at-large-batch.md)
- [DFlash, DSpark, and EAGLE-3: how they draft and what they report on Qwen3-8B](../analyses/dflash-dspark-eagle-3-drafting-comparison.md)
- [I-DLM-8B outpaces EAGLE-3 in per-request throughput on Qwen3-8B](../results/i-dlm-vs-eagle-3-throughput.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^wangLeverSpeculativeLLM2026a]: Wang et al. 2026
[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
