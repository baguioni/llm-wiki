---
type: Benchmark
title: Online-Mind2Web
description: Web navigation benchmark that evaluates agents on live websites with an LLM-as-judge for task success, also called Mind2Web-Online.
tags: [web-agents, benchmark, live-web, llm-as-a-judge, evaluation]
sources:
  - id: karWeblicaScalableReproducible2026
    resource: zotero://select/items/@karWeblicaScalableReproducible2026
    title: "Weblica: Scalable and Reproducible Training Environments for Visual Web Agents"
  - id: chaeSafeScalableWeb2026
    resource: zotero://select/items/@chaeSafeScalableWeb2026
    title: Safe and Scalable Web Agent Learning via Recreated Websites
---

# Online-Mind2Web

The two papers use two names for the benchmark of Xue et al. (2025): Online-Mind2Web (OM2W) in Kar et al. and Mind2Web-Online in Chae et al.[^karWeblicaScalableReproducible2026][^chaeSafeScalableWeb2026]

## Setup

- **Task.** Agents are evaluated on diverse live websites.[^karWeblicaScalableReproducible2026] The benchmark focuses on generalization over 100+ real-world websites and provides 300 tasks with three difficulty levels: easy, medium, and hard.[^chaeSafeScalableWeb2026] A comparison table in Chae et al. lists it with 136 websites and 300 tasks.[^chaeSafeScalableWeb2026]
- **Metric.** Task success decided by an [LLM-as-a-judge](../methods/llm-as-a-judge.md).[^karWeblicaScalableReproducible2026]
- **Protocol in Kar et al.** The official judge of the benchmark is used. Each experiment is repeated three times and the mean accuracy is reported. [Test-time scaling](../methods/test-time-scaling.md) is studied with $k\in\{1,2,4,8\}$ independent attempts, reported as pass@$k$, where the total step budget scales linearly with $k$.[^karWeblicaScalableReproducible2026]
- **Protocol in Chae et al.** Tasks on websites that block web agents are excluded, which leaves 220 tasks. Trajectories are scored with the WebJudge-7B model from the original paper.[^chaeSafeScalableWeb2026]

## Results

### Reported by Kar et al. 2026 (Table 1 and Table 3)

Baseline results are taken from Awadallah et al. (2025) and Gupta et al. (2026). † Fara-7B and MolmoWeb-8B allow up to 5 and 10 retries per trajectory.[^karWeblicaScalableReproducible2026]

| System | Score | Setting / budget | Reported by |
|---|---|---|---|
| Weblica-8B (k=8) | 68.8 | pass@8, 240 total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Yutori Navigator | 64.7 | API-only, total steps not stated | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-4B | 64.1 ± 1.6 | pass@8 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-8B (k=4) | 60.5 | pass@4, 120 total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| OpenAI CUA | 58.3 | API-only, 100 total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Gemini CUA | 57.3 | API-only, 100 total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-4B | 55.8 ± 1.0 | pass@4 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-2B | 55.6 ± 2.2 | pass@8 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (8B) | 54.4 ± 1.7 | base model, pass@8 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-8B (k=2) | 50.3 | pass@2, 60 total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (4B) | 46.9 ± 0.2 | base model, pass@8 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (8B) | 46.3 ± 0.3 | base model, pass@4 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-4B | 46.0 ± 0.6 | pass@2 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-2B | 44.7 ± 1.2 | pass@4 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (4B) | 39.4 ± 0.3 | base model, pass@4 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-8B (k=1) | 39.2 | pass@1, 30 total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (2B) | 38.2 ± 1.3 | base model, pass@8 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (8B) | 37.6 ± 0.2 | base model, pass@2 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| MolmoWeb-8B | 35.3 | open-weight, ≥100† total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-4B | 35.2 ± 0.3 | pass@1 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Fara-7B | 34.1 | open-weight, ≥100† total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| GLM-4.1V-9B-Thinking | 33.9 | open-weight, 100 total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-2B | 33.9 ± 1.1 | pass@2 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| UI-TARS-1.5-7B | 31.3 | open-weight, 100 total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (4B) | 31.3 ± 0.4 | base model, pass@2 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL-Instruct-8B | 28.6 | base model, pass@1, 30 total steps | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (2B) | 28.6 ± 0.9 | base model, pass@4 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Weblica-2B | 24.1 ± 0.8 | pass@1 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (4B) | 23.2 ± 0.2 | base model, pass@1 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (2B) | 20.1 ± 0.6 | base model, pass@2 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |
| Qwen3-VL (2B) | 13.3 ± 0.3 | base model, pass@1 | [Kar et al. 2026](../papers/karWeblicaScalableReproducible2026.md) |

All rows: [^karWeblicaScalableReproducible2026]

- The Table 3 values with ± for the 8B models are 39.2 ± 0.9, 50.3 ± 0.7, 60.5 ± 0.9, and 68.8 ± 1.7 for Weblica-8B, and 28.6 ± 0.4 at pass@1 for Qwen3-VL.[^karWeblicaScalableReproducible2026]
- Raising the action budget from 15 to 30 steps improves Weblica-8B pass@1 from 32.6% to 39.2%.[^karWeblicaScalableReproducible2026]
- Environment type, pass@1: 39.2% with synthesized environments only and 35.3% with cached environments only.[^karWeblicaScalableReproducible2026]

