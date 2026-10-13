---
type: Method
title: OpenHands
description: Open-source coding agent scaffold that runs a model in a sandbox over multiple turns, used in the wiki's papers as an SWE-bench agent, a rollout scaffold for training, and a serving workload.
tags: [swe-agents, agent-scaffold, coding-agents, agentic-workloads]
sources:
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
---

# OpenHands

## Overview

No paper in this wiki introduces OpenHands. The papers below use it as a scaffold, a baseline, or a workload, and this page records only what they state about it.

OpenHands is an agent scaffold for software engineering (SWE) tasks. Unlike non-agent scaffolds such as [Agentless](agentless.md), which are single-turn and pipeline-based, agent scaffolds such as OpenHands and [SWE-agent](swe-agent.md) deploy a sandbox environment in which the model interacts over multiple turns.[^shumSWERMExecutionfreeFeedback2025] SWE-RM calls OpenHands and SWE-Agent "two widely used open-sourced coding agent scaffold".[^shumSWERMExecutionfreeFeedback2025]

## How it works

The wiki's papers give only these details:

- SuffixDecoding runs OpenHands with the CodeActAgent, with `ITERATIVE_EVAL_MODE=true` and a maximum of 100 iterations, which it says the OpenHands authors recommend.[^oliaroSuffixDecodingExtremeSpeculative2024]
- ThunderAgent describes OpenHands as a heavy-initialization workflow with an average disk footprint exceeding 10GB per sandbox.[^kangThunderAgentSimpleFast2026]

## Variants

- **R2E-Gym scaffold.** A minimal scaffold built on top of OpenHands. It uses a [ReAct](react.md) framework without any specialized workflow and gives the LLM only a bash terminal, a file editor, and a search tool.[^jainR2EGymProceduralEnvironments2025]
- **OpenHands Critic.** An execution-free verifier that SWE-RM lists next to the SWE-Gym verifier. Its Table 6 row gives 11 repositories, [SWE-Gym](../datasets/swe-gym.md) as the source, a 32k context length, and a trajectory-only prompt; the amount of training data and the policy are not disclosed.[^shumSWERMExecutionfreeFeedback2025]
- **OpenHands-LM-32B.** A model named `all-hands/openhands-lm-32b-v0.1-ep3`, which SuffixDecoding describes as fine-tuned for SWE-Bench and reaching 37.2% on [SWE-Bench Verified](../benchmarks/swe-bench-verified.md).[^oliaroSuffixDecodingExtremeSpeculative2024]

## Papers using it

### As a SWE-bench agent (reported scores)

Scores on SWE-Bench Verified, as each paper prints them.

