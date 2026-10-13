---
type: Benchmark
title: Terminal-Bench
description: Benchmark of realistic, human-verified command-line tasks, used in this wiki as an out-of-domain check for RL-trained coding agents and as an agentic serving workload.
tags: [benchmark, coding-agents, command-line, agentic-workload]
sources:
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback For Software Engineering Agents"
  - id: yuanKAIROSStatefulContextAware2026
    resource: zotero://select/items/@yuanKAIROSStatefulContextAware2026
    title: "KAIROS: Stateful, Context-Aware Power-Efficient Agentic Inference Serving"
---

# Terminal-Bench

## Setup

- **Task.** KAIROS describes Terminal-Bench 2.0 as a benchmark of realistic, human-verified command-line tasks for evaluating an agent's ability to autonomously complete complex, long-horizon tasks.[^yuanKAIROSStatefulContextAware2026]
- **Versions.** KAIROS names version 2.0.[^yuanKAIROSStatefulContextAware2026] SWE-RM writes "Terminal Bench" with no version.[^shumSWERMExecutionfreeFeedback2025]
- **Metric and protocol.** Neither paper states the metric or the evaluation protocol. SWE-RM prints one number per method in a table of "performance after RL" without a unit.[^shumSWERMExecutionfreeFeedback2025]

## Results

SWE-RM trains a Qwen3-30B-A3B policy (with SFT warm-up) with RL under different feedback signals and then evaluates it on tasks other than [SWE-bench Verified](swe-bench-verified.md), including Terminal Bench (Table 5).[^shumSWERMExecutionfreeFeedback2025]

| System | Score | Setting / budget | Reported by |
|---|---|---|---|
| RL policy, hybrid feedback (execution-based + SWE-RM) | 32.5 | budget not stated | SWE-RM (Table 5)[^shumSWERMExecutionfreeFeedback2025] |
| RL policy, execution-free feedback only | 31.3 | budget not stated | SWE-RM (Table 5)[^shumSWERMExecutionfreeFeedback2025] |
| RL policy, execution-based feedback only | 30.0 | budget not stated | SWE-RM (Table 5)[^shumSWERMExecutionfreeFeedback2025] |
| RL policy, feedback from a poorly calibrated reward model | 15.0 | budget not stated | SWE-RM (Table 5)[^shumSWERMExecutionfreeFeedback2025] |

The paper's Table 8 gives the training setting of the poorly calibrated reward model used in its RL figure: 5k samples, a 1:2 positive-to-negative ratio, off-policy data, from SWE-Rebench, with a 256k context length.[^shumSWERMExecutionfreeFeedback2025]

### Used as a workload

| Paper | What is measured | Models / setting | Reported numbers |
|---|---|---|---|
| KAIROS[^yuanKAIROSStatefulContextAware2026] | GPU power and per-agent throughput of an agentic serving system. Terminal-Bench 2.0 is one of three datasets, with SWE-bench Verified and DABStep. The agent scaffolds are mini-swe-agent and Terminus-2, which the paper describes as Harbor's autonomous reference agent. | [vLLM](../methods/vllm.md) on NVIDIA H100 GPUs | The text gives no result that is specific to Terminal-Bench. The power results it states name SWE-Bench Verified or DABStep as the dataset. |

## Current SOTA

Among the wiki's papers, the best score is **32.5** for the SWE-RM RL policy trained with hybrid feedback.[^shumSWERMExecutionfreeFeedback2025] SWE-RM is the only wiki paper that reports a task score, and it makes no state-of-the-art claim for this benchmark. It uses the benchmark to compare its own feedback variants.[^shumSWERMExecutionfreeFeedback2025]

## Caveats

- **Version mismatch.** The SWE-RM scores cannot be assigned to Terminal-Bench 2.0, because SWE-RM gives no version.[^shumSWERMExecutionfreeFeedback2025][^yuanKAIROSStatefulContextAware2026]
- **No protocol.** SWE-RM does not state the agent scaffold, number of runs, or sampling settings for this benchmark. Its stated single-trajectory greedy protocol is for SWE-bench Verified.[^shumSWERMExecutionfreeFeedback2025]
- **Policy starting point.** The RL policy is warmed up with SFT on in-house collected agentic trajectories.[^shumSWERMExecutionfreeFeedback2025]
- **Out-of-domain use.** The policy was trained with RL on SWE issue-resolution data, and Terminal Bench is in the paper's suite for assessing generalization beyond that domain.[^shumSWERMExecutionfreeFeedback2025]

## Related

- Benchmarks: [SWE-bench Verified](swe-bench-verified.md), [SWE-bench](swe-bench.md)
- Methods: [Execution-free verifier](../methods/execution-free-verifier.md), [vLLM](../methods/vllm.md)
- Papers: [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md), [KAIROS](../papers/yuanKAIROSStatefulContextAware2026.md)

[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
[^yuanKAIROSStatefulContextAware2026]: Yuan et al. 2026
