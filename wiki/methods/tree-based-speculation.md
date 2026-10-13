---
type: Method
title: Tree-based speculation
description: Family of speculative decoding methods in which the drafter proposes a tree of candidate tokens, giving the verifier several options per position, and the target verifies the whole tree in one pass.
tags: [speculative-decoding, tree-based-speculation, draft-tree, token-tree-verification]
sources:
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: svirschevskiSpecExecMassivelyParallel2024
    resource: zotero://select/items/@svirschevskiSpecExecMassivelyParallel2024
    title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: gaoCollaborativeSpeculativeInference
    resource: zotero://select/items/@gaoCollaborativeSpeculativeInference
    title: Collaborative Speculative Inference for Efficient LLM Inference Serving
---

# Tree-based speculation

## Overview

Standard [speculative decoding](../methods/speculative-decoding.md) suffers from exponentially declining acceptance rates as sequence length increases. Tree-based approaches address this by exploring multiple paths simultaneously.[^parkSpecEdgeScalableEdgeAssisted2025] The draft model speculates a tree of tokens instead of a sequence, which gives the verifier several token options at each position and increases the expected number of accepted tokens.[^kumarSpeculativeSpeculativeDecoding2026]

The SuffixDecoding paper credits [SpecInfer](../methods/specinfer.md) with introducing tree-based speculation.[^oliaroSuffixDecodingExtremeSpeculative2024]

## How it works

- A single long draft sequence is truncated as soon as one token is rejected, which wastes most of a large draft budget. A tree shares the budget across multiple stems.[^svirschevskiSpecExecMassivelyParallel2024]
- The target model processes all draft tokens of the tree in parallel with a merged attention mask.[^svirschevskiSpecExecMassivelyParallel2024] The DSpark paper describes this as tree-based verification, which expands candidates into a tree and verifies multiple paths via tree attention.[^chengDSparkConfidenceScheduledSpeculative2026]
- Multiple drafters can generate parallel draft sequences that are merged into a tree topology that preserves causal dependencies based on tree attention.[^gaoCollaborativeSpeculativeInference]

## Variants

| Method | How the tree is built, as stated in the wiki's papers |
|---|---|
| [SpecInfer](../methods/specinfer.md) | Shares a large token budget across multiple stems in a tree, and must sample draft tokens to guarantee correctness.[^svirschevskiSpecExecMassivelyParallel2024] |
| [Sequoia](../methods/sequoia.md) | Fixed (static) tree structures.[^svirschevskiSpecExecMassivelyParallel2024] Prunes unpromising branches.[^parkSpecEdgeScalableEdgeAssisted2025] |
| [SpecExec](../methods/specexec.md) | A deterministic tree of the $K$ tokens with the highest cumulative draft probability, found with a parallel shortest-path search.[^svirschevskiSpecExecMassivelyParallel2024] |
| [EAGLE-3](../methods/eagle-3.md) | Tree drafting configured by draft steps, top-$k$, and draft tree size (7 draft steps, top-$k$ 10, tree size 16 or 60 in the DFlash paper).[^chenDFlashBlockDiffusion2026] |
| SuffixDecoding | A speculation tree grown greedily from a suffix tree, one leaf at a time, up to a size limit `MAX_SPEC`. No draft model is used.[^oliaroSuffixDecodingExtremeSpeculative2024] |
| SpecEdge | A draft tree of size 32 per request, built with the construction from Sequoia and SpecExec, then extended proactively from the single path with the highest cumulative log probability.[^parkSpecEdgeScalableEdgeAssisted2025] |
| CoSine | Draft tokens from multiple drafters are fused by confidence and combined into token trees.[^gaoCollaborativeSpeculativeInference] |

## Papers using it

