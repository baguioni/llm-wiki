---
type: Benchmark
title: SWE-bench Verified
description: Human-verified 500-problem subset of SWE-bench for resolving real GitHub issues, reported in this wiki at rollout budgets from greedy pass@1 to reranking over 500 patches.
tags: [benchmark, swe-agents, issue-resolution, test-time-scaling, agentic-workload]
sources:
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: daAgentRLVRTrainingSoftware2025
    resource: zotero://select/items/@daAgentRLVRTrainingSoftware2025
    title: "Agent-RLVR: Training Software Engineering Agents via Guidance and Environment Rewards"
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: guoSAGAWorkflowAtomicScheduling2026
    resource: zotero://select/items/@guoSAGAWorkflowAtomicScheduling2026
    title: "SAGA: Workflow-Atomic Scheduling for AI Agent Inference on GPU Clusters"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
---

# SWE-bench Verified

## Setup

- **Task.** SWE-bench Verified is a subset of [SWE-bench](swe-bench.md) with 500 human-verified problems.[^weiSWERLAdvancingLLM2025][^shumSWERMExecutionfreeFeedback2025] KAIROS describes it as a human validated benchmark for whether agents can generate test-passing fixes for real GitHub issues.[^yuanKAIROSStatefulContextAware2026]
- **Metric.** The resolve rate (%): one final patch per problem is submitted and checked. What differs between papers is how many rollouts are spent before that one patch is chosen. The budget names used in this wiki's papers are:

| Budget name | Definition | Defined by |
|---|---|---|
| Pass@1 (greedy) | One rollout with greedy decoding at all steps. | Agent-RLVR[^daAgentRLVRTrainingSoftware2025]; SWE-RM uses the same for its RL results (1 trajectory and 1 patch per instance, greedy, no test-time scaling)[^shumSWERMExecutionfreeFeedback2025] |
| "pass@1" after reranking | 500 patches are generated per problem at temperature 1.0, the top 30 reproduction tests are used for execution and reranking, and only the highest-ranked patch is submitted. SWE-RL calls the resulting score pass@1. | SWE-RL[^weiSWERLAdvancingLLM2025] |
| Best@K | Percentage of problems where a verifier selects a correct patch out of $K$ trajectories. | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| RM@K | Resolve rate of the final trajectory selected by a reward model from $k$ samples. | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| Pass@K | Resolve rate with at least one successful solution among $k$ trajectories. This is an upper bound for selection, not a submitted score. | SWE-RM[^shumSWERMExecutionfreeFeedback2025]; also used by Agent-RLVR and R2E-Gym[^daAgentRLVRTrainingSoftware2025][^jainR2EGymProceduralEnvironments2025] |

- **Protocols as stated.**
  - SWE-RL: [Agentless](../methods/agentless.md)-derived pipeline scaffold (Agentless Mini), 500 repair samples and 30 reproduction test samples in the main evaluation. No error bars are reported.[^weiSWERLAdvancingLLM2025]
  - R2E-Gym: an [OpenHands](../methods/openhands.md)-based [ReAct](../methods/react.md) agent. The Best@K pool is 1 trajectory at temperature $T=0$ and 25 trajectories at temperatures $T=0.8$ and $T=0.9$ from the R2E-Gym-32B model.[^jainR2EGymProceduralEnvironments2025]
  - Agent-RLVR: an Agentless-based scaffold with only the localization and repair steps, the SWE-bench authors' evaluation harness on Modal. 6 instances could not be compiled and are still counted in the metrics. With the reward model, $k=32$ patches are generated (greedy for the first, temperature=0.6 for the rest) and ranked to select one final patch.[^daAgentRLVRTrainingSoftware2025]
  - SWE-RM: 32 independent OpenHands runs per instance (temperature 1.0, top_p 0.95, max_iterations 100), giving $32\times 500$ trajectories. For every $k<32$ the mean and variance of 5 random runs are reported.[^shumSWERMExecutionfreeFeedback2025]

## Results

Scores are resolve rate in %, copied with the precision of the reporting paper. "Quoted" in the last column means the reporting paper did not run the system itself and took the score from a leaderboard or another paper. A system quoted by several papers has one row per distinct score.

### Systems evaluated by the reporting paper

