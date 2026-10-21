---
type: Experiment
title: On-device draft cost on the Galaxy S25 Hexagon NPU
description: My profiling of draft-model decode latency, memory, and energy on a Samsung Galaxy S25 NPU across 60 layer-by-width shapes, with the live DFlash depth sweep.
tags: [mobile-npu, on-device-inference, draft-model, speculative-decoding, mobile-specedge, dflash]
date: 2026-10-09
data_sources:
  - /Users/vafbaguio/kaist/ina/dflash-specedge/mobile-specedge/profiling/SUMMARY.md
  - /Users/vafbaguio/kaist/ina/daily-logs/10-02-26.md
sources:
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: caiYourNPUReady2026
    resource: zotero://select/items/@caiYourNPUReady2026
    title: "Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
---

# On-device draft cost on the Galaxy S25 Hexagon NPU

This page records my own measurements. The numbers are copied from the files in `data_sources`, which are outside `raw/`. Only the statements with a footnote come from papers.

## Goal

Find which draft-model shapes fit the mobile-server speculative decoding budget on the phone NPU, and what decides their latency.

## Setup

- Device: Samsung Galaxy S25 (SM-S938N, Snapdragon 8 Elite), measured 2026-10-09.
- Software: llama.cpp `ce8caa6e6` with the experimental Hexagon backend, through `LlamaCppEngine` (tree mode, host top-k, flash attention on, f16 KV, `GGML_HEXAGON_OPPOLL=1`, `GGML_HEXAGON_MM_PIPE_MIN=4`).
- NPU only (HTP0). CPU and OpenCL were not run.
- Models: random-weight models of 2 to 24 layers and widths 512, 1024, 1536, 2048, and 5120, at Q4_0 and Q8_0. Real Qwen3-0.6B Q4_0 and a random twin of the same shape agree: 9.50 vs 9.47 ms for one token.
- Budget: 125 ms (RTT 15 + verify 110), chain drafting, context depth 1024.

## Procedure

`sweep.py` phases `smoke`, `ops`, `grid`, `subset`, `dflash`, and `sustain`, then `inapp.py`, in `ina/dflash-specedge/mobile-specedge/profiling/`. The grid was measured at context depth 0. Seven shapes were also measured at depth 1024, 2048, and 4096. Sustained runs lasted 10 minutes each with USB unplugged.

## Results

### Latency follows weight bytes

Over the 30 Q4_0 shapes, single-token decode at depth 0 fits

    ms/token = 1.05 + 19.2 x (GB of weights read per token)        R² = 0.999

Layer count alone gives R² = 0.13. With a per-layer term:

    ms/token = 0.20 + 0.090 x layers + 19.0 x GB                   R² = 0.9999   (Q4_0)
    ms/token = 0.11 + 0.079 x layers + 18.0 x GB                   R² = 0.9998   (Q8_0, widths <= 2048)

| width | intercept (head + overhead) | per layer | intercept in layers |
|---|---|---|---|
| 512 | 1.27 ms | 0.099 ms | 12.8 |
| 1024 | 1.95 ms | 0.226 ms | 8.6 |
| 1536 | 2.68 ms | 0.407 ms | 6.6 |
| 2048 | 3.38 ms | 0.686 ms | 4.9 |
| 5120 | 8.34 ms | 3.624 ms | 2.3 |

Q8_0 costs 1.4 to 1.9 times Q4_0 per token at the same shape.

### The full-width output head

The width-5120 head (438 MB, 151,936 x 5120) costs 8.3 ms per token at Q4_0. Qwen3-0.6B measured on the same phone takes 9.5 ms for a whole step.

### Longest chain draft that fits 125 ms (Q4_0, cold / after 10 minutes)

| layers | 512 | 1024 | 1536 | 2048 | 5120 |
|---|---|---|---|---|---|
| 2 | 74 / 72 | 47 / 46 | 32 / 31 | 23 / 23 | 7 / 7 |
| 4 | 68 / 66 | 38 / 37 | 25 / 24 | 17 / 17 | 5 / 4 |
| 8 | 51 / 50 | 27 / 26 | 17 / 17 | 12 / 11 | 3 / 1 |
| 12 | 40 / 40 | 21 / 20 | 13 / 12 | 8 / 8 | 2 / 1 |
| 16 | 34 / 33 | 17 / 16 | 10 / 10 | 7 / 6 | 1 / 1 |
| 24 | 25 / 24 | 12 / 12 | 7 / 7 | 5 / 4 | 1 / 0 |

Depth 1024 and the throttled column are partly fitted, not measured for every shape. The source file states how.

### One 16-token pass against 16 sequential tokens (Q4_0, depth 0, ms)

| shape | 1 token | 16-token pass | pass / token | 16 sequential |
|---|---|---|---|---|
| 8 x 512 | 2.03 | 4.73 | 2.3 | 32.4 |
| 8 x 1024 | 3.74 | 6.95 | 1.9 | 59.8 |
| 8 x 1536 | 5.86 | 8.83 | 1.5 | 93.8 |
| 8 x 2048 | 8.71 | 12.27 | 1.4 | 139.4 |
| 8 x 5120 | 37.16 | 40.43 | 1.1 | 594.6 |

