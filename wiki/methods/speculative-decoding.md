---
type: Method
title: Speculative Decoding
description: Lossless LLM inference acceleration in which a cheap drafter proposes several tokens and the target model verifies them in one parallel pass; hub page for the 17 papers in this wiki that change the drafter, the verification, the training, the system, or the deployment.
tags: [speculative-decoding, llm-inference, draft-model, verification, hub]
sources:
  - id: liEAGLE3ScalingInference2025
    resource: zotero://select/items/@liEAGLE3ScalingInference2025
    title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
  - id: samarinLKLossesDirect2026
    resource: zotero://select/items/@samarinLKLossesDirect2026
    title: "LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding"
  - id: chenDFlashBlockDiffusion2026
    resource: zotero://select/items/@chenDFlashBlockDiffusion2026
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: chengDSparkConfidenceScheduledSpeculative2026
    resource: zotero://select/items/@chengDSparkConfidenceScheduledSpeculative2026
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: liSpecForgeFlexibleEfficient2026
    resource: zotero://select/items/@liSpecForgeFlexibleEfficient2026
    title: "SpecForge: A Flexible and Efficient Open-Source Training Framework for Speculative Decoding"
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
  - id: kumarSpeculativeSpeculativeDecoding2026
    resource: zotero://select/items/@kumarSpeculativeSpeculativeDecoding2026
    title: Speculative Speculative Decoding
  - id: liuWhenParallelDrafter2026
    resource: zotero://select/items/@liuWhenParallelDrafter2026
    title: When Parallel Drafter Meets Parallel Speculative Decoding
  - id: oliaroSuffixDecodingExtremeSpeculative2024
    resource: zotero://select/items/@oliaroSuffixDecodingExtremeSpeculative2024
    title: "SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications"
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
  - id: weiSDFPSpeculativeDecoding2026
    resource: zotero://select/items/@weiSDFPSpeculativeDecoding2026
    title: "SDFP: Speculative Decoding with FIT-Pruned Models for Training-Free and Plug-and-Play LLM Acceleration"
  - id: yanDecodingSpeculativeDecoding2025
    resource: zotero://select/items/@yanDecodingSpeculativeDecoding2025
    title: Decoding Speculative Decoding
  - id: zhouDistillSpecImprovingSpeculative2024
    resource: zotero://select/items/@zhouDistillSpecImprovingSpeculative2024
    title: "DistillSpec: Improving Speculative Decoding via Knowledge Distillation"
  - id: svirschevskiSpecExecMassivelyParallel2024
    resource: zotero://select/items/@svirschevskiSpecExecMassivelyParallel2024
    title: "SpecExec: Massively Parallel Speculative Decoding for Interactive LLM Inference on Consumer Devices"
  - id: suSynergySpeculativeDecoding2023
    resource: zotero://select/items/@suSynergySpeculativeDecoding2023
    title: The Synergy of Speculative Decoding and Batching in Serving Large Language Models
  - id: parkSpecEdgeScalableEdgeAssisted2025
    resource: zotero://select/items/@parkSpecEdgeScalableEdgeAssisted2025
    title: "SpecEdge: Scalable Edge-Assisted Serving Framework for Interactive LLMs"
  - id: gaoCollaborativeSpeculativeInference
    resource: zotero://select/items/@gaoCollaborativeSpeculativeInference
    title: Collaborative Speculative Inference for Efficient LLM Inference Serving
---

# Speculative Decoding

## Overview

Speculative decoding (SD, also called speculative sampling or speculative inference) uses a faster draft model to generate several tokens, which the larger target model verifies in parallel, so that the generated text follows the target model's distribution.[^zhouDistillSpecImprovingSpeculative2024] It is a lossless acceleration technique that alternates between drafting, performed at low cost, and verification, which is parallelized.[^liEAGLE3ScalingInference2025]

This is the hub page for the topic. Seventeen papers in the wiki link here. The table in "Papers using it" says what each one changes, and "Reported speedups" compares their headline numbers with the settings behind them.

## How it works

### Draft and verify

