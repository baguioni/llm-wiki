---
type: Method
title: Self-speculative decoding
description: Speculative decoding in which the draft comes from the target model itself (its early layers, a subset of its layers, or masked positions of the same forward pass) instead of a separate draft model, as in LayerSkip, Draft & Verify, SWIFT, SDFP, and I-DLM.
tags: [speculative-decoding, self-speculative-decoding, early-exit, draft-model, llm-inference]
sources:
  - id: elhoushiLayerSkipEnablingEarly2024
    resource: zotero://select/items/@elhoushiLayerSkipEnablingEarly2024
    title: "LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding"
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
---

# Self-speculative decoding

## Overview

Self-speculative methods avoid an auxiliary drafter and draw proposals from the target itself.[^bieOspreyTargetagnosticPretraining2026] Osprey summarizes the trade-off: they remove the cost of training and serving a separate drafter, but tie the drafter to the target's parameters and tokenizer, so it cannot be reused across different targets without retraining the target as well.[^bieOspreyTargetagnosticPretraining2026]

## How it works

The draft-then-verify loop is that of [speculative decoding](speculative-decoding.md); what changes is where the draft comes from.

- **Early exit of the same model.** [LayerSkip](layerskip.md) drafts with the first $E$ layers and the shared LM head, and verifies with the remaining $L-E$ layers. Draft and verification share one KV cache, and the exit layer's query is cached, so verification does not recompute the first $E$ layers.[^elhoushiLayerSkipEnablingEarly2024]
- **Skipping intermediate layers.** Draft & Verify (Zhang et al. 2023) skips a group of intermediate attention and FFN layers to form the draft. LayerSkip notes that this prevents reusing the draft's activations and KV cache in verification.[^elhoushiLayerSkipEnablingEarly2024] Osprey describes it as adaptively skipping intermediate layers at inference time, and SWIFT as choosing the layers to skip on the fly without auxiliary training.[^bieOspreyTargetagnosticPretraining2026]
- **Pruned copies of the target.** SDFP prunes the target's layers ranked by Fisher Information Trace to form a training-free draft.[^weiSDFPSpeculativeDecoding2026]
- **Proposals and verification in one pass.** [I-DLM](i-dlm.md) proposes tokens at [MASK] positions and verifies the previous step's proposals at clean positions of the same forward pass, with the $p/q$ acceptance rule. The paper presents this single-forward drafting-and-verification structure as a natural fit for self-speculative decoding.[^yuIntrospectiveDiffusionLanguage2026]
- **Adapters on shallow layers.** Osprey lists Kangaroo, which adds a small adapter on top of the target's shallow layers.[^bieOspreyTargetagnosticPretraining2026]

## Variants

| Method | Draft source | Needs training | Source |
|---|---|---|---|
| LayerSkip | first $E$ layers + shared LM head | yes, layer dropout and early exit loss in pretraining or finetuning | LayerSkip[^elhoushiLayerSkipEnablingEarly2024] |
| Draft & Verify | target with intermediate layers skipped | no weight change | LayerSkip[^elhoushiLayerSkipEnablingEarly2024] |
| SELF-SD | (not described) | 1000 Bayesian optimization iterations before inference, $\sim$7.5 hours | SDFP[^weiSDFPSpeculativeDecoding2026] |
| SWIFT | layers chosen on the fly | no training, a few minutes of optimization each time | SDFP[^weiSDFPSpeculativeDecoding2026] |
| SDFP | target with FIT-ranked layers pruned | no | SDFP[^weiSDFPSpeculativeDecoding2026] |
| I-DLM (R-ISD) | [MASK] positions with a gated LoRA; verification by base weights | yes, conversion of the AR model (4.5B tokens) | I-DLM[^yuIntrospectiveDiffusionLanguage2026] |

## Papers using it

- [LayerSkip](../papers/elhoushiLayerSkipEnablingEarly2024.md): 1.34× to 2.16× over autoregressive decoding on Llama2 models, greedy. On Llama2 13B, CNN/DM, it reports 1.81× against 1.56× for Draft & Verify, and on XSUM 1.34× against 1.48×.[^elhoushiLayerSkipEnablingEarly2024]
- [Decoding Speculative Decoding](../papers/yanDecodingSpeculativeDecoding2025.md) compares its pruned wide drafts with self-speculative decoding (Zhang et al. 2023) in the settings where the latter is fastest (LLaMa-2-70B target, greedy): 131% vs 99% speedup on CNNDM and 145% vs 60% on XSum.[^yanDecodingSpeculativeDecoding2025] Self-speculative decoding on a 70B target still computes 33 attention and 43 MLP layers per draft token, against 5 of each for the NoFT-Wide-796M draft.[^yanDecodingSpeculativeDecoding2025] With LLaMa-3.1-8B as target, Wide-829M has $51.8\%$ higher throughput than self-speculative decoding.[^yanDecodingSpeculativeDecoding2025]
- [SDFP](../papers/weiSDFPSpeculativeDecoding2026.md) compares against SWIFT, a layer-skipping SD framework, and lists the draft construction cost of LayerSkip-SD, SELF-SD, and SWIFT.[^weiSDFPSpeculativeDecoding2026]
- [I-DLM](../papers/yuIntrospectiveDiffusionLanguage2026.md): I-DLM-8B, a converted Qwen3-8B, reaches 341 tok/s on MATH-500 at concurrency 1 in SGLang, and the bit-for-bit lossless R-ISD variant 310 tok/s, against 238 tok/s for EAGLE-3 on the original Qwen3-8B.[^yuIntrospectiveDiffusionLanguage2026]

## Strengths & Limitations

- No separate draft model to train, store, or keep in sync, and lower memory footprint.[^elhoushiLayerSkipEnablingEarly2024][^yuIntrospectiveDiffusionLanguage2026]
- Methods that need training change the target's weights: LayerSkip costs last-layer accuracy on Llama3 models,[^elhoushiLayerSkipEnablingEarly2024] and I-DLM without the gated LoRA is slightly below its AR base on most benchmarks.[^yuIntrospectiveDiffusionLanguage2026]
- The draft is a large fraction of the target. Yan et al. attribute their throughput advantage to this: their draft's autoregressive decoding latency is $7\%$ of the 70B target's prefill latency.[^yanDecodingSpeculativeDecoding2025]
- The drafter cannot be shared across targets.[^bieOspreyTargetagnosticPretraining2026]

## Related

- [LayerSkip](layerskip.md), [Early exit](early-exit.md), [I-DLM](i-dlm.md), [SDFP](sdfp.md), [Speculative decoding](speculative-decoding.md)
- [Multi-token prediction](multi-token-prediction.md)
- [HAT](hat.md) (on-device draft from the LLM's shallow layers, head, and an adapter)
- [Does choosing what to prune by target agreement beat LM-loss importance?](../questions/target-agreement-pruning-criteria.md)

[^elhoushiLayerSkipEnablingEarly2024]: Elhoushi et al. 2024
[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
