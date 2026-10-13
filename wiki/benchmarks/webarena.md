---
type: Benchmark
title: WebArena
description: Self-hosted web environment with 812 long-horizon tasks that scores web agents by the functional correctness of task completion.
tags: [web-agents, benchmark, autonomous-agents, llm-agents, evaluation]
sources:
  - id: zhouWebArenaRealisticWeb2024
    resource: zotero://select/items/@zhouWebArenaRealisticWeb2024
    title: "WebArena: A Realistic Web Environment for Building Autonomous Agents"
  - id: qiWebRLTrainingLLM2025
    resource: zotero://select/items/@qiWebRLTrainingLLM2025
    title: "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning"
  - id: chaeSafeScalableWeb2026
    resource: zotero://select/items/@chaeSafeScalableWeb2026
    title: Safe and Scalable Web Agent Learning via Recreated Websites
  - id: karWeblicaScalableReproducible2026
    resource: zotero://select/items/@karWeblicaScalableReproducible2026
    title: "Weblica: Scalable and Reproducible Training Environments for Visual Web Agents"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
---

# WebArena

## Setup

- **Environment.** Four fully operational, self-hosted web applications (online shopping, discussion forums, collaborative development, and business content management), plus utility tools such as a map, a calculator, and a scratchpad.[^zhouWebArenaRealisticWeb2024] It does not rely on live websites.[^zhouWebArenaRealisticWeb2024]
- **Tasks.** 812 long-horizon web-based tasks, instantiated from 241 templates. Each task is a high-level natural language intent.[^zhouWebArenaRealisticWeb2024]
- **Metric.** End-to-end task success rate (SR, %). Each example has a metric that evaluates the functional correctness of the task execution, meaning whether the result of the execution achieves the desired goal.[^zhouWebArenaRealisticWeb2024]
- **Evaluation functions.** One of them, `fuzzy_match`, uses gpt-4-0613 as a judge.[^zhouWebArenaRealisticWeb2024]
- **Unachievable tasks.** Some tasks are labeled "N/A", and the agent is expected to produce an equivalent response.[^zhouWebArenaRealisticWeb2024] The **UA hint** is an instruction that asks the agent to stop if it believes the task is impossible.[^zhouWebArenaRealisticWeb2024]
- **Baseline protocol.** GPT-3.5-turbo-16k-0613, GPT-4-0613, and text-bison-001 with a temperature of $1.0$ and a top-$p$ of $0.9$. The maximum number of state transitions is 30.[^zhouWebArenaRealisticWeb2024]
- **Human performance.** One task is sampled from each of 170 templates and performed by five computer science graduate students.[^zhouWebArenaRealisticWeb2024]

A human-verified subset with 165 test cases is tracked on its own page: [WebArena-Lite](webarena-lite.md).[^qiWebRLTrainingLLM2025]

## Results

Task success rate (%) on the full 812 tasks.

| System | SR | Setting / budget | Reported by |
|---|---|---|---|
| Human | 78.24 | one task from each of 170 templates | [Zhou et al. 2024](../papers/zhouWebArenaRealisticWeb2024.md)[^zhouWebArenaRealisticWeb2024] |
| WebPilot + GPT-4o | 37.2 | result on full WebArena taken from the literature | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md)[^qiWebRLTrainingLLM2025] |
| AWM + GPT-4-0613 | 35.5 | result on full WebArena taken from the literature | [Qi et al. 2025](../papers/qiWebRLTrainingLLM2025.md)[^qiWebRLTrainingLLM2025] |
| GPT-4 | 14.41 | CoT, no UA hint | [Zhou et al. 2024](../papers/zhouWebArenaRealisticWeb2024.md)[^zhouWebArenaRealisticWeb2024] |
| GPT-4 | 11.70 | CoT, UA hint | [Zhou et al. 2024](../papers/zhouWebArenaRealisticWeb2024.md)[^zhouWebArenaRealisticWeb2024] |
| GPT-3.5 | 8.75 | CoT, UA hint | [Zhou et al. 2024](../papers/zhouWebArenaRealisticWeb2024.md)[^zhouWebArenaRealisticWeb2024] |
| GPT-3.5 | 6.41 | no CoT, UA hint | [Zhou et al. 2024](../papers/zhouWebArenaRealisticWeb2024.md)[^zhouWebArenaRealisticWeb2024] |
| GPT-3.5 | 6.16 | CoT, no UA hint | [Zhou et al. 2024](../papers/zhouWebArenaRealisticWeb2024.md)[^zhouWebArenaRealisticWeb2024] |
| GPT-3.5 | 5.10 | no CoT, no UA hint | [Zhou et al. 2024](../papers/zhouWebArenaRealisticWeb2024.md)[^zhouWebArenaRealisticWeb2024] |
| text-bison-001 | 5.05 | CoT, UA hint | [Zhou et al. 2024](../papers/zhouWebArenaRealisticWeb2024.md)[^zhouWebArenaRealisticWeb2024] |

- CoT is [chain-of-thought](../methods/chain-of-thought.md) reasoning before the action.[^zhouWebArenaRealisticWeb2024]
- Per-site success rates for the two literature rows, in the order Reddit, Gitlab, CMS, Map, OSS: AWM + GPT-4-0613 50.9, 31.8, 29.1, 43.3, 30.8; WebPilot + GPT-4o 65.1, 39.4, 24.7, 33.9, 36.9.[^qiWebRLTrainingLLM2025]
- GPT-4 with CoT and no UA hint reaches 13.02 on achievable tasks and 44.44 on unachievable tasks. With the UA hint it reaches 8.63 and 77.78.[^zhouWebArenaRealisticWeb2024]