| System | Score | Setting / budget | Reported by |
|---|---|---|---|
| Qwen3-Coder-Max + SWE-RM-30A3B | 74.6% | RM@32, execution-free verifier, OpenHands | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Max + DeepSWE EB verifier | 67.6% | RM@32, execution-based | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Max | 67.0% | no test-time scaling (the baseline SWE-RM lifts to 74.6%) | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Max + DeepSWE EF verifier | 66.2% | RM@32, execution-free | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Max + SWE-Gym verifier | 65.4% | RM@32, execution-free | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Max + Agentless verifier | 65.0% | RM@32, execution-based | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Flash + SWE-RM-30A3B | 62.0% | RM@32, execution-free | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-30B-A3B policy, RL with hybrid (execution-based + SWE-RM) reward | 54.8% | pass@1, 1 trajectory, greedy, OpenHands | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Flash + DeepSWE EB verifier | 54.6% | RM@32, execution-based | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Flash + DeepSWE EF verifier | 53.2% | RM@32, execution-free | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Flash + Agentless verifier | 52.6% | RM@32, execution-based | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-30B-A3B policy, RL with execution-based reward only | 51.8% | pass@1, 1 trajectory, greedy, OpenHands | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Flash | 51.6% | no test-time scaling (the baseline SWE-RM lifts to 62.0%) | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Flash + SWE-Gym verifier | 51.2% | RM@32, execution-free | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| R2E-Gym-32B + hybrid verifier | 51.0 | Best@26 | R2E-Gym (Table 4)[^jainR2EGymProceduralEnvironments2025] |
| R2E-Gym-32B + hybrid verifier | 49.4 | Best@16 | R2E-Gym (Table 4)[^jainR2EGymProceduralEnvironments2025] |
| OpenHands-LM-32B + SWE-RM-30A3B | 48.8% | RM@32, execution-free | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| OpenHands-LM-32B + DeepSWE EF verifier | 44.6% | RM@32, execution-free | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| OpenHands-LM-32B + DeepSWE EB verifier | 44.2% | RM@32, execution-based | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| R2E-Gym-32B + execution-based verifier only | 43.7% | Best@K plateau as editing-agent rollouts grow | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| R2E-Gym-32B + execution-free verifier only | 42.8% | Best@26 (also the Best@K plateau) | R2E-Gym[^jainR2EGymProceduralEnvironments2025] |
| OpenHands-LM-32B + Agentless verifier | 42.4% | RM@32, execution-based | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| OpenHands-LM-32B + SWE-Gym verifier | 41.6% | RM@32, execution-free | SWE-RM (Table 4)[^shumSWERMExecutionfreeFeedback2025] |
| Llama3-SWE-RL-70B (Agentless Mini) | 41.0 | "pass@1" after reranking 500 repair samples with 30 reproduction tests | SWE-RL (Table 1)[^weiSWERLAdvancingLLM2025] |
| Llama3-SWE-RL-70B (Agentless Mini) | 40.0 | same, 160 repair samples, 30 test samples | SWE-RL (Figure 4)[^weiSWERLAdvancingLLM2025] |
| Llama3-SWE-RL-70B (Agentless Mini) | 38.8 | same, 500 repair samples, 1 test sample | SWE-RL (Figure 4)[^weiSWERLAdvancingLLM2025] |
| openhands-lm-32b-v0.1-ep3 (OpenHands) | 37.2% | the model's stated score, budget not stated; SuffixDecoding states it matches this score | SuffixDecoding[^oliaroSuffixDecodingExtremeSpeculative2024] |
| Llama3-SWE-SFT-70B (Agentless Mini) | 36.2 | same protocol as the 41.0 row | SWE-RL (Table 1)[^weiSWERLAdvancingLLM2025] |
| R2E-Gym-32B (Qwen-2.5-Coder 32B, SFT) | 34.4 (±1.2) | Pass@1 | R2E-Gym (Tables 3, 4)[^jainR2EGymProceduralEnvironments2025] |
| Llama3-SWE-RL-70B (Agentless Mini) | 33.6 | reranking, 20 repair samples, 30 test samples | SWE-RL (Figure 4)[^weiSWERLAdvancingLLM2025] |
| Agent-RLVR-RM-Qwen-2.5-72B-Instruct | 27.8% (±3.8) | one patch selected by a reward model from $k=32$ patches (the paper's table labels the column Pass@1) | Agent-RLVR (Table 1)[^daAgentRLVRTrainingSoftware2025] |
| R2E-Gym 14B (Qwen-2.5-Coder 14B, SFT) | 26.8 (±1.4) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| Agent-RLVR-Qwen-2.5-72B-Instruct | 22.4% (±3.6) | Pass@1, greedy | Agent-RLVR (Table 1)[^daAgentRLVRTrainingSoftware2025] |
| Agent-RLVR-Qwen-2.5-Coder-32B | 21.6% (±3.5) | Pass@1, greedy | Agent-RLVR (Table 1)[^daAgentRLVRTrainingSoftware2025] |
| Agent-SFT-Qwen-2.5-72B-Instruct | 20.8% (±3.5) | Pass@1, greedy | Agent-RLVR (Table 1)[^daAgentRLVRTrainingSoftware2025] |
| SWE-Gym, Qwen-2.5-Coder 32B | 20.6 (±2.1) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| Agent-RLVR without guidance, Qwen-2.5-72B-Instruct | 19.8% | Pass@1 | Agent-RLVR[^daAgentRLVRTrainingSoftware2025] |
| R2E-Gym 7B (Qwen-2.5-Coder 7B, SFT) | 19.0 (±1.0) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| Agent-RLVR-Qwen-2.5-Coder-14B | 18.0% (±3.4) | Pass@1, greedy | Agent-RLVR (Table 1)[^daAgentRLVRTrainingSoftware2025] |
| SWE-Gym, Qwen-2.5-Coder 14B | 16.4 (±2.0) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym, Qwen-2.5-Coder 7B | 10.6 (±2.1) | Pass@1 | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| Qwen-2.5-72B-Instruct (base) | 9.4% (±2.5) | Pass@1, greedy, Agentless-based scaffold | Agent-RLVR (Table 1)[^daAgentRLVRTrainingSoftware2025] |
| Qwen-2.5-Coder-32B (base) | 8.8% (±2.5) | Pass@1, greedy, Agentless-based scaffold | Agent-RLVR (Table 1)[^daAgentRLVRTrainingSoftware2025] |
| Qwen-2.5-Coder 32B (base) | 7.0 (±1.3) | Pass@1, OpenHands-based scaffold | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| Qwen-2.5-Coder-14B (base) | 6.8% (±2.2) | Pass@1, greedy, Agentless-based scaffold | Agent-RLVR (Table 1)[^daAgentRLVRTrainingSoftware2025] |
| Qwen-2.5-Coder 14B (base) | 4.0 (±1.6) | Pass@1, OpenHands-based scaffold | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |
| Qwen-2.5-Coder 7B (base) | 1.8 (±1.3) | Pass@1, OpenHands-based scaffold | R2E-Gym (Table 3)[^jainR2EGymProceduralEnvironments2025] |

Upper bounds that are not submitted scores: the R2E-Gym-32B trajectory pool has Pass@26 = 64.4%[^jainR2EGymProceduralEnvironments2025], and Agent-RLVR-Qwen-2.5-72B-Instruct has Pass@32 = 38.4% (34.2% without guidance).[^daAgentRLVRTrainingSoftware2025]

SWE-RL also reports a repair-only setting (oracle localized files, greedy decoding, no test generation or execution): Llama3-SWE-RL-70B 34.8, Llama3-SWE-SFT-70B 29.6, Llama-3.3-70B-Instruct 5.4 (16.6 with 20-sample majority voting at temperature 0.6).[^weiSWERLAdvancingLLM2025] These are not end-to-end resolve rates.

### Scores quoted from other sources

| System | Score | Setting / budget as the quoting paper labels it | Reported by |
|---|---|---|---|
| Claude-3.7-Sonnet, Claude + Tools (Best@Any) | 70.3 | Best@Any | R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| Claude-3.7-Sonnet, Claude + Tools | 62.3 | not stated | R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| Claude-3.5-Sonnet, OpenHands | 53.0 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| Claude-3.6-Sonnet, OpenHands | 53.0 | not stated | R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| Claude-3.5-Sonnet, Agentless | 50.8 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025]; Agent-RLVR (Table 3, quoted, 50.8%)[^daAgentRLVRTrainingSoftware2025] |
| Claude-3.6-Sonnet, Agentless-1.5 | 50.8 | not stated | R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| DeepSeek-R1, Agentless | 49.2 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025]; Agent-RLVR (Table 3, quoted, 49.2%)[^daAgentRLVRTrainingSoftware2025]; R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| Claude-3.5-Sonnet, Tools | 49.0 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| Claude-3.6-Sonnet, Claude + Tools | 49.0 | not stated | R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| O1, Agentless | 48.0 | not stated | R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| Claude-3.5-Sonnet, AutoCodeRover-v2.0 | 46.2 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| DeepSeek-V3, Agentless | 42.0 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025]; Agent-RLVR (Table 3, quoted, 42.0%)[^daAgentRLVRTrainingSoftware2025] |
| o1-preview, Agentless | 41.3 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| Llama3-SWE-RL-70B / SWE-RL-70B | 41.0 | Pass@1 per Agent-RLVR; Best@500 w/ Tests per R2E-Gym | Agent-RLVR (Table 3, quoted, 41.0%)[^daAgentRLVRTrainingSoftware2025]; R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| GPT-4o, Agentless | 38.8 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025]; Agent-RLVR (Table 3, quoted, 38.8%)[^daAgentRLVRTrainingSoftware2025] |
| GPT-4o, Agentless-1.5 | 34.0 | not stated | R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| Claude-3.5-Sonnet, [SWE-agent](../methods/swe-agent.md) | 33.6 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| SWE-Fixer-72B | 32.8 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| SWE-Fixer-72B | 30.2 | Pass@1 per Agent-RLVR; not stated by R2E-Gym | Agent-RLVR (Table 3, quoted, 30.2%)[^daAgentRLVRTrainingSoftware2025]; R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym-32B, OpenHands | 32.0 | listed in a pass@1 table by SWE-RL; Best@16 w/ Verifier per R2E-Gym | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025]; R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| SWE-Gym-Qwen-2.5-Coder-32B, OpenHands | 20.6% | Pass@1 | Agent-RLVR (Table 3, quoted)[^daAgentRLVRTrainingSoftware2025] |
| Lingma-SWE-GPT-72B, SWE-SynInfer | 30.2 | not stated | R2E-Gym (Table 4, quoted)[^jainR2EGymProceduralEnvironments2025] |
| Lingma-SWE-GPT-72B, SWE-SynInfer | 28.8 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| GPT-4o, SWE-agent | 23.2 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| Lingma-SWE-GPT-7B, SWE-SynInfer | 18.2 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| SWE-Llama-7B, RAG | 1.4 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |
| SWE-Llama-13B, RAG | 1.2 | listed in a pass@1 table | SWE-RL (Table 1, quoted)[^weiSWERLAdvancingLLM2025] |

