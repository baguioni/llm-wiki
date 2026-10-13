---
type: Paper
title: "Parrot: Efficient Serving of LLM-based Applications with Semantic Variable"
description: LLM service system that exposes application-level knowledge through the Semantic Variable abstraction so the service can analyze request dependencies and shared prompts and optimize end-to-end application performance.
tags: [llm-serving, llm-applications, scheduling, prompt-prefix-sharing, kv-cache, multi-agent, ai899]
collections: ["ai899"]
authors: [Chaofan Lin, Zhenhua Han, Chengruidong Zhang, Yuqing Yang, Fan Yang, Chen Chen, Lili Qiu]
arxiv: "2405.19888"
arxiv_version: 2405.19888v1
sources:
  - id: linParrotEfficientServing2024
    resource: zotero://select/items/@linParrotEfficientServing2024
    title: "Parrot: Efficient Serving of LLM-Based Applications with Semantic Variable"
---

# Parrot: Efficient Serving of LLM-based Applications with Semantic Variable

Text source: arXiv HTML, version `2405.19888v1`.

## Summary

LLM-based applications (AI agents, co-pilots) use multiple LLM requests in complex workflows to complete one task, but public LLM services expose a request-level API and lose application-level information, so they optimize individual requests blindly.[^linParrotEfficientServing2024] [Parrot](../methods/parrot.md) is an LLM service system that targets the end-to-end experience of LLM applications. Its abstraction, the [Semantic Variable](../methods/semantic-variable.md), annotates an input/output variable in the prompt of a request and forms the data pipeline that connects multiple requests. The service can then run conventional data flow analysis to uncover the correlation across requests.[^linParrotEfficientServing2024]

The paper reports up to 11.7× speedup or 12× higher throughput compared with the state-of-the-art solutions.[^linParrotEfficientServing2024]

## Contributions

- Identification of three problems of request-centric LLM services: excessive overhead of consecutive requests, misaligned scheduling objectives, and redundant computations.[^linParrotEfficientServing2024]
- The Semantic Variable abstraction and the primitives for inter-request analysis (DAG-based and prompt-structure-based).[^linParrotEfficientServing2024]
- Four optimizations built on it: serving dependent requests, performance objective deduction, sharing prompt prefix (with a new GPU attention kernel), and application-centric scheduling.[^linParrotEfficientServing2024]
- A universal engine abstraction (`Fill`, `Generate`, `FreeContext`) that describes the minimal capability an LLM engine needs to be integrated.[^linParrotEfficientServing2024]

## Method

### Motivation measurements

- In a production chain-style application (prompt lengths from 150 to 4000 tokens, output length around 50 tokens), a significant portion of LLM API call latency originates outside the LLM engine: 30∼50% on average and over 70% in the worst cases.[^linParrotEfficientServing2024]
- For a map-reduce summary, maximizing throughput in the map stage and minimizing request latency in the reduce stage reduces end-to-end latency by 2.4×.[^linParrotEfficientServing2024]

Statistics of LLM calls (Table 1). A paragraph counts as repeated if it appears in at least two LLM requests.[^linParrotEfficientServing2024]

| LLM-based App. | # Calls | Tokens | Repeated (%) |
|---|---|---|---|
| Long Doc. Analytics | 2∼40 | 3.5k∼80k | 3% |
| Chat Search | 2∼10 | 5k | 94% |
| [MetaGPT](../methods/metagpt.md) | 14 | 17k | 72% |
| AutoGen | 17 | 57k | 99% |

### Semantic Variable and API

- An LLM request is treated as a *semantic function* implemented in natural language and executed by LLMs. A Semantic Variable is an input or output variable of a semantic function, referred to as a placeholder in the prompt.[^linParrotEfficientServing2024]
- Unlike orchestration frameworks such as [LangChain](../methods/langchain.md), which render placeholders with real data before submission, Parrot preserves the prompt structure for analysis on the service side.[^linParrotEfficientServing2024]
- A completion request is split into a `submit` operation and a `get` operation. Calling a SemanticFunction triggers `submit` and returns futures of the output Semantic Variables. `get` fetches a value on demand and carries a performance criterion: end-to-end latency or throughput.[^linParrotEfficientServing2024]

### Inter-request analysis primitives

- **DAG-based.** Parrot keeps a DAG per registered session, whose nodes are requests or Semantic Variables. `GetProducer` and `GetConsumers` recover request dependencies, and `GetPerfObj` reads the annotated criteria of final outputs.[^linParrotEfficientServing2024]
- **Prompt-structure-based.** `PrefixHash` extracts hash values of a request at the positions split by Semantic Variables, for detecting commonality across requests.[^linParrotEfficientServing2024]

### Optimizations

