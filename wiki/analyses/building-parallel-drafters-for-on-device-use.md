---
type: Analysis
title: Building a parallel drafter for on-device use without training it from scratch
description: Pruning a target gives an autoregressive model, but PARD shows that turning a small autoregressive model into a parallel drafter is a cheap fine-tune, PARD-2 shows that target features can enter through the input embedding of that narrow model, and on my phone such a 409 MB drafter matches the 1741 MB DFlash; the open step is to start from a pruned target.
tags: [speculative-decoding, parallel-drafting, draft-model, mobile-npu, mobile-specedge, structured-pruning, speculative-drafter, pard, dflash, dspark, osprey]
question: How can parallel drafters such as DFlash and DSpark be used on a device, when a parallel drafter cannot be obtained simply by pruning the target model?
sources:
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: "A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models"
  - id: wangEfficientOnDeviceDiffusion2026
    resource: zotero://select/items/@wangEfficientOnDeviceDiffusion2026
    title: Efficient On-Device Diffusion LLM Inference with Mobile NPU
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# Building a parallel drafter for on-device use without training it from scratch

## Question

How can parallel drafters such as [DFlash](../methods/dflash.md) and [DSpark](../methods/dspark.md) be used on a device? The difficulty is training: a small autoregressive drafter can be cut out of the target by [structured pruning](../methods/structured-pruning.md), but a parallel drafter cannot.

## Answer

Statements marked **Inference** are my reading of the sources and of my phone runs. No paper tests them.

### 1. The premise holds for DFlash and DSpark, but not for parallel drafting in general

Pruning yields an autoregressive model. The DFlash recipe then cannot use it, for two reasons:

- DFlash shares the target's token embedding and LM head and keeps them frozen. Only the draft layers are trained.[^chenDFlashBlockDiffusion2026] DSpark keeps the same backbone and the same frozen embedding and head.[^chengDSparkConfidenceScheduledSpeculative2026] So the draft layers run at the target's full width, and a pruned, narrower model does not fit that slot. See [Can a block drafter be narrower than its target?](../questions/narrow-block-drafter.md)
- The DFlash body reads target features as injected keys and values. A warm-started body gains little from its pretraining under that interface (section 3).

[PARD](../methods/pard.md) shows that the step from an autoregressive model to a parallel drafter is itself a cheap fine-tune:

- PARD "adapts a standard autoregressive draft model into a parallel draft model" with mask-token training.[^anPARDAcceleratingLLM2025] It builds on existing high-accuracy small language models.[^anPARDAcceleratingLLM2025]
- Its conditional drop-token (COD) cuts that adaptation cost by up to 3×.[^anPARDAcceleratingLLM2025] Its ablations train on a 93K subset of OpenR1-Math-220K for one epoch.[^anPARDAcceleratingLLM2025]
- PARD keeps the autoregressive backbone and adds masked placeholders "to better match the auto-regressive architecture of the target model", as PARD-2 describes it.[^anPARD2TargetAlignedParallel2026]

**Inference.** The construction therefore splits into two steps. First get a small autoregressive model in the target's vocabulary, by any means, pruning included. Then convert it to a parallel drafter with PARD's training. Pruning is a way to do the first step, not a replacement for the second.

### 2. Target features matter, and they need not enter through KV injection

