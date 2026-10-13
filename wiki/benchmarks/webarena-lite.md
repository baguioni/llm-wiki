---
type: Benchmark
title: WebArena-Lite
description: Human-verified subset of WebArena with 165 test cases, used to compare trained open-model web agents and proprietary LLM agents by task success rate.
tags: [web-agents, benchmark, llm-agents, evaluation]
sources:
  - id: qiWebRLTrainingLLM2025
    resource: zotero://select/items/@qiWebRLTrainingLLM2025
    title: "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning"
  - id: chaeSafeScalableWeb2026
    resource: zotero://select/items/@chaeSafeScalableWeb2026
    title: Safe and Scalable Web Agent Learning via Recreated Websites
---

# WebArena-Lite

## Setup

- WebArena-Lite is a human-verified subset of [WebArena](webarena.md).[^qiWebRLTrainingLLM2025]
- The original WebArena provides 812 instructions. Qi et al. evaluate on 165 test cases from WebArena-Lite, chosen because of the cost of testing.[^qiWebRLTrainingLLM2025]
- The websites are OpenStreetMap (Map), Reddit, GitLab, online store content management system (CMS), and OneStopShop (OSS).[^qiWebRLTrainingLLM2025] Chae et al. describe the benchmark as measuring task success across 5 realistic websites implemented within Docker.[^chaeSafeScalableWeb2026]
- **Metric.** Task success rate (SR), per website and on average.[^qiWebRLTrainingLLM2025]
- **Training split.** WebArena-Lite provides 1,186 training samples, each with an instruction, a trajectory, and a reward function.[^qiWebRLTrainingLLM2025]

## Results

### Reported by Qi et al. 2025 (Table 1)

Per-site columns are in the order Reddit, Gitlab, CMS, Map, OSS.[^qiWebRLTrainingLLM2025]

| System | Avg. SR | Per-site SR | Setting / budget | Reported by |
|---|---|---|---|---|
| Llama3.1 + WebRL | 49.1 | 78.9, 50.0, 54.3, 40.0, 44.4 | 70B, trained with WebRL | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| GLM-4 + WebRL | 43.0 | 57.9, 50.0, 48.6, 36.7, 37.8 | 9B, trained with WebRL | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| Llama3.1 + WebRL | 42.4 | 63.2, 46.7, 54.3, 36.7, 31.1 | 8B, trained with WebRL | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| GLM-4 + DigiRL | 31.5 | 63.2, 30.0, 34.3, 26.7, 26.7 | 9B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| Llama3.1 + DigiRL | 30.3 | 57.9, 26.7, 37.1, 33.3, 17.8 | 8B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| Llama3.1 + AWR | 28.5 | 57.9, 26.7, 31.4, 26.7, 17.8 | 8B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| GLM-4 + AWR | 27.9 | 52.6, 16.7, 34.3, 30.0, 22.2 | 9B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| GLM-4 + Filtered BC | 24.8 | 52.6, 10.0, 31.4, 26.7, 20.0 | 9B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| Llama3.1 + Filtered BC | 23.0 | 52.6, 20.0, 31.4, 23.3, 8.9 | 8B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| Llama3.1 + SFT (BC) | 23.0 | 52.6, 20.0, 20.0, 26.7, 13.3 | 70B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| GLM-4 + SFT (BC) | 22.4 | 47.4, 13.3, 31.4, 23.3, 13.3 | 9B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| Llama3.1 + SFT (BC) | 20.6 | 36.8, 6.7, 20.0, 33.3, 17.8 | 8B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| AutoWebGLM | 18.2 | 9.4, 15.0, 28.6, 24.8, 17.1 | 6B | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| GPT-4-Turbo | 17.6 | 10.5, 16.7, 14.3, 36.7, 13.3 | GPT-4-Turbo-2024-0409, simple prompt | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| GPT-4o | 13.9 | 10.5, 10.0, 20.0, 20.0, 11.1 | simple prompt | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| Llama3.1-Instruct | 12.7 | 10.5, 16.7, 17.1, 20.0, 4.4 | 70B, simple prompt | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| GLM-4-Chat | 6.1 | 5.3, 10.0, 6.7, 3.3, 6.7 | 9B, simple prompt | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |
| Llama3.1-Instruct | 4.8 | 0.0, 3.3, 2.9, 3.3, 11.1 | 8B, simple prompt | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) |

All rows: [^qiWebRLTrainingLLM2025]

The same table also lists AWM + GPT-4-0613 (35.5) and WebPilot + GPT-4o (37.2). Those two are results on full WebArena taken from the literature, so they are on the [WebArena](webarena.md) page.[^qiWebRLTrainingLLM2025]

### Reported by Chae et al. 2026 (Table 4)

Per-site columns are in the order Shopping, CMS, Reddit, GitLab, Map. Rows marked `*` use numbers reported by Chae et al. (2025).[^chaeSafeScalableWeb2026]

