---
type: Analysis
title: Applying the speculative drafter papers to a mobile phone NPU
description: How the thirteen papers in the speculative drafter collection could apply to speculative decoding on a phone NPU, for an on-device target and for a phone drafter with a server verifier, read against the mobile NPU study and the on-phone measurements of Lever.
tags: [speculative-decoding, mobile-npu, on-device-inference, draft-model, speculative-drafter, mobile-specedge, parallel-drafting, device-cloud-collaborative-inference]
question: For all the papers in the group speculative drafter, how might they be applied to a mobile phone NPU?
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
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: wangLeverSpeculativeLLM2026a
    resource: zotero://select/items/@wangLeverSpeculativeLLM2026a
    title: "Lever: Speculative LLM Inference on Smartphones"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: "A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models"
---

# Applying the speculative drafter papers to a mobile phone NPU

## Question

For all the papers in the `speculative drafter` collection, how might they be applied to a mobile phone NPU, considering the paper [Is Your NPU Ready for LLMs?](../papers/caiYourNPUReady2026.md)

## Answer

Of the thirteen papers, only [Lever](../papers/wangLeverSpeculativeLLM2026a.md) measures speculative decoding on a phone. It runs on three Snapdragon phones, with the target model streamed from flash and the draft model resident in DRAM.[^wangLeverSpeculativeLLM2026a] [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md) drafts on the device and verifies in the cloud, but its devices are NVIDIA Jetson boards on WiFi, not phones.[^xieNovelHatShapedDeviceCloud2025] The other eleven papers measure on server GPUs. Every statement marked **Inference** below is reasoning that combines sourced facts. It is not a result from any paper. The remaining gap (energy, a DRAM-resident target, and a phone drafter with a server verifier) is tracked in [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)

There are two deployment settings, and the papers apply to them differently:

- **On-device target.** The phone runs both draft and target. The NPU study and Lever speak to this setting.
- **Phone drafter, server verifier.** The phone runs only the draft and a server runs the target. This is the mobile SpecEdge setting (a Galaxy S25 Hexagon NPU drafts and a server verifies Qwen3-14B; see [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md)). HAT is the closest paper to it.

### What the NPU study establishes

| Fact | Numbers |
|---|---|
| The NPU is best for prefill, and the CPU is usually best for decode (a "phase split") | OnePlus 15, Qwen2.5-1.5B: prefill 1463.7 tokens/s on the NPU with GENIE against 299.9 tokens/s on the CPU with llama.cpp; decode 23.0 tokens/s on the NPU with GENIE against 55.7 tokens/s on the CPU with llama.cpp[^caiYourNPUReady2026] |
| NPU decode is expensive in energy | GENIE's NPU decode energy can be roughly 2–4× higher than CPU/GPU alternatives[^caiYourNPUReady2026] |
| The NPU runs shape-specialized static graphs | NPU decode throughput depends on context size, not on the number of generated tokens; from 16 to 4096 context tokens it drops from 43.9 to 35.1 tokens/s for Qwen2.5-1.5B[^caiYourNPUReady2026] |
| Activation quantization is a large lever with a quality cost | W4A16 improves decode throughput by $2.63\times$ and $2.34\times$ on Llama-3.2-1B and Llama-3.2-3B; WikiText-2 perplexity rises by +30.36% on Llama-3.2-1B and +1.04% on Llama-3.2-3B[^caiYourNPUReady2026] |
| Default scheduling wastes energy | NPU sleep latency defaults to 40 µs, while energy-optimal points are between 1280 and 65535 µs; the tuned configuration cuts decode energy by 54.8% with a 13.4% throughput loss[^caiYourNPUReady2026] |
| Phase-aware pipelines are proposed, not built | Prefill on NPU with decode on CPU, and multi-graph switching on NPU, are future directions[^caiYourNPUReady2026] |

A second paper in the wiki supports the same picture from the other side. [llada.cpp](../papers/wangEfficientOnDeviceDiffusion2026.md) observes that autoregressive decoding advances one token per step and leaves the NPU underutilized, while a block of tokens maps to dense matrix workloads that fit the NPU. One LLaDA-8B denoising pass over 32 tokens takes 478.1 ms on the NPU against 4239.6 ms on the CPU, an 8.87× speedup.[^wangEfficientOnDeviceDiffusion2026]

