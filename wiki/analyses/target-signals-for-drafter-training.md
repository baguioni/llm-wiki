---
type: Analysis
title: What the target must supply to train a drafter
description: Per drafter, which target outputs training needs (regenerated tokens, per-token target probabilities, the full target distribution, or hidden states from 3 to 5 layers), how papers obtain them online or offline, and what they cost to store for a Qwen3-14B target.
tags: [speculative-decoding, draft-model, knowledge-distillation, training-data, speculative-drafter, mobile-specedge]
question: During target inference, what information is needed to train a drafter?
sources:
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
---

# What the target must supply to train a drafter

## Question

During target inference, what information is needed to train a drafter? Which drafters need more than the target's regenerated answers, and how do papers get those signals?

## Answer

Every drafter needs the target's regenerated answers as token ids. Beyond that, it depends on the drafter:

- **PARD** needs nothing else. It uses no target features, so one drafter serves a whole target family.[^anPARDAcceleratingLLM2025]
- **Loss terms that compare against the target** need the target's probabilities:
  - PARD-2's confidence weighting uses the target's probability of each ground-truth token.[^anPARD2TargetAlignedParallel2026]
  - Its distillation term, DSpark's total-variation and confidence losses, and LK losses use the target distribution.
- **Feature drafters** (EAGLE-3, DFlash, DSpark, PARD-2 in target-dependent mode) need hidden states from 3 to 5 target layers.

All of these signals are per-position outputs of the target on a fixed token sequence. They come from one forward pass of the target over the whole sequence, which SpecForge describes as equivalent to the prefill phase of inference.[^liSpecForgeFlexibleEfficient2026] They need not be captured during generation. Papers either compute them online during training or cache them offline. The full distribution is too large to cache in practice, so the papers that report it compute it online.

## Evidence

### What each drafter's training uses

| Drafter | Regenerated tokens | Target token probabilities | Target distribution | Target hidden states |
|---|---|---|---|---|
| [PARD](../methods/pard.md)[^anPARDAcceleratingLLM2025] | Yes (Llama3 and Qwen drafters) | – | – | – |
| [PARD-2](../methods/pard.md)[^anPARD2TargetAlignedParallel2026] | – (not stated) | Yes: the weight $\hat{s}_{k}=\prod_{j<k}\hat{c}_{j}$, where $\hat{c}$ is the target's probability of each ground-truth token | Yes: a distillation term $\mathcal{L}^{\mathrm{KD}}$ | 4 layers, fused by a projection and added to the input embeddings, dropped with probability $\rho$ |
| [EAGLE-3](../methods/eagle-3.md)[^liEAGLE3ScalingInference2025] | Yes | – | – | low-, middle-, and high-level features, fused by an FC layer |
| [DFlash](../methods/dflash.md)[^chenDFlashBlockDiffusion2026] | Yes | – | – | 5 layers by default, projected and injected into every draft layer's keys and values |
| [DSpark](../methods/dspark.md)[^chengDSparkConfidenceScheduledSpeculative2026] | Yes | – | Yes: $\mathcal{L}_{\text{tv}}=\sum_{k}w_{k}\lVert p_{k}^{d}-p_{k}^{t}\rVert_{1}$, and confidence labels $c_{k}^{*}=1-\tfrac{1}{2}\lVert p_{k}^{d}-p_{k}^{t}\rVert_{1}$ | as DFlash, its backbone |
| [LK losses](../papers/samarinLKLossesDirect2026.md)[^samarinLKLossesDirect2026] | Yes | – | Yes: the target logits $z_{p}$ | depends on the drafter trained |
| [Osprey](../methods/osprey.md)[^bieOspreyTargetagnosticPretraining2026] | Yes (adaptation only) | – | Yes: logits, computed online | EAGLE-3 low, mid, and high features, computed online |

DistillSpec recommends on-policy data sampled from the draft model.[^zhouDistillSpecImprovingSpeculative2024] There the target scores sequences that the drafter generates during training, so the signals cannot come from one fixed regenerated dataset.

### Online or offline

- DFlash: "Training can be performed either online or offline." Online computes the target hidden features at each training step. Offline precomputes and caches them, and the storage grows linearly with the number of extracted features.[^chenDFlashBlockDiffusion2026]
- More features cost storage but help. With 3 draft layers and block size 16, 5 target features beat 3 on every reported benchmark. Examples: $\tau$ 5.64 against 5.38 on Math500, and 3.18 against 3.07 on MT-Bench.[^chenDFlashBlockDiffusion2026]
- Osprey computes hidden states and logits online, with the target co-served in bf16. Adapting to Qwen3-8B takes about 195k target forward passes.[^bieOspreyTargetagnosticPretraining2026] It gives per-token FLOPs during target distillation as $\approx 2(N_{p_{\theta}}+N_{q_{\phi}})$, dominated by running the target.[^bieOspreyTargetagnosticPretraining2026]
- DPara produces target features and supervision online from the frozen target.[^liuWhenParallelDrafter2026]
- SpecForge splits EAGLE-3 training into a target pass that generates hidden states and a draft-training stage. It reports that the prefill stage often becomes a dominant bottleneck in large-scale draft-model training. It runs the target on SGLang's model runner, separately from the draft model.[^liSpecForgeFlexibleEfficient2026]

### Storage per token for a Qwen3-14B target (arithmetic)

The sizes use the target dimensions in [my S25 profiling](../experiments/npu-draft-cost-profiling-galaxy-s25.md): a 151,936 × 5120 output head, so hidden size 5120 and a vocabulary of 151,936. They assume 2 bytes per value. This arithmetic is mine, not from a paper.

| Signal | Per token |
|---|---|
| Token id | 4 B (the vocabulary does not fit in 16 bits) |
| Target probability of the ground-truth token | 2 B |
| Hidden state, one layer | 5120 × 2 B ≈ 10 KB |
| EAGLE-3 (3 layers) / PARD-2 (4) / DFlash (5) | ≈ 30 / 40 / 50 KB |
| Full target distribution | 151,936 × 2 B ≈ 304 KB |

### Signals at inference, relevant to SpecEdge

- DFlash projects the concatenated target features once into the drafter's hidden size before injecting them.[^chenDFlashBlockDiffusion2026] If the server applies that projection, it sends one hidden-size vector per token instead of five. That is my inference, not a tested design.
- In target-dependent mode, PARD-2 extracts the hidden state at the last prompt position during prefill and fuses it with the mask token.[^anPARD2TargetAlignedParallel2026]
- A drafter trained on features must receive the same features at inference. A change in the target's precision or in feature compression changes what the drafter sees.

## Caveats

- PARD-2 states that it extracts features from 4 target layers, but its text names them as low-, middle-, and high-level features $l$, $m$, $h$.[^anPARD2TargetAlignedParallel2026]
- No paper here reports the storage of an offline cache, or compares the wall-clock cost of online and offline training.

## Related

- [Drafter training data across papers](drafter-training-data-across-papers.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](../questions/cost-efficient-drafter-construction.md)
- [Was PARD-2's Qwen3-14B drafter trained to run without target features?](../questions/pard-2-qwen3-14b-feature-gating.md)
- [Can a block drafter be narrower than its target?](../questions/narrow-block-drafter.md), [Does an acceptance-oriented loss help a block diffusion drafter?](../questions/acceptance-oriented-loss-for-block-drafters.md)
- Methods: [Knowledge distillation](../methods/knowledge-distillation.md), [KV injection](../methods/kv-injection.md), [Training-time test](../methods/training-time-test.md)

[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