A DFlash block of 16 (random-weight DFlash GGUFs) costs the same as the causal 16-token pass on the same shape: 27.4 vs 27.8 ms (4 x 5120) and 45.0 vs 44.8 ms (8 x 5120), at depth 1024. One 16-token pass of 16 x 5120 Q4_0 is 77 ms cold.

### Row count (Q4_0, depth 0, ms)

| shape | 1 row | 2 rows | 4 rows | 8 rows | 16 rows (pass) |
|---|---|---|---|---|---|
| 8 x 1536 | 5.86 | 6.50 | 11.77 | 7.40 | 8.83 |
| 12 x 2048 | 11.52 | 12.83 | 23.27 | 13.75 | 15.95 |
| 8 x 5120 | 37.16 | 40.89 | 79.35 | 41.53 | 40.43 |

A 4-row decode costs about twice an 8-row decode.

### Memory

| model | file | NPU buffers (DMA-BUF) | process RSS | result |
|---|---|---|---|---|
| 16 x 5120 Q4_0 | 3.85 GB | 3.7 GB | 0.5 GB | runs every test |
| 12 x 5120 Q8_0 | 5.86 GB | 5.3 GB | 0.9 GB | runs every test (single row on CPU, 886 ms) |
| 24 x 5120 Q4_0 | 5.33 GB | 5.2 GB | 0.5 GB | loads; single token 95 ms; hung on the 16-token pass (15 min timeout) |

### Sustained runs and energy (Q4_0, depth 512, 10 minutes)

"Client duty" is 6 tokens then 125 ms idle. Idle power (about 0.5 W with the screen on) is not subtracted.

| run | ms/token min 1 | ms/token min 10 | slowdown | power | J/token | skin at end |
|---|---|---|---|---|---|---|
| 8 x 1536, client duty | 7.02 | 7.18 | 1.02 | 3.3 W | 0.093 | 40.9 C |
| 8 x 1536, 100% duty | 7.02 | 11.78 | 1.68 | 6.3 W | 0.060 | 48.1 C |
| 4 x 5120, client duty | 25.85 | 27.74 | 1.07 | 5.6 W | 0.267 | 47.2 C |
| 8 x 5120, client duty | 41.88 | 65.45 | 1.56 | 6.3 W | 0.440 | 50.1 C |

### Live DFlash depth sweep (2026-10-02, from the daily log)

Qwen3-14B target on the server, the 5-layer block-7 DFlash draft on HTP0, width-8 tree at budget 16, 15 SpecBench requests, 64 new tokens, server temperature 0.

| depth | accept | draft ms | server forward ms | network ms | tok/s |
|---|---|---|---|---|---|
| 7 | 4.51 | 30.3 | 98.2 | 19.1 | 28.30 |
| 6 | 4.38 | 30.0 | 98.5 | 23.2 | 26.85 |
| 5 | 4.07 | 29.8 | 99.7 | 19.0 | 25.39 |
| 4 | 3.69 | 55.2 | 98.4 | 22.9 | 19.65 |

The true token is the draft's first choice at block position 7 in only 21% of rounds.

## Interpretation

- On this NPU, draft latency is set by the weight bytes read per token, not by depth. On server GPUs, [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md) finds that draft latency is bottlenecked by model depth.[^yanDecodingSpeculativeDecoding2025] The two findings are for different hardware, so this is not a contradiction, but depth-based draft design rules do not carry over to this phone.
- A block drafter fits a much larger model than a chain drafter, because a 16-token pass costs 1.1 to 2.3 single-token steps. This matches the [DFlash](../papers/chenDFlashBlockDiffusion2026.md) cost model, in which a parallel drafter pays one pass regardless of the number of draft tokens.[^chenDFlashBlockDiffusion2026]
- A drafter cut from the target by layer removal alone keeps the full-width head, which by itself costs about one Qwen3-0.6B step.
- In the live runs the draft takes about 30 ms and the server forward about 98 ms, so acceptance is the larger lever.
- The NPU-against-CPU comparison is missing. The [mobile NPU study](../papers/caiYourNPUReady2026.md) finds CPU decode faster than NPU decode on its phone (55.7 tokens/s against 23.0 tokens/s for Qwen2.5-1.5B on a OnePlus 15).[^caiYourNPUReady2026]

## Next steps

- Run the same shapes on the CPU and on OpenCL.
- Retest 24 x 5120 Q4_0, which did not run because of battery level.
- Diagnose the NPU hang at width 5120 after many different batch shapes in one process.
- Measure acceptance for real drafters at these shapes. See [DFlash research directions for mobile SpecEdge](../analyses/dflash-research-directions-for-mobile-specedge.md). The live comparison of six released drafters is in [Six phone drafters for a Qwen3-14B server verifier](drafter-evaluation-qwen3-14b.md).

## Related

- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)
- [What is the smallest block drafter that keeps acceptance with a sequential head?](../questions/minimum-drafter-depth-with-sequential-head.md)
- [Can a block drafter be narrower than its target?](../questions/narrow-block-drafter.md)
- [DFlash](../methods/dflash.md), [Speculative decoding](../methods/speculative-decoding.md), [llama.cpp](../methods/llama-cpp.md)
- [Quantization of the target and the draft in speculative decoding](../analyses/quantization-in-speculative-decoding.md) (Q4_0 against Q8_0 cost)

[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^caiYourNPUReady2026]: Cai et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
