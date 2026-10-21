---
type: Paper
title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
description: Trains two co-adaptive reinforcement learning policies, one for draft tree depth and one for verification size, with per-cycle throughput as the reward, on top of Eagle3.
tags: [speculative-decoding, reinforcement-learning, adaptive-drafting, draft-tree, llm-inference, speculative-drafter]
collections: [speculative drafter]
authors: [Jiebin Zhang, Zhenghan Yu, Liang Wang, Nan Yang, Eugene J. Yu, Zheng Li, Yifan Song, Dawei Zhu, Xingxing Zhang, Furu Wei, Sujian Li]
arxiv: "2603.01639"
arxiv_version: 2603.01639v1
code: https://github.com/zhzihao/Learning-to-Draft
sources:
  - id: zhangLearningDraftAdaptive2026
    resource: zotero://select/items/@zhangLearningDraftAdaptive2026
    title: "Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning"
---

# Learning To Draft: Adaptive Speculative Decoding with Reinforcement Learning

Text source: arXiv HTML, version `2603.01639v1`.

## Summary

In [speculative decoding](../methods/speculative-decoding.md), a small draft model generates candidate tokens that a larger target model verifies, and efficiency depends on the trade-off between time spent drafting and time spent verifying.[^zhangLearningDraftAdaptive2026] State-of-the-art methods such as [Eagle3](../methods/eagle-3.md) use a static, manually tuned draft tree size, while existing dynamic methods rely on heuristics or optimize acceptance length, which ignores the time cost of drafting and verification and treats the two phases in isolation.[^zhangLearningDraftAdaptive2026]

[Learning to Draft (LTD)](../methods/ltd.md) formulates the interaction between draft and target models as a reinforcement learning environment and trains two co-adaptive policies: a depth policy that decides when to stop expanding the draft tree, and a size policy that selects how many candidate tokens are sent to the target model. Both are rewarded with the throughput of each draft-and-verify cycle.[^zhangLearningDraftAdaptive2026] Across five LLMs and four tasks, the paper reports speedup ratios ranging from 2.24× to 4.32×, outperforming Eagle3 by up to 36.4%.[^zhangLearningDraftAdaptive2026]

## Contributions

- Direct throughput optimization: speculative decoding is formulated as an RL environment with the throughput of each draft-and-verify cycle as the reward, so the method learns the trade-off between acceptance length and time cost.[^zhangLearningDraftAdaptive2026]
- A co-adaptive policy framework in which two jointly trained policies coordinate the drafting and verification phases instead of treating them as independent problems.[^zhangLearningDraftAdaptive2026]
- Gains of up to 36.4% over the Eagle3 baseline in greedy decoding, and retained effectiveness in high-temperature sampling.[^zhangLearningDraftAdaptive2026]

## Method

### Throughput objective

Throughput of a draft-and-verify cycle is $\lambda_{c}=L_{A}/T_{\text{total}}$, where $L_A$ is the number of accepted tokens and $T_{\text{total}}=T_{\text{draft}}+T_{\text{verify}}$.[^zhangLearningDraftAdaptive2026] Draft time is determined mainly by the draft depth $D$ (the number of sequential forward passes of the draft model) and increases linearly with it. Verification time is governed mainly by the verification size $V$ (the number of candidate tokens processed in one forward pass of the target model) and increases step-wise as $V$ grows.[^zhangLearningDraftAdaptive2026]

### Draft-and-verify cycle

The cycle follows Eagle3. The draft tree is built by a beam-search-like expansion with beam width $W$ and draft depth $D$: the top-$W$ candidates form the first level, then for $D-2$ rounds each of the $W$ leaves generates $W$ children and the top-$W$ of the $W^2$ pool by cumulative path probability are kept.[^zhangLearningDraftAdaptive2026] The final tree holds $V_{all}=1+W+(D-2)\cdot W^{2}$ candidate tokens, of which the $V$ with the highest overall probabilities are flattened with a tree attention mask and verified by the target model in a single forward pass.[^zhangLearningDraftAdaptive2026] Eagle3 uses a default draft depth of 8 and a fixed verification size; LTD replaces both with policies.[^zhangLearningDraftAdaptive2026]

### Policies

| | Depth policy $\pi_D$ | Size policy $\pi_V$ |
|---|---|---|
| Decision | After each draft forward pass, continue or stop | Verification size $V$, once per cycle |
| Action space | Binary, $\{0,1\}$ | Discrete, 12 actions mapping linearly to $V$ from 20 to 240 |
| Observation | Log-probabilities of the $W^2$ candidates at the current expansion frontier, plus draft depth $D$ and input length $L$ | Log-probability scores of all candidate tokens in the tree (padded to fixed length), plus $D$ and $L$ |
| Policy network | Single hidden layer of 1024 units | Two hidden layers of 1024 and 256 units, ReLU |
| Discount factor | $\gamma=0.999$ | $\gamma=0.9$ |
| Initial training | 1M steps with a constant verification size of 60 | 100k steps with draft depths sampled from $[1,12]$ |

