---
type: Paper
title: "A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models"
description: HAT combines U-shaped split inference with speculative decoding, keeping the LLM's first layers, head, and a distilled adapter on the device as a draft model while the cloud runs the middle layers, and adds prompt chunking and parallel drafting to hide hidden-state transfer and drafting delays.
tags: [speculative-decoding, device-cloud-collaborative-inference, split-inference, u-shaped-inference, prompt-chunking, parallel-drafting, privacy, edge-inference, speculative-drafter]
collections: ["speculative drafter"]
authors: [Zuan Xie, Yang Xu, Hongli Xu, Yunming Liao, Zhiwei Yao]
doi: 10.48550/arXiv.2503.18989
arxiv: "2503.18989"
arxiv_version: 2503.18989v1
sources:
  - id: xieNovelHatShapedDeviceCloud2025
    resource: zotero://select/items/@xieNovelHatShapedDeviceCloud2025
    title: "A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models"
  - id: baeHyCoHybridDrafting2026
    resource: zotero://select/items/@baeHyCoHybridDrafting2026
    title: "HyCo: Hybrid Drafting for Cost-Efficient Mobile-Cloud Speculative Decoding"
---

# A Novel Hat-Shaped Device-Cloud Collaborative Inference Framework for Large Language Models

Text source: arXiv HTML, version `2503.18989v1`.

## Summary

The paper compares three device-cloud inference frameworks. A basic framework runs simple requests on an on-device small language model (SLM) and offloads complex ones to the cloud LLM. Device-cloud [speculative decoding](../methods/speculative-decoding.md) drafts on the device and verifies in the cloud, but shares input and output tokens with the cloud. [U-shaped inference](../methods/u-shaped-inference.md) keeps the input and output submodels on the device and so keeps raw tokens local, but it sends hidden states, which are much larger than tokens, at every decoding step.[^xieNovelHatShapedDeviceCloud2025]

[HAT](../methods/hat.md) combines U-shaped inference (for privacy) with speculative decoding (for delay). The device holds the LLM's shallow decoder layers and output head, plus a lightweight adapter distilled from the cloud-side middle submodel. Together these form the draft model. The cloud holds the middle decoder layers and verifies drafts by exchanging hidden states, not tokens, with the device. Two further mechanisms target delay: prompt chunking, which pipelines the upload and in-cloud processing of long prompts during prefill, and parallel drafting, which lets the device draft the next round while the cloud verifies the current one.[^xieNovelHatShapedDeviceCloud2025]

On a testbed of 30 NVIDIA Jetson devices (20 AGX Xavier, 10 AGX Orin) on WiFi and a server with 8 A6000 GPUs, HAT reduces TTFT by 41% to 54% and TBT by 41% to 77% compared to the baselines, which are U-shaped variants (U-shape, U-Medusa, U-Sarathi).[^xieNovelHatShapedDeviceCloud2025]

## Contributions

- HAT, a device-cloud collaborative inference framework that integrates U-shaped inference with speculative decoding.[^xieNovelHatShapedDeviceCloud2025]
- A prompt chunking mechanism for long prompts, with chunk sizes chosen dynamically per device from the state of the cloud and of the device.[^xieNovelHatShapedDeviceCloud2025]
- A parallel drafting mechanism that overlaps drafting of the next round with verification of the current one.[^xieNovelHatShapedDeviceCloud2025]
- An evaluation on a physical platform with 30 NVIDIA Jetson devices.[^xieNovelHatShapedDeviceCloud2025]

## Method

### Motivation experiments (Sec. II-C)

Setup: Vicuna on the Specbench dataset; a workstation with 8 NVIDIA A6000 GPUs as the cloud server; 3 NVIDIA Jetson AGX Orin devices. SD uses Vicuna-7B on the server and Vicuna-68M on a device. U-shaped inference puts the first 2 decoder layers and the head of Vicuna-7B on a device and the rest on the server. The cloud baseline forwards the request to the server-side Vicuna-7B.[^xieNovelHatShapedDeviceCloud2025]

