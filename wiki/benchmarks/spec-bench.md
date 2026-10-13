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

### Used as a workload

This paper uses SpecBench prompts to measure a serving system. It does not compare speculative decoding algorithms on the benchmark.

| Paper | What is measured | Setting | Reported numbers |
|---|---|---|---|
| [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md) | Server-side throughput and cost efficiency against a server-only speculative decoding baseline | Six SpecBench tasks, batch size 1, Qwen3 32B/14B targets with Qwen3 1.7B/0.6B drafts, up to 256 output tokens per query | On average 1.91× better cost efficiency through a 2.22× throughput gain[^parkSpecEdgeScalableEdgeAssisted2025] |
| [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md) | Average inter token latency under network round-trip time (RTT) | Qwen3 32B on SpecBench | At 15 ms RTT, 36.47 ms for SpecEdge against 42.36 ms for server-only (a 13.90% gain) and 99.63 ms for layer-split[^parkSpecEdgeScalableEdgeAssisted2025] |

The per-task rows of the SpecEdge table are on the [SpecEdge paper page](../papers/parkSpecEdgeScalableEdgeAssisted2025.md).

### Task selection only

- [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) follows EAGLE and Spec-Bench in evaluating on five common tasks: multi-turn conversation ([MT-bench](../datasets/mt-bench.md)), code generation ([HumanEval](../datasets/humaneval.md)), mathematical reasoning ([GSM8K](../datasets/gsm8k.md)), instruction following ([Alpaca](../datasets/alpaca.md)), and summarization ([CNN/Daily Mail](../datasets/cnn-dailymail.md)). It reports results per dataset and gives no Spec-Bench score.[^liEAGLE3ScalingInference2025]

## Current SOTA

Among the wiki's papers, the best overall speedup on Spec-Bench is 2.500× for hybrid (linear) SuffixDecoding + EAGLE-3, with Llama-3.1-8B-Instruct on one H100 GPU at batch size 1.[^oliaroSuffixDecodingExtremeSpeculative2024]

## Superseded claims

- **Superseded.** Oliaro et al. call EAGLE-2 and EAGLE-3 state-of-the-art model-based speculators. Standalone EAGLE-3 reaches 2.367× on Spec-Bench, and the hybrid of SuffixDecoding and EAGLE-3 in the same paper reaches 2.500×.[^oliaroSuffixDecodingExtremeSpeculative2024]

Only one paper in the wiki reports Spec-Bench speedups, so no claim is superseded across papers.

## Caveats

- The EAGLE-3 numbers here are measured by Oliaro et al. through the Spec-Bench codebase on Llama-3.1-8B-Instruct. They are not numbers from the EAGLE-3 paper.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The best row is a hybrid that contains EAGLE-3, so it is not an independent method.[^oliaroSuffixDecodingExtremeSpeculative2024]
- The Spec-Bench "Time per output token" table in the source has no eagle3 row.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Oliaro et al. include Spec-Bench to stress-test SuffixDecoding's limitations and to evaluate the hybrid fallback mechanism. Their main targets are agentic workloads.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Task count. Oliaro et al. state 13 categories, and Park et al. state six tasks.[^oliaroSuffixDecodingExtremeSpeculative2024][^parkSpecEdgeScalableEdgeAssisted2025] The sources do not explain the difference. The SpecEdge table names its tasks as Multi-turn bench, Translation, Summarization, QA, Math, and RAG.[^parkSpecEdgeScalableEdgeAssisted2025]
- The SpecEdge rows are throughput, cost, and latency measurements with different models and hardware. They are not comparable with the speedup rows.[^parkSpecEdgeScalableEdgeAssisted2025]

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE](../methods/eagle.md), [EAGLE-2](../methods/eagle-2.md), [EAGLE-3](../methods/eagle-3.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- Datasets: [MT-Bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md), [Alpaca](../datasets/alpaca.md), [CNN/Daily Mail](../datasets/cnn-dailymail.md)
- Other workloads in Oliaro et al.: [SWE-Bench](swe-bench.md)
- Papers: [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md), [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md), [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md)

[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^liEAGLE3ScalingInference2025]: Li et al. 2025
