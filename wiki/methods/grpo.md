---
type: Method
title: GRPO
description: Group Relative Policy Optimization, a policy-gradient RL objective that samples a group of rollouts per prompt and uses each rollout's reward relative to its group as the advantage.
tags: [reinforcement-learning, policy-optimization, agentic-rl, llm-training]
sources:
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
  - id: wangAgentWorldModel2026
    resource: zotero://select/items/@wangAgentWorldModel2026
    title: "Agent World Model: Infinity Synthetic Environments for Agentic Reinforcement Learning"
  - id: liWebSailorV2BridgingChasm2025
    resource: zotero://select/items/@liWebSailorV2BridgingChasm2025
    title: "WebSailor-V2: Bridging the Chasm to Proprietary Agents via Synthetic Data and Scalable Reinforcement Learning"
  - id: karWeblicaScalableReproducible2026
    resource: zotero://select/items/@karWeblicaScalableReproducible2026
    title: "Weblica: Scalable and Reproducible Training Environments for Visual Web Agents"
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
---

# GRPO

## Overview

Group Relative Policy Optimization (GRPO) is the policy optimization algorithm that several papers in this wiki use to train LLMs and LLM agents with reinforcement learning. All of them cite Shao et al., 2024 for it; that paper is not in this wiki.[^weiSWERLAdvancingLLM2025][^wangAgentWorldModel2026][^liWebSailorV2BridgingChasm2025][^karWeblicaScalableReproducible2026] WebSailor-V2 states that the majority of recent RL implementations for agents are based on variants of GRPO.[^liWebSailorV2BridgingChasm2025]

## How it works

The description below is the form given in [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md).[^weiSWERLAdvancingLLM2025]

- For each input prompt $q$, the policy produces a group of $G$ outputs $o_i$.[^weiSWERLAdvancingLLM2025]
- Each output gets a reward $r_i$, and the advantage is the reward normalized within the group: $A_i = \frac{r_i - \text{mean}(r_1,\ldots,r_G)}{\text{std}(r_1,\ldots,r_G)}$.[^weiSWERLAdvancingLLM2025]
- The objective uses the ratio of the current policy to the old policy with a clipping hyperparameter $\epsilon$, and subtracts a KL-divergence term $\beta D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}})$ against a reference policy.[^weiSWERLAdvancingLLM2025]

## Variants

| Variant | Difference from the form above | Paper |
|---|---|---|
| Truncated-history GRPO | The loss is $\frac{1}{G}\sum_{k}A^{(k)}\sum_{t}\log\pi_{\theta}(a_{t}^{(k)}\mid h_{t}^{\text{trunc},(k)})$ with $A^{(k)}=(R^{(k)}-\bar{R})/\sigma_{R}$. Each action is conditioned on the same truncated history that the agent sees at inference. | [Agent World Model](../papers/wangAgentWorldModel2026.md)[^wangAgentWorldModel2026] |
| WebSailor-V2 adaptation | Asymmetric clipping with $\varepsilon_{low}$ and $\varepsilon_{high}$. The advantage is $\hat{A}_{i,t}=R_{i}-\text{mean}(\{R_{i}\}_{i=1}^{G})$, with no division by the standard deviation, and a leave-one-out strategy reduces its variance. Training is strictly on-policy with a token-level policy gradient loss. Some negative samples are excluded from the loss. | [WebSailor-V2](../papers/liWebSailorV2BridgingChasm2025.md)[^liWebSailorV2BridgingChasm2025] |
| Dr. GRPO | Named as a variant of GRPO. The paper does not describe what it changes. | [Weblica](../papers/karWeblicaScalableReproducible2026.md)[^karWeblicaScalableReproducible2026] |
| GSPO | Used in place of the GRPO objective because it gives greater stability, particularly in mixture-of-experts RL training. | [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md)[^shumSWERMExecutionfreeFeedback2025] |

## Papers using it

