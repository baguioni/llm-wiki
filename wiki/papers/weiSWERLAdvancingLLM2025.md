---
type: Paper
title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
description: Reinforcement learning on GitHub pull-request data with a patch-similarity reward that trains Llama3-SWE-RL-70B to a 41.0% solve rate on SWE-bench Verified.
tags: [reinforcement-learning, software-engineering-agents, issue-resolution, grpo, rule-based-reward, llm-reasoning, ai899]
collections: [ai899]
authors: [Yuxiang Wei, Olivier Duchenne, Jade Copet, Quentin Carbonneaux, Lingming Zhang, Daniel Fried, Gabriel Synnaeve, Rishabh Singh, Sida I. Wang]
year: 2025
doi: 10.48550/ARXIV.2502.18449
arxiv: "2502.18449"
code: https://github.com/facebookresearch/swe-rl
sources:
  - id: weiSWERLAdvancingLLM2025
    resource: zotero://select/items/@weiSWERLAdvancingLLM2025
    title: "SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution"
---

# SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution

## Summary

SWE-RL is a reinforcement learning (RL) method that improves LLMs on software engineering tasks using software evolution data (the record of code snapshots, code changes, and events such as issues and pull requests) and a lightweight rule-based reward.[^weiSWERLAdvancingLLM2025] The paper describes it as the first approach to scale RL-based LLM reasoning for real-world software engineering.[^weiSWERLAdvancingLLM2025] The policy LLM receives an issue and its code context, reasons, and produces code edits. The reward is the sequence similarity between the predicted patch and the oracle patch merged by the pull request, and the policy is optimized with [GRPO](../methods/grpo.md).[^weiSWERLAdvancingLLM2025]

The resulting model, Llama3-SWE-RL-70B, is trained on top of Llama-3.3-70B-Instruct and solves 41.0% of the issues in [SWE-bench Verified](../benchmarks/swe-bench-verified.md) with the [Agentless Mini](../methods/agentless-mini.md) scaffold.[^weiSWERLAdvancingLLM2025] The authors state that, to their knowledge, this is the best performance reported for medium-sized (<100B) LLMs to date, and comparable to leading proprietary LLMs like GPT-4o.[^weiSWERLAdvancingLLM2025] Although RL is applied only to issue solving, the model also improves on five out-of-domain tasks (function coding, library use, code reasoning, mathematics, and general language understanding), whereas a supervised-finetuning (SFT) baseline degrades on average.[^weiSWERLAdvancingLLM2025]

## Contributions

- SWE-RL, described as the first RL approach specifically designed to enhance LLMs for software engineering tasks using software evolution data (e.g., PRs) and rule-based rewards.[^weiSWERLAdvancingLLM2025]
- Llama3-SWE-RL-70B, trained with SWE-RL on Llama-3.3-70B-Instruct, which achieves 41.0% on SWE-bench Verified.[^weiSWERLAdvancingLLM2025]
- Evidence that applying RL solely to real-world software engineering tasks such as issue solving can enhance an LLM's general reasoning abilities, with improvements on out-of-domain tasks like math, code generation, and general language understanding.[^weiSWERLAdvancingLLM2025]
- Agentless Mini, a pipeline-based scaffold built on [Agentless](../methods/agentless.md) with simplifications that match the RL process and enhancements for scaling.[^weiSWERLAdvancingLLM2025]

## Method

### Raw pull request data curation

| Stage | What it does | Size after the stage |
|---|---|---|
| GitHub events and clones | All GitHub events from Jan 1, 2015 to Aug 31, 2024 are taken from GHArchive. Repositories are retrieved with `git clone`, including commit history. | 4.6M repositories cloned and processed |
| PR data aggregation | Keeps only merged PRs. Gathers conversational events in chronological order, retrieves modified files at the merge base of `base_commit` and `head_commit`, saves intermediate commits and the complete patch, and associates matched issues with the PR. | 24M aggregated PR instances |
| Relevant files prediction | Llama-3.1-70B-Instruct is prompted to list relevant but unmodified files given each PR description and the changed files. Their contents are added to the dataset. | not stated |
| Data filtering | Removes bot-generated PRs (keywords "[bot]", "dependabot", "renovate", "bump", "automerge"), PRs with empty or extremely large changes, and PRs where the CodeLlama hunk-level filters flag all code changes. | around 11M unique PR instances |
| Seed selection | Heuristics: at least one linked issue, the issue describes a bug-fixing request, and the code changes involve programming files. | 273k high-quality PR seeds |

All rows: [^weiSWERLAdvancingLLM2025]

