---
type: Paper
title: Collaborative Speculative Inference for Efficient LLM Inference Serving
description: CoSine decouples speculative drafting from verification across heterogeneous nodes, with drafter routing, confidence-based token fusion, and pipeline scheduling.
tags: [speculative-decoding, llm-serving, multi-drafter, heterogeneous-gpu, scheduling]
collections: [scheduling]
authors: [Luyao Gao, Jianchun Liu, Hongli Xu, Xichong Zhang, Yunming Liao, Liusheng Huang]
arxiv: "2503.10325"
arxiv_version: 2503.10325v2
sources:
  - id: gaoCollaborativeSpeculativeInference
    resource: zotero://select/items/@gaoCollaborativeSpeculativeInference
    title: Collaborative Speculative Inference for Efficient LLM Inference Serving
---

# Collaborative Speculative Inference for Efficient LLM Inference Serving

Text source: arXiv HTML, version `2503.10325v2`.

## Summary

Speculative inference uses small speculative models (SSMs) as drafters and verifies their draft tokens in parallel with the target LLM.[^gaoCollaborativeSpeculativeInference] The paper names two obstacles. First, drafting and verification have different resource demands: drafting is memory-bound and verification is compute-bound, so co-locating them causes contention. Second, drafters have limited knowledge, so acceptance is low (the paper cites acceptance rates below 0.3 for the LLaMA13B-LLaMA68M pair).[^gaoCollaborativeSpeculativeInference]

CoSine is a speculative inference system that decouples sequential speculative decoding from parallel verification and runs them on different nodes. A *speculation cluster* of consumer-grade GPUs drafts, and a *verification server* of datacenter-grade GPUs verifies.[^gaoCollaborativeSpeculativeInference] Requests are routed to specialized drafters, the drafters' outputs are merged by confidence-based token fusion, and a pipeline scheduler balances drafting and verification.[^gaoCollaborativeSpeculativeInference]

The abstract reports up to a 23.2% decrease in latency and a 32.5% increase in throughput compared to baseline methods at equivalent resource costs.[^gaoCollaborativeSpeculativeInference]

## Contributions

- CoSine, a speculative inference system that architecturally decouples sequential speculative decoding and parallel verification with multi-node collaboration.[^gaoCollaborativeSpeculativeInference]
- An adaptive strategy that routes inference requests to suitable drafters, and a confidence-based token fusion mechanism that synthesizes outputs across multiple nodes.[^gaoCollaborativeSpeculativeInference]
- Dynamic orchestration of pipeline workflows that balances resource allocation between draft generation and verification in real time.[^gaoCollaborativeSpeculativeInference]
- Experiments in which, under equivalent costs, CoSine achieves up to a 23% reduction in latency and a 32% improvement in throughput compared to baseline methods.[^gaoCollaborativeSpeculativeInference]

## Method

### Motivation

- Profiling on an NVIDIA A100 shows that autoregressive drafting in SSMs relies mostly on memory-intensive GEMV operations, and batched verification in LLMs relies on compute-intensive GEMM operations.[^gaoCollaborativeSpeculativeInference]
- With LLaMA-68M drafters and a LLaMA-13B verifier, sequential drafting gives smaller speedup gains as draft length grows, and aggregating predictions from multiple drafters gives greater coverage.[^gaoCollaborativeSpeculativeInference]
- Domain-specialized SSMs are complementary: task-specific efficiency variances exceed $2\times$.[^gaoCollaborativeSpeculativeInference]
- Tokens in the top-10% probability percentile achieve an 80% higher acceptance ratio.[^gaoCollaborativeSpeculativeInference]

### Architecture

- **Speculation cluster.** A star-topology network of consumer-grade nodes, each with a specialized drafter, coordinated by a central node.[^gaoCollaborativeSpeculativeInference]
- **Verification server.** Multiple datacenter-grade GPUs with tensor parallelism, pipeline parallelism, and continuous batching.[^gaoCollaborativeSpeculativeInference]
- **Request pool.** Requests are processed iteratively in batches. After verification a request returns to the pool until `<EOS>` or the maximum generation length.[^gaoCollaborativeSpeculativeInference]

