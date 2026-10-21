---
type: Experiment
title: Six phone drafters for a Qwen3-14B server verifier
description: My live evaluation of six Q4_0 drafters (PARD-1, PARD-2, DFlash, DSpark, Qwen3-0.6B, EAGLE-3) drafting on a Galaxy S25 NPU for a Qwen3-14B-FP8 verifier on a DGX Spark, in chain, matched-tree, and own-best tree shapes; block drafters reach 26.7-30.0 tok/s against 13.0-18.5 for the autoregressive ones, and every block-drafter arm beats server-only speculative decoding with a GPU Qwen3-0.6B draft (17.0-21.6 tok/s), though the block drafters themselves run faster as server-only chains (28.0-34.0 tok/s).
tags: [mobile-npu, on-device-inference, draft-model, speculative-decoding, mobile-specedge, dflash, dspark, pard, eagle-3, tree-based-speculation]
date: 2026-10-16
data_sources:
  - raw/experiments/drafter-evaluation.md
  - raw/experiments/drafter-evaluation-server-shapes.md
  - raw/experiments/drafter-evaluation-server-only-chain.md
sources:
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
  - id: drafter-evaluation-server-shapes
    resource: raw/experiments/drafter-evaluation-server-shapes.md
    title: "Drafter evaluation with server-only baselines at the SpecEdge, chain7, and tree16 shapes (§2.7, §5.5)"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: wangLeverSpeculativeLLM2026a
    resource: zotero://select/items/@wangLeverSpeculativeLLM2026a
    title: "Lever: Speculative LLM Inference on Smartphones"
---

# Six phone drafters for a Qwen3-14B server verifier

This page records my own experiment. Every number without a paper footnote comes from the generated report `raw/experiments/drafter-evaluation.md`.[^drafter-evaluation] The runs took place from 2026-10-15 20:36 to 2026-10-16 03:45 KST: 37 live runs, all of which finished with status ok.[^drafter-evaluation] An updated version of the report, `raw/experiments/drafter-evaluation-server-shapes.md`, adds 5 server-only baseline runs with no phone, made on 2026-10-16: one at the SpecEdge shape (14:58 KST, spark2), and chain7 and tree16 with 2 repeats each (15:24–15:48 KST, spark4). It changes none of the phone-arm numbers.[^drafter-evaluation-server-shapes] A third report, `raw/experiments/drafter-evaluation-server-only-chain.md`, runs all six drafters server-only as chains on 2026-10-19; it has its own page, [Six drafters on the server GPU, chain7, no phone](server-only-chain-drafter-evaluation.md), and is summarized below.[^drafter-evaluation-server-only-chain]

## Goal

Compare six draft models for split [speculative decoding](../methods/speculative-decoding.md) with a phone drafter and a GPU verifier. Each drafter is measured in three tree shapes on the same 60 requests, and the comparison covers throughput, acceptance, phone draft time, network traffic, phone memory, and thermal state.[^drafter-evaluation]

## Setup

### One round

The phone drafts a chain or tree on its NPU and sends it to the server as rows: the seed (last committed token) plus every drafted node. The server runs one Qwen3-14B forward over all rows with a tree attention mask, accepts the longest path that matches greedy target decoding plus one bonus token, and returns the accepted count and the bonus token, plus target features for drafters that use them. Round 0 is the prefill round, and all later rounds are steady rounds.[^drafter-evaluation]

### Hardware and network

| Part | What |
|---|---|
| Phone (drafts) | Samsung Galaxy S25 (Snapdragon 8 Elite, Hexagon v79 NPU). The draft runs on the NPU (`HTP0`) through the Hexagon backend of [llama.cpp](../methods/llama-cpp.md), flash attention on, 6 CPU threads, host-side top-k scoring. |
| Server (verifies) | NVIDIA DGX Spark (GB10), `spark4` for 34 runs and `spark2` for 3 runs (PARD-2 repeat 1). specedge `batch_server.py`, one GPU, batch size 1, one client. |
| Network | Direct over the lab WiFi, no tunnel or relay, gRPC protobuf. |

All rows: [^drafter-evaluation]

### Target and drafters

The target is `Qwen/Qwen3-14B-FP8` (FP8 weights, fp16 activations, thinking mode off). Every draft model is converted to GGUF, quantized to pure Q4_0, and run through the same llama.cpp build (`dbe1a6c`).[^drafter-evaluation]