- All repositories used by [SWE-bench](../benchmarks/swe-bench.md) are excluded during data processing to prevent data contamination.[^weiSWERLAdvancingLLM2025]
- Relevant files prediction was added because, with only modified files in the context, the model learned a bias: it generated edits for every code file presented and could not handle noisy files.[^weiSWERLAdvancingLLM2025]
- Each seed item contains the issue description, the code context (files to repair and relevant files not intended for editing), and the oracle patch.[^weiSWERLAdvancingLLM2025]

### Reward

The policy is prompted to write its thinking process inside `<think>` tags and then the solution inside `<solution>` tags, as search/replace edits.[^weiSWERLAdvancingLLM2025] The code changes are converted into a consistent patch format for reward calculation.[^weiSWERLAdvancingLLM2025] For a rollout $o$ the reward is:

$$\mathcal{R}(o) = \begin{cases} -1, & \text{if } o \text{ has wrong format,} \\ \text{compare}(\text{patch}_{\text{pred}}, \text{patch}_{\text{gt}}), & \text{otherwise.} \end{cases}$$

`compare` is Python's `difflib.SequenceMatcher`, which returns a floating point between 0 and 1 indicating the sequence similarity.[^weiSWERLAdvancingLLM2025]

### Policy optimization

The policy is optimized with Group Relative Policy Optimization ([GRPO](../methods/grpo.md)).[^weiSWERLAdvancingLLM2025] For each input prompt $q$ the policy produces $G$ outputs $o_i$. Rewards are $r_i = \mathcal{R}(o_i)$ and advantages are the rewards normalized within each group, $A_i = \frac{r_i - \text{mean}(r_1,\ldots,r_G)}{\text{std}(r_1,\ldots,r_G)}$.[^weiSWERLAdvancingLLM2025] The objective is the clipped policy-ratio term with clipping hyperparameter $\epsilon$, minus $\beta D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}})$, where $\pi_{\text{ref}}$ is the reference policy.[^weiSWERLAdvancingLLM2025] The values of $\epsilon$ and $\beta$ are not stated.

The input prompt provides the complete content of each file, which implicitly forces the model to identify detailed fault locations before generating repair edits.[^weiSWERLAdvancingLLM2025] Generating search/replace edits is the only subtask in the RL training. At inference the model generalizes to other pipeline subtasks such as file-level localization, reproduction test generation, and regression test selection without explicit training on them.[^weiSWERLAdvancingLLM2025]

### Agentless Mini scaffold

- **Localization.** The model predicts relevant file paths from the issue and the repository structure. Unlike Agentless, there are no additional steps to identify related elements and no separate embedding model. Multiple samples are generated and consolidated into unique file sets for repair.[^weiSWERLAdvancingLLM2025]
- **Repair.** The LLM is conditioned on the full content of the files and predicts search/replace edits. Multiple repair samples are generated from different location sets.[^weiSWERLAdvancingLLM2025]
- **Reproduction tests.** The model retrieves a relevant test file to guide test generation, and multiple top test samples are selected by voting. Agentless selects only one majority sample.[^weiSWERLAdvancingLLM2025]
- **Regression tests.** Selected in the same manner as Agentless: all tests passing before any modification are gathered, and an optional inference step filters out passing tests that should fail after the fix.[^weiSWERLAdvancingLLM2025]
- **Reranking.** Patches with the minimum number of regression test failures are kept. Each patch is run against the top-N reproduction tests. Patches $P$ that pass the same set of reproduction tests $T$ form a consensus group scored $|P| \times |T|^2$ (the dual execution agreement objective from CodeT). The best patch is chosen from the highest-scoring group by majority voting.[^weiSWERLAdvancingLLM2025]

### Emergent reasoning

The paper reports "aha moments" in which Llama3-SWE-RL-70B shows emergent reasoning skills such as self-reflection, exploring alternatives, and divide-and-conquer strategies, on both in-domain (issue solving) and out-of-domain tasks (function implementation and mathematics).[^weiSWERLAdvancingLLM2025]

## Experiments & Results

### Setup

- Training: Llama3-SWE-RL-70B is trained on top of Llama-3.3-70B-Instruct for 1,600 steps with a 16k context window. The global batch size is 512, with 16 rollouts sampled from each of 32 problems per batch. One optimization step with Adam is performed per global step.[^weiSWERLAdvancingLLM2025]
- Hardware: 512 NVIDIA H100 GPUs. A training run takes approximately 32 wall-time hours.[^weiSWERLAdvancingLLM2025]
- Evaluation: SWE-bench Verified, 500 human-verified problems. In the main evaluation, 500 patches are generated per problem at temperature 1.0, and the top 30 reproduction tests are used for execution and reranking. Only the highest-ranked patch per issue is submitted, giving a pass@1 score.[^weiSWERLAdvancingLLM2025]
- SFT baseline: Llama3-SWE-SFT-70B is trained on top of Llama-3.3-70B-Instruct on a 16k context window for 2B tokens, on a mixture of synthetic localization and code editing data, Llama 3 coding SFT data, and Llama 3 general SFT data. The synthetic data is generated by Llama-3.3-70B-Instruct with an approach inspired by Magicoder (OSS-Instruct), from the same PR seeds.[^weiSWERLAdvancingLLM2025]

