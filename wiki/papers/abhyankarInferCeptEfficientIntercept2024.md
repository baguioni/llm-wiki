---
type: Paper
title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
description: LLM inference framework that handles tool, model, and human interceptions by choosing preserve, discard, or swap per request to minimize GPU memory waste.
tags: [llm-serving, augmented-llm, kv-cache, scheduling, ai899]
collections: [ai899]
authors: [Reyna Abhyankar, Zijian He, Vikranth Srivatsa, Hao Zhang, Yiying Zhang]
year: 2024
venue: ICML 2024 (PMLR 235)
doi: 10.48550/arXiv.2402.01869
arxiv: "2402.01869"
arxiv_version: 2402.01869v2
code: https://github.com/WukLab/InferCept
sources:
  - id: abhyankarInferCeptEfficientIntercept2024
    resource: zotero://select/items/@abhyankarInferCeptEfficientIntercept2024
    title: "InferCept: Efficient Intercept Support for Augmented Large Language Model Inference"
---

# InferCept: Efficient Intercept Support for Augmented Large Language Model Inference

Text source: arXiv HTML, version `2402.01869v2`.

## Summary

Augmented LLMs call tools, other models, or wait for humans during decoding. Each such call *intercepts* decoding: generation pauses and resumes when the call returns.[^abhyankarInferCeptEfficientIntercept2024] Existing inference systems treat an interception as the end of the request, discard its context, and start a new request when the call returns. This recomputes the KV cache of all earlier tokens, and the recomputation accounts for 37-40% of total model forwarding time.[^abhyankarInferCeptEfficientIntercept2024]

InferCept is an inference framework built on vLLM whose core idea, *min-waste interception*, is to minimize the GPU memory waste caused by interceptions so that the same GPU resources serve more requests.[^abhyankarInferCeptEfficientIntercept2024] The paper reports that InferCept sustains 1.6×-2× higher request arrival rates and achieves 1.3×-12× lower normalized latency than state-of-the-art inference systems.[^abhyankarInferCeptEfficientIntercept2024]

## Contributions

- A study of six augmentation types (arithmetic, QA, virtual environment, chatbot, image generation, text-to-speech) that measures interception time, number of interceptions, and context length.[^abhyankarInferCeptEfficientIntercept2024]
- Three waste-calculation equations that quantify the GPU memory waste of the Discard, Preserve, and Swap strategies.[^abhyankarInferCeptEfficientIntercept2024]
- Improved mechanisms: swap pipelining and chunking for Swap, and chunked recomputation for Discard.[^abhyankarInferCeptEfficientIntercept2024]
- A scheduler that chooses the interception and resumption strategy within and across requests to minimize overall GPU memory waste while ensuring fairness.[^abhyankarInferCeptEfficientIntercept2024]

## Method

### Three baseline strategies and their waste

Notation: request $i$ at interception $j$ has context $C_i^j$ tokens, each token's KV cache occupies $M$ memory, $T_{fwd}$ maps the number of scheduled tokens in a batch to iteration time, $T_{swap}$ maps the number of swapped tokens to swap latency, and $T_{INT}^j$ is the interception duration.[^abhyankarInferCeptEfficientIntercept2024]

| Strategy | What it does | Waste | Measured cost on the mixed workload |
|---|---|---|---|
| Discard | End the request, drop context, recompute on resume. | $T_{fwd}(C_i^j)\times C_i^j\times M + T_{fwd}(C_i^j)\times C_{other}\times M$ (Eq. 1) | GPU resource wastage (GB\*min) of 27%; 37-40% of total model forwarding time spent on recomputation |
| Preserve | Keep context in GPU memory during the interception. | $T_{INT}^j\times C_i\times M$ (Eq. 2) | Nearly half of the GPU memory is occupied by interrupted requests more than 60% of the time |
| Swap | Move context to CPU memory and back. | $2\times T_{swap}(C_i^j)\times C_{batch}\times M$ (Eq. 3) | Wastes 26% GPU resources; over 25% of total workload time spent waiting for swapping |

All rows: [^abhyankarInferCeptEfficientIntercept2024]

