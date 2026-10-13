---
type: Method
title: EAGLE-2
description: Successor of EAGLE that builds a context-aware dynamic draft tree from the draft model's confidence; the direct baseline of EAGLE-3.
tags: [speculative-decoding, draft-tree, dynamic-draft-tree, llm-inference, baseline]
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: gaoCollaborativeSpeculativeInference
    resource: zotero://select/items/@gaoCollaborativeSpeculativeInference
    title: Collaborative Speculative Inference for Efficient LLM Inference Serving
---

# EAGLE-2

## Overview

EAGLE-2 is the successor of [EAGLE](../methods/eagle.md). It approximates the acceptance rate with the confidence of the draft model, generates the draft tree dynamically from it, and prunes the draft tree at the end of the drafting stage.[^liEAGLE3ScalingInference2025] The wiki has no Paper page for EAGLE-2 itself. Everything here comes from papers that describe it or measure it as a baseline.

## How it works

- EAGLE and [Medusa](../methods/medusa.md) use tree-shaped drafts whose structure is predefined, static, and context-independent. The difficulty of drafting is closely related to the context, so a static draft tree can waste resources. EAGLE-2 makes the tree context-aware.[^liEAGLE3ScalingInference2025]
- SpecForge describes EAGLE-2 as dynamically shaping the draft tree according to token-level confidence, which allocates verification compute to the most promising candidates.[^liSpecForgeFlexibleEfficient2026]
- Settings used in the EAGLE-3 paper: total draft tokens 60, 50, and 48 for the 7B (8B), 13B, and 70B LLMs, a draft tree depth of 6, and 10 nodes selected during the expansion phase.[^liEAGLE3ScalingInference2025]

## Papers using it

### EAGLE-3 paper (Li et al. 2025)

EAGLE-2 is the main baseline, and [EAGLE-3](../methods/eagle-3.md) adopts its dynamic draft tree. Speedup over vanilla autoregressive decoding / average acceptance length $\tau$. V = Vicuna, L31 = LLaMA-Instruct 3.1, L33 = LLaMA-Instruct 3.3, DSL = DeepSeek-R1-Distill-LLaMA.[^liEAGLE3ScalingInference2025]

| Model | Temp. | MT-bench | HumanEval | GSM8K | Alpaca | CNN/DM | Mean |
|---|---|---|---|---|---|---|---|
| V 13B | 0 | 4.26x / 4.83 | 4.96x / 5.41 | 4.22x / 4.79 | 4.25x / 4.89 | 3.40x / 4.21 | 4.22x / 4.83 |
| L31 8B | 0 | 3.16x / 4.05 | 3.66x / 4.71 | 3.39x / 4.24 | 3.28x / 4.12 | 2.65x / 3.45 | 3.23x / 4.11 |
| L33 70B | 0 | 2.83x / 3.67 | 3.12x / 4.09 | 2.83x / 3.69 | 3.03x / 3.92 | 2.44x / 3.55 | 2.85x / 3.78 |
| DSL 8B | 0 | 2.92x / 3.80 | 3.42x / 4.29 | 3.40x / 4.40 | 3.01x / 3.80 | 3.53x / 3.33 | 3.26x / 3.92 |
| V 13B | 1 | 3.80x / 4.40 | 4.22x / 4.89 | 3.77x / 4.41 | 3.78x / 4.37 | 3.25x / 3.97 | 3.76x / 4.41 |
| L31 8B | 1 | 2.44x / 3.16 | 3.39x / 4.39 | 2.86x / 3.74 | 2.83x / 3.65 | 2.44x / 3.14 | 2.80x / 3.62 |
| L33 70B | 1 | 2.73x / 3.51 | 2.89x / 3.81 | 2.52x / 3.36 | 2.77x / 3.73 | 2.32x / 3.27 | 2.65x / 3.54 |
| DSL 8B | 1 | 2.69x / 3.41 | 3.01x / 3.82 | 3.16x / 4.05 | 2.64x / 3.29 | 2.35x / 3.13 | 2.77x / 3.54 |

All rows: [^liEAGLE3ScalingInference2025]

- The paper summarizes EAGLE-3 as a 20%-40% improvement over EAGLE-2, or about 1.4x.[^liEAGLE3ScalingInference2025]
- Starting from EAGLE-2 on L31 8B (3.16x / 4.05 on MT-bench, 3.39x / 4.24 on GSM8K), removing the feature prediction constraint gives 3.82x / 5.37 and 3.77x / 5.22, and adding fused features gives 4.40x / 6.13 and 4.48x / 6.23.[^liEAGLE3ScalingInference2025]
- In [SGLang](../methods/sglang.md) at batch size 1 on one H100 with L31 8B on MT-Bench, SGLang + EAGLE-2 reaches 244.10 tokens/s against 158.34 tokens/s without speculation and 373.25 tokens/s with EAGLE-3.[^liEAGLE3ScalingInference2025]

