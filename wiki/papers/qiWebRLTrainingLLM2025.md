---
type: Paper
title: "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning"
description: Online curriculum reinforcement learning framework that trains open LLMs into web agents using self-generated tasks, a learned outcome reward model, and a KL-constrained off-policy update.
tags: [web-agents, reinforcement-learning, curriculum-learning, llm-agents, reward-model, ai899]
collections: [ai899]
authors: [Zehan Qi, Xiao Liu, Iat Long Iong, Hanyu Lai, Xueqiao Sun, Wenyi Zhao, Yu Yang, Xinyue Yang, Jiadai Sun, Shuntian Yao, Tianjie Zhang, Wei Xu, Jie Tang, Yuxiao Dong]
doi: 10.48550/arXiv.2411.02337
arxiv: "2411.02337"
arxiv_version: 2411.02337v3
code: https://github.com/THUDM/WebRL
sources:
  - id: qiWebRLTrainingLLM2025
    resource: zotero://select/items/@qiWebRLTrainingLLM2025
    title: "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning"
---

# WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning

Text source: arXiv HTML, version `2411.02337v3`.

## Summary

Existing LLM web agents rely on expensive proprietary LLM APIs, while open LLMs lack the decision-making capabilities needed for web tasks.[^qiWebRLTrainingLLM2025] [WebRL](../methods/webrl.md) is a self-evolving online curriculum reinforcement learning framework that trains open LLMs as web agents inside the [WebArena](../benchmarks/webarena.md) environment.[^qiWebRLTrainingLLM2025] It targets three challenges: the scarcity of training tasks, sparse feedback signals, and policy distribution drift in online learning.[^qiWebRLTrainingLLM2025]

On [WebArena-Lite](../benchmarks/webarena-lite.md), WebRL improves the success rate of Llama-3.1-8B from 4.8% to 42.4% and of GLM-4-9B from 6.1% to 43%, and Llama-3.1-70B reaches 49.1%.[^qiWebRLTrainingLLM2025] The paper compares these with GPT-4-Turbo (17.6%), GPT-4o (13.9%), and [AutoWebGLM](../methods/autowebglm.md) (18.2%), the previous state-of-the-art web agent trained on open LLMs.[^qiWebRLTrainingLLM2025]

## Contributions

- WebRL, a self-evolving online curriculum RL framework for training LLM-based web agents, including the infrastructure for RL in the WebArena environment and a strong outcome-supervised reward model (ORM).[^qiWebRLTrainingLLM2025]
- A self-evolving curriculum and adaptive learning strategies that address the scarcity of training tasks, the sparsity of feedback signals, and distribution drift in online learning.[^qiWebRLTrainingLLM2025]
- Improvements over AWR and DigiRL and state-of-the-art results on WebArena-Lite. The paper states that WebRL surpasses the best proprietary LLM API and the previously trained web agent on open LLMs by over 160% relatively.[^qiWebRLTrainingLLM2025]

## Method

### Problem formulation

A web task is a finite-horizon Markov Decision Process $(S,A,R,\mathcal{T})$. The state is the HTML content of the current web page plus the history of previous actions. The agent receives a reward of 1 on successful task completion and 0 otherwise. A trajectory ends when the task is accomplished or when the maximum number of interactions $T$ is exceeded.[^qiWebRLTrainingLLM2025]

### Outcome-supervised reward model (ORM)

- The [ORM](../methods/outcome-supervised-reward-model.md) $\mathcal{M}_{\text{ORM}}$ is an LLM trained to judge whether a rollout trajectory accomplishes a task. It gives a binary reward (0 for failure, 1 for success).[^qiWebRLTrainingLLM2025]
- Its input is the instruction $I$, the historical actions, and the HTML of the final state only. It outputs "YES" or "NO". The reward is 1 if the probability of generating "YES" is higher than that of "NO", and 0 otherwise.[^qiWebRLTrainingLLM2025]
- Training data: WebArena-Lite provides 1,186 training samples, each with an instruction, a trajectory, and a reward function. The authors rewrite the instructions, collect rollouts from all baseline methods on the augmented set, and combine them with the original samples for a total of 12,200 samples, labeled by the associated reward function.[^qiWebRLTrainingLLM2025]
- The ORM is needed because tasks generated later by the curriculum have no predefined reward functions.[^qiWebRLTrainingLLM2025]

### Self-evolving curriculum

- Each phase generates new instructions in two steps, generation and filtering.[^qiWebRLTrainingLLM2025]
- Generation: instructions that the model failed to complete in previous phases are the seeds, and new instructions are created with the in-breadth evolving approach. GPT-4o generates the instructions.[^qiWebRLTrainingLLM2025]
- Filtering: the trained critic scores each new instruction from its initial state, and instructions with critic scores between 0.05 and 0.75 are kept. A prompt with GPT-4o then excludes tasks that are infeasible in WebArena.[^qiWebRLTrainingLLM2025]
- In each phase, 500 new instructions that meet the filtering criteria are selected.[^qiWebRLTrainingLLM2025]

