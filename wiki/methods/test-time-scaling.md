---
type: Method
title: Test-time scaling
description: Spending more compute at inference, by sampling several attempts and selecting one with a verifier or counting any success, to raise an agent's task success rate.
tags: [test-time-compute, verifiers, swe-agents, web-agents, inference]
sources:
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
  - id: karWeblicaScalableReproducible2026
    resource: zotero://select/items/@karWeblicaScalableReproducible2026
    title: "Weblica: Scalable and Reproducible Training Environments for Visual Web Agents"
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
---

# Test-time scaling

## Overview

Test-time scaling (TTS) raises an agent's success rate by spending more compute at inference instead of changing the model. In the wiki's software engineering (SWE) papers, the agent produces several candidate trajectories and patches for a task, and a verifier picks one to submit.[^jainR2EGymProceduralEnvironments2025][^shumSWERMExecutionfreeFeedback2025] R2E-Gym names scaling of test-time compute as one of two obstacles to improving open-weight models on SWE tasks, the other being scalable curation of training environments.[^jainR2EGymProceduralEnvironments2025] In the web-agent paper Weblica, test-time compute is scaled along two axes: the number of parallel attempts and the per-episode action budget.[^karWeblicaScalableReproducible2026]

## How it works

**Selection among samples.** Given a task description, $K$ agent trajectories, and $K$ candidate patches, a verifier assigns scores that rank the patches.[^jainR2EGymProceduralEnvironments2025] Verifiers fall into two categories: execution-based, which rely on unit tests, and [execution-free](execution-free-verifier.md), which use model-based scoring.[^shumSWERMExecutionfreeFeedback2025]

**Metrics.** The papers use different names for the selection metric.

| Metric | Definition | Paper |
|---|---|---|
| Best@K | Percentage of problems where the verifier selects a correct patch out of $K$ trajectories | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| RM@K | Resolve rate of the final selected trajectory from $k$ samples | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| Pass@k | Resolve rate with at least one successful solution among $k$ trajectories, which the paper calls the upper bound | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| pass@$k$ (Weblica) | Success over $k$ independent attempts, with the total step budget scaling linearly with $k$ | Weblica[^karWeblicaScalableReproducible2026] |

## Variants

- **Execution-based selection.** Patches are ranked by generated reproduction tests and filtered by regression tests.[^jainR2EGymProceduralEnvironments2025]
- **Execution-free selection.** A trained model scores each trajectory without running code. See [Execution-free verifier](execution-free-verifier.md).[^shumSWERMExecutionfreeFeedback2025]
- **Hybrid selection.** R2E-Gym combines both: $s_{k}^{H}=\mathrm{Top}_{n}(s_{k}^{EF})+s_{k}^{EB}$, where the execution-based score gives execution feedback and the continuous execution-free score breaks ties.[^jainR2EGymProceduralEnvironments2025]
- **Parallel attempts without selection.** Weblica reports pass@$k$ over $k\in\{1,2,4,8\}$ independent attempts.[^karWeblicaScalableReproducible2026]
- **Longer episodes.** Weblica also raises the per-episode action budget from 15 to 30 steps.[^karWeblicaScalableReproducible2026]

## Papers using it

### SWE-bench Verified, selection among samples

All rows are on [SWE-bench Verified](../benchmarks/swe-bench-verified.md). The rows differ in model, scaffold, and number of samples, so they are not a ranking of selection methods.