*ImprovedDiscard* is Discard that re-inserts an intercepted request into the waiting queue with its original arrival time, so that resumed requests are not starved under FCFS.[^abhyankarInferCeptEfficientIntercept2024]

### InferCept mechanisms

- **Swap pipelining.** Each model layer's swapping is one pipeline stage. Kernel launching, data movement, and foreground model forwarding are pipelined and run in the background.[^abhyankarInferCeptEfficientIntercept2024]
- **Swap chunking.** Swap-out and swap-in are split across iterations. At iteration $i$ with batch size $B_i$, the *swap limit* $N_i$ is set from $T_{swap}(N_i) = T_{fwd}(B_i)$. $N_i$ is the number of tokens that can be swapped for free, hidden behind model forwarding.[^abhyankarInferCeptEfficientIntercept2024]
- **Recomputation chunking.** The *GPU saturation point* $S$ is the number of query tokens that all GPU cores can process in parallel, obtained from offline profiling. The recomputation chunk size is $S$ minus the running group size. The waste becomes $\frac{T_{fwd}(C_i^j)\times C_i^j\times M}{2} + n\times T_{fwd}(\frac{C_i^j}{n})\times C_{other}\times M$ (Eq. 4), where $n$ is the number of iterations needed to finish recomputing.[^abhyankarInferCeptEfficientIntercept2024]
- **Scheduling intercepted requests.** Per request, waste is $\min(\text{WastePreserve}, \text{WasteChunkD})$ (Eq. 5). Intercepted requests are sorted by waste in descending order and swapped out in that order until the swap-out budget runs out. The remaining requests are preserved or discarded according to Eq. 5.[^abhyankarInferCeptEfficientIntercept2024]
- **Scheduling resumed requests.** Three queues (running, swap, waiting), each sorted by original arrival time. Requests are taken from the waiting queue in FCFS order until the GPU saturation point is reached, and from the swap queue in FCFS order until the swap-in budget is reached.[^abhyankarInferCeptEfficientIntercept2024]
- **Interception duration estimation.** For durations that are highly variable or not profiled offline, $\hat{T}_{INT} = t_{now} - t_{call}$. With this estimate InferCept achieves 93% of the performance of an oracle with exact durations on the mixed workload.[^abhyankarInferCeptEfficientIntercept2024]

## Experiments & Results

### Setup

