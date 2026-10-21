---
type: Dataset
title: MBPP
description: Code generation benchmark used in the wiki's papers as a coding prompt set for speculative-decoding speed measurements and as a pass@1 accuracy test.
tags: [code-generation, speculative-decoding, evaluation]
sources:
  - id: shinnReflexionLanguageAgents2023
    resource: zotero://select/items/@shinnReflexionLanguageAgents2023
    title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: muralidharanCompactLanguageModels2024
    resource: zotero://select/items/@muralidharanCompactLanguageModels2024
    title: Compact Language Models via Pruning and Knowledge Distillation
  - id: wangLeverSpeculativeLLM2026a
    resource: zotero://select/items/@wangLeverSpeculativeLLM2026a
    title: "Lever: Speculative LLM Inference on Smartphones"
  - id: elhoushiLayerSkipEnablingEarly2024
    resource: zotero://select/items/@elhoushiLayerSkipEnablingEarly2024
    title: "LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding"
  - id: huAdaSPECSelectiveKnowledge2025
    resource: zotero://select/items/@huAdaSPECSelectiveKnowledge2025
    title: "AdaSPEC: Selective Knowledge Distillation for Efficient Speculative Decoders"
  - id: yuIntrospectiveDiffusionLanguage2026
    resource: zotero://select/items/@yuIntrospectiveDiffusionLanguage2026
    title: "Introspective Diffusion Language Models"
---

# MBPP

## Overview

MBPP, like [HumanEval](humaneval.md), measures function body generation accuracy given natural language descriptions.[^shinnReflexionLanguageAgents2023] Three speculative-decoding papers use its prompts as a code workload for measuring speedup and acceptance length.[^chenDFlashBlockDiffusion2026][^chengDSparkConfidenceScheduledSpeculative2026][^liuWhenParallelDrafter2026] Two papers report pass@1 accuracy on it.[^shinnReflexionLanguageAgents2023][^muralidharanCompactLanguageModels2024] LayerSkip and I-DLM also report its accuracy, for early exit layers and for a diffusion LM against its AR base.[^elhoushiLayerSkipEnablingEarly2024][^yuIntrospectiveDiffusionLanguage2026] AdaSPEC uses it as a task for distilling draft models and measuring their acceptance rate.[^huAdaSPECSelectiveKnowledge2025]

## Composition

- Reflexion translates a subset to Rust with MultiPL-E and reports Python (PY) and Rust (RS) results.[^shinnReflexionLanguageAgents2023]
- The papers do not state the dataset's size or splits.

## Usage across papers

