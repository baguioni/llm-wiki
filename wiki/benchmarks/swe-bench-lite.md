---
type: Benchmark
title: SWE-bench Lite
description: Canonical 300-instance subset of the SWE-bench test set focused on self-contained functional bug fixes, used for ablations, small-model comparisons, and as a serving workload.
tags: [benchmark, swe-agents, issue-resolution, agentic-workload]
sources:
  - id: yangSWEagentAgentComputerInterfaces2024
    resource: zotero://select/items/@yangSWEagentAgentComputerInterfaces2024
    title: "SWE-Agent: Agent-Computer Interfaces Enable Automated Software Engineering"
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
---

# SWE-bench Lite

## Setup

- **Task.** SWE-bench Lite is a canonical subset of 300 instances from [SWE-bench](swe-bench.md) that focus on evaluating self-contained functional bug fixes.[^yangSWEagentAgentComputerInterfaces2024]
- **Metric.** % Resolved (pass@1): the proportion of instances for which all tests pass after the model-generated patch is applied to the repository.[^yangSWEagentAgentComputerInterfaces2024] R2E-Gym reports the same quantity as resolve rate (%), Pass@1.[^jainR2EGymProceduralEnvironments2025]
- **SWE-agent protocol.** Temperature 0.0, window 100, history Last-5, and a per-instance budget of $4, after which existing edits are submitted automatically.[^yangSWEagentAgentComputerInterfaces2024]
- **R2E-Gym protocol.** Qwen-2.5-Coder base models fine-tuned with SFT, run in a minimal [OpenHands](../methods/openhands.md)-based [ReAct](../methods/react.md) scaffold.[^jainR2EGymProceduralEnvironments2025]

## Results

Resolve rate in %, copied with the precision of the reporting paper.

| System | Score | Setting / budget | Reported by |
|---|---|---|---|
| R2E-Gym, Qwen-2.5-Coder 32B (SFT) | 23.77 (±0.8) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| R2E-Gym, Qwen-2.5-Coder 14B (SFT) | 20.67 (±0.7) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| [SWE-agent](../methods/swe-agent.md) w/ GPT-4 Turbo | 18.00 (54/300) | pass@1, $4 per instance, $1.67 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |
| [SWE-Gym](../datasets/swe-gym.md), Qwen-2.5-Coder 32B | 15.3 (±2.5) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| SWE-agent w/ Claude 3 Opus | 13.00 | pass@1, $4 per instance, $2.18 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |
| SWE-Gym, Qwen-2.5-Coder 14B | 12.7 (±2.3) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| Shell-only agent w/ GPT-4 Turbo | 11.00 | pass@1, $1.46 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |
| R2E-Gym, Qwen-2.5-Coder 7B (SFT) | 11.0 (±0.8) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym, Qwen-2.5-Coder 7B | 10.0 (±2.4) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| Shell-only agent w/ GPT-4 Turbo, w/o Demonstration | 7.33 | pass@1, $0.79 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |
| RAG w/ Claude 3 Opus | 4.33 | non-interactive, BM25 retrieval, $0.25 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |
| Qwen-2.5-Coder 32B (base) | 3.0 (±1.4) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| Qwen-2.5-Coder 14B (base) | 2.7 (±1.9) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| RAG w/ GPT-4 Turbo | 2.67 | non-interactive, BM25 retrieval, $0.13 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |
| Qwen-2.5-Coder 7B (base) | 1.0 (±1.0) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |

### Run-to-run variance and pass@k for SWE-agent

6 separate runs of SWE-agent with GPT-4 on SWE-bench Lite (Table 10).[^yangSWEagentAgentComputerInterfaces2024]

| | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Run 6 |
|---|---|---|---|---|---|---|
| Resolve % | 17.33 | 18.00 | 18.00 | 18.67 | 17.33 | 18.33 |

| | Pass@1 | Pass@2 | Pass@3 | Pass@4 | Pass@5 | Pass@6 |
|---|---|---|---|---|---|---|
| Pass@k | 17.94 | 23.89 | 27.35 | 29.67 | 31.33 | 32.67 |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

