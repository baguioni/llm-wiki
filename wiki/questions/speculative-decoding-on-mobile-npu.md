---
type: Open Question
title: Does speculative decoding help on a mobile NPU?
description: Lever measures speculative decoding with NPU verification on Snapdragon phones, but only for a target streamed from flash and with no energy numbers, so the case of a DRAM-resident target and its energy cost stays open.
tags: [speculative-decoding, mobile-npu, on-device-inference, energy-efficiency]
sources:
  - id: caiYourNPUReady2026
    resource: zotero://select/items/@caiYourNPUReady2026
    title: "Is Your NPU Ready for LLMs? Dissecting the Hidden Efficiency Bottlenecks in Mobile LLM Inference"
  - id: wangEfficientOnDeviceDiffusion2026
    resource: zotero://select/items/@wangEfficientOnDeviceDiffusion2026
    title: Efficient On-Device Diffusion LLM Inference with Mobile NPU
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: wangLeverSpeculativeLLM2026a
    resource: zotero://select/items/@wangLeverSpeculativeLLM2026a
    title: "Lever: Speculative LLM Inference on Smartphones"
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

# Does speculative decoding help on a mobile NPU?

## Question

Does speculative decoding with a small draft model give a speedup or an energy saving on a phone, when the target model runs on the NPU?

## Why it matters

The `speculative drafter` and `mobile-specedge` collections meet at this point. Until Lever, the drafter papers in the wiki were all measured on server GPUs, and the mobile NPU study measures plain autoregressive inference only.

## Evidence so far

- On phones the NPU is best for prefill and the CPU is usually best for decode. OnePlus 15, Qwen2.5-1.5B: NPU prefill 1463.7 tokens/s with GENIE; CPU decode 55.7 tokens/s with llama.cpp; NPU decode 23.0 tokens/s with GENIE.[^caiYourNPUReady2026]
- The NPU study proposes phase-aware pipelines (prefill on NPU, decode on CPU) and multi-graph switching as future directions and does not build them.[^caiYourNPUReady2026]
- An NPU pass over a block of tokens is well amortized: one LLaDA-8B denoising pass over 32 tokens takes 478.1 ms on the NPU against 4239.6 ms on the CPU.[^wangEfficientOnDeviceDiffusion2026]
- On servers, draft latency is the bottleneck of speculative decoding and is set by draft depth.[^yanDecodingSpeculativeDecoding2025]

### Lever: speculative decoding with NPU verification on phones

[Lever](../papers/wangLeverSpeculativeLLM2026a.md) is the first paper in the wiki that runs draft-and-verify on a phone NPU.

- **Setup.** OnePlus 12, Honor 500 Pro, and Honor Magic V5 (Snapdragon 8 Gen 3 and 8 Elite). Targets are Llama-3.1-8B, Qwen3-4B, Qwen3-8B, and Qwen3-14B, with EAGLE-3-trained drafts. All weights are Q4\_0. The target's weights stay in flash and are streamed layer by layer at each verification.[^wangLeverSpeculativeLLM2026a]
- **Placement.** All target transformer layers run batched on the NPU. Small draft expansions run on the CPU, and batches of draft nodes move to the NPU once the tree is large. The output projection runs on the CPU, only along the accepted path.[^wangLeverSpeculativeLLM2026a]
- **Speedup.** Geometric mean over 48 configurations: 2.93$\times$ over flash-backed autoregressive decoding, 1.50$\times$ over chain speculative decoding, 1.27$\times$ over EdgeLLM. In the figure, chain speculative decoding is above flash-backed autoregressive decoding in every configuration.[^wangLeverSpeculativeLLM2026a]
- **Where the time goes.** Per-token verification of a flash-resident Qwen3-8B takes 1050.0 ms, of which 953.4 ms (90.8%) is I/O. The paper attributes the speedup over autoregressive decoding to amortizing flash-backed target invocations.[^wangLeverSpeculativeLLM2026a]
- **NPU parallelism.** At 64 verified tokens the Snapdragon 8 Gen 3 NPU reaches 8.0x over single-token generation, against 20.6x for an RTX 3090.[^wangLeverSpeculativeLLM2026a] Decode speed peaks at a tree budget of 16 and falls at 32 and 64, while accepted length keeps rising.[^wangLeverSpeculativeLLM2026a]
- **Drafting on the NPU.** Running draft nodes one at a time on the NPU is the slowest draft schedule, because of launch and synchronization overhead. Batch-aware CPU-then-NPU scheduling is the fastest.[^wangLeverSpeculativeLLM2026a]
- **DRAM residency.** With 100% of Qwen3-8B's layers in DRAM, Lever reaches 3.401 tokens/s on MBPP, against 1.753 tokens/s with all layers in flash.[^wangLeverSpeculativeLLM2026a] No baseline is reported at 100% residency.

**Inference.** Lever shows that NPU verification gives a speedup when the target is bound by flash I/O. It does not show the same for a target that fits in DRAM. That setting is the one my experiment and the CPU-vs-NPU decode numbers above refer to.

### My drafter evaluation: phone drafts, server verifies

