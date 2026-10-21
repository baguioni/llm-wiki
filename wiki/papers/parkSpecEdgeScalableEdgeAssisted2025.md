---
type: Paper
title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
description: Edge-assisted LLM serving framework that splits speculative decoding into drafting on consumer-grade edge GPUs and verification on server GPUs, with proactive edge drafting and pipeline-aware server scheduling.
tags: [speculative-decoding, edge-inference, llm-serving, split-computing, cost-efficiency, scheduling, mobile-specedge]
collections: [mobile-specedge]
authors: [Jinwoo Park, Seunggeun Cho, Dongsu Han]
doi: 10.48550/arXiv.2505.17052
arxiv: "2505.17052"
arxiv_version: 2505.17052v2
code: https://github.com/kaist-ina/specedge
sources:
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs

Text source: arXiv HTML, version `2505.17052v2`.

## Summary

Current server-centric LLM serving systems overlook consumer-grade GPUs at the edge.[^parkSpecEdgeScalableEdgeAssisted2025] The paper states that the GeForce RTX 4090 delivers up to 330.3 TFLOPS for FP16 tensor operations, exceeding the 312 TFLOPS of the A100, at 14.43x lower cost, and that edge devices like the RTX 4090 and RTX 3090 generate tokens at approximately 30-50× lower cost than server-class GPUs when running a small model like Qwen2-0.5B.[^parkSpecEdgeScalableEdgeAssisted2025] Existing parallelization techniques such as tensor and pipeline parallelism rely on high-bandwidth, low-latency interconnects and break down over wide-area networks.[^parkSpecEdgeScalableEdgeAssisted2025]

SpecEdge is an edge-assisted inference framework that splits [speculative decoding](../methods/speculative-decoding.md) into *edge drafting* and *server verification*, exchanging only token outputs over the network.[^parkSpecEdgeScalableEdgeAssisted2025] Two techniques make this practical: *proactive edge drafting*, which overlaps edge token creation with server verification, and *pipeline-aware scheduling*, which interleaves multiple user requests on the server.[^parkSpecEdgeScalableEdgeAssisted2025] The paper reports 1.91× better cost efficiency through 2.22× server throughput, and an 11.24% reduction in inter token latency, compared to a server-only baseline.[^parkSpecEdgeScalableEdgeAssisted2025]

## Contributions

- Disaggregated LLM decoding: token drafting is offloaded to edge GPUs while verification stays on the server, which the paper presents as the first practical edge-assisted inference framework of this kind.[^parkSpecEdgeScalableEdgeAssisted2025]
- Proactive edge drafting, which continues draft generation during server verification to mask network and verification latency.[^parkSpecEdgeScalableEdgeAssisted2025]
- Server-side pipeline-aware scheduling, which batches verification requests from multiple users to keep the server GPU utilized.[^parkSpecEdgeScalableEdgeAssisted2025]
- An evaluation over a wide-area network with a server-side A100 and edge-side RTX 4090 GPUs.[^parkSpecEdgeScalableEdgeAssisted2025]

## Method

### Why not conventional split computing

[Layer-wise split computing](../methods/split-computing.md) divides neural network layers between server and edge. The paper names two limitations for LLMs:[^parkSpecEdgeScalableEdgeAssisted2025]

- **Excessive latency.** LLMs need communication for every generated token because they are autoregressive. In the paper's distributed network setting, layer-wise splitting increases latency by 2.35x compared to the server-only solution.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Ineffectiveness in reducing I/O.** LLM inference is constrained by memory I/O, since generating one token requires accessing all model parameters. Offloading layers does not change this. Batch-verifying multiple candidate tokens reduces the I/O overhead per token.[^parkSpecEdgeScalableEdgeAssisted2025]

### Disaggregated LLM decoding

