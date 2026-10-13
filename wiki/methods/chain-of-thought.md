---
type: Method
title: Chain-of-Thought Prompting
description: Prompting strategy in which the model writes step-by-step reasoning before its answer or action, used in this wiki's papers as an agent component and as a single-agent baseline.
tags: [prompting, reasoning, llm-agents, baseline]
sources:
  - id: zhouWebArenaRealisticWeb2024
    resource: zotero://select/items/@zhouWebArenaRealisticWeb2024
    title: "WebArena: A Realistic Web Environment for Building Autonomous Agents"
  - id: wangAgentDropoutDynamicAgent2025
    resource: zotero://select/items/@wangAgentDropoutDynamicAgent2025
    title: "AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration"
  - id: shinnReflexionLanguageAgents2023
    resource: zotero://select/items/@shinnReflexionLanguageAgents2023
    title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
  - id: wangVOYAGEROpenEndedEmbodied
    resource: zotero://select/items/@wangVOYAGEROpenEndedEmbodied
    title: "VOYAGER: An Open-Ended Embodied Agent with Large Language Models"
---

# Chain-of-Thought Prompting

The chain-of-thought paper itself is not in this wiki. Everything below is what the wiki's papers state about it.

## Overview

With chain-of-thought (CoT) prompting, the model performs step-by-step reasoning in text before it issues its action or answer.[^zhouWebArenaRealisticWeb2024] The alternative that the papers compare it with is direct prediction: WebArena's direct agent predicts the next action from the same inputs without the reasoning step, and AgentDropout's "Vanilla" baseline is direct reasoning by a single agent.[^zhouWebArenaRealisticWeb2024][^wangAgentDropoutDynamicAgent2025]

## How it works

The papers apply it by asking for reasoning first and the output second:

- WebArena: with the current observation, the intent, and the previously performed action, the model first performs chain-of-thought reasoning steps and then predicts the action. Two in-context examples are given.[^zhouWebArenaRealisticWeb2024]
- Voyager, automatic curriculum: GPT-4 is asked to first reason about the current progress and then suggest the next task.[^wangVOYAGEROpenEndedEmbodied]
- Voyager, code generation: GPT-4 is asked to first explain why the code from the last round fails, then give step-by-step plans to finish the task, and finally generate code.[^wangVOYAGEROpenEndedEmbodied]
- Voyager, self-verification: GPT-4 is asked to first reason about the task's success or failure, then output a boolean for the outcome, and finally give a critique if the task fails.[^wangVOYAGEROpenEndedEmbodied]

## Papers using it

### WebArena baseline agents

End-to-end task success rate (SR %) on [WebArena](../benchmarks/webarena.md) with and without CoT (Table 2 of the paper). The UA hint asks the model to stop when a task is unachievable. Temperature is 1.0 and top-p is 0.9.[^zhouWebArenaRealisticWeb2024]

| CoT | UA Hint | Model | SR | SR$_{\textrm{AC}}$ | SR$_{\textrm{UA}}$ |
|---|---|---|---|---|---|
| ✓ | ✓ | text-bison-001 | 5.05 | 4.00 | 27.78 |
| ✗ | ✓ | GPT-3.5 | 6.41 | 4.90 | 38.89 |
| ✓ | ✓ | GPT-3.5 | 8.75 | 6.44 | 58.33 |
| ✓ | ✓ | GPT-4 | 11.70 | 8.63 | 77.78 |
| ✗ | ✗ | GPT-3.5 | 5.10 | 4.90 | 8.33 |
| ✓ | ✗ | GPT-3.5 | 6.16 | 6.06 | 8.33 |
| ✓ | ✗ | GPT-4 | 14.41 | 13.02 | 44.44 |

All rows: [^zhouWebArenaRealisticWeb2024]

- The paper calls the explicit reasoning procedure "somewhat helpful": it brings a 2.34% improvement over the version without it (GPT-3.5 with the UA hint).[^zhouWebArenaRealisticWeb2024]
- At temperature 0.0, GPT-3.5-turbo-16k-0613 with CoT and no UA hint has an SR of 6.28 (Table 5 of the paper).[^zhouWebArenaRealisticWeb2024]
- Human performance on the benchmark is 78.24%.[^zhouWebArenaRealisticWeb2024]

### AgentDropout single-agent baseline

CoT is the single-agent baseline next to Vanilla (direct reasoning). The table gives the two single-agent rows of Table 1 of the paper; the source does not name the metric unit, and the text calls the gains "accuracy".[^wangAgentDropoutDynamicAgent2025]