| Drafter | Source checkpoint | Phone file | Drafting | Sent back to the phone each round |
|---|---|---|---|---|
| Qwen3-0.6B | `Qwen/Qwen3-0.6B` | 409 MB | AR tree, one `llama_decode` per level | tokens only |
| [EAGLE-3](../methods/eagle-3.md) | `deepseek-ai/eagle3_qwen3_14b_ttt7` (DeepSpec) | 1108 MB, full-vocabulary LM head | AR tree with target features | 5120 × fp16 feature row per committed token (10 KB) |
| [DFlash](../methods/dflash.md) | `deepseek-ai/dflash_qwen3_14b_block7` | 1741 MB | block draft: 7 positions in one decode, tree built on the host from per-position top-k | 5120 × fp16 encoder feature row per committed token (10 KB) |
| [DSpark](../methods/dspark.md) | `deepseek-ai/dspark_qwen3_14b_block7` | 1741 MB + 42 MB Markov head | block draft, plus the Markov head on the host CPU | 5120 × fp16 encoder feature row per committed token (10 KB) |
| [PARD](../methods/pard.md)-1 | `amd/PARD-Qwen3-0.6B` | 409 MB | block draft: one causal decode of [accepted tokens, K−1 mask tokens] | tokens only |
| PARD-2 (target-dependent) | `amd/PARD2-Qwen3-14B` | 409 MB | block draft whose input is token embedding + a 1024-wide target feature | 1024 × fp16 feature row per committed token (2 KB) |

All rows: [^drafter-evaluation]

- For PARD-2 the server taps target layers 17, 25, and 33 plus the final post-norm and projects them from 20480 to 1024 with `target_proj` (40 MB, on the server).[^drafter-evaluation]
- Feature drafters also receive one feature row per prompt token in round 0 (≈279 prompt tokens on average, so 2.8 MB per request at width 5120 and 0.56 MB for PARD-2).[^drafter-evaluation]
- PARD-2's target-independent mode was dropped before the live runs, because the offline oracle on 10-15 gave it 2.0 tok/round as a chain.[^drafter-evaluation]

### Workload

- [Spec-Bench](../benchmarks/spec-bench.md), 480 prompts, every 8th prompt, so 60 requests: 10 each from [MT-Bench](../datasets/mt-bench.md) (8 sub-categories pooled), translation, summarization, qa, math_reasoning, and rag. The same 60 requests run in the same order in every arm.[^drafter-evaluation]
- Temperature 0 (greedy), `max_new_tokens` 64, `max_len` 2048, seed 42, one client, batch size 1.[^drafter-evaluation]
- `cache_prefill: true`: the server loads each prompt's prefill KV from a cache, so TTFT excludes the server's prompt compute. Proactive drafting is off in every arm.[^drafter-evaluation]

### Tree shapes

| Shape | Block drafters (PARD-1/2, DFlash, DSpark) | AR drafters (Qwen3-0.6B, EAGLE-3) | Rows verified per round |
|---|---|---|---|
| chain7 | depth 7, width 1, budget 7 | 1 beam, depth 7, width 1, budget 7 | 8 |
| tree16 (matched) | depth 7, width 8, budget 16 | 8 beams × depth 6 × width 4, budget 16 | 17 |
| own-best | DFlash, DSpark: depth 7, width 8, budget 32; PARD-1, PARD-2: depth 8, width 8, budget 32 | 8 beams × depth 6 × width 8, budget 32 | 33 |

All rows: [^drafter-evaluation]

- Block trees are built best-first on the host from each position's top-k, under the budget. DFlash and DSpark produce at most 7 positions per block, and PARD can draft 8.[^drafter-evaluation]
- The own-best shapes were chosen offline with an acceptance oracle that replays each drafter on the host (same Q4_0 GGUF, CPU) against the recorded greedy target outputs and target features of the same 60 requests, combined with a modelled round time. The cost model takes verify time as 92 ms at 8 rows, 99.5 at 17, 101.5 at 25, and 106 at 33, plus 11 ms server overhead and 16 ms network. Budget 64 tied with or beat budget 32 only through an extrapolated 65-row verify time, so budget 32 was taken.[^drafter-evaluation]

### Server-only baselines

Reference runs with no phone: specedge's `server_only.py` drafts and verifies on one GPU in one process.[^drafter-evaluation-server-shapes]

Common to every server-only run:

| Part | What |
|---|---|
| Target | `Qwen/Qwen3-14B-FP8`, same FP8 patch as the phone arms' server |
| Draft | `Qwen/Qwen3-0.6B` in **fp16** on the GPU (the phone arms use Q4_0 on the NPU) |
| Workload | the same 60 Spec-Bench requests, temperature 0, 64 new tokens, batch size 1 |
| Prefill | no prefill cache; round 0 computes the prompt, and steady metrics exclude it |
| GPU | both models on `cuda:0`; GPU checked empty before every run |

All rows: [^drafter-evaluation-server-shapes]

