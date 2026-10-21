---
type: Paper
title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
description: Builds EAGLE-3-style drafters by pruning a pretrained small LM to two layers, pretraining it once on generic web text without any target, then adapting it per target through vocabulary alignment, zero-initialized QKV expansion, and TTT distillation, which raises mean acceptance length over EAGLE-3 by 16.1% to 22.7% on three targets.
tags: [speculative-decoding, draft-model, eagle-3, pretraining, structured-pruning, vocabulary-transfer, knowledge-distillation, training-time-test, domain-generalization, speculative-drafter]
collections: ["speculative drafter"]
authors: [Fengxiang Bie, Yuqing Jian, Yifan Yu, Zhongzhu Zhou, Zelei Shao, Ben Athiwaratkun, Shuaiwen Leon Song, Chenfeng Xu, Xiaoxia Wu, Tianyi Zhang]
doi: 10.48550/arXiv.2609.09338
arxiv: "2609.09338"
arxiv_version: 2609.09338v1
code: https://github.com/LeanModels/Osprey
sources:
  - id: bieOspreyTargetagnosticPretraining2026
    resource: zotero://select/items/@bieOspreyTargetagnosticPretraining2026
    title: "Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding"
---

# Osprey: Target-Agnostic Pre-Training Makes Stronger Drafters in Speculative Decoding

Text source: arXiv HTML, version `2609.09338v1`. The extracted text marks the paper as accepted at EMNLP 2026.[^bieOspreyTargetagnosticPretraining2026]

## Summary

Drafters for [speculative decoding](../methods/speculative-decoding.md) are usually trained on a narrow distribution for a single target, and their acceptance rate drops when the workload shifts. The paper gives an example: an [EAGLE-3](../methods/eagle-3.md) drafter for Qwen3-8B trained on math reaches an average acceptance length of 5.06 on math data and only 1.86 on code data.[^bieOspreyTargetagnosticPretraining2026] The authors argue that pretraining, the usual remedy for poor generalization, is hard to apply to drafters because existing recipes are target-specific: the drafter consumes the target's hidden states and is distilled on the target's logits, so any pretraining would have to be repeated for each target.[^bieOspreyTargetagnosticPretraining2026]