SWE-RL states that its Table 1 scores are collected from the SWE-bench Leaderboard or from the corresponding reference.[^weiSWERLAdvancingLLM2025]

### Used as a workload

These papers run agents on SWE-bench Verified to measure a serving system. They report no new task scores.

| Paper | What is measured | Models / setting | Reported numbers |
|---|---|---|---|
| SAGA[^guoSAGAWorkflowAtomicScheduling2026] | Task completion time (TCT) and GPU memory utilization of a workflow-aware scheduler. The paper calls the workload "SWE-bench" and specifies the 500 "verified" subset tasks, with agent trajectories of mean 37 steps and max 150 steps. | Llama-3-70B-Instruct, 64 A100-80GB GPUs, mean ± std over 10 trials | TCT 203.4±12.8 s for SAGA vs. 612.3±32.1 s for [vLLM](../methods/vllm.md) v0.6.0 and 352.1±21.4 s for vLLM+APC v0.15.1, that is $3.01\times$ and $1.73\times$ speedups. |
| KAIROS[^yuanKAIROSStatefulContextAware2026] | GPU power under a per-agent throughput SLO, with mini-swe-agent as the scaffold. | Qwen3-Coder-30B and Ministral-3-14B on vLLM, NVIDIA H100 | At 0.06 jobs/s, power falls from 367.9 W to 240.9 W (34.5%) on Qwen3-Coder-30B and from 370.8 W to 263.8 W (28.9%) on Ministral-3-14B. With four instances at 0.16 jobs/s, average power falls from 1279.5 W to 686.5 W with context-aware routing. |
| SuffixDecoding[^oliaroSuffixDecodingExtremeSpeculative2024] | End-to-end task-completion time of the OpenHands agent with speculative decoding. | all-hands/openhands-lm-32b-v0.1-ep3 on vLLM, 4 H100 GPUs with 4-way tensor parallelism, prefix caching enabled, concurrency of 8 tasks | 1.8–4.5$\times$ speculative speedup over vanilla decoding, and 1.3–3$\times$ over PLD. The method preserves the output distribution, so the task score stays at the model's 37.2%. |