- The edge GPU generates candidate tokens and sends them to the server, which verifies them in a single forward pass.[^parkSpecEdgeScalableEdgeAssisted2025]
- The server returns the verified tokens and one additional token. The edge updates its sequence and KV cache and continues drafting. The cycle repeats until an end-of-sequence token.[^parkSpecEdgeScalableEdgeAssisted2025]
- The output distribution of the server model is preserved exactly.[^parkSpecEdgeScalableEdgeAssisted2025]
- Draft stages account for the majority of the draft-verify cycle across batch sizes, so offloading them reduces server time.[^parkSpecEdgeScalableEdgeAssisted2025]
- Two challenges follow from the split: a potential latency increase from network round trips in each cycle, and server underutilization while waiting for edge drafting.[^parkSpecEdgeScalableEdgeAssisted2025]

### Proactive edge drafting

- **Initial drafting.** SpecEdge uses tree-based drafting from [SpecExec](../methods/specexec.md). The design is not tied to a specific drafting technique.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Proactive drafting.** After sending $n$ candidate tokens, the edge keeps drafting without waiting for the verification result.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Complete draft alignment.** If all $n$ tokens are accepted and the server's bonus token matches the first proactively drafted token, the proactive tokens are used immediately. If any token is rejected, they are discarded.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Expected gain.** With $P_{\text{align}}$ the probability of alignment, $P_{\text{match | align}}$ the probability that the server's extra token matches an expansion head given alignment, $T_{\text{draft}}$ the total number of proactively drafted tokens, and $H_{\text{expan}}$ the number of expansion heads:[^parkSpecEdgeScalableEdgeAssisted2025]

$$
\mathbb{E}(\text{Gain})=P_{\text{align}}\cdot P_{\text{match | align}}\cdot\left(\frac{T_{\text{draft}}}{H_{\text{expan}}}-1\right)
$$

- **Single expansion head.** More heads raise $P_{\text{align}}$ but lower the token preservation ratio. Treating every leaf as an expansion head yields negligible gains. SpecEdge picks the single path with the highest cumulative log probability and continues drafting only from that node.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Post-verification update.** On complete alignment, the matching branch is kept and drafting continues from the advanced position, which gives a deeper draft for the next round. Otherwise the proactive work is discarded and the tree is rebuilt from the end of the verified sequence.[^parkSpecEdgeScalableEdgeAssisted2025]

### Server-side pipeline-aware scheduling

- The server GPU is dedicated to verification. It verifies completed draft batches from one set of requests while other requests draft on their own edge devices.[^parkSpecEdgeScalableEdgeAssisted2025]
- The paper states that aligning the edge device count with server verification capacity effectively doubles server throughput compared to a server-only configuration of equivalent batch size.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Draft depth calibration.** Draft depth (the number of forward passes through the draft model) is adjusted from real-time measurements so that server verification time ≈ edge drafting time + network round-trip time.[^parkSpecEdgeScalableEdgeAssisted2025]
- **Heterogeneous requests.** Batches with different sequence lengths are handled with custom attention masking per sequence and KV cache padding to the longest sequence in the batch.[^parkSpecEdgeScalableEdgeAssisted2025]

## Experiments & Results

### Setup