| Paper | What it is used for | Models / setting | Reported numbers |
|---|---|---|---|
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) | Code prompt set for speedup and $\tau$; SGLang serving with a coder model | Qwen3-4B and 8B on Transformers; Qwen3-Coder-30B-A3B on SGLang | DFlash (16) on Q3-4B at temperature 0: 4.78×, $\tau$ 6.09[^chenDFlashBlockDiffusion2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) | Code prompt set for accepted length | Qwen3-4B, 8B, 14B, Gemma4-12B; temperature 1.0 | DSpark $\tau$ from 5.11 to 5.26 across the four targets[^chengDSparkConfidenceScheduledSpeculative2026] |
| [DPara](../papers/liuWhenParallelDrafter2026.md) | Coding prompt set for speedup and $\tau$ | Qwen3-8B and 14B; greedy and temperature 1.0 | DPara on Qwen3-8B, greedy: 3.27×, $\tau$ 4.48[^liuWhenParallelDrafter2026] |
| [Reflexion](../papers/shinnReflexionLanguageAgents2023.md) | Pass@1 accuracy, Python and Rust | GPT-4 baseline and Reflexion | Reflexion 77.1 on MBPP (PY) against 80.1 for GPT-4, and 75.4 on MBPP (RS) against 70.9[^shinnReflexionLanguageAgents2023] |
| [Minitron](../papers/muralidharanCompactLanguageModels2024.md) | Zero-shot pass@1 of pruned and baseline models | Minitron 8B and 4B and baselines; temperature 0.2, top-p 0.95 | Minitron 8B 35.2, Minitron 4B 28.2[^muralidharanCompactLanguageModels2024] |
| [Lever](../papers/wangLeverSpeculativeLLM2026a.md) | Decoding workload, 50 samples, up to 128 output tokens; also the sensitivity studies | Four targets on three Snapdragon phones, greedy | Lever on Qwen3-4B, Honor Magic V5: 7.55 tokens/s[^wangLeverSpeculativeLLM2026a] |
| [Elhoushi et al. 2024](../papers/elhoushiLayerSkipEnablingEarly2024.md) | Early exit accuracy at the last and middle layer, baseline → LayerSkip | Llama2 7B/13B, Llama3 8B, Llama3.2 1B, continual pretraining | Llama2 7B last layer 21.0 → 22.4, middle layer 0 → 7.20; Llama3 8B last layer 49.0 → 40.0[^elhoushiLayerSkipEnablingEarly2024] |
| [Hu et al. 2025](../papers/huAdaSPECSelectiveKnowledge2025.md) | Code task for [AdaSPEC](../methods/adaspec.md) draft distillation; acceptance rate; ablations; vLLM speed | Pythia-31M → 1.4B and CodeGen-350M → Phi-2, greedy verification | $\alpha$ 49.88% (DistillSpec) → 65.12% (Pythia, optimal epochs); 149.15 → 181.67 tokens/s on one A100[^huAdaSPECSelectiveKnowledge2025] |
| [Yu et al. 2026](../papers/yuIntrospectiveDiffusionLanguage2026.md) | Accuracy of [I-DLM](../methods/i-dlm.md); serving workload against EAGLE-3 | Qwen3 chat template with thinking, temperature 1.0, three runs; sanitized, 257 problems, pass@1 | I-DLM-8B 92.2 vs Qwen3-8B 93.4; 327 vs 245 tokens/s per request against EAGLE-3 at concurrency 1[^yuIntrospectiveDiffusionLanguage2026] |

## Speed metrics

Speculative-decoding speedup, acceptance length, and throughput measured with this dataset's prompts. These numbers say nothing about task accuracy. Each subsection is one paper and one setting, and rows from different subsections are not comparable.

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): Table 1, Transformers backend

Qwen3 (Q3) targets with thinking mode disabled, maximum of 2048 generated tokens. Speedup is end-to-end over the autoregressive baseline. The number in parentheses is the draft tree size for EAGLE-3 and the block size for DFlash. EAGLE-3 uses 7 draft steps and top-$k$ 10, with the checkpoints released by AngelSlim.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Q3-4B | 0 | EAGLE-3 (16) | 1.78× | 2.95 |
| Q3-4B | 0 | EAGLE-3 (60) | 2.02× | 3.38 |
| Q3-4B | 0 | DFlash (16) | 4.78× | 6.09 |
| Q3-8B | 0 | EAGLE-3 (16) | 1.69× | 2.82 |
| Q3-8B | 0 | EAGLE-3 (60) | 1.93× | 3.25 |
| Q3-8B | 0 | DFlash (16) | 4.65× | 5.95 |
| Q3-4B | 1 | EAGLE-3 (16) | 1.69× | 2.89 |
| Q3-4B | 1 | EAGLE-3 (60) | 1.92× | 3.33 |
| Q3-4B | 1 | DFlash (16) | 4.42× | 5.66 |
| Q3-8B | 1 | EAGLE-3 (16) | 1.64× | 2.74 |
| Q3-8B | 1 | EAGLE-3 (60) | 1.85× | 3.16 |
| Q3-8B | 1 | DFlash (16) | 4.04× | 5.21 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DFlash](../papers/chenDFlashBlockDiffusion2026.md): serving on SGLang (Table 3)