## Current SOTA

Among the wiki's papers, the best score is **74.6%** for Qwen3-Coder-Max with the SWE-RM-30A3B execution-free verifier, at RM@32 (one trajectory selected from 32 OpenHands runs).[^shumSWERMExecutionfreeFeedback2025] SWE-RM describes this as new state-of-the-art performance among open-source models.[^shumSWERMExecutionfreeFeedback2025]

Best score per budget class:

| Budget class | Best score | System | Reported by |
|---|---|---|---|
| Selection over many rollouts | 74.6% (RM@32) | Qwen3-Coder-Max + SWE-RM-30A3B | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| No test-time scaling | 67.0% | Qwen3-Coder-Max | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |
| Greedy pass@1 of a model trained in the paper | 54.8% | Qwen3-30B-A3B policy after RL with hybrid reward | SWE-RM[^shumSWERMExecutionfreeFeedback2025] |

The highest score quoted for a proprietary model is 70.3 for Claude-3.7-Sonnet with Claude + Tools (Best@Any), quoted by R2E-Gym.[^jainR2EGymProceduralEnvironments2025]

## Superseded claims

- **Superseded.** SWE-RL: Llama3-SWE-RL-70B at 41.0 is "the best performance among medium-sized language models (<100B)".[^weiSWERLAdvancingLLM2025] Superseded by R2E-Gym, whose 32B model reaches 51.0 at Best@26 and 49.4 at Best@16[^jainR2EGymProceduralEnvironments2025], and later by SWE-RM, whose RL-trained Qwen3-30B-A3B policy reaches 54.8% at greedy pass@1.[^shumSWERMExecutionfreeFeedback2025] The budgets differ: 41.0 uses 500 repair samples, 51.0 uses 26 rollouts, and 54.8% uses one.
- **Superseded.** R2E-Gym: 51% is "a new state-of-the-art for open-weight SWE agents".[^jainR2EGymProceduralEnvironments2025] Superseded by SWE-RM: 62.0% (Qwen3-Coder-Flash) and 74.6% (Qwen3-Coder-Max) at RM@32, which SWE-RM calls best-in-class among 30B-level and all open-source models respectively.[^shumSWERMExecutionfreeFeedback2025]
- **Superseded.** SWE-RM names DeepSWE Hybrid-TTS "the current state-of-the-art" for test-time scaling and then reports that SWE-RM outperforms the DeepSWE execution-based and execution-free verifiers on all three policies (for Qwen3-Coder-Max, 74.6% vs. 67.6% and 66.2%).[^shumSWERMExecutionfreeFeedback2025] The comparison is against the two DeepSWE components separately, not the hybrid.

