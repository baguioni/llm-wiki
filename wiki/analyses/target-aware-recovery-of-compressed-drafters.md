---
type: Analysis
title: Target-aware recovery of compressed drafters
description: Which speculative decoding papers recover a pruned or truncated drafter by training it against the target; HAT distills an adapter from the target's removed middle layers, Osprey recovers target-agnostically and then distills the target, Yan et al. distill without naming the teacher, and SDFP does no recovery.
tags: [speculative-decoding, draft-model, structured-pruning, knowledge-distillation, speculative-drafter, mobile-specedge]
question: Which papers do recovery by being target-aware for speculative decoding?
sources:
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: "A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
---

# Target-aware recovery of compressed drafters

## Question

Which papers build a drafter by compressing a model (pruning or truncating it) and then recover the lost quality by training against the target, rather than against the compressed model's own parent or a generic language-modeling objective?

## Answer

Only one paper in the wiki recovers a compressed drafter directly against the target: **HAT**. One more does it in two stages: **Osprey**. The other pruning-based drafter papers recover against something other than the target, or skip recovery.

1. **HAT: target-aware recovery of a truncated target.** The draft is the target's own first $m$ decoder layers and output head ($m$ less than 10% of $n$), plus an adapter $\Lambda$. $\Lambda$ is trained by knowledge distillation to imitate the cloud-side middle layers that were cut out, with an EAGLE-style loss: Smooth L1 on the pre-head hidden states plus cross-entropy through the target's head.[^xieNovelHatShapedDeviceCloud2025] The target is the teacher, and the recovery objective is the target's own hidden state.
2. **Osprey: target-agnostic recovery, then target-aware adaptation.** Osprey prunes a pretrained small LM (Qwen3-4B to 2 blocks), recovers it with next-token pretraining on FineWeb that needs no target, then adapts it per target by distilling the frozen target with EAGLE-3's training-time test.[^bieOspreyTargetagnosticPretraining2026] The pruned model is not the target, and the recovery stage itself is deliberately target-agnostic. Target awareness enters only at adaptation.
3. **Yan et al.: distillation recovery, teacher not named.** The Wide-829M draft is pruned from LLaMa-3.2-1B, and its TAR is recovered by distilling over 1 million tokens, following Muralidharan et al.[^yanDecodingSpeculativeDecoding2025] The paper does not say whether the teacher is LLaMa-3.2-1B or the LLaMa-3.1-8B target. In the recipe it follows, the teacher is the unpruned model.[^muralidharanCompactLanguageModels2024] Its other drafts (NoFT) skip recovery entirely, and they are pruned from LLaMa-7B, not from the target.[^yanDecodingSpeculativeDecoding2025]
4. **SDFP: no recovery.** SDFP prunes layers of the target itself, ranked by Fisher Information Trace, and uses the result as the draft with no training at all.[^weiSDFPSpeculativeDecoding2026]

Two general compression papers set the non-target baselines that these drafter papers borrow: Minitron recovers with distillation from the unpruned model,[^muralidharanCompactLanguageModels2024] and Sheared LLaMA continues pre-training with a language-modeling objective on 50 billion tokens.[^xiaShearedLLaMAAccelerating2024] Neither is a speculative decoding paper.

Target-aware training of an *uncompressed* drafter is common. DistillSpec distills the target into the draft with on-policy draft-generated data and a task-tuned divergence,[^zhouDistillSpecImprovingSpeculative2024] and PARD-2 adds a distillation term toward the target.[^anPARD2TargetAlignedParallel2026] Neither starts from a pruned model, so neither is recovery in the sense asked here.

## Evidence

| Paper | What is compressed | Recovery step | Teacher / objective | Target-aware? |
|---|---|---|---|---|
| [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md) | Target truncated to its first $m$ layers + head | Train adapter $\Lambda$ (one self-attention module) | Target's middle submodel; Smooth L1 on hidden states + $w_{ce}$·CE, $w_{ce}$ typically 0.1 | Yes[^xieNovelHatShapedDeviceCloud2025] |
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | Qwen3-4B pruned to 2 blocks | NTP pretraining, 55k steps, approximately 462B tokens | FineWeb text, 0 target forward passes | No, then yes at adaptation[^bieOspreyTargetagnosticPretraining2026] |
| [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md) | LLaMa-3.2-1B pruned to Wide-829M | Distillation over 1 million tokens, within 10 minutes | Not stated | Not stated[^yanDecodingSpeculativeDecoding2025] |
| [SDFP](../papers/weiSDFPSpeculativeDecoding2026.md) | Target layers pruned by FIT | None | – | No recovery[^weiSDFPSpeculativeDecoding2026] |

