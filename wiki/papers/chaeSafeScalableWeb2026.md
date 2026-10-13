---
type: Paper
title: Safe and Scalable Web Agent Learning via Recreated Websites
description: VeriEnv uses a coding agent to clone real websites into executable synthetic environments with a Python SDK, so web agents can train on self-generated tasks with deterministic, programmatically verified rewards.
tags: [web-agents, synthetic-environments, verifiable-rewards, self-evolving-agents, task-generation, coding-agents, ai899]
collections: [ai899]
authors: [Hyungjoo Chae, Jungsoo Park, Alan Ritter]
year: 2026
doi: 10.48550/arXiv.2603.10505
arxiv: "2603.10505"
arxiv_version: 2603.10505v1
code: https://github.com/kyle8581/VeriEnv
sources:
  - id: chaeSafeScalableWeb2026
    resource: zotero://select/items/@chaeSafeScalableWeb2026
    title: Safe and Scalable Web Agent Learning via Recreated Websites
---

# Safe and Scalable Web Agent Learning via Recreated Websites

Text source: arXiv HTML, version `2603.10505v1`.

## Summary

Training web agents on real websites is unsafe or restricted (actions can interfere with other users, violate platform policies, or be blocked by Cloudflare and CAPTCHAs), and self-generated tasks are often underspecified and scored by an [LLM-as-a-judge](../methods/llm-as-a-judge.md), which can be error-prone.[^chaeSafeScalableWeb2026] [VeriEnv](../methods/verienv.md) uses a coding agent to clone a target website into an executable synthetic environment with its frontend, backend logic, and database, and exposes internal access through a Python SDK. Tasks are generated together with executable validation programs, so rewards are deterministic and do not depend on heuristic or LLM-based judges.[^chaeSafeScalableWeb2026]

The paper reports that agents trained with VeriEnv generalize to unseen websites on [WebArena-Lite](../benchmarks/webarena-lite.md) and [Mind2Web-Online](../benchmarks/online-mind2web.md), improve on a fixed website through self-evolving training, and improve as the number of training environments grows.[^chaeSafeScalableWeb2026] The code is to be released upon acceptance.[^chaeSafeScalableWeb2026]

## Contributions

- VeriEnv, a framework that automatically reconstructs real-world websites into executable synthetic environments and generates verifiable tasks.[^chaeSafeScalableWeb2026]
- Experiments on WebArena and Mind2Web-Online showing that agents trained within VeriEnv generalize to unseen websites.[^chaeSafeScalableWeb2026]
- Analyses of verifiability in task construction and reward assignment, of environment scaling, and of coding agents.[^chaeSafeScalableWeb2026]

## Method

### Recreating websites

- A coding agent receives screenshots of a real website $E$ and reconstructs it as a synthetic environment $\tilde{E} = (\mathcal{C},\mathcal{D},\mathcal{P})$: executable application code $\mathcal{C}$, database state $\mathcal{D}$, and a Python SDK $\mathcal{P}$ for querying and verifying environment state.[^chaeSafeScalableWeb2026]
- The agent has local file system and terminal access, and also writes control scripts such as server startup and reset utilities.[^chaeSafeScalableWeb2026]
- After the first implementation the agent interacts with the deployed site through Playwright MCP, finds functional discrepancies, and patches bugs iteratively.[^chaeSafeScalableWeb2026]
- Implementation: GPT-5.2 as the backbone LLM and Cursor CLI as the coding agent. Cloning takes 83.5 minutes and costs $3.6 per website on average, including debugging and task generation. The website list and screenshots come from [Mind2Web](../datasets/mind2web.md).[^chaeSafeScalableWeb2026]

### Verifiable task and judge generation

Each task is a natural language description plus a validation program written with the SDK. The program validates that the task is executable and produces a verifiable judge. At the end of an episode the judge evaluates the terminal state deterministically and returns a binary reward.[^chaeSafeScalableWeb2026] Judge criteria in the examples include `must_include`, `must_include_all`, `exact_match`, and `fuzzy_match`.[^chaeSafeScalableWeb2026]