| Run | Shape | Rows verified | Node | Repeats |
|---|---|---|---|---|
| SpecEdge shape | AR tree, 32 beams × depth 4 × width 16, budget 32 | 33 | spark2 | 1 |
| chain7 | 1 × 7 × 1, budget 7 (the phone AR chain7 shape) | 8 | spark4 | 2 |
| tree16 | 8 beams × depth 6 × width 4, budget 16 (the phone AR tree16 shape) | 17 | spark4 | 2 |

All rows: [^drafter-evaluation-server-shapes]

- The chain7 and tree16 shapes are exactly the phone AR shapes from `harness/arms.yaml`. `server_only.py` reads the same four shape parameters as the phone client.[^drafter-evaluation-server-shapes]
- The Python tree builder drops any candidate whose cumulative score is below −10, and the phone's C++ builder has no such floor. In chain7 this left 7 of 1188 rounds with fewer than 8 rows (5–7). In tree16 every round verified exactly 17 rows.[^drafter-evaluation-server-shapes]
- A logging patch records the real row count and draft depth per round. These values are computed after both timers stop, so the timings are unaffected.[^drafter-evaluation-server-shapes]

Round time is draft + target end-to-end time, with no network and no client-side post-processing. Its accepted count includes the bonus token, as on the phone.[^drafter-evaluation-server-shapes]

## Procedure

- 18 arms (6 drafters × 3 shapes), 2 repeats each, plus a third DFlash tree16 repeat on the newer binary: 37 runs, each with 60 requests and server rows joined for every round. Repeats are interleaved, so every arm runs once before any runs a second time.[^drafter-evaluation]
- Before each arm the harness aborts if any foreign process is on the server GPU, starts this arm's server config, wakes the phone, and waits until the phone's `thermal_zone0` is at or below 36 °C (0 to 440 s). Telemetry is sampled on the phone every 5 s.[^drafter-evaluation]
- tok/s (steady) is computed per request as Σ committed tokens / Σ round time over its steady rounds, then averaged over the 60 requests, then over repeats. tok/round includes the bonus token and is pooled over all steady rounds of an arm. Network time is client wait minus server end-to-end time.[^drafter-evaluation]
- Two client binaries were used (`b300fed`, and `8f6353b`, which adds the PARD-2 client mode), and two server commits. A server startup stall (a deadlock while loading the tokenizer) happened about 8 times and was handled by restarting the server before any request.[^drafter-evaluation]

## Results

### Throughput (tok/s, steady, mean over repeats)

| Drafter | chain7 | tree16 | own-best | own-best, network-normalised |
|---|---|---|---|---|
| PARD-2 | 24.9 | **29.3** | **30.0** | 30.9 |
| DFlash | 25.5 | 27.9 | 28.8 | 29.4 |
| DSpark | **26.5** | 28.3 | 28.2 | 29.0 |
| PARD-1 | 22.1 | 26.7 | 26.7 | 27.7 |
| Qwen3-0.6B | 15.6 | 16.6 | 18.5 | 19.7 |
| EAGLE-3 | 13.0 | 15.9 | 17.6 | 18.2 |

All rows: [^drafter-evaluation]

The network-normalised column replaces each round's network time with 14.5 ms, the median over all 37 runs.[^drafter-evaluation] The 95% bootstrap intervals of repeat 1 are about ±2 tok/s wide, for example 27.3..31.3 for PARD-2 tree16 and 25.8..30.1 for DFlash tree16.[^drafter-evaluation]

### Acceptance and draft cost per round

| Drafter | tok/round chain → tree16 → own | P(k=0) chain → tree16 → own | draft ms chain → tree16 → own | verify ms chain → tree16 → own |
|---|---|---|---|---|
| PARD-2 | 3.34 → 4.21 → 4.58 | 0.252 → 0.050 → 0.045 | 27.8 → 29.3 → 30.2 | 103.2 → 106.4 → 112.0 |
| DFlash | 3.45 → 4.15 → 4.37 | 0.205 → 0.089 → 0.071 | 30.4 → 30.6 → 30.6 | 105.1 → 110.8 → 115.3 |
| DSpark | 3.83 → 4.64 → 5.02 | 0.214 → 0.080 → 0.067 | 38.8 → 45.8 → 54.2 | 104.3 → 110.0 → 115.6 |
| PARD-1 | 2.76 → 3.54 → 3.81 | 0.363 → 0.121 → 0.110 | 21.9 → 22.8 → 23.2 | 101.6 → 104.9 → 110.2 |
| Qwen3-0.6B | 3.11 → 4.06 → 4.53 | 0.354 → 0.144 → 0.092 | 84.9 → 116.4 → 110.4 | 101.5 → 104.7 → 109.7 |
| EAGLE-3 | 2.71 → 3.60 → 3.92 | 0.408 → 0.193 → 0.147 | 114.5 → 114.8 → 104.0 | 102.8 → 108.2 → 111.1 |

