---
type: Paper
title: "SWE-RM: Execution-Free Feedback for Software Engineering Agents"
description: Execution-free reward model for software engineering agents, trained for ranking, discrimination (AUC), and calibration (ECE) so that it works for both test-time scaling and reinforcement learning.
tags: [swe-agents, reward-model, execution-free-verifier, test-time-scaling, reinforcement-learning, calibration, ai899]
collections: [ai899]
authors: [Kashun Shum, Binyuan Hui, Jiawei Chen, Lei Zhang, X. W., Jiaxi Yang, Yuzhen Huang, Junyang Lin, Junxian He]
year: 2025
doi: 10.48550/arXiv.2512.21919
arxiv: "2512.21919"
arxiv_version: 2512.21919v1
sources:
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
---

# SWE-RM: Execution-Free Feedback for Software Engineering Agents

Text source: arXiv HTML, version `2512.21919v1`.

## Summary

Coding agents are developed with execution-based feedback such as unit tests, used in [test-time scaling](../methods/test-time-scaling.md) (TTS) and reinforcement learning (RL). That feedback is a sparse pass/fail signal, cannot separate two trajectories that both pass or both fail, and depends on unit tests that are often overly specific, unrelated to the issue, or model-generated without rigorous validation.[^shumSWERMExecutionfreeFeedback2025] Execution-free feedback from a [reward model](../methods/execution-free-verifier.md) gives a continuous score without a sandbox. The paper uses "reward model" and "execution-free verifier" interchangeably.[^shumSWERMExecutionfreeFeedback2025]

The paper observes that two verifiers with nearly identical TTS performance can give very different RL results, and argues that classification accuracy (AUC) and calibration (ECE) also matter for RL.[^shumSWERMExecutionfreeFeedback2025] After controlled ablations on training data scale, positive/negative ratio, policy mixture, data source, and context length, it introduces SWE-RM, a mixture-of-experts reward model with 30B total parameters and 3B activated during inference.[^shumSWERMExecutionfreeFeedback2025] On [SWE-bench Verified](../benchmarks/swe-bench-verified.md), SWE-RM raises Qwen3-Coder-Flash from 51.6% to 62.0% and Qwen3-Coder-Max from 67.0% to 74.6% with TTS, and in RL training it lifts the resolve rate of execution-based counterparts by 3 absolute points.[^shumSWERMExecutionfreeFeedback2025]

## Contributions

- Evidence that TTS alone is an insufficient measure of verifier quality, with AUC and ECE proposed as complementary metrics.[^shumSWERMExecutionfreeFeedback2025]
- A systematic study of how to train execution-free verifiers: data scaling, data ratio, policy mixture, source mixture, and context length.[^shumSWERMExecutionfreeFeedback2025]
- SWE-RM, a 30B MoE (3B activated) execution-free verifier with up to 256k context.[^shumSWERMExecutionfreeFeedback2025]
- The authors state they are the first to integrate execution-free feedback into SWE agentic RL.[^shumSWERMExecutionfreeFeedback2025]

## Method

### Why TTS is not enough

- TTS checks only whether the correct trajectory is ranked highest among candidates. It ignores *discriminative ability* (scoring near-miss and partially correct trajectories accurately) and *confidence reliability* (calibration of the score as a likelihood of correctness).[^shumSWERMExecutionfreeFeedback2025]
- Verifier A and verifier B have nearly identical TTS improvements (+4.7% vs. +4.5%), yet their AUC scores differ by 0.095, and verifier A is three times better calibrated by expected calibration error.[^shumSWERMExecutionfreeFeedback2025]
- In RL, verifier A supports smooth improvement, while verifier B is unstable and eventually causes training to collapse.[^shumSWERMExecutionfreeFeedback2025]
- Appendix C links each metric to a failure mode of the policy-gradient update: $1-\mathrm{TTS}@k$ is the probability that an unresolved trajectory gets the largest reward among $k$ samples; a fraction $1-\mathrm{AUC}$ of positive-negative pairs induce updates in the wrong direction; high ECE implies a systematic bias and extra variance in the gradient estimator.[^shumSWERMExecutionfreeFeedback2025]

Training settings of the illustrative verifiers (Table 8):[^shumSWERMExecutionfreeFeedback2025]