- With a 128-token prompt, communication delay is more than 80% of the TTFT of U-shaped inference. Because hidden states are much larger than tokens, U-shaped inference has higher TTFT and TBT than both SD and cloud-based inference.[^xieNovelHatShapedDeviceCloud2025]
- In U-shaped inference, communication delay grows almost linearly with prompt length (128 to 2k tokens). The communication delay of a 512-token prompt is 4$\times$ that of a 128-token prompt. For a 2k-token prompt the TTFT is 3.57s, made of local computation 0.09s (2.5%), in-cloud computation 0.28s (7.8%), and communication 3.20s (89.6%).[^xieNovelHatShapedDeviceCloud2025]
- In a batch with one prefill request and nine decode requests, a 32-token prompt raises in-cloud computation delay by only 10.1% over a 1-token prompt. Above 512 tokens the delay grows almost linearly with prompt length.[^xieNovelHatShapedDeviceCloud2025]
- Chunking a 2k-token prompt over 64 consecutive batched steps: smaller chunks reduce total computation delay more, but TTFT grows faster. With a chunk size of 32, total delay drops by 82.3 ms and TTFT rises by approximately 6.6$\times$ over no chunking.[^xieNovelHatShapedDeviceCloud2025]

### Architecture

- Example with a 32-layer LLM: layers #0 and #1 and the head are on the device; the other 30 decoder layers are in the cloud. Drafting runs locally (device only); verification runs device to cloud to device. The shape of the path gives the name "top hat".[^xieNovelHatShapedDeviceCloud2025]
- Four modules: state monitoring, prompt chunking, speculative decoding, parallel drafting. The cloud batches requests from devices in prefill and decode together.[^xieNovelHatShapedDeviceCloud2025]

### State monitoring

The cloud tracks the batched token size $\mu^{t}$ and the in-cloud computation delay $\eta^{t}$ per round, and keeps a predictive function $g^{t}(\cdot)$ of computation delay against batched token size. Both are smoothed by moving averages with $\alpha$ (0.8 in the experiments): $\mu^{t}=\alpha\cdot\mu^{t-1}+(1-\alpha)\cdot\hat{\mu}^{t}$ and $g^{t}(\mu^{t})=\alpha\cdot g^{t-1}(\mu^{t})+(1-\alpha)\cdot\hat{\eta}^{t}$. Each device reports its drafting delay $\gamma^{t}_{i}$ and its upload and download bandwidths $\beta^{t}_{i,up}$, $\beta^{t}_{i,down}$, also as moving averages. The paper treats the overhead of this state collection as negligible.[^xieNovelHatShapedDeviceCloud2025]

### Prompt chunking

- The device splits a long prompt into chunks and processes them as a pipeline, so the upload of one chunk's hidden states overlaps with in-cloud computation and download of the previous chunk. Smaller chunks also reduce in-cloud delay for other devices in decode.[^xieNovelHatShapedDeviceCloud2025]
- Chunks that are too small accumulate computation delay that exceeds the communication delay. Chunks that are too large reduce parallelism.[^xieNovelHatShapedDeviceCloud2025]
- With pipeline-parallel inference over $P$ GPUs, the chunk size $X_{i}$ for device $i$ solves $\frac{X_{i}\cdot A}{\beta^{t}_{i,up}}=\frac{g^{t}(\mu^{t})+g^{t}(\mu^{t}+X_{i})}{P}$, where $A$ is the hidden-state size per token, $g^{t}(\mu^{t})$ approximates the maximum waiting delay, and $g^{t}(\mu^{t}+X_{i})$ is the computation delay of the chunk.[^xieNovelHatShapedDeviceCloud2025]

### Speculative decoding module