### What the phone and edge papers add

Lever, measured on a OnePlus 12 (Snapdragon 8 Gen 3) unless noted:

| Fact | Numbers |
|---|---|
| Verification of a flash-resident target is I/O bound | Per-token verification takes 1050.0 ms for Qwen3-8B, of which 953.4 ms (90.8%) is I/O, and 2108.3 ms for Qwen3-14B (93.3% I/O)[^wangLeverSpeculativeLLM2026a] |
| Verification parallelism on the phone NPU is limited | At 64 verified tokens, the Snapdragon 8 Gen 3 NPU reaches 8.0x over single-token generation, against 20.6x on an RTX 3090 GPU (Figure 4)[^wangLeverSpeculativeLLM2026a] |
| One-node-at-a-time drafting on the NPU is the slowest schedule | Single-node NPU drafting has the highest draft-stage latency in every configuration, because of launch and synchronization overhead. Serial CPU expansion early in tree construction, then batched NPU expansion, has the lowest[^wangLeverSpeculativeLLM2026a] |
| A fixed-shape NPU graph wastes work on the output projection | On-demand output projection on the CPU, only along the accepted path, is faster than eager or on-demand projection on the NPU[^wangLeverSpeculativeLLM2026a] |
| End-to-end gain | Geometric-mean decode speedup over 48 configurations of 2.93× over flash-backed autoregressive decoding, 1.50× over chain speculative decoding, and 1.27× over EdgeLLM, with EAGLE-3-trained drafts and Q4\_0 weights[^wangLeverSpeculativeLLM2026a] |

HAT, on Jetson AGX devices over WiFi with an 8-GPU A6000 server:

| Fact | Numbers |
|---|---|
| Hidden states are expensive to send | In U-shaped inference, communication is more than 80% of TTFT with a 128-token prompt; with a 2k-token prompt, TTFT is 3.57s, of which communication is 3.20s (89.6%)[^xieNovelHatShapedDeviceCloud2025] |
| Link bandwidth | Uplink 5MB/s to 10MB/s and downlink 10MB/s to 15MB/s, measured with iperf3[^xieNovelHatShapedDeviceCloud2025] |
| A small on-device draft from the target's own layers works | The draft is the target's first $m$ decoder layers ($m$ less than 10% of $n$), its output head, and a distilled self-attention adapter. On SpecBench with Vicuna-7B it trains 67M parameters and reaches accept length 2.06 and a 1.65$\times$ decode speedup over plain U-shaped inference[^xieNovelHatShapedDeviceCloud2025] |
| Overlapping hides the link | Prompt chunking pipelines prompt upload with cloud computation, and parallel drafting drafts the next round while the cloud verifies; TTFT falls by 41% to 54% and TBT by 41% to 77% against U-shaped baselines[^xieNovelHatShapedDeviceCloud2025] |

### The mapping

**On-device target.** **Inference.** Speculative decoding splits generation into two workloads that match the phase split. Verification is one target-model pass over several draft tokens, which is a prefill-shaped workload, the kind the NPU is good at. Drafting is a run of sequential single-token steps, which is a decode-shaped workload, the kind the CPU is good at. The natural design is draft on the CPU and verify on the NPU. This is a concrete form of the phase-aware pipeline the NPU study proposes but does not build.[^caiYourNPUReady2026] Lever builds a version of it: all target transformer layers run batched on the NPU, small draft expansions run on the CPU, and draft expansions move to the NPU only once they can be batched.[^wangLeverSpeculativeLLM2026a]

**Parallel drafters change the drafting side.** [PARD](../papers/anPARDAcceleratingLLM2025.md) predicts $K$ tokens in one draft forward pass, so one iteration costs $T_{D}+T_{T}$ instead of $K*T_{D}+T_{T}$ for an autoregressive draft.[^anPARDAcceleratingLLM2025] **Inference.** This makes drafting a block-shaped workload as well, the shape that llada.cpp finds NPU-friendly[^wangEfficientOnDeviceDiffusion2026] and the opposite of the single-node drafting that Lever finds slowest on the NPU.[^wangLeverSpeculativeLLM2026a] With a parallel drafter, both draft and verify could run on the NPU.