Single B200 GPU, FA4 backend, Spec-v2 scheduling overlap enabled. Cells are throughput in tok/s at each concurrency level, with the DFlash speedup over the baseline in parentheses.[^chenDFlashBlockDiffusion2026]

| Model | Temp. | Method | Conc. 1 | Conc. 4 | Conc. 8 | Conc. 16 | Conc. 32 | Avg. $\tau$ |
|---|---|---|---|---|---|---|---|---|
| Qwen3-Coder-30B-A3B | not stated | Baseline | 228 | 682 | 1057 | 1697 | 2735 | – |
| Qwen3-Coder-30B-A3B | not stated | DFlash | 720 (3.2×) | 2052 (3.0×) | 3360 (3.2×) | 5522 (3.3×) | 8538 (3.1×) | 7.23 |

All rows: [^chenDFlashBlockDiffusion2026]

### [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md): accepted length (Table 1)

Accepted length $\tau$ per decoding round, including the bonus token. Standard speculative decoding with chain-based drafting. All three drafters are retrained in the same framework on the same data, with block size 7 for DFlash and DSpark and TTT horizon 7 for Eagle3. Eagle3 has 1 draft layer, DSpark and DFlash have 5. The confidence scheduler is disabled. No speedup is reported for this table.[^chengDSparkConfidenceScheduledSpeculative2026]

| Model | Temp. | Method | $\tau$ |
|---|---|---|---|
| Qwen3-4B | 1.0 | Eagle3 | 3.69 |
| Qwen3-4B | 1.0 | DFlash | 4.40 |
| Qwen3-4B | 1.0 | DSpark | 5.13 |
| Qwen3-8B | 1.0 | Eagle3 | 3.96 |
| Qwen3-8B | 1.0 | DFlash | 4.36 |
| Qwen3-8B | 1.0 | DSpark | 5.16 |
| Qwen3-14B | 1.0 | Eagle3 | 3.81 |
| Qwen3-14B | 1.0 | DFlash | 4.44 |
| Qwen3-14B | 1.0 | DSpark | 5.26 |
| Gemma4-12B | 1.0 | Eagle3 | 4.72 |
| Gemma4-12B | 1.0 | DFlash | 4.39 |
| Gemma4-12B | 1.0 | DSpark | 5.11 |

All rows: [^chengDSparkConfidenceScheduledSpeculative2026]

### [DPara](../papers/liuWhenParallelDrafter2026.md): Tables 1 and 3

Batch size 1, up to 512 new tokens, draft length 7, speedup over AR. Temperature 0 rows are greedy decoding (Table 1). Temperature 1.0 rows use temperature 1.0 for both the target and the drafter (Table 3). SSD-E3 uses the EAGLE3 weight of the target as draft model. SSD, SD, and PEARL on Qwen3-14B use Qwen3-0.6B as draft model. The parallel methods (PEARL, SSD, DPara) use one additional GPU for drafting.[^liuWhenParallelDrafter2026]

| Model | Temp. | Method | Speedup | $\tau$ |
|---|---|---|---|---|
| Qwen3-8B | 0 | SSD-E3 | 1.58× | 2.49 |
| Qwen3-8B | 0 | EAGLE3 | 1.51× | 2.98 |
| Qwen3-8B | 0 | DFlash | 2.80× | 4.95 |
| Qwen3-8B | 0 | DSpark | 3.00× | 5.51 |
| Qwen3-8B | 0 | DPara | 3.27× | 4.48 |
| Qwen3-14B | 0 | SSD | 2.18× | 4.47 |
| Qwen3-14B | 0 | SSD-E3 | 1.82× | 2.54 |
| Qwen3-14B | 0 | PEARL | 2.47× | 2.81 |
| Qwen3-14B | 0 | SD | 1.85× | 4.46 |
| Qwen3-14B | 0 | EAGLE3 | 1.80× | 3.04 |
| Qwen3-14B | 0 | DFlash | 3.16× | 4.89 |
| Qwen3-14B | 0 | DSpark | 3.46× | 5.48 |
| Qwen3-14B | 0 | DPara | 3.58× | 4.45 |
| Qwen3-8B | 1.0 | DFlash | 2.31× | 4.47 |
| Qwen3-8B | 1.0 | DSpark | 2.64× | 5.24 |
| Qwen3-8B | 1.0 | DPara | 2.83× | 4.28 |
| Qwen3-14B | 1.0 | DFlash | 2.76× | 4.53 |
| Qwen3-14B | 1.0 | DSpark | 3.13× | 5.25 |
| Qwen3-14B | 1.0 | DPara | 3.14× | 4.17 |

