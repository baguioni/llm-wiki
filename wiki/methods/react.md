---
type: Method
title: ReAct
description: Agent loop in which an LLM alternates a reasoning trace (thought), an action, and the observation returned by the environment, used as the base scaffold or baseline by many agent papers in this wiki.
tags: [llm-agents, agent-scaffold, reasoning-and-acting, tool-use]
sources:
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: gaoAgentScopeFlexibleRobust2024
    resource: zotero://select/items/@gaoAgentScopeFlexibleRobust2024
    title: "AgentScope: A Flexible yet Robust Multi-Agent Platform"
  - id: karWeblicaScalableReproducible2026
    resource: zotero://select/items/@karWeblicaScalableReproducible2026
    title: "Weblica: Scalable and Reproducible Training Environments for Visual Web Agents"
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: liWebSailorV2BridgingChasm2025
    resource: zotero://select/items/@liWebSailorV2BridgingChasm2025
    title: "WebSailor-V2: Bridging the Chasm to Proprietary Agents via Synthetic Data and Scalable Reinforcement Learning"
  - id: shinnReflexionLanguageAgents2023
    resource: zotero://select/items/@shinnReflexionLanguageAgents2023
    title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
  - id: wangVOYAGEROpenEndedEmbodied
    resource: zotero://select/items/@wangVOYAGEROpenEndedEmbodied
    title: "VOYAGER: An Open-Ended Embodied Agent with Large Language Models"
  - id: yangSWEagentAgentComputerInterfaces2024
    resource: zotero://select/items/@yangSWEagentAgentComputerInterfaces2024
    title: "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
---

# ReAct

The ReAct paper itself is not in this wiki. Everything below is what the wiki's papers state about it.

## Overview

ReAct is an agent paradigm in which the LLM iteratively generates a *Thought* (reasoning), an *Action* (tool invocation), and receives an *Observation* (tool result) until the task is complete.[^guoSAGAWorkflowAtomicScheduling2026] AgentScope describes it as an algorithm that allows the generation of interleaved reasoning and task-specific actions.[^gaoAgentScopeFlexibleRobust2024] Voyager describes it as using [chain-of-thought](chain-of-thought.md) prompting to generate both reasoning traces and action plans with LLMs.[^wangVOYAGEROpenEndedEmbodied]

## How it works

- **Canonical loop.** The LLM generates (thought, action) from the current context. If the action is "finish" the task terminates. Otherwise the action is dispatched to its named tool, and the observation is appended to the context together with the thought and the action, and the loop repeats.[^guoSAGAWorkflowAtomicScheduling2026]
- **Trajectory.** A trajectory with $T$ iterations is $\mathcal{H}_{T}=(\tau_{0},a_{0},o_{0},\dots,\tau_{i},a_{i},o_{i},\dots,\tau_{T},a_{T})$, where $\tau_{i}$, $a_{i}$, $o_{i}$ are the thought, action, and observation of round $i$. At step $t$ the thought and action are sampled from a policy conditioned on all previous context, $\pi(a_{t},\tau_{t}|\mathcal{H}_{t-1})$.[^liWebSailorV2BridgingChasm2025]
- **Serving-side view.** Each iteration needs one LLM inference call followed by a tool execution, and the context accumulates across iterations, growing from 2 to 4K tokens initially to 16 to 128K tokens for complex tasks.[^guoSAGAWorkflowAtomicScheduling2026] A ReAct agent repeatedly sends prompts and tool outputs to an LLM server, executes the returned action in an execution environment, and feeds the observation into the next turn. The per-agent context persists and grows across turns, which makes agentic serving stateful.[^yuanKAIROSStatefulContextAware2026]

## Papers using it

### As the agent scaffold

