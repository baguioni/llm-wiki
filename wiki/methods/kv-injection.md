---
type: Method
title: KV injection
description: Conditioning mechanism from DFlash that injects fused target-model hidden features into the Key and Value projections of every draft layer instead of feeding them only as drafter inputs.
tags: [speculative-decoding, drafter-conditioning, kv-cache, parallel-drafting]
sources:
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
---

# KV injection

## Overview

KV injection is the mechanism that [DFlash](../methods/dflash.md) uses to condition its drafter on the target model in [speculative decoding](../methods/speculative-decoding.md). The fused target context feature is treated as persistent contextual information and injected into the Key and Value projections of every draft model layer.[^chenDFlashBlockDiffusion2026] The DSpark paper describes DFlash as a parallel drafter that conditions its draft model on rich context features extracted from the target model, and names this KV injection.[^chengDSparkConfidenceScheduledSpeculative2026]

## How it works

- **Feature extraction.** During the prefill pass, hidden states are extracted from a fixed set of target layers uniformly sampled from shallow to deep, concatenated, and passed through a lightweight projection layer.[^chenDFlashBlockDiffusion2026]
- **Projection.** $\mathbf{H}_{t}=\mathrm{RMSNorm}\left(W_{c}[\mathbf{H}^{(l_{1})};\ldots;\mathbf{H}^{(l_{5})}]\right)$. The projected target features are shared by all draft layers.[^chenDFlashBlockDiffusion2026]
- **Injection.** At layer $i$ the draft tokens produce the queries, and both target features and draft tokens are projected into keys and values: $\mathbf{K}_{i}=[W_{i}^{K}\mathbf{H}_{t};\,W_{i}^{K}\mathbf{H}_{d}]_{\mathrm{seq}}$, $\mathbf{V}_{i}=[W_{i}^{V}\mathbf{H}_{t};\,W_{i}^{V}\mathbf{H}_{d}]_{\mathrm{seq}}$. Target features serve only as additional KV entries for the masked-block draft tokens.[^chenDFlashBlockDiffusion2026]
- **Caching.** The projected features are stored in the draft model's [KV cache](../methods/kv-cache.md) and reused across drafting iterations.[^chenDFlashBlockDiffusion2026]
- **Training.** The entire clean sequence is passed through the target model to extract and fuse the hidden features for all tokens, which are then injected into the draft model as Key and Value projections.[^chenDFlashBlockDiffusion2026]

The DSpark paper writes the same mechanism with $m$ target layers: $H_{\text{ctx}}=\mathrm{RMSNorm}\bigl(W_{c}\,[H^{(l_{1})};\,\ldots;\,H^{(l_{m})}]\bigr)$ with a shared projection $W_{c}\in\mathbb{R}^{d\times md}$, and $K_{i}=[W_{i}^{K}H_{\text{ctx}};\;W_{i}^{K}H_{d}]$, $V_{i}=[W_{i}^{V}H_{\text{ctx}};\;W_{i}^{V}H_{d}]$. All positions within a block attend bidirectionally to each other and to the injected target context.[^chengDSparkConfidenceScheduledSpeculative2026]

## Variants

- **Input fusion.** [EAGLE-3](../methods/eagle-3.md) fuses target features with the draft model's token embeddings and feeds them only as inputs to the draft model. DFlash uses this as the contrast case.[^chenDFlashBlockDiffusion2026]
- **Number of target features.** The original paper compares 3 and 5 target hidden features with a 3-layer drafter at block size 16.[^chenDFlashBlockDiffusion2026]

## Papers using it

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md)

KV injection against input fusion, Qwen3-4B, 5-layer draft models, draft block size 8. Each cell is $\tau$ / speedup.[^chenDFlashBlockDiffusion2026]

| Drafting | Variant | Injection | [GSM8K](../datasets/gsm8k.md) | [HumanEval](../datasets/humaneval.md) | [MT-Bench](../datasets/mt-bench.md) |
|---|---|---|---|---|---|
| Autoregressive | EAGLE-3-5L | Input | 4.2 / 2.1× | 4.3 / 2.2× | 3.1 / 1.4× |
| Autoregressive | DFlash-AR | KV | 4.8 / 2.4× | 4.6 / 2.3× | 3.4 / 1.5× |
| Block diffusion | DFlash | Input | 3.5 / 2.9× | 3.5 / 2.9× | 2.6 / 2.0× |
| Block diffusion | DFlash | KV | 4.2 / 3.3× | 4.0 / 3.2× | 3.0 / 2.2× |

All rows: [^chenDFlashBlockDiffusion2026]

Number of target hidden features, 3 draft layers, block size 16, greedy decoding. Each cell is speedup / $\tau$.[^chenDFlashBlockDiffusion2026]

| Features | Math500 | HumanEval | MT-Bench |
|---|---|---|---|
| 3-H | 4.49× / 5.38 | 3.80× / 4.47 | 2.32× / 3.07 |
| 5-H | 4.69× / 5.64 | 3.90× / 4.61 | 2.38× / 3.18 |

All rows: [^chenDFlashBlockDiffusion2026]

A 5-layer block diffusion drafter without any conditioning from the target model gives speedups the paper calls modest, typically around 2–3×. On GSM8K it reaches 2.83 speedup with $\tau$ 3.38 at temperature 0.[^chenDFlashBlockDiffusion2026]

### [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md)

[DSpark](../methods/dspark.md) uses DFlash as its parallel backbone with only a minor modification to the anchor position, and all drafters in its comparison use the same target-model feature layers.[^chengDSparkConfidenceScheduledSpeculative2026]

## Strengths & Limitations

- With input fusion, the information from the target model becomes more diluted as draft depth increases, which gives diminishing gains in acceptance length from added draft layers. KV injection gives consistent conditioning throughout the draft model, so acceptance length scales with the number of draft layers.[^chenDFlashBlockDiffusion2026]
- KV injection gives higher acceptance length than input fusion on all three tasks of the ablation, for both autoregressive and block diffusion drafting.[^chenDFlashBlockDiffusion2026]
- Memory overhead is small. The only extra parameterized component is the shared projection $W_{c}\in\mathbb{R}^{D\times 5D}$. For Qwen3.5-35B-A3B with $D=2048$ and BF16 weights this adds about 42 MB.[^chenDFlashBlockDiffusion2026]
- Using more target hidden features raises training cost: in offline training the storage for cached target hidden states grows linearly with the number of extracted features.[^chenDFlashBlockDiffusion2026]

## Related

- [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [EAGLE-3](../methods/eagle-3.md), [KV cache](../methods/kv-cache.md), [Speculative decoding](../methods/speculative-decoding.md)

[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