- **Serving dependent requests.** A graph-based executor polls and sends a request to an engine once its producer requests are all finished. Values move through a message queue allocated per Semantic Variable, which avoids client round trips. String transformations on values are supported, covering most output parsing methods of LangChain.[^linParrotEfficientServing2024]
- **Performance objective deduction.** A throughput annotation marks all requests that generate the variable, directly or indirectly, as throughput-preferred. For latency, Parrot walks the DAG in reverse topological order; requests that directly produce latency-critical variables and their immediate predecessors are labeled latency-sensitive, and parallel requests at the same stage form a *task group* whose total latency the scheduler minimizes.[^linParrotEfficientServing2024]
- **Sharing prompt prefix.** A key-value store maps each hashed prefix of tokens to a list of requests, so the scheduler checks sharing opportunities online for static and dynamically generated prompts. The engine uses vLLM's paged memory management to share the [KV cache](../methods/kv-cache.md) of the prefix, plus a new attention kernel.[^linParrotEfficientServing2024]
- **Attention kernel.** Built with OpenAI Triton and CUDA, it combines [PagedAttention](../methods/paged-attention.md) and [FlashAttention](../methods/flash-attention.md). It loads KV cache tiles for the shared prefix to shared memory only once, computes interim attention metrics for the shared prefix, then processes the new tokens' partial attention and merges the two.[^linParrotEfficientServing2024]
- **Application-centric scheduling (Algorithm 1).** Requests are sorted in topological order. A request in a task group is placed with its group; otherwise with queued requests that share a prefix; otherwise on an engine that holds a context with the shared prefix; otherwise independently. The two principles are to group requests with similar performance requirements and to maximize sharing. Example from the paper: scheduling a latency-sensitive request on an engine that can run up to 64,000 tokens of throughput-driven requests reduces its capacity to 2,000.[^linParrotEfficientServing2024]

### Implementation

- About 14,000 lines of Python in total: front-end 1,600, manager 3,200, LLM engine 5,400 lines of Python and 1,600 lines of CUDA.[^linParrotEfficientServing2024]
- The engine is built on kernels from [vLLM](../methods/vllm.md), xFormers, and the authors' own, and supports paged memory management and [continuous batching](../methods/continuous-batching.md).[^linParrotEfficientServing2024]
- Engine abstraction: `Fill(token_ids, context_id, parent_context_id)`, `Generate(sampling_configs, context_id, parent_context_id)`, `FreeContext(context_id)`. Contexts are created and forked by setting `context_id` and `parent_context_id`.[^linParrotEfficientServing2024]

## Experiments & Results

### Setup

- Single-GPU testbed: 24-core AMD-EPYC-7V13 CPUs with one NVIDIA A100 (80GB). Multi-GPU testbed: 64-core EPYC AMD CPU with four NVIDIA A6000 (48GB). Each LLM engine uses one GPU and runs a LLaMA 13B or LLaMA 7B model.[^linParrotEfficientServing2024]
- Workloads: chain and map-reduce summarization on the [Arxiv dataset](../datasets/arxiv-march.md); Bing Copilot and GPTs prompts with synthesized user queries; a multi-agent programming application built with MetaGPT; chat workloads derived from [ShareGPT](../datasets/sharegpt.md).[^linParrotEfficientServing2024]
- A random delay of 200∼300 ms is added to LLM requests to emulate network overhead over the Internet.[^linParrotEfficientServing2024]
- Baseline: applications built with LangChain that call OpenAI-style chat completion APIs served by [FastChat](../methods/fastchat.md), with HuggingFace Transformers or vLLM as the engine. Baselines treat all requests as independent and latency-sensitive. FastChat assigns a request to the engine with the smallest current queue.[^linParrotEfficientServing2024]
- vLLM's latency per output token rises notably when the batch capacity goes beyond 6144. The evaluation uses a setting where an engine keeps generation latency under 40 ms/s for latency-sensitive requests.[^linParrotEfficientServing2024]

### Headline results