### SuffixDecoding (Oliaro et al. 2024)

EAGLE-2 is a baseline run through the Spec-Bench codebase with Llama-3.1-8B-Instruct on a single H100 GPU at batch size 1.[^oliaroSuffixDecodingExtremeSpeculative2024]

| Workload | Speedup over vanilla | Mean accepted tokens (tokens/step) | Time per output token (ms) | Speculation time per generated token (ms) | Mean acceptance rate |
|---|---|---|---|---|---|
| [Spec-Bench](../benchmarks/spec-bench.md) | 1.825 | 3.466 | 14.387 | 2.936 | 0.041 |
| AgenticSQL | 1.864 | 3.572 | 14.677 | 3.487 | 0.043 |

All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

- AgenticSQL per-task speedups for eagle2 range from 1.527 (SQL1 and SQL3) to 2.751 (Extract).[^oliaroSuffixDecodingExtremeSpeculative2024]
- EAGLE-2/3 failed to run on several SWE-Bench tasks due to long context lengths (>8192 tokens).[^oliaroSuffixDecodingExtremeSpeculative2024]
- The paper reports that SuffixDecoding is up to 2.8× faster than EAGLE-2/3 on AgenticSQL.[^oliaroSuffixDecodingExtremeSpeculative2024]

### CoSine (Gao et al.)

CoSine mentions EAGLE2 in related work, next to OPT-Tree, as a method that explores draft structures. It does not benchmark it.[^gaoCollaborativeSpeculativeInference]

## Strengths & Limitations

- Strength: on Vicuna 13B at temperature 0 the mean speedup is 4.22x against 3.05x for EAGLE.[^liEAGLE3ScalingInference2025]
- Limitation: it keeps EAGLE's feature prediction, which the EAGLE-3 paper identifies as the constraint that limits gains from more training data.[^liEAGLE3ScalingInference2025]
- Limitation: on the repetitive AgenticSQL workload its speedup (1.864) is below the model-free Token Recycling (2.710) and SuffixDecoding (5.345 for suffix (linear)).[^oliaroSuffixDecodingExtremeSpeculative2024]

# Contradictions

1. **EAGLE-2 vs EAGLE-3 ordering.** The EAGLE-3 paper states that EAGLE-3 achieves the highest speedup ratio on all tasks and target models.[^liEAGLE3ScalingInference2025] SuffixDecoding measures eagle2 above eagle3 on AgenticSQL (1.864 vs 1.623 overall), and eagle3 above eagle2 on Spec-Bench (2.367 vs 1.825).[^oliaroSuffixDecodingExtremeSpeculative2024] AgenticSQL is a proprietary agentic workload outside the EAGLE-3 paper's task set. The EAGLE-3 paper's own table also has one cell where EAGLE-2 is ahead: DSL 8B on CNN/DM at temperature 0, 3.53x for EAGLE-2 against 3.52x for EAGLE-3.[^liEAGLE3ScalingInference2025]

2. **Size of the speedup on LLaMA-3.1-8B.** The EAGLE-3 paper reports a mean of 3.23x with $\tau$ 4.11 for EAGLE-2 on L31 8B at temperature 0 over five tasks.[^liEAGLE3ScalingInference2025] SuffixDecoding reports an overall 1.825 with 3.466 mean accepted tokens on Spec-Bench for Llama-3.1-8B-Instruct.[^oliaroSuffixDecodingExtremeSpeculative2024] The task sets differ (five datasets vs 13 Spec-Bench categories), SuffixDecoding runs on a single H100 through the Spec-Bench codebase, and the EAGLE-3 paper does not state its hardware.

3. **Inside SuffixDecoding.** The text gives the AgenticSQL speedup of standalone EAGLE-2/3 as $1.9\times$, while the appendix table lists eagle2 at 1.864 and eagle3 at 1.623.[^oliaroSuffixDecodingExtremeSpeculative2024]

## Related

- Predecessor and successor: [EAGLE](../methods/eagle.md), [EAGLE-3](../methods/eagle-3.md)
- Parent concept: [Speculative decoding](../methods/speculative-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md)
- Benchmarks and datasets: [Spec-Bench](../benchmarks/spec-bench.md), [MT-Bench](../datasets/mt-bench.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^gaoCollaborativeSpeculativeInference]: Gao et al. (year not stated)
