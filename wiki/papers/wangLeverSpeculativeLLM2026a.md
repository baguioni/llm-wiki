---
type: Paper
title: "Lever: Speculative LLM Inference on Smartphones"
description: Speculative decoding system for smartphones that keeps a small draft model in DRAM and streams a flash-resident target model, with gain-per-latency token tree construction, early-exit pruning of the verification tree, and CPU-NPU split execution.
tags: [speculative-decoding, tree-based-speculation, on-device-inference, mobile-npu, flash-offloading, early-exit, speculative-drafter]
collections: ["speculative drafter"]
authors: [Tuowei Wang, Fengzu Li, Yanfan Sun, Wei Gao, Ju Ren]
doi: 10.48550/arXiv.2605.16786
arxiv: "2605.16786"
arxiv_version: 2605.16786v1
sources:
  - id: wangLeverSpeculativeLLM2026a
    resource: zotero://select/items/@wangLeverSpeculativeLLM2026a
    title: "Lever: Speculative LLM Inference on Smartphones"
---

# Lever: Speculative LLM Inference on Smartphones

Text source: arXiv HTML, version `2605.16786v1`.

## Summary

Smartphone DRAM is too small for high-quality LLMs, so the target model's weights can be kept in flash, but flash-backed autoregressive decoding reloads the weights for every token and I/O dominates latency.[^wangLeverSpeculativeLLM2026a] The paper argues that [speculative decoding](../methods/speculative-decoding.md) fits this setting: a small draft model stays resident in DRAM, and the flash-resident target model is invoked only to verify several candidate tokens at once, so the flash I/O is amortized over several output tokens.[^wangLeverSpeculativeLLM2026a]

[Lever](../methods/lever.md) adapts the three stages of speculative decoding to phones. Drafting builds a token tree that maximizes expected output tokens per unit cycle latency, with costs that include flash I/O. Verification prunes low-value branches with an early-exit predictor at an intermediate target layer. Execution splits work between the CPU and the NPU: small draft expansions on the CPU, batched draft expansions and the target's transformer layers on the NPU, and the output projection on the CPU only along the accepted path.[^wangLeverSpeculativeLLM2026a]

On three Snapdragon phones, four target models, and four datasets (48 configurations), Lever reaches a geometric-mean decode speedup of 2.93$\times$ over flash-backed autoregressive decoding, 1.50$\times$ over chain speculative decoding, and 1.27$\times$ over EdgeLLM.[^wangLeverSpeculativeLLM2026a]

## Contributions

- Identifies speculative decoding as an opportunity for mobile DRAM-flash LLM inference and names the system-level challenges in drafting, verification, and execution.[^wangLeverSpeculativeLLM2026a]
- Lever, a system that combines mobile-optimized token tree construction, predictor-based verification pruning, and CPU-NPU hybrid execution for flash-backed LLM inference on smartphones.[^wangLeverSpeculativeLLM2026a]
- An evaluation that shows latency reductions over flash-backed inference and over conventional speculative decoding.[^wangLeverSpeculativeLLM2026a]

## Method

### Motivation measurements (OnePlus 12, Snapdragon 8 Gen 3)

The paper states that mobile DRAM is on the order of 10 GB and that flash offers an effective bandwidth of typically 5 GB/s.[^wangLeverSpeculativeLLM2026a]

Per-token verification latency of flash-resident target models (Table 1):

| Model | Compute (ms) | I/O (ms) | Total (ms) | I/O percentage |
|---|---|---|---|---|
| Llama-3.1-8B | 93.2 | 990.6 | 1083.8 | 91.4% |
| Qwen3-4B | 131.5 | 474.4 | 605.9 | 78.3% |
| Qwen3-8B | 96.6 | 953.4 | 1050.0 | 90.8% |
| Qwen3-14B | 141.2 | 1967.1 | 2108.3 | 93.3% |

All rows: [^wangLeverSpeculativeLLM2026a]

