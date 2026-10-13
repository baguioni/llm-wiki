---
type: Benchmark
title: Humanity's Last Exam (HLE)
description: Expert-written question benchmark that the wiki's papers use to test deep academic and logical reasoning of web agents and as a tool-heavy serving workload.
tags: [benchmark, web-agents, deep-research, reasoning, agentic-workload]
sources:
  - id: liWebSailorV2BridgingChasm2025
    resource: zotero://select/items/@liWebSailorV2BridgingChasm2025
    title: "WebSailor-V2: Bridging the Chasm to Proprietary Agents via Synthetic Data and Scalable Reinforcement Learning"
  - id: kangThunderAgentSimpleFast2026
    resource: zotero://select/items/@kangThunderAgentSimpleFast2026
    title: "ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System"
---

# Humanity's Last Exam (HLE)

## Setup

- **Task.** WebSailor-V2 describes HLE as a global collaborative effort, with questions from nearly 1,000 subject expert contributors affiliated with over 500 institutions across 50 countries, mostly professors, researchers, and graduate degree holders. It calls HLE a benchmark designed to test deep academic and logical reasoning.[^liWebSailorV2BridgingChasm2025]
- **Metric (WebSailor-V2).** pass@1 with non-zero temperature (temperature 0.85, top-p 0.95), with an LLM as judge for accuracy.[^liWebSailorV2BridgingChasm2025]
- The number of questions and any subset used are not stated in the wiki's papers.

## Results

All scores are from Table 1 of WebSailor-V2. ‡ marks proprietary methods that were evaluated manually through their websites (some are reported in the corresponding papers).[^liWebSailorV2BridgingChasm2025]

| System | Score | Setting / budget | Reported by |
|---|---|---|---|
| WebSailor-V2-30B-A3B (RL) | 30.6 | pass@1, temperature 0.85, top-p 0.95, LLM judge | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| DeepSeek-V3.1-671B‡ | 29.8 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| Kimi-Researcher‡ | 26.9 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| OpenAI DeepResearch‡ | 26.6 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| WebSailor-V2-30B-A3B (SFT) | 23.9 | pass@1, temperature 0.85, top-p 0.95, LLM judge | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| GLM-4.5-355B‡ | 21.2 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| Claude-4-Sonnet | 20.3 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| OpenAI-o3 | 20.2 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| Kimi-K2-Instruct-1T‡ | 18.1 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| WebExplorer-8B | 17.3 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| ASearcher-Web-32B | 12.5 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |
| MiroThinker-32B-DPO-v0.2 | 11.8 | setting of the baseline not stated | WebSailor-V2[^liWebSailorV2BridgingChasm2025] |

The table has no HLE result for Claude-4-Opus, WebSailor-72B, DeepDiver-V2-38B, or DeepDive-32B. The paper explains missing entries by cost constraints.[^liWebSailorV2BridgingChasm2025]

### Used as a workload

| Paper | What is measured | Models / setting | Reported numbers |
|---|---|---|---|
| [ThunderAgent](../methods/thunderagent.md)[^kangThunderAgentSimpleFast2026] | Serving throughput (steps per minute) of the ToolOrchestra routing agent on HLE, as the "general agent serving" workload together with ScienceAgentBench. | ToolOrchestra uses Qwen3-8B at FP16 on one RTX 5090 | No HLE-only number is stated in the text. Across base models and datasets, ThunderAgent reports a 1.48–3.58× throughput speedup over [vLLM](../methods/vllm.md) and 1.17–3.31× over Continuum at high concurrency (e.g., 96 parallel programs). |

ThunderAgent uses HLE as its example of a workload with unpredictable tool latency: serving HLE with ToolOrchestra relies heavily on remote-service tools. Its tool buckets are HLE-search (retrieve evidence, remote service with network latency and rate limits), HLE-enhance-reasoning (model-as-a-tool call, remote service), and HLE-answer (final generation, local LLM inference).[^kangThunderAgentSimpleFast2026] ThunderAgent reports no HLE accuracy.[^kangThunderAgentSimpleFast2026]

## Current SOTA

Among the wiki's papers, the best score is **30.6** for WebSailor-V2-30B-A3B after RL, at pass@1 with temperature 0.85 and top-p 0.95, judged by an LLM.[^liWebSailorV2BridgingChasm2025] The paper claims this as a new state-of-the-art on HLE.[^liWebSailorV2BridgingChasm2025]

## Superseded claims

- **Superseded.** DeepSeek-V3.1 (671B) at 29.8 on HLE, which WebSailor-V2 calls the previous best-performing agentic LLM.[^liWebSailorV2BridgingChasm2025] Superseded by WebSailor-V2-30B-A3B (RL) at 30.6.[^liWebSailorV2BridgingChasm2025] Both numbers come from the same paper, and the margin is 0.8 points.

## Caveats

- **Single source.** Every score on this page comes from one paper's table. No second wiki paper reports HLE accuracy, so no score is cross-checked.[^liWebSailorV2BridgingChasm2025][^kangThunderAgentSimpleFast2026]
- **Mixed evaluation routes.** Rows marked ‡ were evaluated manually through the products' websites or taken from the corresponding papers, while the WebSailor-V2 rows use the authors' own pass@1 protocol.[^liWebSailorV2BridgingChasm2025]
- **Sampling.** WebSailor-V2 reports pass@1 at non-zero temperature, and no variance is given in Table 1.[^liWebSailorV2BridgingChasm2025]
- **Judge.** Accuracy is decided by an LLM judge (see [LLM-as-a-judge](../methods/llm-as-a-judge.md)).[^liWebSailorV2BridgingChasm2025]
- **Agent settings.** WebSailor-V2 runs with a context length of 128k and a maximum of 100 ReAct iterations.[^liWebSailorV2BridgingChasm2025]

## Related

- Benchmarks: [SWE-bench Lite](swe-bench-lite.md) (ThunderAgent's coding-agent workload)
- Methods: [ThunderAgent](../methods/thunderagent.md), [LLM-as-a-judge](../methods/llm-as-a-judge.md), [ReAct](../methods/react.md), [vLLM](../methods/vllm.md)
- Papers: [WebSailor-V2](../papers/liWebSailorV2BridgingChasm2025.md), [ThunderAgent](../papers/kangThunderAgentSimpleFast2026.md)

[^liWebSailorV2BridgingChasm2025]: Li et al. 2025
[^kangThunderAgentSimpleFast2026]: Kang et al. 2026
