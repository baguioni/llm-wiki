---
type: Open Question
title: Which SWE-bench Verified scores are comparable?
description: Papers quote the same systems on SWE-bench Verified with different scores and different rollout budgets.
tags: [swe-bench, evaluation, software-engineering-agents]
sources:
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback for Software Engineering Agents"
---

# Which SWE-bench Verified scores are comparable?

## Question

Papers on SWE-bench Verified list each other's systems with different scores, and mix single-attempt scores with scores selected from many rollouts. Which rows can be compared?

## Why it matters

The SOTA entry on [SWE-bench Verified](../benchmarks/swe-bench-verified.md) depends on the budget column. A Best@K score with a verifier is not a pass@1 score.

## Evidence so far

| System | Score | Label in the reporting paper | Reported by |
|---|---|---|---|
| SWE-Gym-32B | 32.0 | listed in a pass@1 table | [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md)[^weiSWERLAdvancingLLM2025] |
| SWE-Gym-32B | 20.6 | Pass@1 | [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md)[^daAgentRLVRTrainingSoftware2025], [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md)[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym-32B | 32.0 | Best@16 | [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md)[^jainR2EGymProceduralEnvironments2025] |
| SWE-Fixer-72B | 32.8 | not stated | [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md)[^weiSWERLAdvancingLLM2025] |
| SWE-Fixer-72B | 30.2 | not stated | [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md)[^daAgentRLVRTrainingSoftware2025] |
| Llama3-SWE-RL-70B | 41.0 | pass@1 after reranking 500 patches | [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md)[^weiSWERLAdvancingLLM2025] |
| Llama3-SWE-RL-70B | 41.0 | Best@500 | [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md)[^jainR2EGymProceduralEnvironments2025] |

## Conflicting claims

- SWE-RL claims the best result among models of at most 100B at 41.0.[^weiSWERLAdvancingLLM2025]
- R2E-Gym reports 51.0 at Best@26 with its hybrid verifier, and 34.4 at Pass@1.[^jainR2EGymProceduralEnvironments2025]
- SWE-RM reports 74.6% at RM@32 with Qwen3-Coder-Max, against 67.0% pass@1 for the same model.[^shumSWERMExecutionfreeFeedback2025]

## What would resolve it

A table that gives, for every system, the model, the scaffold, the number of rollouts, and the selection method (none, tests, execution-free verifier, hybrid). The [SWE-bench Verified](../benchmarks/swe-bench-verified.md) page keeps this budget column.

## Related

- [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [SWE-bench](../benchmarks/swe-bench.md)
- [Test-time scaling](../methods/test-time-scaling.md), [Execution-free verifier](../methods/execution-free-verifier.md), [Agentless](../methods/agentless.md), [OpenHands](../methods/openhands.md)
- [SWE-Gym](../datasets/swe-gym.md), [R2E-Gym](../datasets/r2e-gym.md)

[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