- Hardware: a server-side NVIDIA A100 GPU and multiple edge-side NVIDIA RTX4090 GPUs over a wide-area network. The number of RTX4090 GPUs is batch size x 2. The measured average round-trip time between the edge node and the Google Cloud instance is 14.07ms.[^parkSpecEdgeScalableEdgeAssisted2025]
- Baselines: server-only tree-based speculative decoding (primary), autoregressive decoding, and a layer-split approach.[^parkSpecEdgeScalableEdgeAssisted2025]
- Pricing: A100 40GB at $4.05 per hour, A100 80GB (needed for the 32B model) at $5.05 per hour, and $0.35 per hour for each RTX 4090.[^parkSpecEdgeScalableEdgeAssisted2025]
- Metrics: cost efficiency (generated tokens per dollar), server throughput (generated tokens per unit time), and inter token latency.[^parkSpecEdgeScalableEdgeAssisted2025]
- Target models: Qwen3-32B/14B, Vicuna-33B, Llama2-13B-chat-hf. Temperature is 0.7 unless noted.[^parkSpecEdgeScalableEdgeAssisted2025]
- Draft models: Qwen3-1.7B/0.6B, Sheared Llama-1.3B (SL), Tiny Llama-1.1B (TL), JackFram-160M (JF). All models are off-the-shelf with no fine-tuning.[^parkSpecEdgeScalableEdgeAssisted2025]
- Data: [SpecBench](../benchmarks/spec-bench.md), [C4 (en)](../datasets/c4.md), [OpenAssistant conversations (OAsst)](../datasets/oasst.md), [WikiText-2](../datasets/wikitext-2.md), [MTBench](../datasets/mt-bench.md).[^parkSpecEdgeScalableEdgeAssisted2025]
- Draft tree: the tree construction follows [Sequoia](../methods/sequoia.md) and SpecExec, with draft tree size 32 per request. The server-only baseline uses the optimal draft tree depth found by exhaustive search.[^parkSpecEdgeScalableEdgeAssisted2025]
- Up to 256 output tokens are generated per query. Reported metrics cover output tokens after prefill.[^parkSpecEdgeScalableEdgeAssisted2025]

### End-to-end on SpecBench, batch size 1 (Table 1)

Averaged over this evaluation, SpecEdge achieves 1.91× better cost efficiency through a 2.22× throughput gain compared to the server-only setup.[^parkSpecEdgeScalableEdgeAssisted2025] It reduces inter token latency by an average of 11.24% compared to server-only speculative decoding across batch sizes.[^parkSpecEdgeScalableEdgeAssisted2025]

| Target/Draft | Task | Gen. tokens per verify: Server-only | SpecEdge | Server throughput (tok/s): Server-only | SpecEdge | Cost efficiency (1k toks/$): Server-only | SpecEdge |
|---|---|---|---|---|---|---|---|
| Qwen3 14B/1.7B | Multi-turn bench | 3.92±1.51 | 3.98±1.57 | 31.78 | 66.54 (2.09x) | 28.25 | 50.60 (1.79x) |
| Qwen3 14B/1.7B | Translation | 3.95±1.47 | 4.25±1.45 | 32.24 | 65.25 (2.02x) | 28.66 | 49.47 (1.73x) |
| Qwen3 14B/1.7B | Summarization | 3.73±1.60 | 3.95±1.61 | 29.70 | 67.53 (2.27x) | 26.40 | 51.22 (1.94x) |
| Qwen3 14B/1.7B | QA | 3.42±1.57 | 3.59±1.56 | 27.30 | 62.04 (2.27x) | 24.26 | 47.09 (1.94x) |
| Qwen3 14B/1.7B | Math. | 4.10±1.48 | 4.25±1.49 | 32.84 | 72.93 (2.22x) | 29.19 | 55.28 (1.89x) |
| Qwen3 14B/1.7B | RAG | 3.73±1.53 | 3.83±1.56 | 29.89 | 64.04 (2.14x) | 26.57 | 48.78 (1.84x) |
| Qwen3 14B/0.6B | Multi-turn bench | 3.87±1.41 | 4.41±2.25 | 33.45 | 69.58 (2.08x) | 29.73 | 52.97 (1.78x) |
| Qwen3 14B/0.6B | Translation | 3.79±1.48 | 4.67±2.34 | 32.88 | 69.00 (2.10x) | 29.22 | 52.23 (1.79x) |
| Qwen3 14B/0.6B | Summarization | 3.68±1.49 | 4.21±2.16 | 31.17 | 68.60 (2.20x) | 27.71 | 52.16 (1.88x) |
| Qwen3 14B/0.6B | QA | 3.33±1.41 | 3.79±1.94 | 28.89 | 61.90 (2.14x) | 25.68 | 46.98 (1.83x) |
| Qwen3 14B/0.6B | Math | 3.90±1.57 | 5.27±2.27 | 33.53 | 83.88 (2.50x) | 29.80 | 63.56 (2.13x) |
| Qwen3 14B/0.6B | RAG | 3.53±1.52 | 4.29±2.16 | 30.07 | 69.51 (2.31x) | 26.73 | 52.76 (1.97x) |
| Qwen3 32B/1.7B | Multi-turn bench | 4.22±1.93 | 4.71±2.66 | 24.96 | 56.47 (2.26x) | 17.80 | 35.38 (1.99x) |
| Qwen3 32B/1.7B | Translation | 4.08±1.97 | 5.24±2.84 | 24.33 | 58.79 (2.42x) | 17.34 | 36.83 (2.12x) |
| Qwen3 32B/1.7B | Summarization | 4.19±2.01 | 4.52±2.68 | 24.33 | 54.07 (2.42x) | 17.65 | 33.90 (2.12x) |
| Qwen3 32B/1.7B | QA | 3.62±1.95 | 3.93±2.49 | 21.59 | 46.14 (2.14x) | 15.39 | 28.99 (1.88x) |
| Qwen3 32B/1.7B | Math. | 4.60±1.93 | 5.40±2.78 | 27.52 | 64.01 (2.33x) | 19.62 | 40.18 (2.05x) |
| Qwen3 32B/1.7B | RAG | 3.89±2.05 | 4.19±2.69 | 22.67 | 49.46 (2.18x) | 16.16 | 31.05 (1.92x) |