- **Limited verification parallelism (Figure 4).** Llama-3.1-8B and Qwen3-8B were verified on a Snapdragon 8 Gen 3 NPU and on an NVIDIA RTX 3090 GPU with 1 to 64 verified tokens. On the phone, verification latency rises noticeably with the number of verified tokens. At 64 verified tokens the figure marks a speedup over single-token generation of 20.6x on the GPU and 8.0x on the NPU, and marks the GPU as 77x faster than the NPU in verification latency.[^wangLeverSpeculativeLLM2026a]
- **Tree budget dilemma (Figure 5).** As the token tree budget grows from 4 to 64, target-model calls fall but verification cost rises. Accepted length keeps rising with budget, while decode speed peaks at a budget of 16 and then falls.[^wangLeverSpeculativeLLM2026a]
- **Wasted verification (Table 2).** Verification computation spent on tokens that are not accepted averages 21.4%:[^wangLeverSpeculativeLLM2026a]

| Target model | Budget | Verify (ms) | Waste (ms / %) |
|---|---|---|---|
| Llama-3.1-8B | 16 | 828 | 188 / 22.7 |
| Llama-3.1-8B | 32 | 1255 | 256 / 20.4 |
| Qwen3-8B | 16 | 817 | 183 / 22.4 |
| Qwen3-8B | 32 | 1229 | 249 / 20.3 |

All rows: [^wangLeverSpeculativeLLM2026a]

The paper's reading: on servers verification is cheap and work focuses on acceptance rate, but on phones each verification can incur expensive flash I/O and take far longer than drafting, and limited parallelism makes verification compute a major part of latency.[^wangLeverSpeculativeLLM2026a]

### Mobile-optimized drafting construction

- Lever uses [tree-based speculation](../methods/tree-based-speculation.md) and picks the tree $T^{*}=\arg\max_{T}\frac{\hat{G}(T)}{\hat{C}_{\mathrm{cycle}}(T)}$ (Eq. 1), the expected tokens per cycle divided by the estimated cycle latency.[^wangLeverSpeculativeLLM2026a]
- **Gain.** $\hat{G}(T)=1+\sum_{u\in T\setminus\{\epsilon\}}\hat{b}(u)$ (Eq. 2), where $\hat{b}(u)$ is the estimated probability that the verification path reaches node $u$ and the 1 is the fallback token. For a child $v=(u,a)$, $\hat{b}(v)=\hat{b}(u)\cdot\operatorname{Calibrate}(p_{d}(a\mid u),C(u),r)$ (Eq. 3). The calibration keeps the draft model's ranking within the candidate set $C(u)$ and scales confidence with a reliability factor $r$ updated from recent verification feedback.[^wangLeverSpeculativeLLM2026a]
- **Cost.** $\hat{C}_{\mathrm{cycle}}(T)=\hat{C}_{\mathrm{draft}}(T)+\hat{C}_{\mathrm{verify}}(|T|,L_{T})$ (Eq. 4), with $|T|$ the number of nodes in the verification batch and $L_{T}$ the number of leaf sequences. Draft cost is a moving average of runtime measurements. The flash I/O cost of one verification is treated as roughly fixed across tree shapes; the tree-dependent part comes from batched verification compute and runtime management (KV-cache copying and temporary sequences, one per leaf). Verification cost is read from an online latency profile indexed by $(|T|,L_{T})$, initialized from offline measurements, with a conservative penalty for unseen shapes.[^wangLeverSpeculativeLLM2026a]
- **Greedy construction (Algorithm 1).** From the frontier $\mathcal{F}$ of generated but not yet inserted candidates, Lever repeatedly inserts $v^{\star}=\arg\max_{v\in\mathcal{F}}\frac{\hat{b}(v)}{\Delta\hat{C}(v\mid T)}$ (Eq. 5) and expands it with the draft model if it is expandable. It stops when $\max_{v\in\mathcal{F}}\frac{\hat{b}(v)}{\Delta\hat{C}(v\mid T)}\leq\frac{\hat{G}(T)}{\hat{C}_{\mathrm{cycle}}(T)}$ (Eq. 6), so no fixed tree budget is needed.[^wangLeverSpeculativeLLM2026a]

