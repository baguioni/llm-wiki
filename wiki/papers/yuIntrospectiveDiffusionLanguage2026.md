---
type: Paper
title: "Introspective Diffusion Language Models"
description: I-DLM converts Qwen3-8B and Qwen3-32B into diffusion LMs with causal attention, logit shift, and an all-masked loss, and decodes them with introspective strided decoding, which proposes new tokens and verifies earlier ones in one forward pass, matching the AR base on 15 benchmarks and beating EAGLE-3 throughput in SGLang at concurrency 1 to 32.
tags: [diffusion-llm, self-speculative-decoding, parallel-decoding, llm-inference, sglang, speculative-drafter]
collections: [speculative drafter]
authors: [Yifan Yu, Yuqing Jian, Junxiong Wang, Zhongzhu Zhou, Donglin Zhuang, Xinyu Fang, Sri Yanamandra, Qingyang Wu, Tri Dao, Xiaoxia Wu, Shuaiwen Leon Song, Ben Athiwaratkun, James Zou, Fan Lai, Chenfeng Xu]
doi: 10.48550/arXiv.2604.11035
arxiv: "2604.11035"
arxiv_version: 2604.11035v1
sources:
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
---

# Introspective Diffusion Language Models

Text source: arXiv HTML, version `2604.11035v1`.

## Summary

The paper attributes the quality gap between [diffusion language models](../methods/diffusion-llm.md) (DLMs) and autoregressive (AR) models to missing *introspective consistency*: AR models agree with their own generations, while DLMs often do not.[^yuIntrospectiveDiffusionLanguage2026] It measures this with the *introspective acceptance rate*, and argues that causal masking plus logit shifting in AR training enforce the property implicitly.[^yuIntrospectiveDiffusionLanguage2026]

[I-DLM](../methods/i-dlm.md) converts a pretrained AR model into a DLM with causal attention, logit shift, and an all-masked training objective, and decodes it with introspective strided decoding (ISD), which verifies previously generated tokens and proposes new ones in the same forward pass with the speculative-decoding $p/q$ acceptance rule.[^yuIntrospectiveDiffusionLanguage2026] It is served as an extension of [SGLang](../methods/sglang.md) with a stationary-batch scheduler.[^yuIntrospectiveDiffusionLanguage2026] The authors state that I-DLM is the first DLM to match its same-scale AR counterpart, across 15 benchmarks: 69.6 on AIME-24 and 45.7 on LiveCodeBench-v6, more than 26 and 15 points above LLaDA-2.1-mini (16B), and about 3× the throughput of prior state-of-the-art DLMs.[^yuIntrospectiveDiffusionLanguage2026]

## Contributions

- The observation that DLMs are not trained to agree with their own generations, formalized as the introspective acceptance rate.[^yuIntrospectiveDiffusionLanguage2026]
- Introspective-consistency training, a recipe that converts a pretrained AR model into an introspective DLM with a few billion tokens and no distillation schedule or masking curriculum.[^yuIntrospectiveDiffusionLanguage2026]
- Introspective Strided Decoding (ISD), a single-pass algorithm that generates new tokens at [MASK] positions and verifies earlier tokens against a causal anchor distribution, with output that provably matches the base AR distribution.[^yuIntrospectiveDiffusionLanguage2026]
- An AR-compatible serving stack in SGLang, and a gated LoRA mode (R-ISD) whose output is bit-for-bit identical to the base AR model.[^yuIntrospectiveDiffusionLanguage2026]

## Method

### Introspective acceptance rate

For each generated token $x_k$ sampled from $q_k$, a separate forward pass with all tokens revealed gives the causal distribution $p_k$, and $\alpha=\frac{1}{L}\sum_k\min(1,p_k(x_k)/q_k(x_k))$. For AR models $p=q$ and $\alpha=1$.[^yuIntrospectiveDiffusionLanguage2026] On IFEval, SDAR (8B) reaches 0.699 and LLaDA 2.0-flash (8B) 0.568.[^yuIntrospectiveDiffusionLanguage2026]

### Introspective-consistency training

