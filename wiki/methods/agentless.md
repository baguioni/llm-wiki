---
type: Method
title: Agentless
description: Pipeline-based, non-agent scaffold for SWE-bench issue resolution with localization, repair, and test-based patch selection steps, used as a baseline scaffold and as a base for simplified variants.
tags: [swe-agents, pipeline-scaffold, issue-resolution, patch-selection, execution-based-verifier]
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
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
---

# Agentless

## Overview

No paper in this wiki introduces Agentless. This page records what the papers that build on it or compare against it state.

Agentless is a scaffold for [SWE-bench](../benchmarks/swe-bench.md) that takes a multi-step approach with localization, repair, and validation steps.[^daAgentRLVRTrainingSoftware2025] It is a non-agent scaffold: single-turn and pipeline-based, in contrast to agent scaffolds such as [OpenHands](openhands.md) and [SWE-agent](swe-agent.md), which let the model interact with a sandbox over multiple turns.[^shumSWERMExecutionfreeFeedback2025] SWE-RL calls it one of the state-of-the-art scaffolds for SWE-bench at the time of writing, and Agent-RLVR picks it for its popularity and maturity.[^weiSWERLAdvancingLLM2025][^daAgentRLVRTrainingSoftware2025]

## How it works

The steps below are as SWE-RL describes them when it contrasts Agentless with its own Agentless Mini.[^weiSWERLAdvancingLLM2025]

- **Localization.** Multi-step. Beyond predicting files, Agentless has two additional detailed steps to identify related elements and files, and it uses a separate embedding model.[^weiSWERLAdvancingLLM2025]
- **Reproduction tests.** Multiple reproduction tests are generated from the issue description. The tests must print "Issue reproduced" or "Issue resolved" with distinct logic, they are filtered by whether they print "Issue reproduced" on the original codebase, and one majority sample is selected.[^weiSWERLAdvancingLLM2025]
- **Regression tests.** All tests that pass before any modification are gathered. An optional inference step filters out passing tests that should fail after the fix.[^weiSWERLAdvancingLLM2025]
- **Patch selection.** Agentless uses one reproduction test per issue for reranking.[^weiSWERLAdvancingLLM2025] SWE-RM summarizes the Agentless verifier as an execution-based method that generates reproduction tests for each trajectory and re-ranks by the number of passed tests.[^shumSWERMExecutionfreeFeedback2025]

## Variants

- **Agentless vs. Agentless-1.5.** R2E-Gym states that Agentless used majority voting to select the best patch, and that Agentless-1.5 relied on reproduction and regression tests to verify generated patches.[^jainR2EGymProceduralEnvironments2025]
- **Agentless Mini (SWE-RL).** Built on Agentless. It keeps only file-level localization and gives the repair step the entire file contents, it needs no embedding model, and it can use multiple reproduction tests chosen by voting, where Agentless uses one.[^weiSWERLAdvancingLLM2025]
- **Agent-RLVR scaffold.** Based on Agentless with only the localization and repair steps. The patch selection step, which needs test generation and execution, is removed, which the authors say makes the scaffold significantly simpler, faster, and less compute intensive.[^daAgentRLVRTrainingSoftware2025]

## Papers using it

### Reported SWE-Bench Verified scores with an Agentless scaffold

Scores on [SWE-Bench Verified](../benchmarks/swe-bench-verified.md), as each paper prints them.

| Scaffold as labeled | Model | Score | Reported by |
|---|---|---|---|
| Agentless | GPT-4o | 38.8 | [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md)[^weiSWERLAdvancingLLM2025] |
| Agentless | GPT-4o | 38.8% | [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md)[^daAgentRLVRTrainingSoftware2025] |
| Agentless-1.5 | GPT-4o | 34.0 | [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md)[^jainR2EGymProceduralEnvironments2025] |
| Agentless | o1-preview | 41.3 | SWE-RL[^weiSWERLAdvancingLLM2025] |
| Agentless | O1 | 48.0 | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| Agentless | DeepSeek-V3 | 42.0 | SWE-RL[^weiSWERLAdvancingLLM2025] |
| Agentless | DeepSeek-V3 | 42.0% | Agent-RLVR[^daAgentRLVRTrainingSoftware2025] |
| Agentless | DeepSeek-R1 | 49.2 | SWE-RL[^weiSWERLAdvancingLLM2025] |
| Agentless | DeepSeek-R1 | 49.2% | Agent-RLVR[^daAgentRLVRTrainingSoftware2025] |
| Agentless | DeepSeek-R1 | 49.2 | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| Agentless | Claude-3.5-Sonnet | 50.8 | SWE-RL[^weiSWERLAdvancingLLM2025] |
| Agentless | Claude-3.5-Sonnet | 50.8% | Agent-RLVR[^daAgentRLVRTrainingSoftware2025] |
| Agentless-1.5 | Claude-3.6-Sonnet | 50.8 | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| Agentless Mini | Llama3-SWE-SFT-70B | 36.2 | SWE-RL[^weiSWERLAdvancingLLM2025] |
| Agentless Mini | Llama3-SWE-RL-70B | 41.0 | SWE-RL[^weiSWERLAdvancingLLM2025] |
| Agentless (as labeled by Agent-RLVR) | Llama3-SWE-RL-70B | 41.0% | Agent-RLVR[^daAgentRLVRTrainingSoftware2025] |
| Agentless-based, localization and repair only | Agent-RLVR-Qwen-2.5-72B-Instruct | 22.4% | Agent-RLVR[^daAgentRLVRTrainingSoftware2025] |
| Agentless-based, with a reward model ranking $k=32$ patches | Agent-RLVR-RM-Qwen-2.5-72B-Instruct | 27.8% | Agent-RLVR[^daAgentRLVRTrainingSoftware2025] |

