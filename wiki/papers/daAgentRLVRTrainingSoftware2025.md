---
type: Paper
title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
description: RLVR training framework for software engineering agents that has the agent reattempt failed tasks with teacher-generated guidance and then updates the policy with offline DPO on unit-test rewards.
tags: [rlvr, reinforcement-learning, swe-agents, agent-training, guidance, reward-model, ai899]
collections: ["ai899"]
authors: [Jeff Da, Clinton Wang, Xiang Deng, Yuntao Ma, Nikhil Barhate, Sean Hendryx]
doi: 10.48550/arXiv.2506.11425
arxiv: "2506.11425"
arxiv_version: 2506.11425v2
sources:
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
---

# Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards

Text source: arXiv HTML, version `2506.11425v2`.

## Summary

[Reinforcement Learning from Verifiable Rewards (RLVR)](../methods/rlvr.md) works well in verifiable domains such as math and competitive programming, but its efficacy diminishes in agentic environments. Multi-step tasks have high failure rates even for frontier LLMs, so the reward landscape is too sparse for conventional RLVR.[^daAgentRLVRTrainingSoftware2025]

[Agent-RLVR](../methods/agent-rlvr.md) adds *agent guidance*: for tasks the agent fails, a teacher produces hints (a plan, feedback on the agent's errors, and pointers to the right file and location), and the agent reattempts the task with them. The policy is then updated with RLVR on the rewards of these trajectories.[^daAgentRLVRTrainingSoftware2025] With 817 training environments, Agent-RLVR raises the Pass@1 of Qwen-2.5-72B-Instruct on [SWE-Bench Verified](../benchmarks/swe-bench-verified.md) from 9.4% to 22.4%, and a reward model trained on the same data raises it further to 27.8%.[^daAgentRLVRTrainingSoftware2025]

## Contributions

- Agent-RLVR, a framework that makes RLVR effective for agents by adding pedagogical guidance without changing the verifiability of the reward signal.[^daAgentRLVRTrainingSoftware2025]
- A curated dataset of SWE tasks with problem statements, environments, and guidance.[^daAgentRLVRTrainingSoftware2025]
- Empirical results on SWE-bench Verified: Pass@1 from 9.4% to 22.4%; guidance improves Pass@1 (19.8% $\rightarrow$ 22.4%) and Pass@32 (34.2% $\rightarrow$ 38.4%); a reward model that ranks $k=32$ patch generations raises Pass@1 to 27.8%.[^daAgentRLVRTrainingSoftware2025]

## Method

### RLVR background

A reward function $r(x,y)$ judges prompt-response pairs, modulated by a KL penalty against a reference policy: $R(x,y)=r(x,y)-\beta\log\left[\frac{\pi_{\theta}(y|x)}{\pi_{\text{ref}}(y|x)}\right]$ (Eq. 1).[^daAgentRLVRTrainingSoftware2025] The paper optimizes with [DPO](../methods/dpo.md), which it expands as direct policy optimization. DPO samples pairs of winning responses $y_{w}$ and losing responses $y_{l}$ for the same input and uses the loss in Eq. 2.[^daAgentRLVRTrainingSoftware2025] In Agent-RLVR, $y_{w}$ passes all unit tests and $y_{l}$ fails one or more unit tests.[^daAgentRLVRTrainingSoftware2025]

### Task format

- **Issue description.** A GitHub issue (bug report or feature request) from a real open-source project.[^daAgentRLVRTrainingSoftware2025]
- **Repository.** A complete snapshot of a real-world Python codebase. No issues come from any repository in the SWE-Bench test set.[^daAgentRLVRTrainingSoftware2025]
- **Environment.** A fully functional Docker container. Each problem has its own runtime environment.[^daAgentRLVRTrainingSoftware2025]
- **Unit tests.** Regression tests and focused tests that check whether the issue is resolved. They provide the verifiable reward.[^daAgentRLVRTrainingSoftware2025]

### Guidance

The guidance generator sees the problem statement, the reference patch, and, for environment feedback guidance, the agent's previous trajectory and environment feedback. The paper uses an external LLM (claude-3-7-sonnet-20250219) in place of human annotators due to cost. Guidance is used at train time only. At test time inference is the same with and without guidance-trained models.[^daAgentRLVRTrainingSoftware2025]

| Type | Content |
|---|---|
| Plan | A series of suggested steps and/or a pointer to the crux of the problem, derived from the problem statement. |
| Environment feedback | Guidance that corrects the previous mistake, based on the feedback from the environment. |
| Environment interaction | The correct file and patch location, to mitigate navigation issues during localization. Follows Learn-by-Interact. |

All rows: [^daAgentRLVRTrainingSoftware2025]

### Training loop (Algorithm 1)

1. **Initial attempt.** The agent generates trajectories with the scaffold. A generated patch is validated by running the unit tests in the Docker image.[^daAgentRLVRTrainingSoftware2025]
2. **Guidance.** For failing trajectories (tests fail or no patch is generated), guidance is generated and the agent reattempts the problem with it. The new patches are graded.[^daAgentRLVRTrainingSoftware2025]
3. **Policy update.** For each correct trajectory, an incorrect (non-guidance) trajectory for the same problem is sampled to form a DPO pair. If the model has not yet been fine-tuned, it is first instruct-tuned with SFT on a 20% subset, and the SFT model becomes $\pi_{\text{ref}}$. DPO training on the pairs ends the iteration.[^daAgentRLVRTrainingSoftware2025]

The experiments in the paper run one iteration cycle. The method is offline, which lets environments run asynchronously.[^daAgentRLVRTrainingSoftware2025]

### Scaffold and reward model

- The scaffold is based on [Agentless](../methods/agentless.md), keeping only the localization and repair steps. The patch selection step, which needs test generation and execution, is removed.[^daAgentRLVRTrainingSoftware2025]
- The [reward model](../methods/reward-model.md) takes the generated patch and the problem statement and outputs a reward score. Base model Qwen-2.5-Coder-32B, trained on Agent-RLVR data (including guidance) with a pairwise loss, 1e-5 learning rate, 500 steps, warmup ratio 0.05. At inference, $k=32$ patches are generated and ranked to select one final patch.[^daAgentRLVRTrainingSoftware2025]

## Experiments & Results

### Setup

- Training dataset: 817 agent environments from 27 different repos, with 593 problems from [SWE-Gym](../datasets/swe-gym.md) and 219 self-collected problems. The final dataset has 8186 trajectories, of which 4093 are positive, generated by sampling 16 trajectories per problem in the guidance and non-guidance stages.[^daAgentRLVRTrainingSoftware2025]
- Data includes on-policy trajectories (generated by Qwen2.5-72B-Instruct) and off-policy trajectories (generated by the LLM used for guidance).[^daAgentRLVRTrainingSoftware2025]
- Models: the Qwen-2.5 family. Instruct-tuning: five epochs, learning rate 1e-5, sequence length 8k. RLVR: DPO, learning rate 1e-6, 1 epoch.[^daAgentRLVRTrainingSoftware2025]
- Evaluation: the verified portion of [SWE-Bench](../benchmarks/swe-bench.md) with the authors' evaluation harness, on Modal. 6 instances could not be compiled. All instances are still counted in the metrics.[^daAgentRLVRTrainingSoftware2025]
- Metrics: Pass@1 uses greedy decoding at all steps. Pass@k and Best@1 use greedy decoding for the first generation and temperature=0.6 for the rest.[^daAgentRLVRTrainingSoftware2025]
- SFT baseline (Agent-SFT): rejection sampling on trajectories that pass unit tests, the same 817 tasks, 5 epochs, learning rate 1e-5, cosine schedule, no guidance trajectories.[^daAgentRLVRTrainingSoftware2025]
- Compute: Nvidia H100 GPUs. Two nodes with 8 H100 GPUs each for the 14B and 32B experiments, 4 nodes with 8 H100 GPUs each for 72B. Train time is 4, 6, and 10 hours for 14B, 32B, and 72B.[^daAgentRLVRTrainingSoftware2025]

### Base vs trained models on SWE-Bench Verified (Table 1)

| Model | Pass@1 (STD) |
|---|---|
| Qwen-2.5-Coder-14B (base) | 6.8% ($\pm$2.2) |
| Qwen-2.5-Coder-32B (base) | 8.8% ($\pm$2.5) |
| Qwen-2.5-72B-Instruct (base) | 9.4% ($\pm$2.5) |
| Agent-RLVR-Qwen-2.5-Coder-14B | 18.0% ($\pm$3.4) |
| Agent-RLVR-Qwen-2.5-Coder-32B | 21.6% ($\pm$3.5) |
| Agent-SFT-Qwen-2.5-72B-Instruct | 20.8% ($\pm$3.5) |
| Agent-RLVR-Qwen-2.5-72B-Instruct | 22.4% ($\pm$3.6) |
| Agent-RLVR-RM-Qwen-2.5-72B-Instruct | 27.8% ($\pm$3.8) |

All rows: [^daAgentRLVRTrainingSoftware2025]

### Effect of guidance

Rollout success with and without guidance (Table 2):[^daAgentRLVRTrainingSoftware2025]

| Metric | Without guidance | With guidance |
|---|---|---|
| # of Successful Rollouts (avg) | 138 (16.9%) | 165 (20.3%) |
| Empty Patch % | 8.71% | 7.20% |

All rows: [^daAgentRLVRTrainingSoftware2025]

- The non-guidance model runs the same training cycle but excludes guidance-augmented data from DPO training. Guidance improves Pass@1 (19.8% $\rightarrow$ 22.4%) and Pass@32 (34.2% $\rightarrow$ 38.4%), and the gap grows as $k$ increases.[^daAgentRLVRTrainingSoftware2025]
- For SFT, guidance hurts (Table 4): SFT with guidance scores 16.8 and SFT without guidance scores 20.8. The paper attributes this to likely overfitting to the guidance prompt.[^daAgentRLVRTrainingSoftware2025]

### Comparison with other models on SWE-bench Verified (Table 3)

| Model (scaffold) | Pass@1 |
|---|---|
| Qwen-2.5-72B-Instruct | 9.4% |
| SWE-Gym-Qwen-2.5-Coder-32B (OpenHands) | 20.6% |
| GPT-4o (Agentless) | 38.8% |
| SWE-Fixer-72B | 30.2% |
| Llama3-SWE-RL-70B (Agentless) | 41.0% |
| DeepSeek-V3 (Agentless) | 42.0% |
| DeepSeek-R1 (Agentless) | 49.2% |
| Claude-3.5-Sonnet (Agentless) | 50.8% |
| Agent-RLVR-Qwen-2.5-Coder-32B | 21.6% |
| Agent-RLVR-Qwen-2.5-72B-Instruct | 22.4% |
| Agent-RLVR-RM-Qwen-2.5-72B-Instruct | 27.8% |

All rows: [^daAgentRLVRTrainingSoftware2025]

The paper notes that Agent-RLVR relies on a smaller training set, a simpler scaffold, and/or a less specialized training procedure: SWE-RL has 11M training instances and SWE-Gym has 2k.[^daAgentRLVRTrainingSoftware2025]

## Limitations

- **Programming languages.** The work is limited to Python.[^daAgentRLVRTrainingSoftware2025]
- **Dataset.** Training data covers a relatively small set of repositories due to cost. To the authors' knowledge there is only one substantial human-validated test set for SWE agents. Contamination with respect to pre-training is possible, although repositories do not overlap between training and test sets.[^daAgentRLVRTrainingSoftware2025]
- **Online versus offline RL.** Agent-RLVR is explored only as an offline algorithm. The authors hypothesize that an online, on-policy algorithm would give larger gains, and say Agent-RLVR could run for several iterations with GRPO or PPO.[^daAgentRLVRTrainingSoftware2025]
- The experiments cover one iteration cycle of the training loop.[^daAgentRLVRTrainingSoftware2025]
- Guidance is generated from the reference patch by an external LLM, not by humans.[^daAgentRLVRTrainingSoftware2025]
- Agent-RLVR models score below several entries in Table 3, including Llama3-SWE-RL-70B (41.0%) and SWE-Fixer-72B (30.2%).[^daAgentRLVRTrainingSoftware2025]
- The dataset counts do not add up as stated: 817 environments, but 593 problems from SWE-Gym and 219 self-collected problems.[^daAgentRLVRTrainingSoftware2025]

## Related

- Methods: [Agent-RLVR](../methods/agent-rlvr.md), [RLVR](../methods/rlvr.md), [DPO](../methods/dpo.md), [Reward model](../methods/reward-model.md)
- Systems compared or built on: [Agentless](../methods/agentless.md)
- Datasets: [SWE-Gym](../datasets/swe-gym.md)
- Benchmarks: [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [SWE-bench](../benchmarks/swe-bench.md)
- Papers in this wiki cited by this paper: [SWE-RL](weiSWERLAdvancingLLM2025.md), [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md), [WebRL](qiWebRLTrainingLLM2025.md)

[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