| Paper | Policy and task | Reward | Stated GRPO settings | Key result |
|---|---|---|---|---|
| [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md) | Llama-3.3-70B-Instruct, issue solving from GitHub PR data | Sequence similarity between the predicted and oracle patch (Python's `difflib.SequenceMatcher`), and -1 for a wrong format | Global batch size 512: 16 rollouts for each of 32 problems. 1,600 steps, 16k context window. $\epsilon$ and $\beta$ are not stated. | Llama3-SWE-RL-70B solves 41.0% of [SWE-bench Verified](../benchmarks/swe-bench-verified.md)[^weiSWERLAdvancingLLM2025] |
| [Agent World Model](../papers/wangAgentWorldModel2026.md) | Qwen3 tool-use agents in synthesized environments | not covered here; see the paper page | Learning rate $7\times 10^{-7}$, batch size 64, mini-batch size 16, 16 rollouts per task, 1,024 instances per step, max 96 optimization steps, KL coefficient 0.001, entropy coefficient 0.0, clip ratio (high) 0.28, history window size 3 | Results on [BFCLv3](../benchmarks/bfcl.md) and two other benchmarks are on the paper page[^wangAgentWorldModel2026] |
| [WebSailor-V2](../papers/liWebSailorV2BridgingChasm2025.md) | Web agent, RL after an SFT cold start | not covered here; see the paper page | Larger batch and group sizes in place of dynamic sampling | See the paper page[^liWebSailorV2BridgingChasm2025] |
| [Weblica](../papers/karWeblicaScalableReproducible2026.md) | Qwen3-VL visual web agents, RL after SFT | [LLM-as-judge](llm-as-a-judge.md) reward | Dr. GRPO. Selected values: learning rate 1e-5 or 5e-6, KL coefficient 0, 0.005, or 0.01, batch size 128 or 256, 4 or 8 rollouts per prompt, PPO mini-batch size 32 | Weblica-8B reaches 39.2% pass@1 on [Online-Mind2Web](../benchmarks/online-mind2web.md), from 28.6% for the base model[^karWeblicaScalableReproducible2026] |

Further notes:

- Agent World Model raises the clip ratio to 0.28, following a recommendation from DAPO, to allow more exploration, and uses sequence-level importance sampling to reduce the distribution shift between the rollout engine and the training engine.[^wangAgentWorldModel2026]
- Weblica oversamples rollouts and keeps only groups with mixed success signals, similar to DAPO.[^karWeblicaScalableReproducible2026]
- WebSailor-V2 observes that an unfiltered set of negative trajectories significantly degrades training stability and can lead to a "format collapse" after extended training. It excludes, for instance, trajectories that give no final answer because they exceed a length limit.[^liWebSailorV2BridgingChasm2025]
- [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md) does not use GRPO. It trains offline with [DPO](dpo.md) and says its method could run for several iterations with GRPO or PPO as an online algorithm.[^daAgentRLVRTrainingSoftware2025]
- SWE-RM analyzes reward-model errors with a simple policy gradient, which it says has the same nature as GRPO and GSPO, so the analysis extends to GRPO.[^shumSWERMExecutionfreeFeedback2025]

## Strengths & Limitations

- WebSailor-V2 reports that, in its experiments, the specific RL algorithm is not the primary bottleneck for agentic RL. The quality and distribution of the training data, and how negative trajectories are handled, matter more.[^liWebSailorV2BridgingChasm2025]
- Agent-RLVR states that online, on-policy RL generally outperforms offline DPO, but needs additional infrastructure for the online environment.[^daAgentRLVRTrainingSoftware2025]
- SWE-RM chooses GSPO over GRPO for stability when the policy is a mixture-of-experts model.[^shumSWERMExecutionfreeFeedback2025]

# Contradictions

**The SWE-RL reward as described by another paper.** SWE-RL defines its reward as the sequence similarity between the predicted and oracle patch, computed with Python's `difflib.SequenceMatcher`.[^weiSWERLAdvancingLLM2025] Agent-RLVR describes SWE-RL as using "GRPO and a cosine similarity scoring function".[^daAgentRLVRTrainingSoftware2025] The two descriptions name different similarity measures. SWE-RL is the primary source for its own reward.

## Related

- Methods: [DPO](dpo.md), [LLM-as-a-judge](llm-as-a-judge.md), [Execution-free verifier](execution-free-verifier.md)
- Benchmarks: [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [Online-Mind2Web](../benchmarks/online-mind2web.md), [BFCL](../benchmarks/bfcl.md)

[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
[^wangAgentWorldModel2026]: Wang et al. 2026
[^liWebSailorV2BridgingChasm2025]: Li et al. 2025
[^karWeblicaScalableReproducible2026]: Kar et al. 2026
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
