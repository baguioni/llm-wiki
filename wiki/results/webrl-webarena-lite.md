---
type: Result
title: WebRL lifts open models to 42.4-49.1 average success rate on WebArena-Lite
description: WebRL trains Llama3.1 and GLM-4 web agents to 42.4-49.1 average success rate on WebArena-Lite, above GPT-4-Turbo at 17.6.
tags: [web-agents, reinforcement-learning, webarena]
sources:
  - id: qiWebRLTrainingLLM2025
    resource: zotero://select/items/@qiWebRLTrainingLLM2025
    title: "WebRL: Training LLM Web Agents via Self-Evolving Online Curriculum Reinforcement Learning"
  - id: chaeSafeScalableWeb2026
    resource: zotero://select/items/@chaeSafeScalableWeb2026
    title: Safe and Scalable Web Agent Learning via Recreated Websites
---

# WebRL lifts open models to 42.4-49.1 average success rate on WebArena-Lite

## Claim

Online curriculum reinforcement learning (WebRL) raises open LLM web agents above proprietary-model agents on WebArena-Lite.[^qiWebRLTrainingLLM2025]

## Numbers

| Agent | Avg. SR |
|---|---|
| Llama3.1-70B + WebRL | 49.1[^qiWebRLTrainingLLM2025] |
| GLM-4-9B + WebRL | 43.0[^qiWebRLTrainingLLM2025] |
| Llama3.1-8B + WebRL | 42.4[^qiWebRLTrainingLLM2025] |
| AutoWebGLM | 18.2[^qiWebRLTrainingLLM2025] |
| GPT-4-Turbo | 17.6[^qiWebRLTrainingLLM2025] |

## Comparisons

- VeriEnv fine-tuning reaches a WebArena-Lite total of 13.94 with Qwen3-4B.[^chaeSafeScalableWeb2026] The models and training data differ.

## Related

- [WebRL paper](../papers/qiWebRLTrainingLLM2025.md)
- [WebArena-Lite](../benchmarks/webarena-lite.md), [WebArena](../benchmarks/webarena.md)

[^qiWebRLTrainingLLM2025]: Qi et al. 2025
[^chaeSafeScalableWeb2026]: Chae et al. 2026
