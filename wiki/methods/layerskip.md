---
type: Method
title: LayerSkip
description: Training recipe (depth-increasing layer dropout plus a shared-LM-head early exit loss) that makes a model's early layers usable as a draft, followed by self-speculative decoding in which the first E layers draft and the remaining layers verify with one shared KV cache.
tags: [speculative-decoding, self-speculative-decoding, early-exit, layer-dropout, draft-model]
sources:
  - id: elhoushiLayerSkipEnablingEarly2024
    resource: zotero://select/items/@elhoushiLayerSkipEnablingEarly2024
    title: "LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding"
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
---

# LayerSkip

## Overview

LayerSkip makes an LLM less reliant on its later layers so that it can [exit early](early-exit.md), then uses the early exit as the draft in [self-speculative decoding](self-speculative-decoding.md).[^elhoushiLayerSkipEnablingEarly2024] It adds no auxiliary layers or modules: every layer exits through the model's own LM head.[^elhoushiLayerSkipEnablingEarly2024]

## How it works

- **Layer dropout.** Each layer is skipped per sample with rate $p_{l,t}=S(t)D(l)p_{max}$; $D(l)$ rises exponentially from 0 at the first layer to 1 at the last, and $S(t)$ is 1 for finetuning and continual pretraining or an exponential curriculum for pretraining from scratch.[^elhoushiLayerSkipEnablingEarly2024]
- **Early exit loss.** Cross-entropy of the shared LM head applied to every layer's output, weighted by normalized scales that grow quadratically with depth and controlled by $e_{scale}$. A rotational ($C_{\text{rot},R}$) or gradual ($C_{\text{grad}}$) curriculum decides which layers' exit losses are active at each iteration.[^elhoushiLayerSkipEnablingEarly2024]
- **Self-drafting.** Generate $d$ tokens autoregressively with the first $E$ layers and the LM head.[^elhoushiLayerSkipEnablingEarly2024]
- **Self-verification.** Run layers $E$ to $L$ on the draft in one pass; accept up to the first mismatch and append the next verified token.[^elhoushiLayerSkipEnablingEarly2024]
- **KVQ cache.** The first $E$ layers' KV cache is shared between draft and verification, and the exit layer's query is cached so verification continues from layer $E$.[^elhoushiLayerSkipEnablingEarly2024]

## Variants

- Layer dropout only (LD), early exit loss only (EE), or both (LD+EE).[^elhoushiLayerSkipEnablingEarly2024]
- Applied in four training regimes: continual pretraining (Llama2 7B/13B, Llama3 8B, Llama3.2 1B), pretraining from scratch (Llama2 1.5B and 7B), finetuning on code (Llama1 7B), and finetuning on TOPv2 (Llama 1.5B).[^elhoushiLayerSkipEnablingEarly2024]

## Papers using it

- [Elhoushi et al. 2024](../papers/elhoushiLayerSkipEnablingEarly2024.md) propose it. Self-speculative speedups with greedy decoding:[^elhoushiLayerSkipEnablingEarly2024]

  | Model (training) | Task | $E$ | Token acceptance | Speedup | GPU |
  |---|---|---|---|---|---|
  | Llama2 7B (continual) | CNN/DM | 8 | 68.9% | 1.86× | H100 |
  | Llama2 13B (continual) | CNN/DM | 15 | 74.5% | 1.81× | H100 |
  | Llama2 13B (continual) | XSUM | 15 | 67.7% | 1.34× | H100 |
  | Llama2 7B (continual) | HumanEval | 8 | 67.1% | 1.83× | H100 |
  | Llama2 7B (scratch, 26B tokens) | CNN/DM | 8 | 77.8% | 2.16× | H100 |
  | Llama1 7B (code) | HumanEval | 6 | 45% | 1.82× | A100 |
  | Llama 1.5B (TOPv2) | TOPv2 | 6 | 76.0% | 2.0× | H100 |

  All rows: [^elhoushiLayerSkipEnablingEarly2024]

- [SDFP](../papers/weiSDFPSpeculativeDecoding2026.md) lists LayerSkip-SD's draft construction cost for LLaMA-2-13B as $50\times10^{3}$ training steps with 64 A100 (80GB), against no training for SDFP.[^weiSDFPSpeculativeDecoding2026]
- [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) prunes facebook/layerskip-llama3.2-1B to 4 of its 16 blocks as one of its drafter backbones, and reports that early-exit-trained models such as LayerSkip give a stronger initialization because their auxiliary early-exit objectives train intermediate layers to predict the next token.[^bieOspreyTargetagnosticPretraining2026]

## Strengths & Limitations

- One model and one KV cache serve both draft and verification, so memory footprint is lower than with a separate draft model.[^elhoushiLayerSkipEnablingEarly2024]
- Unlike Draft & Verify (Zhang et al. 2023), which skips intermediate layers, verification can reuse the draft stage's activations and KV cache because both run the same early layers in the same order.[^elhoushiLayerSkipEnablingEarly2024]
- Needs finetuning or pretraining with the recipe, and $p_{max}$, $e_{scale}$, and $R$ must be tuned to avoid last-layer accuracy loss.[^elhoushiLayerSkipEnablingEarly2024] Continual pretraining of Llama3 8B lowers last-layer MMLU from 66.5 to 60.5 and HumanEval from 37.8 to 28.7.[^elhoushiLayerSkipEnablingEarly2024]
- The paper evaluates greedy verification only.[^elhoushiLayerSkipEnablingEarly2024]

## Related

- [Self-speculative decoding](self-speculative-decoding.md), [Early exit](early-exit.md), [Speculative decoding](speculative-decoding.md)
- [SDFP](sdfp.md) (training-free drafts from the target's own layers), [Osprey](osprey.md), [HAT](hat.md) (drafts from the LLM's shallow layers on a device)
- [Does starting a block drafter from the target's own layers cut its training cost?](../questions/target-layer-initialization-for-block-drafters.md)

[^elhoushiLayerSkipEnablingEarly2024]: Elhoushi et al. 2024
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