### Predictor-based verification pruning

- A linear predictor $W\in\mathbb{R}^{|\mathcal{V}|\times d}$ at an intermediate target layer $L$ scores candidate token $a$ under node $u$ as $s(u,a)=W[a]^{\top}h_{u}^{L}$ (Eq. 7).[^wangLeverSpeculativeLLM2026a]
- Training freezes the target and updates only the predictor with $\mathcal{L}=\mathcal{L}_{\mathrm{KD}}+\lambda_{\mathrm{Cand}}\mathcal{L}_{\mathrm{Cand}}$ (Eq. 8): a full-vocabulary KL distillation from the target's final-layer distribution (Eq. 9) and a candidate-set distillation over the draft candidate set $C_{t}(u)$ only (Eq. 10).[^wangLeverSpeculativeLLM2026a]
- **Candidate normalization.** Scores are normalized with a softmax at temperature $\tau_{E}$ over the draft candidate set, including "shadow tokens", candidates not inserted in the tree, which appear only in the denominator so that a parent with a single child still gets a meaningful score (Eq. 11).[^wangLeverSpeculativeLLM2026a]
- **Conservative pruning.** An edge with $s_{norm}(u,a)<\theta$ is removable, subject to safeguards: ancestors of kept nodes are kept; a backbone path of the most reliable child at each depth is kept; several high-scoring children may be kept near the root; and a pruning decision that leaves too few nodes or leaves is rejected. The target runs from layer $L$ to the final layer only on the kept nodes, and acceptance is still decided by the full target model.[^wangLeverSpeculativeLLM2026a]

### Hardware-hybrid execution (CPU-NPU)

- **Draft: batch-aware scheduling.** The paper says drafting usually runs on the CPU because draft trees are dynamic and small, and on the NPU kernel launch and data transfer overheads can dominate. Because verification is far slower than drafting on phones, Lever's trees grow large and accumulate many high-value nodes whose parents are already in the tree; these are expanded together as one batch with a causal mask. Early in tree construction nodes run serially on the CPU; as the tree grows, candidates are batched onto the NPU.[^wangLeverSpeculativeLLM2026a]
- **Verification: layer-wise separation.** All target transformer layers for the kept nodes run as one batch on the NPU. The output projection is taken out of the fixed NPU graph and run on demand on the CPU: logits for the root first, then for each matched candidate step by step along the accepted path. The motivation is that the large-vocabulary output projection takes a large share of verification latency, and a fixed-shape NPU graph would compute logits for every path although only one is accepted.[^wangLeverSpeculativeLLM2026a]
- Target weights are streamed from flash layer by layer, and the verification profile records latency after computation-I/O overlap.[^wangLeverSpeculativeLLM2026a]

## Experiments & Results

### Setup

| Device | SoC | Flash storage |
|---|---|---|
| OnePlus 12 | Snapdragon 8 Gen 3 | UFS 4.0 |
| Honor 500 Pro | Snapdragon 8 Elite | UFS 3.1 |
| Honor Magic V5 | Snapdragon 8 Elite | UFS 4.1 |

All rows: [^wangLeverSpeculativeLLM2026a]