- Draft model: $w_{S}=H_{L}\circ\Lambda\circ w^{m}_{L}$, where $H_{L}$ is the LLM's output head, $w^{m}_{L}$ its first $m$ decoder layers ($m$ less than 10% of $n$), and $\Lambda$ the adapter. $\Lambda$ has the structure of a decoder layer's self-attention module, chosen because self-attention has fewer parameters and less computation delay than the feed-forward network.[^xieNovelHatShapedDeviceCloud2025]
- $\Lambda$ is trained by knowledge distillation to imitate the middle submodel. Following EAGLE, the loss is $Loss=L_{sl}(f^{L}_{i+1},f^{S}_{i+1})+w_{ce}L_{ce}(H_{L}(f^{L}_{i+1}),H_{L}(f^{S}_{i+1}))$, Smooth L1 on the pre-head hidden states plus cross-entropy, with $w_{ce}$ typically 0.1.[^xieNovelHatShapedDeviceCloud2025]
- Verification: the draft sequence goes through the shallow layers on the device; the shallow hidden states go to the cloud; the middle submodel produces deep hidden states; these return to the device, where the head produces the result. Draft tokens that match the LLM's result are accepted, and a new token is generated from the last accepted draft token.[^xieNovelHatShapedDeviceCloud2025]
- Adaptive draft length: drafting stops when the softmax probability of a draft token falls below a threshold $\eta$ (0.6 in the experiments).[^xieNovelHatShapedDeviceCloud2025]

### Parallel drafting

- Because the last draft token fell below the threshold, it has a relatively low probability of acceptance and may be corrected in verification. The device takes the top-k tokens from the last drafting step as candidates and, during verification, drafts a candidate sequence from each. If the corrected token from the cloud matches one of the top-k candidates, that candidate sequence is used in the next round.[^xieNovelHatShapedDeviceCloud2025]
- The cloud sets the number of parallel drafting steps so that drafting finishes before the verification result arrives, assuming no wait time in the cloud: $\lambda_{i}=\lfloor\frac{\frac{\mu_{i}\cdot A}{\beta^{t}_{i,up}}+g^{t}(\mu^{t})+\frac{\mu_{i}\cdot A}{\beta^{t}_{i,down}}}{\gamma^{t}_{i}}\rfloor$, with $\mu_{i}$ the draft length of device $i$ in the current round.[^xieNovelHatShapedDeviceCloud2025]

## Experiments & Results

### Setup

- Cloud: Intel Xeon Platinum 8358P CPU, 8 NVIDIA GeForce RTX A6000 GPUs, 512 GB RAM.[^xieNovelHatShapedDeviceCloud2025]
- Devices: 30 NVIDIA Jetson kits, 20 Jetson AGX Xavier and 10 Jetson AGX Orin.[^xieNovelHatShapedDeviceCloud2025]

| Device | AI performance | GPU | CPU | Memory |
|---|---|---|---|---|
| AGX Xavier | 32 TOPS | 512-core Volta | 8-core Carmel ARM 8 | 32 GB LPDDR4x |
| AGX Orin | 200 TOPS | 1792-core Ampere | 8-core Cortex ARM 8 | 32 GB LPDDR5 |

All rows: [^xieNovelHatShapedDeviceCloud2025]

- Software: Docker Swarm, PyTorch, MPI for device-server communication, FlashAttention and FlashInfer kernels for paged attention and continuous batching, NCCL for pipeline communication between GPUs.[^xieNovelHatShapedDeviceCloud2025]
- Compute heterogeneity: Jetson power modes change the number of working CPUs and CPU/GPU frequency. An AGX Orin in mode 0 infers 10$\times$ faster than an AGX Xavier in mode 1. Modes change randomly every 5 requests.[^xieNovelHatShapedDeviceCloud2025]
- Network: devices connect over WiFi routers, in three groups of 10 at 2m, 8m, and 14m from the routers. Measured with iperf3, uplink bandwidth is 5MB/s to 10MB/s and downlink 10MB/s to 15MB/s.[^xieNovelHatShapedDeviceCloud2025]
- Datasets and models: [SpecBench](../benchmarks/spec-bench.md) with Vicuna-7B (32 decoder layers, 32 attention heads, hidden size 4096), and [CNN/DM](../datasets/cnn-dailymail.md) (11490 news articles) with Vicuna-13B (40 decoder layers, 40 attention heads, hidden size 5120). In SpecBench, summarisation prompts average 877.3 tokens and translation prompts 82.5.[^xieNovelHatShapedDeviceCloud2025]

