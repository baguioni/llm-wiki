---
type: Analysis
title: "DFlash, DSpark, and EAGLE-3: how they draft and what they report on Qwen3-8B"
description: Comparison of the drafting mechanism of EAGLE-3, DFlash, and DSpark, with every speedup and acceptance length reported for Qwen3-8B and the settings behind each number.
tags: [speculative-decoding, eagle-3, dflash, dspark, qwen3, comparison]
question: How do DFlash, DSpark, and EAGLE-3 differ in how they draft tokens, and what speedup does each report on Qwen3-8B?
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
---

# DFlash, DSpark, and EAGLE-3: how they draft and what they report on Qwen3-8B

## Question

How do [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), and [EAGLE-3](../methods/eagle-3.md) differ in how they draft tokens, and what speedup does each report on Qwen3-8B?

## Answer

The three drafters differ in how many forward passes a draft block costs and in whether a draft token depends on the draft tokens before it.

| | EAGLE-3 | DFlash | DSpark |
|---|---|---|---|
| Drafting style | Autoregressive: draft tokens are generated step by step, and each later step takes the draft model's own previous output as input[^liEAGLE3ScalingInference2025] | Parallel: all masked positions of a block are decoded in a single forward pass[^chenDFlashBlockDiffusion2026] | Semi-autoregressive: a parallel backbone pass, then a lightweight sequential head that samples left to right[^chengDSparkConfidenceScheduledSpeculative2026] |
| Drafter | A single layer decoder[^liEAGLE3ScalingInference2025] | A block diffusion model with 5 draft layers by default[^chenDFlashBlockDiffusion2026] | DFlash backbone plus a Markov or RNN head[^chengDSparkConfidenceScheduledSpeculative2026] |
| Use of target features | Low-, mid-, and high-level features are fused and concatenated with the token embedding at the input[^liEAGLE3ScalingInference2025] | The fused feature is injected into the Key and Value projections of every draft layer ([KV injection](../methods/kv-injection.md))[^chenDFlashBlockDiffusion2026] | Uses DFlash as its parallel backbone[^chengDSparkConfidenceScheduledSpeculative2026] |
| Dependency between draft tokens | Yes: the draft model's own output from the previous step is fed back[^liEAGLE3ScalingInference2025] | No: each position is predicted independently, so acceptance decays at later positions[^chengDSparkConfidenceScheduledSpeculative2026] | Yes: a prefix-dependent transition bias is added to the base logits[^chengDSparkConfidenceScheduledSpeculative2026] |
| Draft structure | Context-aware dynamic draft tree, depth 8[^liEAGLE3ScalingInference2025] | One block, size 16 by default[^chenDFlashBlockDiffusion2026] | One block, size 7 in the paper's experiments[^chengDSparkConfidenceScheduledSpeculative2026] |
| Extra component | [Training-time test](../methods/training-time-test.md) during training[^liEAGLE3ScalingInference2025] | none | Confidence head and load-aware scheduler that set the verification length per request[^chengDSparkConfidenceScheduledSpeculative2026] |

Cost consequence, as the DFlash paper states it: an autoregressive drafter pays one step per draft token, while a diffusion drafter pays one parallel pass that is largely insensitive to the block length, so the drafter can be deeper.[^chenDFlashBlockDiffusion2026]

### Reported numbers on Qwen3-8B

No single paper measures all three under one setting with wall-clock speedup, except the DPara paper. The EAGLE-3 paper itself does not evaluate on Qwen3; every EAGLE-3 number below is a re-measurement by another paper.

Average over each paper's benchmark set. Cells are speedup over autoregressive decoding / acceptance length τ.

| Reported by | Setting | EAGLE-3 | DFlash | DSpark |
|---|---|---|---|---|
| [DFlash paper](../papers/chenDFlashBlockDiffusion2026.md) | temperature 0, DFlash block size 16, H200, 2048 tokens | 1.76× / 2.96 (tree 16), 2.02× / 3.40 (tree 60) | 4.86× / 6.49 | not measured |
| [DFlash paper](../papers/chenDFlashBlockDiffusion2026.md) | temperature 1, same | 1.68× / 2.83 (tree 16), 1.88× / 3.26 (tree 60) | 4.03× / 5.48 | not measured |
| [DPara paper](../papers/liuWhenParallelDrafter2026.md) | greedy, draft length 7, batch size 1, H800, 512 tokens | 1.44× / 2.87 | 2.70× / 4.85 | 2.89× / 5.36 |
| [DPara paper](../papers/liuWhenParallelDrafter2026.md) | temperature 1.0, same | not measured | 2.23× / 4.31 | 2.54× / 5.05 |

Rows 1-2: [^chenDFlashBlockDiffusion2026] Rows 3-4: [^liuWhenParallelDrafter2026]

GSM8K only, temperature 1.0, block size 7, τ only (the DSpark paper reports no offline wall-clock speedup):

| Reported by | EAGLE-3 | DFlash | DSpark |
|---|---|---|---|
| [DSpark paper](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | 5.30 | 5.33 | 6.17 |

Row: [^chengDSparkConfidenceScheduledSpeculative2026]

The DSpark paper summarizes its Qwen3-8B macro-average gain in accepted length as 26.7% over Eagle3 and 18.4% over DFlash.[^chengDSparkConfidenceScheduledSpeculative2026]

## Evidence

- The ordering DSpark > DFlash > EAGLE-3 on Qwen3-8B holds in every row above.
- The size of the gap depends on the EAGLE-3 checkpoint. With the AngelSlim checkpoints and tree drafting, EAGLE-3 has τ near 3 and DFlash is more than twice as fast.[^chenDFlashBlockDiffusion2026] With all drafters retrained on the same data and chain drafting, Eagle3 reaches τ 5.30 against 5.33 for DFlash on GSM8K.[^chengDSparkConfidenceScheduledSpeculative2026]
- The DFlash headline speedup depends on block size and generation length: 4.86× at block size 16 in its own paper, 2.70× at draft length 7 in the DPara paper.[^chenDFlashBlockDiffusion2026][^liuWhenParallelDrafter2026]

## Caveats

- The DSpark paper's offline numbers are accepted length only, with its confidence scheduler disabled.[^chengDSparkConfidenceScheduledSpeculative2026] Its speedups on Qwen3-8B come only from the DPara paper.[^liuWhenParallelDrafter2026]
- The DPara paper does not state which DFlash checkpoint its baseline rows use.[^liuWhenParallelDrafter2026]
- The rows use different hardware, generation lengths, and benchmark sets, so compare within a row, not across rows.
- This disagreement is tracked in [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md)

## Related

- [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [KV injection](../methods/kv-injection.md), [Speculative decoding](../methods/speculative-decoding.md)
- [GSM8K](../datasets/gsm8k.md)
- [Why parallel drafters beat EAGLE-3](why-parallel-drafters-beat-eagle-3.md)
- Papers: [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md), [DFlash](../papers/chenDFlashBlockDiffusion2026.md), [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md), [DPara](../papers/liuWhenParallelDrafter2026.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
