---
type: Paper
title: "SGLang: Efficient Execution of Structured Language Model Programs"
description: A Python-embedded language and co-designed runtime for multi-call LLM programs that reuses the KV cache through a radix tree (RadixAttention) and speeds up constrained decoding with a compressed finite state machine.
tags: [llm-serving, lm-programs, kv-cache, prefix-caching, constrained-decoding, scheduling, ai899]
collections: [ai899]
authors: [Lianmin Zheng, Liangsheng Yin, Zhiqiang Xie, Chuyue Sun, Jeff Huang, Cody Hao Yu, Shiyi Cao, Christos Kozyrakis, Ion Stoica, Joseph E. Gonzalez, Clark Barrett, Ying Sheng]
doi: 10.52202/079017-2000
arxiv: "2312.07104"
arxiv_version: 2312.07104v2
code: https://github.com/sgl-project/sglang
sources:
  - id: zhengSGLangEfficientExecution2024
    resource: zotero://select/items/@zhengSGLangEfficientExecution2024
    title: "SGLang: Efficient Execution of Structured Language Model Programs"
---

# SGLang: Efficient Execution of Structured Language Model Programs

Text source: arXiv HTML, version `2312.07104v2`.

## Summary

"Language Model Programs" (LM programs) are programs that schedule and control LLM generation. They typically contain multiple LLM calls interspersed with control flow, and they take structured inputs and produce structured outputs.[^zhengSGLangEfficientExecution2024] The paper identifies two problems: programming them is tedious (string manipulation, prompt tuning, brittle output parsing, parallelism), and executing them is inefficient because inference engines such as vLLM, TGI, and TensorRT-LLM are optimized without knowledge of the workload, so they recompute the KV cache of shared prefixes and decode constrained outputs one token at a time.[^zhengSGLangEfficientExecution2024]

SGLang (Structured Generation Language) has a front-end language embedded in Python and a back-end runtime (SGLang Runtime, SRT). Its core idea is to exploit the multi-call structure of LM programs for efficient execution.[^zhengSGLangEfficientExecution2024] The runtime adds three optimizations: [RadixAttention](../methods/radix-attention.md) for automatic KV cache reuse, a [compressed finite state machine](../methods/compressed-fsm.md) for constrained decoding, and [API speculative execution](../methods/api-speculative-execution.md) for API-only models.[^zhengSGLangEfficientExecution2024] The paper reports up to $6.4\times$ higher throughput than existing programming and inference systems, including Guidance, vLLM, and LMQL.[^zhengSGLangEfficientExecution2024]

## Contributions

- A domain-specific language embedded in Python with primitives for generation (`extend`, `gen`, `select`) and parallelism control (`fork`, `join`), with an interpreter and a compiler.[^zhengSGLangEfficientExecution2024]
- RadixAttention: the KV cache of all requests is kept as an LRU cache in a radix tree, with a cache-aware scheduling policy. The paper states it is the first solution that supports multi-level sharing, cache-aware scheduling, frontend-runtime co-scheduling, and distributed cases.[^zhengSGLangEfficientExecution2024]
- A compressed finite state machine that decodes multiple tokens in one forward pass under a regular-expression constraint.[^zhengSGLangEfficientExecution2024]
- API speculative execution, which reduces the latency and input-token cost of multi-call programs on black-box API models.[^zhengSGLangEfficientExecution2024]
- A theorem that longest-shared-prefix-first scheduling gives an optimal cache hit rate for a batch of requests in the offline case.[^zhengSGLangEfficientExecution2024]

## Method

### Programming model

| Primitive | Function |
|---|---|
| `gen` | Calls a model to generate and stores the result in a named variable. Takes a `regex` argument that constrains the output to a grammar defined by a regular expression (e.g., a JSON schema). |
| `select` | Calls a model to choose the highest-probability option from a list. |
| `+=` or `extend` | Appends a string to the prompt. |
| `[variable_name]` | Fetches the result of a generation. |
| `fork` | Creates parallel forks of the prompt state. |
| `join` | Rejoins the prompt state. |
| `image`, `video` | Take image and video inputs. |

All rows: [^zhengSGLangEfficientExecution2024]

