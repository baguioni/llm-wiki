---
type: Method
title: FR-Spec
description: Frequency-ranked draft vocabulary truncation that restricts a drafter's LM head to high-frequency tokens to cut LM-head latency, used by EAGLE-3 and adopted by HyCo for its phone NPU drafters.
tags: [speculative-decoding, draft-model, vocabulary, lm-head]
sources:
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# FR-Spec

The wiki has no FR-Spec paper page (Zhao et al. 2025). This page collects what other papers say about it and how they use truncated draft vocabularies.

## Overview

FR-Spec observed that the large token vocabularies of contemporary LLMs often make the latency of LM heads dominate the total latency of speculator heads, even in EAGLE. It truncates the draft vocabulary to a small subset of high-frequency tokens learned on training data.[^samarinLKLossesDirect2026]

## How it works

- The drafter's LM head predicts only over the kept subset, which sets a large subset of draft probabilities to zero.[^samarinLKLossesDirect2026]
- The target still verifies over its full vocabulary. In HyCo, tokens outside the keep set can still be sampled by the verifier as bonus tokens and are taken as input by both drafters, so the restriction costs only acceptance and exact verification stays lossless.[^baeHyCoHybridDrafting2026]

## Variants

| User | Draft vocabulary | Notes |
|---|---|---|
| [EAGLE-3](eagle-3.md) | truncated, as proposed in FR-Spec[^samarinLKLossesDirect2026] | Aurora gives draft vocabulary sizes of 32K vs 128K for Llama3 models and 32K vs 152K for Qwen3 models[^wangWhenRLMeets2026] |
| LK losses | truncated vocabularies from RedHatAI speculators (vocabulary definitions only)[^samarinLKLossesDirect2026] | |
| [HyCo](hyco.md) | 86,089-token keep set out of 262,144, shared by the MTP and SLM drafters[^baeHyCoHybridDrafting2026] | 24 special, 256 byte, all 4,678 Hangul tokens, and the 81,131 tokens most frequent in the assistant turns of 20,000 UltraChat train conversations[^baeHyCoHybridDrafting2026] |

## Papers using it

### LK losses (Samarin et al. 2026)

Truncation makes KL training ill-defined: KL divergence becomes infinite for tokens outside the draft vocabulary, so LK losses masks target logits outside the vocabulary and optimizes $\mathrm{KL}(\tilde{p}\|q)$ instead of $\mathrm{KL}(p\|q)$, "a proxy of a proxy". The LK losses themselves handle truncation naturally, since tokens outside the draft vocabulary contribute $\min(p_i,0)=0$ to the acceptance rate.[^samarinLKLossesDirect2026]

### Aurora (Wang et al. 2026)

Because draft vocabularies are much smaller than target vocabularies, Aurora transmits target logits over the draft vocabulary only, a $4\times$ to $5\times$ reduction.[^wangWhenRLMeets2026]

### HyCo ([Bae et al. 2026](../papers/baeHyCoHybridDrafting2026.md))

On a Galaxy S26 Ultra NPU, the drafters' full-vocabulary output layers and their top-$k$ search lengthen the phone's time per round from 52.9 to 77.9 ms. Keep-set selection on UC-val:[^baeHyCoHybridDrafting2026]

| Keep set | MAT | Server ms per output token | On-device ms per round |
|---|---|---|---|
| 21K | 2.98 | 7.00 | 45.7 |
| 45K | 3.25 | 6.44 | 47.8 |
| 86K (chosen) | 3.36 | 6.23 | 52.9 |
| 262K, full vocabulary | 2.85 | 7.57 | 77.9 |

All rows: [^baeHyCoHybridDrafting2026]

Tokens outside the 86K keep set are 3.0% of the verifier's bonus tokens on UC-val and 6.8% on a 150-question Spec-Bench subset.[^baeHyCoHybridDrafting2026]

## Strengths & Limitations

- Cuts LM-head cost. In HyCo, the full vocabulary has the lowest MAT (2.85) of the four sizes as well as the highest server cost.[^baeHyCoHybridDrafting2026]
- The drafter cannot propose tokens outside the kept set.[^baeHyCoHybridDrafting2026]
- A keep set derived from one dataset need not suit every language or domain.[^baeHyCoHybridDrafting2026]
- Complicates KL-based draft training.[^samarinLKLossesDirect2026]

## Related

- [EAGLE-3](eagle-3.md), [HyCo](hyco.md), [Speculative decoding](speculative-decoding.md)
- Papers: [LK losses](../papers/samarinLKLossesDirect2026.md), [Aurora](../papers/wangWhenRLMeets2026.md), [HyCo](../papers/baeHyCoHybridDrafting2026.md)
- [Can a block drafter be narrower than its target?](../questions/narrow-block-drafter.md)

[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^wangWhenRLMeets2026]: Wang et al. 2026
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
