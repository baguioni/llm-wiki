---
type: Method
title: Early exit
description: Stopping a token's forward pass at an intermediate layer and predicting from that layer's hidden state, used in the wiki's papers as a self-speculative draft (LayerSkip) and to prune low-value branches of a verification tree (Lever).
tags: [early-exit, speculative-decoding, self-speculative-decoding, llm-inference]
sources:
  - id: elhoushiLayerSkipEnablingEarly2024
    resource: zotero://select/items/@elhoushiLayerSkipEnablingEarly2024
    title: "LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding"
  - id: wangLeverSpeculativeLLM2026a
    resource: zotero://select/items/@wangLeverSpeculativeLLM2026a
    title: "Lever: Speculative LLM Inference on Smartphones"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
---

# Early exit

## Overview

Early exit runs only the first $E$ layers for a token and maps that layer's output to logits, skipping the remaining layers. Projecting an intermediate layer's output through the LM head (the "unembedding" operation) is equivalent to exiting at that layer.[^elhoushiLayerSkipEnablingEarly2024] Unlike quantization or sparsity, reducing the number of layers needs no specialized hardware or kernels.[^elhoushiLayerSkipEnablingEarly2024]

## How it works

- **Exit head.** Most earlier early-exit work trains a dedicated LM head per layer or adds modules per exit; [LayerSkip](layerskip.md) shares the model's single LM head across all layers.[^elhoushiLayerSkipEnablingEarly2024] [Lever](lever.md) instead trains a linear predictor $W\in\mathbb{R}^{|\mathcal{V}|\times d}$ at a middle layer of a frozen target.[^wangLeverSpeculativeLLM2026a]
- **Training the exit.** LayerSkip adds an early exit loss on every layer (with a curriculum) plus depth-increasing layer dropout, changing the model's weights.[^elhoushiLayerSkipEnablingEarly2024] Lever keeps the target frozen and distills the target's final distribution into the predictor with a full-vocabulary KD loss plus a candidate-set KD loss over the draft's candidates.[^wangLeverSpeculativeLLM2026a]
- **Deciding when to exit.** LayerSkip uses a fixed exit layer $E$.[^elhoushiLayerSkipEnablingEarly2024] In its related work, Elbayad et al. (2020) exit statically and dynamically with auxiliary layers that learn when to exit, and CALM looks for criteria to choose the exit layer at inference. LayerSkip lists per-token dynamic exit layers as future work.[^elhoushiLayerSkipEnablingEarly2024]

## Variants

- **Early exit as the final output.** Fast but lossy: on TOPv2, Llama 1.5B with LayerSkip falls from 85.9% EM (full model) to 79.4% at $E=12$ and 62.9% at $E=6$.[^elhoushiLayerSkipEnablingEarly2024]
- **Early exit as a draft, corrected by the remaining layers** ([self-speculative decoding](self-speculative-decoding.md)): the same TOPv2 model keeps 82.9% EM at $E=6$ with a 2.0× speedup.[^elhoushiLayerSkipEnablingEarly2024]
- **Early exit inside verification.** Lever scores each branch of a draft tree at an intermediate target layer and drops low-value branches before the upper layers; the full target still decides acceptance. It keeps about 48% of upper-layer rows, cuts verification latency by 12.2%, and retains about 95% of accepted tokens.[^wangLeverSpeculativeLLM2026a]

## Papers using it

- [LayerSkip](../papers/elhoushiLayerSkipEnablingEarly2024.md): in a pretrained Llama1 7B on a HumanEval prompt, a token needs on average 23.45 of 32 layers, so an ideal exit predictor could save at most 26% of computation without retraining.[^elhoushiLayerSkipEnablingEarly2024] After continual pretraining with LayerSkip, Llama2 7B's middle layer (16) reaches Wikipedia perplexity 8.12 against 1900 for the baseline.[^elhoushiLayerSkipEnablingEarly2024]
- [Lever](../papers/wangLeverSpeculativeLLM2026a.md): early-exit verification pruning on smartphones with a flash-resident target.[^wangLeverSpeculativeLLM2026a]
- [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md): early-exit-trained models such as LayerSkip give a stronger initialization for a depth-pruned drafter because the early-exit objectives train intermediate layers to predict the next token.[^bieOspreyTargetagnosticPretraining2026]

## Strengths & Limitations

- Without early-exit training, early layers are poor predictors: Llama3 8B's middle layer has Wikipedia perplexity $1.10\times10^{05}$.[^elhoushiLayerSkipEnablingEarly2024]
- In LayerSkip's pretraining-from-scratch ablation, middle-layer perplexity increases drastically with more pretraining tokens unless the early exit loss is applied.[^elhoushiLayerSkipEnablingEarly2024]
- Multiple-choice tasks degrade less than open-ended generation when exiting early, which the paper attributes to errors compounding over generated tokens.[^elhoushiLayerSkipEnablingEarly2024]

## Related

- [LayerSkip](layerskip.md), [Self-speculative decoding](self-speculative-decoding.md), [Lever](lever.md), [Speculative decoding](speculative-decoding.md)

[^elhoushiLayerSkipEnablingEarly2024]: Elhoushi et al. 2024
[^wangLeverSpeculativeLLM2026a]: Wang et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
