---
type: Dataset
title: R2E-Gym
description: Procedurally curated gym of 8,135 executable software engineering tasks built from GitHub commits with generated tests and back-translated issues, used to train SWE agents and verifiers.
tags: [swe-agents, training-environments, synthetic-data, issue-resolution]
sources:
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
---

# R2E-Gym

## Overview

R2E-Gym is a procedurally curated environment for training real-world software engineering (SWE) agents. It has more than 8.1K problems, each with an executable gym environment, unit tests, and a natural-language task description.[^jainR2EGymProceduralEnvironments2025] It was introduced in [Jain et al. 2025](../papers/jainR2EGymProceduralEnvironments2025.md), which calls it the largest procedurally curated environment of its kind and says it increases the number of executable environments by over 3 times.[^jainR2EGymProceduralEnvironments2025]

The environments are built with SweGen, a synthetic data recipe that works from commits. It does not need human-written issues or unit tests, which is the difference from [SWE-Gym](swe-gym.md).[^jainR2EGymProceduralEnvironments2025] SweGen collects over 2.5 times more problems than data collection that relies on GitHub issues.[^jainR2EGymProceduralEnvironments2025]

## Composition

| Split | Repo? | Executable? | # Instances |
|---|---|---|---|
| R2E-Gym (full) | ✓ | ✓ | 8,135 |
| R2E-Gym-Subset | ✓ | ✓ | 4,578 |

All rows: [^jainR2EGymProceduralEnvironments2025]

- **R2E-Gym-Subset** removes repositories that overlap with the SWE-Bench test set, to avoid contamination. It has 4578 executable environments across 10 repositories and is used for all of the paper's experiments unless specified otherwise.[^jainR2EGymProceduralEnvironments2025]
- **Sources.** Commits from Python repositories with a large number of commits, found with SEART GitHub search.[^jainR2EGymProceduralEnvironments2025]
- **Tests.** Existing tests in a commit identify Fail→Pass (F2P) test cases, which fail on the original buggy commit and pass on the fixed commit. Commits without tests get generated tests, using an [Agentless](../methods/agentless.md)-like reproduction test generation approach.[^jainR2EGymProceduralEnvironments2025]
- **Problem statements.** Written by an LLM through back-translation, with the F2P tests as part of the prompt.[^jainR2EGymProceduralEnvironments2025]

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md) | SFT trajectories for a code-editing agent | Sonnet-3.5-v2 on R2E-Gym-Subset with a scaffold built on [OpenHands](../methods/openhands.md); 3321 successful trajectories from 2048 unique task environments; Qwen-2.5-Coder 7B, 14B, 32B | Pass@1 on [SWE-Bench Verified](../benchmarks/swe-bench-verified.md): 19.0 (±1.0), 26.8 (±1.4), 34.4 (±1.2). On [SWE-Bench Lite](../benchmarks/swe-bench-lite.md): 11.0 (±0.8), 20.67 (±0.7), 23.77 (±0.8)[^jainR2EGymProceduralEnvironments2025] |
| R2E-Gym | Training data for verifiers | [Execution-free verifier](../methods/execution-free-verifier.md) on 5700 trajectories (Qwen2.5-Coder-14B); testing agent for the execution-based verifier on 2203 test-generation trajectories | Hybrid verifier with R2E-Gym-32B on SWE-Bench Verified: 49.4 (Best@16), 51.0 (Best@26)[^jainR2EGymProceduralEnvironments2025] |
| R2E-Gym | Real vs. synthetic problem statements | 400 trajectories each | Pass@1 28.0 with real data, 27.8 with synthetic data[^jainR2EGymProceduralEnvironments2025] |
| [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md) | One of four sources of reward-model training trajectories, with SWE-Gym, SWE-rebench, and SWE-smith | Rollouts with OpenHands and SWE-Agent; over 400k trajectories collected across the sources, around 100k usable | No R2E-Gym-only number is reported[^shumSWERMExecutionfreeFeedback2025] |
| [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md) | Serving workload for KV-cache offloading test | MiniMax M2.5 on R2E-Gym, SGLang HiCache with host-memory ratio 2.0, 8×H100, batch size 64 to 192 | Baseline P50 latency goes from ∼10 s to ∼30 s at batch 160 and ∼70 s at batch 192. ThunderAgent holds P50 at ∼10 s and P90 at ∼20 s[^kangThunderAgentSimpleFast2026] |
| ThunderAgent | RL training recipe in SkyRL | Qwen3-32B on R2EGym | 3.01× wall-clock speedup over the baseline[^kangThunderAgentSimpleFast2026] |