| Workload | Setup | Result for Parrot | Compared against |
|---|---|---|---|
| Chain summary, varying output length and chunk size | one engine (A100, LLaMA 13B) | E2E latency reduced by as much as 1.38× and 1.88× | vLLM and HuggingFace baselines |
| Chain summary, variable chunk sizes and fixed output length | one engine (A100, LLaMA 13B) | 1.2× and 1.66× speedup | vLLM and HuggingFace |
| Chain summary with background requests | one engine (A100, LLaMA 13B) | E2E latency reduced by a factor of 2.38× | vLLM baseline |
| Multiple chain-summary applications submitted concurrently | one engine (A100, LLaMA 13B) | average E2E latency reduced by 1.68× without slowing down any application | vLLM baseline |
| Map-reduce summary | one engine (A100, LLaMA 13B) | 2.37× acceleration | baseline limited to a token capacity of 4096 tokens |
| Bing Copilot, batch sizes 8 and 16 | A100, LLaMA 7B | 1.8×∼2.4× speedup | baseline without sharing prompt |
| Bing Copilot | A100, LLaMA 7B | 1.1×∼1.7× speedup | vLLM with paged attention sharing a static prefix |
| Bing Copilot, latency per output token | A100, LLaMA 7B | 1.58× and 1.84× speedup; 40 ms per-output-token latency at a batch size of 32 | vLLM using paged attention |
| Multiple GPTs applications | four A6000, four engines (LLaMA 7B) | sustains 12× higher request rates | baseline without sharing |
| Multiple GPTs applications, affinity scheduling turned off | four A6000, four engines (LLaMA 7B) | only 3× higher request rates | baseline without sharing |
| Multiple GPTs applications, Parrot's attention kernel | four A6000, four engines (LLaMA 7B) | 2.4× higher rate | Parrot using vLLM's PagedAttention |
| Multi-agent programming (MetaGPT) | one A100, LLaMA 13B | speedup of up to 11.7× | latency-centric baseline |
| Multi-agent programming (MetaGPT) | one A100, LLaMA 13B | faster by up to 2.45× | throughput-centric baseline |

All rows: [^linParrotEfficientServing2024]

Details:

- Chain summary uses ten randomly picked long documents from the Arxiv-March dataset, each over 20,000 tokens, and reports mean end-to-end latency. The gain comes mainly from reduced network latency and shrinks as output length increases.[^linParrotEfficientServing2024]
- Bing Copilot: 64 synthesized requests, system prompt of about 6000 tokens, output lengths from 180 to 800 tokens. Only the final request that generates the response is evaluated. Increasing the batch size beyond 16 in the no-sharing baseline leads to out-of-memory.[^linParrotEfficientServing2024]
- Multi-agent: prompt structure analysis contributes a 2.35× acceleration over the throughput-centric baseline. The specialized GPU kernel gives a further 1.2× speedup when there are 16 files, compared to vLLM's PagedAttention. vLLM's static prefix sharing does not work in this dynamic scenario, and Parrot without sharing would hit the GPU memory ceiling.[^linParrotEfficientServing2024]

### Mixed workloads (four A6000, four LLaMA 7B engines)

Chat requests at a rate of 1 req/s mixed with map-reduce data analytics tasks.[^linParrotEfficientServing2024]

| Metric | vs latency-centric baseline | vs throughput-centric baseline |
|---|---|---|
| Chat normalized latency (request latency per number of output tokens) | 5.5× improvement | 1.23× improvement |
| Chat token generation speed | on par | 1.72× |
| Map-reduce application | 3.7× speedup | 1.05× more efficient |

All rows: [^linParrotEfficientServing2024]

## Limitations

- Parrot supports only cloud-side orchestration of LLM requests without dynamic control flow or native functions (for example Python code). These still require client-side execution. Offloading is disabled on purpose to minimize the security risk of malicious injection.[^linParrotEfficientServing2024]
- Scheduling features such as outlier handling, job failures, delay scheduling, fairness, starvation, and heterogeneous clusters are left as future work.[^linParrotEfficientServing2024]
- Serving longer context (for example 32k or 1M tokens) within satisfactory latency is beyond the scope of the paper.[^linParrotEfficientServing2024]
- The Bing Copilot evaluation covers only the final request, with synthesized requests, because the authors have no access to its intermediate steps.[^linParrotEfficientServing2024]
- The details of how Parrot chooses LLM engines (`FindEngine`) are omitted for space.[^linParrotEfficientServing2024]
- Most results appear only in figures; the paper has no results tables and no dedicated limitations section.

## Related

- Proposed: [Parrot](../methods/parrot.md), [Semantic Variable](../methods/semantic-variable.md)
- Builds on: [vLLM](../methods/vllm.md), [PagedAttention](../methods/paged-attention.md), [FlashAttention](../methods/flash-attention.md), [Continuous batching](../methods/continuous-batching.md), [KV cache](../methods/kv-cache.md) sharing for common prompt prefixes
- Baselines and frameworks: [FastChat](../methods/fastchat.md), vLLM, HuggingFace Transformers, [LangChain](../methods/langchain.md)
- Applications evaluated: [MetaGPT](../methods/metagpt.md), Bing Copilot, GPTs
- Datasets: [Arxiv-March](../datasets/arxiv-march.md), [ShareGPT](../datasets/sharegpt.md)
- Papers in this wiki cited by this paper: [SGLang](zhengSGLangEfficientExecution2024.md)

[^linParrotEfficientServing2024]: Lin et al. 2024
