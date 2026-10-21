---
type: Result
title: Drafting on the server GPU instead of the phone NPU
description: Drafting on the server GPU instead of the phone NPU raises throughput for every drafter tested; as chain7 in PyTorch bf16 the six drafters gain ×1.22-1.36 and PARD-2, DSpark, and DFlash (31.0-34.0 tok/s) beat the best phone arm, while the earlier Qwen3-0.6B-only runs gave ×1.09 as a chain and ×1.30 in tree16.
tags: [speculative-decoding, mobile-npu, mobile-specedge, draft-model, server-only]
sources:
  - id: drafter-evaluation-server-shapes
    resource: raw/experiments/drafter-evaluation-server-shapes.md
    title: "Drafter evaluation with server-only baselines at the SpecEdge, chain7, and tree16 shapes (§2.7, §5.5)"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
---

# Drafting on the server GPU instead of the phone NPU

## Claim

For a single request, every drafter tested is faster when it drafts on the server GPU beside the Qwen3-14B-FP8 target than when it drafts on the phone NPU. As chain7, the six drafters gain ×1.22 to ×1.36, and the server-only PARD-2, DSpark, and DFlash chains beat the best phone arm of any shape.[^drafter-evaluation-server-only-chain] The earlier Qwen3-0.6B-only runs gave ×1.09 as a chain and ×1.30 in tree16, and stayed below every phone block drafter.[^drafter-evaluation-server-shapes]

## Conditions

- **Server-only.** Draft and Qwen3-14B-FP8 on one NVIDIA DGX Spark (GB10), one process, no network, batch size 1, cold prefill.[^drafter-evaluation-server-shapes][^drafter-evaluation-server-only-chain]
  - 10-16 runs: Qwen3-0.6B only, fp16, specedge's `server_only.py`, chain7 and tree16, 2 repeats each.[^drafter-evaluation-server-shapes]
  - 10-19 runs: all six drafters, bf16, new PyTorch chain code (CUDA graphs only for the PARD block), chain7 only, 2 repeats each.[^drafter-evaluation-server-only-chain]
- **Phone.** The same checkpoints in Q4_0 on the Galaxy S25 NPU, verified on the same server type over WiFi, cached prefill.[^drafter-evaluation-server-shapes]
- 60 Spec-Bench requests, temperature 0, 64 new tokens.[^drafter-evaluation-server-shapes]
- Sources: [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md) and [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md).

## Numbers

### All six drafters, chain7 (10-19)

| Drafter | Server-only tok/s | Phone tok/s | Server / phone | Server draft ms | Phone draft ms | Server round ms | Phone round ms |
|---|---|---|---|---|---|---|---|
| PARD-2 | 34.0 | 24.9 | 1.36× | 15.6 | 27.8 | 114.1 | 148.8 |
| DSpark | 33.9 | 26.5 | 1.28× | 27.2 | 38.8 | 127.4 | 160.3 |
| DFlash | 31.0 | 25.5 | 1.22× | 24.2 | 30.4 | 124.1 | 152.3 |
| PARD-1 | 28.0 | 22.1 | 1.27× | 13.0 | 21.9 | 111.3 | 137.0 |
| Qwen3-0.6B | 20.4 | 15.6 | 1.31× | 86.4 | 84.9 | 185.2 | 227.0 |
| EAGLE-3 | 17.2 | 13.0 | 1.32× | 88.8 | 114.5 | 188.0 | 239.4 |

All rows: [^drafter-evaluation-server-only-chain]

- Every server-only round is 25.7–51.4 ms shorter. Verify is 98.2–100.2 ms server-only against the phone's client wait of 114.8–129.2 ms.[^drafter-evaluation-server-only-chain]
- Acceptance is within −0.02 to +0.16 tok/round of the phone's, except Qwen3-0.6B at +0.31. The server drafts are bf16 and the phone drafts Q4_0.[^drafter-evaluation-server-only-chain]

### Qwen3-0.6B at the phone AR shapes (10-16)

