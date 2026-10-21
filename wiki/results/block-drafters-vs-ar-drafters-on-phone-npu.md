---
type: Result
title: Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU
description: In my phone-drafts, server-verifies evaluation for Qwen3-14B, the one-decode block drafters (PARD-1, PARD-2, DFlash, DSpark) reach 26.7-30.0 tok/s with their best trees against 17.6-18.5 for the per-level autoregressive drafters (Qwen3-0.6B, EAGLE-3).
tags: [speculative-decoding, mobile-npu, mobile-specedge, parallel-drafting, draft-model]
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
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU

## Claim

With a Galaxy S25 NPU drafting and a DGX Spark verifying Qwen3-14B, block drafters beat autoregressive (AR) drafters by about 1.6–1.8× in tokens per second.[^drafter-evaluation]

## Conditions

- Phone: Samsung Galaxy S25 (Snapdragon 8 Elite, Hexagon v79 NPU), llama.cpp Hexagon backend, every drafter in pure Q4_0. Server: NVIDIA DGX Spark (GB10), `Qwen/Qwen3-14B-FP8`, batch size 1, one client. Direct lab WiFi.[^drafter-evaluation]
- 60 Spec-Bench requests, temperature 0, 64 new tokens, cached prefill, 2 repeats per arm (3 for DFlash tree16).[^drafter-evaluation]
- Block drafters: PARD-1, PARD-2 (target-dependent), DFlash, DSpark. AR drafters: Qwen3-0.6B and EAGLE-3 (DeepSpec ttt7 checkpoint).[^drafter-evaluation]
- Source: [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md).

## Numbers

tok/s, steady state, mean over requests and then over repeats:

| Drafter | Kind | chain7 | tree16 | own-best (budget 32) | draft ms, tree16 |
|---|---|---|---|---|---|
| PARD-2 | block | 24.9 | 29.3 | 30.0 | 29.3 |
| DFlash | block | 25.5 | 27.9 | 28.8 | 30.6 |
| DSpark | block | 26.5 | 28.3 | 28.2 | 45.8 |
| PARD-1 | block | 22.1 | 26.7 | 26.7 | 22.8 |
| Qwen3-0.6B | AR | 15.6 | 16.6 | 18.5 | 116.4 |
| EAGLE-3 | AR | 13.0 | 15.9 | 17.6 | 114.8 |

All rows: [^drafter-evaluation]

- The block drafters draft a whole tree from one decode, in 22–54 ms including host-side work. The AR drafters run one decode per tree level, 85–116 ms in total.[^drafter-evaluation]
- The AR drafters' acceptance is not high enough to pay for that. In tree16, Qwen3-0.6B accepts 4.06 tok/round, close to DFlash's 4.15, but its mean round takes 267.4 ms against 162.4 ms.[^drafter-evaluation]
- Own-best trees help the AR drafters (+11%) but barely change the block drafters (−0.4% to +3%).[^drafter-evaluation]

## Comparisons

- Server verify time hardly differs between drafters at one shape (at most 6 ms), so the gap comes from the phone side of the round.[^drafter-evaluation]
- **Against server-only speculative decoding.** With the same Qwen3-0.6B model as an fp16 draft on the server GPU, server-only reaches 17.0 tok/s as a chain, 21.6 in the tree16 shape, and 21.3 at the SpecEdge shape (32 beams × depth 4 × width 16). Every phone block-drafter arm (22.1–30.0 tok/s) is still faster than the best of these. So moving the AR drafter to the server does not close the gap.[^drafter-evaluation-server-shapes] See [Drafting on the server GPU instead of the phone NPU](server-vs-phone-draft-location.md).
- **The gap also holds on the server GPU.** With all six drafters re-implemented in PyTorch bf16 and drafting beside the target as chain7, the block drafters reach 28.0–34.0 tok/s and the AR drafters 17.2–20.4. The AR drafters take 86–89 ms per round to draft on the GB10, as on the phone, and the block drafters 13–27 ms.[^drafter-evaluation-server-only-chain] **Inference.** So the gap comes from one decode per level, not from the phone NPU. The faster Qwen3-0.6B server-only chain here (20.4 tok/s) is still below every phone block-drafter arm (22.1–30.0).[^drafter-evaluation-server-only-chain] See [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md).
- **HyCo.** On a Galaxy S26 Ultra NPU, a four-pass autoregressive SLM tree (Gemma 4 E2B, 32 nodes) delivers 16.1 tokens/s for Gemma 4 26B-A4B, below the SLM alone at 26.4, while HyCo's one-pass hybrid tree delivers 35.0. The setting and metric differ, but the per-level cost points the same way. See [HyCo cuts server GPU time per token by 38.6% against server-side MTP on Spec-Bench](hyco-server-gpu-time-vs-cloud-mtp.md).[^baeHyCoHybridDrafting2026]
- The ratio is not stated as exact. The table gives, for example, 29.3 / 16.6 for the best block and best AR drafter in tree16 and 30.0 / 18.5 in own-best.[^drafter-evaluation]

## Related

- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md)
- [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md)
- [Why parallel drafters beat EAGLE-3](../analyses/why-parallel-drafters-beat-eagle-3.md)
- [PARD](../methods/pard.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE-3](../methods/eagle-3.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)

[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^drafter-evaluation-server-shapes]: My drafter evaluation report with the server-only baselines, runs of 2026-10-16
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