| Reward Model | # Data | Ratio | Policy | Source | Context Len. |
|---|---|---|---|---|---|
| Verifier A | 20k | 2:1 | Mix-Policy | Mixed-Source | 256k |
| Verifier B | 20k | 1:4 | Off-Policy | SWE-Rebench | 256k |
| Poorly Cali. RM in Figure 7 | 5k | 1:2 | Off-Policy | SWE-Rebench | 256k |

### Reward model training

- Following [SWE-Gym](../datasets/swe-gym.md), reward modeling is a generative classification task: given the full multi-turn trajectory, the model outputs a single special token, YES (resolved) or NO (unresolved), trained with next-token prediction loss on that token.[^shumSWERMExecutionfreeFeedback2025]
- At inference, with log probabilities $l_y$ and $l_n$ of the two tokens, the score is $r = \exp(l_y)/(\exp(l_y)+\exp(l_n))$, so $r\in[0,1]$.[^shumSWERMExecutionfreeFeedback2025]
- Base model: Qwen3-30B-A3B.[^shumSWERMExecutionfreeFeedback2025]
- Data: over 400k multi-turn trajectories of up to 100 iterations were rolled out with [OpenHands](../methods/openhands.md) and [SWE-Agent](yangSWEagentAgentComputerInterfaces2024.md), using Qwen3-Coder-Max, Qwen3-Coder-Flash, and Claude-4-sonnet as policies, on SWE-Gym, [SWE-rebench](../datasets/swe-rebench.md), [SWE-smith](../datasets/swe-smith.md), and [R2E-Gym](jainR2EGymProceduralEnvironments2025.md). The final usable set is around 100k trajectories.[^shumSWERMExecutionfreeFeedback2025]
- Labels are positive or negative according to the execution result of the provided fail2pass test. Instances without any successful trajectory are filtered out.[^shumSWERMExecutionfreeFeedback2025]
- Hyperparameters (30BA3): global batch size 128, learning rate 7e-6 $\rightarrow$ 7e-7 with a cosine scheduler, 3% LR warmup, AdamW, 1 epoch, 256k context window. Training uses 4 nodes of H100 and takes around 20 hours for 100k samples.[^shumSWERMExecutionfreeFeedback2025]
- Rollout uses [SGLang](zhengSGLangEfficientExecution2024.md), and supervised fine-tuning uses Megatron.[^shumSWERMExecutionfreeFeedback2025]

### RL with execution-free feedback

- Base policy: Qwen3-30B-A3B with SFT warm-up. Training scaffold: verl with Megatron. Agent scaffold: OpenHands. Objective: GSPO, chosen for stability in mixture-of-experts RL training.[^shumSWERMExecutionfreeFeedback2025]
- Hybrid reward (Eq. 1), with $\text{Score}_{EF}\in[0,1]$ from SWE-RM: $1+\text{Score}_{EF}$ if the issue is resolved, $-0.5+\text{Score}_{EF}$ if unfinished, and $0+\text{Score}_{EF}$ otherwise.[^shumSWERMExecutionfreeFeedback2025]
- Training data: curated data from SWE-Gym and SWE-rebench, batch size 64, 16 rollouts per problem, a maximum of 100 iterations, context length 128k. Data is filtered by difficulty.[^shumSWERMExecutionfreeFeedback2025]

## Experiments & Results

### Evaluation setup

- SWE-bench Verified, 500 human-verified tasks. For each instance, 32 independent runs are collected with OpenHands (temperature 1.0, top_p 0.95, max_iterations 100), giving $32\times 500$ trajectories.[^shumSWERMExecutionfreeFeedback2025]
- AUC is computed over all 16k trajectories. ECE uses 10 bins.[^shumSWERMExecutionfreeFeedback2025]
- RM@K is the resolve rate of the final selected trajectory from $k$ samples. Pass@k is the resolve rate with at least one successful solution among $k$ trajectories. For every $k<32$, the mean and variance of 5 random runs are reported.[^shumSWERMExecutionfreeFeedback2025]

### Data scale

- Models trained on more than 20k samples generally improve in TTS as $k$ increases, while models trained on fewer than 5k samples may decline.[^shumSWERMExecutionfreeFeedback2025]
- TTS improves as training data grows up to 25k, and expansion to 100k yields diminishing returns.[^shumSWERMExecutionfreeFeedback2025]
- A model trained with only 500 examples has an ECE of 0.481, seven times higher than that of a model trained with 100k examples.[^shumSWERMExecutionfreeFeedback2025]