- A 5-layer block diffusion drafter trained *without* target features reaches speedups of 2.83 to 3.73 (τ 3.38 to 4.61) on four math benchmarks at temperature 0.[^chenDFlashBlockDiffusion2026] DFlash calls this modest and attributes it to the missing target context.[^chenDFlashBlockDiffusion2026]
- PARD-2 adds target features to a PARD drafter. It fuses 4 target layers with a lightweight projection and adds the result to the draft input embeddings, with stochastic gating.[^anPARD2TargetAlignedParallel2026] On server GPUs its target-dependent mode averages 5.81× / τ 6.98 on Qwen3-8B, against 4.61 / 5.58 for DFlash.[^anPARD2TargetAlignedParallel2026]
- On my phone, `amd/PARD2-Qwen3-14B` is a 409 MB Q4_0 drafter, the size of Qwen3-0.6B. The server projects target layers 17, 25, and 33 plus the final post-norm from 20480 to 1024 wide, so the phone downloads 2 KB per committed token. DFlash and DSpark are 1741 MB each and download 10 KB.[^drafter-evaluation]
- Against DFlash on the same 60 requests, PARD-2 reaches 24.9 / 29.3 / 30.0 tok/s against 25.5 / 27.9 / 28.8 (chain7 / tree16 / own-best).[^drafter-evaluation]

**Inference.** This is the main lever for on-device use. A narrow, small-LM-shaped parallel drafter with target features added at the input already matches the full-width DFlash on this phone, at under a quarter of its weight bytes. On my S25 NPU, draft cost follows weight bytes, and the width-5120 head and overhead alone cost 8.34 ms against 1.95 ms at width 1024 (see [my S25 profiling](../experiments/npu-draft-cost-profiling-galaxy-s25.md)).

### 3. A warm-started body helps only if the interface preserves it

- [Osprey](../methods/osprey.md) prunes a pretrained small LM (Qwen3-4B to 2 layers), pretrains it on FineWeb, and adapts it to each target through zero-initialized QKV columns, so that "the attention layers therefore retain their target-agnostic pretrained behavior at initialization".[^bieOspreyTargetagnosticPretraining2026] For an autoregressive drafter on Qwen3-8B this raises mean AL from 3.176 to 3.686 at the same per-target budget.[^bieOspreyTargetagnosticPretraining2026]
- Under the original DFlash interface, warm-starting the body from a small diffusion LM gains at most 0.07 accepted tokens in any domain (math 6.03 against 5.96, OOD average 1.68 against 1.64).[^bieOspreyTargetagnosticPretraining2026] The authors' hypothesis is key/value distribution drift: the pretrained attention now receives target-derived keys and values it never saw.[^bieOspreyTargetagnosticPretraining2026]
- An EAGLE-style DFlash variant adds zero-initialized target projections to Q, K, and V, broadcasts one target feature from the anchor across the block, and uses causal intra-block attention with shift-by-one labels. It raises OOD AL to 2.00 but lowers in-domain math to 5.25.[^bieOspreyTargetagnosticPretraining2026]

**Inference.** A pruned target body is a warm start of the same kind. If it is wrapped in KV injection, most of its value will probably be lost, as with Osprey's diffusion body. A PARD-2 interface (features added to the input embedding) or Osprey's zero-initialized QKV keeps the pretrained computation intact at the start of training, and suits a pruned body better.

### 4. Pruned or target-derived drafters already work for the autoregressive case

- Minitron derives 8B and 4B models from Nemotron-4 15B with up to 40× fewer training tokens than from scratch, and recommends width pruning over depth pruning at scales ≤ 15B.[^muralidharanCompactLanguageModels2024] Sheared LLaMA needs 3% of the compute of training such models from scratch.[^xiaShearedLLaMAAccelerating2024]
- SDFP builds a draft from the target's own layers with no training, with overall speedups of 1.31× to 1.46× on LLaMA-2 models.[^weiSDFPSpeculativeDecoding2026]
- HAT keeps the LLM's first layers, a distilled adapter, and the output head on the device as its drafter. On SpecBench it trains 67M parameters and reaches an accept length of 2.06, against 591M and 1.89 for U-Medusa.[^xieNovelHatShapedDeviceCloud2025]

**Inference.** These give the first step of section 1 for a target with no small sibling. A width-pruned and distilled target keeps the target's vocabulary and tokenizer, which PARD's mask-token step and PARD-2's features then build on.

### 5. Reuse a released parallel checkpoint where one exists