All rows: [^drafter-evaluation]

- DSpark has the highest tok/round in every shape. Its Markov head on the host CPU takes 8.48 ms (chain), 15.49 ms (tree16), and 23.68 ms (own-best) per round, which is why its own-best tree is no faster than its matched tree.[^drafter-evaluation]
- The block drafters draft a whole tree in one decode, 22–54 ms including host-side work. Qwen3-0.6B and EAGLE-3 run one decode per tree level, 85–116 ms in total.[^drafter-evaluation]
- PARD-2's draft has a latency tail (p95 49–55 ms against a 28–30 ms mean), and about 6–8 ms of its draft time is spent outside the NPU decode, which is consistent with building the input embeddings on the host.[^drafter-evaluation]
- Mean round time in tree16: PARD-2 153.1 ms, DFlash 162.4, DSpark 178.1, PARD-1 141.8, Qwen3-0.6B 267.4, EAGLE-3 246.3. Server forward is 93.8–99.9 ms of it.[^drafter-evaluation]
- Survival at full depth 7 in chain7 (P(k_draft = 7)): DSpark 0.160, DFlash 0.104, PARD-2 0.093, Qwen3-0.6B 0.113, EAGLE-3 0.081, PARD-1 0.062.[^drafter-evaluation]

### Network traffic, latency, and memory (tree16)

| Drafter | KB up / round | KB down / token, steady | prompt features KB / request | TTFT p50 ms | round gap p50 ms | client VmHWM MB | peak client DMA-BUF MB |
|---|---|---|---|---|---|---|---|
| PARD-2 | 68.5 | 2.0 | 558 | 133 | 144 | 291 | 885 |
| DSpark | 68.5 | 10.0 | 2790 | 160 | 174 | 678 | 1707 |
| DFlash | 68.5 | 10.0 | 2790 | 160 | 157 | 592 | 1707 |
| PARD-1 | 68.5 | 0.0 | 0 | 176 | 140 | 250 | 885 |
| Qwen3-0.6B | 68.5 | 0.0 | 0 | 285 | 255 | 538 | 885 |
| EAGLE-3 | 68.5 | 10.0 | 2790 | 169 | 243 | 704 | 1094 |

All rows: [^drafter-evaluation]

- Upload is set by the row count, not the drafter: 32.3 / 68.5 / 133 KB per round for 8 / 17 / 33 rows.[^drafter-evaluation]
- With round 0 counted, download is about 56 KB/token for DFlash, DSpark, and EAGLE-3 and 11.3 KB/token for PARD-2 at 64 new tokens.[^drafter-evaluation]
- Qwen3-0.6B's resident memory grows from 196 MB (chain) to 538 MB (tree16) and 457 MB (own-best), because each beam keeps its own KV sequence.[^drafter-evaluation]

### By category (tok/s, own-best)

| Drafter | mt_bench | translation | summarization | qa | math_reasoning | rag |
|---|---|---|---|---|---|---|
| PARD-2 | 33.5 | 26.3 | 23.7 | 26.2 | 43.5 | 26.6 |
| DSpark | 31.8 | 25.8 | 21.4 | 23.9 | 39.7 | 26.7 |
| DFlash | 31.0 | 28.0 | 21.1 | 23.3 | 41.7 | 27.5 |
| PARD-1 | 30.5 | 20.5 | 20.6 | 21.3 | 40.9 | 26.4 |
| Qwen3-0.6B | 19.5 | 20.1 | 14.0 | 15.3 | 25.2 | 16.8 |
| EAGLE-3 | 18.7 | 14.9 | 14.3 | 13.8 | 27.4 | 16.3 |

All rows: [^drafter-evaluation]

- Every drafter is fastest on math_reasoning. PARD-1 is weak on translation: 2.07–2.81 tok/round against 3.2–4.1 for DFlash and DSpark.[^drafter-evaluation]
- Qwen3-0.6B accepts unusually well on translation (3.61 / 4.11 / 4.64 tok/round), but is too slow per round for this to matter.[^drafter-evaluation]

### Server-only at the phone shapes (shape for shape)

The same draft model (Qwen3-0.6B) and the same tree shape, on the server GPU in fp16 against the phone NPU in Q4_0. Means over 2 repeats each.[^drafter-evaluation-server-shapes]