| Dataset | Avg prompt tokens | P90 | Std | Model |
|---|---|---|---|---|
| SpecBench | 351.2 | 891.0 | 397.3 | Vicuna-7B |
| CNN/DM | 1036.6 | 1772.0 | 511.8 | Vicuna-13B |

All rows: [^xieNovelHatShapedDeviceCloud2025]

- Split: first 2 layers of Vicuna-7B and first 3 layers of Vicuna-13B, with their heads, on the device.[^xieNovelHatShapedDeviceCloud2025]
- Baselines, all placed inside the U-shaped framework because of the paper's privacy focus:[^xieNovelHatShapedDeviceCloud2025]
  - **U-shape**: plain U-shaped split inference.[^xieNovelHatShapedDeviceCloud2025]
  - **U-Medusa**: [Medusa](../methods/medusa.md) with 4 heads deployed on the device with the input and output submodels, using tree verification of size 8.[^xieNovelHatShapedDeviceCloud2025]
  - **U-Sarathi**: Sarathi-Serve inside U-shape. The server chunks prompts, with chunk size 128 on SpecBench and 256 on CNN/DM.[^xieNovelHatShapedDeviceCloud2025]
- Both the U-Medusa heads and HAT's $\Lambda$ are trained on [ShareGPT](../datasets/sharegpt.md). Maximum generation length is 128 tokens.[^xieNovelHatShapedDeviceCloud2025]
- Metrics: TTFT, TBT, and SLA compliance rate. The prefill SLA is the delay per 128 prompt tokens and the decode SLA is the delay per 10 decode tokens.[^xieNovelHatShapedDeviceCloud2025]

### Overall delay (Figures 6 and 7, Poisson arrivals, pipeline length 4)

| Dataset | Rate (requests/s) | Metric | HAT | U-Sarathi | U-Medusa | U-shape |
|---|---|---|---|---|---|---|
| SpecBench | 6 | TTFT | 384.2ms | 609.2ms | 644.6ms | 646.2ms |
| SpecBench | 4 | TBT reduction by HAT | | 31.9% | 22.5% | 41.3% |
| CNN/DM | 4 | TTFT | 1027.4ms | 1750.6ms | 2214.8ms | 2140.8ms |
| CNN/DM | 4 | TBT reduction by HAT | | 40.8% | 77.2% | 74.7% |

All rows: [^xieNovelHatShapedDeviceCloud2025]

- On SpecBench, as the rate rises from 4 to 9 requests/s, TBT increases by 5.3% for HAT and 7.8% for U-Sarathi, against 64.5% for U-Medusa and 44% for U-shape. The paper attributes the stability of HAT and U-Sarathi to prompt chunking, and the instability of U-Medusa to tree verification overloading the server.[^xieNovelHatShapedDeviceCloud2025]

### In-cloud computation delay per GPU (Figure 8)

| Dataset | Statistic | HAT | U-Sarathi | U-Medusa | U-shape |
|---|---|---|---|---|---|
| SpecBench | Mean | 6.8ms | 6.5ms | 10.0ms | 8.4ms |
| SpecBench | Std | 1.3ms | 1.2ms | 8.1ms | 7.1ms |
| CNN/DM | Mean | 12.4ms | 11.9ms | 23.3ms | 18.9ms |
| CNN/DM | Std | 1.1ms | 3.4ms | 27.5ms | 24.6ms |

All rows: [^xieNovelHatShapedDeviceCloud2025]

### SLA compliance (Figures 9 and 10, pipeline length 1)