### Reported by Chae et al. 2026 (Table 5)

Per-difficulty columns are in the order Easy, Medium, Hard. Rows marked `*` use numbers reported by Xue et al. (2025).[^chaeSafeScalableWeb2026]

| System | Total | Easy, Medium, Hard | Setting / budget | Reported by |
|---|---|---|---|---|
| Browser-Use-GPT-4o\* | 30.00 | 55.40, 26.60, 8.10 | number from Xue et al. (2025) | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| Claude-3.5-Sonnet\* | 28.80 | 56.60, 26.60, 6.80 | number from Xue et al. (2025) | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| LLaMA-3.2-3B-Instruct + VeriEnv | 24.55 | 40.35, 29.41, 13.95 | rejection-based fine-tuning on cloned websites | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| LLaMA-3.2-3B-Instruct + ADP | 24.09 | 42.11, 24.71, 11.63 | open-source baseline | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| Qwen3-4B + VeriEnv | 20.45 | 29.82, 23.53, 6.98 | rejection-based fine-tuning on cloned websites | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| Qwen3-4B + Synatra | 14.55 | 35.09, 5.88, 9.30 | open-source baseline | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| LLaMA-3.2-3B-Instruct + Synatra | 14.55 | 24.56, 15.29, 6.98 | open-source baseline | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| Qwen3-4B | 13.18 | 26.32, 9.41, 11.63 | base model | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| Qwen3-4B + ADP | 11.36 | 26.32, 7.06, 6.98 | open-source baseline | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |
| LLaMA-3.2-3B-Instruct | 11.36 | 19.30, 12.94, 0.00 | base model | [Chae et al. 2026](../papers/chaeSafeScalableWeb2026.md) |

All rows: [^chaeSafeScalableWeb2026]

## Current SOTA

- The highest score among the wiki's papers is 68.8 for Weblica-8B at pass@8, with 30 steps per attempt and 240 total steps.[^karWeblicaScalableReproducible2026]
- The highest score that is not a pass@$k$ result with $k>1$ is 64.7 for Yutori Navigator, an API-only agent whose step budget is not stated.[^karWeblicaScalableReproducible2026]
- Among open-weight models at pass@1, the best is Weblica-8B with 39.2 at 30 steps.[^karWeblicaScalableReproducible2026]

## Superseded claims

- **Superseded.** MolmoWeb-8B (35.3, ≥100 steps with retries) is the best open-weight baseline in Kar et al. Weblica-8B exceeds it with 39.2% pass@1 at 30 steps, which the paper describes as outperforming open-weight models that use 3$\times$ more steps.[^karWeblicaScalableReproducible2026]

No "best" claim from Chae et al. is beaten by Kar et al., because the two papers use different task sets and judges (see Caveats).

## Caveats

- **Task set.** Chae et al. evaluate on 220 of the 300 tasks.[^chaeSafeScalableWeb2026] Kar et al. do not state a task count.[^karWeblicaScalableReproducible2026] The rows of the two tables are not comparable.
- **Judge.** Chae et al. use the WebJudge-7B model.[^chaeSafeScalableWeb2026] Kar et al. use the official judge provided by the benchmark and do not name it.[^karWeblicaScalableReproducible2026]
- **Copied rows.** The starred rows of Chae et al. are numbers reported by Xue et al. (2025). The source does not say whether they are on the 220-task subset.[^chaeSafeScalableWeb2026]
- **pass@$k$ versus retries.** Weblica reports pass@$k$ over independent attempts. Fara-7B and MolmoWeb-8B use retry-based evaluation, where failures attributed to the environment are selectively discarded.[^karWeblicaScalableReproducible2026]
- **Step budgets differ** between rows (30 to 240 total steps, and ≥100 for the retry-based baselines).[^karWeblicaScalableReproducible2026]
- **Leaderboard values.** The Table 1 caption states that italic Online-Mind2Web results are from the auto-eval leaderboard. The italics are lost in the extracted text, so this page cannot mark which rows they are.[^karWeblicaScalableReproducible2026]
- **Observation space.** Weblica models act on screenshots only.[^karWeblicaScalableReproducible2026]
- **Possible data overlap.** Chae et al. attribute ADP's gain with LLaMA-3.2-3B-Instruct to overlap between ADP's aggregated training data (including Mind2Web and NNetNav) and the evaluation distribution.[^chaeSafeScalableWeb2026] Weblica extracts its capability list from trajectories of Qwen3-VL-32B-Instruct attempting the Online-Mind2Web tasks.[^karWeblicaScalableReproducible2026]

## Related

- Other web-agent benchmarks: [WebArena](webarena.md), [WebArena-Lite](webarena-lite.md)
- Methods: [LLM-as-a-judge](../methods/llm-as-a-judge.md), [Test-time scaling](../methods/test-time-scaling.md)
- Papers: [Weblica](../papers/karWeblicaScalableReproducible2026.md), [VeriEnv](../papers/chaeSafeScalableWeb2026.md)

[^karWeblicaScalableReproducible2026]: Kar et al. 2026
[^chaeSafeScalableWeb2026]: Chae et al. 2026