| Shape | Run | tok/s | tau | P(k=0) | draft ms | verify ms | network ms (mean) | pre/post ms | round ms |
|---|---|---|---|---|---|---|---|---|---|
| chain7 | server-only, GPU fp16 | 17.0 | 3.37 | 0.352 | 111.6 | 101.3 | 0 | 0.0 | 212.8 |
| chain7 | phone, NPU Q4_0 | 15.6 | 3.11 | 0.354 | 84.9 | 101.5 | 27.7 | 12.9 | 227.0 |
| tree16 | server-only, GPU fp16 | 21.6 | 4.14 | 0.171 | 93.5 | 105.3 | 0 | 0.0 | 198.8 |
| tree16 | phone, NPU Q4_0 | 16.6 | 4.06 | 0.144 | 116.4 | 104.7 | 31.1 | 15.2 | 267.4 |

All rows: [^drafter-evaluation-server-shapes]

- **Moving the draft to the server is worth ×1.09 as a chain and ×1.30 in tree16, and it still does not catch the phone block drafters.** The best server-only run (tree16, 21.6 tok/s) is below all 12 phone block-drafter arms (22.1–30.0). The closest is PARD-1 chain7 at 22.1, and PARD-2 own-best is +39%.[^drafter-evaluation-server-shapes]
- **Where the time goes.** Verify is the same on both sides (101.3 vs 101.5 ms in chain7, 105.3 vs 104.7 in tree16). The server-only round saves the network (27.7 / 31.1 ms mean) and the phone's pre/post-processing (12.9 / 15.2 ms). As a chain the GPU drafts slower than the NPU (111.6 vs 84.9 ms); in tree16 it drafts faster (93.5 vs 116.4 ms).[^drafter-evaluation-server-shapes]
- **Per level, the GPU costs about 15.6–15.9 ms with 1 row or with 8**, so its draft is bound by overhead ("Python tree code, non-graph forward" in the report). The NPU costs about 12.1 ms per level as a chain and 19.4 ms with 8 beams × width 4. That is why the location gain is small for the chain and large for the tree.[^drafter-evaluation-server-shapes]
- **The fp16 draft accepts slightly more than Q4_0.** In chain7, 3.37 against 3.11 tok/round, with identical outputs on all 60 requests, so the difference is the draft alone. In tree16, 4.14 against 4.06, on outputs that agree on 41/60 requests.[^drafter-evaluation-server-shapes]
- **By category.** In tree16 server-only is faster in all six categories, from ×1.09 (math_reasoning) to ×1.49 (summarization). In chain7 it is faster in five; on mt_bench it is ×0.89, although tok/round and round time are the same, because the phone's per-request tok/s spreads wider over the 10 requests.[^drafter-evaluation-server-shapes]
- **Output agreement.** Server-only chain7 matches the phone chain7 on 60/60 requests, and server-only tree16 matches the phone tree16 on 41/60. Server-only chain7 and tree16 agree on 28/60, the same chain-vs-tree divergence as the phone arms (28–33/60). It depends on the verified row count, not on where the drafter runs.[^drafter-evaluation-server-shapes]
- Repeats of each server-only arm are identical round for round, with the same outputs, and tok/s within 0.1.[^drafter-evaluation-server-shapes]

### Server-only at the SpecEdge shape

| Run | tok/s (95% CI) | tok/round | P(k=0) | draft ms | verify ms | round ms |
|---|---|---|---|---|---|---|
| Server-only, Qwen3-0.6B fp16, 32 × 4 × 16, budget 32 (1 run) | 21.3 (20.6..22.1) | 3.74 | 0.123 | 67.5 | 111.5 | 179.1 |
| Phone Qwen3-0.6B chain7 (2) | 15.6 | 3.11 | 0.354 | 84.9 | 101.5 | 227.0 |
| Phone Qwen3-0.6B tree16 (2) | 16.6 | 4.06 | 0.144 | 116.4 | 104.7 | 267.4 |
| Phone Qwen3-0.6B own-best (2) | 18.5 | 4.53 | 0.092 | 110.4 | 109.7 | 268.1 |
| Phone PARD-2 own-best, fastest arm (2) | 30.0 | 4.58 | 0.045 | 30.2 | 112.0 | 163.6 |

Server-only row: [^drafter-evaluation-server-shapes] Phone rows: [^drafter-evaluation]

Server-only by category (tok/s / tok/round over all rounds, as the phone category tables pool it): mt_bench 21.0 / 3.76, translation 23.4 / 4.10, summarization 20.4 / 3.66, qa 18.9 / 3.36, math_reasoning 23.9 / 4.26, rag 20.3 / 3.69.[^drafter-evaluation-server-shapes]

