---
type: Method
title: LLM-as-a-Judge
description: Use of an LLM to decide whether an agent trajectory or output is correct, applied in this wiki's papers as a training reward and as an evaluation metric, and contrasted with executable, deterministic verification.
tags: [evaluation, reward-design, agentic-reinforcement-learning, web-agents, verification]
sources:
  - id: karWeblicaScalableReproducible2026
    resource: zotero://select/items/@karWeblicaScalableReproducible2026
    title: "Weblica: Scalable and Reproducible Training Environments for Visual Web Agents"
  - id: wangAgentWorldModel2026
    resource: zotero://select/items/@wangAgentWorldModel2026
    title: "Agent World Model: Infinity Synthetic Environments for Agentic Reinforcement Learning"
  - id: chaeSafeScalableWeb2026
    resource: zotero://select/items/@chaeSafeScalableWeb2026
    title: Safe and Scalable Web Agent Learning via Recreated Websites
---

# LLM-as-a-Judge

## Overview

An LLM-as-a-judge is an LLM that is prompted to decide whether a task was completed, in place of a programmatic check. Weblica uses one because many web navigation tasks are open-ended and cannot be evaluated programmatically or by string matching.[^karWeblicaScalableReproducible2026] The three papers that link this page take different positions on it: Weblica uses an LLM judge alone as the reward, Agent World Model grounds the judge with verification code, and VeriEnv replaces it with executable validators.[^karWeblicaScalableReproducible2026][^wangAgentWorldModel2026][^chaeSafeScalableWeb2026]

## How it works

- **Trajectory judge (Weblica).** GPT-4o receives the task description, the agent's action sequence, and the resulting screenshots, and assesses whether the agent completed the task against task-specific criteria.[^karWeblicaScalableReproducible2026]
- **Code-augmented judge (Agent World Model).** A verification module inspects the database state before and after agent execution and extracts task-relevant signals plus success and failure criteria. The LLM judge combines the agent trajectory with these structured verification signals and returns one of {Completed, Partially Completed, Agent Error, Environment Error}. The judge prompt says the verification results may be empty, erroneous, or inaccurate and should not be fully relied on.[^wangAgentWorldModel2026]
- **Reward mapping (Agent World Model).** The final reward is 1.0 if the task is Completed, 0.1 if Partially Completed, and 0.0 otherwise.[^wangAgentWorldModel2026]

## Variants

| Variant | Inputs to the judge | Paper |
|---|---|---|
| LLM-only | Agent trajectory | Agent World Model (ablation)[^wangAgentWorldModel2026] |
| VLM-based | Trajectory with screenshots and actions | Weblica[^karWeblicaScalableReproducible2026] |
| Code-augmented | Trajectory plus structured state-diff signals from verification code | Agent World Model[^wangAgentWorldModel2026] |
| No LLM (verifiable judge) | Executable predicates over environment state | VeriEnv[^chaeSafeScalableWeb2026] |

## Papers using it

### Weblica

- **Reward.** [Weblica](../papers/karWeblicaScalableReproducible2026.md) trains with Dr. GRPO, a variant of [GRPO](grpo.md), using the LLM-as-Judge reward. The judge is GPT-4o.[^karWeblicaScalableReproducible2026]
- **Validation.** The judge has 88% agreement with human evaluations.[^karWeblicaScalableReproducible2026]
- **Data filtering.** SFT trajectories are filtered with the LLM judge to keep successful completions, giving 51.7K SFT trajectories. During RL, samples the judge labels "website failure" are discarded from the training batch.[^karWeblicaScalableReproducible2026]
- **Evaluation.** The paper uses each benchmark's official judge. It describes [Online-Mind2Web](../benchmarks/online-mind2web.md) as evaluating agents on live websites with an LLM-as-Judge for task success. For WebTailBench it uses the WebVoyager judge.[^karWeblicaScalableReproducible2026]

### Agent World Model

[Agent World Model](../papers/wangAgentWorldModel2026.md) uses GPT-5 as the code-augmented LLM-as-a-Judge for task verification.[^wangAgentWorldModel2026]

Verification strategies compared (Table 9 of the paper). LLM-only decides the reward from the agent trajectory. Code-only inspects database state differences and the final answer.[^wangAgentWorldModel2026]

| Size | Verification | [BFCLv3](../benchmarks/bfcl.md) | $\tau^{2}$ P@1 | $\tau^{2}$ P@4 | MCP |
|---|---|---|---|---|---|
| 4B | LLM | 51.92 | 15.65 | 35.97 | 6.70 |
| 4B | Code | 55.66 | 14.93 | 32.01 | 6.15 |
| 4B | Augmented | 64.50 | 22.57 | 43.89 | 6.70 |
| 8B | LLM | 55.46 | 26.44 | 52.52 | 10.62 |
| 8B | Code | 60.00 | 29.59 | 52.88 | 5.59 |
| 8B | Augmented | 65.94 | 33.45 | 55.40 | 11.17 |
| 14B | LLM | 65.44 | 31.03 | 55.76 | 10.62 |
| 14B | Code | 65.04 | 29.50 | 53.60 | 8.38 |
| 14B | Augmented | 70.18 | 39.03 | 57.19 | 12.29 |

All rows: [^wangAgentWorldModel2026]

- The paper's reading: LLM-only verification is ungrounded in state changes and yields the weakest performance, code-only improves over it but is brittle under environment imperfections, and the code-augmented strategy achieves the best results across all model scales and benchmarks.[^wangAgentWorldModel2026]
- The extra cost of GPT-5 as the judge is about $1.80 per training step (at most 1,024 samples).[^wangAgentWorldModel2026]

