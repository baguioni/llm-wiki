---
type: Method
title: I-DLM (Introspective Diffusion Language Model)
description: Diffusion LM converted from a pretrained AR model with causal attention, logit shift, and an all-masked loss, decoded by introspective strided decoding, which proposes tokens at masks and verifies the previous proposals with the p/q rule in the same forward pass; a lossless gated-LoRA variant makes it a self-speculative decoder.
tags: [diffusion-llm, self-speculative-decoding, parallel-decoding, llm-inference]
sources:
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
---

# I-DLM (Introspective Diffusion Language Model)

## Overview

I-DLM is a diffusion language model built to keep the *introspective consistency* of AR models: the property that a model accepts the tokens it generated when it re-reads them.[^yuIntrospectiveDiffusionLanguage2026] It is converted from a pretrained AR model and decoded by introspective strided decoding (ISD), which generates several tokens per forward pass and verifies them against the model's own causal (AR) distribution.[^yuIntrospectiveDiffusionLanguage2026]

## How it works

- **Training.** Strict causal attention over a $[x_t\,|\,x_0]$ input with $x_t$ fully masked; logit shift so position $i$ predicts token $i+1$; next-token cross-entropy on both regions with an auto-balanced weight $\hat{s}=\mathcal{L}_{\text{mask}}/\mathcal{L}_{\text{clean}}$.[^yuIntrospectiveDiffusionLanguage2026] Clean positions learn the causal anchor $p$ (the AR distribution) and masked positions learn proposals $q$.[^yuIntrospectiveDiffusionLanguage2026]
- **ISD.** Each step appends $N$ masks; the last clean position gives one AR token and the masks give $N-1$ proposals. In the next step the proposals become clean positions whose logits are their causal anchors, and they are accepted with $\min(1,p/q)$, resampled from $\text{normalize}(\max(0,p-q))$ on rejection, with a bonus token on full acceptance.[^yuIntrospectiveDiffusionLanguage2026] Verification shares the forward pass with the next proposals ($2N-1$ query tokens).[^yuIntrospectiveDiffusionLanguage2026]
- **R-ISD.** A LoRA residual gated to [MASK] positions improves proposals, while clean positions use base weights only; with causal attention this makes the anchor equal to the base AR model's distribution and the output bit-for-bit lossless.[^yuIntrospectiveDiffusionLanguage2026]
- **Serving.** Implemented in [SGLang](sglang.md) as an extend of $2N-1$ tokens, so paged KV cache and [continuous batching](continuous-batching.md) work unchanged, plus CUDA graph capture, a stationary-batch decode loop, a single paged attention kernel, and a fused Triton verify kernel.[^yuIntrospectiveDiffusionLanguage2026]

## Variants

- Stride $N$ from 2 to 8, with larger strides from continued stride-extension training (TPF 1.80 at $N=2$ to 4.01 at $N=8$ on 1×H100).[^yuIntrospectiveDiffusionLanguage2026]
- Relaxed acceptance with threshold $\tau$, a [lossy acceptance rule](lossy-acceptance.md): at $\tau=1$, HumanEval 93.3 → 91.2 and TPF 2.63 → 2.73.[^yuIntrospectiveDiffusionLanguage2026]
- Strict (ISD, $\tau=0$, AR distribution of the fine-tuned model) or lossless with respect to the original base model (R-ISD).[^yuIntrospectiveDiffusionLanguage2026]

## Papers using it

- [Yu et al. 2026](../papers/yuIntrospectiveDiffusionLanguage2026.md) build I-DLM-8B and I-DLM-32B from Qwen3-8B and Qwen3-32B with 4.5B training tokens on 8 H100s.[^yuIntrospectiveDiffusionLanguage2026] I-DLM-8B stays close to Qwen3-8B on the benchmarks of Table 1, with the largest gaps on AIME-25 (60.8 vs 65.4) and LiveCodeBench-v6 (45.7 vs 50.3), and is above it on MATH-500 (96.8 vs 95.8). It is well above SDAR (8B) and LLaDA-2.1-mini (16B).[^yuIntrospectiveDiffusionLanguage2026] In SGLang on Qwen3-8B it reaches 341 tok/s per request on MATH-500 at concurrency 1 against 238 for EAGLE-3.[^yuIntrospectiveDiffusionLanguage2026]
- [Osprey](../papers/bieOspreyTargetagnosticPretraining2026.md) applies the I-DLM training recipe to a four-layer LayerSkip-Llama backbone to build a compact diffusion LM that warm-starts a [DFlash](dflash.md) drafter body for Qwen3-8B. It chose I-DLM because ISD unifies decoding and verification in one forward step, which is structurally similar to speculative decoding.[^bieOspreyTargetagnosticPretraining2026] The warm start gains at most 0.07 accepted tokens under DFlash's original KV-injection interface.[^bieOspreyTargetagnosticPretraining2026]

## Strengths & Limitations

- No separate draft model, and output provably follows the causal anchor (exactly the base AR model with R-ISD).[^yuIntrospectiveDiffusionLanguage2026]
- Unlike block diffusion, no KV-commit forward pass is needed, and every step yields at least one token per request, so throughput scales with concurrency.[^yuIntrospectiveDiffusionLanguage2026]
- The model's weights change: without R-ISD, quality is slightly below the AR base on most benchmarks (LiveCodeBench-v6 45.7 vs 50.3 at 8B).[^yuIntrospectiveDiffusionLanguage2026]
- Every forward processes $2N-1$ query tokens, so compute overhead is roughly $2\times$ at $N=3$ and typical acceptance; the paper argues this is hidden in the memory-bound regime.[^yuIntrospectiveDiffusionLanguage2026]
- The released checkpoints (8B, 32B) are too large to serve as drafters for another target.[^bieOspreyTargetagnosticPretraining2026]
- Requires disabling SGLang's radix cache for the KV trim.[^yuIntrospectiveDiffusionLanguage2026]

## Related

- [Self-speculative decoding](self-speculative-decoding.md), [Speculative decoding](speculative-decoding.md), [Diffusion LLMs](diffusion-llm.md), [Block diffusion](block-diffusion.md), [DFlash](dflash.md), [EAGLE-3](eagle-3.md)
- [I-DLM-8B outpaces EAGLE-3 in per-request throughput on Qwen3-8B](../results/i-dlm-vs-eagle-3-throughput.md)

[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
