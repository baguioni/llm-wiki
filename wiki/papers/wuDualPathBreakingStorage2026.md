---
type: Paper
title: "DualPath: Breaking the Storage Bandwidth Bottleneck in Agentic LLM Inference"
description: Inference system for agentic workloads that loads KV-Cache through decode engines as well as prefill engines, pooling the storage NIC bandwidth of all engines in a prefill-decode disaggregated cluster.
tags: [llm-serving, agentic-inference, kv-cache, prefill-decode-disaggregation, storage-io, rdma, scheduling, ai899]
collections: [ai899]
authors: [Yongtong Wu, Shaoyuan Chen, Yinmin Zhong, Rilin Huang, Yixuan Tan, Wentao Zhang, Liyue Zhang, Shangyan Zhou, Yuxuan Liu, Shunfeng Zhou, Mingxing Zhang, Xin Jin, Panpan Huang]
year: 2026
doi: 10.48550/arXiv.2602.21548
arxiv: "2602.21548"
arxiv_version: 2602.21548v2
sources:
  - id: wuDualPathBreakingStorage2026
    resource: zotero://select/items/@wuDualPathBreakingStorage2026
    title: "DualPath: Breaking the Storage Bandwidth Bottleneck in Agentic LLM Inference"
---

# DualPath: Breaking the Storage Bandwidth Bottleneck in Agentic LLM Inference

Text source: arXiv HTML, version `2602.21548v2`.

## Summary

Agentic LLM workloads are multi-turn, long-context, and short-append, so most of each prompt hits the [KV-Cache](../methods/kv-cache.md) and loading that cache, not computation, dominates performance.[^wuDualPathBreakingStorage2026] In [prefill-decode (PD) disaggregated](../methods/prefill-decode-disaggregation.md) systems with external KV-Cache storage, only prefill engines load the cache from storage. Their storage NICs saturate while the storage NICs of decode engines stay largely idle.[^wuDualPathBreakingStorage2026]

[DualPath](../methods/dualpath.md) adds a storage-to-decode path: the KV-Cache is loaded into a decode engine and then sent to the prefill engine by RDMA over the compute network.[^wuDualPathBreakingStorage2026] A scheduler chooses the path per request and balances load across prefill and decode engines.[^wuDualPathBreakingStorage2026] On the authors' in-house inference system, DualPath improves offline inference throughput by up to 1.87$\times$ and online serving throughput by an average factor of 1.96$\times$ without violating the SLO.[^wuDualPathBreakingStorage2026]

## Contributions

- Identifies the I/O-bound nature of multi-turn agentic workloads and shows that KV-Cache loading dominates system performance under modern inference architectures.[^wuDualPathBreakingStorage2026]
- DualPath, an inference system with dual-path KV-Cache loading that uses decode-engine bandwidth to resolve prefill-side bottlenecks.[^wuDualPathBreakingStorage2026]
- A workload-aware scheduling algorithm that balances computation and network resources.[^wuDualPathBreakingStorage2026]

## Method

### Motivation

- A trace from representative coding tasks has a mean of 157 rounds, an average context length of 32.7k, and a mean append length of 429, which gives a KV-Cache hit rate of 98.7%.[^wuDualPathBreakingStorage2026]
- The *cache-compute ratio* is the ratio of KV-Cache to load to the computation needed. It is approximately 22 GB/PFLOP for DeepSeek-V3.2.[^wuDualPathBreakingStorage2026]
- From NVIDIA Ampere to Blackwell, the I/O-compute ratio decreases by 14.4$\times$.[^wuDualPathBreakingStorage2026]
- Compute-network traffic is intermittent: collective operations burst in sub-millisecond intervals, which leaves spare bandwidth.[^wuDualPathBreakingStorage2026]

Cache-compute ratio with append length 429, across context lengths 16k–64k (Table 1). KV-Cache data type is FP8 unless specified.[^wuDualPathBreakingStorage2026]

