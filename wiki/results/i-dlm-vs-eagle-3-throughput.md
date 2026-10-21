---
type: Result
title: I-DLM-8B outpaces EAGLE-3 in per-request throughput on Qwen3-8B
description: In SGLang on one H100, I-DLM-8B (a Qwen3-8B converted to an introspective diffusion LM) generates 341 tok/s per request on MATH-500 at concurrency 1 against 238 for Qwen3-8B with an EAGLE-3 chain draft, and stays ahead up to concurrency 32; the bit-for-bit lossless variant reaches 310 tok/s.
tags: [speculative-decoding, self-speculative-decoding, diffusion-llm, eagle-3, throughput]
sources:
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
---

# I-DLM-8B outpaces EAGLE-3 in per-request throughput on Qwen3-8B

## Claim

I-DLM has higher per-request throughput than EAGLE-3 on Qwen3-8B from concurrency 1 through 32 on MATH-500, LMSYS-Chat, and MBPP, and its lossless variant (R-ISD) is ahead at most concurrencies.[^yuIntrospectiveDiffusionLanguage2026]

## Conditions

- Hardware and engine: NVIDIA H100 80GB SXM, TP 1, [SGLang](../methods/sglang.md) with FlashInfer, CUDA graphs on, radix cache disabled, bf16.[^yuIntrospectiveDiffusionLanguage2026]
- I-DLM-8B: Qwen3-8B converted with 4.5B tokens; ISD with temperature 1.0, top-$k$ 50, top-$p$ 0.95. The serving table lists I-DLM-8B at $N=3$ and $N=5$ and the lossless variant at $N=3$ with a rank-128 LoRA.[^yuIntrospectiveDiffusionLanguage2026]
- EAGLE-3: target Qwen3-8B, draft `Tengyunw/qwen3_8b_eagle3`, steps=3, topk=1, d=4 (3 speculations verified per step), reproduced with its SGLang integration.[^yuIntrospectiveDiffusionLanguage2026]
- Benchmark: genai-bench, burst arrival, 2,048 output tokens, throughput = total tokens / wall-clock time, 5 warmup requests discarded.[^yuIntrospectiveDiffusionLanguage2026]

## Numbers

| Workload | Concurrency | I-DLM | I-DLM-Lossless | EAGLE-3 |
|---|---|---|---|---|
| MATH-500 | 1 | 341 | 310 | 238 |
| LMSYS-Chat | 1 | 319 | — | 221 |
| MBPP | 1 | 327 | — | 245 |
| MATH-500 | 32 | 199 | — | 176 |
| LMSYS-Chat | 32 | 195 | — | 184 |

Tokens per second per request. All rows: [^yuIntrospectiveDiffusionLanguage2026]

## Comparisons

- I-DLM is not lossless with respect to Qwen3-8B: its quality differs slightly (for example MATH-500 96.8 vs 95.8, LiveCodeBench-v6 45.7 vs 50.3). EAGLE-3 and R-ISD preserve the base model's output distribution.[^yuIntrospectiveDiffusionLanguage2026]
- The 341 tok/s on MATH-500 equals Table 13's peak for the $N=4$ stride-extended I-DLM-8B checkpoint; the text does not say which stride the throughput comparison uses.[^yuIntrospectiveDiffusionLanguage2026]
- Table 13 lists R-ISD at 240 TPS on MATH-500 ($N=3$, H100), not 310; the paper does not reconcile the two.[^yuIntrospectiveDiffusionLanguage2026]
- The EAGLE-3 setup is a short chain with no tree. Other papers in the wiki report very different EAGLE-3 numbers depending on configuration; see [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md).

## Related

- [I-DLM](../methods/i-dlm.md), [EAGLE-3](../methods/eagle-3.md), [Self-speculative decoding](../methods/self-speculative-decoding.md)
- [Introspective Diffusion Language Models](../papers/yuIntrospectiveDiffusionLanguage2026.md)

[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
