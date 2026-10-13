---
type: Dataset
title: SWE-Gym
description: Training environment of executable GitHub issue-resolution tasks with human-written issues and tests, used in the wiki's papers as a training source, a baseline model family, and a verifier baseline.
tags: [swe-agents, training-environments, issue-resolution, verifiers]
sources:
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
---

# SWE-Gym

## Overview

No paper in this wiki introduces SWE-Gym (Pan et al.). This page records what the papers that use it or compare against it state.

SWE-Gym is a set of executable GitHub environments for training software engineering (SWE) agents. It relies on human-written issues and test cases, which R2E-Gym says restricts its sample size.[^jainR2EGymProceduralEnvironments2025] SWE-RL describes it as the first open training environment for software engineering agents.[^weiSWERLAdvancingLLM2025]

The name also refers to two artifacts trained on it:

- **SWE-Gym models.** Agent models built on Qwen2.5-Coder. Agent-RLVR says SWE-Gym trained the model via rejection sampling and also explores test-time scaling for model patches.[^daAgentRLVRTrainingSoftware2025] SWE-RL notes that the SWE-Gym training data includes distilled outputs from GPT-4o or Claude-3.5-Sonnet.[^weiSWERLAdvancingLLM2025]
- **SWE-Gym Verifier.** An [execution-free verifier](../methods/execution-free-verifier.md) based on Qwen2.5-32B and trained on the SWE-Gym dataset.[^shumSWERMExecutionfreeFeedback2025]

## Composition

| Split | Repo? | Executable? | # Instances | Reported by |
|---|---|---|---|---|
| SWE-Gym Raw | ✓ | ✗ | 66,894 | R2E-Gym, Table 1[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym | ✓ | ✓ | 2,438 | R2E-Gym, Table 1[^jainR2EGymProceduralEnvironments2025] |

- Agent-RLVR gives the size as "2k" training instances.[^daAgentRLVRTrainingSoftware2025]
- SWE-RM's Table 6 lists 11 repositories for the SWE-Gym Verifier, with 2636 training examples, a mixed policy, a 32k context length, and a trajectory-only prompt.[^shumSWERMExecutionfreeFeedback2025]

## Usage across papers

### As training data

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md) | Source of training problems | 593 problems from SWE-Gym plus 219 self-collected problems; 817 environments from 27 repos; Qwen-2.5 family, offline [DPO](../methods/dpo.md) | Qwen-2.5-72B-Instruct Pass@1 on [SWE-Bench Verified](../benchmarks/swe-bench-verified.md): 9.4% to 22.4%[^daAgentRLVRTrainingSoftware2025] |
| [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md) | One of four sources of reward-model training trajectories, with SWE-rebench, SWE-smith, and [R2E-Gym](r2e-gym.md) | Rollouts with [OpenHands](../methods/openhands.md) and SWE-Agent; Qwen3-30B-A3B reward model | Single-source SWE-Gym: AUC 0.776, ECE 0.087, RM@32 0.588 on Qwen3-Coder-Flash; AUC 0.742, ECE 0.044, RM@32 0.714 on Qwen3-Coder-Max[^shumSWERMExecutionfreeFeedback2025] |
| SWE-RM | RL training data for the policy, with SWE-rebench | Qwen3-30B-A3B policy, batch size 64, 16 rollouts per problem | pass@1 of 54.8% with the hybrid reward vs. 51.8% with execution-based feedback[^shumSWERMExecutionfreeFeedback2025] |

SWE-RM's final reward-model data is a mixture primarily from SWE-rebench, supplemented with SWE-smith and SWE-Gym. Adding SWE-smith and SWE-Gym improves calibration (lower ECE).[^shumSWERMExecutionfreeFeedback2025]

### As a baseline model

Scores of SWE-Gym-trained models on SWE-Bench Verified, as each paper prints them.

