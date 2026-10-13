---
type: Dataset
title: HotpotQA
description: Wikipedia-based multi-hop question answering dataset, used in the wiki's papers to test agent reasoning and to generate agent serving workloads.
tags: [dataset, question-answering, multi-hop, agents, llm-serving]
sources:
  - id: shinnReflexionLanguageAgents2023
    resource: zotero://select/items/@shinnReflexionLanguageAgents2023
    title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
---

# HotpotQA

Also written HotPotQA in one source.[^shinnReflexionLanguageAgents2023]

## Overview

HotPotQA is a Wikipedia-based dataset whose question-and-answer pairs challenge agents to parse content and reason over several supporting documents.[^shinnReflexionLanguageAgents2023] The wiki's papers use it in two ways. Reflexion reports answer accuracy on it.[^shinnReflexionLanguageAgents2023] Two serving papers use it only to generate agent workloads, and report no answer accuracy.[^abhyankarInferCeptEfficientIntercept2024][^luoAutellixEfficientServing]

## Composition

- 113k question-and-answer pairs.[^shinnReflexionLanguageAgents2023]
- The dataset provides a ground truth context for each question, which Reflexion gives to its Chain-of-Thought agent.[^shinnReflexionLanguageAgents2023]
- Splits are not stated in the wiki's papers.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Shinn et al. 2023](../papers/shinnReflexionLanguageAgents2023.md) | Reasoning task for [Reflexion](../methods/reflexion.md) | 100 questions; CoT (GT) and [ReAct](../methods/react.md) agents on text-davinci-003, gpt-3.5-turbo, gpt-4 | See the accuracy table[^shinnReflexionLanguageAgents2023] |
| [Abhyankar et al. 2024](../papers/abhyankarInferCeptEfficientIntercept2024.md) | QA augmentation workload for InferCept | ReAct prompting with a live Wikipedia API endpoint | See the workload table[^abhyankarInferCeptEfficientIntercept2024] |
| [Luo et al.](../papers/luoAutellixEfficientServing.md) | LATS workload (Monte Carlo Tree Search) for Autellix | MCTS run on HotpotQA | See the workload table[^luoAutellixEfficientServing] |

### Protocols

- Reflexion tests reasoning-only ability with Reflexion + [Chain-of-Thought](../methods/chain-of-thought.md) (CoT) as $Q\rightarrow A$ and as $Q$, $C_{gt}\rightarrow A$, where $C_{gt}$ is the ground truth context from the dataset. It tests holistic question answering with a Reflexion + ReAct agent that retrieves context through a Wikipedia API. CoT uses 6-shot prompting, ReAct 2-shot, and self-reflection 2-shot.[^shinnReflexionLanguageAgents2023]
- Between trials, exact match answer grading from the environment gives the agent a binary success signal. Memory size is 3 experiences.[^shinnReflexionLanguageAgents2023]
- In the Reflexion runs the agent retries a failed task until it produces 3 consecutive failed attempts on it.[^shinnReflexionLanguageAgents2023]
- InferCept names the dataset "Multihop QA Wikipedia" and cites the HotpotQA paper for it. It uses the ReAct framework to prompt the LLM to call a live Wikipedia endpoint, retrieves a summary of the relevant page for each call, and limits the response size to fit the maximum model sequence length.[^abhyankarInferCeptEfficientIntercept2024]
- Autellix derives its LATS workloads from running MCTS on HotpotQA.[^luoAutellixEfficientServing]

### Task quality: accuracy

Table 5 of Shinn et al., labelled "Pass@1 accuracy on 100 HotPotQA using various models".[^shinnReflexionLanguageAgents2023]

| Model | Setting | Baseline accuracy | Reflexion accuracy | Reported by |
|---|---|---|---|---|
| text-davinci-003 | CoT (GT), 100 questions | 0.60 | 0.77 | [^shinnReflexionLanguageAgents2023] |
| gpt-3.5-turbo | CoT (GT), 100 questions | 0.57 | 0.71 | [^shinnReflexionLanguageAgents2023] |
| gpt-4 | CoT (GT), 100 questions | 0.68 | 0.80 | [^shinnReflexionLanguageAgents2023] |
| text-davinci-003 | ReAct, 100 questions | 0.30 | 0.55 | [^shinnReflexionLanguageAgents2023] |
| gpt-3.5-turbo | ReAct, 100 questions | 0.26 | 0.38 | [^shinnReflexionLanguageAgents2023] |
| gpt-4 | ReAct, 100 questions | 0.39 | 0.51 | [^shinnReflexionLanguageAgents2023] |

- The paper summarizes its HotPotQA gain over strong baselines as 20%.[^shinnReflexionLanguageAgents2023]
- ReAct-only, CoT-only, and CoT (GT)-only fail to probabilistically improve on any task: no task failed in the first trial was solved in later trials at a temperature of 0.7.[^shinnReflexionLanguageAgents2023]
- The CoT (GT) agent cannot infer the correct answer for 39% of the questions, and Reflexion improves its accuracy by 14%.[^shinnReflexionLanguageAgents2023]
- In the ablation with CoT (GT) as the baseline, self-reflection gives an 8% absolute boost over the episodic memory learning advantage.[^shinnReflexionLanguageAgents2023]

### Serving workload characteristics

These rows describe the LLM-serving workload that each paper builds from HotpotQA. They are not accuracy or speedup results.

InferCept, QA augmentation. Each cell is (mean, variance).[^abhyankarInferCeptEfficientIntercept2024]

| Workload | Setting | Int Time (sec) | Num Interceptions | Context Len | Reported by |
|---|---|---|---|---|---|
| QA | ReAct with a live Wikipedia API | (0.69, 0.17) | (2.52, 1.73) | (1846, 428) | [^abhyankarInferCeptEfficientIntercept2024] |

The paper describes the QA tools as having relatively quick yet variable execution times, due to the non-deterministic network communication latency with Wikipedia.[^abhyankarInferCeptEfficientIntercept2024]

Autellix, LATS workload:[^luoAutellixEfficientServing]

| Workload | Setting | LLM calls per program | Prefill tokens per call (mean) | Decode tokens per call (mean) | Reported by |
|---|---|---|---|---|---|
| LATS | MCTS on HotpotQA | on average 159.7 | 467.2 | 72.6 | [^luoAutellixEfficientServing] |

The paper notes that 159.7 LLM calls per program is an order of magnitude more than its ShareGPT or BFCL workloads.[^luoAutellixEfficientServing]

## Known issues

- Reflexion evaluates 100 questions, not the full dataset.[^shinnReflexionLanguageAgents2023]
- The table of Shinn et al. is labelled "Pass@1 accuracy", while the method text describes exact match answer grading.[^shinnReflexionLanguageAgents2023]

## Related

- Datasets: [ALFWorld](alfworld.md), [ShareGPT](sharegpt.md), [HumanEval](humaneval.md)
- Benchmarks: [BFCL](../benchmarks/bfcl.md)
- Methods: [Reflexion](../methods/reflexion.md), [ReAct](../methods/react.md), [Chain-of-Thought](../methods/chain-of-thought.md), [vLLM](../methods/vllm.md)

[^shinnReflexionLanguageAgents2023]: Shinn et al. 2023
[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
