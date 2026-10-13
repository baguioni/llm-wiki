---
type: Benchmark
title: Berkeley Function Calling Leaderboard (BFCL)
description: Function-calling benchmark for LLMs, reported in the wiki as BFCL v2 and BFCLv3, and also used as a ReAct agent workload for serving systems.
tags: [function-calling, tool-use, benchmark, llm-agents, evaluation]
sources:
  - id: wangAgentWorldModel2026
    resource: zotero://select/items/@wangAgentWorldModel2026
    title: "Agent World Model: Infinity Synthetic Environments for Agentic Reinforcement Learning"
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: luoAutellixEfficientServing
    resource: zotero://select/items/@luoAutellixEfficientServing
    title: "Autellix: An Efficient Serving Engine for LLM Agents as General Programs"
---

# Berkeley Function Calling Leaderboard (BFCL)

## Setup

- **BFCLv3.** A benchmark for function-calling ability evaluation that covers single-turn, multi-turn (long-context), synthetic tools, real-world tools, and hallucination tests. This gives four evaluation categories: non-live, live, multi-turn, and hallucination.[^wangAgentWorldModel2026] Luo et al. describe BFCLv3 as evaluating LLMs on multi-turn, multi-step tool-usage tasks.[^luoAutellixEfficientServing]
- **BFCL v2.** Muralidharan et al. use the Berkeley Function Calling Leaderboard for function calling and report one average score on BFCL v2. They do not describe its categories.[^muralidharanCompactLanguageModels2024]
- **Protocol in Wang et al.** Multi-turn trajectories are aggregated into the expected single-turn or parallel function call format, skipping list\_tools meta-calls. The context window is extended to 131,072 tokens via RoPE scaling for all evaluations, because some BFCLv3 multi-turn tasks require long interaction histories.[^wangAgentWorldModel2026]

## Results

### BFCLv3 (Wang et al. 2026, Table 4)

Base agents are Qwen3 thinking models at 4B, 8B, and 14B scales. Category columns are in the order Non-Live, Live, Multi-Turn, Hall. (hallucination).[^wangAgentWorldModel2026]

| System | Overall | Non-Live, Live, Multi-Turn, Hall. | Setting / budget | Reported by |
|---|---|---|---|---|
| AWM | 70.18 | 81.46, 77.20, 51.88, 78.37 | Qwen3 14B, trained with RL on AWM environments | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| Simulator | 67.68 | 77.23, 73.43, 52.38, 76.91 | Qwen3 14B | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| AWM | 65.94 | 80.44, 72.39, 45.00, 70.80 | Qwen3 8B | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| AWM | 64.50 | 78.60, 76.91, 37.99, 73.70 | Qwen3 4B | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| Base | 61.25 | 69.48, 67.28, 47.00, 77.94 | Qwen3 14B, untrained | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| Simulator | 55.52 | 66.10, 62.69, 37.75, 75.48 | Qwen3 4B | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| Base | 54.92 | 61.44, 63.95, 39.38, 73.93 | Qwen3 4B, untrained | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| EnvScaler | 54.06 | 60.31, 64.25, 37.63, 85.25 | Qwen3 4B | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| Base | 53.83 | 59.58, 58.03, 43.88, 76.42 | Qwen3 8B, untrained | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| Simulator | 52.53 | 56.35, 59.36, 41.88, 74.06 | Qwen3 8B | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |
| EnvScaler | 36.83 | 33.67, 31.83, 45.00, 90.30 | Qwen3 8B | [Wang et al. 2026](../papers/wangAgentWorldModel2026.md) |

All rows: [^wangAgentWorldModel2026]

- EnvScaler did not release a 14B model.[^wangAgentWorldModel2026]
- EnvScaler regresses on BFCLv3 (-8.93) on average, while AWM improves over Base.[^wangAgentWorldModel2026]
- By number of tool calls, with the 8B agent: Simple 53.6 for Base and 80.3 for AWM, Medium 60.0 and 75.3, Hard 43.9 and 45.0.[^wangAgentWorldModel2026]
- Ablation rows (verification design, history limit) with BFCLv3 overall scores are on the [Agent World Model paper page](../papers/wangAgentWorldModel2026.md).

