---
type: Method
title: Speculative Speculative Decoding (SSD)
description: Framework that runs drafting in parallel with verification by pre-speculating, on a separate device, for a set of predicted verification outcomes held in a speculation cache.
tags: [speculative-decoding, parallel-speculative-decoding, llm-inference, latency]
sources:
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
---

# Speculative Speculative Decoding (SSD)

## Overview

[Speculative decoding](../methods/speculative-decoding.md) (SD) has a sequential dependence: verification must complete before the next speculation can begin. Speculative speculative decoding (SSD) is a framework for methods that parallelize drafting and verification. While a verification is ongoing, the draft model predicts likely verification outcomes and pre-speculates for each of them. If the actual outcome is in the predicted set, the speculation is returned immediately.[^kumarSpeculativeSpeculativeDecoding2026] SSD is lossless, and the draft model sits on distinct hardware from the target.[^kumarSpeculativeSpeculativeDecoding2026]

The DPara paper re-measures SSD as a parallel speculative decoding (PSD) baseline and studies how often it falls back to serial drafting under batching.[^liuWhenParallelDrafter2026]

## How it works

- A *verification outcome* is $v^T = (k, t^*)$: $k$ accepted draft tokens from the previous round and the bonus token $t^*$.[^kumarSpeculativeSpeculativeDecoding2026]
- While the verifier verifies the drafted tokens of round $T$, the speculator predicts likely verification outcomes, prepares a speculation for each in parallel, and stores them in the speculation cache.[^kumarSpeculativeSpeculativeDecoding2026]
- On a *cache hit* the speculation is returned immediately. On a *cache miss* the speculator defers to a fallback (backup) speculator, which reduces to ordinary SD.[^kumarSpeculativeSpeculativeDecoding2026]
- The space of verification outcomes has size approximately $(K+1)V$ for lookahead $K$ and vocabulary size $V$, so the cache is built under a budget of outcomes.[^kumarSpeculativeSpeculativeDecoding2026]
- At batch size $b$, the whole batch waits for the backup speculator when any element misses.[^kumarSpeculativeSpeculativeDecoding2026]
- The target sends only the previous round's result (number of accepted tokens, bonus token) to the draft device. No [KV cache](../methods/kv-cache.md) is transferred between the devices.[^kumarSpeculativeSpeculativeDecoding2026]

The DPara paper describes SSD in the same terms: the drafter predicts the accepted prefix and bonus token and generates subsequent draft tokens in advance, and a mismatch reverts SSD to serial speculative decoding.[^liuWhenParallelDrafter2026]

## Variants

- **Saguaro.** The optimized SSD algorithm of the original paper. It uses a geometric fan-out for cache construction, a sampling scheme that trades acceptance rate for cache hit rate, and a batch-size-dependent backup speculator. In the implementation, the fast backup strategy returns random tokens and the slow strategy is just-in-time speculation with the primary speculator.[^kumarSpeculativeSpeculativeDecoding2026]
- **SSD-E3.** In the DPara paper, SSD with the EAGLE3 weight of the target as draft model.[^liuWhenParallelDrafter2026]
- **SpecBranch as a special case.** The original paper states that SpecBranch is (approximately) a special case of the SSD framework where only a single branching point is allowed and the fallback speculator equals the regular speculator.[^kumarSpeculativeSpeculativeDecoding2026]

## Papers using it

### Original paper ([Kumar et al. 2026](../papers/kumarSpeculativeSpeculativeDecoding2026.md))

Setting: the paper's own inference engine, batch size 1, greedy decoding, target on 4×H100, SSD draft on a separate 1×H100, 128 prompts per dataset, 512 decoding tokens each.[^kumarSpeculativeSpeculativeDecoding2026]

| Model (target/draft) | Dataset | AR tok/s | SD tok/s | SSD tok/s | SSD/SD | SSD/AR |
|---|---|---|---|---|---|---|
| Llama-3.1-Instruct 70B/1B | [HumanEval](../datasets/humaneval.md) | 54.7 | 176 | 283 | 1.60× | 5.17× |
| Llama-3.1-Instruct 70B/1B | Ultrafeedback | 54.7 | 138 | 215 | 1.55× | 3.93× |
| Llama-3.1-Instruct 70B/1B | [Alpaca](../datasets/alpaca.md) | 54.7 | 145 | 224 | 1.55× | 4.10× |
| Llama-3.1-Instruct 70B/1B | [GSM8k](../datasets/gsm8k.md) | 54.7 | 188 | 301 | 1.60× | 5.50× |
| Llama-3.1-Instruct 70B/1B | Average | 54.7 | 161.8 | 255.8 | 1.58× | 4.68× |
| Qwen-3 32B/0.6B | HumanEval | 88.8 | 146 | 222 | 1.52× | 2.50× |
| Qwen-3 32B/0.6B | Ultrafeedback | 88.8 | 122 | 174 | 1.43× | 1.96× |
| Qwen-3 32B/0.6B | Alpaca | 88.8 | 127 | 185 | 1.47× | 2.08× |
| Qwen-3 32B/0.6B | GSM8k | 88.8 | 152 | 234 | 1.54× | 2.64× |
| Qwen-3 32B/0.6B | Average | 88.8 | 136.8 | 203.8 | 1.49× | 2.29× |