[Osprey](../methods/osprey.md) instead builds the drafter body from an off-the-shelf pretrained small language model. A four-stage pipeline splits into a target-agnostic phase done once (prune the small LM to a shallow backbone, then continue next-token pretraining on generic web text) and a per-target phase (align the vocabulary, expand the QKV projections with zero-initialized columns to take target hidden states, then distill from the target with EAGLE-3's [training-time test](../methods/training-time-test.md)).[^bieOspreyTargetagnosticPretraining2026] The verification procedure is unchanged.[^bieOspreyTargetagnosticPretraining2026]

One pretrained backbone, Qwen3-4B pruned to two layers, is adapted to Qwen3-8B, Llama-3.3-70B-Instruct, and the 229B MoE MiniMax-M2.5. Mean acceptance length over EAGLE-3 rises by $16.1\%$, $21.2\%$, and $22.7\%$ respectively, and tokens per second rises by $17.9\%$ (Llama-3.3-70B-Instruct) and $17.5\%$ (MiniMax-M2.5). The largest gains are on out-of-domain and multilingual data.[^bieOspreyTargetagnosticPretraining2026]

## Contributions

- A target-agnostic pretraining recipe for speculative drafters that separates general language modeling from target conditioning and yields one reusable drafter backbone.[^bieOspreyTargetagnosticPretraining2026]
- A conversion step (vocabulary alignment and zero-initialized QKV expansion) that lets the pretrained backbone ingest target hidden states and emit target-vocabulary tokens while it computes exactly its pretrained function at initialization.[^bieOspreyTargetagnosticPretraining2026]
- Results against EAGLE-3 on three targets from different model families (8B dense, 70B dense, 229B MoE), including a $5\times 5$ cross-domain study on Qwen3-8B and multilingual evaluation on MiniMax-M2.5.[^bieOspreyTargetagnosticPretraining2026]
- The authors state that the contribution is not a new distillation objective but a reusable initialization and adaptation pathway.[^bieOspreyTargetagnosticPretraining2026]

## Method

Notation: $p_{\theta}$ is the frozen target and $q_{\phi}$ the drafter. Given a prefix $x_{\leq t}$, the drafter proposes $K$ draft tokens, which the target verifies in one forward pass with the standard acceptance rule. The source model that initializes $q_{\phi}$ may come from a different model family and use a different tokenizer from $p_{\theta}$.[^bieOspreyTargetagnosticPretraining2026]

### Stage 1: Pruning (target-agnostic)

- From a source LM with $L$ transformer blocks, keep only the first $N$ blocks, the input embeddings, the final normalization layer, and the LM head. $N$ is kept small ($N\in\{1,2,3,4\}$) because the drafter runs autoregressively and its latency directly affects speedup.[^bieOspreyTargetagnosticPretraining2026]
- Two pruned drafts are built: Qwen3-4B with $N{=}2$ of $36$ blocks ($\approx$591M parameters), and facebook/layerskip-llama3.2-1B with $N{=}4$ of $16$ blocks ($\approx$506M parameters).[^bieOspreyTargetagnosticPretraining2026]
- Early-exit-trained models such as LayerSkip give a stronger initialization because their auxiliary early-exit objectives train intermediate layers to predict the next token. At step 0 the four-layer pruned LayerSkip model has an initial training loss of $\sim$4.5 nats against $\sim$13.5 nats for a standard Llama-3.2-1B truncation.[^bieOspreyTargetagnosticPretraining2026]

### Stage 2: Pretraining (target-agnostic)

- The pruned backbone continues pretraining with standard next-token prediction on the FineWeb sample-100BT corpus, tokenized with the draft's own tokenizer. The result is called the *shallow NTP backbone*.[^bieOspreyTargetagnosticPretraining2026]
- The authors deliberately train past the compute-optimal token count for a model of this size, since the goal is a broadly trained backbone rather than cheap pretraining.[^bieOspreyTargetagnosticPretraining2026]
- No target-model forward passes are needed. Per-token FLOPs are $\approx 6N_{q_{\phi}}$, against $\approx 2(N_{p_{\theta}}+N_{q_{\phi}})$ for distillation from a target.[^bieOspreyTargetagnosticPretraining2026]
- Configuration (Appendix C): 4 nodes $\times$ 8 H100 GPUs (32 GPUs), PyTorch FSDP, bfloat16, FlashAttention-2. AdamW with $(\beta_{1},\beta_{2},\epsilon)=(0.9,\,0.95,\,10^{-8})$, weight decay $0.1$, gradient clipping $1.0$, cosine schedule with $1\%$ linear warmup and peak learning rate $1{\times}10^{-4}$. Sequence length $4096$, micro-batch $4$, gradient accumulation $16$, so $\approx 8.39$M tokens per optimizer step.[^bieOspreyTargetagnosticPretraining2026]

### Stage 3: Drafter conversion (per target)

- **Multi-layer target hidden states.** Following EAGLE-3, hidden states from a low, a middle, and a high target layer are concatenated and projected into the drafter's hidden space: $\mathbf{c}_{t}=W_{c}\left[\mathbf{h}_{t}^{(\ell_{\mathrm{low}})};\mathbf{h}_{t}^{(\ell_{\mathrm{mid}})};\mathbf{h}_{t}^{(\ell_{\mathrm{high}})}\right]$ (Eq. 1). $W_{c}$ is newly initialized, and $\mathbf{c}_{t}$ is fed to every attention layer of the drafter.[^bieOspreyTargetagnosticPretraining2026]
- **Zero-initialized attention expansion.** When a drafting step begins, the target has not yet computed hidden states for the current token $x_{t}$, so the latest available representation is $\mathbf{c}_{t-1}$. It is concatenated with the token-side representation $\mathbf{z}_{t}$, and each pretrained QKV projection is expanded with zero columns: $\widetilde{W}_{\mathrm{qkv}}=[0\;\;W_{\mathrm{qkv}}]$ (Eq. 2). At initialization $\widetilde{W}_{\mathrm{qkv}}[\mathbf{c}_{t-1};\mathbf{z}_{t}]=W_{\mathrm{qkv}}\mathbf{z}_{t}$ (Eq. 3), so the target features do not affect queries, keys, or values and the attention layers keep their pretrained behavior. The new columns and all other weights are then trained.[^bieOspreyTargetagnosticPretraining2026]
- MLP blocks, normalization layers, and other pretrained components transfer without architectural changes.[^bieOspreyTargetagnosticPretraining2026]
- **Vocabulary alignment.** The input embedding and LM head are resized to $\lvert\mathcal{V}_{T}\rvert$ and initialized from the drafter's own pretrained weights, not from the target. A target token that exists in the source vocabulary copies its pretrained row. Any other target token is converted to text, tokenized with the source tokenizer into $(s_{1},\ldots,s_{m_{v}})$, and initialized as the mean of those rows: $\widetilde{W}[v]=\frac{1}{m_{v}}\sum_{i=1}^{m_{v}}W_{S}[s_{i}]$ (Eq. 4). The same rule is used for the embedding and the LM head.[^bieOspreyTargetagnosticPretraining2026] The authors place this average-of-subtokens initialization in the line of FVT, and say it needs no auxiliary corpus.[^bieOspreyTargetagnosticPretraining2026]

### Stage 4: Target adaptation (per target)

- All drafter parameters, pretrained and new, are trained by distilling the frozen target with EAGLE-3's Training-Time Test framework.[^bieOspreyTargetagnosticPretraining2026]
- For each sample the target produces logits (distillation targets) and hidden states (drafter inputs). The drafter is unrolled for $K_{\mathrm{train}}$ steps. At position $t$ it receives the teacher-forced token $x_{t}$ and $\mathbf{c}_{t-1}$, and its own hidden state becomes part of its autoregressive context at the next step.[^bieOspreyTargetagnosticPretraining2026]
- Loss: $\mathcal{L}_{\mathrm{adapt}}=\sum_{k=0}^{K_{\mathrm{train}}-1}\lambda^{k}\operatorname{CE}\left(p_{\theta}^{(k)},q_{\phi}^{(k)}\right)$ with $\lambda=0.8$ (Eq. 5), which weights earlier drafting steps more.[^bieOspreyTargetagnosticPretraining2026]
- The implementation is built in [SpecForge](liSpecForgeFlexibleEfficient2026.md) on top of [SGLang](../methods/sglang.md), with online target hidden-state generation, FSDP draft training, and optional tensor parallelism for the target.[^bieOspreyTargetagnosticPretraining2026]

### Drafter sizes on Qwen3-8B (Table 11)

Body parameters only (transformer layers plus the 3-layer hidden combiner $f_{c}$), excluding the input embedding and LM head.[^bieOspreyTargetagnosticPretraining2026]

| Draft | $L$ | $d_{\text{h}}$ | Body |
|---|---|---|---|
| EAGLE-3 1L | 1 | 4096 | 269 M |
| EAGLE-3 2L | 2 | 4096 | 487 M |
| Osprey | 2 | 2560 | 265 M |
| LayerSkip | 4 | 2048 | 294 M |

All rows: [^bieOspreyTargetagnosticPretraining2026]

The Osprey drafter keeps the hidden size of its Qwen3-4B source (2560), while the EAGLE-3 drafters for the same target use 4096.[^bieOspreyTargetagnosticPretraining2026]

## Experiments & Results

### Setup

- **Backbone.** All Osprey drafters start from the same shallow NTP backbone, Qwen3-4B pruned to two layers and pretrained on FineWeb-100BT for $55$k steps (approximately $462$B tokens), sequence length $4096$, peak learning rate $10^{-4}$.[^bieOspreyTargetagnosticPretraining2026]
- **Baseline.** [EAGLE-3](../methods/eagle-3.md).[^bieOspreyTargetagnosticPretraining2026]
- **Qwen3-8B.** Five adaptation runs per method, one per domain (chat, code, commonsense, finance, math), each on approximately $65$k prompts from the Online SD multi-domain dataset with responses generated by Qwen3-8B. Each drafter is evaluated on $512$ held-out prompts from each of the five domains, a $5\times 5$ in-domain (ID) and out-of-domain (OOD) grid. Osprey and a one-layer EAGLE-3 baseline are adapted for $97.5$k steps (three epochs) with TTT length $5$, sequence length $4096$, and learning rate $10^{-4}$.[^bieOspreyTargetagnosticPretraining2026]
- **Llama-3.3-70B-Instruct.** Osprey and a reproduced EAGLE-3 trained from scratch use the same target-regenerated [Open-PerfectBlend](../datasets/perfectblend.md) data and $37.5$k adaptation steps each. The official EAGLE-3 checkpoint (yuhuili/EAGLE3-LLaMA3.3-Instruct-70B) is also evaluated.[^bieOspreyTargetagnosticPretraining2026]
- **MiniMax-M2.5.** Osprey is adapted for $35$k steps on $70$k coding prompts with responses generated by the target, and compared with the public one-layer EAGLE-3 checkpoint (thoughtworks/MiniMax-M2.5-Eagle3). Evaluation benchmarks: [MATH-500](../datasets/math-500.md), [HumanEval](../datasets/humaneval.md), [LiveCodeBench](../datasets/livecodebench.md), [MT-Bench](../datasets/mt-bench.md), Commonsense-Eval, [MGSM](../datasets/mgsm.md), and [Global-MMLU](../datasets/global-mmlu.md).[^bieOspreyTargetagnosticPretraining2026]
- **Serving.** All drafters run in [SGLang](../methods/sglang.md) with batch=1, steps=5, topk=1, draft_tokens=6, and max_tokens=4096. Unspecified settings in the serving-sensitivity table use temperature 0. MiniMax-M2.5 is served in FP8 with tensor- and expert-parallel degree 4.[^bieOspreyTargetagnosticPretraining2026]
- **Hardware.** Qwen3-8B: adaptation on 2 H100 80 GB GPUs, evaluation on a single H100 80 GB (tp=1). MiniMax-M2.5: adaptation and evaluation on 4 B200 GPUs.[^bieOspreyTargetagnosticPretraining2026] The paper does not state the hardware for Llama-3.3-70B-Instruct.
- **Metrics.** Mean accepted length (AL), defined as the average number of draft tokens accepted per verification step, and end-to-end decoding throughput in tokens per second (TPS). For Qwen3-8B, also mean ID AL, mean OOD AL, and the OOD-to-ID ratio.[^bieOspreyTargetagnosticPretraining2026]

### Cross-domain evaluation on Qwen3-8B (Figure 2, Table 12)

| Metric | EAGLE-3 (1 layer, scratch) | Osprey | Gain |
|---|---|---|---|
| Mean AL over all 25 pairs | $3.176$ | $3.686$ | $16.1\%$ |
| OOD mean AL | $2.977$ | $3.493$ | $17.3\%$ |
| ID mean AL | $3.971$ | $4.465$ | $12.4\%$ |
| OOD-to-ID ratio | $0.750$ | $0.782$ | |

All rows: [^bieOspreyTargetagnosticPretraining2026]

- Osprey has a higher AL for every one of the 25 domain pairs.[^bieOspreyTargetagnosticPretraining2026]
- Math-adapted drafters: in-domain AL $5.25$ (Osprey) against $5.06$ (EAGLE-3), and mean AL over the other four domains $2.90$ against $2.39$.[^bieOspreyTargetagnosticPretraining2026]
- The paper reports Osprey's gains as most significant at further lookahead positions.[^bieOspreyTargetagnosticPretraining2026]

Full AL matrices at learning rate $10^{-4}$ (Table 12; rows are the adaptation domain, the in-domain cell is the diagonal):[^bieOspreyTargetagnosticPretraining2026]

| Draft | Train | Chat | Code | Comm. | Finance | Math | Mean | OOD |
|---|---|---|---|---|---|---|---|---|
| Osprey | chat | **4.335** | 2.867 | 3.867 | 4.124 | 4.057 | 3.850 | 3.729 |
| Osprey | code | 3.844 | **4.145** | 3.538 | 3.855 | 3.854 | 3.847 | 3.773 |
| Osprey | commonsense | 3.793 | 2.246 | **4.259** | 3.477 | 3.228 | 3.401 | 3.186 |
| Osprey | finance | 4.235 | 3.096 | 3.876 | **4.335** | 4.287 | 3.966 | 3.874 |
| Osprey | math | 3.109 | 2.189 | 3.266 | 3.048 | **5.253** | 3.373 | 2.903 |
| EAGLE-3 scratch | chat | **3.755** | 2.407 | 3.245 | 3.558 | 3.581 | 3.309 | 3.198 |
| EAGLE-3 scratch | code | 3.399 | **3.780** | 3.182 | 3.469 | 3.558 | 3.478 | 3.402 |
| EAGLE-3 scratch | commonsense | 3.268 | 1.951 | **3.722** | 2.997 | 2.543 | 2.896 | 2.690 |
| EAGLE-3 scratch | finance | 3.454 | 2.516 | 3.113 | **3.542** | 3.736 | 3.272 | 3.205 |
| EAGLE-3 scratch | math | 2.533 | 1.857 | 2.721 | 2.453 | **5.058** | 2.924 | 2.391 |

All rows: [^bieOspreyTargetagnosticPretraining2026]

### Llama-3.3-70B-Instruct (Table 1)

| Domain / metric | EAGLE-3 reproduced | EAGLE-3 official | Osprey |
|---|---|---|---|
| Chat | 1.95 | 2.03 | **2.33** |
| Code | 2.38 | 2.53 | **3.12** |
| CSense | 2.31 | 2.33 | **2.55** |
| Finance | 2.21 | 2.26 | **2.63** |
| Math | 3.41 | 2.47 | **4.25** |
| Mean AL | 2.45 | 2.33 | **2.97** |
| Throughput (tokens/s) | 155.8 | 150.3 | **183.7** |

All rows: [^bieOspreyTargetagnosticPretraining2026]

Osprey's mean AL and throughput are $21.2\%$ and $17.9\%$ higher than the reproduced EAGLE-3, and $27.5\%$ and $22.2\%$ higher than the official checkpoint.[^bieOspreyTargetagnosticPretraining2026]

### MiniMax-M2.5, 229B MoE in FP8 (Table 2, 64 prompts per benchmark)

| Benchmark | EAGLE-3 AL | EAGLE-3 T/s | Osprey AL | Osprey T/s |
|---|---|---|---|---|
| HumanEval | 2.570 | 184.4 | **3.565** | **243.2** |
| MATH-500 | 2.924 | 206.2 | **3.642** | **250.0** |
| LiveCodeBench | 2.508 | 176.2 | **3.779** | **249.1** |
| MT-Bench | **2.868** | **214.4** | 2.805 | 201.6 |
| Common.-Eval | 2.302 | 154.3 | **2.367** | **154.8** |
| Mean | 2.634 | 187.1 | **3.232** | **219.8** |

All rows: [^bieOspreyTargetagnosticPretraining2026]

- Mean AL is $22.7\%$ higher and throughput $17.5\%$ higher than EAGLE-3. The largest relative AL gains are on LiveCodeBench ($50.7\%$), HumanEval ($38.7\%$), and MATH-500 ($24.6\%$). The two drafters perform similarly on MT-Bench and Commonsense-Eval.[^bieOspreyTargetagnosticPretraining2026]
- The Osprey drafter for this target was adapted on code data only.[^bieOspreyTargetagnosticPretraining2026]

### Multilingual, MiniMax-M2.5 (Table 3)

MGSM uses $64$ prompts; each G-MMLU language setting uses $84$.[^bieOspreyTargetagnosticPretraining2026]

| Suite | EAGLE-3 AL | EAGLE-3 T/s | Osprey AL | Osprey T/s |
|---|---|---|---|---|
| MGSM ($11$ langs) | 2.275 | 167.3 | **2.557** | **179.7** |
| G-MMLU ($42$ langs) | 2.633 | 197.5 | **3.259** | **231.0** |
| G-MMLU native | 2.620 | 193.7 | **3.023** | **209.9** |

All rows: [^bieOspreyTargetagnosticPretraining2026]

Osprey's AL is $12.4\%$ higher on MGSM, $23.8\%$ higher on Global-MMLU, and $15.4\%$ higher when the model must answer in the language of the question (G-MMLU native).[^bieOspreyTargetagnosticPretraining2026]

### Ablations on Qwen3-8B

Unless stated otherwise: $97{,}500$ adaptation steps (three epochs), TTT length $5$, sequence length $4096$.[^bieOspreyTargetagnosticPretraining2026]

**Learning-rate robustness (Table 4).** Mean AL at two adaptation learning rates.[^bieOspreyTargetagnosticPretraining2026]

| Draft | Metric | $10^{-5}$ | $10^{-4}$ | $\Delta$ |
|---|---|---|---|---|
| Osprey (warm start) | ID | 4.260 | 4.465 | $+0.21$ |
| Osprey (warm start) | OOD | 3.407 | 3.493 | $+0.09$ |
| Osprey (warm start) | All | 3.578 | 3.686 | $+0.11$ |
| EAGLE-3 (scratch) | ID | 2.869 | 3.971 | $+1.10$ |
| EAGLE-3 (scratch) | OOD | 1.921 | 2.977 | $+1.06$ |
| EAGLE-3 (scratch) | All | 2.110 | 3.176 | $+1.07$ |

All rows: [^bieOspreyTargetagnosticPretraining2026]

The authors read this as the pretrained initialization giving a strong prior that makes Osprey much less sensitive to the learning rate.[^bieOspreyTargetagnosticPretraining2026]

**Effect of Stage 2 pretraining (Table 5).** Same two-layer architecture and adaptation, with and without FineWeb pretraining, over chat, code, finance, and math (16 pairs; commonsense excluded).[^bieOspreyTargetagnosticPretraining2026]

| Metric | Without Stage 2 | With Stage 2 | $\Delta$ |
|---|---|---|---|
| ID mean AL | 4.306 | **4.517** | $+0.211$ |
| OOD mean AL | 3.371 | **3.547** | $+0.176$ |
| Overall AL | 3.605 | **3.790** | $+0.185$ |

All rows: [^bieOspreyTargetagnosticPretraining2026]

The improvement holds for every one of the 16 pairs. The largest per-pair gains are code→code ($+0.341$), math→finance ($+0.311$), and math→chat ($+0.282$).[^bieOspreyTargetagnosticPretraining2026]

**Pretraining budget (Table 7).** The 10k-step and 55k-step checkpoints, adapted identically at learning rate $10^{-5}$: overall AL $3.552$ against $3.578$ ($+0.026$), ID AL $4.230$ against $4.260$, OOD AL $3.382$ against $3.407$, OOD/ID retention $0.799$ against $0.800$.[^bieOspreyTargetagnosticPretraining2026] Pretraining cross-entropy falls from about $19$ to $5$ nats in the first $1$k steps and then to about $3.7$ nats. Held-out perplexity falls from $\sim$520 to a plateau near $37$ after about $10{,}000$ steps.[^bieOspreyTargetagnosticPretraining2026]

**Parameter-matched from-scratch baseline (Table 6).** The main comparison pits a two-layer Osprey drafter against a one-layer EAGLE-3. Adding a two-layer EAGLE-3 trained from scratch separates depth from pretraining. Same adaptation data, optimizer, and learning rate; chat, code, finance, math. Cells are AL/TPS.[^bieOspreyTargetagnosticPretraining2026]

| Metric | EAGLE-3 1-layer | EAGLE-3 2-layer | Osprey 2-layer |
|---|---|---|---|
| ID mean | 4.034/402 | 4.124/373 | **4.517**/**406** |
| OOD mean | 3.043/309 | 3.139/290 | **3.547**/**322** |
| Overall | 3.291/332 | 3.385/311 | **3.790**/**343** |

All rows: [^bieOspreyTargetagnosticPretraining2026]

The second EAGLE-3 layer adds $0.094$ overall AL ($0.096$ OOD) and lowers TPS from 332 to 311. Osprey beats the two-layer EAGLE-3 by $0.405$ overall AL ($0.408$ OOD). The authors conclude that the gain comes mainly from the pretrained language prior rather than the extra capacity.[^bieOspreyTargetagnosticPretraining2026] By the paper's parameter count, the two-layer Osprey body (265 M) is about the size of the one-layer EAGLE-3 (269 M) and smaller than the two-layer EAGLE-3 (487 M).[^bieOspreyTargetagnosticPretraining2026] In two cells (code→math TPS 370 vs 360; math→math TPS 496 vs 463) the one-layer EAGLE-3 has higher throughput than Osprey.[^bieOspreyTargetagnosticPretraining2026]

### Serving-configuration sensitivity on Qwen3-8B (Table 9, one H100)

Each cell is AL / tok/s. Defaults: batch size 1, 5 steps, 6 draft tokens, temperature 0, top-$k$ 1. SGLang couples chain steps and draft tokens at topk=1, so they are swept together.[^bieOspreyTargetagnosticPretraining2026]

| Axis | Setting | EAGLE-3 | Osprey |
|---|---|---|---|
| Batch size | 1 | 2.34 / 217 | 3.29 / 270 |
| Batch size | 4 | 2.36 / 785 | 3.32 / 970 |
| Batch size | 8 | 2.35 / 1454 | 3.34 / 1716 |
| Batch size | 16 | 2.35 / 2534 | 3.28 / 2855 |
| Steps, draft tokens | $(1,2)$ | 1.67 / 182 | 1.79 / 187 |
| Steps, draft tokens | $(3,4)$ | 2.22 / 227 | 2.76 / 262 |
| Steps, draft tokens | $(5,6)$ | 2.34 / 217 | 3.29 / 270 |
| Steps, draft tokens | $(7,8)$ | 2.36 / 202 | 3.61 / 258 |
| Temperature | 0 | 2.34 / 217 | 3.29 / 270 |
| Temperature | 0.7 | 2.29 / 207 | 3.21 / 258 |
| Temperature | 1.0 | 2.17 / 195 | 2.92 / 231 |

All rows: [^bieOspreyTargetagnosticPretraining2026]

- Osprey's throughput gain is 24% at batch size 1 and 13% at batch size 16.[^bieOspreyTargetagnosticPretraining2026]
- Going from 2 to 8 draft tokens widens Osprey's AL gain from 7% to 53%, as EAGLE-3 saturates near 6 tokens.[^bieOspreyTargetagnosticPretraining2026]
- The AL gain is 41% at temperature 0 and 35% at temperature 1.0.[^bieOspreyTargetagnosticPretraining2026]

### Compute cost and break-even (Table 10, Section 4.3.4)

| Stage / target | Hardware | Wall-clock | GPU-hours | Tokens / steps | Target fwd passes |
|---|---|---|---|---|---|
| Stage 2 pretraining (55k) | 32$\times$ H100 | $\approx 95$ h | 3,040 h | 462B tokens | 0 |
| Stage 2 pretraining (10k) | 32$\times$ H100 | $\approx 18$ h | 576 h | 84B tokens | 0 |
| Qwen3-8B adaptation (Osprey) | 2$\times$ H100 | $\approx 24$ h | 48 h | 97.5k steps | 97.5k rollouts |
| Qwen3-8B scratch (EAGLE-3) | 2$\times$ H100 | $\approx 24$ h | 48 h | 97.5k steps | 97.5k rollouts |
| MiniMax-M2.5 adaptation (Osprey) | 4$\times$ B200 | $\approx 36$ h | 144 h | 35k steps | 35k rollouts |
| MiniMax-M2.5 scratch (EAGLE-3) | 4$\times$ B200 | $\approx 36$ h | 144 h | 35k steps | 35k rollouts |

All rows: [^bieOspreyTargetagnosticPretraining2026]

- Per-target distillation costs the same as standard EAGLE-3 training. Stage 2 is an extra upfront cost that does not reduce the per-target budget.[^bieOspreyTargetagnosticPretraining2026]
- Per-domain Qwen3-8B adaptation workload (Table 8): 65k unique prompts with target-regenerated responses, $\approx$0.8B tokens processed, $\approx$195k target forward passes with hidden states and logits computed online.[^bieOspreyTargetagnosticPretraining2026]
- On MiniMax-M2.5, the throughput gain saves approximately $880$ H100 GPU-hours per billion generated tokens. At that rate the $55$k-step pretraining is recovered after approximately $3.5$ billion generated tokens, and the $10$k-step checkpoint after approximately $0.65$ billion. Reusing the backbone across targets lowers the break-even volume per target.[^bieOspreyTargetagnosticPretraining2026]
- The authors argue that scaling from-scratch distillation to hundreds of billions of tokens would cost hundreds of thousands of GPU-hours for a target like MiniMax-M2.5, because each token needs a target forward pass.[^bieOspreyTargetagnosticPretraining2026]

### Warm start under DFlash (Appendix G)

The paper also asks whether a target-agnostic warm start helps a [DFlash](../methods/dflash.md) block-parallel drafter. Since DFlash drafts a block in parallel, the warm-start source must itself be a diffusion LM, so the authors train a compact Introspective Diffusion Language Model ([IDLM](../methods/i-dlm.md)) on a four-layer LayerSkip-Llama backbone with Nemotron-Post-Training-Dataset-v2.[^bieOspreyTargetagnosticPretraining2026]

- Target Qwen3-8B. Six epochs on the 65k single-domain math split, sequence length $4096$, effective batch $32$, peak learning rate $6{\times}10^{-4}$ with cosine decay to $6{\times}10^{-5}$, warmup ratio $0.04$, block size $B{=}16$. Evaluation on the five domains with $512$ prompts per domain in SGLang.[^bieOspreyTargetagnosticPretraining2026]
- Baseline and warm start share architecture, embedding and LM-head initialization (from IDLM, row-mapped to the Qwen3 vocabulary), data, and optimizer. Only the transformer-block body initialization differs.[^bieOspreyTargetagnosticPretraining2026]
- The EAGLE-style DFlash variant keeps the drafter's own projections and adds zero-initialized target-side projections, $Q=W_{Q}h+W_{Q}^{\mathrm{tgt}}c_{t}$ and likewise for $K$ and $V$. The target feature $c_{t}$ is gathered once at the block's verified anchor and broadcast across the block, with no extra target-derived key/value positions. It also uses causal intra-block attention with shift-by-one labels, where original DFlash uses bidirectional block attention and same-position labels.[^bieOspreyTargetagnosticPretraining2026]

| Eval domain | Original DFlash, random body | Original DFlash, IDLM warm start | EAGLE-style DFlash, IDLM warm start |
|---|---|---|---|
| math (ID) | 5.96 | **6.03** | 5.25 |
| chat | 1.50 | 1.53 | **1.88** |
| code | 1.58 | 1.63 | **1.93** |
| common | 1.88 | 1.92 | **2.21** |
| finance | 1.60 | 1.65 | **1.99** |
| OOD avg. | 1.64 | 1.68 | **2.00** |

All rows: [^bieOspreyTargetagnosticPretraining2026]

- Under the original DFlash interface the warm start gains at most $0.07$ accepted tokens in any domain.[^bieOspreyTargetagnosticPretraining2026]
- The authors hypothesize key/value distribution drift: with [KV injection](../methods/kv-injection.md), the pretrained body's attention receives target-derived key/value streams it never saw in pretraining, so less of its pretrained computation stays reusable and the random-body baseline catches up.[^bieOspreyTargetagnosticPretraining2026]
- The EAGLE-style variant raises OOD mean AL to $2.00$, while its in-domain math AL is $5.25$, below both original-interface runs.[^bieOspreyTargetagnosticPretraining2026] The table caption says this column uses an "aligned HF protocol".[^bieOspreyTargetagnosticPretraining2026]

## Limitations

Stated by the authors:

- Three targets under one fixed SGLang configuration; results may differ with other targets, hardware, batch sizes, or workloads.[^bieOspreyTargetagnosticPretraining2026]
- Stage 2 is an upfront compute cost that pays back only under continuous high-volume serving or reuse across targets. In low-traffic or one-off deployments it is not amortized.[^bieOspreyTargetagnosticPretraining2026]
- The cross-domain study covers five domains, and the MiniMax-M2.5 adaptation uses code-only data.[^bieOspreyTargetagnosticPretraining2026]
- Most results come from single runs, not multiple seeds, so small differences should be read with caution.[^bieOspreyTargetagnosticPretraining2026]
- For MiniMax-M2.5 the public EAGLE-3 comparator's training cost is not reported, so the paper makes no cost-parity claim for that comparison.[^bieOspreyTargetagnosticPretraining2026]

Inconsistencies in the source text:

- The pretraining budget is given three ways: five epochs over a 100B-token FineWeb sample, "approximately 500B" tokens (Section 3.2); $55$k steps, approximately $462$B tokens (Section 4 and Table 10); and $60{,}000$ steps, $\approx 503$B tokens (Appendix C). Appendix C gives $80$–$110$ wall-clock hours per pretraining run, and Table 10 gives $\approx 95$ h.[^bieOspreyTargetagnosticPretraining2026]
- Section 3.2 says $N\in\{1,2,3,4\}$, and Appendix A says $N\in\{2,4\}$.[^bieOspreyTargetagnosticPretraining2026]
- Table 8 gives $\approx$195k target forward passes per Qwen3-8B domain, and Table 10 gives 97.5k rollouts.[^bieOspreyTargetagnosticPretraining2026]
- Table 10 lists a 144 GPU-hour "MiniMax-M2.5 Scratch (EAGLE-3)" row, while Appendix D says the public MiniMax-M2.5 comparator's training cost is not reported.[^bieOspreyTargetagnosticPretraining2026]
- The paper calls the drafter "approximately 591M" (Section 3.2) and "approximately 500M" (Section 4.3.4) in total parameters, and reports a 265 M body without embedding and LM head (Table 11).[^bieOspreyTargetagnosticPretraining2026]
- Table 9 (Qwen3-8B, batch 1, AL 2.34 for EAGLE-3 and 3.29 for Osprey) does not say which adaptation domain or evaluation prompts it uses, so it does not line up with the cross-domain means of 3.176 and 3.686.[^bieOspreyTargetagnosticPretraining2026]
- The AL definition (draft tokens accepted per verification step) does not say whether the bonus token is counted.[^bieOspreyTargetagnosticPretraining2026]

## Related

- Methods: [Osprey](../methods/osprey.md), [Speculative decoding](../methods/speculative-decoding.md), [EAGLE-3](../methods/eagle-3.md), [Training-time test](../methods/training-time-test.md), [Knowledge distillation](../methods/knowledge-distillation.md), [Structured pruning](../methods/structured-pruning.md), [DFlash](../methods/dflash.md), [KV injection](../methods/kv-injection.md), [Medusa](../methods/medusa.md), [EAGLE](../methods/eagle.md), [EAGLE-2](../methods/eagle-2.md), [DistillSpec](../methods/distillspec.md), [LayerSkip](../methods/layerskip.md), [I-DLM](../methods/i-dlm.md), [Vocabulary transfer](../methods/vocabulary-transfer.md)
- Systems: [SGLang](../methods/sglang.md), [SpecForge](liSpecForgeFlexibleEfficient2026.md)
- Datasets: [FineWeb](../datasets/fineweb.md), [Open-PerfectBlend](../datasets/perfectblend.md), [MATH-500](../datasets/math-500.md), [HumanEval](../datasets/humaneval.md), [LiveCodeBench](../datasets/livecodebench.md), [MT-Bench](../datasets/mt-bench.md), [MGSM](../datasets/mgsm.md), [Global-MMLU](../datasets/global-mmlu.md), [Nemotron Post-Training Dataset](../datasets/nemotron-post-training.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md), [DFlash](chenDFlashBlockDiffusion2026.md), [SGLang](zhengSGLangEfficientExecution2024.md), [DistillSpec](zhouDistillSpecImprovingSpeculative2024.md), [Sheared LLaMA](xiaShearedLLaMAAccelerating2024.md)

## Open questions and results

- [Does starting a block drafter from the target's own layers cut its training cost?](../questions/target-layer-initialization-for-block-drafters.md): Osprey initializes the drafter body from a pruned small LM of another model rather than the target, and its Appendix G finds only a small warm-start gain under the DFlash KV-injection interface.
- [Can a block drafter be narrower than its target?](../questions/narrow-block-drafter.md): the Osprey drafter for Qwen3-8B runs at hidden size 2560 with its own resized embedding and LM head, against 4096 for EAGLE-3.
- [Why do reported EAGLE-3 numbers differ so much between papers?](../questions/eagle-3-baseline-variance.md): on Llama-3.3-70B-Instruct the official EAGLE-3 checkpoint has a lower mean AL (2.33) than the authors' reproduction (2.45).

[^bieOspreyTargetagnosticPretraining2026]: Bie et al. 2026