- Ablations and sensitivity analyses run on the OnePlus 12 unless stated; the end-to-end evaluation runs on all three devices.[^wangLeverSpeculativeLLM2026a]
- Targets: Llama-3.1-8B (Instruct), Qwen3-4B (Non-Thinking), Qwen3-8B (Thinking), Qwen3-14B (Thinking).[^wangLeverSpeculativeLLM2026a]
- Draft models are trained with [EAGLE-3](../methods/eagle-3.md), and every speculative method uses the same target-draft pair. Target and draft are quantized to Q4\_0. Target weights are stored in flash and streamed layer by layer unless stated.[^wangLeverSpeculativeLLM2026a]
- Datasets: [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), [GSM8K](../datasets/gsm8k.md), [MT-Bench](../datasets/mt-bench.md), used as decoding workloads, not for task accuracy. 50 random samples per dataset, maximum output length 128 tokens, greedy decoding at temperature 0.[^wangLeverSpeculativeLLM2026a]
- Metric: decode throughput in tokens/s, prefill excluded. Aggregates are geometric means across models, datasets, and devices.[^wangLeverSpeculativeLLM2026a]
- Baselines: **Flash-AR** (autoregressive decoding with a flash-streamed target); **Chain-SD** (standard sequence speculative decoding with the same EAGLE3 draft, fixed 8-token chain); **EdgeLLM** (speculative decoding for flash-backed mobile inference with branch navigation and verification pacing). [SpecInfer](../methods/specinfer.md) and OPT-Tree appear only in the tree-construction ablation. All methods share the target model, quantization, prompt template, decoding configuration, and flash weight-streaming mechanism.[^wangLeverSpeculativeLLM2026a]

### End-to-end decode throughput (Figure 10)

Geometric-mean speedup of Lever over 48 device-model-dataset configurations: 2.93$\times$ over Flash-AR, 1.50$\times$ over Chain-SD, 1.27$\times$ over EdgeLLM. Gains are larger on code and reasoning workloads and smaller on MT-Bench, where draft-target agreement is weaker.[^wangLeverSpeculativeLLM2026a] In the figure Lever has the highest bar in every configuration, and Chain-SD is above Flash-AR in every configuration.[^wangLeverSpeculativeLLM2026a]

Absolute Lever decode throughput (tokens/s), from the labels in Figure 10:

| Dataset | Target | OnePlus 12 | Honor 500 Pro | Honor Magic V5 |
|---|---|---|---|---|
| HumanEval | Llama-3.1-8B | 2.72 | 2.09 | 4.31 |
| HumanEval | Qwen3-4B | 4.92 | 3.16 | 7.27 |
| HumanEval | Qwen3-8B | 1.62 | 1.09 | 2.14 |
| HumanEval | Qwen3-14B | 1.17 | 0.81 | 1.62 |
| MBPP | Llama-3.1-8B | 2.92 | 2.15 | 4.52 |
| MBPP | Qwen3-4B | 5.20 | 3.20 | 7.55 |
| MBPP | Qwen3-8B | 1.75 | 1.25 | 2.40 |
| MBPP | Qwen3-14B | 1.17 | 0.81 | 1.63 |
| GSM8K | Llama-3.1-8B | 2.23 | 1.54 | 3.35 |
| GSM8K | Qwen3-4B | 3.82 | 2.74 | 5.92 |
| GSM8K | Qwen3-8B | 1.74 | 1.19 | 2.32 |
| GSM8K | Qwen3-14B | 1.16 | 0.86 | 1.67 |
| MT-Bench | Llama-3.1-8B | 2.13 | 1.51 | 3.26 |
| MT-Bench | Qwen3-4B | 3.33 | 2.17 | 5.47 |
| MT-Bench | Qwen3-8B | 1.52 | 1.12 | 2.14 |
| MT-Bench | Qwen3-14B | 0.98 | 0.71 | 1.41 |

All rows: [^wangLeverSpeculativeLLM2026a]

### Ablation: tree construction (Figure 11, OnePlus 12)

Only the construction policy changes. Values are relative to SpecInfer.[^wangLeverSpeculativeLLM2026a]