### BFCL v2 (Muralidharan et al. 2024, Table 9)

| System | Avg. | Setting / budget | Reported by |
|---|---|---|---|
| Minitron 4B-instruct | 53.09 | BFCL v2 | [Muralidharan et al. 2024](../papers/muralidharanCompactLanguageModels2024.md) |
| Llama-3-8B-instruct | 50.51 | BFCL v2 | [Muralidharan et al. 2024](../papers/muralidharanCompactLanguageModels2024.md) |
| Gemma-2B-IT | 41.63 | BFCL v2 | [Muralidharan et al. 2024](../papers/muralidharanCompactLanguageModels2024.md) |

All rows: [^muralidharanCompactLanguageModels2024]

On function calling, Minitron 4B-instruct outperforms Gemma-2B-IT and even Llama-3-8B-instruct.[^muralidharanCompactLanguageModels2024]

### Used as a workload

This paper replays BFCL programs to measure a serving engine. It does not report function-calling accuracy.

| Paper | What is measured | Setting | Reported numbers |
|---|---|---|---|
| [Autellix](../papers/luoAutellixEfficientServing.md) | Workload statistics | BFCLv3 run as a [ReAct](../methods/react.md) agent | A mean of 10.75 and a maximum of 70 LLM calls per program. Prefill-heavy: 735.06 tokens per call on average. Decodes average 34.14 tokens[^luoAutellixEfficientServing] |
| [Autellix](../papers/luoAutellixEfficientServing.md) | Throughput at the same token latency | Single-threaded workloads (ShareGPT and BFCL), against vLLM, vLLM-opt, and MLFQ | Up to 8× the throughput of vLLM, twice that of vLLM-opt, and a 1.5× improvement over MLFQ under heavy load[^luoAutellixEfficientServing] |

The Autellix throughput factors are stated for [ShareGPT](../datasets/sharegpt.md) and BFCL together, and the underlying curves are in a figure.[^luoAutellixEfficientServing] The baseline engine is [vLLM](../methods/vllm.md).[^luoAutellixEfficientServing]

## Current SOTA

- **BFCLv3.** The best overall score among the wiki's papers is 70.18 for the Qwen3 14B agent trained with AWM.[^wangAgentWorldModel2026]
- **BFCL v2.** The best average among the wiki's papers is 53.09 for Minitron 4B-instruct.[^muralidharanCompactLanguageModels2024]

The two versions are tracked separately. No claim is superseded, because no later paper in the wiki reports a higher score on the same version.

## Caveats

- BFCL v2 and BFCLv3 scores are not comparable. The papers report them on different versions, with different models.[^muralidharanCompactLanguageModels2024][^wangAgentWorldModel2026]
- All BFCLv3 rows come from one paper and one model family (Qwen3). They are not a ranking of the public leaderboard.[^wangAgentWorldModel2026]
- AWM is modestly weaker on the hallucination category. The authors attribute this to the format correctness reward, which always encourages tool use and penalizes refusals. AWM omits refusal scenarios, while BFCLv3 stresses hallucination resistance.[^wangAgentWorldModel2026]
- BFCLv3 is an out-of-distribution benchmark for the AWM agents.[^wangAgentWorldModel2026]
- The Autellix rows are latency and throughput measurements and say nothing about accuracy.[^luoAutellixEfficientServing]

## Related

- Methods: [ReAct](../methods/react.md), [GRPO](../methods/grpo.md), [vLLM](../methods/vllm.md)
- Datasets used alongside it as workloads in Autellix: [ShareGPT](../datasets/sharegpt.md), [HotpotQA](../datasets/hotpotqa.md)
- Papers: [Agent World Model](../papers/wangAgentWorldModel2026.md), [Minitron](../papers/muralidharanCompactLanguageModels2024.md), [Autellix](../papers/luoAutellixEfficientServing.md)

[^wangAgentWorldModel2026]: Wang et al. 2026
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^luoAutellixEfficientServing]: Luo et al.