- DPara turns the official DSpark checkpoint into M-DFlash for a new regime (multiple anchors, no target features) by fine-tuning only the diffusion backbone for one epoch, with no new trainable parameters.[^liuWhenParallelDrafter2026]
- A target-independent PARD drafter serves a whole target family with no per-target training.[^anPARDAcceleratingLLM2025] On my phone, PARD-1 (`amd/PARD-Qwen3-0.6B`) reaches 22.1 / 26.7 / 26.7 tok/s and needs nothing from the server, though it is weak on translation.[^drafter-evaluation]

### 6. What each route costs to train

| Route | Needs from the target during training | Training cost reported |
|---|---|---|
| PARD on a small AR model | regenerated answers only | 20.22 Pflops per 1M tokens for a LLaMA3-70B target, against 204.4 for EAGLE-3[^anPARDAcceleratingLLM2025] |
| PARD-2 | features from 4 layers, target token probabilities, a KD term | 2 epochs for Qwen3-8B and Qwen3-14B[^anPARD2TargetAlignedParallel2026] |
| DFlash / DSpark | features from 5 layers, online or cached[^chenDFlashBlockDiffusion2026]; DSpark also the target distribution[^chengDSparkConfidenceScheduledSpeculative2026] | DFlash: 6 epochs[^chenDFlashBlockDiffusion2026] |
| Osprey | target features and logits, online | 48 H100-hours per target for Qwen3-8B, after 3,040 H100-hours of one-time pretraining (576 for 10k steps)[^bieOspreyTargetagnosticPretraining2026] |

The per-signal storage arithmetic is in [What the target must supply to train a drafter](target-signals-for-drafter-training.md).

### 7. PARD-1, PARD-2, or DFlash for an arbitrary target

| | PARD-1 | PARD-2 | DFlash |
|---|---|---|---|
| What you need before training | a small AR model with the target's tokenizer[^anPARDAcceleratingLLM2025] | the same, plus the target for training[^anPARD2TargetAlignedParallel2026] | only the target: its embedding and head are reused frozen, the draft layers are trained[^chenDFlashBlockDiffusion2026] |
| Target in the training loop | no[^anPARDAcceleratingLLM2025] | yes: features, token probabilities, distillation[^anPARD2TargetAlignedParallel2026] | yes: 5 target layers, online or cached[^chenDFlashBlockDiffusion2026] |
| Drafter width | the small model's | the small model's, features projected to it | the target's |
| Qwen3-14B drafter size, Q4_0 | 409 MB[^drafter-evaluation] | 409 MB[^drafter-evaluation] | 1741 MB[^drafter-evaluation] |
| Download per committed token | about 0[^drafter-evaluation] | 2 KB[^drafter-evaluation] | 10 KB[^drafter-evaluation] |
| Phone tok/s, chain7 / tree16 / own-best | 22.1 / 26.7 / 26.7[^drafter-evaluation] | 24.9 / 29.3 / 30.0[^drafter-evaluation] | 25.5 / 27.9 / 28.8[^drafter-evaluation] |
| Server, Qwen3-8B average speedup / τ | 4.39 / 5.56 (PARD)[^anPARD2TargetAlignedParallel2026] | 5.81 / 6.98[^anPARD2TargetAlignedParallel2026] | 4.61 / 5.58[^anPARD2TargetAlignedParallel2026] |

**Inference.**
- DFlash is the only one of the three that can be built for any target with nothing but the target. Its cost on the phone, though, grows with the target's width.
- PARD-2 is the most mobile-efficient for Qwen3-14B. It runs at a quarter of DFlash's weight bytes and a fifth of its download, and its throughput is equal or slightly higher (DFlash leads only as a chain).
- PARD-1 is the cheapest to train and needs nothing from the server, but it is about 3 tok/s behind PARD-2 on the phone.
- The PARD routes need a backbone. For a target with no small sibling, that is the open part: a pruned target, or a foreign small LM moved to the target's vocabulary. Osprey does the latter for an AR drafter, from a source model that "may belong to a different model family and may use a different tokenizer".[^bieOspreyTargetagnosticPretraining2026]

