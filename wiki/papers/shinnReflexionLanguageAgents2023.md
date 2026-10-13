---
type: Paper
title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
description: Framework that reinforces LLM agents without weight updates by having them write verbal self-reflections on task feedback and keep them in an episodic memory buffer for later trials.
tags: [llm-agents, self-reflection, verbal-reinforcement-learning, agent-memory, code-generation, ai899]
collections: [ai899]
authors: [Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao]
year: 2023
doi: 10.48550/arXiv.2303.11366
arxiv: "2303.11366"
arxiv_version: 2303.11366v4
code: https://github.com/noahshinn024/reflexion
sources:
  - id: shinnReflexionLanguageAgents2023
    resource: zotero://select/items/@shinnReflexionLanguageAgents2023
    title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
---

# Reflexion: Language Agents with Verbal Reinforcement Learning

Text source: arXiv HTML, version `2303.11366v4`.

## Summary

Traditional reinforcement learning needs extensive training samples and expensive model fine-tuning, so LLM agents have mostly been taught through in-context examples.[^shinnReflexionLanguageAgents2023] Reflexion reinforces a language agent through linguistic feedback instead of weight updates: the agent verbally reflects on a task feedback signal and stores the reflective text in an episodic memory buffer, which is added as context in the next trial.[^shinnReflexionLanguageAgents2023] The paper describes this self-reflective feedback as a "semantic" gradient signal that gives the agent a concrete direction to improve.[^shinnReflexionLanguageAgents2023]

Reflexion is evaluated on sequential decision-making ([ALFWorld](../datasets/alfworld.md)), reasoning ([HotpotQA](../datasets/hotpotqa.md)), and programming ([HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), LeetcodeHardGym).[^shinnReflexionLanguageAgents2023] The paper reports improvements over strong baselines of an absolute 22% on AlfWorld in 12 iterative learning steps, 20% on HotPotQA, and as much as 11% on HumanEval, and a 91% pass@1 accuracy on HumanEval against 80% for GPT-4.[^shinnReflexionLanguageAgents2023]

## Contributions

- Reflexion, a paradigm for "verbal" reinforcement that parameterizes a policy as an agent's memory encoding paired with a choice of LLM parameters.[^shinnReflexionLanguageAgents2023]
- An empirical study of self-reflection in LLMs showing that it is useful for learning complex tasks over a handful of trials.[^shinnReflexionLanguageAgents2023]
- [LeetcodeHardGym](../benchmarks/leetcode-hard-gym.md), a code-generation RL gym environment of 40 hard-level Leetcode questions in 19 programming languages.[^shinnReflexionLanguageAgents2023]
- Improvements over strong baselines across several tasks, and state-of-the-art results on various code generation benchmarks.[^shinnReflexionLanguageAgents2023]

## Method

### Three models and a memory

| Component | Role |
|---|---|
| Actor $M_a$ | An LLM prompted to generate text and actions conditioned on state observations. Actor variants explored: [Chain of Thought](../methods/chain-of-thought.md) and [ReAct](../methods/react.md). A memory component *mem* gives the Actor additional context. |
| Evaluator $M_e$ | Takes a generated trajectory and computes a reward score. Variants: exact match (EM) grading for reasoning tasks, pre-defined heuristic functions for decision-making tasks, and a different instantiation of an LLM as Evaluator for decision-making and programming tasks. |
| Self-Reflection $M_{sr}$ | An LLM that, given a sparse reward signal (such as binary success/fail), the current trajectory, and the persistent memory *mem*, generates specific verbal feedback that is stored in *mem*. |
| Memory | The trajectory history is the short-term memory. Outputs of the Self-Reflection model are the long-term memory. The Actor conditions on both at inference time. |

All rows: [^shinnReflexionLanguageAgents2023]

### The Reflexion loop (Algorithm 1)

1. The policy is $\pi_\theta(a_i|s_i)$ with $\theta=\{M_a, mem\}$.[^shinnReflexionLanguageAgents2023]
2. In the first trial the Actor produces trajectory $\tau_0$, the Evaluator produces a scalar score $r_0$, and the Self-Reflection model turns $\{\tau_0, r_0\}$ into a verbal summary $sr_0$ that is stored in *mem*.[^shinnReflexionLanguageAgents2023]
3. In each later trial $t$ the Actor generates $\tau_t$, the Evaluator scores it, and $sr_t$ is appended to *mem*. The loop runs until the Evaluator deems $\tau_t$ correct (Algorithm 1 also bounds it by a maximum number of trials).[^shinnReflexionLanguageAgents2023]
4. *mem* is bounded by a maximum number of stored experiences $\Omega$, usually set to 1-3, to stay within the LLM context limit.[^shinnReflexionLanguageAgents2023]

