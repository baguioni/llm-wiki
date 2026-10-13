---
type: Method
title: Execution-free verifier
description: A trained model that scores an agent trajectory or patch for correctness without running code, used to select among candidates at test time and as a reward signal in RL.
tags: [verifiers, reward-model, test-time-scaling, swe-agents, reinforcement-learning]
sources:
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
---

# Execution-free verifier

## Overview

In software engineering (SWE) tasks, verifiers fall into two categories. Execution-based verifiers rely on unit tests, human-written or model-generated. Execution-free verifiers are model-based: they give a continuous score for a trajectory without executing code.[^shumSWERMExecutionfreeFeedback2025] SWE-RM uses "reward model" and "execution-free verifier" for the same thing, and R2E-Gym calls them outcome-supervised reward models, "a.k.a verifiers".[^shumSWERMExecutionfreeFeedback2025][^jainR2EGymProceduralEnvironments2025]

The two uses in the wiki's papers are [test-time scaling](test-time-scaling.md) (choosing one of several sampled trajectories) and reinforcement learning (RL) reward.[^shumSWERMExecutionfreeFeedback2025]

## How it works

Both R2E-Gym and SWE-RM follow the formulation of SWE-Gym (Pan et al.), which is not in this wiki.[^jainR2EGymProceduralEnvironments2025][^shumSWERMExecutionfreeFeedback2025]

- **Input.** The task description, the agent trajectory, and, in R2E-Gym and SWE-RM, the output patch.[^jainR2EGymProceduralEnvironments2025][^shumSWERMExecutionfreeFeedback2025]
- **Output.** A single token, YES (correct or resolved) or NO. Training is supervised fine-tuning with the next-token prediction loss on that token.[^shumSWERMExecutionfreeFeedback2025]
- **Score.** With log probabilities $l_y$ and $l_n$ of the two tokens, $r = \exp(l_y)/(\exp(l_y)+\exp(l_n))$, so $r\in[0,1]$.[^shumSWERMExecutionfreeFeedback2025] R2E-Gym writes the same score as $s^{EF}=\mathrm{P}(\texttt{YES})/(\mathrm{P}(\texttt{YES})+\mathrm{P}(\texttt{NO}))$.[^jainR2EGymProceduralEnvironments2025]
- **Labels.** In SWE-RM a trajectory is positive or negative according to the execution result of the provided fail2pass test.[^shumSWERMExecutionfreeFeedback2025]

## Variants

SWE-RM's Table 6 compares the settings of execution-free verifiers ("-" means not disclosed):[^shumSWERMExecutionfreeFeedback2025]

| Reward model | # Data | # repo | Policy | Source | Context length | Prompt |
|---|---|---|---|---|---|---|
| SWE-Gym Verifier | 2636 | 11 | Mix | [SWE-Gym](../datasets/swe-gym.md) | 32k | Traj. |
| R2E-Gym Verifier | 3321 | 10 | Claude-3.5 | [R2E-Gym](../datasets/r2e-gym.md) | 32K | Traj. + Patch |
| Openhands Critic | - | 11 | - | SWE-Gym | 32k | Traj. |
| DeepSWE Verifier | - | 10 | - | R2E-Gym | 76k | Traj. + Patch |
| SWE-RM | $\sim$ 100k | $\sim$ 170 | Mix | Multiple | 256k | Traj. + Patch |

The R2E-Gym row conflicts with R2E-Gym's own description. See Contradictions.

Other forms in the wiki's papers:

- **Patch-only reward model (Agent-RLVR).** Takes the generated patch and the problem statement, not the trajectory. Base model Qwen-2.5-Coder-32B, trained with a pairwise loss on Agent-RLVR data.[^daAgentRLVRTrainingSoftware2025]
- **Hybrid verifier (R2E-Gym).** $s_{k}^{H}=\mathrm{Top}_{n}(s_{k}^{EF})+s_{k}^{EB}$: the execution-free score restricts the choice to the top $n$ patches and breaks ties in the execution-based test score.[^jainR2EGymProceduralEnvironments2025]
- **Hybrid RL reward (SWE-RM).** $1+\text{Score}_{EF}$ if the issue is resolved, $-0.5+\text{Score}_{EF}$ if unfinished, and $0+\text{Score}_{EF}$ otherwise.[^shumSWERMExecutionfreeFeedback2025]

## Papers using it

### R2E-Gym

[R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md) fine-tunes Qwen2.5-Coder-14B with LoRA (rank 64, 2 epochs, batch size 8, learning rate $1e-5$, maximum context length 32K). The training set is 5700 trajectories with equal numbers of positive and negative samples, and it includes on-policy trajectories from the trained 32B model.[^jainR2EGymProceduralEnvironments2025]

- On [SWE-Bench Verified](../benchmarks/swe-bench-verified.md), Best@K with the execution-free verifier alone plateaus at 42.8%, and with the execution-based verifier alone at 43.7%. The hybrid verifier reaches a Best@26 of 51%.[^jainR2EGymProceduralEnvironments2025]
- Removing $\mathrm{Top}_{n}$ filtering by the execution-free score lowers the hybrid result from 51.0% to 49.8%.[^jainR2EGymProceduralEnvironments2025]

Effect of the verifier input (Figure 7a):[^jainR2EGymProceduralEnvironments2025]

| Verifier input | Accuracy (%) | Best@26 (%) |
|---|---|---|
| Final Patch + Traj. | 71.82 | 42.8 |
| Patch Only | 68.01 | 37.6 |
| Traj. - Thoughts | 68.77 | 41.4 |

### SWE-RM

[SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md) trains a mixture-of-experts verifier on Qwen3-30B-A3B (30B total parameters, 3B activated) with a 256k context window, on around 100k usable trajectories.[^shumSWERMExecutionfreeFeedback2025] It evaluates three abilities: selection (RM@K), discrimination (AUC), and calibration (ECE).[^shumSWERMExecutionfreeFeedback2025]

Comparison on SWE-bench Verified (Table 4). Each cell is AUC / ECE / RM@32. EB is execution-based and EF is execution-free.[^shumSWERMExecutionfreeFeedback2025]

| Verifier | Type | OpenHands-LM-32B | Qwen3-Coder-Flash | Qwen3-Coder-Max |
|---|---|---|---|---|
| [Agentless](agentless.md) | EB | - / - / 42.4% | - / - / 52.6% | - / - / 65.0% |
| SWE-Gym | EF | 0.718 / 0.164 / 41.6% | 0.776 / 0.223 / 51.2% | 0.752 / 0.283 / 65.4% |
| DeepSWE | EB | - / - / 44.2% | - / - / 54.6% | - / - / 67.6% |
| DeepSWE | EF | 0.732 / 0.118 / 44.6% | 0.758 / 0.124 / 53.2% | 0.74 / 0.139 / 66.2% |
| SWE-RM-30A3B | EF | 0.748 / 0.080 / 48.8% | 0.783 / 0.051 / 62.0% | 0.768 / 0.047 / 74.6% |

Training findings:

- **Data scale.** Verifiers trained on more than 20k samples generally improve in TTS as $k$ increases, while those trained on fewer than 5k may decline. A model trained with only 500 examples has an ECE of 0.481, seven times higher than one trained with 100k examples.[^shumSWERMExecutionfreeFeedback2025]
- **Positive-to-negative ratio.** A 2:1 ratio is the default. On Qwen3-Coder-Flash it gives AUC 0.805, ECE 0.080, and RM@32 62.0%, against AUC 0.778, ECE 0.349, and RM@32 60.2% at 1:8.[^shumSWERMExecutionfreeFeedback2025]
- **Context length.** With a 32 k context only 12.5% of trajectories can be scored (RM@32 67.4%). With 256 k the score rate is 100% (RM@32 74.4%).[^shumSWERMExecutionfreeFeedback2025]
- **RL.** With [OpenHands](openhands.md) as the agent scaffold, the hybrid reward gives a pass@1 of 54.8% on SWE-bench Verified against 51.8% for execution-based feedback alone. The authors state they are the first to integrate execution-free feedback into SWE agentic RL.[^shumSWERMExecutionfreeFeedback2025]

### Agent-RLVR

[Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md) generates $k=32$ patches at inference and ranks them with its reward model to select one. This raises Pass@1 on SWE-Bench Verified from 22.4% to 27.8% for Qwen-2.5-72B-Instruct.[^daAgentRLVRTrainingSoftware2025]

## Strengths & Limitations

- **Finer signal, no tests needed.** The score is continuous and does not depend on unit tests, while execution-based feedback is a sparse pass/fail signal that cannot separate two trajectories with the same test outcome.[^shumSWERMExecutionfreeFeedback2025] R2E-Gym likewise finds that the execution-free score distinguishes patches better.[^jainR2EGymProceduralEnvironments2025]
- **Bias toward trajectory features.** Execution-free verifiers lean on features such as agent thoughts instead of the final patch. Best@26 drops from 42.8% to 37.6% with patch-only input, and an attention analysis shows the verifier attending to agent thoughts, which can mislead it.[^jainR2EGymProceduralEnvironments2025]
- **TTS does not capture verifier quality.** Two verifiers with nearly identical TTS gains (+4.7% vs. +4.5%) differ by 0.095 in AUC. One is three times better calibrated, and only that one supports stable RL, while the other causes training to collapse.[^shumSWERMExecutionfreeFeedback2025]
- **Weaker alone in late RL.** Execution-free feedback alone gives faster initial progress but weaker convergence in later stages. The best RL result uses the hybrid reward.[^shumSWERMExecutionfreeFeedback2025]
- **Noisy labels.** Training labels come from fail2pass test execution, and unit tests may not reflect the correctness of a patch.[^shumSWERMExecutionfreeFeedback2025]
- **Memory.** A 256k model takes around 2x the GPU memory of a 32k model. Latency is about the same, because the output is one token.[^shumSWERMExecutionfreeFeedback2025]

# Contradictions

**Training data of the R2E-Gym verifier.** SWE-RM's Table 6 lists the R2E-Gym Verifier with 3321 training examples and the policy "Claude-3.5".[^shumSWERMExecutionfreeFeedback2025] R2E-Gym states that its execution-free verifier is trained on 5700 trajectories, balanced between positive and negative samples, which include on-policy trajectories from its trained 32B model.[^jainR2EGymProceduralEnvironments2025] In R2E-Gym, 3321 is the number of successful Sonnet-3.5-v2 trajectories collected to train the code-editing agent, not the verifier.[^jainR2EGymProceduralEnvironments2025] The SWE-RM row likely copies the agent-training figures. The two papers agree on the 10 repositories and the 32K context length.[^shumSWERMExecutionfreeFeedback2025][^jainR2EGymProceduralEnvironments2025]

## Related

- Methods: [Test-time scaling](test-time-scaling.md), [Agentless](agentless.md), [OpenHands](openhands.md), [GRPO](grpo.md)
- Datasets: [SWE-Gym](../datasets/swe-gym.md), [R2E-Gym](../datasets/r2e-gym.md)
- Benchmarks: [SWE-Bench Verified](../benchmarks/swe-bench-verified.md)

[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