- **Every phone block-drafter arm beats this run, and no phone Qwen3-0.6B arm does.** All 12 block-drafter arms run at 22.1–30.0 tok/s against 21.3. PARD-2 own-best is faster in every category, from +12% on translation (26.3 vs 23.4) to +82% on math_reasoning (43.5 vs 23.9).[^drafter-evaluation-server-shapes]
- **Shorter round, lower acceptance than the phone's own-best tree.** This run is +15% over the best phone Qwen3-0.6B arm (18.5) and +37% over its chain (15.6). The same model drafts in 67.5 ms on the GPU against 85–116 ms on the phone NPU, and the server-only round has no network time. But it accepts 3.74 tok/round against 4.53 for the phone own-best tree: the server-only tree is only 4 deep, and half its rounds (P(full depth) 0.502) accept the whole depth.[^drafter-evaluation-server-shapes]
- By category, server-only beats every phone Qwen3-0.6B arm except on math_reasoning, where the phone own-best is faster (25.2 vs 23.9) thanks to 6.12 tok/round against 4.26.[^drafter-evaluation-server-shapes]
- specedge's own metric reports 20.9 tok/s and an acceptance of 3.78 for this run. Its throughput is the pooled tok/s, not the per-request mean the report uses, and its acceptance includes round 0.[^drafter-evaluation-server-shapes]

### Server-only chain7 with all six drafters

On 2026-10-19 each drafter was re-implemented in PyTorch bf16 and run as a chain7 on the same GB10 as the Qwen3-14B-FP8 target, in one process with no phone and no network, on the same 60 requests (2 repeats each, cold prefill). Full details are on [Six drafters on the server GPU, chain7, no phone](server-only-chain-drafter-evaluation.md).[^drafter-evaluation-server-only-chain]

| Drafter | Server-only tok/s | Phone chain7 tok/s | Server / phone | Server tok/round | Phone tok/round | Server draft ms | Phone draft ms |
|---|---|---|---|---|---|---|---|
| PARD-2 | 34.0 | 24.9 | 1.36× | 3.50 | 3.34 | 15.6 | 27.8 |
| DSpark | 33.9 | 26.5 | 1.28× | 3.90 | 3.83 | 27.2 | 38.8 |
| DFlash | 31.0 | 25.5 | 1.22× | 3.43 | 3.45 | 24.2 | 30.4 |
| PARD-1 | 28.0 | 22.1 | 1.27× | 2.86 | 2.76 | 13.0 | 21.9 |
| Qwen3-0.6B | 20.4 | 15.6 | 1.31× | 3.42 | 3.11 | 86.4 | 84.9 |
| EAGLE-3 | 17.2 | 13.0 | 1.32× | 2.81 | 2.71 | 88.8 | 114.5 |

All rows: [^drafter-evaluation-server-only-chain]

- **Every drafter is faster server-only.** Verify takes 98.2–100.2 ms per round against the phone's client wait of 114.8–129.2 ms, and five of the six drafters also draft faster on the GPU.[^drafter-evaluation-server-only-chain]
- **Three server-only chains beat the best phone arm** (PARD-2 own-best, 30.0 tok/s): PARD-2 34.0, DSpark 33.9, and DFlash 31.0.[^drafter-evaluation-server-only-chain]
- **The block-vs-AR gap holds on the GPU**: 28.0–34.0 against 17.2–20.4 tok/s.[^drafter-evaluation-server-only-chain]
- **Implementation matters for the Qwen3-0.6B baseline.** At the same chain7 shape this code gives 20.4 tok/s (86.4 ms draft), against 17.0 tok/s (111.6 ms draft) for the 10-16 `server_only.py` run above.[^drafter-evaluation-server-only-chain]

### Validity checks

- **Repeatability.** In every arm, all repeats produced identical round counts and committed-token counts (for example DFlash tree16: 912 rounds and 3600 tokens in all three repeats). The tok/s spread between repeats is at most 1.5 tok/s and usually ≤ 0.7.[^drafter-evaluation]
- **Node and binary.** PARD-2 on spark2 and spark4 gives identical rounds and tok/s within 0.7. Repeats on the newer binary reproduce the older one round for round.[^drafter-evaluation]
- **Oracle vs live.** 11 of the 15 scored (drafter, shape) pairs agree within ±0.05 tok/round. The largest gap is DSpark own-best (5.13 oracle, 5.02 live). Live is never more than 0.03 above the oracle.[^drafter-evaluation]
- **Output agreement.** All four feature-drafter chains produce identical outputs on all 60 requests. The two plain-server chains (PARD-1, Qwen3-0.6B) match each other and match the feature-drafter chains on 53/60. Tree arms match the chain outputs on only 28–33 of 60 requests. The report attributes this to the FP8 verifier, whose logits shift with the batch's row count and flip near-tied argmaxes, but states that a tree-verify bug has not been ruled out. See [Why do tree-verified outputs diverge from chain outputs at temperature 0?](../questions/fp8-verifier-tree-output-divergence.md).[^drafter-evaluation]
- **Thermal state.** Every run started at tz0 ≤ 36.5 °C. tz0 peaked at 47–54 °C for block drafters and 57–65 °C for the AR drafters, and EAGLE-3's NPU reached 91–93 °C in tree16. Prime-core frequency caps fell as low as 1.69 GHz (EAGLE-3) against 4.47 GHz uncapped, but repeats with different cap levels give the same tok/s.[^drafter-evaluation]