| Dataset | SLA | HAT | U-Sarathi | U-Medusa | U-shape |
|---|---|---|---|---|---|
| SpecBench | Prefill SLA 350ms, compliance | 100% | 76.8% | 78.8% | 86.6% |
| SpecBench | Decode SLA met by 50% of requests | 489.3ms | 565.0ms | 659.8ms | 786.1ms |
| CNN/DM | Prefill SLA 300ms, compliance | 100% | 64.7% | 68.9% | 76.3% |
| CNN/DM | Decode SLA met by 90% of requests | 1352.7ms | 1561.5ms | 3109.6ms | 3357.8ms |

All rows: [^xieNovelHatShapedDeviceCloud2025]

The paper notes that Sarathi chunks prompts but does not overlap transmission with computation, which gives it a longer prefill delay.[^xieNovelHatShapedDeviceCloud2025]

### Speculative decoding quality (Table IV, one device, no other devices)

Accept is the accept length; speedup is in decode phase relative to U-shape.[^xieNovelHatShapedDeviceCloud2025]

| Dataset | Method | Trained params | Accept | Speedup |
|---|---|---|---|---|
| SpecBench (Vicuna-7B) | U-shape | N/A | 1.00 | 1.00$\times$ |
| SpecBench (Vicuna-7B) | U-Medusa | 591M | 1.89 | 1.41$\times$ |
| SpecBench (Vicuna-7B) | HAT | 67M | 2.06 | 1.65$\times$ |
| CNN/DM (Vicuna-13B) | U-shape | N/A | 1.00 | 1.00$\times$ |
| CNN/DM (Vicuna-13B) | U-Medusa | 760M | 1.75 | 1.45$\times$ |
| CNN/DM (Vicuna-13B) | HAT | 105M | 1.98 | 1.60$\times$ |

All rows: [^xieNovelHatShapedDeviceCloud2025]

The paper states that U-Medusa's tree verification causes higher communication delay than HAT's threshold-based drafting.[^xieNovelHatShapedDeviceCloud2025]

### Ablation (Table V): speculative decoding (SD), prompt chunking (PC), parallel drafting (PD)

| Dataset | SD | PC | PD | TTFT (ms) | TBT (ms) |
|---|---|---|---|---|---|
| SpecBench (Vicuna-7B) | | | | 655.6 | 52.3 |
| SpecBench (Vicuna-7B) | | ✓ | | 384.0 | 39.4 |
| SpecBench (Vicuna-7B) | ✓ | | | 655.3 | 38.3 |
| SpecBench (Vicuna-7B) | ✓ | | ✓ | 657.9 | 33.8 |
| SpecBench (Vicuna-7B) | ✓ | ✓ | | 384.3 | 30.6 |
| SpecBench (Vicuna-7B) | ✓ | ✓ | ✓ | 384.2 | 26.4 |
| CNN/DM (Vicuna-13B) | | | | 1989.0 | 128.1 |
| CNN/DM (Vicuna-13B) | | ✓ | | 1038.7 | 74.2 |
| CNN/DM (Vicuna-13B) | ✓ | | | 1993.5 | 84.3 |
| CNN/DM (Vicuna-13B) | ✓ | | ✓ | 1992.1 | 74.9 |
| CNN/DM (Vicuna-13B) | ✓ | ✓ | | 1039.1 | 49.3 |
| CNN/DM (Vicuna-13B) | ✓ | ✓ | ✓ | 1039.9 | 43.5 |

All rows: [^xieNovelHatShapedDeviceCloud2025]

- The row with no strategy is U-shape inference. On SpecBench, SD reduces TBT by 26.8%; SD with PC reduces TTFT by 41.4% and TBT by 41.5%; adding PD reduces TBT by 49.5%. On CNN/DM, SD with PC and without PD reduces TBT by 61.5%.[^xieNovelHatShapedDeviceCloud2025]
- SD mainly lowers TBT, PC lowers TTFT (and also TBT), and PD lowers TBT further. PD alone on top of SD changes TBT from 38.3 to 33.8 ms on SpecBench and from 84.3 to 74.9 ms on CNN/DM.[^xieNovelHatShapedDeviceCloud2025]