- Baselines: vLLM (unmodified, performs Discard), ImprovedDiscard, Preserve, Swap.[^abhyankarInferCeptEfficientIntercept2024]
- Models and hardware: GPT-J 6B on one NVIDIA A100; Vicuna 13B on one A100 and on two A100s with tensor parallelism; Llama3 70B on four A100s with tensor parallelism.[^abhyankarInferCeptEfficientIntercept2024]
- Workload: a mixed dataset that uniformly samples requests from the six augmentations.[^abhyankarInferCeptEfficientIntercept2024]
- Metrics: normalized latency (median of each request's end-to-end latency divided by its output length, with intercepted time removed), throughput (completed requests per second), and time-to-first-token (TTFT).[^abhyankarInferCeptEfficientIntercept2024]

### Interception properties (Table 1)

Each cell is (mean, variance). `*` estimated behavior. `†` partially estimated.[^abhyankarInferCeptEfficientIntercept2024]

| Type | Int Time (sec) | Num Interceptions | Context Len | Dataset |
|---|---|---|---|---|
| Math | (9e-5, 6e-5) | (3.75, 1.3) | (1422, 738) | [GSM8K-XL](../datasets/gsm8k-xl.md) |
| QA | (0.69, 0.17) | (2.52, 1.73) | (1846, 428) | Multihop QA Wikipedia ([HotpotQA](../datasets/hotpotqa.md)) |
| VE | (0.09, 0.014) | (28.18, 15.2) | (2185, 115) | [ALFWorld](../datasets/alfworld.md) |
| Chatbot | (28.6, 15.6)* | (4.45, 1.96) | (753, 703) | [ShareGPT](../datasets/sharegpt.md) |
| Image | (20.03, 7.8)† | (6.91, 3.93)* | (1247, 792) | ChatGPT-generated prompts, Stable Diffusion |
| TTS | (17.24, 7.6)† | (6.91, 3.93)* | (1251, 792) | ChatGPT-generated prompts, Bark |

### End-to-end performance vs vLLM (mixed workload)

| Model / setup | Higher request arrival rate at same normalized latency | Normalized latency at same request rate | TTFT |
|---|---|---|---|
| GPT-J 6B, 1 GPU | up to 1.6× | 1.9×-5.7× lower | 1.7× higher request arrival rate with the smallest TTFT |
| Vicuna 13B, 1 GPU | up to 1.25× without a noticeable increase in normalized latency | not stated | 3.1× higher load with the smallest TTFT |
| Vicuna 13B, 2 GPUs | up to 1.8× | 1.6×-10× improvement | not stated |
| Llama3 70B, 4 GPUs | 2× | 1.3×-12× lower at the same RPS | 2.4× higher load with the same TTFT |

All rows: [^abhyankarInferCeptEfficientIntercept2024]

- On the 6B model, InferCept eliminates over 60% of GPU waste caused by recomputation and 96% of GPU waste for swapping, compared to ImprovedDiscard and Swap.[^abhyankarInferCeptEfficientIntercept2024]
- Preserve is the best baseline for normalized latency and throughput on the small models.[^abhyankarInferCeptEfficientIntercept2024]
- Single-augment workloads: InferCept outperforms vLLM by up to 2.3× (QA) and 1.9× (Chatbot) on normalized latency.[^abhyankarInferCeptEfficientIntercept2024]

### Technique breakdown (6B model, mixed workload, 2 requests per second)

Each step adds one technique to the previous step. Values are the reduction in normalized latency.[^abhyankarInferCeptEfficientIntercept2024]

| Step | Added technique | Improvement |
|---|---|---|
| 1 | Original arrival time (ImprovedDiscard) over vanilla vLLM | 24.5% |
| 2 | Recomputation chunking | 7.8% more |
| 3 | Budgeted swapping | 12.7% added |
| 4 | Preserve with a short/long heuristic | 46.1% |
| 5 | Min-waste adaptive schedule (full InferCept) | additional 46.4% |

Full InferCept has only 0.69% GPU memory waste.[^abhyankarInferCeptEfficientIntercept2024] For the single Chatbot workload, chunking and pipelining for recomputation and swapping contribute 54% of total speedup.[^abhyankarInferCeptEfficientIntercept2024]

## Limitations

- The paper leaves the comparison with alternative request scheduling policies, such as the multi-level feedback queue in FastServe, to future work.[^abhyankarInferCeptEfficientIntercept2024]
- Human response time for Chatbot, Image, and TTS interceptions is estimated (scanning time plus typing time), not measured.[^abhyankarInferCeptEfficientIntercept2024]
- Gains are smaller for the 13B model on a single GPU: larger weights leave less memory for the KV cache, and normal forwarding time dominates normalized latency.[^abhyankarInferCeptEfficientIntercept2024]
- The paper has no dedicated limitations section.

## Related

- Methods: [KV cache swapping](../methods/kv-cache-swapping.md), [Iteration-level scheduling](../methods/iteration-level-scheduling.md), [PagedAttention](../methods/paged-attention.md), [Chunked prefill](../methods/chunked-prefill.md)
- Systems compared or built on: [vLLM](../methods/vllm.md)
- Datasets: [GSM8K-XL](../datasets/gsm8k-xl.md), [HotpotQA](../datasets/hotpotqa.md), [ALFWorld](../datasets/alfworld.md), [ShareGPT](../datasets/sharegpt.md)
- Papers in this wiki cited by this paper: [SGLang](zhengSGLangEfficientExecution2024.md)

## Open questions and results

- [Recomputation share of forwarding time](../results/recomputation-share-of-forwarding-time.md)
- [Does offloading the KV cache to CPU memory help agentic workloads?](../questions/kv-cache-offloading-for-agent-workloads.md)

[^abhyankarInferCeptEfficientIntercept2024]: Abhyankar et al. 2024
