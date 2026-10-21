---
type: Method
title: HyCo
description: Mobile-cloud speculative decoding that drafts a hybrid tree on the phone NPU, taking depth from the verifier's own MTP head (fed with state the server returns) and width from one pass of a small language model.
tags: [speculative-decoding, device-cloud-collaborative-inference, multi-token-prediction, tree-based-speculation, mobile-npu, mobile-specedge]
sources:
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# HyCo

## Overview

HyCo is a device-cloud [speculative decoding](speculative-decoding.md) design in which the mobile device builds a *hybrid draft tree* and the server's LLM (the verifier) checks it. The tree's depth comes from the verifier's native [MTP](multi-token-prediction.md) head, executed on the phone. Its width comes from one pass of a small language model (SLM). The aim is to spend less server GPU time per output token than server-side MTP self-speculation (Cloud+MTP) while delivering tokens at least as fast as the SLM alone on the device.[^baeHyCoHybridDrafting2026]

## How it works

1. **Hand-off.** With each verification the server returns what the MTP head reads: the input embedding of the root token, the last hidden state, and the keys and values of two verifier layers over a 1,024-token window. This is 5.6 KB per round plus 6.1 KB per output token at 8 bits. The server skips the head's $K$ sequential steps.[^baeHyCoHybridDrafting2026]
2. **MTP Drafter.** The head, 4-bit QAT on the phone NPU, drafts a top-1 chain of $K=4$ tokens and plants its second-ranked token as a runner-up sibling at depths 1–2.[^baeHyCoHybridDrafting2026]
3. **SLM Drafter.** One pass of Gemma 4 E2B proposes children under the root and every planted node.[^baeHyCoHybridDrafting2026]
4. **Scoring.** Each depth costs $\ln 0.66$, the log of the chain's measured per-depth acceptance rate. A sibling pays it twice on its own edge, and an SLM candidate adds its log-probability. The tree is trimmed to 32 nodes and sent as token IDs and parent indices (2.2 KB per round).[^baeHyCoHybridDrafting2026]
5. **Verification.** One forward pass with a tree attention mask. Exact verification is lossless. The default instead uses $\epsilon$-threshold acceptance with $\epsilon=0.005$, which is lossy (see [Lossy acceptance rules](lossy-acceptance.md)).[^baeHyCoHybridDrafting2026]

NPU fitting: integer graphs with 16-bit fixed-point activations, an 86,089-token keep set for both drafters' outputs ([FR-Spec](fr-spec.md)-style), and a 1,024-token context window.[^baeHyCoHybridDrafting2026]

## Variants

- **HyCo-2P** runs a second SLM pass over the nodes added by the first. It saves more server time (44.7% on Spec-Bench) but delivers fewer tokens per second (29.0 against 35.0).[^baeHyCoHybridDrafting2026]
- **HyCo exact** sets $\epsilon=1$: 27.7% server saving on Spec-Bench and 11.9% on 32K summarization.[^baeHyCoHybridDrafting2026]
- **Server head** keeps the MTP head on the server in BF16 (86K keep set, 1K window, no siblings) with one SLM pass and exact verification: 14.6% server saving, 36.1 tokens/s.[^baeHyCoHybridDrafting2026]

## Papers using it

### HyCo paper ([Bae et al. 2026](../papers/baeHyCoHybridDrafting2026.md))

Gemma 4 26B-A4B (AWQ 4-bit) on one RTX PRO 6000; drafters on a Galaxy S26 Ultra over LTE/5G; one client.[^baeHyCoHybridDrafting2026]

| Configuration | SB-480 $\Delta g$ vs. Cloud+MTP | SB-480 MAT | SB-480 Tok/s | 32K $\Delta g$ | 32K Tok/s |
|---|---|---|---|---|---|
| SpecEdge-style (exact) | −20.6% | 3.53 | 16.1 | −2.9% | 10.0 |
| SpecEdge-$\epsilon$ | −29.6 ± 0.2% | 4.13 | 18.9 ± 0.1 | −15.7% | 12.4 |
| HyCo | −38.6 ± 0.2% | 4.71 | 35.0 ± 0.7 | −29.2% | 21.0 |
| HyCo exact | −27.7% | 3.84 | 28.2 | −11.9% | 16.8 |

All rows: [^baeHyCoHybridDrafting2026]

The SLM alone (on-device, 8K context, greedy) delivers 26.4 tokens/s on Spec-Bench.[^baeHyCoHybridDrafting2026]

## Strengths & Limitations

- Depth no longer needs extra SLM passes: MAT 4.71 with one SLM pass against 4.13 for an SLM-only tree with four, under the same acceptance rule.[^baeHyCoHybridDrafting2026]
- The SLM half carries over to another model family without retraining through a token bridge (Muse-Glimmer-30B, Appendix H).[^baeHyCoHybridDrafting2026]
- Needs access to the verifier's native head, hidden states, and KV entries, and a head the phone can run. The MTP Drafter adds about 20 ms per mobile round and 365 MB of storage.[^baeHyCoHybridDrafting2026]
- The default acceptance rule is lossy. Translation quality falls below SpecEdge-$\epsilon$ in an exploratory comparison.[^baeHyCoHybridDrafting2026]
- Measured with one client, one phone, and one network; no energy or loaded-service capacity.[^baeHyCoHybridDrafting2026]

## Related

- Paper: [HyCo](../papers/baeHyCoHybridDrafting2026.md)
- Builds on: [Multi-Token Prediction (MTP)](multi-token-prediction.md), [SpecEdge](specedge.md), [Tree-based speculation](tree-based-speculation.md), [SpecInfer](specinfer.md)
- Components: [Lossy acceptance rules](lossy-acceptance.md), [FR-Spec](fr-spec.md)
- Other device-cloud drafting: [HAT](hat.md), [Proactive edge drafting](proactive-edge-drafting.md)
- Result: [HyCo cuts server GPU time per token by 38.6% against server-side MTP on Spec-Bench](../results/hyco-server-gpu-time-vs-cloud-mtp.md)
- [Quantization of the target and the draft in speculative decoding](../analyses/quantization-in-speculative-decoding.md) (the MTP head's 4-bit QAT against 8-bit and BF16)

[^baeHyCoHybridDrafting2026]: Bae et al. 2026