- **Strict causal attention** over both the masked and the clean parts of the input: each [MASK] attends only to preceding positions. SDAR, by contrast, uses block-causal attention, bidirectional within blocks.[^yuIntrospectiveDiffusionLanguage2026]
- **Logit shift:** the hidden state at position $i$ predicts token $i+1$, keeping the AR model's logits[$i$] → token[$i+1$] mapping. Clean positions then produce the causal anchor $p$ (the verify distribution) and masked positions produce proposals $q$.[^yuIntrospectiveDiffusionLanguage2026]
- **All-masked input:** the training input is $[x_t\,|\,x_0]$, where every token of $x_t$ is [MASK] and $x_0$ is the clean sequence, so every position carries a training signal.[^yuIntrospectiveDiffusionLanguage2026]
- **Auto-balanced loss:** $\mathcal{L}=\mathcal{L}_{\text{mask}}+\hat{s}\cdot\mathcal{L}_{\text{clean}}$ with $\hat{s}=\mathcal{L}_{\text{mask}}/\mathcal{L}_{\text{clean}}$ treated as a constant each step. Both terms are next-token cross-entropy; no teacher or separate distillation loss is used.[^yuIntrospectiveDiffusionLanguage2026]
- The individual ingredients (causal-mask training, logit shifting, full-mask training) appear separately in earlier work; the paper's claim is about their combination.[^yuIntrospectiveDiffusionLanguage2026]

### Introspective Strided Decoding (ISD)

- ISD starts with a standard AR prefill. Each step appends $N$ [MASK] tokens. Because of the logit shift, the last clean position gives one token $x_1$ identical to an AR prediction, and the $N-1$ masks give strided proposals.[^yuIntrospectiveDiffusionLanguage2026]
- In the next step the proposals are filled in as clean tokens, so their positions produce the causal anchors $p_k$, while fresh masks produce new proposals. Introspection therefore runs in the same forward pass as the next stride, in a $2N-1$ token pass.[^yuIntrospectiveDiffusionLanguage2026]
- Each proposal is accepted with probability $\min(1,p_k(x_k)/q_k(x_k))$; on rejection it is resampled from $\text{normalize}(\max(0,p_k-q_k))$ and later tokens are discarded; if all are accepted, a bonus token is sampled, for a stride of $N+1$.[^yuIntrospectiveDiffusionLanguage2026]
- Proposals use argmax, which the paper says does not affect output diversity because the $p/q$ rule guarantees correctness regardless of proposal quality.[^yuIntrospectiveDiffusionLanguage2026]
- **Expected tokens per forward:** $\text{TPF}_N=\frac{2+P_1+\cdots+P_{N-2}}{2-P_{N-1}}$ with $P_k$ the cumulative acceptance probability; $\text{TPF}=N$ at full acceptance and 1 at zero acceptance. At $p\geq0.85$, stride $N=3$ reaches TPF $\approx2.3$-$2.4\times$ at roughly $2\times$ compute overhead.[^yuIntrospectiveDiffusionLanguage2026]
- **Relaxed acceptance:** a threshold $\tau$ multiplies the acceptance ratio by $(1+\tau)$, trading the AR guarantee for higher TPF without retraining.[^yuIntrospectiveDiffusionLanguage2026]

### Lossless ISD with gated LoRA (R-ISD)

A LoRA residual is applied only at [MASK] positions; introspection positions use base weights only. Because of strict causal attention, introspection positions never attend to [MASK] positions, so $p$ is computed from base-only weights over a base-only KV cache, which the paper states makes the output bit-for-bit identical to the base AR model.[^yuIntrospectiveDiffusionLanguage2026] The design is inspired by the gated LoRA of Samragh et al. (2025) for [multi-token prediction](../methods/multi-token-prediction.md).[^yuIntrospectiveDiffusionLanguage2026] The paper presents the single-forward draft-and-verify structure as a natural fit for [self-speculative decoding](../methods/self-speculative-decoding.md).[^yuIntrospectiveDiffusionLanguage2026]

### Compute comparison with block diffusion and TiDAR (Appendix B)

| Method | TPF | Overhead | Queries per forward |
|---|---|---|---|
| ISD (variable) | $\frac{2+p+\cdots+p^{N-2}}{2-p^{N-1}}$ | $\frac{3N-1-Np^{N-1}}{2+p+\cdots+p^{N-2}}$ | $N$ or $2N-1$ |
| ISD (fixed) | same | $\frac{(2N-1)(2-p^{N-1})}{2+p+\cdots+p^{N-2}}$ | $2N-1$ |
| SDAR (block diffusion) | $\frac{N}{\mathbb{E}[S\mid N]+1}$ | $\mathbb{E}[S\mid N]+1$ | $N$ |
| TiDAR | $\frac{1-p^N}{1-p}$ | $\frac{N(N+1)(1-p)}{1-p^N}$ | $N(N+1)$ |

All rows: [^yuIntrospectiveDiffusionLanguage2026]