| Base model | Method | [MMLU](../datasets/mmlu.md) | [GSM8K](../datasets/gsm8k.md) | AQuA | MultiArith | SVAMP | [HumanEval](../datasets/humaneval.md) | Avg. |
|---|---|---|---|---|---|---|---|---|
| Llama3-8B-Instruct | Vanilla | 53.59 | 70.23 | 41.67 | 91.11 | 75.00 | 53.33 | 64.16 |
| Llama3-8B-Instruct | CoT | 56.86 | 70.47 | 43.75 | 92.25 | 76.17 | 54.17 | 65.61 |
| Qwen2.5-72B-Instruct | Vanilla | 82.35 | 91.02 | 83.75 | 98.89 | 92.67 | 85.28 | 88.99 |
| Qwen2.5-72B-Instruct | CoT | 83.66 | 92.19 | 84.58 | 100 | 93.35 | 86.67 | 90.08 |
| Deepseek-V3-671B-Instruct | Vanilla | 84.97 | 94.68 | 84.58 | 100 | 93.67 | 88.43 | 91.06 |
| Deepseek-V3-671B-Instruct | CoT | 84.31 | 95.15 | 85.42 | 100 | 93.94 | 89.26 | 91.34 |

All rows: [^wangAgentDropoutDynamicAgent2025]

- The average gain of CoT over Vanilla is 1.45 with Llama3, 1.09 with Qwen2.5, and 0.28 with Deepseek-V3. On MMLU with Deepseek-V3, CoT is 0.66 below Vanilla.[^wangAgentDropoutDynamicAgent2025]
- The paper observes that with a weaker model (Llama3), single-agent methods such as CoT give more significant improvements, while the gains from multi-agent interaction are less stable.[^wangAgentDropoutDynamicAgent2025]
- AgentDropout outperforms CoT on the average in all three settings (68.70, 91.58, and 93.72).[^wangAgentDropoutDynamicAgent2025]
- Token cost, averaged over the six datasets (prompt / completion tokens): Vanilla 68K / 67K and CoT 76K / 102K with Llama3; Vanilla 68K / 69K and CoT 76K / 106K with Qwen2.5; Vanilla 67K / 70K and CoT 75K / 92K with Deepseek-V3.[^wangAgentDropoutDynamicAgent2025]

### Reflexion

Chain of Thought is one of the two Actor variants of [Reflexion](reflexion.md), the other being [ReAct](react.md).[^shinnReflexionLanguageAgents2023] On [HotpotQA](../datasets/hotpotqa.md), Reflexion + CoT is tested as $Q\rightarrow A$ and as $Q, C_{gt}\rightarrow A$, where $C_{gt}$ is the ground truth context. Because CoT is not a multi-step decision-making technique, the ground truth context is given to isolate reasoning over the provided text. CoT uses 6-shot prompting.[^shinnReflexionLanguageAgents2023]

Accuracy on 100 HotPotQA questions (Table 5 of the paper):[^shinnReflexionLanguageAgents2023]

| Model | CoT (GT) baseline | CoT (GT) + Reflexion |
|---|---|---|
| text-davinci-003 | 0.60 | 0.77 |
| gpt-3.5-turbo | 0.57 | 0.71 |
| gpt-4 | 0.68 | 0.80 |

All rows: [^shinnReflexionLanguageAgents2023]

- CoT-only and CoT (GT)-only runs fail to probabilistically improve on any task: no task that failed in the first trial was solved in later trials at a temperature of 0.7.[^shinnReflexionLanguageAgents2023]
- The CoT (GT) agent cannot infer the correct answer for 39% of the questions even with the ground truth context.[^shinnReflexionLanguageAgents2023]
- For programming tasks, Reflexion uses Chain-of-Thought prompting to generate its own unit tests with natural language descriptions.[^shinnReflexionLanguageAgents2023]

### Voyager

Chain-of-thought prompting is part of the prompts for the automatic curriculum, code generation, and self-verification (see How it works).[^wangVOYAGEROpenEndedEmbodied] In the paper's feature comparison (Table A.3), chain-of-thought is the one feature that all four methods have: ReAct, Reflexion, AutoGPT, and Voyager.[^wangVOYAGEROpenEndedEmbodied]

## Strengths & Limitations

- It helps weaker models more in the AgentDropout comparison, and the gain shrinks with stronger models.[^wangAgentDropoutDynamicAgent2025]
- It costs more completion tokens than direct answering (for example 102K against 67K on average with Llama3).[^wangAgentDropoutDynamicAgent2025]
- On WebArena the gain is modest, and the best CoT agent (GPT-4, 14.41%) stays far below human performance (78.24%).[^zhouWebArenaRealisticWeb2024]
- Reflexion notes that CoT is not a multi-step decision-making technique, and in its runs repeating a CoT attempt without self-reflection did not solve any HotpotQA question that failed in the first trial.[^shinnReflexionLanguageAgents2023]

## Related

- Methods: [ReAct](react.md), [Reflexion](reflexion.md)
- Benchmarks: [WebArena](../benchmarks/webarena.md)
- Datasets: [HotpotQA](../datasets/hotpotqa.md), [MMLU](../datasets/mmlu.md), [GSM8K](../datasets/gsm8k.md), [HumanEval](../datasets/humaneval.md)

[^zhouWebArenaRealisticWeb2024]: Zhou et al. 2024
[^wangAgentDropoutDynamicAgent2025]: Wang et al. 2025
[^shinnReflexionLanguageAgents2023]: Shinn et al. 2023
[^wangVOYAGEROpenEndedEmbodied]: Wang et al. n.d.
