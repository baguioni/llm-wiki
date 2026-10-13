---
type: Method
title: Reflexion
description: Verbal reinforcement framework in which an LLM agent writes self-reflections on task feedback and keeps them in an episodic memory that conditions its next trial, with no weight updates.
tags: [llm-agents, self-reflection, verbal-reinforcement-learning, agent-memory, code-generation]
sources:
  - id: shinnReflexionLanguageAgents2023
    resource: zotero://select/items/@shinnReflexionLanguageAgents2023
    title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
  - id: wangVOYAGEROpenEndedEmbodied
    resource: zotero://select/items/@wangVOYAGEROpenEndedEmbodied
    title: "VOYAGER: An Open-Ended Embodied Agent with Large Language Models"
  - id: rasmussenZepTemporalKnowledge2025
    resource: zotero://select/items/@rasmussenZepTemporalKnowledge2025
    title: "Zep: A Temporal Knowledge Graph Architecture for Agent Memory"
---

# Reflexion

## Overview

Reflexion reinforces a language agent through linguistic feedback instead of weight updates. It converts binary or scalar feedback from the environment into verbal feedback, a textual summary, which is added as context for the agent in the next episode.[^shinnReflexionLanguageAgents2023] The paper describes this self-reflective feedback as a "semantic" gradient signal that gives the agent a concrete direction to improve.[^shinnReflexionLanguageAgents2023] It is introduced in [Shinn et al. 2023](../papers/shinnReflexionLanguageAgents2023.md).

## How it works

| Component | Role |
|---|---|
| Actor $M_a$ | An LLM prompted to generate text and actions conditioned on state observations. Variants explored: [Chain of Thought](chain-of-thought.md) and [ReAct](react.md). A memory component *mem* gives it additional context. |
| Evaluator $M_e$ | Takes a generated trajectory and computes a reward score. Variants: exact match grading for reasoning tasks, pre-defined heuristic functions for decision-making tasks, and a different instantiation of an LLM for decision-making and programming tasks. |
| Self-Reflection $M_{sr}$ | An LLM that, given a sparse reward signal (such as binary success/fail), the current trajectory, and *mem*, generates specific verbal feedback that is stored in *mem*. |
| Memory | The trajectory history is the short-term memory. Outputs of the Self-Reflection model are the long-term memory. The Actor conditions on both. |

All rows: [^shinnReflexionLanguageAgents2023]

The loop:

1. In the first trial the Actor produces a trajectory $\tau_0$, the Evaluator produces a score $r_0$, and the Self-Reflection model turns $\{\tau_0, r_0\}$ into a summary $sr_0$ that is stored in *mem*.[^shinnReflexionLanguageAgents2023]
2. After each trial $t$, $sr_t$ is appended to *mem*. The three models run in a loop until the Evaluator deems $\tau_t$ correct.[^shinnReflexionLanguageAgents2023]
3. *mem* is bounded by a maximum number of stored experiences $\Omega$, usually set to 1-3, to stay within the LLM context limit.[^shinnReflexionLanguageAgents2023]

## Variants

Task-specific instantiations in the original paper:

- **Decision-making ([ALFWorld](../datasets/alfworld.md)).** ReAct is the action generator, with GPT-3 and two domain-specific few-shot trajectories. Self-evaluation is either natural language classification with an LLM or a hand-written heuristic: the agent self-reflects if it executes the same action and receives the same response for more than 3 cycles, or if the number of actions in the current environment exceeds 30. Memory is truncated to the last 3 self-reflections.[^shinnReflexionLanguageAgents2023]
- **Reasoning ([HotpotQA](../datasets/hotpotqa.md)).** Reflexion + CoT is run as $Q\rightarrow A$ and as $Q, C_{gt}\rightarrow A$ with ground truth context $C_{gt}$. Reflexion + ReAct retrieves context through a Wikipedia API. CoT uses 6-shot prompting, ReAct 2-shot, and self-reflection 2-shot. Exact match grading gives a binary success signal between trials. Memory size is 3 experiences.[^shinnReflexionLanguageAgents2023]
- **Programming.** The agent writes its own unit tests with Chain-of-Thought prompting, keeps those for which a valid abstract syntax tree can be built, and samples at most 6 into a test suite. Because the tests are self-generated, the implementation is eligible for pass@1 reporting. The memory limit is 1 experience.[^shinnReflexionLanguageAgents2023]