- In the drafting stage, a draft model generates $k$ tokens autoregressively and records the probability $\hat{p}$ of each. In the verification stage, the target model evaluates the draft in one pass and records its probability $p$.[^liEAGLE3ScalingInference2025]
- Draft tokens are accepted sequentially, from front to back. A token is accepted with probability $\min(1, p/\hat{p})$. On the first rejection, a replacement token is sampled from $\text{norm}(\max(0, p-\hat{p}))$ and the remaining draft tokens are discarded.[^liEAGLE3ScalingInference2025]
- The round also yields a *bonus token*: a correction sampled at the first rejection, or an extra target sample after full acceptance.[^liuWhenParallelDrafter2026]
- The acceptance rate is $\alpha=\sum_{x\in\mathcal{V}}\min(q(x),p(x))$ for draft distribution $q$ and target distribution $p$, and $\alpha=1-\operatorname{TV}(p,q)$, where TV is the total variation distance.[^samarinLKLossesDirect2026]

### Speedup models

| Model | Source |
|---|---|
| Per-token latency $L=\frac{T_{\text{draft}}+T_{\text{verify}}}{\tau}$, where $\tau$ is the expected number of accepted tokens per cycle including the bonus token. An autoregressive drafter pays $T_{\text{draft}}=\gamma\cdot t_{\text{step}}$. | DFlash[^chenDFlashBlockDiffusion2026] |
| Three levers on the same formula: lower $T_{\text{draft}}$ (draft faster), raise $\tau$ (draft better), or reduce the effective $T_{\text{verify}}$ (verify smarter). | DSpark[^chengDSparkConfidenceScheduledSpeculative2026] |
| With i.i.d. acceptance rate $\alpha$, lookahead $\gamma$, and cost ratio $c=T_q/T_p$: $\text{Speedup}\approx\frac{1-\alpha^{\gamma+1}}{(1-\alpha)(1+\gamma c)}$. $c$ is hard to estimate because it depends on the serving stack. | Aurora[^wangWhenRLMeets2026] |
| Throughput $=TAR/(t^{d}_{target}+t^{d}_{draft})$ if $TAR>1$, where TAR is the tokens accepted per iteration. The maximum deviation from measured throughput is $3.5\%$. | Yan et al.[^yanDecodingSpeculativeDecoding2025] |
| Throughput of one draft-and-verify cycle $\lambda_{c}=L_{A}/T_{\text{total}}$. Draft time grows linearly with draft depth, and verification time grows step-wise with verification size. | Learning to Draft[^zhangLearningDraftAdaptive2026] |
| Round time with drafting overlapped with verification: $T_{\text{step}}\approx\max(T_{\text{verify}},T_{\text{precompute}})+T_{\text{Head}}$. | DPara[^liuWhenParallelDrafter2026] |

## Variants

SpecForge describes the draft model as having gone through three stages:[^liSpecForgeFlexibleEfficient2026]

1. **Independent draft model.** A smaller, independently trained language model, often from the same family as the target. Both models' parameters and KV caches must reside in GPU memory.[^liSpecForgeFlexibleEfficient2026]
2. **Multi-token prediction heads.** [Medusa](../methods/medusa.md) adds lightweight heads that run in parallel with the standard LM head and reuse the target model's features.[^liSpecForgeFlexibleEfficient2026]
3. **Feature-level extrapolation.** [EAGLE](../methods/eagle.md) shifts autoregression from token space to feature space with a lightweight single-layer Transformer. [EAGLE-2](../methods/eagle-2.md) shapes the draft tree dynamically by token-level confidence.[^liSpecForgeFlexibleEfficient2026] [EAGLE-3](../methods/eagle-3.md) then drops feature prediction for direct token prediction with [training-time test](../methods/training-time-test.md).[^liEAGLE3ScalingInference2025]

Other families that appear in the wiki's papers:

- **Parallel drafters.** [DFlash](../methods/dflash.md) drafts a whole block in one forward pass with a block diffusion model.[^chenDFlashBlockDiffusion2026] [DSpark](../methods/dspark.md) adds a lightweight sequential head to a parallel backbone.[^chengDSparkConfidenceScheduledSpeculative2026]
- **Native modules.** The [multi-token prediction](../methods/multi-token-prediction.md) (MTP) module of DeepSeek-V3 can be repurposed for speculation after training.[^samarinLKLossesDirect2026]
- **Model-free drafters.** SuffixDecoding drafts from suffix trees over the current request and prior outputs. Prompt-lookup decoding (PLD) and Token Recycling are the model-free baselines it compares against.[^oliaroSuffixDecodingExtremeSpeculative2024]
- **Drafts derived from the target.** SDFP prunes the target's least sensitive layers to form the draft, with no training.[^weiSDFPSpeculativeDecoding2026]
- **Tree drafts.** Several draft tokens are proposed at the same position and verified with tree attention ([tree-based speculation](../methods/tree-based-speculation.md)).[^liEAGLE3ScalingInference2025] [SpecExec](../methods/specexec.md) builds trees of up to thousands of tokens.[^svirschevskiSpecExecMassivelyParallel2024]
- **Parallel speculative decoding.** Drafting overlaps with verification instead of waiting for it, as in [speculative speculative decoding](../methods/speculative-speculative-decoding.md), [PEARL](../methods/pearl.md), and DPara.[^kumarSpeculativeSpeculativeDecoding2026][^liuWhenParallelDrafter2026]
- **Lossy SD.** DistillSpec extends to lossy SD for control over the quality-latency trade-off.[^zhouDistillSpecImprovingSpeculative2024] The EAGLE-3 paper notes that methods like Medusa relax acceptance conditions under non-greedy settings, which does not guarantee lossless acceleration.[^liEAGLE3ScalingInference2025]

## Papers using it

"Changes" names the part of the pipeline the paper modifies: drafter, verification, training, system, or deployment.

