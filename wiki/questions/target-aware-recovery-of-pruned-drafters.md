---
type: Open Question
title: Does recovering a pruned drafter against the target beat recovering it against its parent?
description: Pruned drafters in the wiki are recovered against their own unpruned parent, a generic language-modeling objective, or not at all; only HAT trains against the target, and only a small adapter, so no paper measures whether target-aware recovery raises acceptance over self-recovery; my Qwen3-14B run recovers a pruned target against itself with one loss only.
tags: [speculative-decoding, draft-model, structured-pruning, knowledge-distillation, speculative-drafter, mobile-specedge]
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
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
---

# Does recovering a pruned drafter against the target beat recovering it against its parent?

## Question

When a drafter is made by pruning a model, and the pruned model is then retrained to recover its quality, does using the target as the teacher (with a loss aimed at acceptance) give a higher acceptance rate than recovering against the drafter's own unpruned parent or with a plain language-modeling objective, at the same token budget?

## Why it matters

Pruning is a cheap route to a drafter for a target with no size-matched small model (see [Can a pruned target be turned into a parallel drafter?](pruned-target-to-parallel-drafter.md)). If recovery against the target is better, the recovery step and the drafter-alignment step can be one training run instead of two. See [Target-aware recovery of compressed drafters](../analyses/target-aware-recovery-of-compressed-drafters.md).

## Evidence so far

- HAT keeps the target's first layers and head on the device and trains an adapter by distillation from the target's removed middle layers. It reaches accept length 2.06 on SpecBench with Vicuna-7B and 1.98 on CNN/DM with Vicuna-13B.[^xieNovelHatShapedDeviceCloud2025] There is no self-recovery baseline.
- Osprey recovers its pruned body with target-agnostic pretraining, then distills the target per target.[^bieOspreyTargetagnosticPretraining2026] It does not test skipping the target-agnostic stage and recovering against the target alone.
- Yan et al. recover the TAR of a pruned Wide-829M by distilling over 1 million tokens, without naming the teacher.[^yanDecodingSpeculativeDecoding2025]
- SDFP prunes the target and uses it untrained.[^weiSDFPSpeculativeDecoding2026]
- For uncompressed drafters, DistillSpec reports $10-45\%$ speedups over standard SD from distilling the target into the draft.[^zhouDistillSpecImprovingSpeculative2024]
- For general compression, Nemotron-4 15B as the teacher gives better results than Minitron 8B as the teacher in Minitron's final retraining step.[^muralidharanCompactLanguageModels2024] That result is about language-model accuracy, not acceptance.

### My experiment: [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)

- Qwen3-14B pruned to the Qwen3-0.6B shape is recovered by online forward-KL distillation from Qwen3-14B (temperature 1.0, full vocabulary, answer tokens only) on 49,372 of Qwen3-14B's own greedy answers, 3 epochs, 57M target tokens.[^minitron-pard-qwen3-14b] Here the parent and the target are the same model, the case of step 3 below.
- On Spec-Bench, recovery lifts the pruned model from top-1 0.038 and MAT 1.04 to top-1 0.572 and MAT 2.17 at γ=5, against 3.12 for an off-the-shelf Qwen3-0.6B.[^minitron-pard-qwen3-14b]
- On 500 held-out answers the curve rises fastest early (τ at γ=5: 1.02 at step 0, 1.80 at 6.4M tokens, 2.09 at 19M) and is flat by epoch 3 (2.31 at 57.6M).[^minitron-pard-qwen3-14b]
- An earlier version recovered the same pruned model on SlimPajama web text from a cached top-64 teacher. The report calls it superseded and gives no numbers, so the run does not compare data sources. Its explanation for why chat answers worked is that the teacher's greedy answers have lower entropy than web text and Spec-Bench references are the same teacher's chat answers.[^minitron-pard-qwen3-14b]
- Only forward KL was used. The training code supports RKL, JSD, and TVD, and no on-policy samples were used.[^minitron-pard-qwen3-14b]

## Conflicting claims

None. The papers do not test the question, and my run has a single recovery arm.

## What would resolve it

1. Prune one drafter (for example Qwen3-0.6B, or Qwen3-14B cut to that shape) and recover it three ways at equal tokens: language-modeling loss, distillation from its unpruned parent, and distillation from the target with a DistillSpec-style divergence.
2. Measure acceptance length on the same benchmark and target for each, and for the unrecovered model.
3. If the pruned model is the target itself, the second and third arms share a teacher; then compare only the loss (language-modeling KD against an acceptance-oriented divergence). My Qwen3-14B run supplies the forward-KL arm and its data ([Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)); the other divergences have not been run.

## Related

- [Target-aware recovery of compressed drafters](../analyses/target-aware-recovery-of-compressed-drafters.md)
- [Papers that train drafters for target agreement](../analyses/drafter-training-for-target-agreement.md)
- [Does choosing what to prune by target agreement beat LM-loss importance?](target-agreement-pruning-criteria.md)
- [Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md)
- [Can a pruned target be turned into a parallel drafter?](pruned-target-to-parallel-drafter.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)
- [Does an acceptance-oriented loss help a block diffusion drafter?](acceptance-oriented-loss-for-block-drafters.md)
- Methods: [Structured pruning](../methods/structured-pruning.md), [Knowledge distillation](../methods/knowledge-distillation.md), [HAT](../methods/hat.md), [Osprey](../methods/osprey.md), [DistillSpec](../methods/distillspec.md)

[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