### Positive-to-negative ratio (Table 1)

| Ratio | Flash AUC | Flash ECE | Flash RM@32 | Max AUC | Max ECE | Max RM@32 |
|---|---|---|---|---|---|---|
| 2 : 1 | 0.805 | 0.080 | 62.0% | 0.755 | 0.121 | 71.0% |
| 1 : 1 | 0.782 | 0.132 | 60.8% | 0.734 | 0.157 | 70.2% |
| 1 : 2 | 0.789 | 0.235 | 61.0% | 0.736 | 0.371 | 69.4% |
| 1 : 4 | 0.789 | 0.185 | 61.6% | 0.742 | 0.299 | 71.8% |
| 1 : 8 | 0.778 | 0.349 | 60.2% | 0.738 | 0.541 | 70.6% |

Flash is Qwen3-Coder-Flash and Max is Qwen3-Coder-Max. The 2:1 ratio is adopted as the default. Ratios above 2:1 were not tested because positive data is limited.[^shumSWERMExecutionfreeFeedback2025]

### Context length (Table 2)

Score rate is the percentage of trajectories that can be scored without exceeding the context window.[^shumSWERMExecutionfreeFeedback2025]

| Context Len. | Score Rate | RM@32 |
|---|---|---|
| 16 k | 0.5% | 66.8% |
| 32 k | 12.5% | 67.4% |
| 64 k | 88.3% | 70.6% |
| 128 k | 99.5% | 73.0% |
| 256 k | 100% | 74.4% |

A 256k model takes around 2x the GPU memory of a 32k model. Because the output is one token, latency is described as more or less the same across context lengths.[^shumSWERMExecutionfreeFeedback2025]

### Policy and source ablation (Table 3)

RM@32 is printed on a percent scale in the policy rows and as a fraction in the source rows. Values are copied as printed.[^shumSWERMExecutionfreeFeedback2025]

| Setting | Flash AUC | Flash ECE | Flash RM@32 | Max AUC | Max ECE | Max RM@32 |
|---|---|---|---|---|---|---|
| On-Policy | 0.785 | 0.148 | 58.6 | 0.727 | 0.067 | 71.0 |
| Off-Policy | 0.778 | 0.113 | 58.2 | 0.728 | 0.145 | 70.6 |
| Mix-Policy | 0.804 | 0.033 | 59.6 | 0.751 | 0.082 | 70.2 |
| SWE-rebench | 0.814 | 0.076 | 0.612 | 0.774 | 0.048 | 0.718 |
| SWE-smith | 0.781 | 0.033 | 0.584 | 0.736 | 0.039 | 0.70 |
| SWE-Gym | 0.776 | 0.087 | 0.588 | 0.742 | 0.044 | 0.714 |
| SWE-Gym + SWE-smith | 0.813 | 0.034 | 0.602 | 0.772 | 0.035 | 0.72 |
| SWE-Gym + SWE-rebench | 0.802 | 0.087 | 0.61 | 0.762 | 0.039 | 0.712 |
| SWE-rebench + SWE-smith | 0.807 | 0.138 | 0.596 | 0.765 | 0.107 | 0.714 |
| SWE-rebench + SWE-smith + SWE-Gym | 0.807 | 0.067 | 0.612 | 0.766 | 0.033 | 0.718 |

On-policy data is sampled with the corresponding Flash/Max model on SWE-rebench, and off-policy data with Claude-sonnet-4. The final setup uses a mixture primarily from SWE-rebench, supplemented with SWE-smith and SWE-Gym.[^shumSWERMExecutionfreeFeedback2025]

### Comparison with other verifiers on SWE-bench Verified (Table 4)

EB is execution-based, EF is execution-free. Each cell is AUC / ECE / RM@32.[^shumSWERMExecutionfreeFeedback2025]

| Verifier | Type | OpenHands-LM-32B | Qwen3-Coder-Flash | Qwen3-Coder-Max |
|---|---|---|---|---|
| [Agentless](../methods/agentless.md) | EB | - / - / 42.4% | - / - / 52.6% | - / - / 65.0% |
| SWE-Gym | EF | 0.718 / 0.164 / 41.6% | 0.776 / 0.223 / 51.2% | 0.752 / 0.283 / 65.4% |
| [DeepSWE](../methods/deepswe.md) | EB | - / - / 44.2% | - / - / 54.6% | - / - / 67.6% |
| DeepSWE | EF | 0.732 / 0.118 / 44.6% | 0.758 / 0.124 / 53.2% | 0.74 / 0.139 / 66.2% |
| SWE-RM-30A3B | EF | 0.748 / 0.080 / 48.8% | 0.783 / 0.051 / 62.0% | 0.768 / 0.047 / 74.6% |

