---
type: Paper
title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
description: Aurora, a unified training-serving system that trains a speculative-decoding draft model online from live inference traces as an asynchronous RL problem and hot-swaps updates into an SGLang server.
tags: [speculative-decoding, online-training, draft-model, llm-serving, asynchronous-rl, domain-shift, mobile-specedge, speculative-drafter]
collections: ["mobile-specedge", "speculative drafter"]
authors: [Junxiong Wang, Fengxiang Bie, Jisen Li, Zhongzhu Zhou, Zelei Shao, Qingyang Wu, Yinghui Liu, Yubo Wang, Avner May, Sri Yanamandra, Tri Dao, Percy Liang, Ce Zhang, Ben Athiwaratkun, Shuaiwen Leon Song, Chenfeng Xu, Xiaoxia Wu]
doi: 10.48550/arXiv.2602.06932
arxiv: "2602.06932"
arxiv_version: 2602.06932v5
website: https://aurora-spec-ai.github.io/
sources:
  - id: wangWhenRLMeets2026
    resource: zotero://select/items/@wangWhenRLMeets2026
    title: "When RL Meets Adaptive Speculative Training: A Unified Training-Serving System"
---

# When RL Meets Adaptive Speculative Training: A Unified Training-Serving System

Text source: arXiv HTML, version `2602.06932v5`.

## Summary

Most [speculative decoding](../methods/speculative-decoding.md) deployments train the speculator (draft model) offline and serve it separately.[^wangWhenRLMeets2026] The paper argues this causes high time-to-serve, delayed utility feedback (end-to-end speedup cannot be inferred reliably from acceptance rate alone), and degradation under domain drift.[^wangWhenRLMeets2026]

[Aurora](../methods/aurora.md) is a unified training-serving system that continuously learns a speculator from live inference traces.[^wangWhenRLMeets2026] It frames online speculator learning as an [asynchronous reinforcement-learning](../methods/asynchronous-rl.md) problem in which accepted tokens give positive feedback and rejected proposals give implicit negative feedback, and it couples an [SGLang](../methods/sglang.md)-based inference server with an asynchronous training server that hot-swaps speculator updates without service interruption.[^wangWhenRLMeets2026] The abstract reports a 1.5× day-0 speedup on recently released frontier models (MiniMax M2.1 229B and Qwen3-Coder-Next 80B) and an additional 1.25× speedup over a well-trained but static speculator on Qwen3 and Llama3.[^wangWhenRLMeets2026]

## Contributions

- Day-0 serving and real-time observability: a speculator can be deployed from scratch and adapted in situ, turning "train-then-serve" into a "serve-to-train" flywheel.[^wangWhenRLMeets2026]
- Fast adaptation to new traffic, with a reported 1.25× improvement over a strong offline training baseline.[^wangWhenRLMeets2026]
- Reduced infrastructure memory footprint and cost, by removing large-scale activation-collection and replay pipelines.[^wangWhenRLMeets2026]
- Support for heterogeneous request mixtures (online traffic plus offline corpora) and scaling to large GPU deployments.[^wangWhenRLMeets2026]
- An algorithm-agnostic framework that is not tied to a specific speculator.[^wangWhenRLMeets2026]

## Method

### Background

Under the i.i.d. acceptance approximation, with acceptance rate $\alpha$ and lookahead $\gamma$, the expected number of tokens per verifier step is $\mathbb{E}[L] = \frac{1-\alpha^{\gamma+1}}{1-\alpha}$ (Eq. 1). With cost ratio $c = T_q/T_p$ (draft-step time over target-step time), $\text{Speedup} \approx \frac{1-\alpha^{\gamma+1}}{(1-\alpha)(1+\gamma c)}$ (Eq. 2).[^wangWhenRLMeets2026] The paper states that $c$ is hard to estimate because it depends on the serving stack.[^wangWhenRLMeets2026]

The paper contrasts Aurora with [Online Speculative Decoding (OSD)](../methods/online-speculative-decoding.md): Aurora closes three feedback paths (online training on verifier outputs, pushing new speculators back into serving, feeding serving signals back into training), while OSD is described as open-loop and addresses only the first.[^wangWhenRLMeets2026]

### Architecture