### Cooperative generation component

- **Routing score.** For request $r$ and node $n$ with draft length $K$, the score combines the generation confidence $c_{n,i}^{r}$ (token logit probability) and the verification accuracy $d_{n,i}^{r}$:[^gaoCollaborativeSpeculativeInference]

  $$m_{n}^{r}=\frac{1}{K}\sum_{i=1}^{K}\frac{c_{n,i}^{r}d_{n,i}^{r}}{c_{n,i}^{r}d_{n,i}^{r}+(1-c_{n,i}^{r})(1-d_{n,i}^{r})}$$

- **Verification accuracy.** $d_{n,i}^{r}$ is the cosine similarity between the LLM embedding of the accepted token and of the draft token at position $i$ when $i<L_{\text{acc}}$, and 0 otherwise. $L_{\text{acc}}$ is the draft acceptance length.[^gaoCollaborativeSpeculativeInference]
- **Explore or exploit.** $\text{Routing}(r)=\alpha\mathcal{T}(\mathbf{M}_{r})+(1-\alpha)\mathcal{R}(\mathbf{M}_{r})$ when $L_{\text{acc}}<\tau$, and the same form with $\beta$ otherwise, where $\alpha>\beta$, $\mathcal{T}$ selects the top-scoring drafters, and $\mathcal{R}$ selects at random.[^gaoCollaborativeSpeculativeInference]
- **Confidence-based token fusion.** At each drafting iteration the central node aggregates the draft tokens from all participating nodes and selects the token with the highest logit probability, $x_{i}^{*}=\arg\max P(x_{i}^{n})$. The fused token is sent back to the drafters for the next iteration. The aggregated draft tokens form token trees that are verified with tree attention.[^gaoCollaborativeSpeculativeInference]

### Collaborative pipeline component

- **Request scheduler.** A batch assignment $\mathbf{B}=\{b_{1},\ldots,b_{R}\}$, $b_{i}\in\{0,1\}$, is chosen by solving[^gaoCollaborativeSpeculativeInference]

  $$\mathbf{B}^{*}=\arg\min_{\mathbf{B}}\left(\frac{T_{\text{ttl}}}{b}+\lambda\Gamma\right)$$

  subject to $T_{ttl}=\max(T_{ssm}(b,l,\gamma))+T_{llm}(b,l,\Gamma)\leq T_{\text{max}}$, $\sum b_{i}m_{i}\leq M_{\text{max}}$, $\Gamma=\sum b_{i}\gamma_{i}\leq\Gamma_{\text{max}}$, and $\gamma_{i}\geq 1$. Here $b$ is the batch size, $l$ the longest request length in the batch, $\gamma_{i}$ the draft token count of request $i$, and $\Gamma$ the number of verified tokens.[^gaoCollaborativeSpeculativeInference]
- **Adaptive speculation.** While $\sum b_{i}\gamma_{i}>\Gamma_{\text{max}}$, the request with the largest $\gamma_{i}$ loses one draft token. When the verification server is idle the speculation cluster adds participating nodes, and when it is overloaded the cluster removes nodes.[^gaoCollaborativeSpeculativeInference]

### Implementation

- Python prototype of 4.2k LoC on PyTorch 2.1 and DeepSpeed 0.12.[^gaoCollaborativeSpeculativeInference]
- The routing solver has 0.1ms decision latency and selects 2-3 drafters per request.[^gaoCollaborativeSpeculativeInference]
- The verification server shards Llama-2-70B across 4 GPUs with 4-stage pipelining (16 microbatches). A modified HuggingFace `generate()` with CUDA-accelerated rejection sampling gives 1.7× faster verification than sequential decoding.[^gaoCollaborativeSpeculativeInference]

