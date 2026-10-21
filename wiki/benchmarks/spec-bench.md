---
type: Benchmark
title: Spec-Bench
description: Benchmark and codebase for comparing speculative decoding methods by speedup over vanilla decoding across 13 task categories.
tags: [speculative-decoding, benchmark, inference, llm-serving]
sources:
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
  - id: minitron-pard-qwen3-14b
    resource: raw/experiments/minitron-pard-qwen3-14b.md
    title: "Minitron one-shot pruning of Qwen3-14B to the Qwen3-0.6B shape, chat-KD recovery, then PARD-1"
  - id: drafter-evaluation-server-only-chain
    resource: raw/experiments/drafter-evaluation-server-only-chain.md
    title: "Drafter evaluation, server-only chain7: all six drafters in PyTorch on the GB10 (no phone)"
---

# Spec-Bench

The papers write the name as Spec-Bench or SpecBench and cite it as Xia et al. 2024.[^oliaroSuffixDecodingExtremeSpeculative2024][^parkSpecEdgeScalableEdgeAssisted2025]

## Setup

- **Task.** Open-ended, single-turn tasks across 13 categories, including 8 [MT-Bench](../datasets/mt-bench.md) categories (Writing, Roleplay, Reasoning, Math, Coding, Extraction, STEM, Humanities). Oliaro et al. treat it as a non-agentic workload.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The appendix of Oliaro et al. describes the 13 categories as single-turn open-ended tasks (qa, rag, math\_reasoning, summarization, translation) and multi-turn tasks, with the eight MT-Bench categories.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Park et al. describe SpecBench as spanning six different tasks.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Metric in Oliaro et al.** Speedup, measured as the ratio of wall-clock time-per-output-token relative to vanilla decoding, and mean accepted tokens per step.[^oliaroSuffixDecodingExtremeSpeculative2024]
- **Protocol in Oliaro et al.** The Spec-Bench codebase from the original repository, updated to work with the latest version of the transformers library. Llama-3.1-8B-Instruct on a single H100 GPU with batch size 1, as in the original SpecBench code.[^oliaroSuffixDecodingExtremeSpeculative2024]

## Results

"Overall" column of the Spec-Bench tables in Appendix A.1 of Oliaro et al. All rows use Llama-3.1-8B-Instruct, one H100 GPU, and batch size 1.[^oliaroSuffixDecodingExtremeSpeculative2024]

| System | Speedup over vanilla decoding | Mean accepted tokens (tokens/step) | Time per output token (ms) | Reported by |
|---|---|---|---|---|
| hybrid (linear): SuffixDecoding + EAGLE-3 | 2.500 | 4.553 | 10.747 | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |
| hybrid (tree): SuffixDecoding + EAGLE-3 | 2.458 | 4.684 | 11.153 | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |
| eagle3 ([EAGLE-3](../methods/eagle-3.md)) | 2.367 | 4.647 | not in the source table | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |
| recycling (Token Recycling) | 2.169 | 2.548 | 11.947 | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |
| eagle2 ([EAGLE-2](../methods/eagle-2.md)) | 1.825 | 3.466 | 14.387 | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |
| eagle (row label as in the source) | 1.752 | 3.065 | 14.925 | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |
| suffix (tree): SuffixDecoding | 1.661 | 1.750 | 16.875 | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |
| suffix (linear): SuffixDecoding | 1.659 | 1.766 | 16.936 | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |
| pld (Prompt-Lookup Decoding) | 1.448 | 1.606 | 19.190 | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |
| vanilla | 1.000 | 1.000 | 25.076 | [Oliaro et al. 2024](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) |

All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

- The main text gives the same result in rounded form: the hybrid obtains a mean speedup of $2.5\times$ over vanilla decoding, against $2.4\times$ for standalone EAGLE-3 and $2.2\times$ for Token Recycling.[^oliaroSuffixDecodingExtremeSpeculative2024]
- On Spec-Bench, SuffixDecoding alone is outperformed by EAGLE-2/3 and Token Recycling, which the authors expect for less repetitive scenarios.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Hybrid fallback threshold: $\tau\in[5,7]$ produces the highest overall speedups, and the table of thresholds gives 2.50 overall at $\tau=7$ and 1.66 at $\tau=0$ (suffix only).[^oliaroSuffixDecodingExtremeSpeculative2024]
- The per-category values are on the [SuffixDecoding paper page](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md).

### PARD on vLLM

[PARD](../papers/anPARDAcceleratingLLM2025.md) reports SpecBench as one column of its main table, measured on vLLM with one A100-40GB. Each cell is tokens/s / speedup over autoregressive decoding on vLLM. The temperature is not stated.[^anPARDAcceleratingLLM2025]