Judge reliability on 100 sampled trajectories from the 8B agent, each judged 5 times (Tables 10 and 13 of the paper):[^wangAgentWorldModel2026]

| Setting | Metric | GPT-5.1 | Claude-4.5-Sonnet | Qwen3.5-122B-A10B |
|---|---|---|---|---|
| Binary (Completed vs. others) | Self-Consistency | 90.8% | 82.0% | 76.3% |
| Binary | Pairwise Agreement | 95.5% | 91.8% | 88.1% |
| Binary | Fleiss' κ | 0.891 | 0.826 | 0.728 |
| Binary | Reward Flip Rate | 9.2% | 18.0% | 23.7% |
| 4-class | Self-Consistency | 82.7% | 65.0% | 69.5% |
| 4-class | Pairwise Agreement | 91.2% | 83.5% | 82.7% |
| 4-class | Fleiss' κ | 0.781 | 0.693 | 0.650 |
| 4-class | Reward Flip Rate | 11.2% | 25.0% | 18.6% |

All rows: [^wangAgentWorldModel2026]

The paper also uses LLM judges (GPT-5.1 and Claude 4.5) to score the quality of 100 sampled environments on Task Feasibility, Data Alignment, and Toolset Completeness, on a 1-5 scale.[^wangAgentWorldModel2026]

### VeriEnv (contrasted)

[VeriEnv](../papers/chaeSafeScalableWeb2026.md) is motivated by the claim that prior work often generates underspecified instructions with multiple valid answers and relies on an LLM-as-a-judge to score trajectories, and that such evaluation can be error-prone.[^chaeSafeScalableWeb2026]

- Each task comes with a validation program written against a Python SDK. At the end of an episode it acts as a verifiable judge that evaluates the terminal state deterministically and returns a binary reward.[^chaeSafeScalableWeb2026]
- In the paper's human evaluation, task executability is 90% and judge correctness is 76%. Here "judge" is the generated validation program, not an LLM. The most common errors come from database resets that do not preserve the random seeds used to populate website data.[^chaeSafeScalableWeb2026]
- Compared with PAE, which relies on real websites, non-verifiable tasks, and LLM-based judges, the paper states that VeriEnv yields larger and more stable gains across training phases. The result is given only in a figure.[^chaeSafeScalableWeb2026]
- Failure case named for the judge-based approach: when a task is ambiguous, the policy may fail to reach the intended target page, yet a vision-language judge may still label the outcome as successful because it contains seemingly relevant information, a false positive.[^chaeSafeScalableWeb2026]
- VeriEnv still uses a model-based judge for evaluation on Mind2Web-Online, where trajectories are scored with the WebJudge-7B model.[^chaeSafeScalableWeb2026]

## Strengths & Limitations

- It allows training on open-ended tasks that have no programmatic verification.[^karWeblicaScalableReproducible2026]
- It can use trajectory-level context to correct misjudgments caused by imperfect environment signals, such as incomplete state updates or timeouts.[^wangAgentWorldModel2026]
- A judge that sees only the trajectory is ungrounded in state changes, and was the weakest reward in the Agent World Model ablation on BFCLv3 for the 4B and 8B models.[^wangAgentWorldModel2026]
- It can be error-prone and gives false positives on ambiguous tasks.[^chaeSafeScalableWeb2026]
- It is not perfectly repeatable: the best judge in the Agent World Model study still has a 9.2% reward flip rate in the binary setting.[^wangAgentWorldModel2026]
- It adds cost, about $1.80 per training step with GPT-5 in Agent World Model.[^wangAgentWorldModel2026]

# Contradictions

**Is code-only verification more reliable than an LLM judge?** VeriEnv states that LLM-based evaluation can be error-prone, that verification-based rewards are typically more reliable and robust, and that its rule-based validators give deterministic, auditable pass/fail decisions, unlike model-based evaluators that can introduce additional uncertainty.[^chaeSafeScalableWeb2026] Agent World Model states that relying entirely on code-driven verification is fragile, because it assumes task success is perfectly specifiable and reliably observable from state alone, and reports that code-only verification scores below its code-augmented LLM judge at every model size (for example 55.66 against 64.50 on BFCLv3 at 4B).[^wangAgentWorldModel2026]

The two papers agree that an LLM judge with no grounding is the weaker option. They disagree on whether deterministic code should make the final decision. The settings differ:

- VeriEnv works on cloned websites, its validators are checked by running them through the SDK, and its evidence is a human evaluation (judge correctness 76%) plus a comparison with PAE shown in a figure.[^chaeSafeScalableWeb2026]
- Agent World Model works on synthetic tool-use environments backed by a database, and its evidence is downstream benchmark scores of agents trained with each reward.[^wangAgentWorldModel2026]
- Neither paper evaluates the other's method, and no wiki paper compares the two on the same environments.

## Related

- Methods: [GRPO](grpo.md)
- Benchmarks: [Online-Mind2Web](../benchmarks/online-mind2web.md), [BFCL](../benchmarks/bfcl.md), [WebArena](../benchmarks/webarena.md)
- Papers: [Weblica](../papers/karWeblicaScalableReproducible2026.md), [Agent World Model](../papers/wangAgentWorldModel2026.md), [VeriEnv](../papers/chaeSafeScalableWeb2026.md)

## Open questions and results

- [Should agent training environments verify tasks with code or with an LLM judge?](../questions/code-verification-vs-llm-judge.md)

[^karWeblicaScalableReproducible2026]: Kar et al. 2026
[^wangAgentWorldModel2026]: Wang et al. 2026
[^chaeSafeScalableWeb2026]: Chae et al. 2026
