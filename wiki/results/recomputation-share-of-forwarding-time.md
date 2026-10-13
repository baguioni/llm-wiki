---
type: Result
title: Discarding context at interceptions costs 37-40% of model forwarding time
description: InferCept measures that recomputing discarded context takes 37-40% of total model forwarding time on a mixed augmented-LLM workload.
tags: [kv-cache, llm-serving, augmented-llm]
sources:
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
---

# Discarding context at interceptions costs 37-40% of model forwarding time

## Claim

When an inference system discards a request's context at each tool call or human turn, 37-40% of the total model forwarding time is spent on recomputation.[^abhyankarInferCeptEfficientIntercept2024]

## Conditions

- Workload: a mixed workload of six augmentation types (math, QA, virtual environment, chatbot, image generation, text-to-speech).[^abhyankarInferCeptEfficientIntercept2024]
- Strategy measured: Discard, as performed by unmodified vLLM.[^abhyankarInferCeptEfficientIntercept2024]

## Numbers

| Strategy | Cost |
|---|---|
| Discard | GPU resource wastage (GB\*min) of 27%; 37-40% of forwarding time on recomputation[^abhyankarInferCeptEfficientIntercept2024] |
| Swap | wastes 26% GPU resources[^abhyankarInferCeptEfficientIntercept2024] |
| InferCept | 0.69% GPU memory waste[^abhyankarInferCeptEfficientIntercept2024] |

## Related

- [InferCept paper](../papers/abhyankarInferCeptEfficientIntercept2024.md)
- [KV cache](../methods/kv-cache.md), [KV cache swapping](../methods/kv-cache-swapping.md), [vLLM](../methods/vllm.md)
- [Does offloading the KV cache to CPU memory help agentic workloads?](../questions/kv-cache-offloading-for-agent-workloads.md)

[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
