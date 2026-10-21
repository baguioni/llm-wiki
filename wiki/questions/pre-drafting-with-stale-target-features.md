---
type: Open Question
title: Can a block drafter pre-draft with stale target features?
description: In mobile-server speculative decoding the phone idles while the server verifies, but a DFlash-style drafter needs target features that arrive only with the verify response.
tags: [speculative-decoding, dflash, draft-model, mobile-npu, mobile-specedge, proactive-drafting]
sources:
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# Can a block drafter pre-draft with stale target features?

## Question

How much acceptance does a DFlash-style drafter lose when the target context features of the most recent tokens are missing, and is the loss small enough to draft the next block while the server is still verifying the current one?

## Why it matters

In my live runs the draft takes about 30 ms and the server forward about 98 ms per round (see [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md)). The phone is idle for most of each round. If the drafter tolerates stale features, that idle time can hold the next draft.

## Evidence so far

- DFlash conditions the drafter on context features extracted from the target model, and injects them into the Key and Value projections of every draft layer.[^chenDFlashBlockDiffusion2026]
- The drafter always conditions on the clean bonus token from the previous verification step.[^chenDFlashBlockDiffusion2026] A pre-draft does not have that token either.
- A 5-layer block diffusion drafter without any target context features still reaches $\tau$ of 3.38 on GSM8K and 4.61 on Math500 at temperature 0.[^chenDFlashBlockDiffusion2026] The target model of that table is not stated, so it cannot be compared directly with the tables that use features.
- KV injection against input fusion on Qwen3-4B: $\tau$ 4.2 against 3.5 on GSM8K.[^chenDFlashBlockDiffusion2026] The drafter is sensitive to how the features enter.

### HAT: pre-drafting during verification without target features

- [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md) drafts on the device while the cloud verifies. Its last draft token is the one below the confidence threshold, so it is likely to be corrected. The device drafts a continuation from each of that step's top-k tokens, and reuses the one that matches the cloud's corrected token.[^xieNovelHatShapedDeviceCloud2025]
- The cloud sets the number of pre-draft steps so that drafting ends before the verification result returns, from the upload time, cloud compute time, download time, and the device's per-step draft time.[^xieNovelHatShapedDeviceCloud2025]
- HAT's drafter needs no fresh target features. It is the LLM's first layers, an adapter distilled from the middle layers, and the head, all on the device.[^xieNovelHatShapedDeviceCloud2025]
- Adding parallel drafting on top of speculative decoding lowers TBT from 38.3 to 33.8 ms on SpecBench (Vicuna-7B) and from 84.3 to 74.9 ms on CNN/DM (Vicuna-13B), on Jetson devices over WiFi.[^xieNovelHatShapedDeviceCloud2025]
- The paper does not report how often the pre-drafted continuation is used.

### HyCo: proactive drafting on a phone, and a drafter fed by the server's state

- HyCo's MTP Drafter on the phone depends on the target's state: each verification reply carries the root's input embedding, the last hidden state, and two layers' KV entries, and the head drafts only after the reply arrives.[^baeHyCoHybridDrafting2026]
- On HyCo's SpecEdge-style baseline, proactive drafting during the verification wait raises server saving (20.6% to 23.9% on Spec-Bench) but lowers delivery speed on the phone from 16.1 to 12.1 tokens/s. See [Does proactive drafting help when the drafter runs on a phone?](proactive-drafting-on-a-phone.md).[^baeHyCoHybridDrafting2026]
- Recorded Spec-Bench summaries put network and serialization at roughly 40–58 ms per round.[^baeHyCoHybridDrafting2026]

**Inference.** HAT's branching assumes that the rejection falls on the last draft token, so the rest of the block is kept. A DFlash pre-draft would also have to guess the bonus token, and a top-k branch over it is a cheap way to cover that guess. HAT shows the scheme lowers TBT, but not with a drafter that depends on target features.

**Inference.** The first two points say the drafter was never trained for this case. The third says a block drafter is still useful with no features at all, so a few missing positions may cost little.

## Conflicting claims

None. No paper in the wiki measures a drafter with partly missing features.

## What would resolve it

1. Offline, on logged blocks: withhold the features of the last $k$ tokens for $k$ from 1 to 7 and measure acceptance.
2. If the loss is large, fine-tune with the features of the last few tokens randomly dropped, and measure again.
3. In the client: pre-draft during the verify wait and measure tokens per second and how often the pre-draft is usable.

## Related

- [DFlash research directions for mobile SpecEdge](../analyses/dflash-research-directions-for-mobile-specedge.md)
- [DFlash](../methods/dflash.md), [KV injection](../methods/kv-injection.md), [Speculative decoding](../methods/speculative-decoding.md)
- [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md), [HAT](../methods/hat.md), [HyCo](../methods/hyco.md), [Proactive edge drafting](../methods/proactive-edge-drafting.md)

[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