All rows: [^parkSpecEdgeScalableEdgeAssisted2025]

Note: in the source, the Qwen3 32B/1.7B Summarization row repeats the Translation row's server-only throughput (24.33) and both ratios (2.42x, 2.12x). The values are copied as they appear.

### Other models and datasets, batch size 1 (Table 2)

| Target/Draft | Dataset | Gen. tokens per verify: Server-only | SpecEdge | Server throughput (tok/s): Server-only | SpecEdge | Cost efficiency (1k toks/$): Server-only | SpecEdge |
|---|---|---|---|---|---|---|---|
| Vicuna 33B/SL 1.3B | C4 | 3.47±1.41 | 4.41±2.03 | 28.12 | 49.96 (1.78x) | 24.99 | 38.23 (1.53x) |
| Vicuna 33B/SL 1.3B | OAsst | 3.55±1.37 | 4.35±2.06 | 28.72 | 49.94 (1.74x) | 25.53 | 37.89 (1.48x) |
| Vicuna 33B/SL 1.3B | WikiText-2 | 3.42±1.45 | 4.19±1.98 | 27.26 | 47.94 (1.76x) | 24.23 | 36.42 (1.50x) |
| Vicuna 33B/SL 1.3B | MTBench | 3.62±1.72 | 4.57±2.13 | 29.62 | 52.70 (1.78x) | 26.33 | 40.21 (1.53x) |
| Llama2 13B/TL 1.1B | C4 | 3.40±1.35 | 3.48±1.34 | 36.80 | 70.76 (1.92x) | 32.72 | 53.72 (1.64x) |
| Llama2 13B/TL 1.1B | OAsst | 3.57±1.40 | 3.67±1.39 | 38.55 | 69.49 (1.80x) | 34.27 | 52.75 (1.54x) |
| Llama2 13B/TL 1.1B | WikiText-2 | 3.52±1.37 | 3.61±1.40 | 37.69 | 70.21 (1.86x) | 33.50 | 53.30 (1.59x) |
| Llama2 13B/TL 1.1B | MTBench | 3.67±1.43 | 3.75±1.46 | 40.96 | 76.69 (1.87x) | 36.41 | 58.21 (1.60x) |
| Llama2 13B/JF 160M | C4 | 3.03±1.34 | 3.13±1.37 | 42.72 | 66.20 (1.55x) | 37.98 | 50.36 (1.33x) |
| Llama2 13B/JF 160M | OAsst | 2.79±1.37 | 2.85±1.37 | 39.19 | 56.52 (1.44x) | 34.84 | 42.95 (1.23x) |
| Llama2 13B/JF 160M | WikiText-2 | 2.72±1.37 | 2.72±1.39 | 37.87 | 55.39 (1.46x) | 33.66 | 42.08 (1.25x) |
| Llama2 13B/JF 160M | MTBench | 2.80±1.39 | 2.80±1.43 | 40.80 | 60.42 (1.48x) | 36.42 | 45.92 (1.26x) |

