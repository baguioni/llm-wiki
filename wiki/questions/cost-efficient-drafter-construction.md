---
type: Open Question
title: How can a mobile-efficient drafter be built cheaply for a new target?
description: Given an arbitrary target LLM with no suitable first-party or size-matched drafter, how can a drafter that fits a phone NPU be constructed at low training cost; the papers measure construction cost for server drafters only.
tags: [speculative-decoding, draft-model, mobile-specedge, mobile-npu, speculative-drafter, training-data, pard, osprey]
sources:
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# How can a mobile-efficient drafter be built cheaply for a new target?

## Question

Given an arbitrary target LLM, how can we cost-efficiently construct a mobile-efficient speculative drafter when no suitable first-party or size-matched drafter exists? This is the research question of my mobile SpecEdge project, where a phone NPU drafts and a server verifies Qwen3-14B.

## Why it matters

- On my Galaxy S25 NPU, draft latency follows the weight bytes read per token. A width-5120 output head alone costs 8.3 ms per token, about one Qwen3-0.6B step (9.5 ms), and a 16-token pass costs 1.1 to 2.3 single-token steps. See [my S25 profiling](../experiments/npu-draft-cost-profiling-galaxy-s25.md). Released server drafters are not shaped for that budget, so a drafter that fits the phone usually has to be built.
- Construction cost decides whether the approach scales to new targets. Most drafters are target-dependent and need a new drafter trained for each target.[^anPARD2TargetAlignedParallel2026]

## Evidence so far

### Target-independent drafters avoid per-target training

- [PARD](../methods/pard.md) adapts a small language model of the target's own series into a parallel drafter. It uses no target features, so one drafter serves a whole target family.[^anPARDAcceleratingLLM2025]
- PARD's conditional drop-token raises training efficiency by up to 3×.[^anPARDAcceleratingLLM2025]
- PARD estimates training cost in Pflops per 1M tokens for a LLaMA3-70B target: about 20.22 for PARD, 149.20 for EAGLE, and 204.4 for EAGLE-3, which it summarizes as 7× and 10× more efficient. Most of the EAGLE cost is the 70B target's forward pass, which PARD does not run.[^anPARDAcceleratingLLM2025]
- PARD-2 adds optional target features and trains one drafter for both modes. Without features, it raises PARD's average speedup on Qwen3-14B from 4.38× to 4.79×.[^anPARD2TargetAlignedParallel2026] Whether its Qwen3-14B drafter can run feature-free is itself unclear: see [Was PARD-2's Qwen3-14B drafter trained to run without target features?](pard-2-qwen3-14b-feature-gating.md)

### Pretraining once, then adapting cheaply

- [Osprey](../methods/osprey.md) prunes a pretrained small LM to 2 layers and pretrains it once on FineWeb without any target. It then adapts the drafter to each target, with vocabulary resizing and EAGLE-3 distillation.[^bieOspreyTargetagnosticPretraining2026]
- Per-target adaptation costs the same as EAGLE-3 training: 48 H100-hours for Qwen3-8B. Pretraining costs 3,040 H100-hours for 55k steps, or 576 for 10k.[^bieOspreyTargetagnosticPretraining2026]
- The 10k-step checkpoint adapts to an overall AL of 3.552, against 3.578 for the 55k-step checkpoint.[^bieOspreyTargetagnosticPretraining2026] Most of the pretraining benefit comes early.
- Osprey's advantage over EAGLE-3 is larger out of domain (mean AL 3.493 against 2.977) than in domain (4.465 against 3.971).[^bieOspreyTargetagnosticPretraining2026]
- The drafter runs at the hidden size of its source model (2560), narrower than the target's.[^bieOspreyTargetagnosticPretraining2026]

### Pruning the target itself (my experiment)

- [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md) builds a PARD-1 drafter for Qwen3-14B from Qwen3-14B alone: one Minitron prune to the Qwen3-0.6B shape (64 min on a GB10), 49,872 target-written answers (7.9 h on a GB10), chat-KD recovery (3 h 44 min on one H100), and PARD-1 (88 min on one H100).[^minitron-pard-qwen3-14b]
- Offline on Spec-Bench it reaches MAT 1.96 at K=8, against 2.66 for the same PARD recipe on Qwen3-0.6B and 3.07 for the released `amd/PARD-Qwen3-0.6B`. The gap follows the recovered backbone's first-token accuracy (0.570 against 0.751).[^minitron-pard-qwen3-14b]
- **Inference.** For a target with no small sibling this route works end to end at a cost of hours, but with this much data it gives up about a quarter of the MAT that a same-series small model gives. See [Can a pruned target be turned into a parallel drafter?](pruned-target-to-parallel-drafter.md)

