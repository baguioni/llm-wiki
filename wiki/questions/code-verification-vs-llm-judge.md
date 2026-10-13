---
type: Open Question
title: Should agent training environments verify tasks with code or with an LLM judge?
description: VeriEnv argues for deterministic code validators and Agent World Model argues that code-only verification is brittle.
tags: [agent-training, evaluation, reward]
sources:
  - id: chaeSafeScalableWeb2026
    resource: zotero://select/items/@chaeSafeScalableWeb2026
    title: Safe and Scalable Web Agent Learning via Recreated Websites
  - id: wangAgentWorldModel2026
    resource: zotero://select/items/@wangAgentWorldModel2026
    title: "Agent World Model: Infinity Synthetic Environments for Agentic Reinforcement Learning"
---

# Should agent training environments verify tasks with code or with an LLM judge?

## Question

For synthetic agent-training environments, is a code-based task validator or an LLM judge the more reliable reward signal?

## Why it matters

The reward signal decides which trajectories are kept for training. Both papers train agents on the result.

## Conflicting claims

- [VeriEnv](../papers/chaeSafeScalableWeb2026.md) uses executable validators and reports 76% judge correctness and 90% task executability in its human evaluation.[^chaeSafeScalableWeb2026]
- [Agent World Model](../papers/wangAgentWorldModel2026.md) reports that its code-augmented LLM judge scores above code-only verification, for example 64.50 against 55.66 on BFCLv3 at 4B.[^wangAgentWorldModel2026]

The settings differ: recreated websites in VeriEnv, synthetic database-backed tool environments in Agent World Model. Neither paper tests the other's method.

## What would resolve it

Both verification methods applied to the same environments, with human labels for reward correctness and the downstream benchmark score of the trained agent.

## Related

- [LLM-as-a-judge](../methods/llm-as-a-judge.md)
- [BFCL](../benchmarks/bfcl.md), [WebArena-Lite](../benchmarks/webarena-lite.md)

[^chaeSafeScalableWeb2026]: Chae et al. 2026
[^wangAgentWorldModel2026]: Wang et al. 2026
