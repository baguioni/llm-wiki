---
type: Method
title: Proactive edge drafting
description: Continuing to draft on the edge device while the server verifies the previous draft, and reusing that work when the verified path matches, introduced by SpecEdge and re-measured on a phone NPU by HyCo.
tags: [speculative-decoding, edge-inference, parallel-drafting, proactive-drafting, mobile-specedge]
sources:
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: "A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models"
---

# Proactive edge drafting

## Overview

In device-server speculative decoding the edge device would otherwise sit idle while the server verifies. Proactive edge drafting uses that time to draft further tokens, which are kept only if the verification result lands on the path they extend.[^parkSpecEdgeScalableEdgeAssisted2025] HyCo abbreviates it as PD.[^baeHyCoHybridDrafting2026]

## How it works

- After sending $n$ candidate tokens, the edge keeps drafting without waiting for the verification result.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Single expansion head.** SpecEdge picks the single path with the highest cumulative log probability and continues drafting only from that node. Treating every leaf as an expansion head yields negligible gains.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Complete draft alignment.** If the server's accepted tokens and additional token match a path in the proactive tree, the branch is kept and drafting continues from the advanced position. Otherwise the proactive work is discarded and the tree is rebuilt.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Expected gain.** $\mathbb{E}(\text{Gain})=P_{\text{align}}\cdot P_{\text{match | align}}\cdot\left(\frac{T_{\text{draft}}}{H_{\text{expan}}}-1\right)$.[^parkSpecEdgeScalableEdgeAssisted2025]

## Variants

- **HAT parallel drafting.** HAT drafts a continuation from each top-k token of its last (low-confidence) draft step during verification and reuses the one that matches the cloud's corrected token. The cloud sets the number of pre-draft steps so drafting ends before the result arrives.[^xieNovelHatShapedDeviceCloud2025]

## Papers using it

| Paper | Edge hardware | Without PD | With PD |
|---|---|---|---|
| [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md), Qwen3 14B/1.7B | RTX 4090 over WAN | basic disaggregation: 32.76 tokens/s throughput, higher latency | inter token latency 28 ms[^parkSpecEdgeScalableEdgeAssisted2025] |
| [HyCo](../papers/baeHyCoHybridDrafting2026.md), SpecEdge-style tree, Spec-Bench | Galaxy S26 Ultra NPU over LTE/5G | 20.6% server saving, MAT 3.53, 16.1 tokens/s | 23.9% server saving, MAT 3.69, 12.1 tokens/s[^baeHyCoHybridDrafting2026] |
| [HyCo](../papers/baeHyCoHybridDrafting2026.md), SpecEdge-style tree, $\infty$Bench Sum 32K | Galaxy S26 Ultra NPU over LTE/5G | 2.9% server saving, 10.0 tokens/s | 2.9% (rounded), 8.2 tokens/s[^baeHyCoHybridDrafting2026] |
| [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md), Vicuna-7B, SpecBench | Jetson over WiFi | TBT 38.3 ms (+SD) | TBT 33.8 ms (+SD+parallel drafting)[^xieNovelHatShapedDeviceCloud2025] |

## Strengths & Limitations

- SpecEdge states that proactive drafting masks network and verification latency with local computation.[^parkSpecEdgeScalableEdgeAssisted2025]
- HyCo finds that PD raises server saving but lowers delivery speed on the phone, and concludes that overlapping draft work is not uniformly beneficial in its deployment.[^baeHyCoHybridDrafting2026]
- When alignment fails, the proactive work is wasted.[^parkSpecEdgeScalableEdgeAssisted2025]
- For PD, HyCo's mobile draft time per token excludes drafting overlapped with the verification wait, so it is not PD's total active compute.[^baeHyCoHybridDrafting2026]

# Contradictions

SpecEdge reports that adding proactive drafting to basic disaggregation reduces inter token latency (to 28 ms with Qwen3 14B/1.7B on RTX 4090 edges).[^parkSpecEdgeScalableEdgeAssisted2025] HyCo's re-implementation on a phone NPU finds the opposite effect on user-visible speed: delivery falls from 16.1 to 12.1 tokens/s on Spec-Bench and from 10.0 to 8.2 on 32K summarization, while server saving rises.[^baeHyCoHybridDrafting2026] The edge hardware, network, models, and metric (inter token latency against delivery speed from request start to last token) all differ, and HyCo's SpecEdge-style tree is a re-implementation, not SpecEdge's code. See [Does proactive drafting help when the drafter runs on a phone?](../questions/proactive-drafting-on-a-phone.md).

## Related

- [SpecEdge](specedge.md), [HyCo](hyco.md), [HAT](hat.md)
- [Speculative Speculative Decoding (SSD)](speculative-speculative-decoding.md), [PEARL](pearl.md) (drafting in parallel with verification on servers)
- [Can a block drafter pre-draft with stale target features?](../questions/pre-drafting-with-stale-target-features.md)
- [Does proactive drafting help when the drafter runs on a phone?](../questions/proactive-drafting-on-a-phone.md)

[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