| Workload | Lever throughput / SpecInfer | Lever accepted length / SpecInfer |
|---|---|---|
| MBPP, Llama-3.1-8B | 1.12x | 1.11x |
| MBPP, Qwen3-8B | 1.14x | 1.16x |
| GSM8K, Llama-3.1-8B | 1.06x | 1.08x |
| GSM8K, Qwen3-8B | 1.10x | 1.01x |
| MT-Bench, Llama-3.1-8B | 1.14x | 1.14x |
| MT-Bench, Qwen3-8B | 1.10x | 1.13x |
| Geo. mean, all | 1.11x | 1.10x |

All rows: [^wangLeverSpeculativeLLM2026a]

OPT-Tree reaches slightly higher accepted length than Lever but lower throughput, which the paper reads as evidence that maximizing accepted length alone adds verification overhead on mobile hardware.[^wangLeverSpeculativeLLM2026a]

### Ablation: verification pruning (Figure 12)

On the same tree and backend, Lever keeps about 48% of upper-layer rows, reduces verification latency by 12.2%, and retains about 95% of accepted tokens relative to full verification. Removing shadow candidates makes scores less reliable and limits pruning; removing the safeguards prunes more rows but discards useful paths. In the figure, Lever has the highest normalized decode throughput among the pruning variants on both Llama-3.1-8B and Qwen3-8B.[^wangLeverSpeculativeLLM2026a]

### Ablation: CPU-NPU execution (Figures 13 and 14)

- **Draft stage (Figure 13).** Draft-stage latency per cycle for Llama-3.1-8B, Qwen3-8B, and Qwen3-14B on MBPP and GSM8K. Single-node NPU execution has the highest latency in every configuration, because of launch and synchronization overhead. Single-node CPU is lower but cannot exploit tensor parallelism. Batch-aware scheduling (CPU early, NPU batches later) has the lowest latency in every configuration. The figure's y-axis (draft-stage latency per cycle) has gridlines at 10, 20, and 30 ms, and only the single-node NPU bars for Qwen3-14B rise above 30 ms.[^wangLeverSpeculativeLLM2026a]
- **Output projection (Figure 14).** Eager NPU projection (logits for all verified nodes) is the slowest. On-demand projection only along the accepted path is faster, and on-demand CPU projection is faster than on-demand NPU projection because it avoids repeated small NPU invocations and CPU-NPU synchronization, with the same accepted tokens.[^wangLeverSpeculativeLLM2026a]

### Sensitivity (OnePlus 12)

Draft model quality, Qwen3-8B target, decode tokens/s (Table 5):

| Draft | Method | MBPP | GSM8K | MT-Bench | Geo. |
|---|---|---|---|---|---|
| EAGLE3 | Chain-SD | 1.296 | 1.222 | 1.108 | 1.206 |
| EAGLE3 | EdgeLLM | 1.434 | 1.382 | 1.283 | 1.365 |
| EAGLE3 | Lever | 1.753 | 1.741 | 1.516 | 1.666 |
| Qwen3 (0.6B) | Chain-SD | 0.860 | 0.840 | 0.820 | 0.840 |
| Qwen3 (0.6B) | EdgeLLM | 1.010 | 0.940 | 0.890 | 0.945 |
| Qwen3 (0.6B) | Lever | 1.250 | 1.220 | 1.110 | 1.192 |

All rows: [^wangLeverSpeculativeLLM2026a]

Fraction of target layers resident in DRAM (the first $x\%$ of layers stay in DRAM, the rest stream from flash), Lever decode tokens/s (Table 6):

| Workload | 0% | 20% | 40% | 60% | 80% | 100% |
|---|---|---|---|---|---|---|
| Qwen3-8B / MBPP | 1.753 | 2.010 | 2.473 | 2.812 | 3.120 | 3.401 |
| Llama-3.1-8B / MBPP | 2.918 | 3.704 | 4.214 | 4.619 | 4.922 | 5.494 |
| Qwen3-8B / GSM8K | 1.741 | 1.996 | 2.453 | 2.791 | 3.099 | 3.377 |
| Llama-3.1-8B / GSM8K | 2.225 | 2.821 | 3.203 | 3.508 | 3.736 | 4.194 |