### KL-constrained policy update

The policy of the previous phase is $\pi_{\text{ref}}$ and the current policy is $\pi_{\theta}$. The objective adds a KL-divergence constraint between them, with coefficient $\beta$, to limit policy distribution drift between phases.[^qiWebRLTrainingLLM2025] The resulting policy loss is

$$
\mathcal{L}(\pi_{\theta})=\mathbb{E}_{\nu}\left[\left(\beta\log\frac{\pi_{\theta}(a|s,I)}{\pi_{\text{ref}}(a|s,I)}-A^{*}(s,a,I)\right)^{2}\right]
$$

where $\nu$ is the distribution of experience in the phase. The algorithm is off-policy.[^qiWebRLTrainingLLM2025]

- When the advantage is positive, the probability of the action increases, and the increase is amplified if $\pi_{\theta}$ is lower than $\pi_{\text{ref}}$. When the advantage is negative, the probability decreases, and the KL constraint limits the decrease if $\pi_{\theta}$ is already lower than $\pi_{\text{ref}}$.[^qiWebRLTrainingLLM2025]
- Advantage estimation: a value network $V(s_t, I)$ is trained with a cross-entropy objective, and the advantage is computed with [Generalized Advantage Estimation](../methods/generalized-advantage-estimation.md) using only the next-step and final-step estimators, $A(s_{t},a_{t},I)=\lambda\big(r(s_{t},a_{t},I)+V(s_{t+1},I)-V(s_{t},I)\big)+(1-\lambda)\big(r(s_{T},a_{T},I)-V(s_{t},I)\big)$, with $\lambda$ set to 0.5.[^qiWebRLTrainingLLM2025]
- A discount factor of 0.9 is used in the experiments.[^qiWebRLTrainingLLM2025]

Comparison with other algorithms as described in the text of Appendix A.3 (Table 4 of the source lost its cell contents in extraction):[^qiWebRLTrainingLLM2025]

| Algorithm | Difference stated by the paper |
|---|---|
| [DPO](../methods/dpo.md) | Requires pair-wise data, which is hard to obtain in web tasks because state backtracking on web pages is difficult. |
| PPO | On-policy, with low sampling efficiency; requires large amounts of data for stable improvement. |
| [AWR](../methods/advantage-weighted-regression.md) | Constrains the KL divergence to the behavioral policy of the training data instead of the reference policy, and does not directly reduce the probability of incorrect actions. |

All rows: [^qiWebRLTrainingLLM2025]

### Experience replay buffer with actor confidence filtering

- Only successful trajectories from each phase are stored in the [replay buffer](../methods/experience-replay.md).[^qiWebRLTrainingLLM2025]
- In phase $i$, the actor from the last phase computes the perplexity of all actions in the buffer. Actions with perplexity within 1/0.95 to 1/0.5, with their states, are added to the training data of the current phase.[^qiWebRLTrainingLLM2025]
- The amount of historical data used is limited to twice the size of the interaction data.[^qiWebRLTrainingLLM2025]

### Training process

1. Supervised fine-tuning (SFT) on the WebArena-Lite training dataset.[^qiWebRLTrainingLLM2025]
2. The replay buffer and failure set are initialized by running the SFT-trained model on the instructions of the WebArena-Lite training dataset.[^qiWebRLTrainingLLM2025]
3. The actor is initialized from the SFT-trained model, and the critic is the SFT-trained model with a randomly initialized value head.[^qiWebRLTrainingLLM2025]
4. Each phase: generate and filter instructions, roll out the current policy, label rollouts with the ORM, select replay experiences by perplexity, train the actor and critic, then add successes to the replay buffer and failures to the failure set.[^qiWebRLTrainingLLM2025]

The agent observes the user instruction, the action history, and simplified webpage HTML in which clickable elements carry element IDs. The action set is Click, Hover, Type, Search, Press, Scroll, Select_dropdown_option, New_tab, Tab_focus, Close_tab, Goto, Go_back, Go_forward, and Exit.[^qiWebRLTrainingLLM2025]

WebRL hyperparameters (Table 5): actor learning rate 1e-6, critic learning rate 1e-6, constant lr scheduler for both, batch size 128, discount factor 0.9, actor training epoch 1, critic training epoch 1, rollout temperature 1.[^qiWebRLTrainingLLM2025] ORM hyperparameters (Table 6): learning rate 5e-6, cosine lr scheduler, warmup ratio 0.1, batch size 128, training epoch 4, cutoff length 16384.[^qiWebRLTrainingLLM2025]

## Experiments & Results

### Setup