- **Interpreter mode (default).** A prompt is an asynchronous stream. Primitives are submitted to the stream as non-blocking calls. Each prompt is managed by a stream executor in a background thread, which gives intra-program parallelism. Fetching a generation result blocks until it is ready.[^zhengSGLangEfficientExecution2024]
- **Compiler mode.** A program is traced with abstract arguments into a computational graph (an IR with nodes such as ConstantText, Argument, Gen, Select, Variable, Fork, GetForkItem, Join) and run by a graph executor. Tracing is limited to programs without data-dependent control flow.[^zhengSGLangEfficientExecution2024]
- The paper states that an equivalent program for its running example (a multi-dimensional essay judge using branch-solve-merge) written against an OpenAI API-like interface would take $2.1\times$ as many lines of code.[^zhengSGLangEfficientExecution2024]

Feature comparison (Table 1):[^zhengSGLangEfficientExecution2024]

| System | Syntax | Language Primitives | Runtime Backends |
|---|---|---|---|
| LMQL | Custom | extend, gen, select | HF Transformers, llama.cpp, OpenAI |
| Guidance | Python | extend, gen, select, image | HF Transformers, llama.cpp, OpenAI |
| SGLang | Python | extend, gen, select, image, video, fork, join | SGLang Runtime (SRT), OpenAI |

### RadixAttention

- KV cache computation depends only on prefix tokens, so requests with the same prompt prefix can reuse the [KV cache](../methods/kv-cache.md).[^zhengSGLangEfficientExecution2024]
- Existing systems discard the KV cache after a request finishes. SGLang retains the cache for prompts and generation results in a radix tree that maps token sequences to KV cache tensors. This supports prefix search, reuse, insertion, and eviction.[^zhengSGLangEfficientExecution2024]
- KV cache tensors are stored in a non-contiguous, paged layout where each page is one token.[^zhengSGLangEfficientExecution2024]
- **Eviction.** An LRU policy evicts the least recently used leaf first, so common ancestors stay reusable until they become leaves. Each node has a reference counter of running requests that use it, and a node is evictable when the counter is zero.[^zhengSGLangEfficientExecution2024]
- **Memory.** No fixed-size cache pool is preallocated. Cached tokens and running requests share one memory pool, and when enough waiting requests run, the system evicts all cached tokens in favor of a larger batch size.[^zhengSGLangEfficientExecution2024]
- **Frontend hint.** On `fork`, the frontend sends the prefix first as a hint so that it is inserted into the tree, then sends the remaining prompts.[^zhengSGLangEfficientExecution2024]
- The tree structure is stored on the CPU. RadixAttention is compatible with [continuous batching](../methods/continuous-batching.md), paged attention, and tensor parallelism.[^zhengSGLangEfficientExecution2024]
- **Multi-modal inputs.** The hash of an input image is used as the key in the radix tree, so the KV cache of image tokens from the same image is reused.[^zhengSGLangEfficientExecution2024]

### Cache-aware scheduling

- Cache hit rate is defined as $\frac{\text{number of cached prompt tokens}}{\text{number of prompt tokens}}$.[^zhengSGLangEfficientExecution2024]
- In the batch-processing setting, waiting requests are sorted by matched prefix length, and requests with longer matched prefixes run first, instead of first-come, first-served (longest-shared-prefix-first order).[^zhengSGLangEfficientExecution2024]
- **Theorem 3.1.** For a batch of requests, an optimal cache hit rate is achieved by visiting the radix tree of the requests in depth-first search order, with a cache size $\geq$ the maximum request length. The longest-shared-prefix-first order is equivalent to a depth-first search order.[^zhengSGLangEfficientExecution2024]
- In the online case the DFS order is disrupted, but the schedule still approximates DFS behavior on the augmented part of the full radix tree.[^zhengSGLangEfficientExecution2024]
- **Distributed cases.** With tensor parallelism, each GPU keeps a sharded KV cache and no extra synchronization is needed. With data parallelism, each worker keeps its own sub-tree and a router keeps a meta-tree, dispatching by the length of the shared prefix. Evictions at a worker are committed to a queue that the router processes during periods of low activity.[^zhengSGLangEfficientExecution2024]

### Compressed finite state machine

- Existing systems convert a regular expression into a finite state machine (FSM), mask invalid tokens at each step, and decode token by token.[^zhengSGLangEfficientExecution2024]
- SGLang builds the FSM on characters/strings and merges adjacent *singular transition edges* (the source node has only one successor and there is only one acceptable character/string on the edge) into single compressed edges. Multiple tokens on a compressed edge are decoded in one forward pass ("Jump Forward").[^zhengSGLangEfficientExecution2024]
- **Retokenization.** The original tokenizer retokenizes all previous text plus the text of the compressed edge, so the tokens match the model's input format. The paper says this brings only minor overhead.[^zhengSGLangEfficientExecution2024]