All rows: [^liuWhenParallelDrafter2026]


## Task accuracy

Scores on the dataset's own task. These are kept apart from the speed metrics above.

### [Minitron](../papers/muralidharanCompactLanguageModels2024.md): Tables 2, 3

Zero-shot pass@1 with temperature 0.2 and top-p 0.95. In Table 3, columns marked `*` are reported from the corresponding papers.[^muralidharanCompactLanguageModels2024]

| Model | Temp. | Method / table | Metric | Score |
|---|---|---|---|---|
| Llama-3 (8B) | 0.2 | Table 2 | pass@1 | 42.4 |
| Llama-2 (6.7B) | 0.2 | Table 2 | pass@1 | 20 |
| Mistral (7.3B) | 0.2 | Table 2 | pass@1 | 38.8 |
| Gemma (8.5B) | 0.2 | Table 2 | pass@1 | 39 |
| Nemotron-4 (15.6B) | 0.2 | Table 2 | pass@1 | 38 |
| Nemotron-3 (8.5B) | 0.2 | Table 2 | pass@1 | 27.04 |
| Minitron 8B (8.3B) | 0.2 | Table 2 | pass@1 | 35.2 |
| Phi-2 (2.7B) | 0.2 | Table 3 | pass@1 | 47 |
| Gemma (2.5B) | 0.2 | Table 3 | pass@1 | 29 |
| Gemma2* (2.6B) | 0.2 | Table 3 | pass@1 | 29.6 |
| Qwen2* (1.5B) | 0.2 | Table 3 | pass@1 | 37.4 |
| Minitron 4B (4.2B) | 0.2 | Table 3 | pass@1 | 28.2 |

All rows: [^muralidharanCompactLanguageModels2024]

### [Reflexion](../papers/shinnReflexionLanguageAgents2023.md): pass@1 (Table 1)

PY is Python, RS is Rust. Rust versions are produced with MultiPL-E. The base strategy is a single code generation sample.[^shinnReflexionLanguageAgents2023]

| Model | Temp. | Method | Metric | Score |
|---|---|---|---|---|
| CodeT + Codex | not stated | previous SOTA, MBPP (PY) | Pass@1 | 67.7 |
| GPT-4 | not stated | single code generation sample, MBPP (PY) | Pass@1 | 80.1 |
| not stated in the table | not stated | Reflexion, MBPP (PY) | Pass@1 | 77.1 |
| GPT-4 | not stated | single code generation sample, MBPP (RS) | Pass@1 | 70.9 |
| not stated in the table | not stated | Reflexion, MBPP (RS) | Pass@1 | 75.4 |

All rows: [^shinnReflexionLanguageAgents2023]

### [Reflexion](../papers/shinnReflexionLanguageAgents2023.md): test generation quality (Table 2)

Base and Reflexion are pass@1 as fractions. TP: unit tests pass, solution pass. FN: unit tests fail, solution pass. FP: unit tests pass, solution fail. TN: unit tests fail, solution fail.[^shinnReflexionLanguageAgents2023]

| Model | Temp. | Benchmark + language | Base | Reflexion | TP | FN | FP | TN |
|---|---|---|---|---|---|---|---|---|
| not stated in the table | not stated | MBPP (PY) | 0.80 | 0.77 | 0.84 | 0.59 | 0.16 | 0.41 |
| not stated in the table | not stated | MBPP (RS) | 0.71 | 0.75 | 0.84 | 0.51 | 0.16 | 0.49 |

