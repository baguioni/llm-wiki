---
type: Method
title: Lossy acceptance rules
description: Verification rules for speculative decoding that accept drafted tokens the target would not necessarily sample, trading exact preservation of the target's output distribution for higher acceptance, such as HyCo's epsilon-threshold acceptance, Medusa's typical acceptance, and I-DLM's relaxed acceptance.
tags: [speculative-decoding, verification, lossy-acceptance, acceptance-rate]
sources:
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
---

# Lossy acceptance rules

## Overview

Exact verification in [speculative decoding](speculative-decoding.md) preserves the target LLM's sampling distribution. Lossy acceptance rules accept drafted tokens that the target would not necessarily sample, in order to raise acceptance within verification. HyCo groups them by what they test.[^baeHyCoHybridDrafting2026] HyCo and I-DLM are the papers in the wiki that measure one.

## How it works

### $\epsilon$-threshold acceptance (HyCo)

- A drafted child $c$ of node $v$ is accepted if it matches the verifier's sample or if $\tilde{p}(c\mid v)\geq\epsilon$. $\tilde{p}$ is the verifier's sampling distribution after temperature scaling and top-$k$/top-$p$ truncation, not the raw softmax. The fixed threshold follows $\epsilon$-sampling (Hewitt et al. 2022).[^baeHyCoHybridDrafting2026]
- The verifier selects the deepest accepted path and appends its own sample there as the bonus token. Among equally deep paths it prefers more verifier-sampled edges, then the highest product of $\tilde{p}$.[^baeHyCoHybridDrafting2026]
- Every accepted token is in the support of $\tilde{p}$, but the rule can commit tokens the verifier did not sample and changes their selection probabilities. It is therefore lossy. $\epsilon=1$ reduces it to exact verification, and with a one-hot greedy distribution it adds no token.[^baeHyCoHybridDrafting2026]

## Variants

As HyCo describes them:[^baeHyCoHybridDrafting2026]

| Rule | What it tests |
|---|---|
| BiLD (Kim et al. 2023) | Keeps a small model's tokens unless its distribution diverges from the large model's beyond a threshold |
| Fuzzy speculative decoding (Holsman et al. 2025), E2-SCI (Li et al. 2026b) | Accept within divergence thresholds of their own |
| Judge decoding (Bachmann et al. 2025) | A learned judge keeps tokens that exact verification rejects |
| Medusa typical acceptance | Tests the target's raw softmax against an entropy-adaptive threshold taken from $\eta$-sampling |
| HyCo $\epsilon$-threshold | Thresholds the verifier's own truncated sampling distribution $\tilde{p}$ |

I-DLM's relaxed acceptance multiplies the $p/q$ acceptance ratio by $(1+\tau)$; at $\tau=0$ decoding provably matches the AR distribution, and larger $\tau$ trades that guarantee for more tokens per forward without retraining.[^yuIntrospectiveDiffusionLanguage2026]

Synera, which keeps on the device the tokens whose confidence clears a threshold and offloads only the rest, skips verification for those tokens instead; HyCo also calls it lossy.[^baeHyCoHybridDrafting2026]

## Papers using it

### HyCo ([Bae et al. 2026](../papers/baeHyCoHybridDrafting2026.md))

- On HyCo's tree on UC-val at $\epsilon=0.005$, applying the threshold at every node instead of only at rejections lowers server GPU time per token from 5.62 to 5.10 ms at the same judge score of 60.0. [Medusa](medusa.md)'s typical acceptance at its defaults falls below the lossless judge-score range.[^baeHyCoHybridDrafting2026]
- On Spec-Bench, relaxing HyCo exact to $\epsilon=0.005$ raises MAT from 3.84 to 4.71 and server saving against Cloud+MTP from 27.7% to 38.6%. The same rule on an SLM-only tree (SpecEdge-$\epsilon$) gives 29.6% against 20.6% exact.[^baeHyCoHybridDrafting2026]
- Quality on Spec-Bench (GPT-5.4 judge, non-QA first turns): HyCo differs from Cloud+MTP by +0.2 points (95% CI −0.9 to +1.3) and from HyCo exact by −0.4 (−1.5 to +0.6). Translation is 2.6 points below SpecEdge-$\epsilon$ (−5.2 to −0.2).[^baeHyCoHybridDrafting2026]
- About two thirds of threshold-only accepted tokens come from the MTP chain, a tenth from runner-up siblings, and a quarter from the SLM.[^baeHyCoHybridDrafting2026]
- On the fixed logged trees of one run, $\epsilon=0.005$ gives MAT 4.364 against 4.366 if every drafted token in the support were accepted, so lowering $\epsilon$ further has little headroom.[^baeHyCoHybridDrafting2026]

### I-DLM ([Yu et al. 2026](../papers/yuIntrospectiveDiffusionLanguage2026.md))

Relaxed acceptance at stride $N=4$ on [I-DLM](i-dlm.md)-8B:[^yuIntrospectiveDiffusionLanguage2026]

| $\tau$ | 0 | 0.1 | 0.2 | 0.5 | 1 |
|---|---|---|---|---|---|
| HumanEval | 93.3 | 93.3 | 92.1 | 91.8 | 91.2 |
| Tokens per forward | 2.63 | 2.62 | 2.68 | 2.72 | 2.73 |

All rows: [^yuIntrospectiveDiffusionLanguage2026]

The paper reads the small TPF gain (2.63 → 2.73) as a sign that the proposals are already well aligned with the causal anchor.[^yuIntrospectiveDiffusionLanguage2026]

## Strengths & Limitations

- Raises acceptance without changing the drafter.[^baeHyCoHybridDrafting2026]
- HyCo cites Wang et al. (2026): an allowed set constrains which tokens can be accepted but does not preserve the verifier's relative preferences within that set. HyCo places its own rule in this category and states that its results characterize the trade-off on the evaluated tasks without removing the distributional risk.[^baeHyCoHybridDrafting2026]
- A judge-score interval that spans zero does not establish quality equivalence, and HyCo does not measure the effect on output diversity.[^baeHyCoHybridDrafting2026]

## Related

- [HyCo](hyco.md), [Medusa](medusa.md), [I-DLM](i-dlm.md), [Speculative decoding](speculative-decoding.md)
- [HyCo paper](../papers/baeHyCoHybridDrafting2026.md)

[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