| Target | AR | VSD | EAGLE | [EAGLE-3](../methods/eagle-3.md) | [PARD](../methods/pard.md) |
|---|---|---|---|---|---|
| LLaMA3.1-8B | 72.70 / 1.00 | 106.44 / 1.46 | 100.11 / 1.38 | 155.58 / 2.14 | 157.49 / 2.17 |
| LLaMA3.3-70B | 23.95 / 1.00 | 53.09 / 2.22 | not reported | 63.14 / 2.64 | 57.41 / 2.40 |

All rows: [^anPARDAcceleratingLLM2025]

PARD's SpecBench speedup is lower than its HumanEval and GSM8K speedups on every target in its Table 1, from 1.56 (Qwen2.5-3B) to 2.40 (LLaMA3.3-70B).[^anPARDAcceleratingLLM2025]

### Used as a workload

This paper uses SpecBench prompts to measure a serving system. It does not compare speculative decoding algorithms on the benchmark.

| Paper | What is measured | Setting | Reported numbers |
|---|---|---|---|
| [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md) | Server-side throughput and cost efficiency against a server-only speculative decoding baseline | Six SpecBench tasks, batch size 1, Qwen3 32B/14B targets with Qwen3 1.7B/0.6B drafts, up to 256 output tokens per query | On average 1.91× better cost efficiency through a 2.22× throughput gain[^parkSpecEdgeScalableEdgeAssisted2025] |
| [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md) | Average inter token latency under network round-trip time (RTT) | Qwen3 32B on SpecBench | At 15 ms RTT, 36.47 ms for SpecEdge against 42.36 ms for server-only (a 13.90% gain) and 99.63 ms for layer-split[^parkSpecEdgeScalableEdgeAssisted2025] |
| [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md) | TTFT and TBT of device-cloud split inference with speculative decoding | Vicuna-7B, 30 Jetson devices on WiFi, cloud with 8 A6000 GPUs; prompts average 351.2 tokens | At 6 requests/s, TTFT 384.2 ms for HAT against 609.2 ms (U-Sarathi), 644.6 ms (U-Medusa), and 646.2 ms (U-shape). Speculative decoding alone: accept length 2.06 and 1.65× decoding speedup over U-shape[^xieNovelHatShapedDeviceCloud2025] |
| [HyCo](../papers/baeHyCoHybridDrafting2026.md) | Server GPU time per output token ($\Delta g$) against server-side MTP self-speculation, MAT, and delivery speed on the phone | All 480 questions (SB-480) incl. both MT-bench turns, 1,024-token cap; Gemma 4 26B-A4B on one RTX PRO 6000, drafters on a Galaxy S26 Ultra over LTE/5G; temperature 1 | HyCo: $\Delta g$ −38.6 ± 0.2%, MAT 4.71, 35.0 ± 0.7 tokens/s; SpecEdge-style: −20.6%, 3.53, 16.1; HyCo exact: −27.7%, 3.84, 28.2[^baeHyCoHybridDrafting2026] |

The per-task rows of the SpecEdge table are on the [SpecEdge paper page](../papers/parkSpecEdgeScalableEdgeAssisted2025.md). All HyCo configurations are on the [HyCo paper page](../papers/baeHyCoHybridDrafting2026.md). HyCo also scores first-turn answers with a GPT-5.4 judge: 90.34 ± 0.50 for HyCo against 90.15 for Cloud+MTP.[^baeHyCoHybridDrafting2026]

[My drafter evaluation](../experiments/drafter-evaluation-qwen3-14b.md) uses every 8th of 480 Spec-Bench prompts (60 requests: MT-Bench, translation, summarization, qa, math_reasoning, rag, 10 each) to compare six phone drafters for a Qwen3-14B server verifier. It reports tok/s, not speedup over vanilla decoding, so it has no row in the results table. The best drafter reaches 30.0 tok/s (PARD-2, budget-32 tree).[^drafter-evaluation] Its server-only counterpart, [Six drafters on the server GPU, chain7, no phone](../experiments/server-only-chain-drafter-evaluation.md), runs the same 60 requests with all six drafters on the server GPU; the best chain reaches 34.0 tok/s (PARD-2).[^drafter-evaluation-server-only-chain]

[Pruning Qwen3-14B into a PARD-1 drafter](../experiments/minitron-pard-qwen3-14b.md) scores PARD-1 drafters offline on all 480 questions against stored Qwen3-14B greedy references (greedy MAT, no wall-clock). The released `amd/PARD-Qwen3-0.6B` reaches MAT 3.07 at K=8 and 3.15 at K=16, and a drafter pruned from Qwen3-14B 1.96 at K=8.[^minitron-pard-qwen3-14b] The report notes that the PARD paper's Qwen3-14B K=16 τ of 5.14 averages HumanEval, GSM8K, MATH-500, and MT-Bench, while Spec-Bench adds translation, summarization, QA, and RAG, so lower numbers are expected.[^minitron-pard-qwen3-14b]

