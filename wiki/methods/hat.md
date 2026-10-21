---
type: Method
title: HAT
description: Device-cloud framework that combines U-shaped split inference with speculative decoding, drafting on the device from the LLM's shallow layers, head, and a distilled adapter, with prompt chunking and parallel drafting to hide transfer and drafting delays.
tags: [speculative-decoding, device-cloud-collaborative-inference, split-inference, u-shaped-inference, parallel-drafting, edge-inference, speculative-drafter]
sources:
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: "A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# HAT

## Overview

HAT splits an LLM between a device and the cloud. The device keeps the first decoder layers and the output head, so raw tokens never leave it, as in [U-shaped inference](u-shaped-inference.md). The cloud runs the middle layers. To cut the cost of sending hidden states at every step, HAT adds [speculative decoding](speculative-decoding.md) with a draft model that lives on the device.[^xieNovelHatShapedDeviceCloud2025]

## How it works

- **Draft model.** $w_{S}=H_{L}\circ\Lambda\circ w^{m}_{L}$: the LLM's first $m$ decoder layers ($m$ less than 10% of $n$), an adapter $\Lambda$ with the structure of one self-attention module, and the LLM's output head. $\Lambda$ is distilled from the cloud's middle submodel with an EAGLE-style loss (Smooth L1 on hidden states plus cross-entropy with $w_{ce}$ typically 0.1).[^xieNovelHatShapedDeviceCloud2025]
- **Adaptive draft length.** Drafting stops when a draft token's softmax probability falls below $\eta$ (0.6 in the experiments).[^xieNovelHatShapedDeviceCloud2025]
- **Verification.** The draft goes through the device's shallow layers, the hidden states go to the cloud, the middle layers return deep hidden states, and the device's head produces the result. Only hidden states cross the network.[^xieNovelHatShapedDeviceCloud2025]
- **Prompt chunking.** Long prompts are split into chunks so that uploading one chunk overlaps with cloud computation on the previous one. The chunk size solves $\frac{X_{i}\cdot A}{\beta^{t}_{i,up}}=\frac{g^{t}(\mu^{t})+g^{t}(\mu^{t}+X_{i})}{P}$.[^xieNovelHatShapedDeviceCloud2025]
- **Parallel drafting.** The last draft token is the one below the confidence threshold, so it is likely to be corrected. During verification the device drafts a continuation from each of that step's top-k tokens. If the cloud's corrected token matches a candidate, its continuation is used in the next round. The cloud sets the number of pre-draft steps so drafting finishes before the verification result arrives.[^xieNovelHatShapedDeviceCloud2025]

## Papers using it

### HAT paper ([Xie et al. 2025](../papers/xieNovelHatShapedDeviceCloud2025.md))

Cloud: 8 RTX A6000 GPUs with pipeline parallelism. Devices: 30 NVIDIA Jetsons (20 AGX Xavier, 10 AGX Orin) on WiFi. Vicuna-7B on SpecBench and Vicuna-13B on CNN/DM.[^xieNovelHatShapedDeviceCloud2025]

- Against U-shaped baselines, HAT reduces TTFT by 41% to 54% and TBT by 41% to 77%.[^xieNovelHatShapedDeviceCloud2025]
- Speculative decoding alone, one device: on SpecBench HAT has 67M trained parameters, an accept length of 2.06, and a 1.65× decoding speedup over U-shape, against 591M, 1.89, and 1.41× for U-Medusa.[^xieNovelHatShapedDeviceCloud2025]
- Ablation on SpecBench TBT (ms): U-shape 52.3, +SD 38.3, +SD+parallel drafting 33.8, all three mechanisms 26.4.[^xieNovelHatShapedDeviceCloud2025]

### Characterized by HyCo ([HyCo](../papers/baeHyCoHybridDrafting2026.md))

HyCo's related-work table lists HAT among device-cloud systems that draft on the device and verify every token, but do not draft with the LLM's native draft head or from server-computed state. HyCo describes HAT as running the LLM's first layers on the device.[^baeHyCoHybridDrafting2026]

## Strengths & Limitations

- Raw tokens stay on the device.[^xieNovelHatShapedDeviceCloud2025]
- Hidden states are much larger than tokens. In the motivation run with plain U-shaped inference, a 2k-token prompt had a TTFT of 3.57s, of which communication was 3.20s (89.6%).[^xieNovelHatShapedDeviceCloud2025]
- The paper reports neither how often the pre-drafted continuation is used nor any energy measurement. The devices are Jetson boards, not phones.

## Related

- [Target-aware recovery of compressed drafters](../analyses/target-aware-recovery-of-compressed-drafters.md)
- [Does recovering a pruned drafter against the target beat recovering it against its parent?](../questions/target-aware-recovery-of-pruned-drafters.md)
- Paper: [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md)
- Split inference: [U-shaped inference](u-shaped-inference.md)
- Draft training: [EAGLE](eagle.md), [Knowledge distillation](knowledge-distillation.md)
- Baseline drafter: [Medusa](medusa.md)
- Prefill chunking: [Chunked prefill](chunked-prefill.md)
- Other edge drafting setups: [SpecEdge](specedge.md), [Lever](lever.md), [HyCo](hyco.md)

## Open questions and results

- [Can a block drafter pre-draft with stale target features?](../questions/pre-drafting-with-stale-target-features.md)

[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