- Environment: WebArena, with five websites: OpenStreetMap (Map), Reddit, GitLab, online store content management system (CMS), and OneStopShop (OSS). The original WebArena provides 812 instructions. The evaluation uses 165 test cases from WebArena-Lite.[^qiWebRLTrainingLLM2025]
- Proprietary baselines: GPT-4-Turbo-2024-0409 and GPT-4o with a simple prompt, plus [AWM](../methods/agent-workflow-memory.md) and [WebPilot](../methods/webpilot.md).[^qiWebRLTrainingLLM2025]
- Open-model baselines on Llama3.1 and GLM-4-9B: the simple prompt, SFT (imitation learning on WebArena-Lite human-labeled demonstrations), [Filtered BC](../methods/filtered-behavior-cloning.md), [AWR](../methods/advantage-weighted-regression.md), and [DigiRL](../methods/digirl.md).[^qiWebRLTrainingLLM2025]
- RL baselines other than DigiRL use the interaction data from WebRL's first phase, so they are offline RL. DigiRL is trained online on the first-phase instructions and conducts 8 rounds of interaction and training.[^qiWebRLTrainingLLM2025]

### Main results (Table 1)

Task success rate (SR) on WebArena-Lite. `*` marks results on full WebArena taken from the literature.[^qiWebRLTrainingLLM2025]

| Models | #Params | Reddit | Gitlab | CMS | Map | OSS | Avg. SR |
|---|---|---|---|---|---|---|---|
| GPT-4-Turbo | N/A | 10.5 | 16.7 | 14.3 | 36.7 | 13.3 | 17.6 |
| GPT-4o | N/A | 10.5 | 10.0 | 20.0 | 20.0 | 11.1 | 13.9 |
| AWM + GPT-4-0613* | N/A | 50.9 | 31.8 | 29.1 | 43.3 | 30.8 | 35.5 |
| WebPilot + GPT-4o* | N/A | 65.1 | 39.4 | 24.7 | 33.9 | 36.9 | 37.2 |
| AutoWebGLM | 6B | 9.4 | 15.0 | 28.6 | 24.8 | 17.1 | 18.2 |
| GLM-4-Chat | 9B | 5.3 | 10.0 | 6.7 | 3.3 | 6.7 | 6.1 |
| GLM-4 + SFT (BC) | 9B | 47.4 | 13.3 | 31.4 | 23.3 | 13.3 | 22.4 |
| GLM-4 + Filtered BC | 9B | 52.6 | 10.0 | 31.4 | 26.7 | 20.0 | 24.8 |
| GLM-4 + AWR | 9B | 52.6 | 16.7 | 34.3 | 30.0 | 22.2 | 27.9 |
| GLM-4 + DigiRL | 9B | 63.2 | 30.0 | 34.3 | 26.7 | 26.7 | 31.5 |
| GLM-4 + WebRL | 9B | 57.9 | 50.0 | 48.6 | 36.7 | 37.8 | 43.0 |
| Llama3.1-Instruct | 8B | 0.0 | 3.3 | 2.9 | 3.3 | 11.1 | 4.8 |
| Llama3.1 + SFT (BC) | 8B | 36.8 | 6.7 | 20.0 | 33.3 | 17.8 | 20.6 |
| Llama3.1 + Filtered BC | 8B | 52.6 | 20.0 | 31.4 | 23.3 | 8.9 | 23.0 |
| Llama3.1 + AWR | 8B | 57.9 | 26.7 | 31.4 | 26.7 | 17.8 | 28.5 |
| Llama3.1 + DigiRL | 8B | 57.9 | 26.7 | 37.1 | 33.3 | 17.8 | 30.3 |
| Llama3.1 + WebRL | 8B | 63.2 | 46.7 | 54.3 | 36.7 | 31.1 | 42.4 |
| Llama3.1-Instruct | 70B | 10.5 | 16.7 | 17.1 | 20.0 | 4.4 | 12.7 |
| Llama3.1 + SFT (BC) | 70B | 52.6 | 20.0 | 20.0 | 26.7 | 13.3 | 23.0 |
| Llama3.1 + WebRL | 70B | 78.9 | 50.0 | 54.3 | 40.0 | 44.4 | 49.1 |

All rows: [^qiWebRLTrainingLLM2025]

- For Llama3.1-70B, the paper describes the 49.1% result as a 26.1% improvement over the accuracy achieved with SFT.[^qiWebRLTrainingLLM2025]
- The paper attributes the gap over SFT and Filtered BC to imitation learning over-repeating frequent actions such as "Scroll Down", and the gap over DigiRL to DigiRL updating on a predefined, fixed set of tasks.[^qiWebRLTrainingLLM2025]
- Error types: WebRL reduces the "Get Stuck Midway" error, especially compared with SFT and Filtered BC, and has the lowest error rate on "Stop at Wrong Page" and "Fail to Make Reasonable Attempt". The values are given only in a figure.[^qiWebRLTrainingLLM2025]
- Task length: SFT and Filtered BC decline as task length increases, and DigiRL struggles on tasks of more than 10 steps. The values are given only in a figure.[^qiWebRLTrainingLLM2025]

