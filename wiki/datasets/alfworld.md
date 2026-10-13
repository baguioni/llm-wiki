---
type: Dataset
title: ALFWorld
description: Suite of text-based interactive environments for multi-step household tasks, used in the wiki's papers to test agent decision-making and to generate an agent serving workload.
tags: [dataset, environment, agents, decision-making, llm-serving]
sources:
  - id: shinnReflexionLanguageAgents2023
    resource: zotero://select/items/@shinnReflexionLanguageAgents2023
    title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
---

# ALFWorld

Also written AlfWorld in one source.[^shinnReflexionLanguageAgents2023]

## Overview

AlfWorld is a suite of text-based environments that challenge an agent to solve multi-step tasks in a variety of interactive environments based on TextWorld.[^shinnReflexionLanguageAgents2023] InferCept describes it as an interactive environment that aligns text descriptions and commands with a physically embodied robotic simulation.[^abhyankarInferCeptEfficientIntercept2024] Reflexion reports task completion on it.[^shinnReflexionLanguageAgents2023] InferCept uses it only to generate a virtual-environment serving workload.[^abhyankarInferCeptEfficientIntercept2024]

## Composition

- Reflexion runs 134 AlfWorld environments across six different tasks, including finding hidden objects, moving objects, and manipulating objects with other objects.[^shinnReflexionLanguageAgents2023]
- The tasks are set in common household environments.[^shinnReflexionLanguageAgents2023]
- The environment can only signal whether a task is complete.[^shinnReflexionLanguageAgents2023]
- The permissible actions can be seen in the observations.[^shinnReflexionLanguageAgents2023]

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [Shinn et al. 2023](../papers/shinnReflexionLanguageAgents2023.md) | Sequential decision-making task for [Reflexion](../methods/reflexion.md) | [ReAct](../methods/react.md) action generator with GPT-3, 134 environments, 12 consecutive trials | See the task quality table[^shinnReflexionLanguageAgents2023] |
| [Abhyankar et al. 2024](../papers/abhyankarInferCeptEfficientIntercept2024.md) | Virtual Environment (VE) augmentation workload for InferCept | GPT-4 prompted with the ReAct event loop | See the workload table[^abhyankarInferCeptEfficientIntercept2024] |

### Protocols

- Reflexion uses ReAct as the action generator, with GPT-3 as the LLM and two domain-specific few-shot trajectories.[^shinnReflexionLanguageAgents2023]
- Two self-evaluation techniques are used: natural language classification with an LLM, and a hand-written heuristic. The heuristic triggers self-reflection if the agent executes the same action and receives the same response for more than 3 cycles, or if the number of actions taken in the current environment exceeds 30.[^shinnReflexionLanguageAgents2023]
- In the baseline runs, if self-reflection is suggested, the self-reflection process is skipped, the environment is reset, and a new trial starts. The agent's memory is truncated to the last 3 self-reflections.[^shinnReflexionLanguageAgents2023]
- InferCept prompts GPT-4 with an initial virtual environment and uses the ReAct event loop to interact with the environment repeatedly, truncating to fit within the context length.[^abhyankarInferCeptEfficientIntercept2024]

### Task quality: task completion

| Model | Setting | Result | Reported by |
|---|---|---|---|
| GPT-3 | ReAct + Reflexion, heuristic self-evaluation, 134 tasks | completes 130 out of 134 tasks | [^shinnReflexionLanguageAgents2023] |
| GPT-3 | ReAct only, 134 tasks | performance increase halts between trials 6 and 7; converges at a hallucination rate of 22% | [^shinnReflexionLanguageAgents2023] |

- The paper summarizes its AlfWorld gain over strong baseline approaches as an absolute 22% in 12 iterative learning steps.[^shinnReflexionLanguageAgents2023]
- ReAct + Reflexion learns to solve additional tasks over 12 consecutive trials.[^shinnReflexionLanguageAgents2023]
- A common error in failed baseline trajectories is the agent thinking it has possession of an item that it does not have. Reflexion eliminates almost all of these cases.[^shinnReflexionLanguageAgents2023]
- Per-trial success curves are given only in a figure.[^shinnReflexionLanguageAgents2023]

### Serving workload characteristics

This row describes the LLM-serving workload that InferCept builds from ALFWorld. It is not a task-quality or speedup result. Each cell is (mean, variance).[^abhyankarInferCeptEfficientIntercept2024]

| Workload | Setting | Int Time (sec) | Num Interceptions | Context Len | Reported by |
|---|---|---|---|---|---|
| VE | GPT-4 with the ReAct event loop | (0.09, 0.014) | (28.18, 15.2) | (2185, 115) | [^abhyankarInferCeptEfficientIntercept2024] |

The VE interaction has a short and stable interception time because the text-based environment is executed locally. The context length is long because of the instructions needed to prompt the LLM to understand VE action sequences.[^abhyankarInferCeptEfficientIntercept2024]

## Related

- Datasets: [HotpotQA](hotpotqa.md), [ShareGPT](sharegpt.md)
- Methods: [Reflexion](../methods/reflexion.md), [ReAct](../methods/react.md), [vLLM](../methods/vllm.md)

[^shinnReflexionLanguageAgents2023]: Shinn et al. 2023
[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