All rows: [^kumarSpeculativeSpeculativeDecoding2026]

- The authors state that Saguaro is on average 30% faster than the strongest speculative decoding baselines and up to 5x faster than autoregressive generation, and that this establishes a new state of the art.[^kumarSpeculativeSpeculativeDecoding2026]
- Baselines are [vLLM](../methods/vllm.md) and [SGLang](../methods/sglang.md) with autoregressive decoding, standalone speculative decoding, and [EAGLE-3](../methods/eagle-3.md). The best baseline configurations on Llama-3.1-70B/1B reach 201.9 tok/s (SGLang standalone SD) and 197.6 tok/s (vLLM EAGLE-3).[^kumarSpeculativeSpeculativeDecoding2026]
- The paper states that Saguaro outperforms SD by 20% even at larger batch sizes.[^kumarSpeculativeSpeculativeDecoding2026]

### DPara paper ([Liu et al. 2026](../papers/liuWhenParallelDrafter2026.md))

Setting: batch size 1, greedy decoding, up to 512 new tokens, draft length 7, NVIDIA H800, one additional GPU dedicated to drafting. SSD on Qwen3-14B uses Qwen3-0.6B as draft model. Each cell is speedup over autoregressive decoding / $\tau$.[^liuWhenParallelDrafter2026]

| Model | Method | GSM8K | [MATH-500](../datasets/math-500.md) | HumanEval | [MBPP](../datasets/mbpp.md) | CodeAlpaca | Alpaca | [MT-Bench](../datasets/mt-bench.md) | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3-8B | SSD-E3 | 1.51× / 2.39 | 1.54× / 2.42 | 1.72× / 2.75 | 1.58× / 2.49 | 1.67× / 2.62 | 1.29× / 2.17 | 1.34× / 2.26 | 1.52× / 2.44 |
| Qwen3-14B | SSD | 2.70× / 5.47 | 2.80× / 5.63 | 2.36× / 4.87 | 2.18× / 4.47 | 2.05× / 4.39 | 1.39× / 3.17 | 1.51× / 3.47 | 2.14× / 4.50 |
| Qwen3-14B | SSD-E3 | 1.76× / 2.48 | 1.80× / 2.48 | 2.02× / 2.80 | 1.82× / 2.54 | 1.91× / 2.68 | 1.48× / 2.17 | 1.57× / 2.28 | 1.77× / 2.49 |
| Qwen3-14B | SD | 2.21× / 5.47 | 2.28× / 5.65 | 1.99× / 4.86 | 1.85× / 4.46 | 1.76× / 4.39 | 1.31× / 3.17 | 1.42× / 3.47 | 1.83× / 4.50 |
| Qwen3-14B | [PEARL](../methods/pearl.md) | 3.35× / 3.70 | 3.58× / 3.85 | 2.95× / 3.18 | 2.47× / 2.81 | 2.58× / 2.81 | 1.84× / 1.98 | 2.03× / 2.20 | 2.68× / 2.93 |
| Qwen3-14B | [DFlash](../methods/dflash.md) | 3.86× / 6.03 | 3.76× / 5.92 | 3.36× / 5.20 | 3.16× / 4.89 | 3.13× / 4.97 | 2.07× / 3.24 | 2.25× / 3.55 | 3.08× / 4.83 |
| Qwen3-14B | [DSpark](../methods/dspark.md) | 4.07× / 6.53 | 4.01× / 6.39 | 3.66× / 5.79 | 3.46× / 5.48 | 3.45× / 5.60 | 2.32× / 3.71 | 2.50× / 4.02 | 3.35× / 5.36 |
| Qwen3-14B | DPara | 4.53× / 5.73 | 4.32× / 5.37 | 3.84× / 4.76 | 3.58× / 4.45 | 3.49× / 4.46 | 2.32× / 2.91 | 2.53× / 3.16 | 3.52× / 4.41 |

All rows: [^liuWhenParallelDrafter2026]