- **[SWE-agent](../papers/yangSWEagentAgentComputerInterfaces2024.md).** At each step [SWE-agent](swe-agent.md) generates a thought and a command and then incorporates the feedback from the command's execution, following ReAct.[^yangSWEagentAgentComputerInterfaces2024] With GPT-4 Turbo it solves 12.47% (286/2294) of the full [SWE-bench](../benchmarks/swe-bench.md) test set and 18.00% (54/300) of [SWE-bench Lite](../benchmarks/swe-bench-lite.md).[^yangSWEagentAgentComputerInterfaces2024]
- **[R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md).** The agent is a minimal scaffold on top of [OpenHands](openhands.md) that uses a traditional ReAct framework without any specialized workflow, giving the LLM only a bash terminal, a file editor, and a search tool.[^jainR2EGymProceduralEnvironments2025] Supervised fine-tuning uses both the agent's thoughts and its actions as targets. In the ablation table, Pass@1 is 34.4% with thoughts and 30.4% without. The running text gives the with-thoughts figure as 34.2%.[^jainR2EGymProceduralEnvironments2025]
- **[WebSailor-V2](../papers/liWebSailorV2BridgingChasm2025.md).** The agent is built on ReAct. The authors state the choice is deliberate, for its simplicity and universality, so that results reflect the model's intrinsic capabilities and the post-training pipeline. Their implementation does not presuppose complex plans or require any prompt design.[^liWebSailorV2BridgingChasm2025] Inference uses a context length of 128k and a maximum of 100 ReAct iterations, raised from 32k context in WebSailor-V1.[^liWebSailorV2BridgingChasm2025] WebSailor-V2-30B-A3B scores 35.3 on BrowseComp-EN, 44.1 on BrowseComp-ZH, and 30.6 on [HLE](../benchmarks/hle.md).[^liWebSailorV2BridgingChasm2025]
- **[Weblica](../papers/karWeblicaScalableReproducible2026.md).** The policy is a vision-language model in a ReAct-style framework: at each step it produces a reasoning trace analyzing the current observation, then selects an action, and both are appended to the history. The base model is Qwen3-VL-Instruct.[^karWeblicaScalableReproducible2026]
- **[AgentScope](../papers/gaoAgentScopeFlexibleRobust2024.md).** The tool usage module is designed on the ReAct algorithm together with a service toolkit. It has four steps: function preparation, instruction preparation, iterative reasoning, and iterative acting. The calling format is a JSON dictionary in a Markdown fenced code block with `thought`, `speak`, and `function` fields. `ReActAgent` is one of the built-in agents ("an agent that can reason and use tools"), and one application example equips a ReAct agent with DAIL-SQL to convert natural language to SQL.[^gaoAgentScopeFlexibleRobust2024]
- **[Reflexion](../papers/shinnReflexionLanguageAgents2023.md).** ReAct is one of the two Actor variants of [Reflexion](reflexion.md), the other being Chain of Thought.[^shinnReflexionLanguageAgents2023] Results are in the table below.

### As a baseline

Reflexion reports ReAct alone against ReAct + Reflexion:[^shinnReflexionLanguageAgents2023]

| Task | ReAct only | ReAct + Reflexion | Setting |
|---|---|---|---|
| [ALFWorld](../datasets/alfworld.md) | Performance increase halts between trials 6 and 7; converges at a hallucination rate of 22% | Completes 130 out of 134 tasks | GPT-3, two few-shot trajectories, 12 consecutive trials, heuristic self-evaluation |
| [HotpotQA](../datasets/hotpotqa.md) (100 questions), text-davinci-003 | 0.30 | 0.55 | 2-shot ReAct, Wikipedia API |
| HotpotQA (100 questions), gpt-3.5-turbo | 0.26 | 0.38 | same |
| HotpotQA (100 questions), gpt-4 | 0.39 | 0.51 | same |
| [WebShop](../benchmarks/webshop.md) (100 environments) | Figure only | Fails to significantly outperform ReAct; runs terminated after four trials | two-shot |

All rows: [^shinnReflexionLanguageAgents2023]

On HotpotQA, ReAct-only runs fail to probabilistically improve on any task: no task that failed in the first trial was solved in later trials at a temperature of 0.7.[^shinnReflexionLanguageAgents2023]

[Voyager](../papers/wangVOYAGEROpenEndedEmbodied.md) re-interprets ReAct to be executable in MineDojo, gives it the environment feedback and agent states as observations, and runs one round of code generation from scratch followed by three rounds of code refinement, repeated until the maximum prompting iteration.[^wangVOYAGEROpenEndedEmbodied] ReAct unlocks no level of the tech tree (wooden, stone, iron, diamond tool: 0/3 trials each within 160 prompting iterations) and solves none of the four unseen tasks (0/3 each within 50 prompting iterations).[^wangVOYAGEROpenEndedEmbodied] The paper states that ReAct and Reflexion struggle to make significant progress because the open-ended exploration goal is abstract and hard to execute without an appropriate curriculum.[^wangVOYAGEROpenEndedEmbodied] In Voyager's feature comparison, ReAct has chain-of-thought, environment feedback, and agent state, but no self-verification, execution errors, skill library, or automatic curriculum.[^wangVOYAGEROpenEndedEmbodied]