## Experiments & Results

### Setup

- Hardware: a server with four NVIDIA A100 (80GB) GPUs connected by NVLink, and a cluster of 16 consumer-grade GPUs (8 NVIDIA RTX 2080Ti and 8 RTX 3090) connected by 100Mbps Ethernet. The two are connected by 10Gbps Ethernet.[^gaoCollaborativeSpeculativeInference]
- Prompts: 8192 prompts sampled from [PIQA](../datasets/piqa.md) (physics), [MedQA](../datasets/medqa.md) (medicine), [FIQA](../datasets/fiqa.md) (finance), [Alpaca](../datasets/alpaca.md) (instruction following), and [OASST2](../datasets/oasst2.md) (conversational alignment).[^gaoCollaborativeSpeculativeInference]
- LLaMA pair: DeepSeek-R1-Distill-Llama-70B target and LLaMA68M drafter, evaluated with the 2080Ti GPUs. Qwen pair: DeepSeek-R1-Distill-Qwen-32B target and Qwen2.5-0.5B drafter, evaluated with the 3090 GPUs.[^gaoCollaborativeSpeculativeInference]
- Baselines: [vLLM](../methods/vllm.md), Vanilla speculative inference (a single draft model on vLLM), [PipeInfer](../methods/pipeinfer.md), and [SpecInfer](../methods/specinfer.md).[^gaoCollaborativeSpeculativeInference]
- Settings: fixed input of 256 tokens, output of 128 tokens, greedy sampling. Offline serving uses batch sizes from 1 to 16 and reports the mean of 10 trials. Performance metrics are computation-normalized for cost fairness.[^gaoCollaborativeSpeculativeInference]

### Hardware comparison (Table 1)

| Metrics | 2080Ti | 3090 | A100 |
|---|---|---|---|
| FPLOPS (FP16) | 107.6 | 285 | 5144 |
| Bandwidth (GB/s) | 616 | 936 | 2,039 |
| SSM Speed (tokens/s) | 350 | 450 | 9,500 |
| LLM Speed (tokens/s) | OOM | OOM | 7.13 |
| Rent Cost ($/hr) | 0.12 | 0.22 | 5.67 |
| Deploy Cost ($) | 200 | 1,000 | 60,000 |

All rows: [^gaoCollaborativeSpeculativeInference]

### Drafter specialization (Table 2)

The table caption calls the values "acceptance ratio". Drafters #1-#6 are fine-tuned on different domains.[^gaoCollaborativeSpeculativeInference]

| Datasets | #1 | #2 | #3 | #4 | #5 | #6 |
|---|---|---|---|---|---|---|
| PIQA | 2.86 | 1.82 | 1.74 | 1.80 | 1.91 | 2.20 |
| MedQA | 1.72 | 3.13 | 1.85 | 2.01 | 1.84 | 2.05 |
| FIQA | 1.69 | 1.73 | 2.95 | 1.96 | 2.28 | 2.13 |
| Alpaca | 1.83 | 1.95 | 2.04 | 2.86 | 2.13 | 1.82 |
| OASST2 | 2.24 | 1.84 | 1.87 | 1.94 | 3.20 | 2.08 |

All rows: [^gaoCollaborativeSpeculativeInference]

### Offline serving

The per-batch-size curves exist only in figures. The numbers below are the ones stated in the text.[^gaoCollaborativeSpeculativeInference]

| Metric | LLaMA pair | Qwen pair | Compared against |
|---|---|---|---|
| Latency reduction | 17.9%–27.1% | 15.2%–20.5% | strongest baseline (e.g., SpecInfer for small batches and PipeInfer for large batches) |
| Latency reduction at larger batch sizes | 22.4% | 17.9% | PipeInfer |
| Throughput improvement, $B=1$ to $B=16$ | $1.31\times$ to $1.62\times$ | not stated | SpecInfer |
| Throughput improvement, $B=1$ to $B=16$ | $1.24\times$ to $1.46\times$ | not stated | PipeInfer |
| Normalized throughput | $3.15\times$ to $4.71\times$ | $2.84\times$ to $3.79\times$ | vLLM |

