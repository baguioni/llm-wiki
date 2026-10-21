---
type: Method
title: AdaSPEC
description: Selective knowledge distillation for speculative-decoding drafts that trains the draft only on the top-k fraction of tokens where its KL to the target exceeds that of a DistillSpec-distilled reference copy, to raise acceptance rate within the draft's limited capacity.
tags: [speculative-decoding, knowledge-distillation, draft-model, token-selection, acceptance-rate]
sources:
  - id: huAdaSPECSelectiveKnowledge2025
    resource: zotero://select/items/@huAdaSPECSelectiveKnowledge2025
    title: "AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders"
---

# AdaSPEC

## Overview

AdaSPEC is a [knowledge distillation](knowledge-distillation.md) method for [speculative decoding](speculative-decoding.md) drafts. Its premise is that minimizing KL over all tokens is misaligned with maximizing acceptance rate, because a small draft cannot fit the whole target distribution and wastes capacity on tokens that are hard to learn and unlikely to be accepted.[^huAdaSPECSelectiveKnowledge2025] It therefore distills only on a selected subset of tokens, chosen with a reference model.[^huAdaSPECSelectiveKnowledge2025]

## How it works

1. Fine-tune the target on the task data.[^huAdaSPECSelectiveKnowledge2025]
2. Copy the draft into a reference model and distill it from the target with [DistillSpec](distillspec.md) using forward KL.[^huAdaSPECSelectiveKnowledge2025]
3. For every token, compute the forward KL from the target to the draft, $\mathcal{L}_{\mathrm{draft}}$, and to the reference, $\mathcal{L}_{\mathrm{ref}}$. Keep the tokens whose $\Delta_{\mathcal{L}}=\mathcal{L}_{\mathrm{draft}}-\mathcal{L}_{\mathrm{ref}}$ is in the top $k\times100\%$ and train the draft on the forward KL of those tokens only, normalized by $k\cdot|y|$.[^huAdaSPECSelectiveKnowledge2025]

- The paper reads a high $\Delta_{\mathcal{L}}$ as a token that is not yet aligned but learnable at the draft's size, since a same-size reference already fits it.[^huAdaSPECSelectiveKnowledge2025]
- Default $k=0.4$; lower values (0.2-0.4) generally do better on GSM8K.[^huAdaSPECSelectiveKnowledge2025]
- Training data is the task dataset; the method needs target, reference, and draft logits at each step.[^huAdaSPECSelectiveKnowledge2025]

## Variants

- **Fine-tuning instead of distillation** for both reference and draft still beats the distilled reference (GSM8K 63.13% vs 59.77%; MBPP 45.61% vs 42.22%).[^huAdaSPECSelectiveKnowledge2025]
- **Other divergences.** With TVD or reverse KL in place of forward KL, acceptance collapses (reference $\alpha$ 9.32% and 30.22% on GSM8K).[^huAdaSPECSelectiveKnowledge2025]
- **On EAGLE.** Applied to [EAGLE](eagle.md) training for Vicuna-7B-v1.3 on ShareGPT, it raises first-token training accuracy from 75.3% to 76.3% and MT-Bench speed from 63.48 to 68.21 tokens/s.[^huAdaSPECSelectiveKnowledge2025]

## Papers using it

- [Hu et al. 2025](../papers/huAdaSPECSelectiveKnowledge2025.md) propose AdaSPEC and compare it with DistillSpec on Pythia-31M → 1.4B and CodeGen-350M → Phi-2 over GSM8K, Alpaca, MBPP, CNN/Daily Mail, and XSUM, under greedy verification.[^huAdaSPECSelectiveKnowledge2025]
  - Acceptance rate is higher than DistillSpec in all 20 task/pair/setting cells; the largest gap is MBPP with Pythia in the Optimal-Epoch setting, 49.88% → 65.12%.[^huAdaSPECSelectiveKnowledge2025]
  - In [vLLM](vllm.md) on one A100, tokens/s rises from 149.15 to 181.67 (MBPP), 227.86 to 241.34 (GSM8K), and 248.49 to 283.50 (CNN/DailyMail) over DistillSpec.[^huAdaSPECSelectiveKnowledge2025]
  - Qwen2.5-0.5B → Qwen2.5-32B on GSM8K: 84.43% (DistillSpec) → 86.21%.[^huAdaSPECSelectiveKnowledge2025]

## Strengths & Limitations

- Gains over DistillSpec grow with the draft-target size gap.[^huAdaSPECSelectiveKnowledge2025]
- The core is about 100 lines of PyTorch on top of a KD trainer.[^huAdaSPECSelectiveKnowledge2025]
- Requires training a reference model first, and per-task training of target, reference, and draft.[^huAdaSPECSelectiveKnowledge2025]
- Evaluated with greedy acceptance and chain drafts only; integration with tree-based or multi-step verification is left as future work.[^huAdaSPECSelectiveKnowledge2025]
- The DistillSpec baseline is run with a shorter schedule than in its own paper and with forward KL only.[^huAdaSPECSelectiveKnowledge2025]

## Related

- [DistillSpec](distillspec.md), [GKD](gkd.md), [Knowledge distillation](knowledge-distillation.md), [Speculative decoding](speculative-decoding.md)
- [Which divergence should a draft model be distilled with?](../questions/drafter-distillation-divergence.md)
- [Does an acceptance-oriented loss help a block diffusion drafter?](../questions/acceptance-oriented-loss-for-block-drafters.md)

[^huAdaSPECSelectiveKnowledge2025]: Hu et al. 2025