| Model | GB/PFLOP (16K–64K) |
|---|---|
| Qwen2.5-32B (FP16) | 117-267 |
| GPT-OSS-120B | 47–95 |
| Qwen3-235B-A22B | 39–60 |
| DeepSeek-V3.2 660B | 13–36 |
| DeepSeek-V3 660B | 4.8–5.8 |

All rows: [^wuDualPathBreakingStorage2026]

### Dual-path loading

DualPath adopts PD disaggregation and [layerwise prefill](../methods/layerwise-prefill.md), in which the GPU holds only one layer's KV-Cache for the forward batch.[^wuDualPathBreakingStorage2026] Each engine manages one GPU and is either a prefill engine (PE) or a decode engine (DE). Each PE and DE has a small DRAM buffer.[^wuDualPathBreakingStorage2026]

- **PE read path.** Hit-token KV-Cache is read from storage into the PE buffer. Before each attention layer, that layer's KV-Cache moves to PE HBM, the miss tokens are computed, and the KV-Cache of hit and miss tokens moves to the DE buffer. This repeats $n_{layer}$ times and overlaps with computation.[^wuDualPathBreakingStorage2026]
- **DE read path.** Hit-token KV-Cache is read into the DE buffer. During PE prefill, each layer's KV-Cache is read from the DE buffer. After a layer completes, only the miss-token KV-Cache is sent to the DE buffer and merged.[^wuDualPathBreakingStorage2026]
- **Decode phase.** The DE allocates HBM, performs host-to-device transfers, and releases CPU memory before decoding. Whenever a full block of tokens (e.g., 64 tokens) accumulates, it is persisted to disk.[^wuDualPathBreakingStorage2026]
- **Block layouts.** A *Layer Block* has shape $[1,tokens,bytes]$ and a *Full Block* has shape $[layer,tokens,bytes]$. Storage uses Full Blocks in a trie structure, and PE-DE transfers use Layer Blocks.[^wuDualPathBreakingStorage2026]

### Bottleneck-free analysis

With $P$ prefill and $D$ decode nodes, $g$ GPUs per node, compute NIC bandwidth $B$, storage bandwidth $s\times B$ per machine, and memory bandwidth $M$ per machine, the system saturates all storage NICs without a compute-NIC or DRAM bottleneck when[^wuDualPathBreakingStorage2026]

$$
\frac{s}{g-s}\leq P/D\leq\min\left\{\frac{g-2s}{s},\frac{g-s}{2s},\frac{M/Bs-3}{2}\right\}
$$

For $(g=8,s=1)$ with $M\approx 500$ GB/s and $Bs\approx 50$ GB/s, the range is $\frac{1}{7}\leq$ P/D $\leq\frac{7}{2}$.[^wuDualPathBreakingStorage2026]

### CNIC-centric traffic manager

- All data traffic in or out of a GPU, including local H2D/D2H copies, goes through the GPU's paired compute NIC (CNIC) with a GPUDirect RDMA data path, so that the compute network's QoS can separate traffic classes.[^wuDualPathBreakingStorage2026]
- On InfiniBand, model inference communication uses a high-priority virtual lane and KV-Cache transfer uses a low-priority one. A weighted round-robin policy reserves approximately 99% of total bandwidth for the high-priority lane.[^wuDualPathBreakingStorage2026]
- Submitting one copy via cudaMemcpyAsync has a latency overhead of approximately 5-7$\mu s$. Submitting one RDMA Write work request takes around 1$\mu s$.[^wuDualPathBreakingStorage2026]

### Adaptive request scheduler

