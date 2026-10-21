---
type: Method
title: Multi-Token Prediction (MTP)
description: A module that ships with the target model (DeepSeek-V3, DeepSeek-V4, Qwen3.5, Gemma 4 in the wiki's papers) and predicts tokens beyond the next one, reused as the drafter for speculative decoding.
tags: [speculative-decoding, draft-model, native-drafter, llm-inference, baseline]
sources:
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# Multi-Token Prediction (MTP)

## Overview

Multi-token prediction modules are trained with the target model and can be repurposed for speculation after training.[^samarinLKLossesDirect2026] In the wiki's papers, MTP appears as the native drafter of DeepSeek-V3, of the DeepSeek-V4 production system, and of Qwen3.5 models, and it serves as a baseline for [speculative decoding](../methods/speculative-decoding.md) drafters.[^samarinLKLossesDirect2026][^chengDSparkConfidenceScheduledSpeculative2026][^chenDFlashBlockDiffusion2026] HyCo runs the native MTP head of Gemma 4 26B-A4B on a phone NPU as a drafter for the server model.[^baeHyCoHybridDrafting2026] The wiki has no Paper page that proposes MTP. Everything here comes from papers that fine-tune it or compare against it.

## How it works

- LK losses describes the Multi-Token Prediction module of DeepSeek-V3 as adopting an autoregressive design similar to [EAGLE](../methods/eagle.md)-style draft heads.[^samarinLKLossesDirect2026]
- The EAGLE-3 paper states that EAGLE inspired the multi-token prediction technique used in the pre-training of DeepSeek-v3, which in turn inspired new architectural designs in [EAGLE-3](../methods/eagle-3.md).[^liEAGLE3ScalingInference2025]
- The released open-source DeepSeek-V3 weights include only the first MTP module. It was originally trained to predict the first token and is reused autoregressively for later ones.[^samarinLKLossesDirect2026]
- The DeepSeek-V3 MTP module has an MoE architecture.[^samarinLKLossesDirect2026]

## Variants

- **MTP-1** is the former production setup of DeepSeek-V4, a single-token setup whose verification budget is a static 2 tokens per request. DSpark compares against it and mentions static multi-token drafters MTP-3/5.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Fine-tuned MTP.** LK losses initializes from the original DeepSeek-V3 MTP weights and fine-tunes for 1 epoch, with KL or with its hybrid LK loss, keeping the original MoE architecture and the full vocabulary.[^samarinLKLossesDirect2026]
- **Native MTP of Qwen3.5.** DFlash compares against "native MTP" for Qwen3.5-4B, Qwen3.5-9B, and Qwen3.5-35B-A3B. The paper does not describe the module.[^chenDFlashBlockDiffusion2026]
- **Gemma 4 MTP head.** Released with Gemma 4 26B-A4B as google/gemma-4-26B-A4B-it-assistant, 420M parameters, in BF16. It reads the input embedding of the current token, the last hidden state, and the keys and values of two verifier layers (the last full-attention and the last sliding-window layer).[^baeHyCoHybridDrafting2026]
- **On-device MTP Drafter (HyCo).** The Gemma 4 head with 4-bit QAT weights, an 86K-token output keep set, and a 1,024-token window, run on a phone NPU from state the server returns with each verification.[^baeHyCoHybridDrafting2026]
- **Naming.** SpecForge uses "Multi-Token Prediction Heads" for the [Medusa](../methods/medusa.md) stage of draft model design, which is a different architecture from the DeepSeek module.[^liSpecForgeFlexibleEfficient2026]

## Papers using it

### LK losses (Samarin et al. 2026)

DeepSeek-V3-0324 (685B). Chain sampling with $K=7$ in [vLLM](../methods/vllm.md), batch size 1. Each cell is average acceptance length $\tau$ / end-to-end speedup over decoding without speculation. "Original" is the public deepseek-ai checkpoint (DS-685B).[^samarinLKLossesDirect2026]

| MTP module | T=0 MT-Bench | T=0 HumanEval | T=0 GSM8K | T=1 MT-Bench | T=1 HumanEval | T=1 GSM8K |
|---|---|---|---|---|---|---|
| Original | 2.90 / 1.66 | 3.28 / 1.84 | 3.41 / 1.82 | 2.82 / 1.54 | 3.17 / 1.59 | 3.27 / 1.47 |
| Fine-tuned, KL | 3.96 / 2.22 | 4.74 / 2.62 | 5.67 / 2.95 | 3.66 / 1.85 | 4.39 / 2.17 | 5.23 / 2.30 |
| Fine-tuned, $\mathcal{L}_{\text{LK}}^{\lambda}$ | 4.00 / 2.22 | 4.77 / 2.64 | 5.72 / 2.97 | 3.88 / 2.14 | 4.64 / 2.42 | 5.51 / 2.71 |

All rows: [^samarinLKLossesDirect2026]

Mean $\tau$ over the three benchmarks: 3.20 (original), 4.79 (KL), and 4.83 (+0.8) (LK) at $T=0$; 3.09, 4.43, and 4.68 (+5.6) at $T=1$.[^samarinLKLossesDirect2026]

### DSpark (Cheng et al. 2026)

[DSpark](../methods/dspark.md)-5 (maximum draft length $\gamma=5$) against MTP-1 in the production serving engines of DeepSeek-V4-Flash (preview) and DeepSeek-V4-Pro (preview), under live user traffic.[^chengDSparkConfidenceScheduledSpeculative2026]

| Engine | Condition | DSpark vs. MTP-1 |
|---|---|---|
| V4-Flash | 80 tok/s/user SLA | 51% higher aggregate throughput |
| V4-Flash | 120 tok/s/user SLA | nominal 661% higher aggregate throughput |
| V4-Flash | matched practical throughput levels | 60% to 85% faster per-user generation |
| V4-Pro | 35 tok/s/user SLA | 52% higher aggregate throughput |
| V4-Pro | 50 tok/s/user SLA | nominal 406% relative throughput advantage |
| V4-Pro | matched system capacities | 57% to 78% faster per-user generation |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

- At the strict SLAs (120 and 50 tok/s/user), MTP-1 can sustain only a very small concurrent batch.[^chengDSparkConfidenceScheduledSpeculative2026]
- MTP-1 was kept in production because a static multi-token drafter (e.g., MTP-3/5) degrades aggregate throughput under high concurrency due to excessive verification overhead. DSpark superseded MTP-1 two weeks after the DeepSeek-V4-preview release.[^chengDSparkConfidenceScheduledSpeculative2026]
- Under moderate concurrency, the DSpark scheduler extends the verification budget from MTP-1's static 2 tokens to roughly 4–6 tokens per request.[^chengDSparkConfidenceScheduledSpeculative2026]

### DFlash (Chen et al. 2026)

[SGLang](../methods/sglang.md) on one B200 with concurrency 8. Each cell is acceptance length / speedup over autoregressive decoding.[^chenDFlashBlockDiffusion2026]

| Model | Method | Math500 | HumanEval | MT-Bench |
|---|---|---|---|---|
| Qwen3.5-4B | MTP | 6.5 / 1.5× | 6.3 / 1.6× | 5.3 / 1.3× |
| Qwen3.5-4B | DFlash | 7.1 / 3.0× | 7.3 / 2.9× | 5.6 / 2.3× |
| Qwen3.5-9B | MTP | 6.7 / 1.7× | 6.6 / 1.7× | 5.3 / 1.3× |
| Qwen3.5-9B | DFlash | 7.3 / 3.5× | 7.9 / 3.4× | 5.5 / 2.5× |
| Qwen3.5-35B-A3B | MTP | 6.9 / 1.7× | 7.1 / 1.6× | 5.2 / 1.2× |
| Qwen3.5-35B-A3B | DFlash | 7.2 / 2.4× | 7.9 / 2.3× | 5.4 / 1.7× |

All rows: [^chenDFlashBlockDiffusion2026]

In this table the native MTP has an acceptance length close to [DFlash](../methods/dflash.md) (for example 6.5 vs 7.1 on Math500 for Qwen3.5-4B) but about half the speedup (1.5× vs 3.0×).[^chenDFlashBlockDiffusion2026]

### HyCo ([HyCo](../papers/baeHyCoHybridDrafting2026.md))

Gemma 4 26B-A4B (AWQ 4-bit) on one RTX PRO 6000, sampling at temperature 1, top-$k$ 64, top-$p$ 0.95. *Cloud+MTP* is server-side MTP self-speculation with the released BF16 head over the full prefix and vocabulary, chain depth $K=4$, and exact verification. HyCo moves the head to a Galaxy S26 Ultra NPU and adds one SLM pass for alternative branches.[^baeHyCoHybridDrafting2026]

| Configuration | SB-480 $g$ (ms/token) | SB-480 MAT | 32K $g$ (ms/token) | 32K MAT |
|---|---|---|---|---|
| Cloud+MTP | 7.81 | 3.05 | 23.91 | 2.37 |
| HyCo server head (BF16 head on server, 86K vocab, 1K window, + one SLM pass, exact) | 6.67 | 3.79 | 23.00 | 2.70 |
| HyCo exact (W4 head on phone, + one SLM pass) | 5.64 | 3.84 | 21.07 | 2.81 |
| HyCo ($\epsilon=0.005$) | 4.80 | 4.71 | 16.92 | 3.73 |

All rows: [^baeHyCoHybridDrafting2026]

- After every verification pass, Cloud+MTP runs the head's $K$ sequential steps on the server. On UC-val, moving the head to the phone shortens the server's median round from 26.8 to 21.7 ms and lowers server GPU time per token by 15.2%, at about 20 ms more per round on the phone.[^baeHyCoHybridDrafting2026]
- The chain's per-depth acceptance rate is 0.65–0.68 at every depth (geometric mean 0.66), and cumulative chain acceptance reaches 18.9% at depth 4.[^baeHyCoHybridDrafting2026]
- 4-bit QAT of the head (100 steps, KL from the BF16 head) raises top-1 agreement with BF16 on UC-val from 87.4% to 91.0%. 8-bit weights retain 98.8% without training.[^baeHyCoHybridDrafting2026]
- In a paired 150-question Spec-Bench experiment, the device-head configuration (W4, 86K keep set, 1K window) has 4.0% lower MAT than the original BF16 server head (95% CI 3.0–4.9%).[^baeHyCoHybridDrafting2026]
- The head's server-side CUDA graphs agree with eager execution on 99.2–99.6% of tokens.[^baeHyCoHybridDrafting2026]

## Strengths & Limitations

- Strength: the module ships with the target model, so no separate draft has to be trained before first use. LK losses evaluates the released DeepSeek-V3 module as is.[^samarinLKLossesDirect2026]
- Limitation: the released DeepSeek-V3 module was not trained primarily for predicting multiple tokens ahead. Fine-tuning it with KL raises the mean $\tau$ from 3.20 to 4.79 at $T=0$.[^samarinLKLossesDirect2026]
- Limitation: a static multi-token setup degrades aggregate throughput under high concurrency, which is why production used the single-token MTP-1.[^chengDSparkConfidenceScheduledSpeculative2026]
- Strength: the head reads only a small slice of the LLM's state, so it can run on a phone if the server returns that state (5.6 KB per round plus 6.1 KB per output token at 8 bits in HyCo).[^baeHyCoHybridDrafting2026]
- Limitation: on Qwen3.5 the native MTP's speedup is 1.2× to 1.7× at concurrency 8, below DFlash's 1.7× to 3.5× on the same models.[^chenDFlashBlockDiffusion2026]

Caveat on the numbers: the papers measure different modules (DeepSeek-V3, DeepSeek-V4 production, Qwen3.5, Gemma 4) with different metrics, so no two of their numbers describe the same setting.

## Related

- Parent concept: [Speculative decoding](../methods/speculative-decoding.md)
- Related drafters: [EAGLE](../methods/eagle.md), [EAGLE-3](../methods/eagle-3.md), [Medusa](../methods/medusa.md)
- Methods compared against it: [DSpark](../methods/dspark.md), [DFlash](../methods/dflash.md), [HyCo](../methods/hyco.md) (runs it on the phone)
- Serving engines: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md)
- Datasets: [MT-Bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [MATH-500](../datasets/math-500.md)

[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