All rows: [^zhangLearningDraftAdaptive2026]

- The full state is $s_{t}=[D,L,P_{1};\dots;P_{V_{all}}]$.[^zhangLearningDraftAdaptive2026]
- The reward is $R_{t}=L_{A}/(T_{draft}+T_{verify})$. For the depth policy the reward is given only on the STOP action; CONTINUE actions yield zero reward, and the high discount factor counteracts a bias towards premature termination.[^zhangLearningDraftAdaptive2026]
- Both policies are optimized with [PPO](../methods/ppo.md), implemented with Stable-Baselines3: rollout buffer of 2048 steps, minibatch size of 256, 20 epochs per update cycle, entropy coefficient 0.01, learning rate 1e-3 with linear decay after a warm-up over the initial 1% of training steps.[^zhangLearningDraftAdaptive2026]
- PPO is chosen because it integrates into the online speculative decoding process; the authors argue GRPO would require repeated sampling from the same state, which means reconstructing the KV cache or introducing timing mismatches.[^zhangLearningDraftAdaptive2026]

### Two-stage training

1. **Initial policy training** on [HumanEval](../datasets/humaneval.md): each policy is trained independently while the other follows a fixed heuristic. The checkpoint with the highest speedup on the validation set is selected.[^zhangLearningDraftAdaptive2026]
2. **Iterative optimization for co-adaptation**: one policy is frozen while the other is optimized against it, alternating. The paper finds that only two rounds of this process yield a highly synergistic strategy.[^zhangLearningDraftAdaptive2026]

Training cost on a single NVIDIA A100 GPU: the size policy (100k steps) takes 2.0, 2.5, and 3.5 hours for Llama3-8B, Vicuna-13B, and Qwen3-32B; the depth policy (1M steps) takes 5, 5, and 7 hours. With three iterations of training, the total stays below 30 GPU hours.[^zhangLearningDraftAdaptive2026]

## Experiments & Results

### Setup

- Target models: Llama-3.1-8B-Instruct, Vicuna-13B-v1.3, DeepSeek-R1-Distill-LLaMA 8B, Qwen3-14B, Qwen3-32B. Eagle3 draft models for the Qwen3 series come from AngelSlim; the others are the official Eagle3 releases.[^zhangLearningDraftAdaptive2026]
- Tasks: [MT-bench](../datasets/mt-bench.md) (multi-turn conversation), [GSM8K](../datasets/gsm8k.md) (mathematical reasoning), [Alpaca](../datasets/alpaca.md) (instruction following), and [Natural Questions](../datasets/natural-questions.md) (QA), with the same policy weights for all tasks.[^zhangLearningDraftAdaptive2026]
- Metrics: speedup ratio relative to vanilla auto-regressive decoding, and average acceptance length $\tau$ (average number of tokens generated per draft-and-verify cycle).[^zhangLearningDraftAdaptive2026]
- Baselines on top of Eagle3: dynamic depth methods [DDD](../methods/ddd.md), SVIP, Gammatune (GT), Disco, and [SpecDec++](../methods/specdec-plus-plus.md); the dynamic size method [C2T](../methods/c2t.md); and grid search (GS) over draft depths 4 to 12 and verification sizes 40 to 240 on HumanEval.[^zhangLearningDraftAdaptive2026]
- Default Eagle3: verification size 60 and 50 for the 8B and 13B LLMs respectively, draft depth 8, 10 nodes selected during expansion. Dynamic depth methods use verification size 60 and maximum depth 12; dynamic size methods use depth 8.[^zhangLearningDraftAdaptive2026]

### Greedy decoding, Temperature=0 (Table 1)

Each cell is speedup / $\tau$. The Qwen3 Eagle3 models lack default settings, so only grid search is given as their baseline.[^zhangLearningDraftAdaptive2026]