All rows: [^parkSpecEdgeScalableEdgeAssisted2025]

### Inter token latency and speedup over autoregressive decoding (Table 3)

| Target/Draft | Dataset | ITL (ms): Server-only | SpecEdge | Speedup: Server-only | SpecEdge |
|---|---|---|---|---|---|
| Vicuna 33B/SL 1.3B | C4 | 33.229 | 30.612 | 1.86x | 2.02x |
| Vicuna 33B/SL 1.3B | OAsst | 34.496 | 30.460 | 1.76x | 2.00x |
| Vicuna 33B/SL 1.3B | WikiText-2 | 34.77 | 30.631 | 1.69x | 1.92x |
| Vicuna 33B/SL 1.3B | MTBench | 33.948 | 31.168 | 1.82x | 1.98x |
| Llama2 13B/TL 1.1B | C4 | 23.687 | 21.851 | 1.63x | 1.76x |
| Llama2 13B/TL 1.1B | OAsst | 24.661 | 22.377 | 1.54x | 1.70x |
| Llama2 13B/TL 1.1B | WikiText-2 | 23.883 | 21.338 | 1.59x | 1.78x |
| Llama2 13B/TL 1.1B | MTBench | 23.136 | 21.463 | 1.66x | 1.79x |
| Llama2 13B/JF 160M | C4 | 20.6 | 19.007 | 1.87x | 2.03x |
| Llama2 13B/JF 160M | OAsst | 23.711 | 22.378 | 1.60x | 1.70x |
| Llama2 13B/JF 160M | WikiText-2 | 26.222 | 24.579 | 1.45x | 1.54x |
| Llama2 13B/JF 160M | MTBench | 23.458 | 22.199 | 1.64x | 1.73x |

All rows: [^parkSpecEdgeScalableEdgeAssisted2025]

### Component-wise benefit

- Offloading drafting reduces server runtime by approximately 40-50% in all model configurations.[^parkSpecEdgeScalableEdgeAssisted2025]
- Ablation with the 14B/1.7B pair: basic disaggregation achieves 32.76 tokens/s throughput with higher latency. Adding proactive drafting reduces inter token latency to 28 ms. Complete SpecEdge with pipeline-aware scheduling raises server throughput to 67.89 tok/s (2.07× improvement) while maintaining latency.[^parkSpecEdgeScalableEdgeAssisted2025]
- Generated tokens per verification: SpecEdge is 13.21% higher on average. For 32B-1.7B, 4.5 tokens against 4.02 server-only. For 14B-0.6B, 4.45 against 3.66.[^parkSpecEdgeScalableEdgeAssisted2025]
- Draft depth adjustment (32B/1.7B): verification takes 94.2 ms on average and each draft model forward pass about 11 ms. SpecEdge sets the draft depth to seven at 15 ms RTT, five at 40 ms RTT, and four at 50 ms RTT.[^parkSpecEdgeScalableEdgeAssisted2025]

### Network RTT sensitivity (Qwen 32B on SpecBench)

The layer-split configuration runs autoregressive decoding with one-quarter of the model layers on an edge RTX4090 and the rest on a server-side A100.[^parkSpecEdgeScalableEdgeAssisted2025]

| RTT | SpecEdge ITL | Server-only ITL | Layer-split ITL | Stated comparison |
|---|---|---|---|---|
| 15 ms | 36.47 ms | 42.36 ms | 99.63 ms | 13.90% gain over server-only; layer-split 2.73× slower than SpecEdge |
| 50 ms | 40.26 ms | not stated | 134.90 ms | layer-split 3.35× slower than SpecEdge |
| 65 ms | 44.47 ms | not stated | not stated | SpecEdge latency rises by 22.00% over its 15 ms RTT performance |