| Paper | Changes | What it does | Key reported result |
|---|---|---|---|
| [Su et al. 2023](../papers/suSynergySpeculativeDecoding2023.md) | system | Studies batching together with SD. The optimal speculation length depends on the batch size, and an adaptive scheme picks the length for each batch.[^suSynergySpeculativeDecoding2023] | An extra 9% latency reduction for time-varying requests compared with a fixed speculation length.[^suSynergySpeculativeDecoding2023] |
| [DistillSpec](../papers/zhouDistillSpecImprovingSpeculative2024.md) ([method](../methods/distillspec.md)) | training | White-box [knowledge distillation](../methods/knowledge-distillation.md) that aligns the draft with the target, with on-policy data and a task-specific divergence.[^zhouDistillSpecImprovingSpeculative2024] | $10-45\%$ speedups over standard SD.[^zhouDistillSpecImprovingSpeculative2024] |
| [SpecExec](../papers/svirschevskiSpecExecMassivelyParallel2024.md) ([method](../methods/specexec.md)) | drafter, verification, deployment | Builds a large deterministic draft tree with a capable draft model and validates it as a cache in one target pass, for offloaded inference on consumer GPUs. The baseline is [SpecInfer](../methods/specinfer.md).[^svirschevskiSpecExecMassivelyParallel2024] | Up to 20 tokens per target model iteration, and 10-18x speedups over sequential inference on the same hardware.[^svirschevskiSpecExecMassivelyParallel2024] |
| [SuffixDecoding](../papers/oliaroSuffixDecodingExtremeSpeculative2024.md) | drafter | Model-free drafting from suffix trees, with speculation length adapted to the pattern match length, and a hybrid mode that falls back to EAGLE-3.[^oliaroSuffixDecodingExtremeSpeculative2024] | 5.345 speedup on AgenticSQL and 2.452 on SWE-Bench traces for suffix (linear).[^oliaroSuffixDecodingExtremeSpeculative2024] |
| [Yan et al. 2025](../papers/yanDecodingSpeculativeDecoding2025.md) | drafter | Over 350 experiments on draft model choice. Draft latency, bottlenecked by depth, matters more than language modeling capability. Proposes wide and shallow drafts pruned with [Sheared-LLaMA](../methods/sheared-llama.md).[^yanDecodingSpeculativeDecoding2025] | NoFT-Wide-796M has $97.7\%$ to $111.8\%$ higher throughput than Sheared-LLaMA-1.3B.[^yanDecodingSpeculativeDecoding2025] |
| [EAGLE-3](../papers/liEAGLE3ScalingInference2025.md) ([method](../methods/eagle-3.md)) | drafter, training | Direct token prediction from fused multi-layer target features, trained with training-time test.[^liEAGLE3ScalingInference2025] | Speedup ratio up to 6.5x, about 1.4x over EAGLE-2.[^liEAGLE3ScalingInference2025] |
| [CoSine](../papers/gaoCollaborativeSpeculativeInference.md) | system, deployment | Decouples drafting from verification across nodes: a cluster of consumer-grade GPUs drafts with specialized drafters, and a server of datacenter-grade GPUs verifies.[^gaoCollaborativeSpeculativeInference] | Up to a 23.2% decrease in latency and a 32.5% increase in throughput at equivalent resource costs.[^gaoCollaborativeSpeculativeInference] |
| [SpecEdge](../papers/parkSpecEdgeScalableEdgeAssisted2025.md) | deployment, system | Edge GPUs draft and the server verifies, exchanging only tokens. Proactive edge drafting overlaps with server verification. The draft tree follows [Sequoia](../methods/sequoia.md) and SpecExec.[^parkSpecEdgeScalableEdgeAssisted2025] | 1.91× better cost efficiency through 2.22× server throughput, and 11.24% lower inter token latency than server-only SD.[^parkSpecEdgeScalableEdgeAssisted2025] |
| [SDFP](../papers/weiSDFPSpeculativeDecoding2026.md) | drafter | Training-free draft made by pruning the target's layers, ranked by Fisher Information Trace.[^weiSDFPSpeculativeDecoding2026] | Overall speedups of $1.31\times$ to $1.46\times$ on LLaMA-2 models.[^weiSDFPSpeculativeDecoding2026] |
| [DFlash](../papers/chenDFlashBlockDiffusion2026.md) ([method](../methods/dflash.md)) | drafter, training | Block diffusion drafter conditioned on target features through [KV injection](../methods/kv-injection.md).[^chenDFlashBlockDiffusion2026] | Average 4.9× speedup under greedy decoding on Qwen3, a 2.4× improvement over EAGLE-3 (16).[^chenDFlashBlockDiffusion2026] |
| [LK losses](../papers/samarinLKLossesDirect2026.md) | training | Losses that optimize the acceptance rate directly instead of KL divergence.[^samarinLKLossesDirect2026] | Gains of up to 8-10% in average acceptance length.[^samarinLKLossesDirect2026] |
| [Aurora](../papers/wangWhenRLMeets2026.md) | training, system | Trains the speculator online from live inference traces and hot-swaps updates into an SGLang server.[^wangWhenRLMeets2026] | 1.57× on MiniMax M2.1 and 1.51× on Qwen3-Coder-Next at batch size 1, against serving without speculation.[^wangWhenRLMeets2026] |
| [Learning to Draft](../papers/zhangLearningDraftAdaptive2026.md) | drafter, verification | Two RL policies choose the draft tree depth and the verification size, with per-cycle throughput as the reward, on top of Eagle3.[^zhangLearningDraftAdaptive2026] | Speedup ratios from 2.24× to 4.32×, up to 36.4% over Eagle3.[^zhangLearningDraftAdaptive2026] |
| [Speculative Speculative Decoding](../papers/kumarSpeculativeSpeculativeDecoding2026.md) ([method](../methods/speculative-speculative-decoding.md)) | system | Drafts in parallel with verification by pre-speculating for predicted verification outcomes on a separate device.[^kumarSpeculativeSpeculativeDecoding2026] | SSD/SD of 1.58× and SSD/AR of 4.68× on average for Llama-3.1-Instruct 70B/1B.[^kumarSpeculativeSpeculativeDecoding2026] |
| [SpecForge](../papers/liSpecForgeFlexibleEfficient2026.md) | training, system | Training framework for EAGLE-3 draft models that runs the target on SGLang and trains the draft separately. Releases the SpecBundle draft models.[^liSpecForgeFlexibleEfficient2026] | Up to 9.99× faster training, and up to 4.48× inference speedup on SGLang.[^liSpecForgeFlexibleEfficient2026] |
| [DSpark](../papers/chengDSparkConfidenceScheduledSpeculative2026.md) ([method](../methods/dspark.md)) | drafter, verification, deployment | Semi-autoregressive drafter plus a scheduler that sets each request's verification length from calibrated confidence and engine load. Deployed in the DeepSeek-V4 serving system.[^chengDSparkConfidenceScheduledSpeculative2026] | 60%–85% (V4-Flash) and 57%–78% (V4-Pro) faster per-user generation than MTP-1 at matched aggregate throughput.[^chengDSparkConfidenceScheduledSpeculative2026] |
| [DPara](../papers/liuWhenParallelDrafter2026.md) | system, drafter | Precomputes the diffusion drafter backbone for every acceptance boundary during verification, so only a light autoregressive head stays on the critical path.[^liuWhenParallelDrafter2026] | Average speedups of 3.21× (Qwen3-8B) and 3.52× (Qwen3-14B) over autoregressive decoding.[^liuWhenParallelDrafter2026] |

## Reported speedups