- Block diffusion needs a separate KV-commit forward after denoising, which caps TPF at $N/2$ even at full acceptance. Fusing the commit with the next block's denoising would need per-position mixed attention masks that FlashAttention and FlashInfer do not support.[^yuIntrospectiveDiffusionLanguage2026]
- At $N=4$, compute efficiency TPF/OH exceeds 1 for ISD at $p\approx0.83$ (variable query) and $p\approx0.86$ (fixed query); at the observed $p\geq0.85$ ISD reaches $1.08$-$2.29\times$. TiDAR is capped at $N/(N+1)=0.80$, and SDAR stays around $0.64$-$0.72$ at practical acceptance rates.[^yuIntrospectiveDiffusionLanguage2026]

### Serving stack

- Each ISD step is an SGLang *extend* of $2N-1$ tokens with causal attention, so paged KV cache, [continuous batching](../methods/continuous-batching.md), and tensor parallelism are inherited unchanged. Every step yields at least one token per request, so requests advance uniformly.[^yuIntrospectiveDiffusionLanguage2026]
- The extend forward is captured in one CUDA graph; since extend sizes are at most 9 tokens, the three-kernel attention cascade is replaced with one paged kernel per layer.[^yuIntrospectiveDiffusionLanguage2026]
- A stationary-batch decode loop reuses the batch object across ISD steps because the forward → verify → trim → prepare chain blocks CPU-GPU overlap. Verification is a fused Triton kernel; the accept path (about 78% of positions) returns after one streaming pass.[^yuIntrospectiveDiffusionLanguage2026]
- SGLang parameters include disable-radix-cache=true, which is required for the DLLM KV trim.[^yuIntrospectiveDiffusionLanguage2026]

### Training details

- I-DLM-8B and I-DLM-32B from Qwen3-8B and Qwen3-32B, 4.5B tokens of responses generated across reasoning datasets, 8 H100 GPUs, built on the SDAR codebase.[^yuIntrospectiveDiffusionLanguage2026]
- I-DLM-8B: 2 epochs, stride $N=2$ then $N=3$, with a fixed clean-loss scale of 0.2 for the first two stride expansions and the auto-balanced loss from $N=3\to4$ on. I-DLM-32B: 1 epoch at $N=2$ with LoRA rank 1024 and scale 0.2.[^yuIntrospectiveDiffusionLanguage2026]
- Full fine-tuning, DeepSpeed ZeRO-2, LR $1\times10^{-5}$ with cosine decay and 0.03 warmup, effective batch 32, max length 4096, bf16. R-ISD LoRA rank 128, LR 2e-4.[^yuIntrospectiveDiffusionLanguage2026]
- $N=4$ and $N=8$ checkpoints come from further stride-extension training.[^yuIntrospectiveDiffusionLanguage2026]

## Experiments & Results

Benchmarks run with the Qwen3 chat template and thinking mode, temperature 1.0, top-$k$ 50, top-$p$ 0.95, max 32,768 tokens, averaged over three runs. Baselines are taken from their papers where available; LLaDA-2.1-mini, SDAR, and EAGLE-3 are reproduced in SGLang.[^yuIntrospectiveDiffusionLanguage2026]

### Quality (Table 1, I-DLM with ISD at $N=4$)

| Benchmark | LLaDA-2.1-mini (16B) | SDAR 8B | I-DLM 8B | Qwen3 8B | I-DLM 32B | Qwen3 32B |
|---|---|---|---|---|---|---|
| ARC-C | 90.2 | 91.9 | 95.8 | 95.8 | 96.8 | 97.2 |
| [MMLU](../datasets/mmlu.md) | 74.5 | 78.6 | 82.4 | 83.5 | 86.8 | 87.2 |
| MMLU-Pro | 64.8 | 56.9 | 73.1 | 75.1 | 79.7 | 80.1 |
| GPQA-D | 46.0 | 40.2 | 55.6 | 58.9 | 62.1 | 64.1 |
| GPQA | 53.3 | — | 54.9 | 55.4 | 58.7 | 65.0 |
| [GSM8K](../datasets/gsm8k.md) | 89.0 | 91.7 | 95.0 | 96.0 | 94.9 | 94.7 |
| [MATH-500](../datasets/math-500.md) | 85.0 | 78.6 | 96.8 | 95.8 | 97.6 | 97.8 |
| MathBench | 84.2 | 76.9 | 89.1 | 93.1 | 95.6 | 95.5 |
| AIME-24 | 43.3 | 10.0 | 69.6 | 73.1 | 83.3 | 76.7 |
| AIME-25 | 43.3 | 10.0 | 60.8 | 65.4 | 80.0 | 80.0 |
| [HumanEval](../datasets/humaneval.md) | 86.0 | 78.7 | 93.3 | 95.1 | 96.3 | 96.3 |
| [MBPP](../datasets/mbpp.md) | 82.1 | 72.0 | 92.2 | 93.4 | 94.6 | 95.7 |
| [LiveCodeBench](../datasets/livecodebench.md)-v6 | 30.4 | 16.6 | 45.7 | 50.3 | 57.1 | 58.3 |
| IFEval | 83.2 | 61.4 | 84.7 | 84.7 | 84.7 | 84.5 |

