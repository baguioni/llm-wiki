---
type: Benchmark
title: SWE-bench
description: Benchmark of 2,294 GitHub-issue resolution tasks from 12 Python repositories, scored by the share of issues whose tests pass after the generated patch is applied.
tags: [benchmark, swe-agents, issue-resolution, agentic-workload]
sources:
  - id: yangSWEagentAgentComputerInterfaces2024
    resource: zotero://select/items/@yangSWEagentAgentComputerInterfaces2024
    title: "SWE-Agent: Agent-Computer Interfaces Enable Automated Software Engineering"
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
---

# SWE-bench

This page covers the full SWE-bench test set and uses of "SWE-bench" that name no subset. Results on the subsets are on [SWE-bench Verified](swe-bench-verified.md) and [SWE-bench Lite](swe-bench-lite.md).

## Setup

- **Task.** The dataset has 2294 task instances from 12 different repositories of popular Python packages.[^yangSWEagentAgentComputerInterfaces2024] Agent-RLVR credits SWE-bench with first defining the task of agents that autonomously solve issues and debug coding problems in a large repository: agents are assessed on their ability to produce a patch that passes a set of unit tests, and problem statements are derived from previous pull-requests or commits in the repository.[^daAgentRLVRTrainingSoftware2025]
- **Metric.** % Resolved (pass@1): the proportion of instances for which all tests pass after the model-generated patch is applied to the repository.[^yangSWEagentAgentComputerInterfaces2024]
- **Splits and subsets.**

| Split or subset | Instances | Executable environments | Stated by |
|---|---|---|---|
| SWE-Bench (train) | 19,008 | no | R2E-Gym (Table 1)[^jainR2EGymProceduralEnvironments2025] |
| SWE-Bench (test) | 2,294 | yes | R2E-Gym (Table 1)[^jainR2EGymProceduralEnvironments2025]; SWE-agent[^yangSWEagentAgentComputerInterfaces2024] |
| [SWE-bench Lite](swe-bench-lite.md) | 300 | | SWE-agent[^yangSWEagentAgentComputerInterfaces2024] |
| [SWE-bench Verified](swe-bench-verified.md) | 500 | | SWE-RL[^weiSWERLAdvancingLLM2025] |

- A development split also exists: SWE-agent tuned its interface on hand-picked examples from it and ran its hyperparameter sweep on 37 instances sampled from it.[^yangSWEagentAgentComputerInterfaces2024]
- **Baseline protocol from the benchmark.** The non-interactive retrieval-augmented generation (RAG) baseline retrieves the most relevant codebase files with BM25, using the issue as the query, and asks the model to directly generate a patch file.[^yangSWEagentAgentComputerInterfaces2024]
- **SWE-agent protocol.** Temperature 0.0 and a per-instance budget of $4. When a run exceeds the budget, existing edits are submitted automatically.[^yangSWEagentAgentComputerInterfaces2024]

## Results

Full test set (2,294 instances), % Resolved.

| System | Score | Setting / budget | Reported by |
|---|---|---|---|
| [SWE-agent](../methods/swe-agent.md) w/ GPT-4 Turbo | 12.47 (286/2294) | pass@1, $4 per instance, $1.59 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |
| SWE-agent w/ Claude 3 Opus | 10.46 | pass@1, $4 per instance, $2.59 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |
| RAG w/ Claude 3 Opus | 3.79 | non-interactive, BM25 retrieval, $0.25 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |
| RAG w/ GPT-4 Turbo | 1.31 | non-interactive, BM25 retrieval, $0.13 avg. cost | SWE-agent (Table 1)[^yangSWEagentAgentComputerInterfaces2024] |

$ Avg. Cost is the API inference cost averaged over successfully resolved instances.[^yangSWEagentAgentComputerInterfaces2024]

### Used as a workload

| Paper | What is measured | Models / setting | Reported numbers |
|---|---|---|---|
| SuffixDecoding[^oliaroSuffixDecodingExtremeSpeculative2024] | Speculative decoding speedup on traced requests of the [OpenHands](../methods/openhands.md) agent running SWE-Bench. The paper does not name a subset for the traces; its end-to-end experiment is on [SWE-bench Verified](swe-bench-verified.md). | Llama-3.1-8B-Instruct, a single H100 GPU, batch size 1 | Mean speedup of $2.5\times$ over vanilla decoding, a $1.7\times$ improvement over PLD. 7.8 mean accepted tokens per step, against 3.2 for PLD. EAGLE-2/3 fail due to their maximum sequence length limitations. |

## Current SOTA

On the full test set, the best score among the wiki's papers is **12.47%** for SWE-agent with GPT-4 Turbo, at pass@1 with a $4 per-instance budget.[^yangSWEagentAgentComputerInterfaces2024] It is the only wiki paper that reports full-test-set scores. Later papers in the wiki report on [SWE-bench Verified](swe-bench-verified.md) instead.[^weiSWERLAdvancingLLM2025][^jainR2EGymProceduralEnvironments2025][^daAgentRLVRTrainingSoftware2025]

## Superseded claims

- **Superseded.** The previous best resolve rate was 3.8%, by a non-interactive, retrieval-augmented system, as cited by SWE-agent.[^yangSWEagentAgentComputerInterfaces2024] Superseded by SWE-agent w/ GPT-4 Turbo at 12.47%.[^yangSWEagentAgentComputerInterfaces2024]

## Caveats

- **Subset scores are not full-set scores.** SWE-RL writes that its model "sets a new record for Llama-based methods on SWE-bench", but the score behind that sentence (41.0) is on SWE-bench Verified.[^weiSWERLAdvancingLLM2025]
- **Cost cap.** For SWE-agent with GPT-4 Turbo on the full set, 14.3% of instances that end with a `submit` are resolved, against 3.1% for those that end on the cost limit.[^yangSWEagentAgentComputerInterfaces2024]
- **Training-data decontamination.** Training papers remove the benchmark's repositories from their data: SWE-RL excludes all repositories used by SWE-bench during data processing[^weiSWERLAdvancingLLM2025], Agent-RLVR collects no issues from any repository in the SWE-Bench test set[^daAgentRLVRTrainingSoftware2025], and R2E-Gym trains on a subset of [R2E-Gym](../datasets/r2e-gym.md) with no repository overlap with SWE-Bench.[^jainR2EGymProceduralEnvironments2025]
- **The train split is not executable.** R2E-Gym notes that the SWE-Bench training split contains output patches but lacks executable environments.[^jainR2EGymProceduralEnvironments2025]
- **Python only.** Agent-RLVR limits its work to Python and names SWE-Bench as one of the infrastructure components that support it.[^daAgentRLVRTrainingSoftware2025]

## Related

- Benchmarks: [SWE-bench Verified](swe-bench-verified.md), [SWE-bench Lite](swe-bench-lite.md), [Terminal-Bench](terminal-bench.md)
- Methods: [SWE-agent](../methods/swe-agent.md), [Retrieval-augmented generation](../methods/retrieval-augmented-generation.md), [OpenHands](../methods/openhands.md), [Agentless](../methods/agentless.md)
- Datasets: [SWE-Gym](../datasets/swe-gym.md), [R2E-Gym](../datasets/r2e-gym.md)
- Papers: [SWE-agent](../papers/yangSWEagentAgentComputerInterfaces2024.md), [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md), [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md), [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md), [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md)

[^yangSWEagentAgentComputerInterfaces2024]: Yang et al. 2024
[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