### As a workload model for LLM serving

- **[SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md).** Agent workflows follow stereotyped patterns such as ReAct loops, which SAGA captures as Agent Execution Graphs. For ReAct agents the graph is typically a linear chain with $P(v_{i}\rightarrow v_{i+1})\approx 1-p_{term}$. For linear ReAct chains, which the paper calls the dominant pattern, the next step's prompt is the full current context plus the tool observation, so cache overlap is estimated as $n_{current}/(n_{current}+\hat{n}_{obs})$.[^guoSAGAWorkflowAtomicScheduling2026] The paper states that the pattern has been adopted by frameworks including [LangChain](langchain.md), [AutoGen](autogen.md), and CrewAI.[^guoSAGAWorkflowAtomicScheduling2026]
- **[KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md).** The paper characterizes ReAct-style agents, chosen because a prior characterization study found that ReAct often lies on or near the accuracy-cost Pareto frontier, and because they are simple, widely adopted, and effective across diverse tasks. Each agent keeps long-lived state in the serving system's context cache ([KV cache](kv-cache.md)) that grows across tool-interleaved turns.[^yuanKAIROSStatefulContextAware2026]

## Variants

- [Reflexion](reflexion.md) adds a self-reflection step and an episodic memory on top of a ReAct actor.[^shinnReflexionLanguageAgents2023] Voyager describes Reflexion as built on top of ReAct.[^wangVOYAGEROpenEndedEmbodied]
- AutoGPT, as described by Voyager, decomposes a high-level goal into subgoals and executes them in a ReAct-style loop.[^wangVOYAGEROpenEndedEmbodied]
- WebSailor-V2 notes that context management strategies built on top of ReAct have yielded significant performance improvements in other agents.[^liWebSailorV2BridgingChasm2025]

## Strengths & Limitations

- Simplicity and universality are the reasons given for choosing it: it gives the clearest benchmark of a model's intrinsic capabilities (WebSailor-V2), and it is simple, widely adopted, and effective across diverse tasks (KAIROS).[^liWebSailorV2BridgingChasm2025][^yuanKAIROSStatefulContextAware2026]
- Reflexion uses ReAct as the action generator on AlfWorld because explicit intermediate thoughts had shown success in long-trajectory decision-making.[^shinnReflexionLanguageAgents2023]
- Explicit thoughts matter for fine-tuning: R2E-Gym models trained with thought demonstrations do better than those trained without.[^jainR2EGymProceduralEnvironments2025]
- Without a mechanism to learn across trials, a ReAct-only agent stops improving (AlfWorld) and does not recover tasks it failed in the first trial (HotpotQA).[^shinnReflexionLanguageAgents2023]
- In open-ended embodied exploration it makes no meaningful progress without a curriculum.[^wangVOYAGEROpenEndedEmbodied]
- The context grows at every iteration, which creates long-lived per-agent state that serving systems must manage.[^guoSAGAWorkflowAtomicScheduling2026][^yuanKAIROSStatefulContextAware2026]

## Related

- Methods: [Chain-of-thought](chain-of-thought.md), [Reflexion](reflexion.md), [SWE-agent](swe-agent.md), [OpenHands](openhands.md), [LangChain](langchain.md), [AutoGen](autogen.md), [KV cache](kv-cache.md)
- Benchmarks: [SWE-bench](../benchmarks/swe-bench.md), [SWE-bench Lite](../benchmarks/swe-bench-lite.md), [WebShop](../benchmarks/webshop.md), [HLE](../benchmarks/hle.md)
- Datasets: [ALFWorld](../datasets/alfworld.md), [HotpotQA](../datasets/hotpotqa.md)

[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^gaoAgentScopeFlexibleRobust2024]: Gao et al. 2024
[^karWeblicaScalableReproducible2026]: Kar et al. 2026
[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^liWebSailorV2BridgingChasm2025]: Li et al. 2025
[^shinnReflexionLanguageAgents2023]: Shinn et al. 2023
[^wangVOYAGEROpenEndedEmbodied]: Wang et al. n.d.
[^yangSWEagentAgentComputerInterfaces2024]: Yang et al. 2024
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