### API speculative execution

For a multi-call pattern on a black-box API model, the first call ignores the stop condition and generates a few more tokens. The interpreter keeps the extra output and matches and reuses it for later primitives, which can save the latency and input cost of an API call.[^zhengSGLangEfficientExecution2024]

## Experiments & Results

### Setup

- Implementation: PyTorch with custom CUDA kernels from FlashInfer and Triton.[^zhengSGLangEfficientExecution2024]
- Models: Llama-2 (dense), Mixtral (sparse mixture of experts), LLaVA image and video models, and OpenAI's GPT-3.5. Open-weight models range from 7 billion to 70 billion parameters, in float16 precision.[^zhengSGLangEfficientExecution2024]
- Hardware: AWS EC2 G5 instances with NVIDIA A10G GPUs (24GB) for most experiments, and A100G (80GB) GPUs for some. Llama-7B on a single A10G; Mixtral-8x7B on 8 A10G GPUs with tensor parallelism; Llama-70B on 4 A100G GPUs with tensor parallelism.[^zhengSGLangEfficientExecution2024]
- Baselines: [Guidance](../methods/guidance.md) v0.1.8 with llama.cpp backend; [vLLM](../methods/vllm.md) v0.2.5 with its default API server; [LMQL](../methods/lmql.md) v0.7.3 with Hugging Face Transformers backend. An earlier vLLM version was used because RadixAttention has been partially integrated into the latest vLLM as an optional experimental feature.[^zhengSGLangEfficientExecution2024]
- Workloads: 5-shot [MMLU](../datasets/mmlu.md), 20-shot [HellaSwag](../datasets/hellaswag.md), ReAct agent and generative agents (replayed traces from the original papers), Tree-of-thought on GSM-8K, Skeleton-of-thought for tip generation, LLM judges with branch-solve-merge, JSON decoding with a regex schema, multi-turn chat with 4 turns (short: 4-8 output tokens; long: 256-512 output tokens; input of each turn sampled between 256-512 tokens), and a DSPy retrieval-augmented generation pipeline.[^zhengSGLangEfficientExecution2024]
- Metrics: throughput (programs per second, p/s, at a sufficiently large batch of program instances) and latency (average over instances, one program at a time without batching).[^zhengSGLangEfficientExecution2024]

### End-to-end results

| Setting | Result | Compared against |
|---|---|---|
| Llama-7B, open-weight benchmarks (Fig. 5) | throughput improved by up to $6.4\times$ | Guidance, vLLM, LMQL |
| Llama-7B, open-weight benchmarks (Fig. 6) | latency reduced by up to $3.7\times$ | Guidance, vLLM, LMQL |
| Cache hit rate on these benchmarks | ranges from 50% to 99% | not applicable |
| Cache-aware scheduling | approaches 96% of the optimal hit rate on average | optimal cache hit rate |
| Chatbot Arena deployment, LLaVA-Next-34B | 52.4% RadixAttention cache hit rate after one month | not applicable |
| Chatbot Arena deployment, Vicuna-33B | 74.1% RadixAttention cache hit rate after one month; first-token latency reduced by an average of $1.7\times$ | not stated |
| GPT-3.5, extracting three fields from a Wikipedia page | cost of input tokens reduced by about threefold | without API speculative execution |

All rows: [^zhengSGLangEfficientExecution2024]

Per-benchmark throughput and latency values are reported only as normalized bar charts (Fig. 5, 6, 7, 12), so they are not tabulated here.[^zhengSGLangEfficientExecution2024]

- Speedup on Mixtral-8x7B and Llama-70B with tensor parallelism shows a trend similar to the smaller models.[^zhengSGLangEfficientExecution2024]
- In multi-turn chat, the speedup is more noticeable for short outputs. For long outputs there is almost no speedup, because there is little sharing between chat sessions and decoding time dominates.[^zhengSGLangEfficientExecution2024]
- LMQL and Guidance are excluded from some of the last five benchmarks because of slow performance and missing functionalities, and from the tensor-parallel runs because they lack efficient implementations of tensor parallelism.[^zhengSGLangEfficientExecution2024]

### Multi-modal throughput (Table 2)

LLaVA-v1.5-7B runs on llava-bench-in-the-wild on a single A10G (24GB) GPU; LLaVA-NeXT-34B runs on ActivityNet on a single A100G (80GB) GPU. The baseline is the model authors' original implementation in Hugging Face Transformers.[^zhengSGLangEfficientExecution2024]