**Phone drafter, server verifier.** **Inference.** When the server verifies, the phone runs only the draft, and the per-round cost is draft time plus the network round trip plus server time. Two questions decide the drafter choice. First, is the draft decode-shaped (autoregressive, CPU-favored) or block-shaped (parallel, NPU-favored)? Second, what has to cross the link each round? Feature-free drafters such as PARD need only tokens.[^anPARDAcceleratingLLM2025] EAGLE-3-style drafters, including [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) and the target-dependent mode of [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md), consume hidden states from several target layers,[^bieOspreyTargetagnosticPretraining2026][^anPARD2TargetAlignedParallel2026] which would have to be sent down from the server every round. HAT's measurements show that hidden-state transfer can dominate delay on a WiFi link.[^xieNovelHatShapedDeviceCloud2025]

### Paper by paper

The first two rows are the system papers that run drafting on a device. The rest are drafter designs and training methods measured on server GPUs.

| Paper | What it contributes | How it could apply on a phone NPU (inference) |
|---|---|---|
| [Lever](../papers/wangLeverSpeculativeLLM2026a.md) | Speculative decoding on Snapdragon phones with the target streamed from flash. It builds the token tree that maximizes expected tokens per unit of cycle latency, prunes the verification tree with an early-exit predictor, and splits work between the CPU and the NPU. 2.93× over flash-backed autoregressive decoding, 1.50× over chain speculative decoding, 1.27× over EdgeLLM.[^wangLeverSpeculativeLLM2026a] | The only measured evidence in the collection. Its draft-stage finding, that single-node NPU drafting is the slowest schedule because of launch and synchronization overhead,[^wangLeverSpeculativeLLM2026a] argues against running a one-token-per-step draft on the NPU. Its target sits on the phone, so its verification costs do not carry over to a server verifier. Its gain-per-latency tree objective does carry over, with the cost term measured as network round trip plus server time instead of flash I/O. |
| [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md) | A device-cloud split. The device holds the target's first layers, its output head, and a distilled adapter as the draft model; the cloud runs the middle layers; verification exchanges hidden states, not tokens. Prompt chunking and parallel drafting hide the link. TTFT falls by 41% to 54% and TBT by 41% to 77% against U-shaped baselines.[^xieNovelHatShapedDeviceCloud2025] | Closest in structure to a phone-drafts, server-verifies design. Its numbers are a warning about link payload: with a 2k-token prompt, communication is 3.20s of a 3.57s TTFT.[^xieNovelHatShapedDeviceCloud2025] A drafter that needs only tokens avoids that cost. Its parallel drafting, which drafts from the top-k candidates of the last draft token while the cloud verifies,[^xieNovelHatShapedDeviceCloud2025] is a way to hide the round trip. Building the draft from the target's own shallow layers keeps raw tokens on the device, which is its privacy argument, but it ties the draft to one target. |
| [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md) | Speculative decoding performance depends heavily on draft latency, and draft latency is bottlenecked by model depth. A wide draft reduces draft latency by $49\%$ and improves throughput by $41\%$ against a deep one with $3\%$ higher TAR. The design also gives a $37\%$ reduction in KV-Caches.[^yanDecodingSpeculativeDecoding2025] | The most directly relevant drafter-design paper. A phone draft should be shallow and wide, because each draft layer is one more sequential step on the CPU. The smaller KV cache matters on a device where two models share DRAM. |
| [PARD](../papers/anPARDAcceleratingLLM2025.md) | Fine-tunes the smallest model of the target's series (LLaMA3.2-1B, Qwen2.5-0.5B) with mask tokens to predict $K$ tokens in one forward pass, with no target features. One drafter serves a whole target family. On vLLM on an A100, average speedups range from 2.65$\times$ to 3.71$\times$, and draft-phase bandwidth stays at 2.48 GB for $k$ = 4, 6, and 8, against 5.94 GB to 11.88 GB for EAGLE and EAGLE-3.[^anPARDAcceleratingLLM2025] | Two properties fit a phone drafter for a server target. It needs no target hidden states, so only tokens cross the link. It also turns drafting into one block-shaped pass, which suits the NPU. Because draft bandwidth stays constant as $k$ grows, longer blocks do not add draft memory traffic. Its cost is size: the drafter is a complete small LM, not a one- or two-layer head. Target-independence holds within one model series,[^anPARDAcceleratingLLM2025] so a Qwen3 server target needs a Qwen3-series drafter. |
| [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md) | Adds Confidence-Adaptive Token loss weighting from the target's cumulative prefix confidence, target hidden features from 4 target layers, and knowledge distillation. A stochastic gate in training lets one drafter run with target features (target-dependent mode) or without them (target-independent mode). On Qwen3-14B at temperature 0 on vLLM, the average speedup is 5.81$\times$ ($\tau$ 6.91) target-dependent and 4.79$\times$ ($\tau$ 6.03) target-independent, against 4.51$\times$ for PARD.[^anPARD2TargetAlignedParallel2026] | For a server Qwen3-14B target, the two modes become a link choice. Target-independent mode needs nothing sent down from the server. Target-dependent mode needs multi-layer target features every round, and on a GPU it is worth 5.81$\times$ against 4.79$\times$. Two cautions for Qwen3-14B. Table 2 says only that all target-independent runs use "the same draft model". Table 6 lists $\rho=0.0$ for the Qwen3-14B drafter, while the implementation details state $\rho=0.1$.[^anPARD2TargetAlignedParallel2026] With $\rho=0.0$ the gate never drops the features, so that drafter would never see the feature-free case in training. Its target-independent quality should be measured before relying on it. The paper also does not give the drafter's size, and reports greedy decoding only.[^anPARD2TargetAlignedParallel2026] |
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | Prunes Qwen3-4B to its first two blocks, pretrains it once on FineWeb with no target, then adapts it to each target with EAGLE-3's training-time test. On Qwen3-8B the body has 265 M parameters at width 2560 (one-layer EAGLE-3: 269 M at width 4096), and mean acceptance length over a 5×5 cross-domain grid rises from 3.176 to 3.686. Pretraining costs 3,040 H100-hours once; per-target adaptation costs 48 H100-hours, the same as EAGLE-3.[^bieOspreyTargetagnosticPretraining2026] | A narrow, shallow drafter is the shape a phone wants, and the paper keeps the depth small because drafter latency directly affects speedup.[^bieOspreyTargetagnosticPretraining2026] The paper reports its largest gains on out-of-domain and multilingual data,[^bieOspreyTargetagnosticPretraining2026] which suits one user's mixed traffic. Its accepted-length gain over EAGLE-3 widens from 7% to 53% as the chain grows from 2 to 8 draft tokens,[^bieOspreyTargetagnosticPretraining2026] which matters when every round pays a network round trip. But it consumes fused hidden states from three target layers,[^bieOspreyTargetagnosticPretraining2026] so in a server split those states must reach the phone each round. Running the fusion projection on the server would send one drafter-width vector per token instead of three target-width states. The pruned backbone is about 591M parameters including the embedding and LM head,[^bieOspreyTargetagnosticPretraining2026] so the vocabulary layers are a large part of its memory on the phone. |
| [Sheared LLaMA](../papers/xiaShearedLLaMAAccelerating2024.md) | Prunes LLaMA2-7B down to 1.3B and 2.7B parameters with $3\%$ of the compute of training such models from scratch.[^xiaShearedLLaMAAccelerating2024] | A recipe for building the draft from the target. The phones in the NPU study run targets of 1B to 7B,[^caiYourNPUReady2026] so a 1.3B draft is too large for most of them. The method would need a much smaller target shape. For a server target it is closer to useful, since the draft then only has to fit the phone. |
| [Minitron](../papers/muralidharanCompactLanguageModels2024.md) | Best practices for structured pruning plus distillation-based retraining; produces 8B and 4B models from Nemotron-4 15B with up to 40$\times$ fewer training tokens.[^muralidharanCompactLanguageModels2024] | Same role as Sheared LLaMA: a way to derive a phone-sized target and its draft from one large model. Its pruning-axis findings would guide which axis to cut for a shallow draft. |
| [SDFP](../papers/weiSDFPSpeculativeDecoding2026.md) | Builds the draft by removing the target's least sensitive layers, with no training. Overall speedups of $1.31\times$ to $1.46\times$ on LLaMA-2 models.[^weiSDFPSpeculativeDecoding2026] | Attractive on a phone because no second model has to be trained or shipped. The cost is a second static graph for the pruned model, which depends on the multi-graph switching that the NPU study lists as future work.[^caiYourNPUReady2026] The reported gain is small, so NPU wake and switch overhead could remove it. With a server target the draft is the target minus some layers (for LLaMA-2-13B, 50% of attention layers and 35% of FFN layers are pruned),[^weiSDFPSpeculativeDecoding2026] which is far too large to run on a phone, so it does not fit the phone-drafter setting. |
| [DistillSpec](../papers/zhouDistillSpecImprovingSpeculative2024.md) | Distills the draft to align with the target, for a higher acceptance rate; $10-45\%$ speedups over standard speculative decoding.[^zhouDistillSpecImprovingSpeculative2024] | The target on an NPU is quantized, and W4A16 changes its output distribution.[^caiYourNPUReady2026] The draft should be distilled against the quantized target as deployed, not the full-precision one. The same applies in reverse when the draft is quantized for the phone and the target stays on the server. |
| [LK losses](../papers/samarinLKLossesDirect2026.md) | Trains the draft for acceptance rate directly. Low-capacity drafts gain most: MEDUSA and MLP speculators improve by 7.8% and 8.3%, EAGLE-3 by 3.8%.[^samarinLKLossesDirect2026] | Phone drafts are low-capacity by necessity, which is the case where this loss helps most. It adds no inference cost, so it is free on device. |
| [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md) | Two RL policies choose draft depth and verification size, rewarded by the throughput of each draft-and-verify cycle; up to 36.4% over Eagle3.[^zhangLearningDraftAdaptive2026] | The policy would have to be trained on phone timing, where verification cost moves in steps with fixed graph shapes instead of smoothly. The reward could be energy per token instead of throughput, since PowerBench measures µJ/token per compute unit.[^caiYourNPUReady2026] Lever's tree builder already optimizes tokens per unit of cycle latency from an online latency profile,[^wangLeverSpeculativeLLM2026a] which is a non-learned version of the same goal. |
| [Aurora](../papers/wangWhenRLMeets2026.md) | Trains the speculator online from live serving traces and hot-swaps updates; argues that end-to-end speedup cannot be inferred reliably from acceptance rate alone.[^wangWhenRLMeets2026] | A phone cannot run the training server. The transferable parts are the warning that acceptance rate does not predict speedup, which is stronger on a phone where NPU and CPU costs differ, and the idea of adapting the draft to one user's traffic off-device. In a server-verifier setting the server already sees the traffic, so it could train the update and push it to the phone. |

