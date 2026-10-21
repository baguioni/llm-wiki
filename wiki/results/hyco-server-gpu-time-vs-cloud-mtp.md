---
type: Result
title: HyCo cuts server GPU time per token by 38.6% against server-side MTP on Spec-Bench
description: Drafting on a Galaxy S26 Ultra NPU with the verifier's own MTP head plus one SLM pass, HyCo needs 38.6% less server GPU time per output token than server-side MTP self-speculation on Spec-Bench (27.7% with exact verification) while delivering 35.0 tokens/s.
tags: [speculative-decoding, multi-token-prediction, mobile-npu, mobile-specedge, server-cost]
sources:
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
---

# HyCo cuts server GPU time per token by 38.6% against server-side MTP on Spec-Bench

## Claim

Moving the verifier's MTP head to the phone and adding one SLM pass for alternative branches reduces server GPU time per output token against server-side MTP self-speculation (Cloud+MTP) by 38.6 ± 0.2% on Spec-Bench and 29.2% on 32K-token summarization.[^baeHyCoHybridDrafting2026]

## Conditions

- Verifier: Gemma 4 26B-A4B, 4-bit AWQ, on one RTX PRO 6000, sampling at temperature 1, top-$k$ 64, top-$p$ 0.95, in SpecEdge's verification server.[^baeHyCoHybridDrafting2026]
- Device: Galaxy S26 Ultra (SM8850, Hexagon Tensor Processor v81) over commercial LTE/5G. MTP head at W4 QAT, SLM Drafter Gemma 4 E2B from Google's QAT checkpoint, 86K keep set, 1,024-token window, 32-node tree.[^baeHyCoHybridDrafting2026]
- Default acceptance is $\epsilon$-threshold with $\epsilon=0.005$, which is lossy; HyCo exact uses exact verification.[^baeHyCoHybridDrafting2026]
- SB-480 (all 480 Spec-Bench questions, 1,024-token cap) and the first 50 novels of $\infty$Bench Sum at 32K (1,200-token cap). One client at a time. $g$ includes prefill.[^baeHyCoHybridDrafting2026]

## Numbers

| Configuration | SB-480 $\Delta g$ | SB-480 Tok/s | 32K $\Delta g$ | 32K Tok/s |
|---|---|---|---|---|
| HyCo ($\epsilon$) | −38.6 ± 0.2% | 35.0 ± 0.7 | −29.2% | 21.0 |
| HyCo exact | −27.7% | 28.2 | −11.9% | 16.8 |
| SpecEdge-$\epsilon$ (SLM-only tree, same rule) | −29.6 ± 0.2% | 18.9 ± 0.1 | −15.7% | 12.4 |
| SpecEdge-style (exact) | −20.6% | 16.1 | −2.9% | 10.0 |

All rows: [^baeHyCoHybridDrafting2026]

Reference $g$ for Cloud+MTP is 7.81 ms per token on SB-480 and 23.91 ms on 32K. HyCo's $g$ is 4.80 and 16.92 ms.[^baeHyCoHybridDrafting2026]

## Comparisons

- **Against the SLM alone.** On Spec-Bench, HyCo delivers 35.0 tokens/s against 26.4 for the SLM running alone on the phone, at 12.1 against 36.8 ms of mobile draft time per output token.[^baeHyCoHybridDrafting2026]
- **Quality.** The GPT-5.4 judge score of HyCo differs from Cloud+MTP by +0.2 points (95% CI −0.9 to +1.3) on 398 non-QA first-turn questions. The paper does not claim equivalence.[^baeHyCoHybridDrafting2026]
- **Where the saving comes from.** Moving the head off the server alone shortens the server's median round from 26.8 to 21.7 ms and lowers $g$ by 15.2% on UC-val.[^baeHyCoHybridDrafting2026]
- **My drafter evaluation.** In [my phone-drafts, server-verifies evaluation](../experiments/drafter-evaluation-qwen3-14b.md), the per-level autoregressive drafters (Qwen3-0.6B, EAGLE-3) were the slowest, at 17.6–18.5 tok/s with their best trees against 26.7–30.0 for the one-decode block drafters.[^drafter-evaluation] HyCo's finding that a four-pass SLM tree on the phone is slower than the SLM alone points the same way.[^baeHyCoHybridDrafting2026] The setups differ (Qwen3-14B at temperature 0 on a DGX Spark against Gemma 4 26B-A4B at temperature 1 on an RTX PRO 6000), and the metrics differ (tok/s against server GPU time), so the numbers are not comparable. See [Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU](block-drafters-vs-ar-drafters-on-phone-npu.md).

## Related

- [HyCo paper](../papers/baeHyCoHybridDrafting2026.md), [HyCo](../methods/hyco.md)
- [Multi-Token Prediction (MTP)](../methods/multi-token-prediction.md), [SpecEdge](../methods/specedge.md), [Lossy acceptance rules](../methods/lossy-acceptance.md)
- [Spec-Bench](../benchmarks/spec-bench.md), [InfiniteBench](../datasets/infinitebench.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)

[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