### Replay buffer perplexity filter (Table 2)

Tested in the first learning phase. Columns are the perplexity range of replay data used for training.[^qiWebRLTrainingLLM2025]

| $[1,\infty]$ | $[1,\frac{1}{0.95}]$ | $[\frac{1}{0.95},\frac{1}{0.5}]$ | $[\frac{1}{0.5},\infty]$ |
|---|---|---|---|
| 29.1 | 27.9 | 31.5 | 23.0 |

All values: [^qiWebRLTrainingLLM2025]

### ORM evaluation (Table 3)

Accuracy of the ORM against baselines adopted from Pan et al. (2024), on the WebArena-Lite test set (labels from its reward function) and on 100 sampled rollouts that are manually labeled.[^qiWebRLTrainingLLM2025]

| | Our ORM (8B) | GPT-4 | Captioner + GPT-4 | GPT-4V |
|---|---|---|---|---|
| Test Dataset (%) | 80.8 | 71.9 | 72.6 | 71.2 |
| Rollout (%) | 79.4 | 71.2 | 73.3 | 70.5 |

All values: [^qiWebRLTrainingLLM2025]

### Ablations

- Without the replay buffer, performance worsens over time, both with and without the KL-constrained update.[^qiWebRLTrainingLLM2025]
- Without the KL-constrained update (REINFORCE with a value function baseline, replay buffer kept), WebRL consistently performs worse. Without a replay buffer, REINFORCE with a value function baseline consistently underperforms its initial value.[^qiWebRLTrainingLLM2025]
- Without curriculum learning (only first-phase instructions), performance still trends upward but progresses more slowly and reaches a lower ceiling.[^qiWebRLTrainingLLM2025]
- $\beta$: with $\beta$ = 0.01, performance deteriorates with or without a replay buffer. Without the replay buffer, performance declines again when $\beta$ is too large ($\beta\geq 1$). With the replay buffer, performance stays high at larger $\beta$ values.[^qiWebRLTrainingLLM2025]
- Adding curriculum learning to DigiRL significantly enhances its performance, but it remains below WebRL. WebRL without curriculum learning still slightly surpasses DigiRL.[^qiWebRLTrainingLLM2025]
- Including failed trajectories in the replay buffer leads to slower and more volatile performance improvement.[^qiWebRLTrainingLLM2025]
- Four runs with distinct random seeds show an overall upward trend across phases.[^qiWebRLTrainingLLM2025]

Task-generation prompt stability (Table 7), measured after eight phases of training:[^qiWebRLTrainingLLM2025]

| Prompt 1 | Prompt 2 | Prompt 3 |
|---|---|---|
| 42.4 | 40.6 | 43.6 |

All values: [^qiWebRLTrainingLLM2025]

## Limitations

- On the Map website, the per-site curve of Llama3.1-8B rises and then declines. The authors hypothesize a trade-off with the significant increase on OSS and CMS, which also causes a slight decline on GitLab.[^qiWebRLTrainingLLM2025]
- WebRL and DigiRL with curriculum learning show a higher standard deviation, which the authors attribute to the randomness in task generation.[^qiWebRLTrainingLLM2025]
- Instruction generation and the infeasible-task filter both use GPT-4o, a proprietary model.[^qiWebRLTrainingLLM2025]
- Evaluation uses the 165 test cases of WebArena-Lite, chosen because of the cost of testing, and the AWM and WebPilot rows are results on full WebArena taken from the literature.[^qiWebRLTrainingLLM2025]
- The paper has no dedicated limitations section.

## Related

- Proposed: [WebRL](../methods/webrl.md), [Outcome-supervised reward model](../methods/outcome-supervised-reward-model.md)
- Builds on: [Generalized Advantage Estimation](../methods/generalized-advantage-estimation.md), [Experience replay](../methods/experience-replay.md)
- Compared against: [DigiRL](../methods/digirl.md), [Advantage-weighted regression](../methods/advantage-weighted-regression.md), [Filtered behavior cloning](../methods/filtered-behavior-cloning.md), [AutoWebGLM](../methods/autowebglm.md), [Agent Workflow Memory](../methods/agent-workflow-memory.md), [WebPilot](../methods/webpilot.md), [DPO](../methods/dpo.md)
- Benchmarks: [WebArena](../benchmarks/webarena.md), [WebArena-Lite](../benchmarks/webarena-lite.md)
- Papers in this wiki cited by this paper: [WebArena](zhouWebArenaRealisticWeb2024.md)

[^qiWebRLTrainingLLM2025]: Qi et al. 2025