- **Inference Server.** Runs an SGLang speculative decoding engine with a target model and a draft model. Accepted and rejected tokens are streamed to a distributed data buffer; hidden states are also sent to support [EAGLE](../methods/eagle-3.md)-style training.[^wangWhenRLMeets2026]
- **Training Server.** Runs asynchronously, fetches batches from the data buffer, performs gradient updates on a copy of the draft model, and pushes new weights back as a hot-swap.[^wangWhenRLMeets2026]
- **Implementation.** Batched RPC transfers use `torch.distributed.rpc` with the TensorPipe backend and expandable CUDA memory segments. The actor-learner design is realized in [AReaL](../methods/areal.md), with SGLang replicas as actors.[^wangWhenRLMeets2026]
- **[Tree Attention](../methods/tree-attention.md).** A custom attention mask that respects the causal structure of the speculative tree, so all accepted and rejected branches are processed in a single batched forward and backward pass.[^wangWhenRLMeets2026]
- **Lazy synchronization.** Limited staleness is accepted to avoid interrupting the inference critical path.[^wangWhenRLMeets2026]
- **Zero-copy target model design.** The inference server transmits $\mathcal{D}_{\text{RPC}}=\{(h_{t}^{(l)},\ell_{t},x_{\text{in}},y_{\text{out}},\mathcal{R})\}$ (Eq. 4), where $h_t^{(l)}$ concatenates hidden states from three target layers (early, middle, late), so training nodes load only the draft model (∼1B) and not the target model (8B to 70B).[^wangWhenRLMeets2026]
- **Inference-side memory overhead.** $M_{\text{aux}}=B\times(T\times 3d\times 2+T_{\text{output}}\times V\times 2)$ bytes (Eq. 5). Transmitting logits only over the draft vocabulary gives a 4× to 5× reduction (e.g., 32K vs 128K for Llama3 models and 32K vs 152K for Qwen3 models). Top-$K$ logits filtering (e.g., $K=1024$) reduces per-token logit storage from 256 KB to 2 KB (a 128× reduction).[^wangWhenRLMeets2026]
- Multiple inference servers can feed a single training server, aggregated through thread-safe LRU caching.[^wangWhenRLMeets2026]

### Training objective

The draft model is the policy $\pi$ and the target model plus verifier are the environment. Maximizing expected return is equivalent to maximizing acceptance length.[^wangWhenRLMeets2026]

$$
\mathcal{L}=\mathbb{E}_{x\sim p_{\text{accept}}}[\text{KL}(p_{\text{target}}\|p_{\text{draft}})]+\lambda_{\text{discard}}\,\mathbb{E}_{x\sim p_{\text{discard}}}[\text{KL}(p_{\text{target}}\|p_{\text{draft}})]
$$

The first term trains on accepted sequences. The second term, [Discard Sampling](../methods/discard-sampling.md), trains on rejected sequences, with top-$k$ filtering applied to discarded tokens (Eq. 3).[^wangWhenRLMeets2026]

### Hyperparameters (Table 3)

| Parameter | Value |
|---|---|
| Learning Rate | $10^{-5}$/$10^{-4}$ (finetuning / training from scratch) |
| Warmup Steps | 400 |
| Global Batch Size | 8 |
| Draft/Target Micro-batch | 1 / 4 |
| Optimizer | AdamW |
| Weight Decay | 0.0 |
| Gradient Clipping | 0.5 |
| Precision | BF16 + FP32 |
| Max Sequence Length | 2,048 |
| TTT Length | 5 |
| Top-$k$ Filter (discard) | 10 |
| Discard Loss Weights ($\lambda$) | 1.0 |
| Divergence | Reverse KL |
| Speculative Steps | 5 |
| Top-$k$ Sampling | 1 |
| Draft Tokens per Step | 6 |

All rows: [^wangWhenRLMeets2026]

Gradient updates are triggered every 100 inference requests.[^wangWhenRLMeets2026]

## Experiments & Results

### Setup

- The request stream is a fixed corpus of prompts consumed sequentially; no ground-truth assistant responses are used.[^wangWhenRLMeets2026]
- Traffic patterns: ordered streams (grouped by domain, abrupt shift) and mixed streams (randomly shuffled).[^wangWhenRLMeets2026]
- Speculative decoding framework: [EAGLE-3](../methods/eagle-3.md). Target model for the day-0 study: Qwen3-8B; the draft model is initialized with random weights.[^wangWhenRLMeets2026]
- Hardware: Qwen-8B and Llama-8B experiments on H100 GPUs; MiniMax M2.1 and Qwen3-Coder-Next on H200 GPUs. The target model is placed on GPUs 0-3 and the draft model is trained on a separate GPU.[^wangWhenRLMeets2026]
- Metric: per-request throughput, $(T_{\text{input}}+T_{\text{output}})/t_{\text{request}}$ in tokens/s (Eq. 7), and speculative acceptance length.[^wangWhenRLMeets2026]

Dataset composition (Table 2):[^wangWhenRLMeets2026]

