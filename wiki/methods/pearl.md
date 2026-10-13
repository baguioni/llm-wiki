---
type: Method
title: PEARL
description: Parallel speculative decoding method that drafts the next round during ongoing verification, preparing only for the outcome in which all draft tokens are accepted.
tags: [speculative-decoding, parallel-speculative-decoding, llm-inference]
sources:
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
---

# PEARL

## Overview

PEARL is a parallel [speculative decoding](../methods/speculative-decoding.md) method. The wiki has no paper page for PEARL itself. Both papers below cite it as "PEARL: parallel speculative decoding with adaptive draft length" (Liu et al., 2025) and describe it only briefly.[^kumarSpeculativeSpeculativeDecoding2026][^liuWhenParallelDrafter2026]

## How it works

- PEARL and AMUSD speculate the next round during ongoing verification, but prepare only for the verification outcome in which all tokens are accepted, which is one special case of many possible outcomes.[^kumarSpeculativeSpeculativeDecoding2026]
- PEARL and AMUSD generate continuations during verification under an all-accepted assumption, which provides only limited opportunities for parallelism.[^liuWhenParallelDrafter2026]
- An unanticipated verification outcome can invalidate the precomputed continuation and fall back to serial speculation.[^liuWhenParallelDrafter2026]

Neither paper describes the adaptive draft length named in PEARL's title.

## Papers using it

- **[Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md)** discusses PEARL as prior parallel speculative decoding work and does not benchmark it. [SSD](../methods/speculative-speculative-decoding.md) prepares for many predicted verification outcomes instead of one.[^kumarSpeculativeSpeculativeDecoding2026]
- **[DPara](../papers/liuWhenParallelDrafter2026.md)** benchmarks PEARL as a parallel speculative decoding baseline on Qwen3-14B with Qwen3-0.6B as draft model and one additional GPU dedicated to drafting. The Qwen3-8B block of the table has no PEARL row.[^liuWhenParallelDrafter2026]

Qwen3-14B, batch size 1, greedy decoding, up to 512 new tokens, draft length 7, NVIDIA H800. Each cell is speedup over autoregressive decoding / average acceptance length $\tau$.[^liuWhenParallelDrafter2026]

| Method | [GSM8K](../datasets/gsm8k.md) | [MATH-500](../datasets/math-500.md) | [HumanEval](../datasets/humaneval.md) | [MBPP](../datasets/mbpp.md) | CodeAlpaca | [Alpaca](../datasets/alpaca.md) | [MT-Bench](../datasets/mt-bench.md) | Avg. |
|---|---|---|---|---|---|---|---|---|
| PEARL | 3.35× / 3.70 | 3.58× / 3.85 | 2.95× / 3.18 | 2.47× / 2.81 | 2.58× / 2.81 | 1.84× / 1.98 | 2.03× / 2.20 | 2.68× / 2.93 |
| SSD | 2.70× / 5.47 | 2.80× / 5.63 | 2.36× / 4.87 | 2.18× / 4.47 | 2.05× / 4.39 | 1.39× / 3.17 | 1.51× / 3.47 | 2.14× / 4.50 |
| SD | 2.21× / 5.47 | 2.28× / 5.65 | 1.99× / 4.86 | 1.85× / 4.46 | 1.76× / 4.39 | 1.31× / 3.17 | 1.42× / 3.47 | 1.83× / 4.50 |
| DPara | 4.53× / 5.73 | 4.32× / 5.37 | 3.84× / 4.76 | 3.58× / 4.45 | 3.49× / 4.46 | 2.32× / 2.91 | 2.53× / 3.16 | 3.52× / 4.41 |

All rows: [^liuWhenParallelDrafter2026]

On Qwen3-14B, DPara improves the average speedup over PEARL by 31%.[^liuWhenParallelDrafter2026]

## Strengths & Limitations

- PEARL covers a single verification outcome (all tokens accepted).[^kumarSpeculativeSpeculativeDecoding2026]
- In the DPara table, PEARL has a higher speedup than SSD and SD on all seven benchmarks, with a lower acceptance length than both.[^liuWhenParallelDrafter2026]
- PEARL is below [DFlash](../methods/dflash.md) (3.08× average), [DSpark](../methods/dspark.md) (3.35×), and DPara (3.52×) on Qwen3-14B.[^liuWhenParallelDrafter2026]

# Contradictions

No two papers report a number for PEARL in the same setting. One tension is recorded here. The SSD paper presents PEARL as covering one special case of the outcomes that SSD prepares for, and does not benchmark it.[^kumarSpeculativeSpeculativeDecoding2026] In the DPara paper's measurement on Qwen3-14B with a Qwen3-0.6B draft, PEARL is faster than SSD (2.68× against 2.14× on average), although its acceptance length is lower (2.93 against 4.50).[^liuWhenParallelDrafter2026] The SSD paper's own results are for Llama-3.1-70B and Qwen-3 32B targets on 4×H100.[^kumarSpeculativeSpeculativeDecoding2026]

## Related

- [Speculative decoding](../methods/speculative-decoding.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md)
- Papers: [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md), [DPara](../papers/liuWhenParallelDrafter2026.md)

[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
