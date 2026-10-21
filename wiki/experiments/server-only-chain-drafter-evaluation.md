---
type: Experiment
title: Six drafters on the server GPU, chain7, no phone
description: My server-only counterpart of the phone chain7 arms, with all six drafters re-implemented in PyTorch bf16 and drafting on the same DGX Spark GB10 as the Qwen3-14B-FP8 target; every drafter is 1.22-1.36× faster than on the phone, PARD-2 (34.0 tok/s) and DSpark (33.9) tie for first, and three chain arms beat the best phone arm (30.0).
tags: [speculative-decoding, draft-model, server-only, mobile-specedge, dflash, dspark, pard, eagle-3]
date: 2026-10-19
data_sources:
  - raw/experiments/drafter-evaluation-server-only-chain.md
sources:
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
---

# Six drafters on the server GPU, chain7, no phone

This page records my own experiment. Every number comes from the report `raw/experiments/drafter-evaluation-server-only-chain.md`. It ran on 2026-10-19 from 16:52 to 17:55 KST on spark2: 12 live runs (6 drafters × 2 repeats), all finished OK, with offline replays against the C++ oracle earlier that day.[^drafter-evaluation-server-only-chain] The phone numbers quoted for comparison are the chain7 arms of [Six phone drafters for a Qwen3-14B server verifier](drafter-evaluation-qwen3-14b.md), unchanged.[^drafter-evaluation-server-only-chain]

## Goal

Measure what each of the six drafters gives when it drafts on the server GPU, beside the target, instead of on the phone NPU. The earlier server-only baselines covered only a Qwen3-0.6B draft.[^drafter-evaluation-server-only-chain]

## Setup

- **One process, one GPU.** Draft and target run in one Python process on one GB10 (spark2), one request at a time, temperature 0, no network. Feature rows reach the drafter as GPU tensors cast from fp16 to bf16, with no serialization.[^drafter-evaluation-server-only-chain]
- **Target.** `Qwen/Qwen3-14B-FP8`, the server's own `Qwen3ForCausalLM` with fp16 activations, no CUDA graph, batch size 1, thinking off. Same model code and FP8 patch as the phone arms' server. The feature hooks are the same server code the phone arms used.[^drafter-evaluation-server-only-chain]
- **Drafters.** New PyTorch code in specedge `src/chain/` (branch `eval/so-chain`, commit `3c22ed0`), bf16 weights and activations, mirroring the C++ phone client's chain at width 1. DFlash, DSpark, and EAGLE-3 follow DeepSpec's eval modules; PARD-1 and PARD-2 follow AMD's PARD repository.[^drafter-evaluation-server-only-chain]

| Drafter | Checkpoint | How one round drafts 7 tokens | CUDA graph |
|---|---|---|---|
| Qwen3-0.6B | `Qwen/Qwen3-0.6B` | AR chain: decode the pending committed tokens, then 6 single-token steps | no (eager) |
| [PARD](../methods/pard.md)-1 | `amd/PARD-Qwen3-0.6B` | one causal forward of [uncached committed tokens, anchor, 6 mask tokens] | yes |
| PARD-2 | `amd/PARD2-Qwen3-14B` | as PARD-1, with each row's input = embedding + projected target feature of the previous position | yes |
| [DFlash](../methods/dflash.md) | `deepseek-ai/dflash_qwen3_14b_block7` | new feature rows injected as context K/V, then one non-causal block forward over [anchor, 6 masks] | no |
| [DSpark](../methods/dspark.md) | `deepseek-ai/dspark_qwen3_14b_block7` | as DFlash, then the Markov bias added row by row, chained greedily from the anchor | no |
| [EAGLE-3](../methods/eagle-3.md) | `deepseek-ai/eagle3_qwen3_14b_ttt7` | 1 head step from the last committed cell, then 6 single-cell steps feeding the head's own output back | no |

All rows: [^drafter-evaluation-server-only-chain]

- **Round.** Draft 7 tokens greedily, verify [anchor, d1 … d7] as 8 rows in one causal forward, accept the longest matching prefix plus one bonus token, then commit at the start of the next draft (timed as draft time).[^drafter-evaluation-server-only-chain]
- **Workload.** The same 60 Spec-Bench requests as the phone arms, 10 per category, temperature 0, `max_new_tokens` 64, batch size 1, 1 unlogged warm-up request.[^drafter-evaluation-server-only-chain]
- **Prefill.** Computed live (no prefill cache). The phone arms used `cache_prefill: true`, so TTFT is not comparable.[^drafter-evaluation-server-only-chain]
- **Metrics.** As for the earlier server-only runs: tok/s steady is Σk / Σ round time per request over steady rounds (round 0 excluded), averaged over the 60 requests and then the 2 repeats; k includes the bonus token; round time is draft + target, each wall-clock with a CUDA synchronize at both ends.[^drafter-evaluation-server-only-chain]

