---
type: Method
title: SWE-agent
description: LM agent for software engineering that pairs a language model with an agent-computer interface of custom file viewing, search, and editing commands, and solves 12.47% of SWE-bench with GPT-4 Turbo.
tags: [swe-agents, agent-scaffold, agent-computer-interface, issue-resolution, swe-bench]
sources:
  - id: yangSWEagentAgentComputerInterfaces2024
    resource: zotero://select/items/@yangSWEagentAgentComputerInterfaces2024
    title: "SWE-Agent: Agent-Computer Interfaces Enable Automated Software Engineering"
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
---

# SWE-agent

## Overview

SWE-agent is an agent made of a language model (LM) and an agent-computer interface (ACI) for software engineering. The ACI is the abstraction layer between the agent and the computer: it specifies the commands available to the LM, how environment state is reported back, and how the history of commands and observations is formatted into the LM input.[^yangSWEagentAgentComputerInterfaces2024] It was introduced in [Yang et al. 2024](../papers/yangSWEagentAgentComputerInterfaces2024.md), which states that, to the authors' knowledge, it is the first work to explore language agents for end-to-end software engineering.[^yangSWEagentAgentComputerInterfaces2024]

With GPT-4 Turbo, SWE-agent solves 12.47% (286/2294) of the full [SWE-bench](../benchmarks/swe-bench.md) test set and 18.00% (54/300) of [SWE-bench Lite](../benchmarks/swe-bench-lite.md). The previous best resolve rate was 3.8%, by a non-interactive, retrieval-augmented system.[^yangSWEagentAgentComputerInterfaces2024]

## How it works

At each step SWE-agent generates a thought and a command and then takes in the feedback from the command's execution, following [ReAct](react.md).[^yangSWEagentAgentComputerInterfaces2024] It is built atop the Linux shell, so common Linux commands and utilities stay available.[^yangSWEagentAgentComputerInterfaces2024] The LM's weights are not changed; the interface is designed around a fixed LM.[^yangSWEagentAgentComputerInterfaces2024]

- **Search.** The search commands return at most 50 results per query. Beyond that, results are not reported and the agent is asked for a more specific query.[^yangSWEagentAgentComputerInterfaces2024]
- **File viewer.** Shows a window of at most 100 lines of the file at a time.[^yangSWEagentAgentComputerInterfaces2024]
- **File editor.** `edit` takes 3 required arguments: the start line, the end line, and the replacement text.[^yangSWEagentAgentComputerInterfaces2024]
- **Linting guardrail.** A linter (`flake8`) runs on each edit. An edit that raises a linting error is a failed edit and is not applied.[^yangSWEagentAgentComputerInterfaces2024]
- **Context management.** Observations preceding the last 5 are each collapsed into a single line.[^yangSWEagentAgentComputerInterfaces2024]

Full details are on the [paper page](../papers/yangSWEagentAgentComputerInterfaces2024.md).

## Variants

- **mini-SWEAgent.** [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md) uses a framework it calls mini-SWEAgent and cites the SWE-agent paper for it. It describes mini-SWEAgent as a lightweight workflow with a footprint of 2GB per sandbox, against more than 10GB for [OpenHands](openhands.md). The paper does not say how mini-SWEAgent differs from SWE-agent.[^kangThunderAgentSimpleFast2026]

## Papers using it

### Reported results

| Model | Benchmark | Score | Reported by |
|---|---|---|---|
| GPT-4 Turbo | SWE-bench (full), % Resolved | 12.47 | [Yang et al. 2024](../papers/yangSWEagentAgentComputerInterfaces2024.md)[^yangSWEagentAgentComputerInterfaces2024] |
| Claude 3 Opus | SWE-bench (full), % Resolved | 10.46 | Yang et al. 2024[^yangSWEagentAgentComputerInterfaces2024] |
| GPT-4 Turbo | SWE-bench Lite, % Resolved | 18.00 | Yang et al. 2024[^yangSWEagentAgentComputerInterfaces2024] |
| Claude 3 Opus | SWE-bench Lite, % Resolved | 13.00 | Yang et al. 2024[^yangSWEagentAgentComputerInterfaces2024] |
| GPT-4o | [SWE-bench Verified](../benchmarks/swe-bench-verified.md) | 23.2 | [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md)[^weiSWERLAdvancingLLM2025] |
| Claude-3.5-Sonnet | SWE-bench Verified | 33.6 | SWE-RL[^weiSWERLAdvancingLLM2025] |