What each reports:

- **HAT**, Table IV, decode-phase speedup relative to U-shape inference: on SpecBench with Vicuna-7B, HAT trains 67M parameters and reaches accept length 2.06 and $1.65\times$, against U-Medusa's 591M, 1.89, and $1.41\times$. On CNN/DM with Vicuna-13B, HAT trains 105M parameters and reaches 1.98 and $1.60\times$, against U-Medusa's 760M, 1.75, and $1.45\times$.[^xieNovelHatShapedDeviceCloud2025] The device holds the first 2 layers of Vicuna-7B and the first 3 of Vicuna-13B.[^xieNovelHatShapedDeviceCloud2025] No ablation trains the adapter against anything other than the target.
- **Osprey**, Qwen3-8B 5×5 cross-domain grid: mean AL 3.686 against 3.176 for a 1-layer EAGLE-3 from scratch.[^bieOspreyTargetagnosticPretraining2026] A 10k-step pretraining checkpoint adapts to AL 3.552 against 3.578 for 55k steps.[^bieOspreyTargetagnosticPretraining2026]
- **Yan et al.**, LLaMa-3.1-8B target: Wide-829M reaches 53.35, 61.77, and 60.44 tokens/s on Chat, MMLU, and Hellaswag, against 37.41, 44.89, and 39.03 for LLaMa-3.2-1B. The paper gives no TAR or throughput for Wide-829M before its recovery step.[^yanDecodingSpeculativeDecoding2025] It states that pruning layers had a larger impact on TAR for LLaMa-3, which is why the distillation step was needed.[^yanDecodingSpeculativeDecoding2025]
- **SDFP**: overall speedups of $1.31\times$ to $1.46\times$ over vanilla autoregressive decoding on LLaMA-2 models, comparable to SWIFT's $1.34\times$ to $1.48\times$.[^weiSDFPSpeculativeDecoding2026]
- **DistillSpec**, for context: distilling the target into an uncompressed draft gives $10-45\%$ speedups over standard SD.[^zhouDistillSpecImprovingSpeculative2024]

## Caveats

- "Target-aware recovery" is my framing. None of these papers uses the phrase, and only Yan et al. call their step recovery of TAR.[^yanDecodingSpeculativeDecoding2025]
- HAT's adapter recovers the removed middle of the target, which is a narrow form of recovery: the kept layers and head are the target's own. The trained parameter counts (67M for Vicuna-7B, 105M for Vicuna-13B)[^xieNovelHatShapedDeviceCloud2025] match one attention module, $4d^{2}$, at hidden size 4096 and 5120, which suggests the kept layers are frozen. That is my arithmetic; the paper does not say so.
- No paper here compares recovery against the target with recovery against the compressed model's parent, on the same drafter. That gap is filed as an open question.

## Related

- [Where Osprey's ideas fit a pruned-target PARD pipeline](osprey-ideas-for-pruned-target-pard-pipeline.md)
- [Papers that train drafters for target agreement](drafter-training-for-target-agreement.md) (the uncompressed-drafter papers with the same goal)
- [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md) (my target-pruned drafter, recovered against the target)
- Open question: [Does recovering a pruned drafter against the target beat recovering it against its parent?](../questions/target-aware-recovery-of-pruned-drafters.md)
- [Can a pruned target be turned into a parallel drafter?](../questions/pruned-target-to-parallel-drafter.md), [How can a mobile-efficient drafter be built cheaply for a new target?](../questions/cost-efficient-drafter-construction.md)
- [What the target must supply to train a drafter](target-signals-for-drafter-training.md), [Building a parallel drafter for on-device use without training it from scratch](building-parallel-drafters-for-on-device-use.md)
- Methods: [HAT](../methods/hat.md), [Osprey](../methods/osprey.md), [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md), [DistillSpec](../methods/distillspec.md), [Layer pruning](../methods/layer-pruning.md)

[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