### Task selection only

- [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) follows EAGLE and Spec-Bench in evaluating on five common tasks: multi-turn conversation ([MT-bench](../datasets/mt-bench.md)), code generation ([HumanEval](../datasets/humaneval.md)), mathematical reasoning ([GSM8K](../datasets/gsm8k.md)), instruction following ([Alpaca](../datasets/alpaca.md)), and summarization ([CNN/Daily Mail](../datasets/cnn-dailymail.md)). It reports results per dataset and gives no Spec-Bench score.[^liEAGLE3ScalingInference2025]

## Current SOTA

Among the wiki's papers, the best overall speedup on Spec-Bench is 2.500× for hybrid (linear) SuffixDecoding + EAGLE-3, with Llama-3.1-8B-Instruct on one H100 GPU at batch size 1.[^oliaroSuffixDecodingExtremeSpeculative2024]

## Superseded claims

- **Superseded.** Oliaro et al. call EAGLE-2 and EAGLE-3 state-of-the-art model-based speculators. Standalone EAGLE-3 reaches 2.367× on Spec-Bench, and the hybrid of SuffixDecoding and EAGLE-3 in the same paper reaches 2.500×.[^oliaroSuffixDecodingExtremeSpeculative2024]

Two papers in the wiki report Spec-Bench speedups over autoregressive decoding. On the same target, PARD's best (2.17 on vLLM) is below the 2.500× of SuffixDecoding's hybrid, so no claim is superseded across papers.[^anPARDAcceleratingLLM2025][^oliaroSuffixDecodingExtremeSpeculative2024]

## Caveats

- The EAGLE-3 numbers here are measured by Oliaro et al. through the Spec-Bench codebase on Llama-3.1-8B-Instruct. They are not numbers from the EAGLE-3 paper.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The best row is a hybrid that contains EAGLE-3, so it is not an independent method.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The Spec-Bench "Time per output token" table in the source has no eagle3 row.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Oliaro et al. include Spec-Bench to stress-test SuffixDecoding's limitations and to evaluate the hybrid fallback mechanism. Their main targets are agentic workloads.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Task count. Oliaro et al. state 13 categories, and Park et al. state six tasks.[^oliaroSuffixDecodingExtremeSpeculative2024][^parkSpecEdgeScalableEdgeAssisted2025] The sources do not explain the difference. The SpecEdge table names its tasks as Multi-turn bench, Translation, Summarization, QA, Math, and RAG.[^parkSpecEdgeScalableEdgeAssisted2025]
- The SpecEdge rows are throughput, cost, and latency measurements with different models and hardware. They are not comparable with the speedup rows.[^parkSpecEdgeScalableEdgeAssisted2025]
- PARD's speedups are against autoregressive decoding on vLLM, while Oliaro et al. use the Spec-Bench codebase on transformers. PARD reports that relative speedups differ by framework: on LLaMA3.1-8B, vanilla SD averages 1.36 under Transformers against 2.02 on vLLM (HumanEval and GSM8K).[^anPARDAcceleratingLLM2025] The two sets of numbers are not directly comparable.
- HyCo reports server GPU time and delivery speed against server-side MTP self-speculation, not speedup over vanilla decoding, so it has no row in the results table. Its default acceptance rule is lossy.[^baeHyCoHybridDrafting2026] HyCo describes Spec-Bench's tasks as MT-bench, translation (WMT14), summarization (CNN/DailyMail), QA (Natural Questions), RAG (DPR passages), and math (GSM8K), and its task-wise quality contrasts use 80 questions per task (78 for summarization).[^baeHyCoHybridDrafting2026]
- HAT's speedup is over U-shaped split inference without speculation, not over autoregressive decoding on one machine.[^xieNovelHatShapedDeviceCloud2025]

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE](../methods/eagle.md), [EAGLE-2](../methods/eagle-2.md), [EAGLE-3](../methods/eagle-3.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- Datasets: [MT-Bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [Alpaca](../datasets/alpaca.md), [CNN/Daily Mail](../datasets/cnn-dailymail.md)
- Other workloads in Oliaro et al.: [SWE-Bench](swe-bench.md)
- Papers: [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md), [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md), [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md), [PARD](../papers/anPARDAcceleratingLLM2025.md), [HAT](../papers/xieNovelHatShapedDeviceCloud2025.md), [HyCo](../papers/baeHyCoHybridDrafting2026.md)

[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
[^minitron-pard-qwen3-14b]: My Minitron pruning, chat-KD recovery, and PARD-1 report, runs of 2026-10-17/19
[^drafter-evaluation-server-only-chain]: My server-only chain7 drafter evaluation report, runs of 2026-10-19