### How each paper uses it

- [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md) builds Agentless Mini on Agentless and evaluates Llama3-SWE-RL-70B with it: 500 patches per problem at temperature 1.0, the top 30 reproduction tests for reranking, and one submitted patch per issue (41.0).[^weiSWERLAdvancingLLM2025]
- [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md) uses its reduced Agentless scaffold for both training rollouts and evaluation.[^daAgentRLVRTrainingSoftware2025]
- [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md) follows Agentless in using existing regression tests to filter patches, and uses an Agentless-like reproduction test generation approach when it creates environments.[^jainR2EGymProceduralEnvironments2025] It contrasts its testing agent, which interacts with the environment, with zero-shot test generation in Agentless.[^jainR2EGymProceduralEnvironments2025] In its hybrid verifier, replacing its agent-generated tests with the official Agentless tests lowers the SWE-Bench Verified result from 51.0% to 48.8%.[^jainR2EGymProceduralEnvironments2025]
- [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md) uses Agentless as an execution-based verifier baseline. Its RM@32 is 42.4% on OpenHands-LM-32B trajectories, 52.6% on Qwen3-Coder-Flash, and 65.0% on Qwen3-Coder-Max, against 48.8%, 62.0%, and 74.6% for SWE-RM-30A3B.[^shumSWERMExecutionfreeFeedback2025]

## Strengths & Limitations

- The patch selection step requires test generation and execution, which Agent-RLVR calls rather expensive.[^daAgentRLVRTrainingSoftware2025]
- SWE-RL says of its pipeline-based Agentless Mini that dividing all steps into distinct inference stages is an "external structure" that prevents the model from learning through interaction feedback and from considering the whole problem holistically.[^weiSWERLAdvancingLLM2025]
- Agent-RLVR notes that Agentless supports Python, which is one reason its own work is limited to Python.[^daAgentRLVRTrainingSoftware2025]

# Contradictions

**GPT-4o with Agentless: 38.8 or 34.0.** SWE-RL and Agent-RLVR list GPT-4o with Agentless at 38.8.[^weiSWERLAdvancingLLM2025][^daAgentRLVRTrainingSoftware2025] R2E-Gym lists GPT-4o with "Agentless-1.5" at 34.0.[^jainR2EGymProceduralEnvironments2025] The scaffold label differs (Agentless vs. Agentless-1.5), and none of the papers states the GPT-4o snapshot, so the rows may not be the same system.

**Scaffold of the SWE-RL result.** SWE-RL reports its 41.0 with Agentless Mini.[^weiSWERLAdvancingLLM2025] Agent-RLVR labels the same result "Llama3-SWE-RL-70B (Agentless)", and R2E-Gym describes it as "Best@500 (using Agentless)".[^daAgentRLVRTrainingSoftware2025][^jainR2EGymProceduralEnvironments2025] The score is the same; only the scaffold name is less specific in the later papers.

**Model names.** The 50.8 row is Claude-3.5-Sonnet with Agentless in SWE-RL and Agent-RLVR, and Claude-3.6-Sonnet with Agentless-1.5 in R2E-Gym.[^weiSWERLAdvancingLLM2025][^daAgentRLVRTrainingSoftware2025][^jainR2EGymProceduralEnvironments2025] The o1-preview (41.3) and O1 (48.0) rows name different models and are not in conflict.[^weiSWERLAdvancingLLM2025][^jainR2EGymProceduralEnvironments2025]

## Related

- Methods: [OpenHands](openhands.md), [SWE-agent](swe-agent.md), [Test-time scaling](test-time-scaling.md), [Execution-free verifier](execution-free-verifier.md)
- Benchmarks: [SWE-Bench Verified](../benchmarks/swe-bench-verified.md), [SWE-bench](../benchmarks/swe-bench.md)
- Datasets: [R2E-Gym](../datasets/r2e-gym.md), [SWE-Gym](../datasets/swe-gym.md)

[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