| Domain | Source | Samples |
|---|---|---|
| Mathematical Reasoning | [GSM8K](../datasets/gsm8k.md) | 7k |
| Text-to-SQL | [Spider](../datasets/spider.md) | 7k |
| Code | [CodeSearchNet](../datasets/codesearchnet.md) | 10k |
| Finance | [Finance-Alpaca](../datasets/finance-alpaca.md) | 10k |
| Conversational Instructions | [chatbot_instruction_prompts](../datasets/chatbot-instruction-prompts.md) | 10k |
| Total | | 44k |

### Day-0 speculator (Qwen3-8B)

| Traffic | Configuration | Acceptance length | Throughput |
|---|---|---|---|
| Mixed | Aurora (scratch) | 3.08 | 302.3 tokens/s |
| Mixed | Static baseline | 2.63 | not stated |
| Mixed | Pretrained-then-finetuned baseline | 2.99 | not stated |
| Domain shift (ordered) | Aurora (scratch) | 2.46 within approximately 10,000 requests | 295.6 tokens/s |
| Domain shift (ordered) | Pretrained baseline / static speculator | 2.57 | 288.8 tokens/s |

All rows: [^wangWhenRLMeets2026]

### Synchronization policy

The policy update interval is swept from every 48 requests to every 1600 requests under a stream with an abrupt domain shift. Aggressive updates recover acceptance length faster but have the lowest throughput.[^wangWhenRLMeets2026] The body text states a moderately lazy schedule (every 80 requests) gives the best overall throughput, even surpassing the baseline.[^wangWhenRLMeets2026]

### Training objective study

- Variants: Frozen Draft (static baseline), Aurora (FKL), Aurora (RKL), Aurora (RKL + NTP), Aurora (w discard).[^wangWhenRLMeets2026]
- Online fine-tuning consistently beats the static baseline; adding NTP and discarded tokens yields only marginal additional improvements under domain shift.[^wangWhenRLMeets2026]
- With lookahead = 5 the pretrained speculator already had an acceptance length of ∼3.6. With lookahead = 10 (Llama-3.1-8B-Instruct, coding), learning from discarded tokens yields greater gains over accept-only fine-tuning, while top-$k$ = 0, 10, 50 differ only marginally.[^wangWhenRLMeets2026]
- Reducing batch size from 12 to 4: the relative throughput uplift is greater for batch size 4 than for batch size 12.[^wangWhenRLMeets2026]

### Frontier models

- MiniMax M2.1: 229B-parameter decoder-only Transformer-MoE, 62 layers, 256-expert router (top-8 per token), native context window of 196 K tokens; served on 4×H200 with TP=4 in FP8, plus one GPU for online speculator tuning. Aurora (Scratch) raises mean accepted draft length to 2.8, about 1.45× speedup.[^wangWhenRLMeets2026]
- Qwen3-Coder-Next: MoE with 80B total parameters and 3B activated parameters, 48 layers, 262K native context length; served on 4×H200 with TP=4 and EP=4 in FP8. The body text reports acceptance beyond 3 and 1.23× throughput improvement.[^wangWhenRLMeets2026]

End-to-end throughput by batch size (Table 1; TPS). MiniMax M2.1 uses lookahead 4; Qwen3-Coder-Next uses lookahead 5.[^wangWhenRLMeets2026]

| Model | BS | Config | Mean | P50 | P05 | P95 | Speedup | Acc Len |
|---|---|---|---|---|---|---|---|---|
| MiniMax M2.1 (FP8) | 1 | w/o spec | 134.9 | 136.4 | 130.6 | 136.9 | – | – |
| MiniMax M2.1 (FP8) | 1 | w/ spec | 211.8 | 210.6 | 163.1 | 270.3 | 1.57× | 2.62 |
| MiniMax M2.1 (FP8) | 8 | w/o spec | 79.0 | 78.7 | 73.7 | 85.1 | – | – |
| MiniMax M2.1 (FP8) | 8 | w/ spec | 107.1 | 104.5 | 79.9 | 137.1 | 1.36× | 2.62 |
| MiniMax M2.1 (FP8) | 16 | w/o spec | 64.5 | 63.7 | 58.9 | 72.3 | – | – |
| MiniMax M2.1 (FP8) | 16 | w/ spec | 83.1 | 82.9 | 60.9 | 112.0 | 1.29× | 2.62 |
| MiniMax M2.1 (FP8) | 32 | w/o spec | 53.5 | 52.9 | 47.1 | 67.1 | – | – |
| MiniMax M2.1 (FP8) | 32 | w/ spec | 67.1 | 64.7 | 44.0 | 100.5 | 1.25× | 2.62 |
| Qwen3-Coder-Next (FP8) | 1 | w/o spec | 176.4 | 178.0 | 172.3 | 178.4 | – | – |
| Qwen3-Coder-Next (FP8) | 1 | w/ spec | 265.7 | 264.8 | 208.7 | 320.5 | 1.51× | 3.06 |
| Qwen3-Coder-Next (FP8) | 8 | w/o spec | 119.8 | 121.5 | 104.8 | 134.6 | – | – |
| Qwen3-Coder-Next (FP8) | 8 | w/ spec | 146.3 | 143.5 | 109.6 | 189.5 | 1.23× | 3.07 |
| Qwen3-Coder-Next (FP8) | 16 | w/o spec | 99.6 | 102.1 | 74.5 | 119.2 | – | – |
| Qwen3-Coder-Next (FP8) | 16 | w/ spec | 107.6 | 103.7 | 75.7 | 156.6 | 1.09× | 3.06 |