## Interpretation

The report's main findings:[^drafter-evaluation]

1. Block drafters beat AR drafters by about 1.6–1.8×, because they draft a whole tree from one decode and the AR drafters' acceptance is not high enough to pay for one decode per level. See [Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU](../results/block-drafters-vs-ar-drafters-on-phone-npu.md).
2. PARD-2 is the best drafter with a tree, and DSpark the best chain drafter. The top three are within 2 tok/s of each other in every shape. PARD-2 has the lowest TTFT and downloads 5× less than DFlash, DSpark, and EAGLE-3.
3. PARD-1 is the best drafter that needs nothing from the server: no server-side drafter code and close to 0 bytes downloaded per token.
4. Own-best trees help the AR drafters (+11%) but barely change the block drafters (−0.4% to +3%).
5. DSpark's Markov head costs as much as it gains.

Against the papers:

- **DSpark vs DFlash.** The DSpark paper reports an 18.3% higher macro-average accepted length than DFlash on Qwen3-14B (temperature 1.0, chain, other benchmarks).[^chengDSparkConfidenceScheduledSpeculative2026] Here the chain7 gain is 3.83 against 3.45 tok/round, about 11% (my arithmetic).[^drafter-evaluation] The direction agrees. The paper's server-side finding that longer drafts add only 0.2% to 1.3% to round latency at batch size 128[^chengDSparkConfidenceScheduledSpeculative2026] does not carry over: on the phone the host Markov head adds 8.48 to 23.68 ms per round.[^drafter-evaluation]
- **PARD-2 vs PARD.** The PARD-2 paper reports $\tau$ 6.91 for PARD-2 (target-dependent) against 5.14 for PARD on Qwen3-14B (A100, draft length 16, no tree).[^anPARD2TargetAlignedParallel2026] Here the chain7 values are 3.34 against 2.76 tok/round.[^drafter-evaluation] The direction agrees. The PARD-2 paper reports DFlash only for Qwen3-8B,[^anPARD2TargetAlignedParallel2026] so there is no paper number for the DFlash-vs-PARD-2 order on Qwen3-14B. Here DFlash accepts more as a chain (3.45 against 3.34) and PARD-2 more in both trees.[^drafter-evaluation]
- **Flat draft cost of parallel drafters.** PARD states that a parallel draft costs one pass regardless of the number of draft tokens.[^anPARDAcceleratingLLM2025] Here PARD-1's draft time goes from 21.9 to 23.2 ms and DFlash's from 30.4 to 30.6 ms between chain7 and the budget-32 tree.[^drafter-evaluation]
- **EAGLE-3 against a Qwen3-0.6B draft on a phone.** Lever measures the opposite order: as a fixed 8-token chain with a flash-resident Qwen3-8B on a OnePlus 12, its EAGLE3 draft reaches 1.206 tokens/s against 0.840 for a Qwen3-0.6B draft.[^wangLeverSpeculativeLLM2026a] Here Qwen3-0.6B is ahead of EAGLE-3 in every shape (15.6 against 13.0 tok/s as a chain).[^drafter-evaluation] The settings differ in almost every respect: Lever verifies on the phone NPU and trains its own EAGLE-3 drafts,[^wangLeverSpeculativeLLM2026a] while this experiment verifies on a server and uses the DeepSpec ttt7 checkpoint with a full-vocabulary head.[^drafter-evaluation] Recorded on [EAGLE-3](../methods/eagle-3.md) under Contradictions.
- **SpecEdge's server-only baseline.** SpecEdge's server-only tree speculative decoding for Qwen3 14B with a 0.6B draft generates 3.87±1.41 tokens per verification on multi-turn bench and 3.79±1.48 on translation, at temperature 0.7 on an A100 with a draft tree of size 32.[^parkSpecEdgeScalableEdgeAssisted2025] My server-only run gives 3.74 tok/round overall (3.76 on mt_bench, 4.10 on translation) at temperature 0 on a GB10.[^drafter-evaluation-server-shapes] The values are close, but the temperature, hardware, and tree search differ: SpecEdge's server-only baseline uses the optimal draft tree depth found by exhaustive search.[^parkSpecEdgeScalableEdgeAssisted2025]
- **My earlier live DFlash sweep.** On 2026-10-02 DFlash at depth 7, width 8, budget 16 reached 4.51 tok/round and 28.30 tok/s on 15 SpecBench requests ([On-device draft cost on the Galaxy S25 Hexagon NPU](npu-draft-cost-profiling-galaxy-s25.md)). Here the same shape gives 4.15 tok/round and 27.9 tok/s on 60 requests.[^drafter-evaluation] The request sets differ, so the two numbers are not comparable one to one.