| Model | LLaVA-v1.5-7B (image) | LLaVA-NeXT-34B (video) |
|---|---|---|
| Author's original implementation | 0.18 image/s | 0.02 frame/s |
| SGLang | 1.15 image/s | 0.10 frame/s |

The paper summarizes this as throughput up to $6\times$ higher.[^zhengSGLangEfficientExecution2024]

### Ablations

- **Cache hit rate.** On the tree-of-thought benchmark, a higher cache hit rate leads to a larger batch size, higher throughput, and lower latency.[^zhengSGLangEfficientExecution2024]
- **RadixAttention components (Fig. 8(c), Llama-7B on a single A10G).** Variants tested: No Cache, No Tree-Structure, FCFS Schedule, Random Schedule, No Frontend Parallelism, No Frontend Hint, Full optimizations. The paper reports that each component is required for the best performance. Numbers are given only in the figure.[^zhengSGLangEfficientExecution2024]
- **RadixAttention overhead.** On [ShareGPT](../datasets/sharegpt.md), a benchmark with no KV cache reuse opportunities, 100 requests take 74.3 seconds, of which managing the RadixAttention data structures takes 0.2 seconds, an overhead of less than 0.3%.[^zhengSGLangEfficientExecution2024]
- **Compressed FSM.** On JSON decoding, the compressed FSM increases throughput by $1.6\times$. Redoing the FSM preprocessing for each request instead of reusing it across a batch makes the throughput $2.4\times$ lower.[^zhengSGLangEfficientExecution2024]
- **Data-parallel RadixAttention.** With four workers on the MMLU dataset, the paper reports linear scaling and an optimal cache hit rate.[^zhengSGLangEfficientExecution2024]
- **Compiler optimization case study.** GPT-4 is prompted to reorder graph nodes to lengthen the constant prefix. Of 20 prompt templates, 5 are few-shot examples and 15 are test cases. GPT-4 reorders 12 out of the 15 without altering the semantics, and the shareable prefix grows by 60 tokens on average.[^zhengSGLangEfficientExecution2024]

## Limitations

- Greedy cache-aware scheduling can lead to starvation. Integration with fair scheduling methods is left as future work.[^zhengSGLangEfficientExecution2024]
- In practice, the unpredictable number of output tokens can cause recomputation of the KV cache, so the computation differs from the one in the proof of Theorem 3.1.[^zhengSGLangEfficientExecution2024]
- Compiler-mode tracing does not support data-dependent control flow. The prefix-sharing code movement does not strictly preserve the original computation, and it fails on 3 of the 15 test templates by putting all constants upfront even when that changes the semantics.[^zhengSGLangEfficientExecution2024]
- The compressed FSM can distort the probability distribution over choices, because the model does not see the full range of choices when a choice lies on a compressed transition. The paper offers a workaround (put the choices or the regex in the prompt) and says it does not solve the underlying issue.[^zhengSGLangEfficientExecution2024]
- There is a trade-off between data locality and parallel processing efficiency in the data-parallel setting. Scheduling policies for it are left for future research.[^zhengSGLangEfficientExecution2024]
- Listed future directions: more output modalities, RadixAttention across multiple levels of the memory hierarchy (e.g., DRAM, Disk), fuzzy semantic matching within RadixAttention, higher-level primitives, and static compiler optimizations such as scheduling and memory planning.[^zhengSGLangEfficientExecution2024]

## Related

- Methods proposed: [SGLang](../methods/sglang.md), [RadixAttention](../methods/radix-attention.md), [Compressed finite state machine](../methods/compressed-fsm.md), [API speculative execution](../methods/api-speculative-execution.md), [Cache-aware scheduling](../methods/cache-aware-scheduling.md)
- Methods built on: [KV cache](../methods/kv-cache.md), [Constrained decoding](../methods/constrained-decoding.md), [Continuous batching](../methods/continuous-batching.md)
- Systems compared: [vLLM](../methods/vllm.md), [Guidance](../methods/guidance.md), [LMQL](../methods/lmql.md)
- Datasets: [MMLU](../datasets/mmlu.md), [HellaSwag](../datasets/hellaswag.md), [ShareGPT](../datasets/sharegpt.md)
- Papers in this wiki cited by this paper: [InferCept](abhyankarInferCeptEfficientIntercept2024.md) (cited under the name "API Serve"; the paper says it studies KV cache reuse for interleaving with external API calls but does not have a radix tree or cache-aware scheduling)[^zhengSGLangEfficientExecution2024]

[^zhengSGLangEfficientExecution2024]: Zheng et al. 2024