All rows: [^yuIntrospectiveDiffusionLanguage2026]

- Table 1 also lists LLaDA-2.0-flash (100B), LLaDA-2.1-flash (100B), and SDAR 30B-A3B; I-DLM-32B is +16.7 on AIME-25 and +11.7 on LiveCodeBench-v6 over LLaDA-2.1-flash (100B).[^yuIntrospectiveDiffusionLanguage2026]
- SDAR is built on the same Qwen3-8B base; it reaches 10.0 on AIME-24 against I-DLM-8B's 69.6, after 54B training tokens (12× more than I-DLM's 4.5B).[^yuIntrospectiveDiffusionLanguage2026]
- Table 2 adds DLMs reported in their own papers: on HumanEval / MBPP, NBDiff (7B) 89.0 / 87.6, TiDAR (8B) 57.9 / 65.4, DREAM (7B) 57.9 / 58.8, Fast-dLLM (7B) 43.3 / 28.2, Mercury Coder Small 90.0 / 76.6, Gemini Diffusion 89.6 / 76.0, against I-DLM-8B 93.3 / 92.2.[^yuIntrospectiveDiffusionLanguage2026]

### Serving efficiency

- Workloads: MBPP, MATH-500, LMSYS-Chat; concurrency $C\in\{1,\dots,64\}$; burst arrival, 2,048 output tokens; 1×H100 for 8B models, 2×H100 for 32B.[^yuIntrospectiveDiffusionLanguage2026]
- From $C\geq4$, I-DLM has higher per-request throughput than SDAR (8B) and LLaDA-2.1-mini (16B). At $C=16$-32 it delivers 2.2-3.8× the throughput of LLaDA-2.1-mini and 3.7-4.5× that of SDAR; at $C=64$ it sustains about 125 tok/s per request, 2.9-4.1× higher throughput.[^yuIntrospectiveDiffusionLanguage2026]
- On MATH-500, I-DLM-8B matches Qwen3-8B (thinking) quality at 3.1× higher throughput, is +11.8 points over LLaDA-2.1-mini (16B), and has 4.0× higher throughput than SDAR (8B) (Figure 1).[^yuIntrospectiveDiffusionLanguage2026]
- In Figure 2(c) at batch size 8, SDAR's tokens-per-second grows with TPF at a slope of 84, against 549 for ISD.[^yuIntrospectiveDiffusionLanguage2026]

### Comparison with EAGLE-3 on Qwen3-8B

EAGLE-3 is the `Tengyunw/qwen3_8b_eagle3` draft in SGLang with steps=3, topk=1, d=4 (3 speculations verified per step).[^yuIntrospectiveDiffusionLanguage2026]

| Workload | Concurrency | I-DLM tok/s | I-DLM-Lossless tok/s | EAGLE-3 tok/s |
|---|---|---|---|---|
| MATH-500 | 1 | 341 | 310 | 238 |
| LMSYS-Chat | 1 | 319 | — | 221 |
| MBPP | 1 | 327 | — | 245 |
| MATH-500 | 32 | 199 | — | 176 |
| LMSYS-Chat | 32 | 195 | — | 184 |

All rows: [^yuIntrospectiveDiffusionLanguage2026]

I-DLM is ahead of EAGLE-3 in per-request throughput from $C=1$ through $C=32$ on all three workloads, and I-DLM-Lossless is ahead at most concurrencies.[^yuIntrospectiveDiffusionLanguage2026]

### Ablations

- **Training design** (same data budget): block diffusion (block-causal attention, no logit shift) instead of I-DLM training drops HumanEval 92.7 → 60.3, MBPP 92.8 → 67.4, MathBench 89.1 → 71.6, and MMLU 82.4 → 80.0.[^yuIntrospectiveDiffusionLanguage2026]
- **Systems** (cumulative, $C=1,8,32$): the full system reaches 2.1-2.5× the naive baseline. CUDA graph capture +42-76%, stationary-batch decode loop +11-21%, argmax proposals +11-15%, paged-only attention +10-14%, kernel fusion +1-4%.[^yuIntrospectiveDiffusionLanguage2026] The three-kernel cascade costs +4% at $C=1$ and +20% at $C=64$ in forward latency.[^yuIntrospectiveDiffusionLanguage2026]