### Risks specific to the NPU

- **Inference.** Draft-then-verify makes the NPU alternate between work and idle. The NPU study shows that short RPC polling intervals reduce total energy per token by $30.9\%$–$37.8\%$ and energy-optimal NPU sleep latency settings reduce it by $44.6\%$–$50.9\%$,[^caiYourNPUReady2026] so these settings would decide whether speculative decoding saves or costs energy. Lever reports decode throughput only, with no energy numbers,[^wangLeverSpeculativeLLM2026a] so this is still unmeasured.
- **Inference.** The verification length must fit a fixed graph shape. [llada.cpp](../papers/wangEfficientOnDeviceDiffusion2026.md) reports stage-like NPU latency caused by fixed-size tiles,[^wangEfficientOnDeviceDiffusion2026] so the verify length should be chosen to fill a tile. The same holds for the block size of a parallel drafter such as PARD or PARD-2 when it runs on the NPU.
- **Inference.** A one-token-per-step draft is a poor fit for the NPU. Lever finds single-node NPU drafting slowest because of launch and synchronization overhead.[^wangLeverSpeculativeLLM2026a] An autoregressive draft should run on the CPU or be batched across tree nodes, and a parallel draft should fill a block.
- **Inference.** For an on-device target, the baseline to beat is CPU decode, not NPU decode. At 55.7 tokens/s on the CPU for Qwen2.5-1.5B,[^caiYourNPUReady2026] the draft model must be far faster than the target on the same CPU for the scheme to win.
- **Inference.** For a server target, the link is part of every round. HAT measures uplinks of 5MB/s to 10MB/s on WiFi and finds communication can be most of the delay when hidden states are sent.[^xieNovelHatShapedDeviceCloud2025] A drafter that needs target features from the server adds a downlink payload every round; a feature-free drafter does not.