| Model | Method | MT-bench | Gsm8k | Alpaca | Qa | Mean |
|---|---|---|---|---|---|---|
| L31 8B | Eagle3 | 3.70 / 6.39 | 3.58 / 6.44 | 4.26 / 6.93 | 3.17 / 5.35 | 3.68 / 6.28 |
| L31 8B | Eagle3+DDD | 3.67 / 5.41 | 3.55 / 5.48 | 3.97 / 5.58 | 3.07 / 4.21 | 3.57 / 5.17 |
| L31 8B | Eagle3+Svip | 3.65 / 6.21 | 3.47 / 6.21 | 4.04 / 6.73 | 3.12 / 4.78 | 3.57 / 5.98 |
| L31 8B | Eagle3+GT | 3.79 / 5.86 | 3.64 / 5.77 | 4.37 / 6.49 | 3.38 / 4.92 | 3.80 / 5.76 |
| L31 8B | Eagle3+C2T | 3.80 / 6.39 | 3.57 / 6.44 | 4.19 / 6.93 | 3.25 / 5.36 | 3.70 / 6.28 |
| L31 8B | Eagle3+Disco | 3.70 / 6.11 | 3.56 / 6.18 | 4.14 / 6.51 | 3.22 / 5.05 | 3.66 / 5.96 |
| L31 8B | Eagle3+Spec++ | 3.82 / 6.09 | 3.65 / 6.08 | 4.29 / 6.70 | 3.28 / 5.23 | 3.76 / 6.03 |
| L31 8B | Eagle3+GS | 3.83 / 6.75 | 3.78 / 6.91 | 4.38 / 7.42 | 3.33 / 5.67 | 3.83 / 6.69 |
| L31 8B | Eagle3+LTD | 3.96 / 6.74 | 3.79 / 6.73 | 4.53 / 7.31 | 3.41 / 5.44 | 3.92 / 6.56 |
| V 13B | Eagle3 | 4.48 / 7.22 | 4.36 / 6.58 | 4.16 / 6.47 | 3.43 / 5.12 | 4.11 / 6.35 |
| V 13B | Eagle3+DDD | 4.15 / 6.69 | 4.25 / 6.22 | 3.98 / 5.50 | 3.22 / 4.34 | 3.90 / 5.69 |
| V 13B | Eagle3+Svip | 4.02 / 7.74 | 3.86 / 6.79 | 3.77 / 6.53 | 3.02 / 4.96 | 3.67 / 6.51 |
| V 13B | Eagle3+GT | 4.15 / 6.85 | 4.07 / 6.00 | 3.94 / 6.09 | 3.35 / 4.81 | 3.88 / 5.94 |
| V 13B | Eagle3+C2T | 4.33 / 7.22 | 3.97 / 6.58 | 3.93 / 6.47 | 3.23 / 5.12 | 3.87 / 6.35 |
| V 13B | Eagle3+Disco | 4.48 / 7.08 | 4.13 / 6.49 | 4.02 / 6.29 | 3.31 / 5.05 | 3.99 / 6.23 |
| V 13B | Eagle3+Spec++ | 4.25 / 6.78 | 4.09 / 6.16 | 4.00 / 6.27 | 3.21 / 5.03 | 3.89 / 6.06 |
| V 13B | Eagle3+GS | 4.53 / 7.99 | 4.47 / 7.27 | 4.38 / 7.16 | 3.51 / 5.48 | 4.22 / 6.98 |
| V 13B | Eagle3+LTD | 4.64 / 8.24 | 4.59 / 7.38 | 4.40 / 7.01 | 3.66 / 5.37 | 4.32 / 7.00 |
| Dpsk 8B | Eagle3 | 3.67 / 5.82 | 4.73 / 7.39 | 3.65 / 5.63 | 3.14 / 5.02 | 3.80 / 5.53 |
| Dpsk 8B | Eagle3+GS | 3.69 / 6.42 | 4.83 / 8.37 | 3.54 / 6.24 | 3.20 / 5.55 | 3.82 / 6.08 |
| Dpsk 8B | Eagle3+LTD | 4.05 / 6.32 | 4.98 / 8.53 | 3.98 / 6.00 | 3.62 / 5.37 | 4.16 / 6.08 |
| Qwen3 14B | Eagle3+GS | 2.34 / 3.40 | 2.75 / 3.95 | 2.15 / 2.90 | 1.86 / 2.65 | 2.28 / 3.23 |
| Qwen3 14B | Eagle3+LTD | 2.44 / 3.34 | 2.82 / 3.92 | 2.24 / 2.87 | 1.98 / 2.62 | 2.37 / 3.19 |
| Qwen3 32B | Eagle3+GS | 1.76 / 3.30 | 2.26 / 4.10 | 1.75 / 2.96 | 1.45 / 2.67 | 1.81 / 3.26 |
| Qwen3 32B | Eagle3+LTD | 2.42 / 3.17 | 3.02 / 3.90 | 2.38 / 2.85 | 2.06 / 2.60 | 2.47 / 3.13 |

All rows: [^zhangLearningDraftAdaptive2026]