SWE-agent also runs its interface ablations on Lite: against the default 18.0, removing linting from the edit action gives 15.0, iterative search gives 12.0, a full-file viewer gives 12.7, and full history gives 15.0.[^yangSWEagentAgentComputerInterfaces2024]

### Used as a workload

| Paper | What is measured | Models / setting | Reported numbers |
|---|---|---|---|
| [ThunderAgent](../methods/thunderagent.md)[^kangThunderAgentSimpleFast2026] | Serving throughput (steps per minute) of coding agents. OpenHands and mini-SWEAgent are deployed on SWE-bench Lite. | GLM-4.6 (355B) and Qwen-3 (235B), FP8, on 8×H100 nodes, with [vLLM](../methods/vllm.md) as the inference engine | At high concurrency (e.g., 96 parallel programs), a 1.48–3.58× speedup over vLLM and 1.17–3.31× over Continuum across base models and datasets. In RL rollout with GLM-4.6 ($N=144$) on 2×H100 nodes: mini-SWEAgent 671.8 vs. 375.4 steps per minute (1.79×), OpenHands 270.8 vs. 69.1 (3.92×), against vLLM + Gateway. |

ThunderAgent reports no resolve rates on the benchmark.[^kangThunderAgentSimpleFast2026]

## Current SOTA

Among the wiki's papers, the best score is **23.77 (±0.8)** for the R2E-Gym 32B model (Qwen-2.5-Coder 32B fine-tuned on R2E-Gym trajectories), at Pass@1.[^jainR2EGymProceduralEnvironments2025]

## Superseded claims

- **Superseded.** SWE-agent: "SWE-agent w/ GPT-4 Turbo achieves the best performance all-around", solving 18.00% (54/300) of the Lite split.[^yangSWEagentAgentComputerInterfaces2024] Superseded by R2E-Gym at 23.77 with a 32B open-weight model, and also by its 14B model at 20.67.[^jainR2EGymProceduralEnvironments2025] The scaffold, model, and budget rules differ between the two papers.

## Caveats

- **Pass@k is not a submitted score.** SWE-agent's Pass@6 of 32.67 counts an instance as solved if any of 6 runs solves it. It is above every Pass@1 row but is not comparable to them.[^yangSWEagentAgentComputerInterfaces2024]
- **Cost cap vs. step cap.** SWE-agent caps each instance at $4 of API cost.[^yangSWEagentAgentComputerInterfaces2024] R2E-Gym states a limit of a maximum of $N=40$ steps per trajectory for its trajectory collection.[^jainR2EGymProceduralEnvironments2025]
- **Precision is mixed inside R2E-Gym's table.** The 7B row and the SWE-Gym column are printed to one decimal and the 14B and 32B rows of the R2E-Gym column to two.[^jainR2EGymProceduralEnvironments2025]
- **SWE-Gym rows are second-hand.** R2E-Gym prints them as a comparison; whether it re-ran them is not stated.[^jainR2EGymProceduralEnvironments2025]
- **Variance.** SWE-agent's six runs range from 17.33 to 18.67, and the paper notes that per-instance resolution can change considerably between runs.[^yangSWEagentAgentComputerInterfaces2024]

## Related

- Benchmarks: [SWE-bench](swe-bench.md), [SWE-bench Verified](swe-bench-verified.md), [HLE](hle.md) (ThunderAgent's other serving workload)
- Methods: [SWE-agent](../methods/swe-agent.md), [OpenHands](../methods/openhands.md), [ReAct](../methods/react.md), [ThunderAgent](../methods/thunderagent.md), [Retrieval-augmented generation](../methods/retrieval-augmented-generation.md)
- Datasets: [R2E-Gym](../datasets/r2e-gym.md), [SWE-Gym](../datasets/swe-gym.md)
- Papers: [SWE-agent](../papers/yangSWEagentAgentComputerInterfaces2024.md), [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md), [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md)

[^yangSWEagentAgentComputerInterfaces2024]: Yang et al. 2024
[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