### Self-evolving training

The agent solves a sampled task in the cloned website, the validation program scores the trajectory by querying the database through the SDK, and the verified rewards update the agent. The paper uses reward-based [rejection fine-tuning](../methods/rejection-fine-tuning.md): for each generated task, agent trajectories are sampled and only those that satisfy the validation criteria are kept as supervised training data.[^chaeSafeScalableWeb2026]

### Environment statistics (Table 1)

| Statistic | Value |
|---|---|
| Number of websites | 149 |
| Number of tasks per website | 49.5 |
| Total number of tasks | 7,400 |
| Easy tasks | 2,972 (40.2%) |
| Medium tasks | 2,900 (39.2%) |
| Hard tasks | 1,528 (20.6%) |

All rows: [^chaeSafeScalableWeb2026]

Difficulty labels follow predefined criteria on action length, statefulness, and authentication requirements.[^chaeSafeScalableWeb2026]

### Comparison with existing datasets and benchmarks (Table 2)

| Dataset / Benchmark | # Websites | # Tasks | Browser Interaction | Verifiable Judge | Scalable Task Gen. |
|---|---|---|---|---|---|
| WebArena | 5 | 812 | yes | yes | no |
| WorkArena | 1 | 33 | yes | yes | no |
| WebVoyager | 15 | 643 | yes | no | no |
| Mind2Web | 137 | 2,350 | no | yes | no |
| Mind2Web-Online | 136 | 300 | yes | no | no |
| Mind2Web-Live | 137 | 542 | yes | no | no |
| VeriEnv (Ours) | 149 | 7,400 | yes (w/ synthetic websites) | yes | yes |

All rows: [^chaeSafeScalableWeb2026]

## Experiments & Results

### Human evaluation of environments and tasks (Table 3)

Four graduate students with computer science background annotated two subsets, 15 instances per annotator, with double annotation per subset.[^chaeSafeScalableWeb2026]

| Metric | Result |
|---|---|
| Functional correctness (avg.) | 90% |
| Signup | 94% |
| Login | 95% |
| Search | 81% |
| Filter | 88% |
| Navigation | 100% |
| Forms | 100% |
| Visual rating (Likert, 1–5) | 4.7 |
| Task executability | 90% |
| Judge correctness | 76% |

All rows: [^chaeSafeScalableWeb2026]

- The running text gives the functionality average as 90.3%.[^chaeSafeScalableWeb2026]
- Mean Cohen's $\kappa=0.61$ on the binary judgments.[^chaeSafeScalableWeb2026]
- The most common judge errors come from database resets that do not preserve the random seeds used to populate website data. The paper states these can be detected and resolved by re-running the validation programs.[^chaeSafeScalableWeb2026]

### Setup for cross-domain generalization

- Base models: Qwen3-4B and LLaMA-3.2-3B-Instruct, trained by rejection-based fine-tuning on 97 websites. Websites that overlap with the test split of the evaluation benchmarks are excluded from cloning and training.[^chaeSafeScalableWeb2026]
- Training: LLaMA-Factory, learning rate $1\times 10^{-5}$, two epochs, linear warmup over the first 10% of steps, maximum sequence length 8,000 tokens, DeepSpeed ZeRO-3, gradient accumulation step of 2, two NVIDIA A40 GPUs.[^chaeSafeScalableWeb2026]
- Benchmarks: WebArena-Lite (5 websites in Docker) and Mind2Web-Online (300 tasks with three difficulty levels). Tasks on websites that block web agents are excluded from Mind2Web-Online, leaving 220 tasks. Trajectories are scored with the WebJudge-7B model.[^chaeSafeScalableWeb2026]
- Baselines: proprietary LLMs (GPT-4o-mini, GPT-4o, Claude-3.5-Sonnet), and open-source agents trained with [Synatra](../methods/synatra.md) and [Agent Data Protocol (ADP)](../methods/agent-data-protocol.md).[^chaeSafeScalableWeb2026]

### WebArena-Lite (Table 4)

Rows marked `*` use numbers reported by Chae et al. (2025).[^chaeSafeScalableWeb2026]

