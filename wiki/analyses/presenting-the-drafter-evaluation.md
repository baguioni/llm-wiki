---
type: Analysis
title: Presenting the drafter evaluation the way the drafter papers do
description: How the DFlash, PARD, PARD-2, DSpark, and EAGLE-3 papers lay out their results in tables and figures, and a table-versus-figure plan for my six-drafter phone evaluation built on those conventions.
tags: [speculative-decoding, mobile-specedge, research-writing, dflash, dspark, pard, eagle-3]
sources:
  - id: drafter-evaluation
    resource: raw/experiments/drafter-evaluation.md
    title: "Drafter evaluation: six Q4_0 draft models for Qwen3-14B (phone drafts, spark verifies)"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: anPARDAcceleratingLLM2025
    resource: zotero://select/items/@anPARDAcceleratingLLM2025
    title: "PARD: Accelerating LLM Inference with Low-Cost PARallel Draft Model Adaptation"
  - id: anPARD2TargetAlignedParallel2026
    resource: zotero://select/items/@anPARD2TargetAlignedParallel2026
    title: "PARD-2: Target-Aligned Parallel Draft Model for Dual-Mode Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: drafter-evaluation-server-shapes
    resource: raw/experiments/drafter-evaluation-server-shapes.md
    title: "Drafter evaluation with server-only baselines at the SpecEdge, chain7, and tree16 shapes (§2.7, §5.5)"
---

# Presenting the drafter evaluation the way the drafter papers do

## Question

How do the DFlash, PARD, PARD-2, DSpark, and EAGLE-3 papers present their results? Given [my drafter evaluation](../experiments/drafter-evaluation-qwen3-14b.md), which of its data should go in tables and which in figures?

## Answer

The papers share one convention: **comparisons with exact numbers across methods and benchmarks go in tables, and anything swept over a continuous axis goes in a figure.** The continuous axes are draft position, draft length, data scale, batch size, and threshold. My evaluation should follow the same split. The main table has drafters as rows, tree shapes as columns, and a tok/s | tok/round pair per cell. The figures carry the headline bar chart, the acceptance survival curve, the round-time breakdown, and the acceptance-versus-draft-cost trade-off. The split setting adds network bytes and phone memory, which papers do not report, and these go in a separate system-cost table.

### How each paper presents its results

| Paper | Main table layout | Metric per cell | Figures carry |
|---|---|---|---|
| EAGLE-3 | Rows: Temperature=0 and Temperature=1 blocks, then target model, then method. Columns: MT-bench, HumanEval, GSM8K, Alpaca, CNN/DM, Mean | Speedup / $\tau$ | Headline speedup bars per target; speedup and acceptance vs data scale; acceptance rate vs number of self-generated inputs (n-α) |
| DFlash | Rows: temperature block, then model, then method with tree or block size in parentheses. Columns: benchmarks grouped by domain (math, code, chat), plus Avg. | Speedup / $\tau$ | Headline speedup bars on Qwen3-8B; draft latency vs number of draft tokens for 1-, 3-, and 5-layer DFlash and 1-layer EAGLE-3 |
| PARD | Rows: target, then method. Columns: HumanEval, GSM8K, SpecBench, Average. Best values bold | tokens/s and speedup | Tokens/s bars per target; first-token acceptance; a per-step time comparison of VSD and PARD |
| PARD-2 | Same column layout as DFlash with an Average column; temperature 0 only; target-dependent and target-independent modes in two tables | Speedup / $\tau$ | Throughput per GPU vs throughput per user over batch sizes 1 to 64 (Pareto); acceptance vs draft position |
| DSpark | One table: target, then drafter as rows; Math, Code, and Chat benchmarks as columns. Bold marks the best results | $\tau$ only | Conditional acceptance vs draft position per domain; accepted length vs drafter depth and vs draft length; calibration; production throughput frontiers |

Sources: EAGLE-3 Table 1 and Figures 1, 2, 4, 7;[^liEAGLE3ScalingInference2025] DFlash Table 1 and Figures 1 and 3;[^chenDFlashBlockDiffusion2026] PARD Table 1 and Figures 1 and 2;[^anPARDAcceleratingLLM2025] PARD-2 Tables 1 and 2 and Figures 1 and 2;[^anPARD2TargetAlignedParallel2026] DSpark Table 1 and Figures 2 to 8.[^chengDSparkConfidenceScheduledSpeculative2026]

Common points:

- **Speedup next to acceptance.** Four of the five papers put a speed number and an acceptance number side by side in each cell. DSpark reports $\tau$ alone and states it as accepted length per decoding round.[^chengDSparkConfidenceScheduledSpeculative2026] PARD reports tokens/s with speedup.[^anPARDAcceleratingLLM2025]
- **An average column.** EAGLE-3 (Mean), DFlash (Avg.), PARD and PARD-2 (Average) have one.[^liEAGLE3ScalingInference2025][^chenDFlashBlockDiffusion2026][^anPARDAcceleratingLLM2025][^anPARD2TargetAlignedParallel2026]
- **Ablations are small tables** with one configuration per row, for example DFlash's draft-layer, target-feature, and block-size ablations, and PARD-2's loss-weighting and gating ablations.[^chenDFlashBlockDiffusion2026][^anPARD2TargetAlignedParallel2026] DSpark is the exception and puts its analyses in figures.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Serving or batch results.** DFlash tabulates tok/s by concurrency (1 to 32) on SGLang.[^chenDFlashBlockDiffusion2026] PARD-2 plots a throughput Pareto front over batch sizes instead.[^anPARD2TargetAlignedParallel2026]
- **Per-position acceptance is a line plot**: EAGLE-3 (accept rate vs n-α), PARD-2 (acceptance vs draft position), DSpark (conditional acceptance vs position).[^liEAGLE3ScalingInference2025][^anPARD2TargetAlignedParallel2026][^chengDSparkConfidenceScheduledSpeculative2026]

### Proposed tables for my evaluation

**Table 1, main results.** Rows are the six drafters, grouped as block (PARD-2, DFlash, DSpark, PARD-1) and autoregressive (Qwen3-0.6B, EAGLE-3). The columns are chain7, tree16, and own-best, each a tok/s | tok/round pair, with the best value per column in bold. This is the EAGLE-3 and DFlash layout with shapes in place of benchmarks. The data is the throughput and acceptance tables of the report.[^drafter-evaluation]

| Drafter | chain7 tok/s / tok/round | tree16 tok/s / tok/round | own-best tok/s / tok/round |
|---|---|---|---|
| PARD-2 | 24.9 / 3.34 | **29.3** / 4.21 | **30.0** / 4.58 |
| DFlash | 25.5 / 3.45 | 27.9 / 4.15 | 28.8 / 4.37 |
| DSpark | **26.5** / **3.83** | 28.3 / **4.64** | 28.2 / **5.02** |
| PARD-1 | 22.1 / 2.76 | 26.7 / 3.54 | 26.7 / 3.81 |
| Qwen3-0.6B | 15.6 / 3.11 | 16.6 / 4.06 | 18.5 / 4.53 |
| EAGLE-3 | 13.0 / 2.71 | 15.9 / 3.60 | 17.6 / 3.92 |

All rows: [^drafter-evaluation]

Two changes would make the table read like the papers:

- **Add a speedup column.** No target-only (non-speculative) baseline was run, so the report gives tok/s and no speedup.[^drafter-evaluation] The updated report adds server-only speculative decoding baselines (Qwen3-0.6B fp16 drafting on the GPU): 17.0 tok/s at chain7 and 21.6 at tree16 (2 repeats each), and 21.3 at the SpecEdge shape (1 run).[^drafter-evaluation-server-shapes] It supports a column labelled "× vs server-only", but this is not the speedup over autoregressive decoding that the papers report. One target-only arm over the same WiFi path would give speedup = tok/s ÷ baseline tok/s. PARD shows tokens/s and speedup side by side, a format that fits this setting.[^anPARDAcceleratingLLM2025]
- **Name the acceptance metric.** tok/round includes the bonus token,[^drafter-evaluation] which matches DSpark's $\tau$ (accepted length per decoding round).[^chengDSparkConfidenceScheduledSpeculative2026] Call it $\tau$ in the paper and state that it includes the bonus token.

**Table 2, by Spec-Bench category.** Show tok/s | tok/round for the six categories plus an average, for one shape (own-best), in the same layout as Table 1. The other shapes go in the appendix. This plays the role of the papers' benchmark columns, and it shows the PARD-1 translation weakness and that every drafter is fastest on math_reasoning.[^drafter-evaluation]

**Table 3, cost of the split setting.** The papers have no counterpart, because they run the drafter beside the target. Columns: draft ms (with p95), verify ms, network median, round ms, KB up per round, KB down per token (steady), prompt-feature KB per request, TTFT p50, client VmHWM, and NPU DMA-BUF. Use one shape (tree16) and put the rest in the appendix. This must be a table because the units are mixed and the exact values matter.[^drafter-evaluation]

**Table 4, drafter setup.** Checkpoint, phone file size, drafting mode, and what the server returns, as in §2.3 of the report.[^drafter-evaluation] It replaces the paper-style hyperparameter table.

**Appendix tables.** Oracle vs live tok/round, repeat ranges and 95% CIs, output agreement, thermal peaks and frequency caps, and the run inventory. These are validity checks with exact numbers, which the papers also keep in tables or the appendix.[^drafter-evaluation]

