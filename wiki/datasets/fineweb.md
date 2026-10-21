---
type: Dataset
title: FineWeb
description: Web text corpus whose 100B-token sample (sample-100BT) Osprey uses for target-agnostic next-token pretraining of its pruned drafter backbone.
tags: [web-text, pretraining-data, speculative-decoding, draft-model]
sources:
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
---

# FineWeb

## Overview

Osprey cites FineWeb as Penedo et al. 2024, "The FineWeb datasets: Decanting the web for the finest text data at scale", in the NeurIPS Datasets and Benchmarks Track.[^bieOspreyTargetagnosticPretraining2026] It is the only paper in this wiki that uses the dataset. Osprey continues pretraining a depth-pruned small LM on the FineWeb sample-100BT corpus with next-token prediction (Stage 2), to restore its language-modeling ability before target-specific adaptation. The result is the *shallow NTP backbone* that all [Osprey](../methods/osprey.md) drafters start from.[^bieOspreyTargetagnosticPretraining2026]

## Composition

Only what Osprey states.

- Osprey uses a 100B-token sample from FineWeb, which it names FineWeb-100BT and FineWeb sample-100BT.[^bieOspreyTargetagnosticPretraining2026]
- Osprey fixes the sequence length at $4096$ tokens, which it says covers the dominant document length in FineWeb.[^bieOspreyTargetagnosticPretraining2026]
- Osprey tokenizes the corpus once with the draft's own tokenizer (Llama-3.2 for the LayerSkip-Llama draft, Qwen3-4B for the Qwen draft) and stores it as per-shard uint32 memory-mapped binaries with documents separated by a single EOS token. A multi-shard, infinite random-window sampler yields fixed-length $4096$-token training examples.[^bieOspreyTargetagnosticPretraining2026]

## Usage across papers

| Paper | Use | Setting | Numbers |
|---|---|---|---|
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | Stage 2 target-agnostic pretraining of the shallow NTP backbone (main run) | Qwen3-4B pruned to two layers; 32× H100; sequence length $4096$; peak learning rate $10^{-4}$, cosine schedule; effective batch $\approx 8.39$M tokens per step | $55$k steps, approximately $462$B tokens, $\approx 95$ h wall-clock, 3,040 H100-hours, 0 target forward passes[^bieOspreyTargetagnosticPretraining2026] |
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | Shorter Stage 2 checkpoint, for the pretraining-budget ablation | Same run, 10k-step checkpoint | $10$k steps, 84B tokens, $\approx 18$ h wall-clock, 576 H100-hours[^bieOspreyTargetagnosticPretraining2026] |
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | Ablation: drafter with and without Stage 2 FineWeb pretraining | Qwen3-8B target, same two-layer architecture and adaptation; chat, code, finance, and math (16 adaptation–evaluation pairs) | Overall AL $3.605$ without and $3.790$ with Stage 2 ($+0.185$); in-domain $4.306$ to $4.517$; OOD $3.371$ to $3.547$[^bieOspreyTargetagnosticPretraining2026] |
| [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) | Ablation: 10k-step against 55k-step pretraining checkpoint | Both adapted identically to Qwen3-8B with lr $10^{-5}$ | Overall AL $3.552$ (10k) and $3.578$ (55k), a difference of $0.026$; OOD/ID retention $0.799$ and $0.800$[^bieOspreyTargetagnosticPretraining2026] |

### Pretraining budget and break-even

Osprey reports that extending pretraining from $10$k to $55$k steps gives little extra benefit after target-specific adaptation. Held-out perplexity of the Qwen3-4B 2-layer drafter falls from $\sim$520 to a plateau near $37$ after approximately $10{,}000$ steps.[^bieOspreyTargetagnosticPretraining2026]

On MiniMax-M2.5, Osprey's $17.5\%$ throughput gain over EAGLE-3 (219.8 against 187.1 tokens/s) saves approximately $880$ H100 GPU-hours per billion generated tokens. At this rate the $55$k-step pretraining cost is recovered after approximately $3.5$ billion generated tokens, and the $10$k-step checkpoint breaks even after approximately $0.65$ billion tokens.[^bieOspreyTargetagnosticPretraining2026] The authors note that the upfront cost may not be recovered in low-traffic or one-off deployments.[^bieOspreyTargetagnosticPretraining2026]

## Known issues

- Osprey states the FineWeb pretraining budget three ways. Section 3.2 says five epochs over the 100B-token sample, "approximately 500B training tokens". Section 4 and Table 10 give $55$k steps, approximately $462$B tokens. Appendix C gives $60{,}000$ optimizer steps, $\approx 503$B tokens (about five passes over FineWeb sample-100BT).[^bieOspreyTargetagnosticPretraining2026]
- Wall-clock time also differs: Appendix C gives approximately $80$–$110$ wall-clock hours per pretraining run on 32 GPUs, and Table 10 gives $\approx 95$ h for the 55k-step run.[^bieOspreyTargetagnosticPretraining2026]
- Appendix C describes tokenizing FineWeb for a LayerSkip-Llama draft as well as the Qwen draft. Section 4 says target-agnostic pretraining is also applied to a four-layer LayerSkip Llama model used as a DFlash drafter, but Appendix G says that drafter's warm-start model is trained on Nemotron-Post-Training-Dataset-v2. The paper does not say whether the LayerSkip-Llama backbone saw FineWeb before that training.[^bieOspreyTargetagnosticPretraining2026]
- Most of Osprey's results come from single runs rather than multiple random seeds, so the authors advise caution with small differences,[^bieOspreyTargetagnosticPretraining2026] such as the $0.026$ AL gap between the 10k-step and 55k-step checkpoints.

## Related

- Papers: [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md)
- Methods: [Osprey](../methods/osprey.md), [Structured pruning](../methods/structured-pruning.md), [EAGLE-3](../methods/eagle-3.md) (the baseline Osprey is compared against), [DFlash](../methods/dflash.md)
- Datasets: [Open-PerfectBlend](perfectblend.md) (Osprey's adaptation data for Llama-3.3-70B-Instruct), [Nemotron Post-Training Dataset](nemotron-post-training.md) (Osprey's data for the DFlash warm-start model)
- [Drafter training data across papers](../analyses/drafter-training-data-across-papers.md)

[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
