---
type: Method
title: DPO
description: Policy optimization from pairs of winning and losing responses to the same input, which avoids explicitly modeling the reward and is used offline by Agent-RLVR.
tags: [reinforcement-learning, policy-optimization, preference-pairs, offline-rl, rlvr]
sources:
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
  - id: qiWebRLTrainingLLM2025
    resource: zotero://select/items/@qiWebRLTrainingLLM2025
    title: "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning"
---

# DPO

## Overview

DPO is a policy optimization method that learns from pairs of responses to the same input. It removes the need to explicitly model the reward function: it samples a winning response $y_{w}$ (higher reward) and a losing response $y_{l}$ (lower reward) for the same input $x$, and its loss drives the LLM towards the preferred response.[^daAgentRLVRTrainingSoftware2025] Agent-RLVR expands the name in its text as "direct policy optimization", while the work it cites for DPO is titled "Direct preference optimization: Your language model is secretly a reward model" in its reference list.[^daAgentRLVRTrainingSoftware2025] WebRL uses the abbreviation only and cites a work with the same title (Rafailov et al., 2024b), which is not in this wiki.[^qiWebRLTrainingLLM2025]

## How it works

The loss, as given in Agent-RLVR (Eq. 2), with reference policy $\pi_{\text{ref}}$ and hyperparameter $\beta$:[^daAgentRLVRTrainingSoftware2025]

$$\mathcal{L}_{\text{DPO}}(\theta)=-\mathbb{E}_{(x,y_{w},y_{l})\sim\mathcal{D}}\left[\log\sigma\left(\beta\left(\log\frac{\pi_{\theta}(y_{w}|x)}{\pi_{\text{ref}}(y_{w}|x)}-\log\frac{\pi_{\theta}(y_{l}|x)}{\pi_{\text{ref}}(y_{l}|x)}\right)\right)\right]$$

WebRL describes the same idea from the side of its own derivation: DPO solves for the optimal value of the KL-constrained objective and obtains the relationship between the optimal policy $\pi^{*}$ and the reward $r$. It then uses contrastive learning on paired data to build the learning target, which bypasses the need to estimate $r$.[^qiWebRLTrainingLLM2025]

## Papers using it

- **[Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md)** uses offline DPO as its policy update. $y_{w}$ is a trajectory that passes all unit tests, and $y_{l}$ is one that fails one or more unit tests.[^daAgentRLVRTrainingSoftware2025] For each correct trajectory, an incorrect non-guidance trajectory for the same problem is sampled to form a pair.[^daAgentRLVRTrainingSoftware2025] The model is first instruct-tuned with SFT (five epochs, learning rate 1e-5), and DPO then runs with a learning rate of 1e-6 for 1 epoch.[^daAgentRLVRTrainingSoftware2025] The dataset has 8186 trajectories, of which 4093 are positive.[^daAgentRLVRTrainingSoftware2025] On [SWE-Bench Verified](../benchmarks/swe-bench-verified.md), Qwen-2.5-72B-Instruct improves from a Pass@1 of 9.4% to 22.4%, against 20.8% for the SFT baseline (Agent-SFT).[^daAgentRLVRTrainingSoftware2025] When guidance-augmented data is excluded from DPO training, Pass@1 is 19.8%.[^daAgentRLVRTrainingSoftware2025]
- **[WebRL](../papers/qiWebRLTrainingLLM2025.md)** does not use DPO. It compares its algorithm against it: WebRL explicitly fits a value function $V$ to guide the policy, where DPO avoids estimating the reward.[^qiWebRLTrainingLLM2025] It also notes that AgentQ uses DPO for policy updates based on interaction data.[^qiWebRLTrainingLLM2025]

## Strengths & Limitations

- **No explicit reward model.** DPO does not need to model or estimate the reward function.[^daAgentRLVRTrainingSoftware2025][^qiWebRLTrainingLLM2025]
- **Works offline.** Agent-RLVR's use of DPO is offline, which lets it avoid the extra infrastructure of an online environment.[^daAgentRLVRTrainingSoftware2025]
- **Needs pair-wise data.** WebRL states that pair-wise data is challenging to obtain in web tasks, because state backtracking on web pages is difficult, so it is hard to collect the outcomes of different actions on the same page state.[^qiWebRLTrainingLLM2025]
- **Offline vs. online.** Agent-RLVR states that online, on-policy RL generally outperforms offline DPO, and hypothesizes that an online algorithm such as [GRPO](grpo.md) or PPO would give larger gains.[^daAgentRLVRTrainingSoftware2025]

## Related

- Methods: [GRPO](grpo.md), [Agentless](agentless.md)
- Datasets: [SWE-Gym](../datasets/swe-gym.md)
- Benchmarks: [SWE-Bench Verified](../benchmarks/swe-bench-verified.md)

[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^qiWebRLTrainingLLM2025]: Qi et al. 2025