### Data budget

- Full recipes use about 0.5M to 1.4M target-regenerated samples. Adaptation and ablations use 65K to 100K. See [Drafter training data across papers](../analyses/drafter-training-data-across-papers.md).
- EAGLE-3's speedup keeps rising with more training data.[^liEAGLE3ScalingInference2025] SpecForge finds that data composition and regeneration both raise acceptance.[^liSpecForgeFlexibleEfficient2026]
- DistillSpec recommends on-policy data sampled from the draft model, which it finds similar to or better than target-generated data at much lower cost.[^zhouDistillSpecImprovingSpeculative2024]

### Target signals

- Feature drafters and distillation losses need the target running during training, or a cache whose size grows with the number of features.[^chenDFlashBlockDiffusion2026] SpecForge reports the target's prefill as a dominant bottleneck in large-scale draft-model training.[^liSpecForgeFlexibleEfficient2026] See [What the target must supply to train a drafter](../analyses/target-signals-for-drafter-training.md).

### Warm starts for block drafters

- For a DFlash drafter under KV injection, Osprey's diffusion-LM warm start gains at most 0.07 accepted tokens in any domain over a random body.[^bieOspreyTargetagnosticPretraining2026] So pretraining helps the EAGLE-3-style interface but has not been shown to help the KV-injection one.

### Reusing released drafters on the phone (HyCo)

- [HyCo](../papers/baeHyCoHybridDrafting2026.md) trains no new drafter. It keeps its drafters as released, apart from quantization and a restricted output vocabulary, and calls drafter-retraining approaches (DistillSpec, PARD) orthogonal.[^baeHyCoHybridDrafting2026]
- Its two drafters are the target's own released MTP head and a released small model of the same family (Gemma 4 E2B from Google's QAT checkpoint). The only weight training is 100 steps of 4-bit QAT on the MTP head, about 1.5 s per step on one DGX Spark, on 60 prompts with the verifier's greedy answers.[^baeHyCoHybridDrafting2026]
- The SLM half was also used without retraining for a verifier of another family (Muse-Glimmer-30B) through a token bridge.[^baeHyCoHybridDrafting2026]
- **Inference.** This route needs a target that ships a native draft head the phone can run. For a target like Qwen3-14B, which my project uses, the wiki has no such head, so HyCo's recipe would cover only the SLM half.

## Conflicting claims

None between sources so far. The construction costs above are for server drafters (Osprey on H100, PARD estimated in FLOPs) and come from different accounting methods, so they cannot be compared directly.

## What would resolve it

- Measure acceptance against construction GPU-hours for drafters built for the same target (Qwen3-14B) from the same target-regenerated data. Vary the donor (same-series small LM, older series, cross-family with vocabulary transfer) and the data budget, and keep every candidate inside the phone's draft-cost budget.
- Run existing checkpoints on the phone first, to fix which architecture (block or chain, with or without target features) the construction should target.
- Answer the related questions on width, initialization, and loss for block drafters, below.

## Related

- [Building a parallel drafter for on-device use without training it from scratch](../analyses/building-parallel-drafters-for-on-device-use.md)
- [Can a pruned target be turned into a parallel drafter?](pruned-target-to-parallel-drafter.md), [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)
- [Can a block drafter be narrower than its target?](narrow-block-drafter.md)
- [Does starting a block drafter from the target's own layers cut its training cost?](target-layer-initialization-for-block-drafters.md)
- [Does an acceptance-oriented loss help a block diffusion drafter?](acceptance-oriented-loss-for-block-drafters.md)
- [What is the smallest block drafter that keeps acceptance with a sequential head?](minimum-drafter-depth-with-sequential-head.md)
- [Does speculative decoding help on a mobile NPU?](speculative-decoding-on-mobile-npu.md)
- [Drafter training data across papers](../analyses/drafter-training-data-across-papers.md), [What the target must supply to train a drafter](../analyses/target-signals-for-drafter-training.md)
- Methods: [HyCo](../methods/hyco.md), [Multi-Token Prediction (MTP)](../methods/multi-token-prediction.md), [PARD](../methods/pard.md), [Osprey](../methods/osprey.md), [DFlash](../methods/dflash.md), [Knowledge distillation](../methods/knowledge-distillation.md), [Vocabulary transfer](../methods/vocabulary-transfer.md)

[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