### Task-specific instantiations

- **Decision-making (AlfWorld).** ReAct is the action generator, with GPT-3 as the LLM and two domain-specific few-shot trajectories. Two self-evaluation techniques are used: natural language classification with an LLM, and a hand-written heuristic. The heuristic triggers self-reflection if the agent executes the same action and receives the same response for more than 3 cycles, or if the number of actions in the current environment exceeds 30. Memory is truncated to the last 3 self-reflections.[^shinnReflexionLanguageAgents2023]
- **Reasoning (HotPotQA).** Reflexion + CoT is tested as $Q\rightarrow A$ and as $Q, C_{gt}\rightarrow A$, where $C_{gt}$ is the ground truth context. Reflexion + ReAct retrieves context through a Wikipedia API. CoT uses 6-shot prompting, ReAct 2-shot, and self-reflection 2-shot. Exact match grading from the environment gives a binary success signal between trials. Memory size is 3 experiences.[^shinnReflexionLanguageAgents2023]
- **Programming.** The agent writes its own unit tests with Chain-of-Thought prompting, keeps the tests for which a valid abstract syntax tree (AST) can be built, and samples $n$ of them into a test suite, with $n$ at most 6. Because the tests are self-generated, the implementation is eligible for pass@1 reporting. The memory limit is 1 experience.[^shinnReflexionLanguageAgents2023]

## Experiments & Results

### Sequential decision-making: AlfWorld

- 134 AlfWorld environments across six different tasks.[^shinnReflexionLanguageAgents2023]
- ReAct + Reflexion completes 130 out of 134 tasks using the simple heuristic to detect hallucinations and inefficient planning, and keeps solving additional tasks over 12 consecutive trials.[^shinnReflexionLanguageAgents2023]
- In the ReAct-only approach the performance increase halts between trials 6 and 7, and the agent converges at a hallucination rate of 22% with no signs of long-term recovery.[^shinnReflexionLanguageAgents2023]
- A common failure in baseline trajectories is the agent believing it possesses an item that it does not have. Reflexion eliminates almost all of these cases.[^shinnReflexionLanguageAgents2023]
- The per-trial success curves are given only in Figure 3 and are not reproduced here.

### Reasoning: HotPotQA (100 questions)

Table 5 of the paper, labelled "Pass@1 accuracy on 100 HotPotQA using various models":[^shinnReflexionLanguageAgents2023]

| Model | Baseline accuracy | Reflexion accuracy |
|---|---|---|
| CoT (GT) + text-davinci-003 | 0.60 | 0.77 |
| CoT (GT) + gpt-3.5-turbo | 0.57 | 0.71 |
| CoT (GT) + gpt-4 | 0.68 | 0.80 |
| ReAct + text-davinci-003 | 0.30 | 0.55 |
| ReAct + gpt-3.5-turbo | 0.26 | 0.38 |
| ReAct + gpt-4 | 0.39 | 0.51 |

- ReAct-only, CoT-only, and CoT (GT)-only fail to probabilistically improve on any task: no task failed in the first trial was solved in later trials at a temperature of 0.7.[^shinnReflexionLanguageAgents2023]
- In Reflexion runs the agent retries a failed task until it produces 3 consecutive failed attempts on it.[^shinnReflexionLanguageAgents2023]
- The CoT (GT) agent cannot infer the correct answer for 39% of the questions, and Reflexion improves its accuracy by 14%.[^shinnReflexionLanguageAgents2023]
- Ablation with CoT (GT) as the baseline: adding episodic memory (EPM) means including the most recent trajectory. Self-reflection gives an 8% absolute boost over the episodic memory learning advantage.[^shinnReflexionLanguageAgents2023]

### Programming: pass@1 (Table 1)

The base strategy is a single code generation sample. PY is Python, RS is Rust.[^shinnReflexionLanguageAgents2023]

| Benchmark + Language | Prev SOTA Pass@1 | SOTA Pass@1 | Reflexion Pass@1 |
|---|---|---|---|
| HumanEval (PY) | 65.8 ([CodeT](../methods/codet.md) + GPT-3.5) | 80.1 (GPT-4) | 91.0 |
| HumanEval (RS) | – | 60.0 (GPT-4) | 68.0 |
| MBPP (PY) | 67.7 (CodeT + Codex) | 80.1 (GPT-4) | 77.1 |
| MBPP (RS) | – | 70.9 (GPT-4) | 75.4 |
| Leetcode Hard (PY) | – | 7.5 (GPT-4) | 15.0 |

