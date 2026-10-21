---
type: Open Question
title: Does proactive drafting help when the drafter runs on a phone?
description: SpecEdge reports that proactive edge drafting lowers inter token latency on RTX 4090 edges, while HyCo finds that it lowers delivery speed on a phone NPU even as it raises server saving.
tags: [speculative-decoding, proactive-drafting, mobile-npu, mobile-specedge, edge-inference]
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

# Does proactive drafting help when the drafter runs on a phone?

## Question

[Proactive edge drafting](../methods/proactive-edge-drafting.md) uses the wait for the server's verification to draft ahead. Does that make the user's tokens arrive faster when the drafter runs on a phone NPU, or does it only help the server?

## Why it matters

My mobile SpecEdge setting drafts on a phone NPU and verifies on a server, and the phone is idle for most of each round (see [Can a block drafter pre-draft with stale target features?](pre-drafting-with-stale-target-features.md)). Proactive drafting is the obvious use of that idle time.

## Evidence so far

- **SpecEdge, RTX 4090 edges over WAN.** With the Qwen3 14B/1.7B pair, basic disaggregation reaches 32.76 tokens/s server throughput with higher latency, and adding proactive drafting reduces inter token latency to 28 ms.[^parkSpecEdgeScalableEdgeAssisted2025]
- **HyCo, Galaxy S26 Ultra NPU over LTE/5G.** On its SpecEdge-style tree (four Gemma 4 E2B passes, 32 nodes, exact verification), PD raises server saving against Cloud+MTP on Spec-Bench from 20.6% to 23.9% and MAT from 3.53 to 3.69, but lowers delivery from 16.1 to 12.1 tokens/s. On 32K summarization both save 2.9% (rounded) and PD lowers delivery from 10.0 to 8.2 tokens/s.[^baeHyCoHybridDrafting2026]
- HyCo concludes that neither more passes nor overlapping draft work is uniformly beneficial in its deployment.[^baeHyCoHybridDrafting2026]
- **HAT, Jetson over WiFi.** Parallel drafting (a top-k variant) lowers TBT from 38.3 to 33.8 ms on SpecBench with Vicuna-7B.[^xieNovelHatShapedDeviceCloud2025]

## Conflicting claims

SpecEdge's ablation finds proactive drafting lowers latency.[^parkSpecEdgeScalableEdgeAssisted2025] HyCo's phone runs find it lowers user-visible delivery speed.[^baeHyCoHybridDrafting2026] The settings differ in edge hardware (desktop GPU against phone NPU), network (WAN at 14.07 ms average RTT against cellular), models, metric (inter token latency against tokens from request start to last token), and implementation (SpecEdge's code against HyCo's SpecEdge-style re-implementation).[^parkSpecEdgeScalableEdgeAssisted2025][^baeHyCoHybridDrafting2026]

**Inference.** On a phone each SLM pass is expensive (HyCo's four-pass tree already delivers less than the SLM alone), so extra passes during the wait may delay the next round when alignment fails or when the reply arrives before drafting ends. Neither paper reports the alignment rate or how often proactive drafting overruns the wait.

## What would resolve it

On one phone and network, with one drafter: run with and without PD, and log per round the alignment rate, the proactive drafting time, the verification wait, and whether drafting overran the wait. Repeat for a one-pass block drafter, where the proactive draft is a single extra pass.

## Related

- [Proactive edge drafting](../methods/proactive-edge-drafting.md), [SpecEdge](../methods/specedge.md), [HyCo](../methods/hyco.md), [HAT](../methods/hat.md)
- [Can a block drafter pre-draft with stale target features?](pre-drafting-with-stale-target-features.md)
- [Does speculative decoding help on a mobile NPU?](speculative-decoding-on-mobile-npu.md)

[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