Other uses of the idea:

- Zep applies "a reflection technique inspired by reflexion" after its initial entity extraction, to minimize hallucinations and enhance extraction coverage.[^rasmussenZepTemporalKnowledge2025]

## Papers using it

### Shinn et al. 2023 (the original paper)

The paper summarizes its gains over strong baselines as an absolute 22% on AlfWorld in 12 iterative learning steps, 20% on HotPotQA, and as much as 11% on HumanEval.[^shinnReflexionLanguageAgents2023]

**AlfWorld.** ReAct + Reflexion completes 130 out of 134 tasks with the simple heuristic and keeps solving additional tasks over 12 consecutive trials. With ReAct only, the performance increase halts between trials 6 and 7, and the agent converges at a hallucination rate of 22%.[^shinnReflexionLanguageAgents2023]

**HotpotQA, 100 questions (Table 5 of the paper).**

| Model | Baseline accuracy | Reflexion accuracy |
|---|---|---|
| CoT (GT) + text-davinci-003 | 0.60 | 0.77 |
| CoT (GT) + gpt-3.5-turbo | 0.57 | 0.71 |
| CoT (GT) + gpt-4 | 0.68 | 0.80 |
| ReAct + text-davinci-003 | 0.30 | 0.55 |
| ReAct + gpt-3.5-turbo | 0.26 | 0.38 |
| ReAct + gpt-4 | 0.39 | 0.51 |

All rows: [^shinnReflexionLanguageAgents2023]

In an ablation with CoT (GT) as the baseline, self-reflection gives an 8% absolute boost over the episodic memory learning advantage, where episodic memory means including the most recent trajectory.[^shinnReflexionLanguageAgents2023]

**Programming, pass@1 (Table 1 of the paper).** The base strategy is a single code generation sample. PY is Python, RS is Rust.[^shinnReflexionLanguageAgents2023]

| Benchmark + Language | Prev SOTA Pass@1 | SOTA Pass@1 | Reflexion Pass@1 |
|---|---|---|---|
| [HumanEval](../datasets/humaneval.md) (PY) | 65.8 (CodeT + GPT-3.5) | 80.1 (GPT-4) | 91.0 |
| HumanEval (RS) | – | 60.0 (GPT-4) | 68.0 |
| [MBPP](../datasets/mbpp.md) (PY) | 67.7 (CodeT + Codex) | 80.1 (GPT-4) | 77.1 |
| MBPP (RS) | – | 70.9 (GPT-4) | 75.4 |
| Leetcode Hard (PY) | – | 7.5 (GPT-4) | 15.0 |

All rows: [^shinnReflexionLanguageAgents2023]

- Reflexion sets a new state of the art on all of these benchmarks for Python and Rust except MBPP Python.[^shinnReflexionLanguageAgents2023]
- The paper explains the MBPP Python result by false positives from the self-generated tests: the false positive test execution rate is 16.3% for MBPP Python and 1.4% for HumanEval Python.[^shinnReflexionLanguageAgents2023]
- That passage gives the baseline pass@1 accuracy of HumanEval Python as 82%, while Table 1 gives 80.1 and Table 2 gives 0.80 for the same GPT-4 baseline. Both values are in the same paper.[^shinnReflexionLanguageAgents2023]

**Ablation on HumanEval Rust, 50 hardest problems, GPT-4 (Table 3 of the paper).**

| Approach | Test Generation | Self-reflection | Pass@1 (Acc) |
|---|---|---|---|
| Base model | False | False | 0.60 |
| Test generation omission | False | True | 0.52 |
| Self-reflection omission | True | False | 0.60 |
| Reflexion | True | True | 0.68 |

All rows: [^shinnReflexionLanguageAgents2023]

**Weaker model.** With starchat-beta on HumanEval Python, pass@1 averaged over 8 trials is 0.26 for the baseline and 0.26 for Reflexion.[^shinnReflexionLanguageAgents2023]

