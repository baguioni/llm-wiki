---
type: Dataset
title: TOPv2
description: Multi-domain task-oriented compositional semantic parsing dataset, used by LayerSkip to finetune a 1.5B Llama model and measure early exit and self-speculative decoding by exact match.
tags: [dataset, semantic-parsing, speculative-decoding, early-exit, evaluation]
sources:
  - id: elhoushiLayerSkipEnablingEarly2024
    resource: zotero://select/items/@elhoushiLayerSkipEnablingEarly2024
    title: "LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding"
---

# TOPv2

## Overview

TOPv2 is a multi-domain task-oriented compositional semantic parsing dataset. Correctness requires an exact match (EM) between the generated sequence and the annotated parse.[^elhoushiLayerSkipEnablingEarly2024]

## Composition

- LayerSkip post-processes the dataset into a JSON format to align it with code pretraining, trains on the training set, and reports EM on the evaluation set.[^elhoushiLayerSkipEnablingEarly2024]
- Split sizes are not stated in the wiki's papers.

## Usage across papers

[LayerSkip](../papers/elhoushiLayerSkipEnablingEarly2024.md) finetunes a 24-layer Llama 1.5B on TOPv2 with $p_{max}=0.2$, $e_{scale}=1.0$, and the gradual early exit curriculum (batch size 32, $5.8\times10^{3}$ steps, 8 A100 80 GB).[^elhoushiLayerSkipEnablingEarly2024]

- Early exit: the baseline produces 0 EM when layers are removed; with LayerSkip, exiting at layer 12 reaches 77%, at a 3% cost at the final layer.[^elhoushiLayerSkipEnablingEarly2024]
- Self-speculative decoding on H100 (1000 sampled test examples, 8 speculations, 80 tokens, greedy): autoregressive 85.9% EM at 36 ms per token; self-speculation 82.9% EM at all exits, 29 ms ($E=18$, 1.24×), 22 ms ($E=12$, 1.64×), 18 ms ($E=6$, 2.0×).[^elhoushiLayerSkipEnablingEarly2024]
- On CPU (first 100 test samples, 7 speculations, 50 tokens): autoregressive 165 ms per token at 85.39 EM, self-speculation 87 ms at $E=6$ with 82.9 EM.[^elhoushiLayerSkipEnablingEarly2024]

## Known issues

- Self-speculation gives 82.9% EM at every exit layer, below the autoregressive row's 85.9% (H100) or 85.39 (CPU). The autoregressive row uses a model finetuned without LayerSkip, the self-speculative rows use the LayerSkip model, and LayerSkip's final layer regresses by 3% on TOPv2.[^elhoushiLayerSkipEnablingEarly2024]

## Related

- [LayerSkip](../methods/layerskip.md), [Early exit](../methods/early-exit.md), [Self-speculative decoding](../methods/self-speculative-decoding.md)

[^elhoushiLayerSkipEnablingEarly2024]: Elhoushi et al. 2024