All rows: [^parkSpecEdgeScalableEdgeAssisted2025]

SpecEdge gives lower inter token latency than the server-only baseline below 50 ms RTT. The server-only configuration is unaffected by network RTT.[^parkSpecEdgeScalableEdgeAssisted2025]

### Lighter edge GPUs (Table 4)

| Target/Draft | Edge GPU | Peak FP16 TFLOPS | Memory bandwidth (GB/s) | Inter token latency (ms) | Server throughput (tok/s) |
|---|---|---|---|---|---|
| Qwen3-14B/1.7B | RTX 3060 Ti | 16.20 | 448.0 | 36.818 | 50.297 |
| Qwen3-14B/1.7B | RTX 2080 Ti | 26.90 | 616.0 | 34.409 | 54.657 |
| Qwen3-14B/1.7B | Server-only (A100 40GB) | 312 | 1555 | 32.451 | 30.816 |
| Qwen3-14B/0.6B | RTX 3060 Ti | 16.20 | 448.0 | 36.818 | 56.135 |
| Qwen3-14B/0.6B | RTX 2080 Ti | 26.90 | 616.0 | 34.409 | 54.657 |
| Qwen3-14B/0.6B | Server-only (A100 40GB) | 312 | 1555 | 32.326 | 30.935 |

All rows: [^parkSpecEdgeScalableEdgeAssisted2025]

Note: in the source, the inter token latencies are identical across the two draft models for each edge GPU, and the RTX 2080 Ti throughput is identical in both blocks. The values are copied as they appear. In this table SpecEdge with these lighter GPUs has higher inter token latency than the server-only rows.[^parkSpecEdgeScalableEdgeAssisted2025]

### Non-tree speculative decoding (Tables 5 and 6)

SpecEdge with the linear-sequence speculative decoding of Leviathan et al. (2023):[^parkSpecEdgeScalableEdgeAssisted2025]

| Target/Draft | Server throughput (tokens/s): Server-only | SpecEdge | Cost efficiency (1k tokens/$): Server-only | SpecEdge | ITL (ms): Server-only | SpecEdge | Speedup: Server-only | SpecEdge |
|---|---|---|---|---|---|---|---|---|
| Vicuna 33B/SL 1.3B | 24.527 | 39.370 (1.61x) | 17.484 | 24.649 (1.41x) | 40.771 | 38.067 | 1.61x | 1.72x |
| Llama2 13B/TL 1.1B | 33.044 | 64.851 (1.96x) | 29.372 | 49.150 (1.67x) | 30.263 | 26.085 | 1.40x | 1.62x |
| Llama2 13B/JF 160M | 32.755 | 49.639 (1.52x) | 29.116 | 37.621 (1.29x) | 30.530 | 30.818 | 1.38x | 1.37x |

All rows: [^parkSpecEdgeScalableEdgeAssisted2025]

### Batch drafting on one edge GPU (Table 7)

A single RTX 4090 drafts for multiple concurrent requests. Percentages are the source's comparison against the default one-GPU-per-request deployment.[^parkSpecEdgeScalableEdgeAssisted2025]

| Target/Draft | Batch size | Inter token latency (ms) | Cost efficiency (1k toks/$) |
|---|---|---|---|
| Qwen3-14B/1.7B | 2 | 31.777 (6.8% slower) | 67.299 (14.7% better) |
| Qwen3-14B/1.7B | 3 | 36.617 (13.0% slower) | 71.369 (29.5% better) |
| Qwen3-14B/1.7B | 4 | 40.099 (16.7% slower) | 85.662 (24.5% better) |
| Qwen3-14B/0.6B | 2 | 30.494 (8.5% slower) | 67.680 (5.8% better) |
| Qwen3-14B/0.6B | 3 | 34.028 (15.2% slower) | 80.252 (12.0% better) |
| Qwen3-14B/0.6B | 4 | 39.035 (19.0% slower) | 82.376 (20.0% better) |
| Qwen3-32B/1.7B | 2 | 43.539 (5.9% slower) | 51.245 (4.4% better) |
| Qwen3-32B/1.7B | 3 | 48.889 (3.9% slower) | 59.635 (21.3% better) |
| Qwen3-32B/1.7B | 4 | 58.402 (9.5% slower) | 57.857 (25.1% better) |