### Proposed figures for my evaluation

1. **Headline grouped bar chart (intro).** x = drafter, bars = the three shapes, y = tok/s, with value labels. A dashed line for target-only tok/s can be added once that baseline is run. This is the figure that DFlash, PARD, and EAGLE-3 open with.[^chenDFlashBlockDiffusion2026][^anPARDAcceleratingLLM2025][^liEAGLE3ScalingInference2025]
2. **Round-time breakdown (stacked horizontal bars).** One bar per drafter at tree16: NPU decode, host top-k, Markov head, network, server verify, and client postprocess. It shows in one picture why the block drafters win (22–54 ms of draft against 85–116 ms) and where DSpark's Markov head goes.[^drafter-evaluation] It plays the role of DFlash's draft-cost figure and PARD's per-step time comparison.[^chenDFlashBlockDiffusion2026][^anPARDAcceleratingLLM2025]
3. **Acceptance survival curve.** x = draft depth j (1 to 7, or 8), y = $a_j$, one line per drafter, one panel per shape. The report has $a_1$ to $a_8$ for every arm.[^drafter-evaluation] This matches the per-position plots of EAGLE-3, PARD-2, and DSpark.[^liEAGLE3ScalingInference2025][^anPARD2TargetAlignedParallel2026][^chengDSparkConfidenceScheduledSpeculative2026] DSpark plots conditional acceptance,[^chengDSparkConfidenceScheduledSpeculative2026] which can be derived as $a_j / a_{j-1}$ if a direct comparison is wanted.
4. **Acceptance vs draft cost.** x = draft ms per round, y = tok/round, one marker per drafter, connected across the three shapes, with iso-throughput curves in the background. It shows that DSpark buys acceptance with draft time, while the autoregressive drafters sit far to the right. This is the trade-off format of PARD-2's and DSpark's Pareto figures.[^anPARD2TargetAlignedParallel2026][^chengDSparkConfidenceScheduledSpeculative2026] It should use the network-normalised round time, so that WiFi variance does not move the points.[^drafter-evaluation]
5. **Tree budget sweep (optional).** x = rows verified (8, 17, 33), y = tok/s, one line per drafter. It shows that own-best trees help the autoregressive drafters and barely change the block drafters. A second panel can plot the Markov head time (8.48 → 15.49 → 23.68 ms), in the way DSpark's draft-length figure adds a latency panel.[^drafter-evaluation][^chengDSparkConfidenceScheduledSpeculative2026]

## Evidence

The proposed tables and figures use only data that the report already contains: throughput, acceptance, survival, histograms, draft stages, round and server times, latency, network bytes, memory, telemetry peaks, and per-category results for every arm.[^drafter-evaluation]

## Caveats

- Without a target-only baseline the main table cannot report speedup, the metric every paper's headline uses.[^drafter-evaluation] The server-only chain7 and tree16 runs use the phone shapes, so they can sit in the same columns as the phone arms, as a reference row labelled by location and precision (GPU fp16). The SpecEdge-shape run uses a different tree and belongs in a footnote.[^drafter-evaluation-server-shapes]
- The arms decode slightly different continuations because of FP8 verifier divergence, so the tok/round comparison is on matched prompts, not identical outputs.[^drafter-evaluation] A footnote under Table 1 should say so. See [the divergence question](../questions/fp8-verifier-tree-output-divergence.md).
- Thermal time series would need the per-run `phone_telemetry.csv`, which is not in `raw/`. The report has only per-run peaks, which suit a table.[^drafter-evaluation]
- The choice of tables and figures is my recommendation. The papers' layouts are the evidence for it, not a rule.

## Related

- [Six phone drafters for a Qwen3-14B server verifier](../experiments/drafter-evaluation-qwen3-14b.md)
- [Block drafters reach 1.6–1.8× the throughput of autoregressive drafters on a phone NPU](../results/block-drafters-vs-ar-drafters-on-phone-npu.md)
- [DFlash, DSpark, and EAGLE-3: how they draft and what they report on Qwen3-8B](dflash-dspark-eagle-3-drafting-comparison.md)
- Papers: [DFlash](../papers/chenDFlashBlockDiffusion2026.md), [PARD](../papers/anPARDAcceleratingLLM2025.md), [PARD-2](../papers/anPARD2TargetAlignedParallel2026.md), [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md), [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md)

[^drafter-evaluation]: My drafter evaluation report, runs of 2026-10-15/16
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^anPARDAcceleratingLLM2025]: An et al. 2025
[^anPARD2TargetAlignedParallel2026]: An et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^drafter-evaluation-server-shapes]: My drafter evaluation report with the server-only baselines, runs of 2026-10-16