Comparison with SWE-Gym at the same base model (Qwen-2.5-Coder), Pass@1 on SWE-Bench Verified:[^jainR2EGymProceduralEnvironments2025]

| Model size | SWE-Gym | R2E-Gym | Δ |
|---|---|---|---|
| 7B | 10.6 (±2.1) | 19.0 (±1.0) | +8.4 |
| 14B | 16.4 (±2.0) | 26.8 (±1.4) | +10.4 |
| 32B | 20.6 (±2.1) | 34.4 (±1.2) | +13.8 |

Other papers also refer to verifiers named after R2E-Gym. SWE-RM lists an "R2E-Gym Verifier" and a "DeepSWE Verifier" whose source is R2E-Gym (10 repositories each), and says the DeepSWE verifiers extend the R2E-Gym execution-based and execution-free verifiers.[^shumSWERMExecutionfreeFeedback2025]

## Known issues

- **Installation does not scale easily.** Build scripts are collected semi-manually by searching across dependency pins.[^jainR2EGymProceduralEnvironments2025]
- **Subset size is stated two ways.** The main text gives 4578 environments for R2E-Gym-Subset. Appendix B gives 4538 and calls the subset R2E-Gym-lite.[^jainR2EGymProceduralEnvironments2025]
- **Generated tests are not rigorously validated.** SWE-RM names R2E-Gym as an example of work that relies on model-generated unit tests that are not rigorously validated.[^shumSWERMExecutionfreeFeedback2025]
- **Trajectory scaling saturates for smaller models.** With more training trajectories, the 14B model begins to saturate at approximately 800 samples, while the 32B model still improves.[^jainR2EGymProceduralEnvironments2025]

# Contradictions

**Subset size, within the source paper.** 4578 (main text and Table 1) vs. 4538 (Appendix B, as R2E-Gym-lite). Both describe the subset with no repository overlap with SWE-Bench, across 10 repositories. The paper does not explain the difference.[^jainR2EGymProceduralEnvironments2025]

**Training data of the R2E-Gym verifier.** SWE-RM's Table 6 lists the R2E-Gym Verifier with 3321 training examples and the policy "Claude-3.5".[^shumSWERMExecutionfreeFeedback2025] R2E-Gym states that its execution-free verifier is trained on 5700 trajectories that include on-policy trajectories from its 32B model, and that 3321 is the number of Sonnet-3.5-v2 trajectories used to train the code-editing agent.[^jainR2EGymProceduralEnvironments2025] Details are on the [Execution-free verifier](../methods/execution-free-verifier.md) page.

## Related

- Datasets: [SWE-Gym](swe-gym.md)
- Methods: [Execution-free verifier](../methods/execution-free-verifier.md), [Test-time scaling](../methods/test-time-scaling.md), [OpenHands](../methods/openhands.md), [Agentless](../methods/agentless.md), [ReAct](../methods/react.md), [ThunderAgent](../methods/thunderagent.md), [SGLang](../methods/sglang.md)
- Benchmarks: [SWE-Bench Verified](../benchmarks/swe-bench-verified.md), [SWE-Bench Lite](../benchmarks/swe-bench-lite.md), [SWE-bench](../benchmarks/swe-bench.md)

[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