All rows: [^parkSpecEdgeScalableEdgeAssisted2025]

### Reasoning mode (Table 8)

| Target/Draft | Accepted tokens: Non-reasoning | Reasoning | Server throughput (tok/s): Non-reasoning | Reasoning | Cost efficiency (1k toks/$): Non-reasoning | Reasoning |
|---|---|---|---|---|---|---|
| Qwen3-14B/1.7B | 3.80±1.54 | 4.17±1.39 | 64.343 | 72.249 | 48.883 | 54.898 |
| Qwen3-14B/0.6B | 3.68±1.50 | 4.10±1.36 | 70.703 | 81.890 | 53.693 | 62.157 |
| Qwen3-32B/1.7B | 4.09±1.95 | 4.62±1.90 | 24.880 | 27.617 | 39.430 | 43.373 |

All rows: [^parkSpecEdgeScalableEdgeAssisted2025]

### Cost efficiency across providers (Tables 9-11)

GPU pricing ($/hr): RTX 4090 at RunPod 0.69, Vast.ai 0.35, TensorDock 0.359. RTX Pro 6000 at Vast.ai 1.08, TensorDock 1.15. A100 40GB at Google Cloud Platform 4.05, Amazon Web Services 4.10. A100 80GB at Google Cloud Platform 5.05, Amazon Web Services 5.12, Microsoft Azure 3.673.[^parkSpecEdgeScalableEdgeAssisted2025]

Cost efficiency (1k toks/$) by server cloud provider:[^parkSpecEdgeScalableEdgeAssisted2025]

| Target/Draft | Server/Edge GPU | Edge GPU provider | Google Cloud Platform | Amazon Web Service | Microsoft Azure |
|---|---|---|---|---|---|
| Qwen3-14B/1.7B | A100 40GB / RTX 4090 | Vast.ai | 51.018 (1.87×) | 50.485 (1.87×) | - |
| Qwen3-14B/1.7B | A100 40GB / RTX 4090 | RunPod | 44.721 (1.64×) | 44.311 (1.65×) | - |
| Qwen3-14B/1.7B | A100 40GB / RTX 4090 | TensorDock | 50.829 (1.87×) | 50.30 (1.87×) | - |
| Qwen3-14B/1.7B | A100 40GB / RTX 4090 | Baseline (Server-only) | 27.222 | 26.890 | - |
| Qwen3-14B/1.7B | A100 40GB / RTX Pro 6000 | Vast.ai | 47.68 (1.75×) | 47.30 (1.76×) | - |
| Qwen3-14B/1.7B | A100 40GB / RTX Pro 6000 | TensorDock | 46.64 (1.71×) | 46.27 (1.72×) | - |
| Qwen3-14B/1.7B | A100 40GB / RTX Pro 6000 | Baseline (Server-only) | 27.222 | 26.890 | - |
| Qwen3-14B/0.6B | A100 40GB / RTX 4090 | Vast.ai | 52.938 (1.86×) | 52.386 (1.88×) | - |
| Qwen3-14B/0.6B | A100 40GB / RTX 4090 | RunPod | 46.382 (1.63×) | 45.957 (1.65×) | - |
| Qwen3-14B/0.6B | A100 40GB / RTX 4090 | TensorDock | 52.741 (1.86×) | 52.192 (1.88×) | - |
| Qwen3-14B/0.6B | A100 40GB / RTX 4090 | Baseline (Server-only) | 28.415 | 27.802 | - |
| Qwen3-32B/1.7B | A100 80GB / RTX 4090 | Vast.ai | 31.619 (1.82×) | 31.332 (1.83×) | 41.757 (1.75×) |
| Qwen3-32B/1.7B | A100 80GB / RTX 4090 | RunPod | 28.453 (1.64×) | 28.144 (1.65×) | 36.280 (1.52×) |
| Qwen3-32B/1.7B | A100 80GB / RTX 4090 | TensorDock | 31.619 (1.82×) | 31.239 (1.83×) | 41.591 (1.75×) |
| Qwen3-32B/1.7B | A100 80GB / RTX 4090 | Baseline (Server-only) | 17.330 | 17.090 | 23.822 |

