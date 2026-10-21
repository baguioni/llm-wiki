---
type: Dataset
title: InfiniteBench
description: Long-context evaluation suite beyond 100K tokens whose English novel summarization task (En.Sum, written ∞Bench Sum) HyCo uses, truncated to 32K tokens, as its long-input speculative-decoding workload.
tags: [long-context, summarization, benchmark, speculative-decoding]
sources:
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# InfiniteBench

## Overview

InfiniteBench ($\infty$Bench, Zhang et al. 2024) extends long-context evaluation beyond 100K tokens. HyCo uses its English summarization task, En.Sum, which it writes as $\infty$Bench Sum. Its license is MIT.[^baeHyCoHybridDrafting2026]

## Composition

- HyCo evaluates the first 50 English novels in HELMET's seed-42 order, truncated to 32K tokens with HELMET's preprocessing and its 2-shot prompt. The prompts have a median of 30.6K Gemma tokens.[^baeHyCoHybridDrafting2026]
- Each novel has an expert summary, against which HELMET's model-based metrics score key-point recall and precision.[^baeHyCoHybridDrafting2026]

## Usage across papers

### HyCo ([Bae et al. 2026](../papers/baeHyCoHybridDrafting2026.md))

Gemma 4 26B-A4B verifier, drafters on a Galaxy S26 Ultra, 1,200-token output cap, answers sampled rather than greedily decoded as in HELMET. Metrics are server GPU time per output token ($\Delta g$ against server-side MTP self-speculation, whose $g$ is 23.91 ms), MAT, delivery speed, ROUGE-L-Sum, and HELMET's fluency-weighted F1, recall, and precision with GPT-5.4.[^baeHyCoHybridDrafting2026]

| Configuration | $\Delta g$ (%) | MAT | Tok/s | HELMET F1 |
|---|---|---|---|---|
| Cloud+MTP | 0.0 | 2.37 | – | 29.6 |
| SpecEdge-style | −2.9 | 2.52 | 10.0 | 31.3 |
| SpecEdge-style + PD | −2.9 | 2.52 | 8.2 | 29.1 |
| SpecEdge-$\epsilon$ | −15.7 | 3.08 | 12.4 | 28.5 |
| HyCo | −29.2 | 3.73 | 21.0 | 30.0 |
| HyCo-2P | −31.9 | 3.95 | 18.8 | 28.0 |
| HyCo exact | −11.9 | 2.81 | 16.8 | 29.7 |
| HyCo server head | −3.8 | 2.70 | 19.8 | 29.0 |

All rows: [^baeHyCoHybridDrafting2026]

- HyCo's ROUGE-L-Sum is 37.5 against 38.5 for Cloud+MTP, a difference of −1.0 (95% CI −2.1 to +0.1).[^baeHyCoHybridDrafting2026]
- On this workload, prefill, which drafting does not shorten, accounts for about a fifth of $g$, so a second SLM pass adds only 2.7 percentage points of server saving.[^baeHyCoHybridDrafting2026]
- HyCo's mean time to first token is 4.60 s on these 32K inputs, against 846 ms on Spec-Bench.[^baeHyCoHybridDrafting2026]

## Known issues

- HELMET precision tests support in the expert summary, not factual verification against the whole novel.[^baeHyCoHybridDrafting2026]
- The SpecEdge-style + PD run completed 49 of 50 requests.[^baeHyCoHybridDrafting2026]
- One generation and one metric evaluation per configuration.[^baeHyCoHybridDrafting2026]

## Related

- [HyCo](../methods/hyco.md), [Spec-Bench](../benchmarks/spec-bench.md), [CNN/Daily Mail](cnn-dailymail.md) (short-input summarization)

[^baeHyCoHybridDrafting2026]: Bae et al. 2026
