---
type: Open Question
title: How fast can the server-only baseline go?
description: The same Qwen3-0.6B chain7 draft runs server-only at 17.0 tok/s with specedge's server_only.py and 20.4 tok/s with my later PyTorch chain code, and the later runs still leave most draft paths unoptimized, so the phone-versus-server comparison rests on a baseline whose ceiling is unknown.
tags: [speculative-decoding, server-only, mobile-specedge, draft-model, reproducibility]
sources:
  - id: drafter-evaluation-server-shapes
    resource: raw/experiments/drafter-evaluation-server-shapes.md
    title: "Drafter evaluation with server-only baselines at the SpecEdge, chain7, and tree16 shapes (§2.7, §5.5)"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
---

# How fast can the server-only baseline go?

## Question

When the drafter runs on the server GPU beside the Qwen3-14B-FP8 target, how much of the measured draft time is the drafter's real cost, and how much is the implementation? What throughput would a well-optimized server-only draft path reach?

## Why it matters

Server-only speculative decoding is the reference against which phone drafting is judged in my evaluation. The gain from moving the draft to the server changed from ×1.09 to ×1.31 for the same Qwen3-0.6B chain between two implementations.[^drafter-evaluation-server-shapes][^drafter-evaluation-server-only-chain] If the baseline can go further, the phone arms fall further behind on single-request throughput. See [Drafting on the server GPU instead of the phone NPU](../results/server-vs-phone-draft-location.md).

## Evidence so far

- **Two implementations, one configuration.** Qwen3-0.6B chain7, same 60 requests, same target: specedge `server_only.py` in fp16 gives 17.0 tok/s, 111.6 ms draft, 212.8 ms round; the 10-19 PyTorch chain code in bf16 (eager) gives 20.4 tok/s, 86.4 ms draft, 185.2 ms round.[^drafter-evaluation-server-only-chain]
- **The earlier path was overhead-bound.** With `server_only.py` the GPU cost about 15.6–15.9 ms per draft level with 1 row or with 8, which the 10-16 report attributes to "Python tree code, non-graph forward".[^drafter-evaluation-server-shapes]
- **A 1-row step is bound by weight reads.** In the 10-19 code a single-row Qwen3-0.6B step takes about 11.7 ms, at about 150 GB/s on bf16 GEMVs in torch on the GB10. A CUDA graph made it slower (13.2 against 11.7 ms per step in isolation), because the graph's attention reads a whole 256-key bucket.[^drafter-evaluation-server-only-chain]
- **Graphs help the block drafters.** The PARD block graph cut replay draft time from 15.2 to 12.6 ms (PARD-1) and from 18.7 to 15.4 ms (PARD-2).[^drafter-evaluation-server-only-chain]
- **Much is still unoptimized.** In the 10-19 runs the AR and EAGLE-3 steps are eager, DFlash and DSpark use eager PyTorch with SDPA, there are no fused kernels or quantized drafts, and the target runs without CUDA graphs.[^drafter-evaluation-server-only-chain]

## Conflicting claims

The ×1.09 (10-16) and ×1.31 (10-19) server-over-phone gains for the same Qwen3-0.6B chain7. Both are kept, with the explanation, on [Drafting on the server GPU instead of the phone NPU](../results/server-vs-phone-draft-location.md#contradictions).[^drafter-evaluation-server-shapes][^drafter-evaluation-server-only-chain]

## What would resolve it

1. Profile one Qwen3-0.6B draft step on the GB10 against its weight-read lower bound (weight bytes over achievable bandwidth).
2. Re-run the server-only chain with an optimized draft path: fused or graph-captured steps for the AR and EAGLE-3 drafters, graphs for DFlash and DSpark, and a graph-captured target.
3. Add server-only trees for the block and feature drafters, to compare with the phone's own-best trees.

## Related

- [Drafting on the server GPU instead of the phone NPU](../results/server-vs-phone-draft-location.md)
- [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md)
- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md)
- [Does speculative decoding help on a mobile NPU?](speculative-decoding-on-mobile-npu.md)

[^drafter-evaluation-server-shapes]: My drafter evaluation report with the server-only baselines, runs of 2026-10-16
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
