---
type: Method
title: SpecEdge
description: Edge-assisted serving framework that drafts on edge GPUs and verifies on a server GPU, exchanging only tokens, with proactive edge drafting and pipeline-aware server scheduling; also the base engine and SLM-only baseline of HyCo.
tags: [speculative-decoding, edge-inference, llm-serving, tree-based-speculation, mobile-specedge]
sources:
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# SpecEdge

## Overview

SpecEdge splits [speculative decoding](speculative-decoding.md) into edge drafting and server verification, and exchanges only token outputs over the network. The server's output distribution is preserved exactly.[^parkSpecEdgeScalableEdgeAssisted2025]

## How it works

- **Disaggregated decoding.** The edge GPU drafts candidate tokens and sends them to the server, which verifies them in one forward pass and returns the verified tokens and one additional token.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Tree drafting.** Initial drafting uses tree-based drafting from [SpecExec](specexec.md); the evaluation's tree construction follows [Sequoia](sequoia.md) and SpecExec with a draft tree size of 32 per request.[^parkSpecEdgeScalableEdgeAssisted2025]
- **[Proactive edge drafting](proactive-edge-drafting.md).** After sending the tree, the edge keeps drafting from the single path with the highest cumulative log probability and reuses that work only on complete draft alignment.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Pipeline-aware scheduling.** The server verifies completed drafts of one set of requests while other requests draft on their own edge devices. Draft depth is calibrated so that server verification time ≈ edge drafting time + network round-trip time.[^parkSpecEdgeScalableEdgeAssisted2025]

## Variants

- **SpecEdge-style (in HyCo).** HyCo's SLM-only baseline drafts a 32-node tree in four sequential SLM passes on a phone NPU, with a 1K-token mobile prefill bound and exact verification. "+ PD" adds proactive drafting. **SpecEdge-$\epsilon$** keeps this construction but uses HyCo's $\epsilon$-threshold acceptance.[^baeHyCoHybridDrafting2026]

## Papers using it

### SpecEdge paper ([Park et al. 2025](../papers/parkSpecEdgeScalableEdgeAssisted2025.md))

Server-side A100 and edge-side RTX 4090 GPUs over a wide-area network (14.07 ms average RTT). Against a server-only tree speculative decoding baseline, SpecEdge reports 1.91× better cost efficiency through a 2.22× throughput gain on average, and an 11.24% average reduction in inter token latency.[^parkSpecEdgeScalableEdgeAssisted2025] Per-task numbers are on the paper page and on [Spec-Bench](../benchmarks/spec-bench.md).

### HyCo ([Bae et al. 2026](../papers/baeHyCoHybridDrafting2026.md))

All HyCo configurations use SpecEdge's verification server, extended with Gemma 4 26B-A4B and its MTP head. SpecEdge-style is a baseline on a Galaxy S26 Ultra NPU with Gemma 4 E2B drafting. On Spec-Bench it cuts server GPU time per output token by 20.6% against server-side MTP self-speculation, reaches MAT 3.53, and delivers 16.1 tokens/s. That is slower than the SLM alone on the phone (26.4 tokens/s), because of its four mobile SLM passes.[^baeHyCoHybridDrafting2026]

| Configuration | SB-480 $\Delta g$ | MAT | Tok/s | Draft ms/token |
|---|---|---|---|---|
| SpecEdge-style | −20.6% | 3.53 | 16.1 | 42.8 |
| SpecEdge-style + PD | −23.9% | 3.69 | 12.1 | 40.1 |
| SpecEdge-$\epsilon$ | −29.6 ± 0.2% | 4.13 | 18.9 ± 0.1 | 37.0 |

All rows: [^baeHyCoHybridDrafting2026]

## Strengths & Limitations

- Offloading drafting reduces server runtime by approximately 40-50% in all of the SpecEdge paper's model configurations.[^parkSpecEdgeScalableEdgeAssisted2025]
- The latency advantage over server-only holds below 50 ms RTT.[^parkSpecEdgeScalableEdgeAssisted2025]
- On a phone NPU, one SLM pass per tree level is the bottleneck: HyCo reports that the four-level tree leaves the user slower than the SLM alone.[^baeHyCoHybridDrafting2026]
- The SpecEdge server permits research and evaluation but needs a separate license for commercial deployment.[^baeHyCoHybridDrafting2026]

## Related

- Papers: [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md), [HyCo](../papers/baeHyCoHybridDrafting2026.md)
- Components: [Proactive edge drafting](proactive-edge-drafting.md), [Tree-based speculation](tree-based-speculation.md), [SpecExec](specexec.md), [Sequoia](sequoia.md)
- Successor design on phones: [HyCo](hyco.md)
- Other device-cloud drafting: [HAT](hat.md)
- [Does proactive drafting help when the drafter runs on a phone?](../questions/proactive-drafting-on-a-phone.md)

[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