Qwen3-Coder-Next at batch size 32 (Table 5): w/o spec 85.0 mean TPS; lookahead 3, 4, 5 give 78.9, 79.5, 80.3 mean TPS (0.93×, 0.94×, 0.94×).[^wangWhenRLMeets2026] Tables 4 and 5 also report lookahead 3 to 5 at each batch size; for MiniMax M2.1 at batch size 1, lookahead 3 gives 213.0 mean TPS (1.58×, Acc Len 2.42).[^wangWhenRLMeets2026]

## Limitations

- For Qwen3-Coder-Next at batch size 32, verification overhead dominates and speculative decoding is slightly slower than the baseline.[^wangWhenRLMeets2026]
- Throughput gains shrink as batch size increases, because speculative overhead (drafting, verification, synchronization) becomes a larger fraction of the pipeline.[^wangWhenRLMeets2026]
- Online training from scratch initially lowers per-request throughput until the speculator adapts.[^wangWhenRLMeets2026]
- Frequent weight synchronization reduces serving throughput.[^wangWhenRLMeets2026]
- Aurora (Scratch) uses one additional GPU for online speculator tuning, and the inference server carries auxiliary memory overhead for buffered hidden states and logits.[^wangWhenRLMeets2026]
- Traffic is simulated from a fixed prompt corpus, not measured on production traffic.[^wangWhenRLMeets2026]
- Making speculative decoding faster for hybrid models is left to future work.[^wangWhenRLMeets2026]
- The paper has no dedicated limitations section.

Internal inconsistencies in the source text (all from the same version):

- The stream is described as 40k prompts in Section 4.1, while Table 2 totals 44k.[^wangWhenRLMeets2026]
- The Figure 5 caption names "Trained w Async 48" as the Pareto point, while the body text names every 80 requests as the moderately lazy schedule and every 48 requests as the aggressive end of the sweep.[^wangWhenRLMeets2026]
- For Qwen3-Coder-Next at batch size 8, the Figure 10 caption reports 1.21× and the body text and Table 1 report 1.23×.[^wangWhenRLMeets2026]
- For MiniMax M2.1, the abstract reports 1.5× day-0 speedup and Figure 9 reports 1.45× (BS4).[^wangWhenRLMeets2026]
- Table 1 labels MiniMax M2.1 as FP8 and the Table 4 caption labels it BF16.[^wangWhenRLMeets2026]
- Figure captions say acceptance length starts at one; the body text says the untrained speculator starts at zero acceptance length.[^wangWhenRLMeets2026]

## Related

- Proposed system and techniques: [Aurora](../methods/aurora.md), [Discard Sampling](../methods/discard-sampling.md), [Tree Attention](../methods/tree-attention.md)
- Builds on: [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [SGLang](../methods/sglang.md), [Asynchronous RL](../methods/asynchronous-rl.md), [AReaL](../methods/areal.md)
- Compared against conceptually: [Online Speculative Decoding](../methods/online-speculative-decoding.md)
- Datasets: [GSM8K](../datasets/gsm8k.md), [Spider](../datasets/spider.md), [CodeSearchNet](../datasets/codesearchnet.md), [Finance-Alpaca](../datasets/finance-alpaca.md), [chatbot_instruction_prompts](../datasets/chatbot-instruction-prompts.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md), [SGLang](zhengSGLangEfficientExecution2024.md)

## Open questions and results

- [Applying the speculative drafter papers to a mobile phone NPU](../analyses/speculative-drafter-papers-on-mobile-npu.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)

[^wangWhenRLMeets2026]: Wang et al. 2026