### Pipeline length (Figures 11 and 12)

- TTFT and TBT of all approaches fall as the server's pipeline length grows. At pipeline length 1, requests accumulate in the server, and U-Sarathi's extra prefill steps give it high TTFT.[^xieNovelHatShapedDeviceCloud2025]

| Setting | Metric | HAT | U-Sarathi | U-Medusa | U-shape |
|---|---|---|---|---|---|
| SpecBench, pipeline length 1 | TTFT | 431.4ms | 1080.0ms | 727.1ms | 694.0ms |
| SpecBench, pipeline length 1 | TBT | 39.2ms | 67.5ms | 65.3ms | 88.6ms |
| CNN/DM, pipeline length 4 | TTFT reduction by HAT (stated as "about") | | 36.9% | 40.7% | 40.1% |
| CNN/DM, pipeline length 4 | TBT reduction by HAT (stated as "about") | | 32.3% | 33.9% | 47.1% |

All rows: [^xieNovelHatShapedDeviceCloud2025]

## Limitations

- All baselines are U-shaped variants. The paper does not report HAT against token-level device-cloud speculative decoding or against cloud-only inference in the main evaluation; those appear only in the preliminary experiment of Figure 1(a).[^xieNovelHatShapedDeviceCloud2025]
- Accuracy is claimed as "promising" but no output-quality metric is reported. Acceptance is by matching the LLM's inference result.[^xieNovelHatShapedDeviceCloud2025]
- The privacy argument is that raw input and output tokens stay on the device; the paper does not evaluate leakage from the transmitted hidden states.[^xieNovelHatShapedDeviceCloud2025]
- Parallel drafting covers only the case where the last draft token is corrected to one of the top-k candidates. The paper does not state what happens when an earlier draft token is rejected or how often the candidate sequence is used.[^xieNovelHatShapedDeviceCloud2025]
- The parallel drafting step count assumes no wait time in the cloud.[^xieNovelHatShapedDeviceCloud2025]
- Devices are Jetson AGX boards with GPUs over WiFi, and maximum generation length is 128 tokens. Energy is not measured.[^xieNovelHatShapedDeviceCloud2025]

## Related

- Methods: [HAT](../methods/hat.md), [Speculative decoding](../methods/speculative-decoding.md), [U-shaped inference](../methods/u-shaped-inference.md), [Split computing](../methods/split-computing.md), [Chunked prefill](../methods/chunked-prefill.md), [Continuous batching](../methods/continuous-batching.md), [Knowledge distillation](../methods/knowledge-distillation.md)
- Systems compared or built on: [Medusa](../methods/medusa.md), [EAGLE](../methods/eagle.md) (source of the distillation loss), [Tree-based speculation](../methods/tree-based-speculation.md), Sarathi-Serve
- Datasets and benchmarks: [Spec-Bench](../benchmarks/spec-bench.md), [CNN/Daily Mail](../datasets/cnn-dailymail.md), [ShareGPT](../datasets/sharegpt.md)
- Other device-server drafting papers in this wiki: [SpecEdge](parkSpecEdgeScalableEdgeAssisted2025.md) (proactive edge drafting during server verification), [HyCo](baeHyCoHybridDrafting2026.md) (phone runs the verifier's MTP head; it lists HAT as drafting on the device with the LLM's first layers[^baeHyCoHybridDrafting2026]), [Speculative Speculative Decoding](kumarSpeculativeSpeculativeDecoding2026.md) (drafting in parallel with verification), [CoSine](gaoCollaborativeSpeculativeInference.md)

## Open questions and results

- [Can a block drafter pre-draft with stale target features?](../questions/pre-drafting-with-stale-target-features.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)

[^xieNovelHatShapedDeviceCloud2025]: Xie et al. 2025
[^baeHyCoHybridDrafting2026]: Bae et al. 2026