- On Qwen3-14B, DPara improves the average speedup over SSD by 64%.[^liuWhenParallelDrafter2026]
- SSD fallback rate, Qwen3-14B, seven benchmarks: at batch size 1, 8%–32% of steps fall back to serial re-drafting. At batch size 16 the rate reaches 57%–96%.[^liuWhenParallelDrafter2026]
- Chat workloads have the highest rate: 29%–32% at batch 1 and 91%–96% at batch 16.[^liuWhenParallelDrafter2026]
- A per-request bonus-mismatch probability $p$ becomes a per-step fallback probability $1-(1-p)^{B}$ for a batch of $B$ requests.[^liuWhenParallelDrafter2026]

## Strengths & Limitations

- SSD with the same speculator does no worse than SD (Corollary 8 of the original paper).[^kumarSpeculativeSpeculativeDecoding2026]
- SSD needs additional hardware: the draft runs on its own device, and the draft decodes $BK(K+1)F$ tokens per round against $BK$ in SD.[^kumarSpeculativeSpeculativeDecoding2026]
- Cache misses happen increasingly often at large batch sizes and temperatures.[^kumarSpeculativeSpeculativeDecoding2026]
- Most of the end-to-end speedup comes from hiding draft latency, not from increasing lookahead, because the custom-mask attention kernels dominate the critical path.[^kumarSpeculativeSpeculativeDecoding2026]
- Combined with EAGLE-3, the SSD draft does not yet have target activations from round $T$, so with lookahead $K$ it conditions on up to $2K$ self-generated tokens.[^kumarSpeculativeSpeculativeDecoding2026]
- The overlap depends on the verification outcome. The DPara paper calls this outcome-dependent overlap and states that it exchanges a best-case gain for a regression that intensifies with serving load.[^liuWhenParallelDrafter2026]

# Contradictions

**1. Robustness to batch size.** The original paper states that, with its batch-size-dependent fallback strategy, Saguaro outperforms SD by 20% even at larger batch sizes, and that SSD improves the throughput-latency Pareto frontier across batch sizes.[^kumarSpeculativeSpeculativeDecoding2026] The DPara paper measures that 57%–96% of SSD steps fall back to serial re-drafting at batch size 16 on Qwen3-14B, and describes a markedly steeper throughput drop-off for SSD as batches grow.[^liuWhenParallelDrafter2026] Setting differences: the original claim is for Llama-3.1-70B and Qwen-3 32B targets on 4×H100 and is shown only in figures, with a fast backup speculator that returns random tokens at large batch sizes.[^kumarSpeculativeSpeculativeDecoding2026] The DPara measurement is on Qwen3-14B with a Qwen3-0.6B draft on an H800 node, counts steps in which the drafter re-drafts the whole batch serially, and gives the SSD batch throughput only in a figure.[^liuWhenParallelDrafter2026] The two papers agree on the mechanism: a miss by any batch element stalls the whole batch.[^kumarSpeculativeSpeculativeDecoding2026][^liuWhenParallelDrafter2026]

**2. State-of-the-art claim.** The original paper states that SSD establishes a new state of the art against standalone SD and EAGLE-3 baselines.[^kumarSpeculativeSpeculativeDecoding2026] In the DPara paper's table for Qwen3-14B, SSD (2.14× on average) is above EAGLE3 (1.73×) and SD (1.83×), and below PEARL (2.68×), DFlash (3.08×), DSpark (3.35×), and DPara (3.52×).[^liuWhenParallelDrafter2026] The claim is superseded within this wiki by the DPara result. The baselines differ: DFlash, DSpark, and PEARL are not benchmarked in the original paper.[^kumarSpeculativeSpeculativeDecoding2026]

**3. Size of the SSD gain.** The values are for different targets and so are not a like-for-like conflict. With a Qwen3-0.6B draft, the original paper reports SSD/AR of 2.64× on GSM8k, 2.50× on HumanEval, and 2.08× on Alpaca for a Qwen-3 32B target.[^kumarSpeculativeSpeculativeDecoding2026] The DPara paper reports 2.70×, 2.36×, and 1.39× on the same datasets for a Qwen3-14B target.[^liuWhenParallelDrafter2026]

## Related

- [Speculative decoding](../methods/speculative-decoding.md), [PEARL](../methods/pearl.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE-3](../methods/eagle-3.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- Engines used as baselines: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Papers: [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md), [DPara](../papers/liuWhenParallelDrafter2026.md)

## Open questions and results

- [Does speculative decoding still help at large batch sizes?](../questions/speculative-decoding-at-large-batch.md)

[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