[My drafter evaluation](../experiments/drafter-evaluation-qwen3-14b.md) covers the split setting, not an on-device target. With a Galaxy S25 NPU drafting at Q4_0 and a DGX Spark verifying Qwen3-14B-FP8, the block drafters reach 26.7–30.0 tok/s with their best trees and the autoregressive drafters 17.6–18.5.[^drafter-evaluation] Running one NPU decode per tree level costs the autoregressive drafters 85–116 ms per round, against 22–54 ms for a block drafter's single decode.[^drafter-evaluation] No energy was measured and no non-speculative baseline was run.[^drafter-evaluation] Server-only speculative decoding, with Qwen3-0.6B drafting in fp16 on the same GPU type and no phone, reaches 17.0 tok/s as a chain and 21.6 in tree16. Against the phone Qwen3-0.6B at the same shapes, that is ×1.09 and ×1.30. All 12 phone block-drafter arms are still faster (22.1–30.0 tok/s).[^drafter-evaluation-server-shapes]

The block drafters themselves, however, are faster on the server GPU. Re-implemented in PyTorch bf16 and run as chain7 beside the target, all six drafters gain ×1.22 to ×1.36 over their phone chain7 arms, and PARD-2 (34.0 tok/s), DSpark (33.9), and DFlash (31.0) beat the best phone arm of any shape (30.0).[^drafter-evaluation-server-only-chain] Every server-only round is 25.7–51.4 ms shorter, because the verify wait drops from the phone's client wait to the bare target forward and five of the six drafters also draft faster on the GPU.[^drafter-evaluation-server-only-chain] See [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md).

**Inference.** For a single request on an idle server, drafting on the phone does not beat drafting on the server, for any of these drafters. What the phone can still save is server GPU time per token, the quantity HyCo measures (below), and that matters only with several clients, which none of my runs measures.

### HyCo: phone NPU drafts, server verifies

[HyCo](../papers/baeHyCoHybridDrafting2026.md) is the first paper in the wiki that drafts on a phone NPU for a server verifier. A Galaxy S26 Ultra (Hexagon Tensor Processor v81) drafts for Gemma 4 26B-A4B on one RTX PRO 6000 over LTE/5G.[^baeHyCoHybridDrafting2026]

- **Per-level SLM passes are too slow on the phone.** A SpecEdge-style tree of four Gemma 4 E2B passes delivers 16.1 tokens/s on Spec-Bench, below the 26.4 tokens/s of the SLM generating alone on the phone. HyCo, with one SLM pass plus the verifier's MTP head on the phone, delivers 35.0 tokens/s.[^baeHyCoHybridDrafting2026]
- **Integer graphs matter.** 16-bit floating-point activations lengthened the SLM's 32-row pass from 15.7 to 38–41 ms at unchanged acceptance; both drafters use 16-bit fixed-point activations and static QAIRT graphs.[^baeHyCoHybridDrafting2026]
- **The output layer is a large share of a round.** The full 262,144-token vocabulary lengthens the phone's time per round from 52.9 to 77.9 ms against an 86K keep set.[^baeHyCoHybridDrafting2026]
- **Server cost.** HyCo reduces server GPU time per output token against server-side MTP self-speculation by 38.6% on Spec-Bench (27.7% with exact verification).[^baeHyCoHybridDrafting2026]
- HyCo measures no device or radio energy.[^baeHyCoHybridDrafting2026]

**Inference.** HyCo agrees with my evaluation that one NPU pass per tree level is what makes autoregressive drafters slow on a phone. It also reaches the same conclusion from a different direction: it keeps an autoregressive SLM but limits it to one pass and takes depth from a head that is much cheaper per step.

## Conflicting claims

No direct conflict. Lever's NPU-parallelism finding and the llada.cpp finding compare against different references. One LLaDA-8B pass over 32 tokens is far cheaper on the NPU than on the CPU (478.1 ms against 4239.6 ms).[^wangEfficientOnDeviceDiffusion2026] Lever finds the NPU amortizes batched verification much less than a server GPU does (8.0x against 20.6x at 64 tokens).[^wangLeverSpeculativeLLM2026a] **Inference.** Together they suggest that on a phone NPU a small verify width gives more per token than a large one.

## What would resolve it

A measurement on one phone of tokens/s and µJ/token for three setups with the same DRAM-resident target model: CPU decode, NPU decode, and draft on CPU with verification on NPU. The sweep should cover draft size, verification length, and the NPU sleep latency setting. Lever covers the flash-resident case for speed only.

## Related

- [Applying the speculative drafter papers to a mobile phone NPU](../analyses/speculative-drafter-papers-on-mobile-npu.md)
- [Speculative decoding](../methods/speculative-decoding.md), [llama.cpp](../methods/llama-cpp.md), [DVFS](../methods/dvfs.md), [Lever](../methods/lever.md)
- [Does speculative decoding still help at large batch sizes?](speculative-decoding-at-large-batch.md)
- [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md) (my own measurements of draft cost on a phone NPU)
- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md), [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md), [Drafting on the server GPU instead of the phone NPU](../results/server-vs-phone-draft-location.md), [How fast can the server-only baseline go?](server-only-baseline-implementation.md), [Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU](../results/block-drafters-vs-ar-drafters-on-phone-npu.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)
- [HyCo](../methods/hyco.md), [HyCo cuts server GPU time per token by 38.6% against server-side MTP on Spec-Bench](../results/hyco-server-gpu-time-vs-cloud-mtp.md), [Does proactive drafting help when the drafter runs on a phone?](proactive-drafting-on-a-phone.md)

[^caiYourNPUReady2026]: Cai et al. 2026
[^wangEfficientOnDeviceDiffusion2026]: Wang et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^wangLeverSpeculativeLLM2026a]: Wang et al. 2026
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^drafter-evaluation-server-shapes]: My drafter evaluation report with the server-only baselines, runs of 2026-10-16
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