| Policy model | Single attempt | With test-time scaling | Selection method | Paper |
|---|---|---|---|---|
| R2E-Gym-32B | 34.4 (Pass@1) | 49.4 (Best@16), 51.0 (Best@26) | Hybrid verifier | [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md)[^jainR2EGymProceduralEnvironments2025] |
| R2E-Gym-32B | 34.4 (Pass@1) | 43.7% (plateau) | Execution-based verifier alone | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| R2E-Gym-32B | 34.4 (Pass@1) | 42.8% (plateau) | Execution-free verifier alone | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| Qwen3-Coder-Flash | 51.6% | 62.0% (RM@32) | SWE-RM, execution-free | [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Max | 67.0% | 74.6% (RM@32) | SWE-RM, execution-free | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| OpenHands-LM-32B | not stated | 48.8% (RM@32) | SWE-RM, execution-free | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| Agent-RLVR-Qwen-2.5-72B-Instruct | 22.4% (Pass@1) | 27.8% | Reward model ranking $k=32$ patches | [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md)[^daAgentRLVRTrainingSoftware2025] |
| Llama3-SWE-RL-70B | not stated | 33.6 at 20 repair samples, 40.0 at 160, 41.0 at 500 | Reproduction and regression tests ([Agentless](agentless.md) Mini) | [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md)[^weiSWERLAdvancingLLM2025] |
| SWE-Gym-32B | 20.6 (Pass@1) | 32.0 (Best@16) | Verifier | reported by R2E-Gym[^jainR2EGymProceduralEnvironments2025] |

Notes on each paper:

- **R2E-Gym.** The sample pool is 1 trajectory at temperature $T=0$ and 25 trajectories at $T=0.8$ and $T=0.9$, with Pass@26 = 64.4%.[^jainR2EGymProceduralEnvironments2025] Best@K plateaus quickly for both single verifiers, and the hybrid verifier adds 7-8%.[^jainR2EGymProceduralEnvironments2025] Raising editing-agent rollouts from 16 to 21 improves Best@K from 47.6% to 48.4%, while sampling 5 more test-agent rollouts gives 49.3%, and test-agent rollouts are usually considerably cheaper.[^jainR2EGymProceduralEnvironments2025]
- **SWE-RM.** 32 independent [OpenHands](openhands.md) runs per instance at temperature 1.0. For the Qwen3-Coder series, RM@32 improves pass@1 by 7-10 points.[^shumSWERMExecutionfreeFeedback2025] The paper argues that TTS alone is an insufficient measure of verifier quality: two verifiers with nearly identical TTS improvements (+4.7% vs. +4.5%) differ by 0.095 in AUC and behave very differently when used as RL rewards.[^shumSWERMExecutionfreeFeedback2025]
- **Agent-RLVR.** The reward model takes the generated patch and the problem statement. The paper also reports Pass@32 of 38.4% for the guidance-trained model and 34.2% without guidance, and the gap between the two grows as $k$ increases.[^daAgentRLVRTrainingSoftware2025]
- **SWE-RL.** The paper does not use the term test-time scaling. It studies how the final score scales with the number of repair samples and reproduction test samples: beyond 160 repair samples the improvement begins to plateau, and the score goes from 38.8 with 1 test sample to 41.0 with 20 or 30.[^weiSWERLAdvancingLLM2025] R2E-Gym labels this result "Best@500 w/ Tests".[^jainR2EGymProceduralEnvironments2025]

### Web navigation, parallel attempts and step budget

[Weblica](../papers/karWeblicaScalableReproducible2026.md), on [Online-Mind2Web](../benchmarks/online-mind2web.md) with 30 steps per attempt:[^karWeblicaScalableReproducible2026]

| Model | pass@1 | pass@2 | pass@4 | pass@8 |
|---|---|---|---|---|
| Qwen3-VL-8B (base) | 28.6 ± 0.4 | 37.6 ± 0.2 | 46.3 ± 0.3 | 54.4 ± 1.7 |
| Weblica-8B | 39.2 ± 0.9 | 50.3 ± 0.7 | 60.5 ± 0.9 | 68.8 ± 1.7 |

- Raising the action budget from 15 to 30 steps improves Weblica-8B pass@1 from 32.6% to 39.2%. The base model shows minimal gains from a larger action budget, which the authors take to suggest that RL training is key to using longer episodes.[^karWeblicaScalableReproducible2026]
- Averaged over three live benchmarks, Weblica-8B scores 35.6% at pass@1 with 30 steps, 47.6% with 60 total steps, 58.9% with 120, and 68.9% with 240.[^karWeblicaScalableReproducible2026]
- Weblica counts every attempt. It contrasts this with retry-based evaluation in prior work, where failures attributed to the environment are selectively discarded.[^karWeblicaScalableReproducible2026]

## Strengths & Limitations

- **Selection saturates.** Execution-based and execution-free verifiers each plateau around 42-43% on SWE-Bench Verified for R2E-Gym-32B, below the Pass@26 of 64.4% of the same sample pool.[^jainR2EGymProceduralEnvironments2025]
- **Execution-based feedback is coarse.** It is a sparse pass/fail signal that cannot separate two trajectories that both pass or both fail, and it needs high-quality unit tests.[^shumSWERMExecutionfreeFeedback2025] In R2E-Gym, for the majority of problems less than 20% of generated tests distinguish top-ranked correct patches from incorrect ones.[^jainR2EGymProceduralEnvironments2025]
- **More samples can hurt a weak verifier.** Verifiers trained on fewer than 5k samples may decline as $k$ increases, since a single erroneously high score for an incorrect trajectory can distort the final resolve rate.[^shumSWERMExecutionfreeFeedback2025]
- **Headline numbers depend on it.** R2E-Gym notes that its results with all open-weight models are reported with test-time scaling.[^jainR2EGymProceduralEnvironments2025]
- **Cost.** In Weblica the total step budget scales linearly with $k$.[^karWeblicaScalableReproducible2026]

## Related

- Methods: [Execution-free verifier](execution-free-verifier.md), [Agentless](agentless.md), [OpenHands](openhands.md)
- Benchmarks: [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [Online-Mind2Web](../benchmarks/online-mind2web.md)
- Datasets: [R2E-Gym](../datasets/r2e-gym.md), [SWE-Gym](../datasets/swe-gym.md)

## Open questions and results

- [Test-time scaling on SWE-bench Verified](../results/swe-bench-verified-test-time-scaling.md)
- [Which SWE-bench Verified scores are comparable?](../questions/swe-bench-verified-comparability.md)

[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
[^karWeblicaScalableReproducible2026]: Kar et al. 2026
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