**Stride (Table 3, 1×H100, batch size 1):**

| $N$ | TPF | TPS | MATH-500 | MBPP |
|---|---|---|---|---|
| 2 | 1.80 | 209.6 | 96.8 | 93.4 |
| 3 | 2.48 | 281.9 | 95.8 | 92.8 |
| 4 | 2.96 | 324.5 | 96.8 | 92.2 |
| 8 | 4.01 | 445.1 | 94.6 | 88.3 |

All rows: [^yuIntrospectiveDiffusionLanguage2026]

**Relaxed acceptance (Table 4, $N=4$):**

| $\tau$ | 0 | 0.1 | 0.2 | 0.5 | 1 |
|---|---|---|---|---|---|
| HumanEval | 93.3 | 93.3 | 92.1 | 91.8 | 91.2 |
| TPF | 2.63 | 2.62 | 2.68 | 2.72 | 2.73 |

All rows: [^yuIntrospectiveDiffusionLanguage2026]

**Peak per-request TPS (Table 13):** 925 on GSM8K (B200, TP 2, $N=8$), 685 on MBPP (H100, TP 2, $N=8$), 341 on MATH-500 (H100, $N=4$), 272 on MATH-500 (H100, $N=3$), and 240 on MATH-500 for R-ISD with LoRA rank 128 (H100, $N=3$).[^yuIntrospectiveDiffusionLanguage2026]

### Use as a drafter warm start

Osprey uses the I-DLM training recipe on a four-layer LayerSkip-Llama backbone, trained on Nemotron-Post-Training-Dataset-v2, as the target-agnostic warm-start source for a [DFlash](../methods/dflash.md) drafter body, because the released I-DLM checkpoints are too large to serve as drafters.[^bieOspreyTargetagnosticPretraining2026] Under DFlash's original interface the warm start gains at most 0.07 accepted tokens in any domain.[^bieOspreyTargetagnosticPretraining2026]

## Limitations

- The "lossless" claim holds only for R-ISD; standard I-DLM decodes from the fine-tuned model's own causal anchor, and its quality is slightly below the AR base on most benchmarks (for example AIME-24 69.6 vs 73.1 and LiveCodeBench-v6 45.7 vs 50.3 at 8B).[^yuIntrospectiveDiffusionLanguage2026]
- The EAGLE-3 baseline uses a single chain configuration (topk=1, 3 speculations) and a third-party draft checkpoint.[^yuIntrospectiveDiffusionLanguage2026]
- Throughput figures for most concurrency levels and baselines are in figures only.[^yuIntrospectiveDiffusionLanguage2026]
- Internal inconsistencies: the training budget is given as 4.5B tokens in most places and "just using 5B tokens" in the contribution list; the stride ablation is cited as Table 4 but is Table 3; I-DLM-Lossless is 310 tok/s on MATH-500 at $C=1$ in Section 4.2 and 240 TPS for R-ISD on MATH-500 in Table 13 (at $N=3$); Appendix H places the throughput and infrastructure-ablation results in Sections 5 and 6, while in v1 Section 5 is the conclusion and there is no Section 6.[^yuIntrospectiveDiffusionLanguage2026]
- The paper has no limitations section.

## Related

- Methods proposed: [I-DLM](../methods/i-dlm.md)
- Methods: [Diffusion LLMs](../methods/diffusion-llm.md), [Block diffusion](../methods/block-diffusion.md), [Self-speculative decoding](../methods/self-speculative-decoding.md), [Speculative decoding](../methods/speculative-decoding.md), [Lossy acceptance rules](../methods/lossy-acceptance.md), [EAGLE-3](../methods/eagle-3.md), [Multi-token prediction](../methods/multi-token-prediction.md), [SGLang](../methods/sglang.md), [Continuous batching](../methods/continuous-batching.md), [PagedAttention](../methods/paged-attention.md)
- Datasets: [GSM8K](../datasets/gsm8k.md), [MATH-500](../datasets/math-500.md), [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), [LiveCodeBench](../datasets/livecodebench.md), [MMLU](../datasets/mmlu.md)
- Used by: [Osprey](bieOspreyTargetagnosticPretraining2026.md) (DFlash warm-start ablation)

## Open questions and results

- [I-DLM-8B outpaces EAGLE-3 in per-request throughput on Qwen3-8B](../results/i-dlm-vs-eagle-3-throughput.md)
- [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md)

[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