Speedups are over autoregressive decoding of the same target unless the "Baseline" column says otherwise. The rows are not comparable with each other: targets, hardware, engines, batch sizes, and temperatures all differ.

| Paper | Speedup | Target (draft) | Hardware and engine | Batch, temperature | Baseline |
|---|---|---|---|---|---|
| DistillSpec | 1.44× → 1.58× with distillation (XSum, $\gamma=3$) | T5-XL 3B (T5-Small 77M) | TPUv4 | batch size 1, T=0 | autoregressive target[^zhouDistillSpecImprovingSpeculative2024] |
| Su et al. | $1.93\times$ at speculation length 3 | OPT-6.7B | RTX 3090 | batch size 4 | no speculation[^suSynergySpeculativeDecoding2023] |
| SpecExec | 18.7x (budget 2048, 3.12 tok/s) | Llama 2-70B (Llama 2-7B) | A100 with RAM offloading | batch size 1, t=0.6, OAsst | sequential offloaded inference[^svirschevskiSpecExecMassivelyParallel2024] |
| SpecExec | 8.3x (5.66 tok/s) | Llama 2 70B-GPTQ (Llama 2-7B) | RTX 4090 with offloading | batch size 1, t=0.6, OAsst | sequential offloaded inference[^svirschevskiSpecExecMassivelyParallel2024] |
| SDFP | $1.40\times$, $1.31\times$, $1.46\times$ overall | LLaMA-2-13B, 13B-Chat, 70B (pruned self) | not stated | batch size 1, greedy | vanilla autoregressive[^weiSDFPSpeculativeDecoding2026] |
| EAGLE-3 | 5.51x, 4.44x, 4.12x, 4.16x mean | Vicuna 13B, LLaMA-Instruct 3.1 8B, LLaMA-Instruct 3.3 70B, DeepSeek-R1-Distill-LLaMA 8B | hardware not stated, Huggingface.transformers | temperature 0, tree draft | vanilla autoregressive[^liEAGLE3ScalingInference2025] |
| EAGLE-3 | 1.81x at batch size 2, 1.38x at batch size 64 | LLaMA-Instruct 3.1 8B | single H100, [SGLang](../methods/sglang.md) v0.4.4 | chain length 3, MT-Bench | SGLang without speculation[^liEAGLE3ScalingInference2025] |
| SuffixDecoding | 5.345 (AgenticSQL), 2.452 (SWE-Bench), 1.659 ([Spec-Bench](../benchmarks/spec-bench.md)) | Llama-3.1-8B-Instruct (suffix trees) | single H100, Spec-Bench codebase | batch size 1 | vanilla decoding[^oliaroSuffixDecodingExtremeSpeculative2024] |
| SuffixDecoding hybrid | 2.500 (Spec-Bench, linear), 4.068 (AgenticSQL, tree) | Llama-3.1-8B-Instruct (suffix trees + EAGLE-3) | single H100, Spec-Bench codebase | batch size 1 | vanilla decoding[^oliaroSuffixDecodingExtremeSpeculative2024] |
| DFlash | 4.91× (Q3-4B), 4.86× (Q3-8B) average | Qwen3-4B, Qwen3-8B (5-layer block diffusion) | H200, Transformers backend | temperature 0, block size 16 | autoregressive[^chenDFlashBlockDiffusion2026] |
| DFlash | 4.8× at concurrency 1, 2.9× at concurrency 32 | Qwen3-4B, Math500 | single B200, SGLang | concurrency 1 to 32 | SGLang baseline[^chenDFlashBlockDiffusion2026] |
| LK losses | $\tau$ / speedup 3.84 / 2.62 (MT-Bench), 4.89 / 3.35 (HumanEval), 4.57 / 3.10 (GSM8K) | LLaMA 3.1 8B Instruct (EAGLE-3 head, LK loss $\eta=3$) | [vLLM](../methods/vllm.md) v0.11.0 | batch size 1, T=0, chain $K=7$ | no speculative decoding[^samarinLKLossesDirect2026] |
| Learning to Draft | 3.92, 4.32, 4.16, 2.37, 2.47 mean | Llama-3.1-8B-Instruct, Vicuna-13B-v1.3, DeepSeek-R1-Distill-LLaMA 8B, Qwen3-14B, Qwen3-32B (Eagle3) | single NVIDIA A100 | temperature 0 | vanilla autoregressive[^zhangLearningDraftAdaptive2026] |
| SSD (Saguaro) | 4.68× average (255.8 vs 54.7 tok/s) | Llama-3.1-Instruct 70B (1B) | target on 4×H100, draft on 1×H100, custom engine | batch size 1, greedy | own autoregressive implementation[^kumarSpeculativeSpeculativeDecoding2026] |
| SSD (Saguaro) | 2.29× average (203.8 vs 88.8 tok/s) | Qwen-3 32B (0.6B) | target on 4×H100, draft on 1×H100, custom engine | batch size 1, greedy | own autoregressive implementation[^kumarSpeculativeSpeculativeDecoding2026] |
| SpecForge (SpecBundle) | 1.81 to 3.34 across seven benchmarks, except 1.39 on FinanceQA | Llama-3.1-8B (EAGLE-3) | 1 H200, SGLang | 8 concurrent requests | target model alone[^liSpecForgeFlexibleEfficient2026] |
| SpecForge (SpecBundle) | 4.48 (LiveCodeBench) | Llama-4-Scout (EAGLE-3) | 8 H200, SGLang | 16 concurrent requests | target model alone[^liSpecForgeFlexibleEfficient2026] |
| Aurora | 1.57× (batch size 1), 1.25× (batch size 32) | MiniMax M2.1 (Aurora speculator) | 4×H200, SGLang, FP8 | lookahead 4 | without speculation[^wangWhenRLMeets2026] |
| DPara | 3.21×, 3.52× average | Qwen3-8B, Qwen3-14B (M-DFlash backbone + AR head) | NVIDIA H800, one additional GPU for drafting | batch size 1, greedy, draft length 7 | autoregressive[^liuWhenParallelDrafter2026] |
| DPara (its baselines) | DSpark 2.89×, DFlash 2.70×, EAGLE3 1.44× average | Qwen3-8B | NVIDIA H800 | batch size 1, greedy, draft length 7 | autoregressive[^liuWhenParallelDrafter2026] |
| CoSine | normalized throughput $3.15\times$ to $4.71\times$ | DeepSeek-R1-Distill-Llama-70B (LLaMA68M drafters) | four A100 plus consumer-grade GPUs | batch sizes 1 to 16, greedy | vLLM[^gaoCollaborativeSpeculativeInference] |