## Procedure

1. **Against DeepSpec upstream.** On tiny random checkpoints, DFlash, DSpark, and EAGLE-3 give identical drafts and logits to DeepSpec's own modules over 4 rounds.[^drafter-evaluation-server-only-chain]
2. **Offline replay.** The 60 requests are replayed in bf16 with the target replaced by the recorded trace and dumped target features, and compared with the C++ oracle's Q4_0 chain7 rounds (PARD-2: the fp32 HF oracle).[^drafter-evaluation-server-only-chain]
3. **Live runs.** Repeat 1 of all six drafters, then repeat 2, each after a GPU check that no other compute process is present. None was.[^drafter-evaluation-server-only-chain]

**CUDA graphs.** A graph for the PARD block cut replay draft time from 15.2 to 12.6 ms (PARD-1) and from 18.7 to 15.4 ms (PARD-2). The AR 1-row step was slower as a graph (replay draft 86.1 against 83.0 ms per round), because a 1-row step is bound by weight reads (about 150 GB/s on bf16 GEMVs in torch on the GB10) and the graph's attention reads a whole 256-key bucket. So the AR drafter went back to eager before the live runs. Graphs do not change acceptance beyond numerics.[^drafter-evaluation-server-only-chain]

## Results

### Throughput and round time (steady, mean over repeats)

| Drafter | Server-only tok/s | 95% CI (r1) | Phone chain7 tok/s | Server / phone | Server tok/round | Phone tok/round | Server draft ms | Server round ms | Phone round ms |
|---|---|---|---|---|---|---|---|---|---|
| PARD-2 | **34.0** | 30.67..36.60 | 24.9 | 1.36× | 3.50 | 3.34 | 15.6 | 114.1 | 148.8 |
| DSpark | **33.9** | 30.87..36.72 | 26.5 | 1.28× | 3.90 | 3.83 | 27.2 | 127.4 | 160.3 |
| DFlash | **31.0** | 28.29..34.02 | 25.5 | 1.22× | 3.43 | 3.45 | 24.2 | 124.1 | 152.3 |
| PARD-1 | **28.0** | 25.42..30.87 | 22.1 | 1.27× | 2.86 | 2.76 | 13.0 | 111.3 | 137.0 |
| Qwen3-0.6B | **20.4** | 18.81..22.32 | 15.6 | 1.31× | 3.42 | 3.11 | 86.4 | 185.2 | 227.0 |
| EAGLE-3 | **17.2** | 15.38..19.02 | 13.0 | 1.32× | 2.81 | 2.71 | 88.8 | 188.0 | 239.4 |
| *Qwen3-0.6B, 10-16 specedge `server_only.py` (fp16)* | *17.0* | | | | *3.37* | | *111.6* | *212.8* | |

All rows: [^drafter-evaluation-server-only-chain]

- Verify (target) time is 98.2–100.2 ms mean per round in every arm.[^drafter-evaluation-server-only-chain]
- Against the phone's client wait of 114.8–129.2 ms, every server-only round is 25.7–51.4 ms shorter.[^drafter-evaluation-server-only-chain]
- Drafting is also faster on the GPU for five of the six drafters. The exception is Qwen3-0.6B, at 86.4 ms against 84.9 ms on the phone.[^drafter-evaluation-server-only-chain]
- DSpark's draft is 3.0 ms longer than DFlash's (27.2 against 24.2 ms), the cost of its Markov chain on the GPU. On the phone's host CPU the Markov head took 8.48 ms.[^drafter-evaluation-server-only-chain]
- EAGLE-3's commit step, which re-extends the committed cells through the head, averages 3.66 ms; it is 0.00–0.02 ms for the other drafters.[^drafter-evaluation-server-only-chain]

### Acceptance (steady rounds)