### Recommendation

**Inference.** For Qwen3-14B, use the released PARD-2 checkpoint, which is already the fastest drafter in my phone evaluation. For a new target without a small sibling model:

1. Width-prune the target to a 0.6B-class shape and distill it (Minitron's recipe). This gives a narrow autoregressive model in the target's vocabulary.
2. Convert it to a parallel drafter with PARD's mask-token training and COD, on data with regenerated answers (PARD does not say which model regenerates them).
3. Add target features PARD-2-style: project a few target layers on the server to the drafter's width and add them to the input embedding, with stochastic gating so a feature-free mode stays available.
4. If more acceptance is needed, test a sequential head (DSpark) on top. A 2-layer DSpark outperforms the 5-layer DFlash on Qwen3-4B,[^chengDSparkConfidenceScheduledSpeculative2026] but on my phone its Markov head runs on the host CPU and cancels its gain (see [the minimum-depth question](../questions/minimum-drafter-depth-with-sequential-head.md)).

No paper has tested step 1 feeding step 2. That is the gap recorded in [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md) My first run of steps 1–2 on Qwen3-14B (one-shot prune, chat-KD recovery, PARD-1 with K=8) reaches offline MAT 1.96 on Spec-Bench, against 2.66 for the same PARD recipe on Qwen3-0.6B and 3.07 for the released `amd/PARD-Qwen3-0.6B`.[^minitron-pard-qwen3-14b] See [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md).

## Evidence

The numbers above are copied from the Paper and Method pages of the cited papers and from [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md). The NPU cost figures are from [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md), whose data lives outside `raw/`.

On why parallel drafting suits a phone at all: llada.cpp argues that the parallel decoding of diffusion LLMs aligns well with the tensor-computation capability of mobile NPUs, while autoregressive decoding exposes limited parallelism at each step.[^wangEfficientOnDeviceDiffusion2026] In my evaluation, the block drafters draft a whole tree from one decode in 22–54 ms, while the autoregressive drafters take 85–116 ms.[^drafter-evaluation]

## Caveats

- "On-device" here means a phone drafter with a server verifier. Whether speculative decoding helps with a target resident in phone DRAM is still open: see [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)
- PARD-2 adds its features to the input embedding, not through KV injection, and differs from DFlash in training and loss, so the phone comparison is between two drafter families, not a test of a narrow DFlash.
- The PARD-2 Qwen3-14B checkpoint's own ability to run without features is uncertain: see [the feature-gating question](../questions/pard-2-qwen3-14b-feature-gating.md).
- Minitron and Sheared LLaMA measure general language-model quality, not drafter acceptance.
- DFlash states that PARD's small models have a speedup ceiling of about 3×, while PARD-2 reports PARD above 4× on Qwen3 targets. This is recorded on [PARD](../methods/pard.md) and in the open question.
- My phone runs are temperature 0, 64 new tokens, 60 Spec-Bench requests, one device.[^drafter-evaluation]

## Related

- [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md), [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](../questions/cost-efficient-drafter-construction.md)
- [Can a block drafter be narrower than its target?](../questions/narrow-block-drafter.md)
- [Does starting a block drafter from the target's own layers cut its training cost?](../questions/target-layer-initialization-for-block-drafters.md)
- [DFlash research directions for mobile SpecEdge](dflash-research-directions-for-mobile-specedge.md)
- [What the target must supply to train a drafter](target-signals-for-drafter-training.md)
- [Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU](../results/block-drafters-vs-ar-drafters-on-phone-npu.md)
- Methods: [PARD](../methods/pard.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [Osprey](../methods/osprey.md), [Structured pruning](../methods/structured-pruning.md), [KV injection](../methods/kv-injection.md), [HAT](../methods/hat.md)

[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^wangEfficientOnDeviceDiffusion2026]: Wang et al. 2026
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