All rows: [^wangLeverSpeculativeLLM2026a]

Maximum output length, Lever decode tokens/s (Table 7):

| Workload | 32 | 64 | 128 | 256 | 512 |
|---|---|---|---|---|---|
| Qwen3-8B / MBPP | 1.768 | 1.772 | 1.753 | 1.741 | 1.712 |
| Llama-3.1-8B / MBPP | 3.082 | 3.110 | 2.918 | 2.890 | 2.854 |
| Qwen3-8B / GSM8K | 1.756 | 1.760 | 1.741 | 1.729 | 1.681 |
| Llama-3.1-8B / GSM8K | 2.349 | 2.371 | 2.225 | 2.204 | 2.173 |

All rows: [^wangLeverSpeculativeLLM2026a]

A weaker draft lowers absolute throughput for all speculative methods, but Lever stays ahead of Chain-SD and EdgeLLM. Throughput rises as more target layers stay in DRAM, and Lever stays effective at the fully flash-backed 0% setting. Throughput decreases only mildly with longer outputs.[^wangLeverSpeculativeLLM2026a]

## Limitations

- The setting is flash-backed: the target model's weights are streamed from flash during each verification, and the gain over Flash-AR comes from amortizing those invocations. The evaluation has no autoregressive baseline with a fully DRAM-resident target; Table 6 reports Lever itself at a 100% DRAM budget.[^wangLeverSpeculativeLLM2026a]
- The paper reports decode throughput only. It does not report energy or power, prefill time is excluded, and task accuracy is not evaluated.[^wangLeverSpeculativeLLM2026a]
- The main evaluation uses greedy decoding at temperature 0, 50 samples per dataset, and a maximum output length of 128 tokens.[^wangLeverSpeculativeLLM2026a]
- The paper does not name the inference framework or NPU runtime that Lever is built on, and it does not state which processor runs the target model for the Flash-AR, Chain-SD, and EdgeLLM baselines.[^wangLeverSpeculativeLLM2026a]
- Verification pruning keeps about 95% of accepted tokens, so it shortens the accepted length relative to full verification on the same tree, while final token decisions on kept paths remain those of the target model.[^wangLeverSpeculativeLLM2026a]
- All devices use Qualcomm Snapdragon SoCs.[^wangLeverSpeculativeLLM2026a]

## Related

- Methods: [Lever](../methods/lever.md), [Speculative decoding](../methods/speculative-decoding.md), [Tree-based speculation](../methods/tree-based-speculation.md), [EAGLE-3](../methods/eagle-3.md) (draft model), [SpecInfer](../methods/specinfer.md) (ablation baseline), [OPT-Tree](../methods/opt-tree.md) (ablation baseline), [EdgeLLM](../methods/edgellm.md) (baseline), [Early exit](../methods/early-exit.md), [Medusa](../methods/medusa.md) and [Sequoia](../methods/sequoia.md) (cited related work)
- Datasets: [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), [GSM8K](../datasets/gsm8k.md), [MT-Bench](../datasets/mt-bench.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md)
- Mobile inference papers in this wiki: [Is Your NPU Ready for LLMs?](caiYourNPUReady2026.md), [Efficient On-Device Diffusion LLM Inference with Mobile NPU](wangEfficientOnDeviceDiffusion2026.md), [SpecEdge](parkSpecEdgeScalableEdgeAssisted2025.md), [SpecExec](svirschevskiSpecExecMassivelyParallel2024.md) (offloaded target on consumer GPUs)

## Open questions and results

- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)
- [Applying the speculative drafter papers to a mobile phone NPU](../analyses/speculative-drafter-papers-on-mobile-npu.md)
- [On-device draft cost on the Galaxy S25 Hexagon NPU](../experiments/npu-draft-cost-profiling-galaxy-s25.md)

[^wangLeverSpeculativeLLM2026a]: Wang et al. 2026