All rows: [^gaoCollaborativeSpeculativeInference]

From $B=1$ to $B=16$, CoSine's latency varies by only 23%, against 43% for baseline methods.[^gaoCollaborativeSpeculativeInference]

### Online serving (LLaMA pair)

| Arrival rate mode | CoSine latency vs SpecInfer |
|---|---|
| Low | 1.2x-1.5x lower |
| High | 1.3x-1.6x lower |
| Fluctuated | 1.2x-1.4x lower |

All rows: [^gaoCollaborativeSpeculativeInference]

### Cost efficiency (Table 3)

The paper does not state the unit or the reference of the percentages. The column labels are copied as printed.[^gaoCollaborativeSpeculativeInference]

| Mode | SpecInfer LLM | SpecInfer Qwen | PipeInfer LLM | PipeInfer Qwen | CoSine LLM | CoSine Qwen |
|---|---|---|---|---|---|---|
| Low | 43.34% | 47.79% | 33.23% | 38.57% | 29.98% | 34.34% |
| High | 36.87% | 41.8% | 26.18% | 30.19% | 21.18% | 26.36% |
| Volatile | 38.01% | 42.87% | 28.61% | 33.07% | 25.71% | 30.63% |

All rows: [^gaoCollaborativeSpeculativeInference]

### Ablation

- Without the cooperative generation mechanism, throughput is 29-33% lower than full CoSine (8 devices: 1.18 vs. 1.72).[^gaoCollaborativeSpeculativeInference]
- Without confidence-based token fusion, throughput is 17-34% lower (8 devices: 1.13 vs. 1.72).[^gaoCollaborativeSpeculativeInference]

## Limitations

- The paper has no limitations section and states no limitations of CoSine.
- Internal inconsistencies in the source: the abstract reports up to 23.2% latency reduction, and Section 6.2 reports up to 27.1%.[^gaoCollaborativeSpeculativeInference]
- The online tests are described as running "over 2 hours" in the setup and "across 240 miuntes" in Section 6.3.[^gaoCollaborativeSpeculativeInference]
- The text gives the drafter acceptance range as 1.73 to 3.20, and Table 2 has a minimum of 1.69.[^gaoCollaborativeSpeculativeInference]
- The implementation section names TinyLlama-1.1B and Phi-2 drafters and a Llama-2-70B verifier, and the evaluation section names LLaMA68M and Qwen2.5-0.5B drafters with DeepSeek-R1-Distill targets.[^gaoCollaborativeSpeculativeInference]
- The conclusion mentions theoretical analysis, and the paper contains no theorem or proof.[^gaoCollaborativeSpeculativeInference]
- Publication year and venue are not stated in the extracted text.

## Related

- Proposed system: [CoSine](../methods/cosine.md)
- Methods it builds on: [Speculative decoding](../methods/speculative-decoding.md), [Token tree verification](../methods/token-tree-verification.md), [Continuous batching](../methods/continuous-batching.md), [LLM ensemble](../methods/llm-ensemble.md)
- Systems compared: [vLLM](../methods/vllm.md), [SpecInfer](../methods/specinfer.md), [PipeInfer](../methods/pipeinfer.md)
- Related methods discussed: [EAGLE-2](../methods/eagle-2.md), [Medusa](../methods/medusa.md)
- Datasets: [PIQA](../datasets/piqa.md), [MedQA](../datasets/medqa.md), [FIQA](../datasets/fiqa.md), [Alpaca](../datasets/alpaca.md), [OASST2](../datasets/oasst2.md)

[^gaoCollaborativeSpeculativeInference]: Gao et al. (year not stated)