### Voyager (as a baseline)

[Voyager](../papers/wangVOYAGEROpenEndedEmbodied.md) re-interprets Reflexion to be executable in MineDojo. It describes Reflexion as built on top of ReAct with self-reflection, and provides it with environment feedback, the agent states, execution errors, and Voyager's self-verification module. Reflexion runs one round of code generation from scratch followed by three rounds of code refinement, repeated until the maximum prompting iteration.[^wangVOYAGEROpenEndedEmbodied]

| Evaluation | Reflexion | Voyager |
|---|---|---|
| Tech tree: wooden / stone / iron / diamond tool (prompting iterations, successful trials out of 3, limit 160) | N/A (0/3) for all four | 6 ± 2 (3/3) / 11 ± 2 (3/3) / 21 ± 7 (3/3) / 102 (1/3) |
| Unseen tasks: diamond pickaxe / golden sword / lava bucket / compass (limit 50) | N/A (0/3) for all four | 19 ± 3 (3/3) / 18 ± 7 (3/3) / 21 ± 5 (3/3) / 18 ± 2 (3/3) |

All rows: [^wangVOYAGEROpenEndedEmbodied]

The paper states that ReAct and Reflexion struggle to make significant progress because the open-ended exploration goal is abstract and hard to execute without an appropriate curriculum.[^wangVOYAGEROpenEndedEmbodied]

### Zep

[Zep](../papers/rasmussenZepTemporalKnowledge2025.md) uses a reflection step inspired by Reflexion inside its entity extraction (see Variants). The paper reports no separate measurement of that step.[^rasmussenZepTemporalKnowledge2025]

## Strengths & Limitations

Strengths stated by the original paper:

- It is lightweight and does not require fine-tuning the LLM.[^shinnReflexionLanguageAgents2023]
- It allows more nuanced feedback, such as targeted changes in actions, than scalar or vector rewards.[^shinnReflexionLanguageAgents2023]
- It gives a more explicit and interpretable form of episodic memory, and more explicit hints for actions in future episodes.[^shinnReflexionLanguageAgents2023]

Limitations:

- It relies on the LLM's self-evaluation capabilities (or heuristics) and has no formal guarantee of success.[^shinnReflexionLanguageAgents2023]
- It does policy optimization in natural language and may still succumb to non-optimal local minima.[^shinnReflexionLanguageAgents2023]
- Long-term memory is a sliding window with a maximum capacity.[^shinnReflexionLanguageAgents2023]
- For code generation it is bound by the agent's ability to write diverse, comprehensive tests. A flaky test suite produces false positives, as on MBPP Python.[^shinnReflexionLanguageAgents2023]
- It did not help a weaker model (starchat-beta). The paper concludes that the ability to specify self-corrections is an emergent quality of stronger, larger models.[^shinnReflexionLanguageAgents2023]
- On [WebShop](../benchmarks/webshop.md), a two-shot ReAct + Reflexion agent in 100 environments showed no signs of improvement and the runs were terminated after four trials. The paper concludes that Reflexion is unable to solve tasks that require a significant amount of diversity and exploration.[^shinnReflexionLanguageAgents2023]
- In Voyager's open-ended Minecraft setting it unlocks no tech tree level and solves no unseen task.[^wangVOYAGEROpenEndedEmbodied]

## Related

- Methods: [ReAct](react.md), [Chain-of-thought](chain-of-thought.md)
- Benchmarks: [WebShop](../benchmarks/webshop.md)
- Datasets: [ALFWorld](../datasets/alfworld.md), [HotpotQA](../datasets/hotpotqa.md), [HumanEval](../datasets/humaneval.md), [MBPP](../datasets/mbpp.md)
- Papers: [Reflexion](../papers/shinnReflexionLanguageAgents2023.md), [Voyager](../papers/wangVOYAGEROpenEndedEmbodied.md), [Zep](../papers/rasmussenZepTemporalKnowledge2025.md)

[^shinnReflexionLanguageAgents2023]: Shinn et al. 2023
[^wangVOYAGEROpenEndedEmbodied]: Wang et al. n.d.
[^rasmussenZepTemporalKnowledge2025]: Rasmussen et al. 2025
