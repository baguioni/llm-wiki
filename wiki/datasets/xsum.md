---
type: Dataset
title: XSum
description: Extreme Summarization dataset of BBC news articles, used in the wiki's papers to measure speculative decoding speedup and ROUGE-2.
tags: [dataset, summarization, speculative-decoding, evaluation]
sources:
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
---

# XSum

## Overview

The Extreme Summarization (XSum) dataset is an evaluation benchmark for abstractive single-document summarization systems.[^zhouDistillSpecImprovingSpeculative2024] In the wiki it is used by two [speculative decoding](../methods/speculative-decoding.md) papers: one studies draft model distillation on it,[^zhouDistillSpecImprovingSpeculative2024] and one uses it to compare a pruned draft model against self-speculative decoding.[^yanDecodingSpeculativeDecoding2025]

## Composition

- 226,711 news articles, sourced from BBC articles spanning the years 2010 to 2017.[^zhouDistillSpecImprovingSpeculative2024]
- The articles cover domains including News, Politics, Sports, Weather, Business, Technology, Science, Health, Family, Education, Entertainment, and Arts.[^zhouDistillSpecImprovingSpeculative2024]
- Split sizes are not stated in the wiki's papers.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Zhou et al. 2024](../papers/zhouDistillSpecImprovingSpeculative2024.md) | Block efficiency, speedup, and ROUGE-2 of [DistillSpec](../methods/distillspec.md); distillation recipe study | T5-XL (3B) target, T5-Small (77M) draft; T5 model garden | See the quality and speed tables[^zhouDistillSpecImprovingSpeculative2024] |
| [Yan et al. 2025](../papers/yanDecodingSpeculativeDecoding2025.md) | Comparison against self-speculative decoding | LLaMa-2-70B target, greedy sampling | See the speed table[^yanDecodingSpeculativeDecoding2025] |

### Protocols

- Zhou et al. evaluate summarization with ROUGE scores on the validation split, primarily ROUGE-2, and use a maximum input length of 1,024 and a maximum output length of 64 for distillation and evaluation.[^zhouDistillSpecImprovingSpeculative2024] For latency they sample 500 examples from the test or validation set and measure wall-clock decoding time at batch size 1.[^zhouDistillSpecImprovingSpeculative2024]
- Yan et al. pick the setting where self-speculative decoding achieves its highest speedup: LLaMa-2-70B as target model with greedy sampling on [CNNDM](cnn-dailymail.md) and XSum.[^yanDecodingSpeculativeDecoding2025]

### Task quality: ROUGE-2

Zhou et al. compare four pipelines over five T5 sizes (T5-Small 77M to T5-XXL 11B) and report the two end points of the DistillSpec trade-off on XSum. The text does not name which model sizes the two end points use.[^zhouDistillSpecImprovingSpeculative2024]

| Model | Setting | Rouge2 | Reported by |
|---|---|---|---|
| T5 model garden | end point at relative latency 17.3 | 23.1 | [^zhouDistillSpecImprovingSpeculative2024] |
| T5 model garden, DistillSpec | end point at relative latency 2.7 | 23.0 | [^zhouDistillSpecImprovingSpeculative2024] |

Other ROUGE-2 results on XSum (draft model task performance over training, improvement by divergence function) are given only in figures.[^zhouDistillSpecImprovingSpeculative2024]

### Speed: DistillSpec

Target T5-XL (3B), draft T5-Small (77M). $\gamma$ is the block size, $\tau$ is block efficiency, and Method is the distillation method used.[^zhouDistillSpecImprovingSpeculative2024]