## Limitations

- TTFT uses cached prefill and excludes the server's prompt compute. The planned cold-prefill side pass was not run.[^drafter-evaluation]
- Single client and batch size 1, so nothing is said about server throughput under concurrency.[^drafter-evaluation]
- 64 new tokens per request. Longer generations would weight steady-state speed more and would run the phone hotter.[^drafter-evaluation]
- No energy measurement, by decision on 10-15.[^drafter-evaluation]
- The own-best shapes were chosen with a modelled round time, not a live search. Shapes outside the modelled sweep (DSpark with fewer Markov rows, budget 24) were not tried.[^drafter-evaluation]
- One phone and one WiFi network: network time has a median of 10–18 ms with p95 up to 115 ms.[^drafter-evaluation]
- No vanilla autoregressive baseline was run, so the results give tok/s, not speedup over autoregressive decoding. The server-only baseline is itself speculative decoding.[^drafter-evaluation-server-shapes]
- The server-only draft is fp16 rather than Q4_0, so the shape-for-shape comparison mixes the drafter's location with its quantization. There is no server-only run at the own-best (budget-32) phone shapes.[^drafter-evaluation-server-shapes] The 10-19 server-only runs of all six drafters are bf16 and chain only, with no server-only trees for the block or feature drafters.[^drafter-evaluation-server-only-chain]

## Next steps

From the report's limitations and checks:[^drafter-evaluation]

- Run the cold-prefill TTFT arms (`configs/server/*-nocache.yaml`).
- Compare tree-arm outputs against a target-only greedy run with the same row count, to rule out a tree-verify bug.
- Try DSpark with fewer Markov rows and a budget of 24.
- Fix the server startup stall by starting the child process with the spawn method.
- ~~Run server-only on the phone shapes (chain7, tree16).~~ Done on 2026-10-16; see above.
- Run the server-only draft in Q4_0, or the phone draft in fp16, to separate the drafter's location from its quantization.
- ~~Run the other five drafters server-only.~~ Done as chains on 2026-10-19 ([Six drafters on the server GPU, chain7, no phone](server-only-chain-drafter-evaluation.md)). Server-only trees for the block and feature drafters are still open.[^drafter-evaluation-server-only-chain]

## Related

- [On-device draft cost on the Galaxy S25 Hexagon NPU](npu-draft-cost-profiling-galaxy-s25.md) (my earlier profiling of draft cost on the same phone)
- [Six drafters on the server GPU, chain7, no phone](server-only-chain-drafter-evaluation.md) (the server-only counterpart of the chain7 arms)
- [Drafting on the server GPU instead of the phone NPU](../results/server-vs-phone-draft-location.md)
- [Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU](../results/block-drafters-vs-ar-drafters-on-phone-npu.md)
- [Why do tree-verified outputs diverge from chain outputs at temperature 0?](../questions/fp8-verifier-tree-output-divergence.md)
- [What is the smallest block drafter that keeps acceptance with a sequential head?](../questions/minimum-drafter-depth-with-sequential-head.md)
- [Was PARD-2's Qwen3-14B drafter trained to run without target features?](../questions/pard-2-qwen3-14b-feature-gating.md)
- [Can a block drafter be narrower than its target?](../questions/narrow-block-drafter.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)
- [Why parallel drafters beat EAGLE-3](../analyses/why-parallel-drafters-beat-eagle-3.md)
- Methods: [PARD](../methods/pard.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE-3](../methods/eagle-3.md), [Tree-based speculation](../methods/tree-based-speculation.md), [llama.cpp](../methods/llama-cpp.md)
- Benchmark: [Spec-Bench](../benchmarks/spec-bench.md)
- [Quantization of the target and the draft in speculative decoding](../analyses/quantization-in-speculative-decoding.md) and [How much acceptance does quantizing the draft or the target cost?](../questions/quantization-and-acceptance.md) (Q4_0 against fp16/bf16 drafts)

[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^drafter-evaluation-server-shapes]: My drafter evaluation report with the server-only baselines, runs of 2026-10-16
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^wangLeverSpeculativeLLM2026a]: Wang et al. 2026