- **Inter-engine, PE.** Each engine $e$ reports its unfinished token count $tok_{e}$ and its node's disk reading queue length $read\_q_{n(e)}$. Engines with $tok_{e}>\beta$ are overloaded and get no new requests. A request goes to the PE with minimum $tok_{e}$ among engines with $read\_q_{n(e)}\leq\alpha$, otherwise among those with a longer queue.[^wuDualPathBreakingStorage2026]
- **Inter-engine, DE.** Requests go to the DE group with the minimum total $tok_{e}$. Within a group, DEs with enough HBM are split by the threshold $Z=1.05\times(\sum_{r\in R}{len_{r}}+\sum_{e\in E}{tok_{e}})/|E|$, and the DE with minimum $seq_{e}$ below the threshold is preferred.[^wuDualPathBreakingStorage2026]
- **Read path choice.** After the PE and DE are selected, the KV-Cache is read on the side with the shorter reading queue.[^wuDualPathBreakingStorage2026]
- **Intra-engine, PE only.** Requests are added to a forward batch in FIFO order while the predicted attention-layer time stays under a *compute quota*. If a request would exceed it, a binary search finds a smaller batch size and the request uses [chunked prefill](../methods/chunked-prefill.md).[^wuDualPathBreakingStorage2026]
- Settings: $\alpha$ is the number of tokens that can be read during $3$ seconds, $\beta$ is the number of tokens one GPU can process for $5$ seconds, and the compute quota is 300ms.[^wuDualPathBreakingStorage2026]

## Experiments & Results

### Setup

- Implementation: approximately 5K lines of modifications on the authors' in-house inference framework, with [3FS](../methods/3fs.md) as distributed storage.[^wuDualPathBreakingStorage2026]
- Testbed: servers with 8 NVIDIA Hopper GPUs, eight 400Gbps RDMA NICs on InfiniBand, and one storage NIC connected to 3FS.[^wuDualPathBreakingStorage2026]
- Models: DeepSeek V3.2 660B (DS 660B), a 27B downscaled version (DS 27B), and Qwen2.5-32B (Qwen 32B).[^wuDualPathBreakingStorage2026]
- Default P/D: 2P4D for DS 660B, 1P2D for Qwen 32B, 1P1D for DS 27B.[^wuDualPathBreakingStorage2026]
- Baselines: *Basic* (the unmodified internal framework), *SGL(MC)* ([SGLang](../methods/sglang.md) with HiCache, [Mooncake](../methods/mooncake.md) Store, and 3FS), and *Oracle* (DualPath with all disk reads and KV-Cache transfers bypassed).[^wuDualPathBreakingStorage2026] The paper states that comparing DualPath with SGL(MC) is unfair because of implementation differences, and reports improvements only from Basic.[^wuDualPathBreakingStorage2026]
- DRAM: DualPath allocates 80GB per node for DeepSeek models and 320GB for Qwen 32B. SGL(MC) uses 1.5TB on every node.[^wuDualPathBreakingStorage2026]
- Online SLO: TTFT $\leq$ 4 seconds and TPOT $\leq$ 50ms.[^wuDualPathBreakingStorage2026]

Agent trace datasets from production agentic RL training, 500 trajectories each (Table 2):[^wuDualPathBreakingStorage2026]

| MaxLen | Turns | Append | Gen | Total | Context |
|---|---|---|---|---|---|
| 32K | 60 | 608 | 148 | 28639 | 17183 |
| 48K | 106 | 474 | 172 | 42607 | 25120 |
| 64K | 157 | 429 | 176 | 55958 | 32721 |

All rows: [^wuDualPathBreakingStorage2026]

### Offline batch inference (job completion time, JCT)

| Setting | DualPath vs Basic |
|---|---|
| DS 660B, varying agent batch size and max agent length | up to $1.87\times$ |
| DS 27B, varying agent batch size and max agent length | up to $1.78\times$; DualPath remains $1.09$–$1.85\times$ slower than Oracle |
| DS 660B, 64K context, 1024 agents, varying append length scale | $1.82-1.99\times$ |
| DS 27B, P/D ratios 1P1D, 2P1D, 1P2D | average $1.64\times$, up to $2.46\times$ |

All rows: [^wuDualPathBreakingStorage2026]

Per-configuration JCT values are given only in Figures 7 to 9.[^wuDualPathBreakingStorage2026] DualPath 1P1D and Basic 2P1D perform comparably, which the paper attributes to equal available storage bandwidth.[^wuDualPathBreakingStorage2026]

### Online serving

| Model | Agent arrival rate (APS) capacity, DualPath vs Basic |
|---|---|
| DS 27B | 1.67$\times$ |
| DS 660B | 2.25$\times$ |