Agent-RLVR makes no best-score claim: its 27.8% is below several rows of its own comparison table.[^daAgentRLVRTrainingSoftware2025]

## Caveats

- **Budgets are not comparable.** The rows mix one greedy rollout, selection from 16, 26, or 32 rollouts, and reranking of 500 patches. SWE-RL's score rises from 33.6 at 20 repair samples to 41.0 at 500[^weiSWERLAdvancingLLM2025], and R2E-Gym's rises from 34.4 at Pass@1 to 51.0 at Best@26.[^jainR2EGymProceduralEnvironments2025]
- **"Pass@1" has two meanings.** SWE-RL and Agent-RLVR label a score pass@1 when one patch is submitted, even if it was selected from 500 or 32 candidates.[^weiSWERLAdvancingLLM2025][^daAgentRLVRTrainingSoftware2025] R2E-Gym and SWE-RM reserve Pass@1 for a single rollout and use Best@K or RM@K otherwise.[^jainR2EGymProceduralEnvironments2025][^shumSWERMExecutionfreeFeedback2025]
- **Verifier type.** Execution-based selection (SWE-RL, the Agentless and DeepSWE EB rows) needs generated tests and a sandbox. Execution-free selection (SWE-RM, Agent-RLVR's reward model) scores without execution. R2E-Gym's hybrid uses both.[^weiSWERLAdvancingLLM2025][^shumSWERMExecutionfreeFeedback2025][^daAgentRLVRTrainingSoftware2025][^jainR2EGymProceduralEnvironments2025] See [test-time scaling](../methods/test-time-scaling.md) and [execution-free verifier](../methods/execution-free-verifier.md).
- **Scaffolds differ.** Pipeline scaffolds (Agentless, Agentless Mini) and agent scaffolds (OpenHands, SWE-agent) are mixed in every comparison table.[^weiSWERLAdvancingLLM2025][^jainR2EGymProceduralEnvironments2025]
- **Model size and openness.** Rows range from 7B open-weight models to proprietary models. SWE-RL marks DeepSeek-V3 and DeepSeek-R1 as open-source Mixture-of-Experts models with 671B total and 37B active parameters and groups them with closed models.[^weiSWERLAdvancingLLM2025] SWE-RM is a 30B MoE with 3B activated parameters, but the policies it scores are Qwen3-Coder-Flash and Qwen3-Coder-Max.[^shumSWERMExecutionfreeFeedback2025]
- **Error bars.** SWE-RL reports none.[^weiSWERLAdvancingLLM2025] Agent-RLVR reports standard deviations of ±2.2 to ±3.8 points, so its 22.4% vs. 20.8% RLVR-vs-SFT gap is inside one standard deviation.[^daAgentRLVRTrainingSoftware2025]
- **Broken instances.** Agent-RLVR could not compile 6 instances and counts them as failures.[^daAgentRLVRTrainingSoftware2025]
- **Training data.** SWE-RL notes that Lingma-SWE-GPT, [SWE-Gym](../datasets/swe-gym.md), and SWE-Fixer include distilled outputs from GPT-4o or Claude-3.5-Sonnet in their training data.[^weiSWERLAdvancingLLM2025] [R2E-Gym](../datasets/r2e-gym.md) trains on Sonnet-3.5-v2 trajectories.[^jainR2EGymProceduralEnvironments2025] SWE-RM's RL policy is warmed up on in-house agentic trajectories.[^shumSWERMExecutionfreeFeedback2025]
- **Ablation variants inside SWE-RM.** RM@32 for Qwen3-Coder-Max is 74.6% for the final SWE-RM (Table 4), 74.4% for the 256k model in the context-length ablation (Table 2), and 71.0% for the 2:1 model in the ratio ablation (Table 1). These are different reward model variants, not a conflict.[^shumSWERMExecutionfreeFeedback2025]
- **Contamination.** Agent-RLVR states that contamination with respect to pre-training is possible, although repositories do not overlap between training and test sets.[^daAgentRLVRTrainingSoftware2025]

# Contradictions

Each item keeps both attributed values. None can be resolved from the wiki's sources.

1. **SWE-Fixer-72B: 32.8 vs. 30.2.** SWE-RL quotes 32.8.[^weiSWERLAdvancingLLM2025] Agent-RLVR quotes 30.2% and R2E-Gym quotes 30.2.[^daAgentRLVRTrainingSoftware2025][^jainR2EGymProceduralEnvironments2025] All three cite the SWE-Fixer paper as the source and none states a budget, so the setting difference is unknown.
2. **Lingma-SWE-GPT-72B (SWE-SynInfer): 28.8 vs. 30.2.** SWE-RL quotes 28.8.[^weiSWERLAdvancingLLM2025] R2E-Gym quotes 30.2.[^jainR2EGymProceduralEnvironments2025] Both cite the same reference and neither states a budget.
3. **SWE-Gym-32B: 32.0 vs. 20.6.** SWE-RL lists 32.0 in a table it describes as pass@1 results, with no rollout budget.[^weiSWERLAdvancingLLM2025] Agent-RLVR lists 20.6% as Pass@1.[^daAgentRLVRTrainingSoftware2025] R2E-Gym reports both and explains the gap: 20.6 is Pass@1 and 32.0 is Best@16 with a verifier.[^jainR2EGymProceduralEnvironments2025] The likely cause is the budget, so SWE-RL's row is a 16-rollout score in a table of nominally pass@1 scores.
4. **Llama3-SWE-RL-70B: same 41.0, different budget label.** SWE-RL calls 41.0 a pass@1 score and Agent-RLVR lists it under a Pass@1 column next to its own greedy single-rollout scores.[^weiSWERLAdvancingLLM2025][^daAgentRLVRTrainingSoftware2025] R2E-Gym labels it "Best@500 w/ Tests".[^jainR2EGymProceduralEnvironments2025] SWE-RL's own protocol (500 patches, reranking with 30 reproduction tests) matches R2E-Gym's label.[^weiSWERLAdvancingLLM2025] Agent-RLVR's Table 3 therefore compares a greedy 22.4% with a 500-sample 41.0%.
5. **GPT-4o with Agentless: 38.8 vs. 34.0.** SWE-RL and Agent-RLVR quote 38.8 for GPT-4o with Agentless.[^weiSWERLAdvancingLLM2025][^daAgentRLVRTrainingSoftware2025] R2E-Gym quotes 34.0 for GPT-4o with "Agentless-1.5".[^jainR2EGymProceduralEnvironments2025] The scaffold version name differs; the papers do not say whether the model snapshot or budget also differs.
6. **Claude model naming for identical scores.** SWE-RL attributes 49.0 (Tools), 50.8 (Agentless), and 53.0 (OpenHands) to Claude-3.5-Sonnet, and Agent-RLVR attributes 50.8% to Claude-3.5-Sonnet.[^weiSWERLAdvancingLLM2025][^daAgentRLVRTrainingSoftware2025] R2E-Gym attributes the same three scores to Claude-3.6-Sonnet (with Agentless-1.5 for the 50.8 row).[^jainR2EGymProceduralEnvironments2025] The scores agree; the model and scaffold names do not.
7. **Qwen-2.5-Coder-32B base model: 8.8% vs. 7.0.** Agent-RLVR measures 8.8% (±2.5) with its Agentless-based scaffold.[^daAgentRLVRTrainingSoftware2025] R2E-Gym measures 7.0 (±1.3) with its OpenHands-based scaffold.[^jainR2EGymProceduralEnvironments2025] The scaffolds differ and the values are within the stated deviations. The 14B base model shows the same pattern (6.8% vs. 4.0).[^daAgentRLVRTrainingSoftware2025][^jainR2EGymProceduralEnvironments2025]
8. **R2E-Gym with-thoughts Pass@1: 34.4 vs. 34.2.** Inside R2E-Gym, the ablation table gives 34.4 and the running text gives 34.2%, as noted on the [Paper page](../papers/jainR2EGymProceduralEnvironments2025.md).[^jainR2EGymProceduralEnvironments2025]

## Related

- Benchmarks: [SWE-bench](swe-bench.md), [SWE-bench Lite](swe-bench-lite.md), [Terminal-Bench](terminal-bench.md), [WebArena](webarena.md) (SAGA's second workload)
- Methods: [Test-time scaling](../methods/test-time-scaling.md), [Execution-free verifier](../methods/execution-free-verifier.md), [Agentless](../methods/agentless.md), [OpenHands](../methods/openhands.md), [SWE-agent](../methods/swe-agent.md), [GRPO](../methods/grpo.md), [DPO](../methods/dpo.md), [vLLM](../methods/vllm.md)
- Datasets: [SWE-Gym](../datasets/swe-gym.md), [R2E-Gym](../datasets/r2e-gym.md)
- Papers: [SWE-RL](../papers/weiSWERLAdvancingLLM2025.md), [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md), [Agent-RLVR](../papers/daAgentRLVRTrainingSoftware2025.md), [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md), [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md), [SAGA](../papers/guoSAGAWorkflowAtomicScheduling2026.md), [KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md)

## Open questions and results

- [Which SWE-bench Verified scores are comparable?](../questions/swe-bench-verified-comparability.md)
- [Test-time scaling on SWE-bench Verified](../results/swe-bench-verified-test-time-scaling.md)

[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^daAgentRLVRTrainingSoftware2025]: Da et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^guoSAGAWorkflowAtomicScheduling2026]: Guo et al. 2026
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