| Method | Shopping | CMS | Reddit | GitLab | Map | Total | Δ |
|---|---|---|---|---|---|---|---|
| GPT-4o-mini\* | 21.74 | 22.86 | 19.05 | 34.38 | 19.35 | 23.64 | – |
| GPT-4o\* | 23.91 | 31.43 | 28.57 | 56.25 | 19.35 | 31.52 | – |
| Qwen3-4B | 3.77 | 6.67 | 4.17 | 13.89 | 14.29 | 7.88 | – |
| +Synatra | 0.00 | 0.00 | 12.50 | 8.33 | 0.00 | 3.64 | $-4.24$ |
| +ADP | 4.35 | 5.71 | 9.52 | 3.13 | 9.68 | 6.06 | $-1.82$ |
| +VeriEnv (Ours) | 4.35 | 20.00 | 23.81 | 12.50 | 16.13 | 13.94 | +6.06 |
| LLaMA-3.2-3B-Instruct | 0.00 | 2.86 | 9.52 | 3.13 | 3.23 | 3.03 | – |
| +Synatra | 2.17 | 2.86 | 14.29 | 9.38 | 6.45 | 6.06 | +3.03 |
| +ADP | 4.35 | 11.43 | 14.29 | 12.50 | 6.45 | 9.09 | +6.06 |
| +VeriEnv (Ours) | 4.35 | 17.14 | 19.05 | 15.63 | 12.90 | 12.73 | +9.70 |

All rows: [^chaeSafeScalableWeb2026]

### Mind2Web-Online (Table 5)

Rows marked `*` use numbers reported by Xue et al. (2025).[^chaeSafeScalableWeb2026]

| Method | Easy | Medium | Hard | Total | Δ |
|---|---|---|---|---|---|
| Browser-Use-GPT-4o\* | 55.40 | 26.60 | 8.10 | 30.00 | – |
| Claude-3.5-Sonnet\* | 56.60 | 26.60 | 6.80 | 28.80 | – |
| Qwen3-4B | 26.32 | 9.41 | 11.63 | 13.18 | – |
| +Synatra | 35.09 | 5.88 | 9.30 | 14.55 | $+1.37$ |
| +ADP | 26.32 | 7.06 | 6.98 | 11.36 | $-1.82$ |
| +VeriEnv (Ours) | 29.82 | 23.53 | 6.98 | 20.45 | +7.27 |
| LLaMA-3.2-3B-Instruct | 19.30 | 12.94 | 0.00 | 11.36 | – |
| +Synatra | 24.56 | 15.29 | 6.98 | 14.55 | +3.19 |
| +ADP | 42.11 | 24.71 | 11.63 | 24.09 | +12.73 |
| +VeriEnv (Ours) | 40.35 | 29.41 | 13.95 | 24.55 | +13.19 |

All rows: [^chaeSafeScalableWeb2026]

The paper attributes ADP's gain with LLaMA-3.2-3B-Instruct on Mind2Web-Online to overlap between ADP's aggregated training data (including Mind2Web and NNetNav) and the evaluation distribution.[^chaeSafeScalableWeb2026]

### Site-specific mastery

Websites from [WebArena](../benchmarks/webarena.md) are cloned and agents are trained only inside the clones, then compared with [PAE](../methods/pae.md), which uses real websites, non-verifiable tasks, and LLM-based judges.[^chaeSafeScalableWeb2026] The paper states that VeriEnv yields larger and more stable gains than PAE across training phases, with the strongest improvements in CMS and Shopping.[^chaeSafeScalableWeb2026] The results are given only in Figure 4 (Base, Phase 1, Phase 2). The text states no numbers.[^chaeSafeScalableWeb2026]

### Environment scaling

Agent performance generally improves as the share of training environments increases, on both WebArena and Mind2Web-Online, while the Synatra and ADP baselines are shown as flat reference lines.[^chaeSafeScalableWeb2026] The results are given only in Figure 5 (0%, 25%, 50%, 75%, 100% of environments). The text states no numbers.[^chaeSafeScalableWeb2026]