All rows: [^wuDualPathBreakingStorage2026]

DualPath's TTST is comparable to Basic, and TPOT shows no additional decoding overhead.[^wuDualPathBreakingStorage2026] For DS 660B serving, the KV-Cache working set of DualPath ranges from 69 GB at APS 0.1 to 681 GB at APS 0.45.[^wuDualPathBreakingStorage2026]

### Ablation (offline, DS 660B, 64K, agent batch size 1024 and 2048)

Techniques are added cumulatively. Values are the JCT reduction compared to Basic.[^wuDualPathBreakingStorage2026]

| Configuration | JCT reduction vs Basic |
|---|---|
| + Layerwise prefill | $17.21\%$ on average |
| + Dual-path loading | $38.19\%$ on average |
| + Scheduling algorithm (full DualPath) | $45.62\%$ |

All rows: [^wuDualPathBreakingStorage2026]

Load balance, as the ratio of maximum to average: storage NIC traffic improves from 1.53 with round robin scheduling to 1.18, and attention execution time stays as low as 1.06 during the first 5% of the task.[^wuDualPathBreakingStorage2026]

### Large-scale scalability (Table 3, up to 1,152 GPUs)

| | Setting | JCT | TTFT | TTST | TPOT |
|---|---|---|---|---|---|
| Offline | 2P4D, 2K agents | 3,167s | – | – | – |
| Offline | 48P96D, 48K agents | 3,201s | – | – | – |
| Online | 2P4D, 0.4 APS | – | 1.739s | 0.228s | 0.039s |
| Online | 44P88D, 8.8 APS | – | 1.847s | 0.194s | 0.036s |

All rows: [^wuDualPathBreakingStorage2026]

The 44P88D configuration achieves 22$\times$ throughput (8.8 vs. 0.4 APS). Scheduler CPU usage stays below 10 cores.[^wuDualPathBreakingStorage2026]

## Limitations

- The large-scale experiments show no additional JCT or serving capacity gains over multiple small-scale units of equivalent cost, because parallelism settings and P/D ratios were not fine-tuned.[^wuDualPathBreakingStorage2026]
- On DS 27B, both Basic and DualPath show significantly higher TPOT than Oracle, which suggests considerable P-D transfer overhead for small models. This is left as future work.[^wuDualPathBreakingStorage2026]
- A request's KV-Cache is read from one side only. Splitting it across both sides is left as future work.[^wuDualPathBreakingStorage2026]
- The evaluation assumes zero inter-arrival time and zero tool call latency, so the realistic working set would be larger.[^wuDualPathBreakingStorage2026]
- The DE buffer adds an extra H2D transfer, which puts bandwidth pressure on DRAM and the CNIC.[^wuDualPathBreakingStorage2026]
- Gains are measured only against the authors' own Basic framework. SGL(MC) failed on some large configurations, has no DS 27B run, and uses TP=8 for Qwen 32B where DualPath uses DP.[^wuDualPathBreakingStorage2026]
- The traces come from the authors' production agentic RL training workloads, and DS 27B is an internal model.[^wuDualPathBreakingStorage2026]
- The authors expect lower TTFT percentiles to be achievable with a better scheduling algorithm under large-scale deployment.[^wuDualPathBreakingStorage2026]
- Code availability: not stated.

## Related

- Methods proposed: [DualPath](../methods/dualpath.md)
- Methods built on: [KV cache](../methods/kv-cache.md), [Prefill-decode disaggregation](../methods/prefill-decode-disaggregation.md), [Layerwise prefill](../methods/layerwise-prefill.md), [Chunked prefill](../methods/chunked-prefill.md)
- Systems compared or built on: [SGLang](../methods/sglang.md), [Mooncake](../methods/mooncake.md), [3FS](../methods/3fs.md)
- Papers in this wiki cited by this paper: [SGLang](zhengSGLangEfficientExecution2024.md)

[^wuDualPathBreakingStorage2026]: Wu et al. 2026