| Shape | Run | tok/s | tau | draft ms | verify ms | network ms (mean) | pre/post ms | round ms |
|---|---|---|---|---|---|---|---|---|
| chain7 | server-only, GPU fp16 | 17.0 | 3.37 | 111.6 | 101.3 | 0 | 0.0 | 212.8 |
| chain7 | phone, NPU Q4_0 | 15.6 | 3.11 | 84.9 | 101.5 | 27.7 | 12.9 | 227.0 |
| chain7 | server-only / phone | ×1.09 | ×1.083 | ×1.31 | ×1.00 | | | ×0.94 |
| tree16 | server-only, GPU fp16 | 21.6 | 4.14 | 93.5 | 105.3 | 0 | 0.0 | 198.8 |
| tree16 | phone, NPU Q4_0 | 16.6 | 4.06 | 116.4 | 104.7 | 31.1 | 15.2 | 267.4 |
| tree16 | server-only / phone | ×1.30 | ×1.019 | ×0.80 | ×1.01 | | | ×0.74 |

All rows: [^drafter-evaluation-server-shapes]

- With `server_only.py` the GPU costs about 15.6–15.9 ms per draft level with 1 row or 8. The NPU costs about 12.1 ms per level as a chain and 19.4 ms with 8 beams × width 4.[^drafter-evaluation-server-shapes]
- In chain7 the outputs are identical on all 60 requests, so the higher acceptance of the fp16 draft (3.37 against 3.11) comes from the draft alone.[^drafter-evaluation-server-shapes]

## Comparisons

- **Against the phone's best arm.** Three server-only chains (PARD-2 34.0, DSpark 33.9, DFlash 31.0) beat the best phone arm, PARD-2 with its own-best tree at 30.0 tok/s.[^drafter-evaluation-server-only-chain] The best Qwen3-0.6B server-only run (tree16, 21.6 tok/s) is below all 12 phone block-drafter arms (22.1–30.0).[^drafter-evaluation-server-shapes]
- **SpecEdge shape.** The Qwen3-0.6B server-only run at the SpecEdge shape (32 beams × depth 4 × width 16, budget 32, one run) gives 21.3 tok/s, on par with tree16.[^drafter-evaluation-server-shapes]
- Both comparisons mix the drafter's location with its precision (fp16 or bf16 against Q4_0).[^drafter-evaluation-server-shapes][^drafter-evaluation-server-only-chain]

# Contradictions

**How much the server gains with the same Qwen3-0.6B chain.** With specedge's `server_only.py` (fp16), Qwen3-0.6B chain7 runs at 17.0 tok/s, ×1.09 over the phone, and drafts in 111.6 ms, slower than the NPU's 84.9 ms.[^drafter-evaluation-server-shapes] With the 10-19 PyTorch chain code (bf16, eager), the same model and shape run at 20.4 tok/s, ×1.31 over the phone, and draft in 86.4 ms, about as fast as the NPU.[^drafter-evaluation-server-only-chain] The 10-19 report lists both rows in one table and attributes the earlier `server_only.py` per-level cost to overhead ("Python tree code, non-graph forward" in the 10-16 report).[^drafter-evaluation-server-shapes] **Inference.** The server-only gain depends on how well the server draft path is implemented, so the ×1.09 figure is a lower bound for this pair. See [How fast can the server-only baseline go?](../questions/server-only-baseline-implementation.md)

## Related

- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md)
- [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md)
- [How fast can the server-only baseline go?](../questions/server-only-baseline-implementation.md)
- [Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU](block-drafters-vs-ar-drafters-on-phone-npu.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)
- [Why do tree-verified outputs diverge from chain outputs at temperature 0?](../questions/fp8-verifier-tree-output-divergence.md)
- [SpecEdge paper](../papers/parkSpecEdgeScalableEdgeAssisted2025.md)

[^drafter-evaluation-server-shapes]: My drafter evaluation report with the server-only baselines, runs of 2026-10-16
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