| Model | Score | Setting as labeled | Reported by |
|---|---|---|---|
| Claude-3.5-Sonnet | 53.0 | scaffold OpenHands | [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md)[^weiSWERLAdvancingLLM2025] |
| Claude-3.6-Sonnet | 53.0 | OpenHands, type Agent | [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md)[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym-32B | 32.0 | scaffold OpenHands, in a table of pass@1 results | SWE-RL[^weiSWERLAdvancingLLM2025] |
| SWE-Gym-Qwen-2.5-Coder-32B | 20.6% | OpenHands, Pass@1 | [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md)[^daAgentRLVRTrainingSoftware2025] |
| openhands-lm-32b-v0.1-ep3 | 37.2% | OpenHands running live on vLLM | [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md)[^oliaroSuffixDecodingExtremeSpeculative2024] |

See Contradictions for the two SWE-Gym-32B rows.

### As a scaffold for data collection and training

- [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md) builds its agent on OpenHands and uses it to collect 3321 successful Sonnet-3.5-v2 trajectories from 2048 unique task environments. The Qwen-2.5-Coder 32B model trained on them reaches a Pass@1 of 34.4% on SWE-Bench Verified.[^jainR2EGymProceduralEnvironments2025]
- [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md) rolls out over 400k multi-turn trajectories of up to 100 iterations with OpenHands and SWE-Agent to train its reward model.[^shumSWERMExecutionfreeFeedback2025] For evaluation it collects 32 independent OpenHands runs per SWE-bench Verified instance (temperature 1.0, top_p 0.95, max_iterations 100).[^shumSWERMExecutionfreeFeedback2025] OpenHands is also the agent scaffold in its RL training, where the hybrid reward reaches a pass@1 of 54.8% against 51.8% for the execution-based baseline.[^shumSWERMExecutionfreeFeedback2025]
- In SWE-RM's verifier comparison, trajectories from OpenHands-LM-32B are one of three evaluation sets. SWE-RM-30A3B gives an RM@32 of 48.8% on them, against 42.4% for the Agentless execution-based verifier and 41.6% for the SWE-Gym verifier.[^shumSWERMExecutionfreeFeedback2025]

### As a serving workload

- [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) traces OpenHands requests on [SWE-Bench](../benchmarks/swe-bench.md) as one of its two agentic workloads, and also runs OpenHands live on [vLLM](vllm.md).[^oliaroSuffixDecodingExtremeSpeculative2024] In the live run, decoding time takes a majority of the time across all SWE-Bench tasks, more than prefilling and code execution. SuffixDecoding outperforms PLD by 1.3–3×, a 1.8–4.5× speculative speedup over vanilla decoding, and matches the model's 37.2% score because it preserves the output distribution.[^oliaroSuffixDecodingExtremeSpeculative2024]
- [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md) deploys OpenHands and mini-SWEAgent on [SWE-bench Lite](../benchmarks/swe-bench-lite.md) as its coding-agent workloads, and OpenHands on ScienceAgentBench.[^kangThunderAgentSimpleFast2026] In the GLM-4.6 rollout test ($N=144$) on 2×H100 nodes, OpenHands throughput is 69.1 with vLLM + Gateway and 270.8 with ThunderAgent (3.92×).[^kangThunderAgentSimpleFast2026] On 8×A100 at concurrency 48 and 72, ThunderAgent is 1.16–1.62× faster than vLLM on OpenHands.[^kangThunderAgentSimpleFast2026] In the eviction-policy ablation, the gap is largest on OpenHands, where program contexts are heaviest: shortest-first is roughly 2.0× the throughput of longest-first, with an average prefill time of 7.5 s vs. 15.1 s.[^kangThunderAgentSimpleFast2026]

## Strengths & Limitations

- For serving systems OpenHands is a heavy workload: more than 10GB of disk per sandbox, against 2GB for mini-SWEAgent, and the heaviest program contexts in ThunderAgent's eviction ablation.[^kangThunderAgentSimpleFast2026]
- In code-centric settings such as SWE-Bench with SWE-agent or OpenHands, agents mostly call local, lightweight tools, and tool latency is relatively stable with low variance.[^kangThunderAgentSimpleFast2026]

# Contradictions

**SWE-Gym-32B with OpenHands on SWE-Bench Verified: 32.0 or 20.6.** SWE-RL lists SWE-Gym-32B with the OpenHands scaffold at 32.0, in a table it describes as pass@1 results.[^weiSWERLAdvancingLLM2025] Agent-RLVR lists SWE-Gym-Qwen-2.5-Coder-32B (OpenHands) at a Pass@1 of 20.6%.[^daAgentRLVRTrainingSoftware2025] R2E-Gym reports both numbers and separates them: 20.6 is the SWE-Gym 32B Pass@1, and 32.0 is "SWE-Gym (Best@16 w/ Verifier)".[^jainR2EGymProceduralEnvironments2025] The likely cause is the setting: 32.0 uses [test-time scaling](test-time-scaling.md) over 16 rollouts with a verifier, and 20.6 is a single rollout.

**Model name for the 53.0 result.** SWE-RL attributes the 53.0 OpenHands result to Claude-3.5-Sonnet, and R2E-Gym attributes it to Claude-3.6-Sonnet.[^weiSWERLAdvancingLLM2025][^jainR2EGymProceduralEnvironments2025] Neither paper explains the naming.

## Related

- Methods: [SWE-agent](swe-agent.md), [Agentless](agentless.md), [ReAct](react.md), [Execution-free verifier](execution-free-verifier.md), [Test-time scaling](test-time-scaling.md), [vLLM](vllm.md), [ThunderAgent](thunderagent.md)
- Datasets: [SWE-Gym](../datasets/swe-gym.md), [R2E-Gym](../datasets/r2e-gym.md)
- Benchmarks: [SWE-Bench Verified](../benchmarks/swe-bench-verified.md), [SWE-bench Lite](../benchmarks/swe-bench-lite.md), [SWE-bench](../benchmarks/swe-bench.md)

[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