| Model as labeled | Score | Setting as labeled | Reported by |
|---|---|---|---|
| SWE-Gym, Qwen-2.5-Coder 7B | 10.6 (±2.1) | Pass@1 | [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md)[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym, Qwen-2.5-Coder 14B | 16.4 (±2.0) | Pass@1 | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym, Qwen-2.5-Coder 32B | 20.6 (±2.1) | Pass@1 | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym-Qwen-2.5-Coder-32B (OpenHands) | 20.6% | Pass@1 | [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md)[^daAgentRLVRTrainingSoftware2025] |
| SWE-Gym-32B | 32.0 | Best@16 w/ Verifier | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym-32B | 32.0 | scaffold OpenHands, in a table of pass@1 results | [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md)[^weiSWERLAdvancingLLM2025] |

On [SWE-Bench Lite](../benchmarks/swe-bench-lite.md), R2E-Gym reports SWE-Gym Pass@1 of 10.0 (±2.4) at 7B, 12.7 (±2.3) at 14B, and 15.3 (±2.5) at 32B.[^jainR2EGymProceduralEnvironments2025] At the same base model and scale, the R2E-Gym-trained models score higher: 19.0, 26.8, and 34.4 on Verified.[^jainR2EGymProceduralEnvironments2025]

### As a verifier baseline

SWE-RM compares against the SWE-Gym Verifier on SWE-bench Verified (AUC / ECE / RM@32):[^shumSWERMExecutionfreeFeedback2025]

| Verifier | OpenHands-LM-32B | Qwen3-Coder-Flash | Qwen3-Coder-Max |
|---|---|---|---|
| SWE-Gym (execution-free) | 0.718 / 0.164 / 41.6% | 0.776 / 0.223 / 51.2% | 0.752 / 0.283 / 65.4% |
| SWE-RM-30A3B | 0.748 / 0.080 / 48.8% | 0.783 / 0.051 / 62.0% | 0.768 / 0.047 / 74.6% |

Both R2E-Gym and SWE-RM follow SWE-Gym's formulation for their own verifiers: the model outputs a YES or NO token for a trajectory.[^jainR2EGymProceduralEnvironments2025][^shumSWERMExecutionfreeFeedback2025]

## Known issues

- Its size is limited by its reliance on human-written issues and test cases.[^jainR2EGymProceduralEnvironments2025]
- SWE-RM describes the SWE-Gym verifier and OpenHands Critic as early, naive execution-free verifiers with limited coverage, confined to relatively simple settings.[^shumSWERMExecutionfreeFeedback2025]

# Contradictions

**SWE-Gym-32B on SWE-Bench Verified: 32.0 or 20.6.** SWE-RL lists SWE-Gym-32B at 32.0 in a table it describes as pass@1 results.[^weiSWERLAdvancingLLM2025] Agent-RLVR lists the SWE-Gym 32B model at a Pass@1 of 20.6%.[^daAgentRLVRTrainingSoftware2025] R2E-Gym reports both and separates them: 20.6 is Pass@1, and 32.0 is Best@16 with a verifier.[^jainR2EGymProceduralEnvironments2025] The likely cause is the setting: 32.0 uses [test-time scaling](../methods/test-time-scaling.md) over 16 rollouts, and 20.6 is a single rollout. SWE-RL's own 41.0 in the same table also uses many samples (500 patches per problem) with one final submission.[^weiSWERLAdvancingLLM2025]

**Size.** R2E-Gym gives 2,438 executable instances, and Agent-RLVR says "2k".[^jainR2EGymProceduralEnvironments2025][^daAgentRLVRTrainingSoftware2025] The second figure looks like a rounded form of the first, so this is a difference in precision.

## Related

- Datasets: [R2E-Gym](r2e-gym.md)
- Methods: [Execution-free verifier](../methods/execution-free-verifier.md), [Test-time scaling](../methods/test-time-scaling.md), [OpenHands](../methods/openhands.md), [DPO](../methods/dpo.md)
- Benchmarks: [SWE-Bench Verified](../benchmarks/swe-bench-verified.md), [SWE-Bench Lite](../benchmarks/swe-bench-lite.md), [SWE-bench](../benchmarks/swe-bench.md)

[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