### How each paper uses it

- **Yang et al. 2024** introduces it and ablates the interface on SWE-bench Lite with GPT-4 Turbo (default 18.0): no linting 15.0, no edit command 10.3, iterative search 12.0, no search 15.7, a 30-line viewer 14.3, a full-file viewer 12.7, full history 15.0, and no demonstration 16.3.[^yangSWEagentAgentComputerInterfaces2024] SWE-agent shows a 64% relative increase over a Shell-only agent, both with GPT-4 Turbo.[^yangSWEagentAgentComputerInterfaces2024] Across 6 runs on SWE-bench Lite, Pass@1 is 17.94 and Pass@6 is 32.67.[^yangSWEagentAgentComputerInterfaces2024]
- **[SWE-RL](../papers/weiSWERLAdvancingLLM2025.md)** lists SWE-agent as a baseline scaffold for closed-source models in its SWE-bench Verified table (the two rows above).[^weiSWERLAdvancingLLM2025]
- **[SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md)** rolls out over 400k multi-turn trajectories of up to 100 iterations with OpenHands and SWE-Agent to build training data for its reward model.[^shumSWERMExecutionfreeFeedback2025]
- **[Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md)** cites SWE-Agent as an early agent design that improves the scaffold with a fixed model and no additional training, using an agent-computer interface for tool use.[^daAgentRLVRTrainingSoftware2025]
- **[ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md)** uses mini-SWEAgent on SWE-bench Lite as a serving and rollout workload. In the GLM-4.6 rollout test ($N=144$) on 2×H100 nodes, throughput is 375.4 with vLLM + Gateway and 671.8 with ThunderAgent (1.79×).[^kangThunderAgentSimpleFast2026] On 8×A100 at concurrency 48 and 72, ThunderAgent is 1.71–2.08× faster than vLLM on mini-SWEAgent.[^kangThunderAgentSimpleFast2026] With GLM-4.6 on up to 8 nodes, its speedup over the SGLang cache-aware routing baseline widens from 1.79× at 2 nodes to 2.39× at 8 nodes.[^kangThunderAgentSimpleFast2026]

## Strengths & Limitations

- Interface design alone gives a large gain: compared to RAG on SWE-bench Lite, SWE-agent yields a 6.7-fold improved % Resolved rate.[^yangSWEagentAgentComputerInterfaces2024]
- It costs more: 8-13x more than RAG on Lite.[^yangSWEagentAgentComputerInterfaces2024]
- For file localization, SWE-agent w/ GPT-4 Turbo achieves an F1 of 59.05%, against 45.47% for BM25 w/ Claude 3 Opus.[^yangSWEagentAgentComputerInterfaces2024]
- Iterative search performs worse than no search tools at all (12.0 vs. 15.7), because it can exhaust the agent's cost budget or context window.[^yangSWEagentAgentComputerInterfaces2024]
- For serving systems, code-centric workloads such as SWE-Bench with SWE-agent or OpenHands mostly call local, lightweight tools, so tool latency is relatively stable.[^kangThunderAgentSimpleFast2026]

## Related

- Methods: [OpenHands](openhands.md), [Agentless](agentless.md), [ReAct](react.md), [Retrieval-augmented generation](retrieval-augmented-generation.md), [ThunderAgent](thunderagent.md)
- Benchmarks: [SWE-bench](../benchmarks/swe-bench.md), [SWE-bench Lite](../benchmarks/swe-bench-lite.md), [SWE-bench Verified](../benchmarks/swe-bench-verified.md)

[^yangSWEagentAgentComputerInterfaces2024]: Yang et al. 2024
[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