For the Qwen3-Coder series, RM@32 improves pass@1 by 7-10 points.[^shumSWERMExecutionfreeFeedback2025]

### Comparison of execution-free verifier settings (Table 6)

| Reward Model | # Data | # repo | Policy | Source | Context Len. | Prompt |
|---|---|---|---|---|---|---|
| SWE-Gym Verifier | 2636 | 11 | Mix | SWE-Gym | 32k | Traj. |
| R2E-Gym Verifier | 3321 | 10 | Claude-3.5 | R2E-Gym | 32K | Traj. + Patch |
| Openhands Critic | - | 11 | - | SWE-Gym | 32k | Traj. |
| DeepSWE Verifier | - | 10 | - | R2E-Gym | 76k | Traj. + Patch |
| SWE-RM | $\sim$ 100k | $\sim$ 170 | Mix | Multiple | 256k | Traj. + Patch |

All rows: [^shumSWERMExecutionfreeFeedback2025]

### RL results

- On SWE-bench Verified, with 1 trajectory and 1 patch per instance under greedy decoding and no test-time scaling, hybrid feedback improves pass@1 by about 3 absolute points over the execution-based baseline (54.8% vs. 51.8%).[^shumSWERMExecutionfreeFeedback2025]
- Execution-based feedback alone shows slower early gains and an early plateau. Execution-free feedback alone shows faster initial progress but weaker convergence in later stages.[^shumSWERMExecutionfreeFeedback2025]

Performance after RL on other tasks (Table 5):[^shumSWERMExecutionfreeFeedback2025]

| Method | SWE-Bench Live (Lite) | SWE-Bench Multilingual | Multi-SWE-Bench mini | [Terminal Bench](../benchmarks/terminal-bench.md) |
|---|---|---|---|---|
| Hybrid | 22.4 | 35.7 | 20.0 | 32.5 |
| Execution-free only | 20.4 | 33.0 | 18.8 | 31.3 |
| Execution-based only | 20.0 | 33.3 | 18.5 | 30.0 |
| Poor Calibrated RM | 12.0 | 21.0 | 10.0 | 15.0 |

## Limitations

- Training labels come from fail2pass test execution and may be noisy, since unit tests may not reflect the correctness of a patch. The authors rely on filtering and data scale to handle this.[^shumSWERMExecutionfreeFeedback2025]
- Execution-free feedback alone converges more weakly in later RL stages, which the authors attribute to inaccuracies in its unverified signals. The best RL result uses the hybrid reward, which still needs execution.[^shumSWERMExecutionfreeFeedback2025]
- Architectural comparisons (MoE vs. Dense vs. Adapters) are left to future work.[^shumSWERMExecutionfreeFeedback2025]
- A 256k context costs more memory.[^shumSWERMExecutionfreeFeedback2025]
- The metric discussion in Section 3 uses early, small-scale reward model variants as illustrative examples.[^shumSWERMExecutionfreeFeedback2025]
- The RL policy is warmed up on in-house collected agentic trajectories.[^shumSWERMExecutionfreeFeedback2025]
- The paper has no dedicated limitations section.

## Related

- Methods: [SWE-RM](../methods/swe-rm.md), [Execution-free verifier](../methods/execution-free-verifier.md), [Test-time scaling](../methods/test-time-scaling.md), [GSPO](../methods/gspo.md)
- Systems compared or built on: [OpenHands](../methods/openhands.md), [Agentless](../methods/agentless.md), [DeepSWE](../methods/deepswe.md)
- Benchmarks: [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [Terminal Bench](../benchmarks/terminal-bench.md)
- Datasets: [SWE-Gym](../datasets/swe-gym.md), [SWE-rebench](../datasets/swe-rebench.md), [SWE-smith](../datasets/swe-smith.md)
- Papers in this wiki cited by this paper: [R2E-Gym](jainR2EGymProceduralEnvironments2025.md), [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md), [SWE-RL](weiSWERLAdvancingLLM2025.md)
- Papers in this wiki whose system is used: [SGLang](zhengSGLangEfficientExecution2024.md)

[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
