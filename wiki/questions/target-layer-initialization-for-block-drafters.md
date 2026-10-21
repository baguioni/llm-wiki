---
type: Open Question
title: Does starting a block drafter from the target's own layers cut its training cost?
description: DFlash-style drafters share the target's embedding and head but train their layers from scratch, and no paper tests starting those layers from target layers.
tags: [speculative-decoding, dflash, draft-model, structured-pruning, mobile-specedge]
sources:
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: xiaShearedLLaMAAccelerating2024
    resource: zotero://select/items/@xiaShearedLLaMAAccelerating2024
    title: "Sheared LLaMA: Accelerating Language Model Pre-Training via Structured Pruning"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
---

# Does starting a block drafter from the target's own layers cut its training cost?

## Question

If the transformer layers of a DFlash-style drafter are copied from the target model instead of being randomly initialized, does the drafter reach the same acceptance length with less training data or fewer steps?

## Why it matters

The goal of the target-aware drafter work is a cheap way to build a mobile drafter for an arbitrary target. If target-layer initialization works, a block drafter becomes a target-derived model, and the construction cost falls. The shape of the drafter does not change, so its cost on the phone does not change either.

## Evidence so far

- In DFlash the embedding layer and LM head are shared with the target and frozen, and only the draft transformer layers are updated.[^chenDFlashBlockDiffusion2026]
- The DFlash paper trains for 6 epochs and runs its ablations on 100K samples.[^chenDFlashBlockDiffusion2026]
- Deriving a small model from a pretrained one is cheap for general language models. Sheared LLaMA prunes LLaMA2-7B to 1.3B and 2.7B parameters with $3\%$ of the compute of training such models from scratch.[^xiaShearedLLaMAAccelerating2024] Minitron needs up to 40$\times$ fewer training tokens.[^muralidharanCompactLanguageModels2024]
- SDFP builds a working draft from the target's layers with no training, with overall speedups of $1.31\times$ to $1.46\times$ on LLaMA-2 models.[^weiSDFPSpeculativeDecoding2026]

### Osprey: warm-starting drafters from a pretrained LM

- For an EAGLE-3-style autoregressive drafter, starting the body from a pruned small LM pretrained on web text (not from the target) raises mean AL on Qwen3-8B from 3.176 to 3.686 at the same per-target training budget.[^bieOspreyTargetagnosticPretraining2026]
- The warm start makes adaptation less sensitive to the learning rate. Going from $10^{-4}$ to $10^{-5}$ costs Osprey 0.11 AL and the from-scratch EAGLE-3 1.07 AL.[^bieOspreyTargetagnosticPretraining2026]
- For a DFlash drafter on Qwen3-8B, a body warm-started from a diffusion LM gains at most $0.07$ accepted tokens in any domain over a random body (math in-domain 6.03 against 5.96, OOD average 1.68 against 1.64).[^bieOspreyTargetagnosticPretraining2026]
- The authors' hypothesis is key/value distribution drift: under KV injection the pretrained body's attention receives target-derived keys and values it never saw in pretraining. An EAGLE-style DFlash variant with zero-initialized target projections and causal attention raises OOD AL to 2.00, but in-domain math falls to 5.25.[^bieOspreyTargetagnosticPretraining2026]

**Inference.** Osprey's warm start is not from the target's own layers, so it does not test this question directly. But its DFlash result is the closest evidence in the wiki, and it is negative for the KV-injection interface: a pretrained body helped little once it had to read injected target keys and values. Target layers would face the same issue, since they too never saw injected keys and values.

**Inference.** Reasons it may not help: the deep target layers expect a residual stream that has passed through the earlier layers, while the drafter feeds them token embeddings and mask tokens. The target layers were trained with causal attention, while a block drafter attends in both directions inside a block. The projection of the fused target features has no counterpart in the target and stays randomly initialized.

**Inference.** My prediction is that the benefit, if any, shows with little training data and disappears with the full training set.

## Conflicting claims

None. No paper in the wiki tests initialization from the target's own layers. Osprey tests initialization from another pretrained model.[^bieOspreyTargetagnosticPretraining2026]

## What would resolve it

Three training runs on the same subset of about 100K samples, compared on acceptance length at equal steps and on the steps needed to reach the baseline's final value:

1. Random initialization with the released recipe.
2. Draft layers copied from target layers, with a lower learning rate.
3. As 2, with early target layers for the first draft layers and late target layers for the rest.

## Related

- [Building a parallel drafter for on-device use without training it from scratch](../analyses/building-parallel-drafters-for-on-device-use.md)
- [Can a pruned target be turned into a parallel drafter?](pruned-target-to-parallel-drafter.md)
- [DFlash research directions for mobile SpecEdge](../analyses/dflash-research-directions-for-mobile-specedge.md)
- [DFlash](../methods/dflash.md), [Osprey](../methods/osprey.md), [Sheared-LLaMA](../methods/sheared-llama.md), [Structured pruning](../methods/structured-pruning.md), [KV injection](../methods/kv-injection.md)
- [Does an acceptance-oriented loss help a block diffusion drafter?](acceptance-oriented-loss-for-block-drafters.md)
- [Can a block drafter be narrower than its target?](narrow-block-drafter.md)
- [How can a mobile-efficient drafter be built cheaply for a new target?](cost-efficient-drafter-construction.md)

[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^xiaShearedLLaMAAccelerating2024]: Xia et al. 2024
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