### Other edge devices

SpecEdge gives a speedup over autoregressive decoding on the A100 with each tested edge GPU (RTX 4090, 4070 Ti Super, 3090, and 2080 Ti) across three target-draft combinations, with larger speedups from more powerful edge GPUs. The values are shown only in a figure.[^parkSpecEdgeScalableEdgeAssisted2025]

## Limitations

- The cost-efficiency analysis covers consumer-grade GPUs rented from edge cloud providers, not user-owned GPUs.[^parkSpecEdgeScalableEdgeAssisted2025]
- Fault tolerance and security when untrusted devices take part in computation are named as new challenges and left to future work.[^parkSpecEdgeScalableEdgeAssisted2025]
- The evaluation covers models with parameters up to 33B. Larger models are planned as future work.[^parkSpecEdgeScalableEdgeAssisted2025]
- The default deployment needs RTX4090 GPUs numbering batch size x 2. Sharing one edge GPU across requests improves cost efficiency (4.4% to 29.5% better) but raises inter token latency (5.9% to 19.0% slower, as stated in the text).[^parkSpecEdgeScalableEdgeAssisted2025]
- The latency advantage over the server-only baseline holds below 50 ms RTT.[^parkSpecEdgeScalableEdgeAssisted2025]
- When complete draft alignment fails, the proactive work is discarded.[^parkSpecEdgeScalableEdgeAssisted2025]
- Reported metrics exclude prefill. The paper argues time to first token is comparable to the baseline because prefill latency is max(server_time, edge_time), and reports no measurement of it.[^parkSpecEdgeScalableEdgeAssisted2025]

# Contradictions

The ablation above finds that proactive drafting reduces inter token latency (to 28 ms with Qwen3 14B/1.7B on RTX 4090 edges).[^parkSpecEdgeScalableEdgeAssisted2025] HyCo re-implements a SpecEdge-style tree (four Gemma 4 E2B passes, 32 nodes) on a Galaxy S26 Ultra NPU over LTE/5G and finds that proactive drafting raises server saving on Spec-Bench (20.6% to 23.9% against server-side MTP) but lowers delivery speed from 16.1 to 12.1 tokens/s.[^baeHyCoHybridDrafting2026] Hardware, network, models, metric, and implementation all differ. See [Does proactive drafting help when the drafter runs on a phone?](../questions/proactive-drafting-on-a-phone.md).

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md), [SpecEdge](../methods/specedge.md), [Proactive edge drafting](../methods/proactive-edge-drafting.md), [Split computing](../methods/split-computing.md)
- Systems built on or compared: [SpecExec](../methods/specexec.md), [Sequoia](../methods/sequoia.md)
- Benchmarks: [SpecBench](../benchmarks/spec-bench.md), [MTBench](../datasets/mt-bench.md)
- Datasets: [C4](../datasets/c4.md), [OAsst](../datasets/oasst.md), [WikiText-2](../datasets/wikitext-2.md)
- Later work that builds on SpecEdge's server and uses a SpecEdge-style baseline on a phone: [HyCo](baeHyCoHybridDrafting2026.md)
- Papers in this wiki cited by this paper: [SpecExec](svirschevskiSpecExecMassivelyParallel2024.md), [Sheared LLaMA](xiaShearedLLaMAAccelerating2024.md)

[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