### Used as a workload

These papers run WebArena tasks to measure a serving system. They do not report task success.

| Paper | What is measured | Setting | Reported numbers |
|---|---|---|---|
| [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md) | Task completion time (TCT) and GPU memory utilization | Full 812 browser tasks (mean 18 steps), mean $\pm$ std over 10 trials | SAGA: TCT 82.1$\pm$6.8 s, Mem 74.6$\pm$2.3%. vLLM+APC v0.15.1: TCT 127.3$\pm$10.1 s, Mem 61.2$\pm$2.5%. vLLM v0.6.0: TCT 178.4$\pm$14.2 s, Mem 45.3$\pm$2.1%. Speedup of SAGA: 1.55$\times$ vs. vLLM+APC, 2.17$\times$ vs. vLLM v0.6.0[^guoSAGAWorkflowAtomicScheduling2026] |
| [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md) | Competitive ratio of eviction policies against Bélády's optimal offline algorithm (lower is better) | WebArena column of the eviction table | Standard LRU 2.12, LRU + Prefix (vLLM v0.5) 1.74, WA-LRU 1.28[^guoSAGAWorkflowAtomicScheduling2026] |

The comparison baselines are serving systems such as [vLLM](../methods/vllm.md) and [SGLang](../methods/sglang.md).[^guoSAGAWorkflowAtomicScheduling2026]

### Other uses

- [WebRL](../papers/qiWebRLTrainingLLM2025.md) trains its agents inside the WebArena environment and evaluates on WebArena-Lite.[^qiWebRLTrainingLLM2025]
- [VeriEnv](../papers/chaeSafeScalableWeb2026.md) clones websites drawn from WebArena and trains agents only inside the clones, to study site-specific mastery. The results are shown in a figure, and the text states no numbers.[^chaeSafeScalableWeb2026]
- [Weblica](../papers/karWeblicaScalableReproducible2026.md) mentions WebArena as a benchmark on self-hosted websites with programmatic success checking, and states that such benchmarks are reproducible but suffer from a sim-to-real gap. It reports no WebArena result.[^karWeblicaScalableReproducible2026]

## Current SOTA

Among the wiki's papers, the best agent score on the full benchmark is 37.2 for WebPilot + GPT-4o. It is a result on full WebArena that Qi et al. take from the literature.[^qiWebRLTrainingLLM2025] Human performance is 78.24%.[^zhouWebArenaRealisticWeb2024]

## Superseded claims

- **Superseded.** The WebArena paper states that its best GPT-4-based agent reaches an end-to-end task success rate of 14.41%.[^zhouWebArenaRealisticWeb2024] The WebRL paper later lists AWM + GPT-4-0613 at 35.5 and WebPilot + GPT-4o at 37.2 on full WebArena.[^qiWebRLTrainingLLM2025]

## Caveats

- The two literature rows come from other papers. Qi et al. do not state their prompting setup or step budget, so they are not matched to the baseline protocol of Zhou et al.[^qiWebRLTrainingLLM2025]
- The UA hint changes the score of the same model: it helps on unachievable tasks and hinders performance on achievable tasks.[^zhouWebArenaRealisticWeb2024]
- The human score is measured on one task per template for 170 templates, not on all 812 tasks.[^zhouWebArenaRealisticWeb2024]
- Website count. Zhou et al. describe four web applications and treat the map as a utility tool.[^zhouWebArenaRealisticWeb2024] Qi et al. list five websites: OpenStreetMap (Map), Reddit, GitLab, online store content management system (CMS), and OneStopShop (OSS).[^qiWebRLTrainingLLM2025] Chae et al. also list WebArena with 5 websites and 812 tasks.[^chaeSafeScalableWeb2026]
- Chae et al. label Table 4 as WebArena-Lite and refer to the same results as "WebArena" in the running text. Those numbers are on the [WebArena-Lite](webarena-lite.md) page.[^chaeSafeScalableWeb2026]
- The SAGA rows are systems measurements and are not comparable with success rates.[^guoSAGAWorkflowAtomicScheduling2026]

## Related

- Subset: [WebArena-Lite](webarena-lite.md)
- Other web-agent benchmarks: [Online-Mind2Web](online-mind2web.md), [WebShop](webshop.md)
- Workload companion in SAGA: [SWE-bench Verified](swe-bench-verified.md)
- Methods: [Chain-of-thought](../methods/chain-of-thought.md), [LLM-as-a-judge](../methods/llm-as-a-judge.md)
- Papers: [WebArena](../papers/zhouWebArenaRealisticWeb2024.md), [WebRL](../papers/qiWebRLTrainingLLM2025.md), [VeriEnv](../papers/chaeSafeScalableWeb2026.md), [Weblica](../papers/karWeblicaScalableReproducible2026.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md)

[^zhouWebArenaRealisticWeb2024]: Zhou et al. 2024
[^qiWebRLTrainingLLM2025]: Qi et al. 2025
[^chaeSafeScalableWeb2026]: Chae et al. 2026
[^karWeblicaScalableReproducible2026]: Kar et al. 2026
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