## Evidence

All numbers above are copied from the Paper pages of the fifteen cited papers. The NPU study measures only Qualcomm Snapdragon devices.[^caiYourNPUReady2026] Lever's three phones also use Snapdragon SoCs (8 Gen 3 and 8 Elite).[^wangLeverSpeculativeLLM2026a]

## Caveats

- Lever is the only paper in the wiki that runs speculative decoding with an autoregressive target on a phone NPU. Its target streams from flash, it reports no energy, and its baselines share the same flash streaming,[^wangLeverSpeculativeLLM2026a] so its speedups say little about a DRAM-resident target or a server target. The mapping and every other "how it could apply" cell are inferences.
- No paper in the wiki measures a phone drafter with a server verifier. HAT's devices are Jetson AGX boards with GPUs, connected over WiFi, running Vicuna-7B and Vicuna-13B, with no energy measurement; its baselines are all U-shaped variants.[^xieNovelHatShapedDeviceCloud2025]
- The other eleven drafter papers use server GPUs and targets from LLaMA-2 7B up to models of hundreds of billions of parameters. Their speedups do not transfer to 1B to 7B phone targets.
- PARD does not state its sampling temperature, and PARD-2 reports greedy decoding only.[^anPARDAcceleratingLLM2025][^anPARD2TargetAlignedParallel2026] PARD-2's hyperparameter table and implementation details disagree on $\rho$ for Qwen3-14B.[^anPARD2TargetAlignedParallel2026]
- Osprey's pretraining is a one-time cost of 3,040 H100-hours that the authors say pays back only under high-volume serving or reuse across targets.[^bieOspreyTargetagnosticPretraining2026] Most of its results come from single runs.[^bieOspreyTargetagnosticPretraining2026]
- llada.cpp uses its own speculative scheme for diffusion LLMs, where future-block tokens are marked as draft.[^wangEfficientOnDeviceDiffusion2026] It is evidence about NPU behavior with token blocks, not about draft-and-verify with two models.