All rows: [^shinnReflexionLanguageAgents2023]


## Known issues

- Reflexion measures a false positive test execution rate of 16.3% for MBPP Python, against 1.4% for HumanEval Python, and uses this to explain why Reflexion is below the GPT-4 baseline on MBPP Python.[^shinnReflexionLanguageAgents2023] MBPP Python is the only programming benchmark in that paper where Reflexion does not set a new state of the art.[^shinnReflexionLanguageAgents2023]

# Contradictions

### Same drafter, target, and temperature in different papers

More than one paper reports the same drafter on the same Qwen3 target and temperature with this dataset. The values are side by side below, and most of them differ.

| Target | Temp. | Method | DFlash paper[^chenDFlashBlockDiffusion2026] (speedup / $\tau$) | DSpark paper[^chengDSparkConfidenceScheduledSpeculative2026] ($\tau$) | DPara paper[^liuWhenParallelDrafter2026] (speedup / $\tau$) |
|---|---|---|---|---|---|
| Qwen3-4B | 1 | EAGLE-3 | 1.69× / 2.89 (tree size 16); 1.92× / 3.33 (tree size 60) | 3.69 | – |
| Qwen3-4B | 1 | DFlash | 4.42× / 5.66 (block size 16) | 4.40 | – |
| Qwen3-8B | 0 | EAGLE-3 | 1.69× / 2.82 (tree size 16); 1.93× / 3.25 (tree size 60) | – | 1.51× / 2.98 |
| Qwen3-8B | 0 | DFlash | 4.65× / 5.95 (block size 16) | – | 2.80× / 4.95 |
| Qwen3-8B | 1 | EAGLE-3 | 1.64× / 2.74 (tree size 16); 1.85× / 3.16 (tree size 60) | 3.96 | – |
| Qwen3-8B | 1 | DFlash | 4.04× / 5.21 (block size 16) | 4.36 | 2.31× / 4.47 |
| Qwen3-8B | 1 | DSpark | – | 5.16 | 2.64× / 5.24 |
| Qwen3-14B | 1 | DFlash | – | 4.44 | 2.76× / 4.53 |
| Qwen3-14B | 1 | DSpark | – | 5.26 | 3.13× / 5.25 |

The settings differ in ways that the papers state. The DFlash paper runs the Transformers backend on H200 GPUs with up to 2048 generated tokens, uses the EAGLE-3 checkpoints released by AngelSlim with tree drafting, and uses DFlash block size 16.[^chenDFlashBlockDiffusion2026] The DSpark paper retrains all three drafters in one framework on the same data, uses chain-based drafting with block size 7 (TTT horizon 7 for Eagle3), and reports only $\tau$.[^chengDSparkConfidenceScheduledSpeculative2026] The DPara paper uses batch size 1, draft length 7, and up to 512 new tokens on an H800 node.[^liuWhenParallelDrafter2026]


## Related

- Methods measured on it: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md), [PEARL](../methods/pearl.md), [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [Reflexion](../methods/reflexion.md)
- Serving engines used for the measurements: [SGLang](../methods/sglang.md)
- Datasets evaluated alongside it: [HumanEval](humaneval.md), [LiveCodeBench](livecodebench.md), [GSM8K](gsm8k.md), [MATH-500](math-500.md), [MT-Bench](mt-bench.md), [Alpaca](alpaca.md)

[^shinnReflexionLanguageAgents2023]: Shinn et al. 2023
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^muralidharanCompactLanguageModels2024]: Muralidharan et al. 2024
[^wangLeverSpeculativeLLM2026a]: Wang et al. 2026
[^elhoushiLayerSkipEnablingEarly2024]: Elhoushi et al. 2024
[^huAdaSPECSelectiveKnowledge2025]: Hu et al. 2025
[^yuIntrospectiveDiffusionLanguage2026]: Yu et al. 2026