| Drafter | tok/round | P(k=0) | a1 | a2 | a3 | a4 | a5 | a6 | a7 |
|---|---|---|---|---|---|---|---|---|---|
| PARD-2 | 3.50 | 0.227 | 0.773 | 0.559 | 0.405 | 0.285 | 0.204 | 0.161 | 0.116 |
| DSpark | 3.90 | 0.202 | 0.798 | 0.629 | 0.476 | 0.363 | 0.272 | 0.198 | 0.162 |
| DFlash | 3.43 | 0.223 | 0.777 | 0.545 | 0.383 | 0.277 | 0.200 | 0.143 | 0.108 |
| PARD-1 | 2.86 | 0.337 | 0.663 | 0.436 | 0.279 | 0.197 | 0.132 | 0.088 | 0.066 |
| Qwen3-0.6B | 3.42 | 0.308 | 0.692 | 0.500 | 0.384 | 0.294 | 0.222 | 0.183 | 0.143 |
| EAGLE-3 | 2.81 | 0.398 | 0.602 | 0.398 | 0.258 | 0.191 | 0.149 | 0.119 | 0.092 |

All rows: [^drafter-evaluation-server-only-chain]

$a_j$ is the fraction of steady rounds whose accepted path reached depth j. The two repeats give identical acceptance.[^drafter-evaluation-server-only-chain]

### By category (tok/s, server-only, phone chain7 in parentheses)

| Drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 | 37.5 (28.3) | 32.0 (22.8) | 24.7 (18.4) | 25.6 (19.3) | 52.1 (37.2) | 31.9 (23.5) |
| DSpark | 35.1 (26.8) | 32.3 (25.5) | 24.2 (19.1) | 27.4 (21.8) | 50.6 (40.3) | 33.5 (25.4) |
| DFlash | 31.8 (27.0) | 29.5 (23.8) | 22.5 (18.0) | 23.3 (19.0) | 48.7 (40.7) | 30.4 (24.7) |
| PARD-1 | 32.0 (25.0) | 20.3 (16.5) | 21.4 (17.2) | 23.1 (17.5) | 44.3 (35.2) | 27.1 (21.4) |
| Qwen3-0.6B | 21.8 (17.7) | 21.1 (16.9) | 15.9 (11.3) | 15.3 (11.9) | 30.1 (22.1) | 18.5 (13.4) |
| EAGLE-3 | 18.0 (13.5) | 15.1 (11.9) | 13.4 (10.2) | 11.0 (8.7) | 29.1 (21.7) | 16.2 (12.1) |

All rows: [^drafter-evaluation-server-only-chain]

### Prefill and time to first token (cold prefill)

Target prefill is 303.2–318.3 ms for every drafter. For the feature drafters the first token is committed with the prefill (306.4–318.3 ms); the token drafters need a separate round 0 after it, so their first token comes at 457.9 ms (PARD-1) and 519.7 ms (Qwen3-0.6B).[^drafter-evaluation-server-only-chain]

### Validity checks

- **Repeatability.** In every arm, repeat 2 reproduces repeat 1 exactly: the same k for every round, the same output tokens, and the same stop reasons. Steady tok/s moves by 0.04–0.52 between repeats.[^drafter-evaluation-server-only-chain]

Replay against the oracle (tok/round, chain7, 60 requests):

| Drafter | PyTorch bf16 replay | C++ oracle | Oracle precision | Live server-only | Live phone |
|---|---|---|---|---|---|
| DFlash | 3.44 | 3.42 | Q4_0 | 3.43 | 3.45 |
| DSpark | 3.88 | 3.86 | Q4_0 | 3.90 | 3.83 |
| EAGLE-3 | 2.86 | 2.80 | Q4_0 | 2.81 | 2.71 |
| PARD-1 | 2.90 | 2.78 (fp32 HF oracle: 2.909) | Q4_0 | 2.86 | 2.76 |
| Qwen3-0.6B | 3.38 | 3.11 | Q4_0 | 3.42 | 3.11 |
| PARD-2 | 3.61 | 3.580 | fp32 HF | 3.50 | 3.34 |

All rows: [^drafter-evaluation-server-only-chain]

- **Replay.** The bf16 replay sits at or slightly above the Q4_0 oracle for every drafter, which the report reads as the cost of quantization. Replay draft times are within 0–3.4 ms of the live ones.[^drafter-evaluation-server-only-chain]
- **Output agreement (first 64 tokens, repeat 1).** Within a server-only run, the four feature drafters produce identical outputs on 60/60 requests, as do the two token drafters. Token drafters against feature drafters agree on 57/60 (median first difference at token 58). Each token drafter matches its phone chain7 arm on 60/60, and each feature drafter matches its phone arm on 52/60 (median first difference at token 49).[^drafter-evaluation-server-only-chain]
  - The report explains the two groups by how the target sees the last prompt token: a feature drafter's prefill covers the whole prompt, while a token drafter's prompt ends in round 0's 8-row verify. It concludes that the output depends on the target's numerics (FP8, fp16 activations, the exact batch shape), not on the drafter.[^drafter-evaluation-server-only-chain]
  - The cause of the 8 feature-drafter differences from the phone was not investigated. The phone arms' server prefilled from a cache and these runs compute the prefill live.[^drafter-evaluation-server-only-chain]

