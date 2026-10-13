---
type: Method
title: DSpark
description: Speculative decoding framework that adds a lightweight sequential head to a parallel DFlash-style drafter and schedules per-request verification length from calibrated confidence and engine load.
tags: [speculative-decoding, parallel-drafting, semi-autoregressive, confidence-estimation, verification-scheduling, llm-serving]
sources:
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
---

# DSpark

## Overview

DSpark is a [speculative decoding](../methods/speculative-decoding.md) framework with two parts. A semi-autoregressive drafter couples a parallel backbone ([DFlash](../methods/dflash.md) in the paper's instantiation) with a lightweight sequential head that models dependencies inside the block. Confidence-scheduled verification then sets the verification length of each request from estimated prefix survival probabilities and a profiled engine throughput curve.[^chengDSparkConfidenceScheduledSpeculative2026]

It targets two problems of parallel drafters: they predict each position independently, so acceptance decays at later positions, and verifying the whole block wastes batch capacity on tokens that are likely to be rejected.[^chengDSparkConfidenceScheduledSpeculative2026] DSpark is deployed in the DeepSeek-V4 serving system.[^chengDSparkConfidenceScheduledSpeculative2026]

The DPara paper re-measures DSpark as its strongest serial baseline and builds its own drafter from a DSpark checkpoint.[^liuWhenParallelDrafter2026]

## How it works

- **Parallel stage.** The backbone runs one forward pass over the block and produces hidden states $h_{1},\ldots,h_{\gamma}$ and base logits $U_{1},\ldots,U_{\gamma}$. The one change from DFlash is that the anchor itself is the first prediction position, so $\gamma$ input tokens (anchor $+$ $\gamma{-}1$ masks) yield $\gamma$ draft logits.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Sequential stage.** A prefix-dependent transition bias $B_{k}$ is added to the base logits, and sampling runs left to right.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Confidence head.** $c_{k}$ models the probability that the draft token at position $k$ survives verification given that all preceding tokens in the block were accepted. It is calibrated post hoc with Sequential Temperature Scaling (STS).[^chengDSparkConfidenceScheduledSpeculative2026]
- **Hardware-aware prefix scheduler.** For $R$ active requests, the prefix survival probability is $a_{r,j}=\prod_{i\leqslant j}c_{r,i}$. The scheduler maximizes $\Theta=\tau\cdot\text{SPS}(B)$, where $\text{SPS}(B)$ is engine throughput in steps per second for forward-pass batch size $B$. It sorts all candidates $(r,j)$ by $a_{r,j}$, admits them one at a time, and stops at the first step where $\Theta$ does not improve.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Training.** The target is frozen. The drafter shares the target's embedding layer and LM head, both frozen. The loss is $\mathcal{L}=\alpha_{\text{ce}}\,\mathcal{L}_{\text{ce}}+\alpha_{\text{tv}}\,\mathcal{L}_{\text{tv}}+\alpha_{\text{conf}}\,\mathcal{L}_{\text{conf}}$ with defaults $\alpha_{\text{ce}}=0.1$, $\alpha_{\text{tv}}=0.9$, $\alpha_{\text{conf}}=1.0$.[^chengDSparkConfidenceScheduledSpeculative2026]

The DPara paper summarizes the design as a parallel diffusion backbone coupled with a lightweight autoregressive (AR) head that conditions each position on the preceding sampled tokens.[^liuWhenParallelDrafter2026]

## Variants

- **Markov head.** $B_{k}$ depends only on the preceding token. The transition matrix is approximated as $B=W_{1}W_{2}$ with $r{=}256$ by default. DSpark means this variant unless stated.[^chengDSparkConfidenceScheduledSpeculative2026]
- **RNN head.** A recurrent state accumulates the full prefix history in the block. It gives only marginal gains over the Markov head, mainly at longer proposal lengths.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Production drafter (DSpark-5).** Three MoE layers with mHC and a sliding window attention of 128, maximum block size $\gamma=5$, Markov head, confidence head calibrated with STS. The production scheduler is asynchronous: the batch capacity limit is set from confidence outputs of two steps prior, and the early stop is removed.[^chengDSparkConfidenceScheduledSpeculative2026]
- **M-DFlash.** The DPara backbone, initialized from the official DSpark checkpoint. Only the backbone is adapted. The AR head and the confidence head stay frozen, and the confidence loss is disabled.[^liuWhenParallelDrafter2026]

## Papers using it

### Original paper ([Cheng et al. 2026](../papers/chengDSparkConfidenceScheduledSpeculative2026.md))

Setting: targets Qwen3-{4B, 8B, 14B} and Gemma4-12B, 5 draft layers, block size 7, drafters trained for 10 epochs on prompts from [Open-PerfectBlend](../datasets/perfectblend.md), sampling temperature 1.0, chain-based drafting, non-thinking mode, confidence scheduler disabled. The metric is accepted length $\tau$ per decoding round including the bonus token.[^chengDSparkConfidenceScheduledSpeculative2026]

| Target | [GSM8K](../datasets/gsm8k.md) | [MATH](../datasets/math-500.md) | AIME25 | [MBPP](../datasets/mbpp.md) | [HumanEval](../datasets/humaneval.md) | [LCB](../datasets/livecodebench.md) | [MT-Bench](../datasets/mt-bench.md) | [Alpaca](../datasets/alpaca.md) | Arena-Hard |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3-4B | 6.11 | 5.70 | 4.89 | 5.13 | 5.38 | 4.86 | 3.64 | 3.54 | 3.29 |
| Qwen3-8B | 6.17 | 5.78 | 5.01 | 5.16 | 5.52 | 5.17 | 3.72 | 3.58 | 3.21 |
| Qwen3-14B | 6.21 | 5.74 | 4.94 | 5.26 | 5.43 | 5.02 | 3.70 | 3.58 | 3.13 |
| Gemma4-12B | 6.05 | 5.78 | 5.12 | 5.11 | 5.64 | 4.51 | 3.49 | 3.35 | 2.92 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

- On Qwen3-4B, 8B, and 14B, DSpark improves the macro-average accepted length over [Eagle3](../methods/eagle-3.md) by 30.9%, 26.7%, and 30.0%, and over DFlash by 16.3%, 18.4%, and 18.3%.[^chengDSparkConfidenceScheduledSpeculative2026]
- Gain in accepted length over DFlash on Qwen3-4B: 16% on math, 15% on code, and 18% on chat at $\gamma=7$; 30%, 26%, and 22% at $\gamma=15$.[^chengDSparkConfidenceScheduledSpeculative2026]
- At batch size 128, scaling the draft length from 4 to 16 adds 0.2% to 1.3% to the full-round latency over the DFlash baseline.[^chengDSparkConfidenceScheduledSpeculative2026]
- Live traffic in DeepSeek-V4, DSpark-5 against [MTP-1](../methods/multi-token-prediction.md): per-user generation is 60% to 85% faster on V4-Flash and 57% to 78% faster on V4-Pro at matched throughput. Aggregate throughput is 51% higher at an 80 tok/s/user SLA on V4-Flash and 52% higher at a 35 tok/s/user SLA on V4-Pro.[^chengDSparkConfidenceScheduledSpeculative2026]

### DPara paper ([Liu et al. 2026](../papers/liuWhenParallelDrafter2026.md))

Setting: batch size 1, draft length 7, up to 512 new tokens, NVIDIA H800. Each cell is speedup over autoregressive decoding / $\tau$.[^liuWhenParallelDrafter2026]

| Model | Decoding | GSM8K | MATH-500 | HumanEval | MBPP | CodeAlpaca | Alpaca | MT-Bench | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3-8B | greedy | 3.48× / 6.51 | 3.46× / 6.39 | 3.15× / 5.82 | 3.00× / 5.51 | 3.01× / 5.55 | 2.00× / 3.72 | 2.13× / 4.01 | 2.89× / 5.36 |
| Qwen3-14B | greedy | 4.07× / 6.53 | 4.01× / 6.39 | 3.66× / 5.79 | 3.46× / 5.48 | 3.45× / 5.60 | 2.32× / 3.71 | 2.50× / 4.02 | 3.35× / 5.36 |
| Qwen3-8B | temperature 1.0 | 3.06× / 6.15 | 3.00× / 5.96 | 2.78× / 5.53 | 2.64× / 5.24 | 2.63× / 5.22 | 1.80× / 3.54 | 1.89× / 3.74 | 2.54× / 5.05 |
| Qwen3-14B | temperature 1.0 | 3.74× / 6.18 | 3.61× / 5.91 | 3.33× / 5.46 | 3.13× / 5.25 | 3.15× / 5.17 | 2.16× / 3.54 | 2.26× / 3.79 | 3.05× / 5.04 |

All rows: [^liuWhenParallelDrafter2026]

Batched throughput of DSpark in tok/s, with speedup over the batched autoregressive baseline in parentheses:[^liuWhenParallelDrafter2026]

| Model | Task | b=1 | b=2 | b=4 | b=8 | b=16 |
|---|---|---|---|---|---|---|
| Qwen3-8B | GSM8K | 491 (3.48×) | 901 (3.25×) | 1507 (2.85×) | 2426 (2.59×) | 3627 (2.39×) |
| Qwen3-8B | HumanEval | 445 (3.15×) | 815 (3.02×) | 1464 (2.75×) | 2283 (2.39×) | 3382 (2.01×) |
| Qwen3-14B | GSM8K | 355 (4.07×) | 647 (3.79×) | 1142 (3.47×) | 1813 (3.03×) | 2847 (2.79×) |
| Qwen3-14B | HumanEval | 319 (3.66×) | 598 (3.52×) | 1082 (3.25×) | 1688 (2.71×) | 2523 (2.34×) |

All rows: [^liuWhenParallelDrafter2026]

- Latency on Qwen3-14B, GSM8K, batch size 1: the DSpark draft stage exposes 4.4 ms on the critical path (backbone 2.7 ms, AR head 0.3 ms, context bookkeeping 1.4 ms), 25% of its 17.7 ms step. The step grows to 23.3 ms (+32%) at batch size 16.[^liuWhenParallelDrafter2026]
- DPara improves average speedup over DSpark by 11.1% on Qwen3-8B and 5.1% on Qwen3-14B, although DPara's average acceptance length (4.43 and 4.41) is below DSpark's 5.36.[^liuWhenParallelDrafter2026]
- On a GB200 with Qwen3-8B at batch size 1, DSpark reaches 2.34× over autoregressive decoding, against 2.62× for DPara-single and 2.77× for DPara.[^liuWhenParallelDrafter2026]
- Running DPara with the original DSpark checkpoint instead of M-DFlash lowers $\tau$ on Qwen3-8B: 4.07 against 5.82 on GSM8K, and 2.55 against 2.92 on Alpaca.[^liuWhenParallelDrafter2026]

## Strengths & Limitations

- DSpark has the highest accepted length in every cell of the original paper's main table.[^chengDSparkConfidenceScheduledSpeculative2026]
- A 2-layer DSpark outperforms the 5-layer DFlash baseline across all domains.[^chengDSparkConfidenceScheduledSpeculative2026]
- DSpark still pays a fixed draft-side cost to generate the initial $\gamma$-token block. For complex queries with inherently low acceptance rates, this drafting compute is unrecoverable.[^chengDSparkConfidenceScheduledSpeculative2026]
- The scheduler assumes that engine throughput depends predominantly on the verification batch size $B$, not on context length. Its early stop is globally optimal only if $\Theta$ is unimodal, while the real $\text{SPS}(B)$ curve is jagged and step-wise.[^chengDSparkConfidenceScheduledSpeculative2026]
- The original paper reports offline accepted length with the scheduler disabled. The scheduler is evaluated in live production traffic.[^chengDSparkConfidenceScheduledSpeculative2026]
- The draft phase remains serialized on the critical path of every round. DSpark's step stays 28%–30% longer than DPara's at every batch size.[^liuWhenParallelDrafter2026]

# Contradictions

**DSpark acceptance length at temperature 1.0 with block (draft) length 7.** Two papers report $\tau$ for the same target models, benchmarks, temperature, and length, and the values differ by up to 0.18.

| Model | Reported by | GSM8K | MATH-500 | HumanEval | MBPP | MT-Bench | Alpaca |
|---|---|---|---|---|---|---|---|
| Qwen3-8B | Cheng et al. | 6.17 | 5.78 | 5.52 | 5.16 | 3.72 | 3.58 |
| Qwen3-8B | Liu et al. | 6.15 | 5.96 | 5.53 | 5.24 | 3.74 | 3.54 |
| Qwen3-14B | Cheng et al. | 6.21 | 5.74 | 5.43 | 5.26 | 3.70 | 3.58 |
| Qwen3-14B | Liu et al. | 6.18 | 5.91 | 5.46 | 5.25 | 3.79 | 3.54 |

Rows "Cheng et al.": [^chengDSparkConfidenceScheduledSpeculative2026] Rows "Liu et al.": [^liuWhenParallelDrafter2026]

Setting differences: Cheng et al. call the length "block size (7)" and use chain-based drafting with the confidence scheduler disabled.[^chengDSparkConfidenceScheduledSpeculative2026] Liu et al. call it "draft length 7", evaluate 80 requests per benchmark with up to 512 new tokens, top-$p$ 1.0, and temperature 1.0 for both the target and the drafter. They initialize M-DFlash from the official DSpark checkpoint, and do not state the checkpoint of the DSpark baseline rows separately.[^liuWhenParallelDrafter2026]

The original paper reports no offline wall-clock speedup for DSpark, so the DPara paper's speedups (2.89× and 3.35× on average under greedy decoding) have no counterpart to compare against.[^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026]

## Related

- Backbone and mechanism: [DFlash](../methods/dflash.md), [KV injection](../methods/kv-injection.md), [Speculative decoding](../methods/speculative-decoding.md)
- Compared against: [EAGLE-3](../methods/eagle-3.md), [Multi-token prediction](../methods/multi-token-prediction.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [PEARL](../methods/pearl.md)
- Related training idea: [Training-time test](../methods/training-time-test.md)
- Papers: [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md), [DPara](../papers/liuWhenParallelDrafter2026.md)

## Open questions and results

- [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md)
- [DFlash, DSpark, and EAGLE-3: how they draft and what they report on Qwen3-8B](../analyses/dflash-dspark-eagle-3-drafting-comparison.md)

[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