### Main results on SWE-bench Verified (Table 1)

Scores are collected from the SWE-bench Leaderboard or from the corresponding reference.[^weiSWERLAdvancingLLM2025]

| Model | Scaffold | SWE-bench Verified |
|---|---|---|
| *Model closed-source or size ≫ 100B* | | |
| GPT-4o | [SWE-agent](../methods/swe-agent.md) | 23.2 |
| Claude-3.5-Sonnet | SWE-agent | 33.6 |
| GPT-4o | [Agentless](../methods/agentless.md) | 38.8 |
| o1-preview | Agentless | 41.3 |
| DeepSeek-V3 (a) | Agentless | 42.0 |
| Claude-3.5-Sonnet | AutoCodeRover-v2.0 | 46.2 |
| Claude-3.5-Sonnet | Tools | 49.0 |
| DeepSeek-R1 (a) | Agentless | 49.2 |
| Claude-3.5-Sonnet | Agentless | 50.8 |
| Claude-3.5-Sonnet | [OpenHands](../methods/openhands.md) | 53.0 |
| *Model size ≤ 100B* | | |
| SWE-Llama-13B | RAG | 1.2 |
| SWE-Llama-7B | RAG | 1.4 |
| Lingma-SWE-GPT-7B | SWE-SynInfer | 18.2 |
| Lingma-SWE-GPT-72B | SWE-SynInfer | 28.8 |
| SWE-Gym-32B | OpenHands | 32.0 |
| SWE-Fixer-72B | SWE-Fixer | 32.8 |
| Llama3-SWE-SFT-70B | [Agentless Mini](../methods/agentless-mini.md) | 36.2 |
| Llama3-SWE-RL-70B | Agentless Mini | 41.0 |

(a) Open-source Mixture-of-Experts model with 671B total and 37B active parameters.[^weiSWERLAdvancingLLM2025]

All rows: [^weiSWERLAdvancingLLM2025]

- The paper notes that the other open-source baselines it compares (Lingma-SWE-GPT, [SWE-Gym](../datasets/swe-gym.md), SWE-Fixer) include distilled outputs from GPT-4o or Claude-3.5-Sonnet in their training data, are built upon Qwen2.5 models, and use supervised finetuning objectives. Llama3-SWE-RL is trained solely with publicly available data, without any proprietary LLM in the pipeline.[^weiSWERLAdvancingLLM2025]

### Repair-only baseline comparison (Table 2)

Oracle localized files are given in the input context, with no test generation or execution. Decoding is greedy, except for the majority voting row, which uses 20 samples at a temperature of 0.6.[^weiSWERLAdvancingLLM2025]

| Model | Setting | Correct format | Repair performance (oracle) |
|---|---|---|---|
| Llama-3.3-70B-Instruct | Greedy decoding | 12.2% | 5.4 |
| Llama-3.3-70B-Instruct | Majority voting | 44.6% | 16.6 |
| Llama3-SWE-SFT-70B | Greedy decoding | 96.2% | 29.6 |
| Llama3-SWE-RL-70B | Greedy decoding | 95.6% | 34.8 |

All rows: [^weiSWERLAdvancingLLM2025]

### Scaling with more samples (Figure 4)

Pass@1 on SWE-bench Verified. The values come from the data labels in the figure. The text confirms 33.6 at 20 repair samples, 40.0 at 160, 41.0 at 500, and 38.8 to 41.0 for test samples.[^weiSWERLAdvancingLLM2025]

| Number of repair samples (30 test samples fixed) | 20 | 40 | 80 | 160 | 320 | 500 |
|---|---|---|---|---|---|---|
| SWE-bench Verified score | 33.6 | 35.6 | 37.0 | 40.0 | 40.6 | 41.0 |

| Number of reproduction test samples (500 repair samples fixed) | 1 | 5 | 10 | 20 | 30 |
|---|---|---|---|---|---|
| SWE-bench Verified score | 38.8 | 39.8 | 40.6 | 41.0 | 41.0 |

All rows: [^weiSWERLAdvancingLLM2025]