| Target / draft | Setting | $\tau$ w/o distill. | Speedup w/o distill. | $\tau$ with distill. | Speedup with distill. | $\Delta$ | Method | Reported by |
|---|---|---|---|---|---|---|---|---|
| T5-XL / T5-Small | T=0, $\gamma$=3 | 2.31 | 1.44$\times$ | 2.62 | 1.58$\times$ | +0.14$\times$ | $f$-Distill | [^zhouDistillSpecImprovingSpeculative2024] |
| T5-XL / T5-Small | T=0, $\gamma$=5 | 2.57 | 1.43$\times$ | 3.08 | 1.62$\times$ | +0.19$\times$ | $f$-Distill | [^zhouDistillSpecImprovingSpeculative2024] |
| T5-XL / T5-Small | T=0, $\gamma$=7 | 2.68 | 1.36$\times$ | 3.31 | 1.57$\times$ | +0.21$\times$ | $f$-Distill | [^zhouDistillSpecImprovingSpeculative2024] |
| T5-XL / T5-Small | T=1, $\gamma$=3 | 2.19 | 1.40$\times$ | 2.58 | 1.57$\times$ | +0.17$\times$ | $f$-Distill | [^zhouDistillSpecImprovingSpeculative2024] |
| T5-XL / T5-Small | T=1, $\gamma$=5 | 2.39 | 1.37$\times$ | 3.01 | 1.61$\times$ | +0.25$\times$ | $f$-Distill | [^zhouDistillSpecImprovingSpeculative2024] |
| T5-XL / T5-Small | T=1, $\gamma$=7 | 2.47 | 1.28$\times$ | 3.21 | 1.55$\times$ | +0.27$\times$ | $f$-Distill | [^zhouDistillSpecImprovingSpeculative2024] |

The $\Delta$ for T=1, $\gamma$=5 is printed as +0.25$\times$, while the two speedup columns as printed differ by 0.24$\times$. The values are copied as the source gives them.[^zhouDistillSpecImprovingSpeculative2024]

Quality-latency trade-off with the T5 model garden:[^zhouDistillSpecImprovingSpeculative2024]

| Model | Setting | Relative latency | Speedup improvement | Reported by |
|---|---|---|---|---|
| T5 model garden, DistillSpec | XSum | from 17.3 to 2.7 | 6.4$\times$ | [^zhouDistillSpecImprovingSpeculative2024] |

- On XSum with greedy decoding, distilling on data generated from both the draft and the target leads to the best block efficiency, with JSD slightly outperforming the other divergences.[^zhouDistillSpecImprovingSpeculative2024]
- GKD achieves the best wall-time performance improvement on XSum.[^zhouDistillSpecImprovingSpeculative2024]
- A high sampling temperature for generating distillation data is needed for the best acceptance rate in XSum decoding, for both draft-generated and target-generated data.[^zhouDistillSpecImprovingSpeculative2024]
- Supervised KD exhibits declining acceptance rates after $\sim$40k training steps on XSum and CNNDM.[^zhouDistillSpecImprovingSpeculative2024]

### Speed: wide-and-shallow draft vs self-speculative decoding

LLaMa-2-70B target, greedy sampling. The source gives the speedup as a percentage.[^yanDecodingSpeculativeDecoding2025]

| Target model | Strategy | Setting | Speedup | Reported by |
|---|---|---|---|---|
| LLaMa-2-70B | Self-Speculative | greedy | 60% | [^yanDecodingSpeculativeDecoding2025] |
| LLaMa-2-70B | NoFT-Wide-796M draft | greedy | 145% | [^yanDecodingSpeculativeDecoding2025] |

## Known issues

- The two papers' speed rows are not comparable: Zhou et al. use T5 models and print a speedup ratio,[^zhouDistillSpecImprovingSpeculative2024] and Yan et al. use LLaMa models and print a percentage.[^yanDecodingSpeculativeDecoding2025]

## Related

- Datasets: [CNN/Daily Mail](cnn-dailymail.md), [GSM8K](gsm8k.md)
- Methods: [Speculative decoding](../methods/speculative-decoding.md), [DistillSpec](../methods/distillspec.md), [Knowledge distillation](../methods/knowledge-distillation.md)

[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