| System | Total | Per-site | Setting / budget | Reported by |
|---|---|---|---|---|
| GPT-4o\* | 31.52 | 23.91, 31.43, 28.57, 56.25, 19.35 | number from Chae et al. (2025) | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| GPT-4o-mini\* | 23.64 | 21.74, 22.86, 19.05, 34.38, 19.35 | number from Chae et al. (2025) | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| Qwen3-4B + VeriEnv | 13.94 | 4.35, 20.00, 23.81, 12.50, 16.13 | rejection-based fine-tuning on 97 cloned websites | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| LLaMA-3.2-3B-Instruct + VeriEnv | 12.73 | 4.35, 17.14, 19.05, 15.63, 12.90 | rejection-based fine-tuning on 97 cloned websites | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| LLaMA-3.2-3B-Instruct + ADP | 9.09 | 4.35, 11.43, 14.29, 12.50, 6.45 | open-source baseline | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| Qwen3-4B | 7.88 | 3.77, 6.67, 4.17, 13.89, 14.29 | base model | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| Qwen3-4B + ADP | 6.06 | 4.35, 5.71, 9.52, 3.13, 9.68 | open-source baseline | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| LLaMA-3.2-3B-Instruct + Synatra | 6.06 | 2.17, 2.86, 14.29, 9.38, 6.45 | open-source baseline | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| Qwen3-4B + Synatra | 3.64 | 0.00, 0.00, 12.50, 8.33, 0.00 | open-source baseline | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| LLaMA-3.2-3B-Instruct | 3.03 | 0.00, 2.86, 9.52, 3.13, 3.23 | base model | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |

All rows: [^chaeSafeScalableWeb2026]

## Current SOTA

Among the wiki's papers, the best score is 49.1 average SR for Llama3.1-70B trained with WebRL.[^qiWebRLTrainingLLM2025] The later VeriEnv paper does not beat it: its best trained agent reaches 13.94 and its best listed row is GPT-4o at 31.52.[^chaeSafeScalableWeb2026]

## Superseded claims

- **Superseded.** Qi et al. describe AutoWebGLM (18.2% SR) as the previous state-of-the-art web agent trained on open LLMs, and GPT-4-Turbo (17.6% SR) as the most advanced proprietary LLM API they compare with. WebRL beats both in the same paper, with 42.4% for Llama-3.1-8B, 43% for GLM-4-9B, and 49.1% for Llama-3.1-70B.[^qiWebRLTrainingLLM2025]

## Caveats

- The two tables come from different agent setups and are not directly comparable. Qi et al. run the proprietary models with a simple prompt.[^qiWebRLTrainingLLM2025] Chae et al. take their GPT-4o and GPT-4o-mini rows from Chae et al. (2025).[^chaeSafeScalableWeb2026]
- Qi et al. state the test set size (165 test cases).[^qiWebRLTrainingLLM2025] Chae et al. do not state the number of test tasks for their table.[^chaeSafeScalableWeb2026]
- WebRL agents are trained inside the WebArena environment, starting from supervised fine-tuning on the WebArena-Lite training dataset.[^qiWebRLTrainingLLM2025] VeriEnv agents are trained on cloned websites, and websites that overlap with the test split of the evaluation benchmarks are excluded from cloning and training.[^chaeSafeScalableWeb2026] The first is in-domain training and the second is an out-of-domain setting.
- Chae et al. refer to their Table 4 results as "WebArena" in the running text.[^chaeSafeScalableWeb2026]
- Inside Chae et al., the gain for LLaMA-3.2-3B-Instruct is $+9.09$ in the introduction and the results text, and +9.70 in Table 4 (12.73 against a base of 3.03).[^chaeSafeScalableWeb2026]

# Contradictions

**GPT-4o on WebArena-Lite.** Two papers report different success rates for GPT-4o.

| Paper | GPT-4o score | Setting stated |
|---|---|---|
| [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md) | 13.9 | simple prompt, 165 test cases[^qiWebRLTrainingLLM2025] |
| [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) | 31.52 | number reported by Chae et al. (2025)[^chaeSafeScalableWeb2026] |

The per-site values also differ. For example, GitLab is 10.0 in Qi et al. and 56.25 in Chae et al.[^qiWebRLTrainingLLM2025][^chaeSafeScalableWeb2026] The likely cause is a different agent setup: Qi et al. use a simple prompt, and Chae et al. copy a number from an earlier paper whose setup is not described in the source. Neither source states the GPT-4o version.

## Related

- Parent benchmark: [WebArena](webarena.md)
- Other web-agent benchmarks: [Online-Mind2Web](online-mind2web.md)
- Papers: [WebRL](../papers/qiWebRLTrainingLLM2025.md), [VeriEnv](../papers/chaeSafeScalableWeb2026.md)

## Open questions and results

- [WebRL on WebArena-Lite](../results/webrl-webarena-lite.md)

[^qiWebRLTrainingLLM2025]: Qi et al. 2025
[^chaeSafeScalableWeb2026]: Chae et al. 2026