- **[SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md)** uses server-only tree-based speculative decoding as its primary baseline and tree-based drafting on the edge. With a non-tree (linear-sequence) speculative decoding method, SpecEdge still achieves up to 1.96× higher server throughput and 1.67× better cost efficiency than server-only deployment (Llama2 13B/TL 1.1B).[^parkSpecEdgeScalableEdgeAssisted2025]
- **[SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md)** compares tree speculation with linear speculation, which allows only sequential token chains, using Llama-3.1-8B-Instruct on a single H100 GPU with batch size 1.[^oliaroSuffixDecodingExtremeSpeculative2024]

  | System | AgenticSQL speedup | SWE-Bench speedup | [Spec-Bench](../benchmarks/spec-bench.md) speedup |
  |---|---|---|---|
  | suffix (linear) | 5.345 | 2.452 | 1.659 |
  | suffix (tree) | 5.175 | 2.433 | 1.661 |
  | hybrid (linear) | 3.799 | - | 2.500 |
  | hybrid (tree) | 4.068 | - | 2.458 |

  All rows: [^oliaroSuffixDecodingExtremeSpeculative2024]

- **[SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md)** studies trees of up to 2048 draft tokens. The optimal draft tree size on an A100 with RAM offloading is 128–512 for SpecInfer and 1024–2048 for SpecExec.[^svirschevskiSpecExecMassivelyParallel2024]
- **[Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md)** contrasts itself with tree-based methods, which are still sequential (speculate, then verify), and states that [SSD](../methods/speculative-speculative-decoding.md) can be combined with them by pre-speculating a token tree for each verification outcome instead of a token chain.[^kumarSpeculativeSpeculativeDecoding2026]
- **[DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md)** uses chain-based drafting for all drafters in its offline evaluation.[^chengDSparkConfidenceScheduledSpeculative2026]
- **[DFlash](../papers/chenDFlashBlockDiffusion2026.md)** compares its block drafting against EAGLE-3 with tree sizes 16 and 60. On [SGLang](../methods/sglang.md), Spec-v2 does not support tree-based drafting for EAGLE-3, so that comparison runs with Spec-v1.[^chenDFlashBlockDiffusion2026]
- **[CoSine](../papers/gaoCollaborativeSpeculativeInference.md)** verifies fused token trees from multiple drafters.[^gaoCollaborativeSpeculativeInference]

## Strengths & Limitations

- Speculating a tree instead of a sequence increases the expected number of accepted tokens.[^kumarSpeculativeSpeculativeDecoding2026]
- The entire tree must be verified in the target model forward pass, which adds a large amount of verifier compute.[^kumarSpeculativeSpeculativeDecoding2026]
- The large number of verification tokens reduces overall serving throughput.[^chengDSparkConfidenceScheduledSpeculative2026]
- A larger tree can lose under load. For LLaMA-3.1-8B-Instruct on SGLang with GSM8K, EAGLE-3 with 60 draft tokens goes from 1.9× at concurrency 1 to 0.6× at concurrency 32, while EAGLE-3 with 10 draft tokens goes from 1.6× to 1.0×. The 60-token setting has the higher average $\tau$ (4.55 against 3.49).[^chenDFlashBlockDiffusion2026]
- Tree speculation does not always beat a chain. In the SuffixDecoding results above, suffix (linear) is faster than suffix (tree) on AgenticSQL and SWE-Bench.[^oliaroSuffixDecodingExtremeSpeculative2024]
- Fixed tree structures require tree structure optimization for every change in the text domain, generation parameters, and the hardware setup.[^svirschevskiSpecExecMassivelyParallel2024]

## Related

- [Speculative decoding](../methods/speculative-decoding.md), [SpecInfer](../methods/specinfer.md), [Sequoia](../methods/sequoia.md), [SpecExec](../methods/specexec.md), [EAGLE-3](../methods/eagle-3.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md)
- Benchmarks: [Spec-Bench](../benchmarks/spec-bench.md)

[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^gaoCollaborativeSpeculativeInference]: Gao et al. (year not stated)