## Related

- [Speculative decoding](../methods/speculative-decoding.md), [Sheared-LLaMA](../methods/sheared-llama.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md), [DistillSpec](../methods/distillspec.md), [EAGLE-3](../methods/eagle-3.md), [Training-time test](../methods/training-time-test.md)
- Parallel and pretrained drafters: [PARD](../methods/pard.md) (also PARD-2), [Osprey](../methods/osprey.md), [DFlash](../methods/dflash.md)
- On-device and edge systems: [Lever](../methods/lever.md), [HAT](../methods/hat.md), [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md), [Tree-based speculation](../methods/tree-based-speculation.md), [Chunked prefill](../methods/chunked-prefill.md)
- [llama.cpp](../methods/llama-cpp.md), [DVFS](../methods/dvfs.md), [KV cache](../methods/kv-cache.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md), [Can a block drafter pre-draft with stale target features?](../questions/pre-drafting-with-stale-target-features.md), [Can a block drafter be narrower than its target?](../questions/narrow-block-drafter.md)
- [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](../questions/cost-efficient-drafter-construction.md)
- [Was PARD-2's Qwen3-14B drafter trained to run without target features?](../questions/pard-2-qwen3-14b-feature-gating.md)
- [Quantization of the target and the draft in speculative decoding](quantization-in-speculative-decoding.md)

[^caiYourNPUReady2026]: Cai et al. 2026
[^wangEfficientOnDeviceDiffusion2026]: Wang et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^wangWhenRLMeets2026]: Wang et al. 2026
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^wangLeverSpeculativeLLM2026a]: Wang et al. 2026
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