- Rust versions are produced with MultiPL-E. HumanEval (RS) is the hardest 50 problems from HumanEval Python translated to Rust.[^shinnReflexionLanguageAgents2023]
- LeetcodeHardGym contains 40 Leetcode hard-rated questions released after October 8, 2022, which the paper gives as the pre-training cutoff date of GPT-4.[^shinnReflexionLanguageAgents2023]
- Reflexion sets a new state of the art on all benchmarks for Python and Rust except MBPP Python.[^shinnReflexionLanguageAgents2023]

### Test generation quality (Table 2)

TP: unit tests pass, solution pass. FN: unit tests fail, solution pass. FP: unit tests pass, solution fail. TN: unit tests fail, solution fail.[^shinnReflexionLanguageAgents2023]

| Benchmark + Language | Base | Reflexion | TP | FN | FP | TN |
|---|---|---|---|---|---|---|
| HumanEval (PY) | 0.80 | 0.91 | 0.99 | 0.40 | 0.01 | 0.60 |
| MBPP (PY) | 0.80 | 0.77 | 0.84 | 0.59 | 0.16 | 0.41 |
| HumanEval (RS) | 0.60 | 0.68 | 0.87 | 0.37 | 0.13 | 0.63 |
| MBPP (RS) | 0.71 | 0.75 | 0.84 | 0.51 | 0.16 | 0.49 |

- The paper explains the MBPP Python result by false positives: the false positive test execution rate is 16.3% for MBPP Python and 1.4% for HumanEval Python.[^shinnReflexionLanguageAgents2023]
- The same passage gives the baseline pass@1 accuracies of HumanEval and MBPP Python as 82% and 80%, while Tables 1 and 2 give 80.1 and 0.80 for HumanEval Python.[^shinnReflexionLanguageAgents2023]
- False negatives are preferred over false positives, because the agent may identify the incorrect test through self-reflection and keep the original code, whereas a false positive makes the agent report an invalid submission prematurely.[^shinnReflexionLanguageAgents2023]

### Ablation on HumanEval Rust, 50 hardest problems, GPT-4 base model (Table 3)

| Approach | Test Generation | Self-reflection | Pass@1 (Acc) |
|---|---|---|---|
| Base model | False | False | 0.60 |
| Test generation omission | False | True | 0.52 |
| Self-reflection omission | True | False | 0.60 |
| Reflexion | True | True | 0.68 |

All rows: [^shinnReflexionLanguageAgents2023]

Without unit tests the agent cannot determine whether the current implementation is correct, so it cannot return early and makes harmful edits. Without self-reflection the tests and compiler catch syntax and logic errors, but the implementation fixes do not reflect them.[^shinnReflexionLanguageAgents2023]

### Weaker model (Table 4)

Pass@1 on HumanEval Python with starchat-beta, average over 8 trials: Baseline 0.26 (std 0.00481), Reflexion 0.26 (std 0.00305). The paper concludes that the ability to specify self-corrections is an emergent quality of stronger, larger models.[^shinnReflexionLanguageAgents2023]

## Limitations

- Reflexion does policy optimization in natural language and may still succumb to non-optimal local minima.[^shinnReflexionLanguageAgents2023]
- Long-term memory is a sliding window with maximum capacity. The authors suggest vector embedding databases or SQL databases as future extensions.[^shinnReflexionLanguageAgents2023]
- It relies on the LLM's self-evaluation capabilities (or heuristics) and has no formal guarantee of success.[^shinnReflexionLanguageAgents2023]
- For code generation, test-driven development cannot specify accurate input-output mappings for non-deterministic generator functions, impure functions that interact with APIs, functions whose output varies with hardware, or functions with parallel or concurrent behavior.[^shinnReflexionLanguageAgents2023]
- [WebShop](../benchmarks/webshop.md): a two-shot ReAct + Reflexion agent was tested in 100 environments and the runs were terminated after only four trials because the agent showed no signs of improvement and did not generate helpful self-reflections. The paper concludes that Reflexion is unable to solve tasks that require a significant amount of diversity and exploration.[^shinnReflexionLanguageAgents2023]
- The authors advise isolated execution environments, because generated code is not validated before execution.[^shinnReflexionLanguageAgents2023]

## Related

- Methods: [Reflexion](../methods/reflexion.md), [ReAct](../methods/react.md), [Chain of Thought](../methods/chain-of-thought.md), [Self-Refine](../methods/self-refine.md), [CodeT](../methods/codet.md)
- Benchmarks: [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md), [LeetcodeHardGym](../benchmarks/leetcode-hard-gym.md), [WebShop](../benchmarks/webshop.md)
- Datasets and environments: [HotpotQA](../datasets/hotpotqa.md), [ALFWorld](../datasets/alfworld.md)

[^shinnReflexionLanguageAgents2023]: Shinn et al. 2023