- The introduction states throughput improvements over Eagle3 in greedy decoding of 36.4% on Qwen3-32B, 9.5% on Deepseek-Distilled-Llama-8B, 6.5% on Llama-3-8B, 5% on Vicuna-1.3-13B, and 4% on Qwen3-14B.[^zhangLearningDraftAdaptive2026] Section 5.2 states an average of 6.5% on Llama-3 and 5.1% on Vicuna compared to the default Eagle3 configuration, and 10% on Deepseek-R1-Distll-LLaMA 8B.[^zhangLearningDraftAdaptive2026]
- LTD's $\tau$ is often shorter than that of the grid-search baseline while its speedup is higher; the paper attributes this to forgoing candidate tokens whose time cost is disproportionately high.[^zhangLearningDraftAdaptive2026]
- For the Qwen models LTD has a lower acceptance length than the baseline but significantly reduces verification time, especially for Qwen3-32B.[^zhangLearningDraftAdaptive2026]

### Temperature=1, mean over four tasks (Table 5)

Policies are trained exclusively at greedy decoding. Each cell is mean speedup / mean $\tau$.[^zhangLearningDraftAdaptive2026]

| Method | L31 8B | V 13B | Dpsk 8B | Qwen3 14B | Qwen3 32B |
|---|---|---|---|---|---|
| Eagle3 | 2.98 / 4.47 | 3.44 / 5.33 | 3.07 / 4.66 | | |
| Eagle3+DDD | 3.00 / 3.76 | 3.34 / 4.91 | | | |
| Eagle3+Svip | 2.86 / 4.12 | 3.07 / 5.34 | | | |
| Eagle3+GT | 3.00 / 4.04 | 3.28 / 5.00 | | | |
| Eagle3+C2T | 2.89 / 4.47 | 3.22 / 5.37 | | | |
| Eagle3+Disco | 2.90 / 4.24 | 3.35 / 5.35 | | | |
| Eagle3+Spec++ | 3.01 / 4.43 | 3.40 / 5.29 | | | |
| Eagle3+GS | 2.98 / 4.69 | 3.50 / 5.91 | 3.07 / 5.03 | 2.10 / 3.08 | 1.66 / 3.01 |
| Eagle3+LTD | 3.01 / 4.51 | 3.62 / 5.99 | 3.15 / 5.09 | 2.21 / 3.07 | 2.26 / 2.89 |

All rows: [^zhangLearningDraftAdaptive2026]

Per-task Temperature=1 results are in Table 5 of the paper. On L31 8B, LTD is not the best method on any single task at Temperature=1 (for example Eagle3 has 3.43 on Gsm8k against 3.35 for LTD) and ties Eagle3+Spec++ on the mean at 3.01.[^zhangLearningDraftAdaptive2026]

### Ablations

**Components** (Table 4, Vicuna-13B, mean over four tasks):[^zhangLearningDraftAdaptive2026]

| Variant | Mean speedup | Mean $\tau$ |
|---|---|---|
| Eagle3 | 4.11 | 6.35 |
| -Depth (size policy only) | 4.13 | 6.84 |
| -Size (depth policy only) | 4.29 | 6.57 |
| -Iterative Training | 4.20 | 7.06 |
| LTD | 4.32 | 7.00 |

All rows: [^zhangLearningDraftAdaptive2026]

**Reward signal** (Table 2, size policy alone, Vicuna-13B, mean over four tasks):[^zhangLearningDraftAdaptive2026]

| Reward | Mean speedup | Mean $\tau$ |
|---|---|---|
| Acceptance Length | 3.59 | 6.89 |
| Time Cost | 3.45 | 5.66 |
| Throughput | 4.13 | 6.84 |

All rows: [^zhangLearningDraftAdaptive2026]

**Iterative optimization** (Tables 7 and 8, mean speedup / mean $\tau$). Iter0 is the naive combination of the initial policies; Iter1 optimizes the size policy, Iter2 the depth policy, Iter3 the size policy again.[^zhangLearningDraftAdaptive2026]

| Stage | Llama3.1-8B | Dpsk-8B |
|---|---|---|
| Eagle3 | 3.68 / 6.28 | 3.80 / 5.53 |
| Iter0 | 3.87 / 6.20 | 3.91 / 5.72 |
| Iter1 | 3.90 / 6.26 | 4.05 / 5.78 |
| Iter2 | 3.92 / 6.56 | 4.05 / 5.97 |
| Iter3 | 3.92 / 6.56 | 4.16 / 6.08 |

All rows: [^zhangLearningDraftAdaptive2026]

