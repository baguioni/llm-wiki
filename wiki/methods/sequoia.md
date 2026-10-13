---
type: Method
title: Sequoia
description: Tree-based speculative decoding method that the wiki's papers describe as using fixed (static) draft tree structures and pruning unpromising branches, used as a comparison point and as a source of tree construction.
tags: [speculative-decoding, tree-based-speculation, draft-tree, baseline]
sources:
  - id: svirschevskiSpecExecMassivelyParallel2024
    resource: zotero://select/items/@svirschevskiSpecExecMassivelyParallel2024
    title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
---

# Sequoia

## Overview

Sequoia is a [tree-based](../methods/tree-based-speculation.md) [speculative decoding](../methods/speculative-decoding.md) method by Chen et al., cited by the wiki's papers as "Sequoia: Scalable, robust, and hardware-aware speculative decoding".[^svirschevskiSpecExecMassivelyParallel2024][^parkSpecEdgeScalableEdgeAssisted2025] The wiki has no paper page for Sequoia itself, so this page records only what the two citing papers say.

- The SpecExec paper describes Sequoia as a speculative decoding method using fixed trees.[^svirschevskiSpecExecMassivelyParallel2024]
- The SpecEdge paper states that Sequoia and [SpecExec](../methods/specexec.md) further optimize tree-based approaches by pruning unpromising branches.[^parkSpecEdgeScalableEdgeAssisted2025]

## How it works

The wiki's papers do not describe the Sequoia algorithm itself. The SpecEdge paper describes the tree construction it adopts from Sequoia and SpecExec: given a specified tree size, each forward pass of the draft model generates multiple parallel candidate tokens, which are then pruned based on cumulative log probabilities so that the total number of tokens remains within the tree budget. The total number of forward passes (the draft tree depth) is set as a hyperparameter.[^parkSpecEdgeScalableEdgeAssisted2025]

## Papers using it

- **[SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md)** compares against it in one setup. The paper states that Sequoia attains 2.2 tokens per second in the Llama 3-8B/70B setup, compared to 2.8 tokens per second for SpecExec. The sentence follows the paper's tables for RAM offloading on an A100 GPU, where SpecExec with Llama 3-8B / 70B reaches 2.79 tok/s on MTBench at t=0.6. The Sequoia figure is cited from Sequoia's project page. The paper's own tables have no Sequoia row, and it does not state the hardware behind the Sequoia figure.[^svirschevskiSpecExecMassivelyParallel2024]
- The SpecExec paper also cites the Sequoia paper, as concurrent work, for the finding that speculative decoding algorithms with single or multiple sequences, like [SpecInfer](../methods/specinfer.md), are effectively upper-bounded in the number of accepted tokens as the speculation budget grows.[^svirschevskiSpecExecMassivelyParallel2024]
- **[SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md)** adopts a tree construction algorithm from Sequoia and SpecExec for both SpecEdge and its server-only speculative decoding baseline, with draft tree size 32 for each request. It reports no separate Sequoia result.[^parkSpecEdgeScalableEdgeAssisted2025]

## Strengths & Limitations

- The SpecExec paper names Sequoia as a method that scales better with more draft tokens than earlier speculative decoding approaches.[^svirschevskiSpecExecMassivelyParallel2024]
- The same paper states that such methods rely on static tree structures that may not be optimal for every setting, because they require tree structure optimization for every change in the text domain, generation parameters, and the hardware setup.[^svirschevskiSpecExecMassivelyParallel2024]

## Related

- [Tree-based speculation](../methods/tree-based-speculation.md), [SpecExec](../methods/specexec.md), [SpecInfer](../methods/specinfer.md), [Speculative decoding](../methods/speculative-decoding.md)
- Papers: [SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md), [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md)

[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