Results reported against another speculative decoding setup, not against autoregressive decoding:

| Paper | Result | Setting | Reference |
|---|---|---|---|
| Yan et al. | $97.7\%$ to $111.8\%$ higher throughput | LLaMa-65B target, NoFT-Wide-796M draft, temperature sampling, 4 Nvidia 80GB A100 GPUs | Sheared-LLaMA-1.3B draft[^yanDecodingSpeculativeDecoding2025] |
| SpecEdge | 1.91× cost efficiency, 2.22× server throughput | server A100, edge RTX4090 GPUs, 14.07ms average round-trip time, SpecBench | server-only tree-based SD[^parkSpecEdgeScalableEdgeAssisted2025] |
| DSpark | 60%–85% (V4-Flash) and 57%–78% (V4-Pro) faster per-user generation | DeepSeek-V4 production engines under live traffic, matched aggregate throughput | MTP-1[^chengDSparkConfidenceScheduledSpeculative2026] |
| DSpark | accepted length +30.9%, +26.7%, +30.0% over Eagle3 and +16.3%, +18.4%, +18.3% over DFlash | Qwen3-4B, 8B, 14B, temperature $1.0$, chain drafting, offline | retrained Eagle3 and DFlash[^chengDSparkConfidenceScheduledSpeculative2026] |
| Su et al. | extra 9% latency reduction | OPT-6.7B with OPT-125M, RTX 3090, time-varying requests | fixed speculation length[^suSynergySpeculativeDecoding2023] |
| SSD (Saguaro) | 1.58× and 1.49× on average | Llama-3.1-Instruct 70B/1B and Qwen-3 32B/0.6B, batch size 1 | own SD implementation[^kumarSpeculativeSpeculativeDecoding2026] |
| CoSine | throughput $1.31\times$ to $1.62\times$ | LLaMA pair, batch sizes 1 to 16 | SpecInfer[^gaoCollaborativeSpeculativeInference] |

SpecForge also cites an early demonstration of speedups of up to 3.4× on T5-XXL.[^liSpecForgeFlexibleEfficient2026]

## Strengths & Limitations

Strengths:

- The output distribution of the target is preserved. The EAGLE-3 paper points to Appendix A.1 of Leviathan et al. 2023 for the proof.[^liEAGLE3ScalingInference2025] SuffixDecoding uses this to match the original model's 37.2% score on SWE-Bench Verified.[^oliaroSuffixDecodingExtremeSpeculative2024]
- It fits bandwidth-bound settings: with offloading, hundreds or thousands of tokens can be processed in a batch within the same time as one token.[^svirschevskiSpecExecMassivelyParallel2024]
- Drafting and verification can be split across devices, with only tokens or small messages exchanged.[^parkSpecEdgeScalableEdgeAssisted2025][^kumarSpeculativeSpeculativeDecoding2026]

Limitations:

- **Batch size.** Larger batch sizes need a smaller speculation length, and a speculation length that is too large deteriorates performance.[^suSynergySpeculativeDecoding2023] As batch sizes increase, the redundant computational power that speculative sampling exploits decreases.[^liEAGLE3ScalingInference2025] SSD states that speculative decoding is generally ineffective for throughput-bound workloads.[^kumarSpeculativeSpeculativeDecoding2026] For Qwen3-Coder-Next at batch size 32, Aurora measures speculation at 0.93× to 0.94× of the baseline.[^wangWhenRLMeets2026]
- **Draft acquisition.** SDFP argues that acquiring, tuning, and maintaining the draft model is the primary barrier to deployment.[^weiSDFPSpeculativeDecoding2026] SpecForge names limited availability and poor quality of open-source draft models.[^liSpecForgeFlexibleEfficient2026]
- **Acceptance does not scale with budget.** In SpecExec's analysis, the number of accepted tokens with existing methods is empirically upper-bounded (approximately by 10 for Llama 2-7B / Llama 2-70B on MTBench) regardless of the number of speculated tokens.[^svirschevskiSpecExecMassivelyParallel2024]
- **Drafting is on the critical path.** Under the sequential draft-verify schedule, drafting accounts for 24%–32% of end-to-end latency for parallel drafters.[^liuWhenParallelDrafter2026]
- **Domain drift.** A speculator trained offline degrades when the traffic shifts.[^wangWhenRLMeets2026]
- **Resource contention.** Drafting is memory-bound and verification is compute-bound, so co-locating them causes contention.[^gaoCollaborativeSpeculativeInference]
- **Repetitive workloads.** Model-based methods can use significant GPU time when speculating long, predictable sequences.[^oliaroSuffixDecodingExtremeSpeculative2024]

# Contradictions

1. **EAGLE-3 baseline numbers.** Later papers measure EAGLE-3 at much lower speedups than its own paper (for example 4.40x on MT-bench for LLaMA-Instruct 3.1 8B in the original against 3.70 in Learning to Draft and 2.42 for the yuhuili checkpoint in LK losses).[^liEAGLE3ScalingInference2025][^zhangLearningDraftAdaptive2026][^samarinLKLossesDirect2026] The full list with settings is on the [EAGLE-3 page](../methods/eagle-3.md).

2. **What determines the speedup.** LK losses states that the speedup is largely determined by the acceptance rate.[^samarinLKLossesDirect2026] Yan et al. find that performance depends heavily on the latency of the draft model, and that the draft's language modeling capability does not correlate strongly with its speculative decoding performance.[^yanDecodingSpeculativeDecoding2025] Aurora states that end-to-end speedup cannot be inferred reliably from acceptance rate alone.[^wangWhenRLMeets2026] Three measurements support the second view: DPara has a lower average acceptance length than DSpark (4.43 vs 5.36 on Qwen3-8B) and a higher speedup (3.21× vs 2.89×);[^liuWhenParallelDrafter2026] Learning to Draft often has a shorter $\tau$ than grid search with a higher speedup;[^zhangLearningDraftAdaptive2026] and EAGLE-3 (60) has a higher $\tau$ than DFlash (10) on GSM8K with a lower speedup.[^chenDFlashBlockDiffusion2026] The claims are made in different contexts: LK losses compares training objectives for a fixed draft architecture, where draft latency is constant.