## Interpretation

The report's main findings:[^drafter-evaluation-server-only-chain]

1. **Every drafter is faster server-only than on the phone**, by 1.22× (DFlash) to 1.36× (PARD-2). The verify wait drops from the phone's client wait to the bare target forward, and five of the six drafters also draft faster on the GPU.
2. **PARD-2 and DSpark tie for first** (34.0 and 33.9 tok/s); on the phone DSpark led the chains and PARD-2 was third. PARD-2 has the cheapest draft of the feature drafters (15.6 ms); DSpark accepts the most (3.90 tok/round) but drafts in 27.2 ms.
3. **The block drafters still beat the AR drafters by a wide margin**: 28.0–34.0 against 17.2–20.4 tok/s. The AR drafters take 86–89 ms per round to draft on the GB10, as on the phone; the block drafters 13–27 ms.
4. **Three server-only chain arms beat the best phone arm overall** (PARD-2 own-best tree, 30.0 tok/s): PARD-2 34.0, DSpark 33.9, and DFlash 31.0. The 10-16 server-only Qwen3-0.6B baseline (best 21.6 tok/s) beat none of the phone block-drafter arms.
5. **Acceptance is close to the phone's**: within −0.02 to +0.16 tok/round, except Qwen3-0.6B at +0.31. The server drafts are bf16 and the phone drafts Q4_0.

**Implementation matters for the AR baseline.** The same Qwen3-0.6B draft at the same chain7 shape gives 20.4 tok/s with this code and 17.0 with specedge's `server_only.py` on 10-16, mostly through the draft time (86.4 against 111.6 ms per round).[^drafter-evaluation-server-only-chain] **Inference.** The earlier finding that the GPU drafts slower than the NPU as a chain ([Drafting on the server GPU instead of the phone NPU](../results/server-vs-phone-draft-location.md)) therefore belongs to that implementation; here the GPU and NPU AR drafts are about equal (86.4 against 84.9 ms).[^drafter-evaluation-server-only-chain]

## Limitations

- **Chain only (depth 7).** There are no server-only trees for the block or feature drafters, while the phone's best arms are trees.[^drafter-evaluation-server-only-chain]
- **bf16 against Q4_0.** The comparison mixes the drafter's location with its precision.[^drafter-evaluation-server-only-chain]
- **Little GPU optimization of the drafts.** CUDA graphs only for the PARD block; AR and EAGLE-3 steps are eager, DFlash and DSpark use eager PyTorch with SDPA, no fused kernels or quantized drafts, and the target runs without CUDA graphs.[^drafter-evaluation-server-only-chain]
- **Single process, batch size 1.** Draft and target share the GPU but never run concurrently. The results say nothing about serving several clients.[^drafter-evaluation-server-only-chain]
- **64 new tokens, cold prefill, one node, two repeats.** Branch `eval/so-chain` is not merged into `eval/drafters`.[^drafter-evaluation-server-only-chain]

## Next steps

From the limitations: server-only trees for the block and feature drafters, to compare with the phone's own-best trees; and a GPU-optimized draft path (graphs, fused kernels) for the AR and EAGLE-3 drafters.[^drafter-evaluation-server-only-chain]

## Related

- [Six phone drafters for a Qwen3-14B server verifier](drafter-evaluation-qwen3-14b.md) (the phone arms and the earlier server-only baselines)
- [Drafting on the server GPU instead of the phone NPU](../results/server-vs-phone-draft-location.md)
- [Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU](../results/block-drafters-vs-ar-drafters-on-phone-npu.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)
- [Why do tree-verified outputs diverge from chain outputs at temperature 0?](../questions/fp8-verifier-tree-output-divergence.md)
- [What is the smallest block drafter that keeps acceptance with a sequential head?](../questions/minimum-drafter-depth-with-sequential-head.md)
- Methods: [PARD](../methods/pard.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE-3](../methods/eagle-3.md). Benchmark: [Spec-Bench](../benchmarks/spec-bench.md)
- [Quantization of the target and the draft in speculative decoding](../analyses/quantization-in-speculative-decoding.md) and [How much acceptance does quantizing the draft or the target cost?](../questions/quantization-and-acceptance.md)

[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