**Observation space** (Table 6, size policy, Vicuna-13B, mean speedup): P+L 4.05, P+D 4.07, P+D+L (LTD) 4.13, P+D+L+H 4.10, P+D+L+E 4.11, where P is predicted probabilities, D draft depth, L input length, H hidden states, and E entropy.[^zhangLearningDraftAdaptive2026]

**Size policy architecture** (Table 10, Llama-3.1-8B-Instruct, mean speedup): [1024] 3.86, [1024, 256] 3.92, [1024, 512, 256] 3.93.[^zhangLearningDraftAdaptive2026]

### Policy overhead (Table 9)

| Model | Size policy overhead (%) | Depth policy overhead (%) | Total overhead (%) | Total latency per sample (s) |
|---|---|---|---|---|
| Llama-3.1-8B-Instruct | 0.483 | 0.909 | 1.39 | 2.07 |
| Vicuna-13B-v1.3 | 0.414 | 0.810 | 1.22 | 1.81 |

Mean over the four tasks. All rows: [^zhangLearningDraftAdaptive2026]

### Generalization

- **[MMLU](../datasets/mmlu.md)** (Llama-3.1-8B-Instruct, 57 subtasks, 80 sampled examples per subtask): LTD outperforms Eagle3 on 54 out of 57 subtasks, with an average speedup improvement of 5% and over 10% in mathematics and logic-related tasks.[^zhangLearningDraftAdaptive2026]
- **[Griffin](../methods/griffin.md)** (Table 11, Meta-Llama-3-8B-Instruct, greedy decoding, mean speedup / mean $\tau$): Griffin 2.55 / 4.68, Griffin+GS 2.78 / 4.93, Griffin+LTD 2.81 / 4.89.[^zhangLearningDraftAdaptive2026]

## Limitations

- At Temperature=1 on Llama-3.1-8B-Instruct, LTD's mean speedup (3.01) is close to default Eagle3 (2.98) and equal to Eagle3+Spec++ (3.01).[^zhangLearningDraftAdaptive2026]
- For Qwen3-14B and Qwen3-32B the only baseline is grid-searched Eagle3 with third-party (AngelSlim) draft models, because no default Eagle3 settings exist for them; the 36.4% headline gain is measured against that baseline.[^zhangLearningDraftAdaptive2026]
- The comparison with other dynamic methods (DDD, SVIP, Gammatune, C2T, Disco, SpecDec++) covers only Llama-3.1-8B and Vicuna-13B.[^zhangLearningDraftAdaptive2026]
- Policies are trained per target model and need RL training (below 30 GPU hours with three iterations).[^zhangLearningDraftAdaptive2026]
- Validation speedup first improves and then declines during training, so checkpoint selection on a validation set is needed to avoid overfitting to the training set.[^zhangLearningDraftAdaptive2026]
- The benefit of later co-adaptation iterations is model-dependent: Llama3-8B saturates after Iter2 while Dpsk-8B still improves through Iter3.[^zhangLearningDraftAdaptive2026]
- Generation quality is not evaluated, on the grounds that speculative decoding does not change the target model's output distribution.[^zhangLearningDraftAdaptive2026]
- The paper has no dedicated limitations section.

## Related

- Methods: [Speculative decoding](../methods/speculative-decoding.md), [LTD](../methods/ltd.md), [Eagle3](../methods/eagle-3.md), [PPO](../methods/ppo.md), [Griffin](../methods/griffin.md)
- Baselines compared: [DDD](../methods/ddd.md), [SpecDec++](../methods/specdec-plus-plus.md), [C2T](../methods/c2t.md)
- Datasets: [HumanEval](../datasets/humaneval.md), [MT-bench](../datasets/mt-bench.md), [GSM8K](../datasets/gsm8k.md), [Alpaca](../datasets/alpaca.md), [Natural Questions](../datasets/natural-questions.md), [MMLU](../datasets/mmlu.md)
- Papers in this wiki cited by this paper: [EAGLE-3](liEAGLE3ScalingInference2025.md), [DistillSpec](zhouDistillSpecImprovingSpeculative2024.md)

## Open questions and results

- [Choosing what to verify: Learning to Draft vs. DSpark](../analyses/choosing-what-to-verify-ltd-vs-dspark.md)
- [Learned policy or calibrated confidence for choosing the verify set?](../questions/learned-vs-confidence-scheduled-verification.md)
- [Applying the speculative drafter papers to a mobile phone NPU](../analyses/speculative-drafter-papers-on-mobile-npu.md)
- [Does speculative decoding help on a mobile NPU?](../questions/speculative-decoding-on-mobile-npu.md)

[^zhangLearningDraftAdaptive2026]: Zhang et al. 2026