3. **Speculation at large batch sizes.** The EAGLE-3 paper reports a 1.38x throughput improvement at batch size 64 in SGLang and argues against the view that speculative sampling reduces throughput at large batch sizes.[^liEAGLE3ScalingInference2025] DFlash measures the official EAGLE-3 checkpoint in SGLang at 0.5× to 0.6× of the baseline at concurrency 32 with 60 draft tokens, and 0.9× to 1.2× with 10 draft tokens.[^chenDFlashBlockDiffusion2026] Aurora measures 0.93× to 0.94× at batch size 32 for Qwen3-Coder-Next.[^wangWhenRLMeets2026] Setting differences: the EAGLE-3 result uses a chain of length 3 on an H100 with SGLang v0.4.4; DFlash uses a tree with 7 draft steps on a B200; Aurora uses a different target model and FP8.

4. **Parallel SD under batching.** SSD states that Saguaro outperforms SD by 20% even at larger batch sizes.[^kumarSpeculativeSpeculativeDecoding2026] DPara measures that at batch size 16 the SSD fallback rate reaches 57%–96% of steps on Qwen3-14B.[^liuWhenParallelDrafter2026] DPara's SSD numbers come from its own setup (Qwen3-14B with a Qwen3-0.6B draft, H800), not from the SSD paper's models.

5. **Autoregressive vs parallel drafters.** DFlash reports a higher acceptance length than EAGLE-3 on every Qwen3 benchmark.[^chenDFlashBlockDiffusion2026] DSpark, with all drafters retrained on the same data, finds Eagle3 above DFlash in every column on Gemma4-12B.[^chengDSparkConfidenceScheduledSpeculative2026]

## Related

- Draft architectures: [EAGLE](../methods/eagle.md), [EAGLE-2](../methods/eagle-2.md), [EAGLE-3](../methods/eagle-3.md), [Medusa](../methods/medusa.md), [Multi-token prediction](../methods/multi-token-prediction.md), [DFlash](../methods/dflash.md), [DSpark](../methods/dspark.md)
- Draft trees: [Tree-based speculation](../methods/tree-based-speculation.md), [SpecExec](../methods/specexec.md), [Sequoia](../methods/sequoia.md), [SpecInfer](../methods/specinfer.md)
- Parallel speculative decoding: [Speculative speculative decoding](../methods/speculative-speculative-decoding.md), [PEARL](../methods/pearl.md)
- Draft training: [Training-time test](../methods/training-time-test.md), [DistillSpec](../methods/distillspec.md), [Knowledge distillation](../methods/knowledge-distillation.md), [KV injection](../methods/kv-injection.md)
- Draft construction by pruning: [Sheared-LLaMA](../methods/sheared-llama.md), [Structured pruning](../methods/structured-pruning.md)
- Serving engines: [SGLang](../methods/sglang.md), [vLLM](../methods/vllm.md), [Continuous batching](../methods/continuous-batching.md)
- Benchmarks and datasets: [Spec-Bench](../benchmarks/spec-bench.md), [MT-Bench](../datasets/mt-bench.md), [HumanEval](../datasets/humaneval.md), [GSM8K](../datasets/gsm8k.md)

## Open questions and results

- [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md)
- [Does speculative decoding still help at large batch sizes?](../questions/speculative-decoding-at-large-batch.md)
- [Speculative decoding speedup vs batch size](../results/speculative-decoding-speedup-vs-batch-size.md)

[^liEAGLE3ScalingInference2025]: Li et al. 2025
[^samarinLKLossesDirect2026]: Samarin et al. 2026
[^chenDFlashBlockDiffusion2026]: Chen et al. 2026
[^chengDSparkConfidenceScheduledSpeculative2026]: Cheng et al. 2026
[^liSpecForgeFlexibleEfficient2026]: Li et al. 2026
[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
[^kumarSpeculativeSpeculativeDecoding2026]: Kumar et al. 2026
[^liuWhenParallelDrafter2026]: Liu et al. 2026
[^oliaroSuffixDecodingExtremeSpeculative2024]: Oliaro et al. 2024
[^wangWhenRLMeets2026]: Wang et al. 2026
[^weiSDFPSpeculativeDecoding2026]: Wei et al. 2026
[^yanDecodingSpeculativeDecoding2025]: Yan et al. 2025
[^zhouDistillSpecImprovingSpeculative2024]: Zhou et al. 2024
[^svirschevskiSpecExecMassivelyParallel2024]: Svirschevski et al. 2024
[^suSynergySpeculativeDecoding2023]: Su et al. 2023
[^parkSpecEdgeScalableEdgeAssisted2025]: Park et al. 2025
[^gaoCollaborativeSpeculativeInference]: Gao et al. (year not stated)