Beyond 160 repair samples the improvement begins to plateau, and there is no difference between 20 and 30 test samples.[^weiSWERLAdvancingLLM2025]

### Out-of-domain generalization (Table 3)

Zero-shot greedy decoding. MMLU is the macro average over category accuracy, and the others are pass@1. MATH (strict) uses the simple-evals "Answer: ..." prompt format. MATH (lenient) also accepts "\boxed...", because only the RL model consistently follows the format requirements.[^weiSWERLAdvancingLLM2025]

| Category | Benchmark | Llama-3.3-70B-Instruct | Llama3-SWE-SFT-70B | Llama3-SWE-RL-70B |
|---|---|---|---|---|
| Function coding | [HumanEval+](../benchmarks/humaneval-plus.md) | 76.2 | 73.2 | 79.9 |
| Library use | [BigCodeBench](../benchmarks/bigcodebench.md)-Hard (I) | 28.4 | 25.7 | 28.4 |
| Library use | BigCodeBench-Hard (C) | 29.1 | 24.3 | 29.1 |
| Code reasoning | [CRUXEval](../benchmarks/cruxeval.md)-I | 60.5 | 68.4 | 71.6 |
| Code reasoning | CRUXEval-O | 61.9 | 75.1 | 75.5 |
| Math | [MATH](../benchmarks/math.md) (strict) | 63.2 | 54.0 | 73.7 |
| Math | MATH (lenient) | 70.9 | 71.7 | 73.7 |
| General | [MMLU](../datasets/mmlu.md) | 86.49 | 85.26 | 86.82 |

All rows: [^weiSWERLAdvancingLLM2025]

- Statistical significance: the paper states that small absolute gains (1-2 percentage points) on HumanEval or CRUXEval are, by themselves, unlikely to be statistically significant. Using Eval Arena, it reports that improvements of > 0.8 percentage points on MMLU, 3 points on CRUXEval, and > 3 points on the full MATH dataset are significant on their own, and that taken together the results achieve significance at the 0.05 level.[^weiSWERLAdvancingLLM2025]

### Reward ablation (Figure 5)

The discrete reward outputs 1 if the predicted and oracle patches exactly match and 0 otherwise, with the same training setup. Repair (oracle) is the repair-only performance with greedy decoding and oracle files in the context. The table values appear only in the figure.[^weiSWERLAdvancingLLM2025]

| Reward type | Correct format | Repair (oracle) |
|---|---|---|
| Discrete | 94.2% | 29.0 |
| Continuous | 95.6% | 34.8 |

All rows: [^weiSWERLAdvancingLLM2025]

Discrete rewards grow slower than continuous rewards during training, and the average discrete reward remains approximately zero at the end of training.[^weiSWERLAdvancingLLM2025]

## Limitations

- The reward compares the sequence similarity between the predicted and oracle patch, not their semantic equivalence. This may prevent the policy from exploring alternative, functionally equivalent solutions.[^weiSWERLAdvancingLLM2025]
- In Agentless Mini, localization is simplified to mapping repository structures to file paths, which lacks comprehensive context.[^weiSWERLAdvancingLLM2025]
- Agentless Mini is pipeline-based and divides all steps into distinct inference stages. This "external structure" prevents the model from learning through interaction feedback and hinders its ability to consider the whole problem holistically.[^weiSWERLAdvancingLLM2025]
- No error bars are reported for the SWE-bench evaluations, because each instance is very expensive to run and SWE-bench submissions are evaluated with a single attempt per example.[^weiSWERLAdvancingLLM2025]
- The training data and training pipeline are not shared at the time of writing, due to privacy and proprietary considerations. The reward implementation and evaluation code are included in the supplemental material.[^weiSWERLAdvancingLLM2025]

## Related

- Methods: [SWE-RL](../methods/swe-rl.md), [GRPO](../methods/grpo.md), [Agentless Mini](../methods/agentless-mini.md), [Agentless](../methods/agentless.md)
- Systems compared: [SWE-agent](../methods/swe-agent.md), [OpenHands](../methods/openhands.md), [SWE-Gym](../datasets/swe-gym.md)
- Benchmarks: [SWE-bench Verified](../benchmarks/swe-bench-verified.md), [SWE-bench](../benchmarks/swe-bench.md), [HumanEval+](../benchmarks/humaneval-plus.md), [BigCodeBench](../benchmarks/bigcodebench.md), [CRUXEval](../benchmarks/cruxeval.md), [MATH](../benchmarks/math.md), [MMLU](../datasets/mmlu.md)
- Papers in this wiki cited by this paper: [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md)

[^weiSWERLAdvancingLLM2025]: Wei et al. 2025