### Error analysis of environment construction

- 39 websites out of 136 failed to be implemented. Figure 9 shows the filtering flow: 136 candidate websites, 118 after the server-script check (18 filtered), and 97 after task generation (21 filtered).[^chaeSafeScalableWeb2026]
- Primary failure reasons for the 39 filtered websites, read from the labels in Figure 7: `start_servers.sh` not created 35.9%, task generation failed 33.3%, incomplete clone (no front/back) 7.7%, frontend-only (no backend) 7.7%, SDK not created 7.7%, task generation not attempted 5.1%, `reset_servers.sh` not created 2.6%.[^chaeSafeScalableWeb2026]
- Among websites that ran but still had errors, port conflicts and CORS misconfigurations account for the majority of failures. The paper attributes port conflicts to deploying more than 100 web applications on a single server.[^chaeSafeScalableWeb2026]
- Coding agents and models: Claude CLI and OpenHands frequently ended the implementation early. Qwen3-Coder-30B-A3B-Instruct and GLM-4.7-Flash struggled with frontend issues and tool use, which the paper attributes to the lack of strong multimodal capabilities.[^chaeSafeScalableWeb2026]

### Inconsistencies inside the paper

- The WebArena gain for LLaMA-3.2-3B-Instruct is $+9.09$ in the introduction and Section 4.1, and +9.70 in Table 4 (12.73 vs 3.03).[^chaeSafeScalableWeb2026]
- Website counts: Table 1 and Table 2 give 149 websites and 7,400 tasks, training uses 97 websites, and the error analysis and Figure 9 start from 136 candidate websites of which 97 are validated.[^chaeSafeScalableWeb2026]
- Section 3.4 says 50 task instructions are generated per website, while Table 1 gives 49.5 tasks per website.[^chaeSafeScalableWeb2026]
- The Figure 3 caption calls the example a "synthetic recipe website (i.e., cloned from apartments.com)", while the task is about apartment listings.[^chaeSafeScalableWeb2026]

## Limitations

- Judge correctness is 76% in the human evaluation, lower than task executability at 90%.[^chaeSafeScalableWeb2026]
- The cloned environment is not identical to the original website.[^chaeSafeScalableWeb2026]
- Websites that rely on multimedia delivery, such as arXiv (PDF documents) or YouTube (video streams), are harder to reproduce faithfully.[^chaeSafeScalableWeb2026]
- 39 of 136 websites could not be implemented, mostly because of incomplete system setup.[^chaeSafeScalableWeb2026]
- Training uses rejection fine-tuning. Reinforcement learning on the environments is left to future work.[^chaeSafeScalableWeb2026]
- The trained 3B and 4B agents remain below the proprietary baselines in total score on both benchmarks (Tables 4 and 5).[^chaeSafeScalableWeb2026]
- Site-specific mastery and environment scaling results are reported only as plots.[^chaeSafeScalableWeb2026]
- The impact statement lists misuse risks (large-scale scraping, account abuse, manipulation of online services) and possible intellectual-property or terms-of-service concerns from recreating websites.[^chaeSafeScalableWeb2026]

## Related

- Proposed: [VeriEnv](../methods/verienv.md)
- Methods used or contrasted: [Rejection fine-tuning](../methods/rejection-fine-tuning.md), [LLM-as-a-judge](../methods/llm-as-a-judge.md)
- Compared against: [PAE](../methods/pae.md), [Synatra](../methods/synatra.md), [Agent Data Protocol (ADP)](../methods/agent-data-protocol.md)
- Benchmarks: [WebArena](../benchmarks/webarena.md), [WebArena-Lite](../benchmarks/webarena-lite.md), [Mind2Web-Online](../benchmarks/online-mind2web.md)
- Datasets: [Mind2Web](../datasets/mind2web.md)
- Papers in this wiki cited by this paper: [WebArena](zhouWebArenaRealisticWeb2024.md), [WebRL](qiWebRLTrainingLLM2025.md), [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md)

[^chaeSafeScalableWeb2026]: Chae et al. 2026
