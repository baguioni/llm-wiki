---
type: Paper
title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
description: Procedurally curated gym of more than 8.1K executable SWE tasks built from commits (SweGen), plus a hybrid execution-based and execution-free verifier that reaches 51% on SWE-Bench Verified with a 32B open-weight model.
tags: [swe-agents, synthetic-data, training-environments, test-time-scaling, verifiers, supervised-fine-tuning, ai899]
collections: [ai899]
authors: [Naman Jain, Jaskirat Singh, Manish Shetty, Liang Zheng, Koushik Sen, Ion Stoica]
year: 2025
doi: 10.48550/arXiv.2504.07164
arxiv: "2504.07164"
arxiv_version: 2504.07164v1
project_page: https://r2e-gym.github.io
sources:
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
---

# R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents

Text source: arXiv HTML, version `2504.07164v1`.

## Summary

The paper targets two obstacles to improving open-weight models on real-world software engineering (SWE) tasks, that is, solving GitHub issues: scalable curation of execution environments for training, and optimal scaling of test-time compute.[^jainR2EGymProceduralEnvironments2025] It introduces R2E-Gym, a procedurally curated gym of more than 8.1K tasks with executable environments, unit tests, and natural-language task descriptions.[^jainR2EGymProceduralEnvironments2025]

R2E-Gym is built with SweGen, a synthetic data recipe that derives environments directly from commits by test generation and back-translation, so it does not depend on human-written issues or unit tests.[^jainR2EGymProceduralEnvironments2025] A Qwen-2.5-Coder 32B model fine-tuned on trajectories from these environments reaches a Pass@1 of 34.4% on SWE-Bench Verified.[^jainR2EGymProceduralEnvironments2025] For test-time scaling, the paper analyzes execution-based and execution-free verifiers, finds that each saturates around 42-43%, and combines them into a hybrid verifier that reaches 51% on SWE-Bench Verified (Best@26).[^jainR2EGymProceduralEnvironments2025] The authors describe this as a new state of the art for open-weight SWE agents and as competitive with proprietary systems such as o1 or sonnet with tools.[^jainR2EGymProceduralEnvironments2025]

The project page is https://r2e-gym.github.io.[^jainR2EGymProceduralEnvironments2025]

## Contributions

- R2E-Gym, described as the largest procedurally curated environment for training real-world SWE agents, which increases the number of executable environments by over 3 times.[^jainR2EGymProceduralEnvironments2025]
- An analysis showing that execution-based and execution-free axes for scaling test-time compute have complementary strengths and weaknesses.[^jainR2EGymProceduralEnvironments2025]
- A hybrid scaling approach that uses the strengths of both verifier types.[^jainR2EGymProceduralEnvironments2025]
- An open-weights 32B model that achieves 51% on SWE-Bench Verified.[^jainR2EGymProceduralEnvironments2025]

## Method

### SweGen: environments from commits

- **Repository and commit curation.** Python repositories with many commits are found with SEART GitHub search. Commits are filtered with rule-based and LLM-based heuristics, and build scripts are collected by semi-manually searching across dependency pins.[^jainR2EGymProceduralEnvironments2025]
- **Commit filter thresholds.** Maximum of 5 non-test files modified; maximum of 100 edited lines across non-test files; maximum patch length of 2000 characters; no more than 1 deleted entity, maximum of 3 added entities, and maximum of 3 edited entities in non-test files; no more than 10 statement-level changes. An LLM-as-judge filter is applied in addition.[^jainR2EGymProceduralEnvironments2025]
- **Installation.** A Docker-based approach with search-based dependency resolution: extract dependency information, generate multiple candidate dependency configurations, and test each until a working environment is found. The authors call this process semi-manual and challenging to scale.[^jainR2EGymProceduralEnvironments2025]
- **Test validation and generation.** Existing tests in a commit are used to identify Fail→Pass (F2P) tests, which fail on the original buggy commit and pass on the fixed commit. Commits without tests get automatically generated F2P tests, using an Agentless-like reproduction test generation approach that takes the ground-truth patch as context.[^jainR2EGymProceduralEnvironments2025]
- **Back-translation of problem statements.** An LLM writes the issue from the commit message, the code patch, and test execution results. The F2P tests are part of the prompt, because naive back-translation of code changes yields generic problem statements.[^jainR2EGymProceduralEnvironments2025]
- **Patch minimization.** Code changes are removed iteratively while checking that the tests still pass, to find the minimal set of changes that fixes the bug.[^jainR2EGymProceduralEnvironments2025]

### Agent and SFT training

- **Scaffold.** A minimal scaffold on top of [OpenHands](../methods/openhands.md) in the [ReAct](../methods/react.md) format with no specialized workflow. It has four tools: `file_editor`, `search_tool`, `execute_bash`, and `submit`. The agent has no internet or browser access.[^jainR2EGymProceduralEnvironments2025]
- **Trajectory collection.** Sonnet-3.5-v2 runs the scaffold on R2E-Gym-Subset and only successful trajectories are kept (rejection sampling with the environments' unit tests). This gives 3321 trajectories from 2048 unique task environments. Limits per trajectory: a maximum of $N=40$ steps, 32K max tokens, a 10-min overall timeout, and 90 seconds per action. Collection temperature is 0.2.[^jainR2EGymProceduralEnvironments2025]
- **Training.** Full supervised fine-tuning on agent thoughts and actions with LLaMA-Factory, using Qwen-2.5-Coder 7B, 14B, and 32B as base models: 2 epochs, batch size 8, learning rate $1e^{-5}$, warmup ratio 0.1, and a maximum context length of 20K.[^jainR2EGymProceduralEnvironments2025]

### Verifiers

Given a task description, $K$ agent trajectories, and $K$ candidate patches, a verifier assigns scores that rank the patches.[^jainR2EGymProceduralEnvironments2025]

- **Execution-based (EB) verifier.** A trained testing agent (Qwen-Coder-32B base) writes a test script with $M=10$ diverse tests, and a regression-test filter removes patches that break existing functionality. The score is $s^{EB}_{k}=\mathrm{TestScore}_{k}$ if the patch has the maximum regression test score $RS_k$ among the $K$ patches and 0 otherwise, where $\mathrm{TestScore}_{k}=\sum_{i}\mathrm{Pass}(\mathcal{P}_{k},Test_{i})$ (Eq. 1). Unlike zero-shot test generation in [Agentless](../methods/agentless.md), the testing agent interacts with the environment.[^jainR2EGymProceduralEnvironments2025]
- **Testing-agent training.** SFT on 2203 test-generation trajectories from sonnet (positive and negative, with minimal rejection sampling): 2 epochs, batch size 8, learning rate $1e-5$, maximum context length 20K.[^jainR2EGymProceduralEnvironments2025]
- **Execution-free (EF) verifier.** A Qwen2.5-Coder-14B model fine-tuned to predict YES or NO for a trajectory given the task description, the trajectory, and the output patch. The score is $s^{EF}=\mathrm{P}(\texttt{YES})/(\mathrm{P}(\texttt{YES})+\mathrm{P}(\texttt{NO}))$. Training data is 5700 trajectories with equal numbers of positive and negative samples, including on-policy trajectories from the trained 32B model. Training uses LoRA with rank 64, 2 epochs, batch size 8, learning rate $1e-5$, and a maximum context length of 32K.[^jainR2EGymProceduralEnvironments2025]
- **Hybrid verifier.** $s_{k}^{H}=\mathrm{Top}_{n}(s_{k}^{EF})+s_{k}^{EB}$ (Eq. 2), where $\mathrm{Top}_{n}(s_{k}^{EF})$ equals $s_{k}^{EF}$ if it is among the top $n$ scores and $-\infty$ otherwise. The EB score gives execution feedback, the continuous EF score breaks ties, and $\mathrm{Top}_{n}$ restricts the choice to the top EF-ranked patches. Regression filtering is done after the top-n filtering.[^jainR2EGymProceduralEnvironments2025]

## Experiments & Results

### Setup

- Benchmarks: [SWE-Bench Verified](../benchmarks/swe-bench-verified.md) and [SWE-Bench Lite](../benchmarks/swe-bench-lite.md).[^jainR2EGymProceduralEnvironments2025]
- Training data: R2E-Gym-Subset, which removes repositories that overlap with the SWE-Bench test set, is used across all experiments unless specified otherwise.[^jainR2EGymProceduralEnvironments2025]
- Verifier evaluation: Best@K is the percentage of problems where the verifier selects a correct patch out of $K$ trajectories. The pool is 1 trajectory at temperature $T=0$ and 25 trajectories at temperatures $T=0.8$ and $T=0.9$ from the R2E-Gym-32B model, with Pass@26 = 64.4%. 7 tests are sampled from the testing agent at $T=0.8$.[^jainR2EGymProceduralEnvironments2025]

### Dataset statistics (Table 1)

| Dataset (split) | Repo? | Executable? | # Instances |
|---|---|---|---|
| APPS | ✗ | ✓ | 10,000 |
| R2E | ✓ | ✓ | 246 |
| SWE-Bench (train) | ✓ | ✗ | 19,008 |
| [SWE-Gym](../datasets/swe-gym.md) Raw | ✓ | ✗ | 66,894 |
| SWE-Bench (test) | ✓ | ✓ | 2,294 |
| [SWE-Gym](../datasets/swe-gym.md) | ✓ | ✓ | 2,438 |
| R2E-Gym-Subset (Ours) | ✓ | ✓ | 4,578 |
| [R2E-Gym](../datasets/r2e-gym.md) (Ours) | ✓ | ✓ | 8,135 |

All rows: [^jainR2EGymProceduralEnvironments2025]

SweGen collects over 2.5 times more problems than data collection that relies on GitHub issues.[^jainR2EGymProceduralEnvironments2025]

### Resolve rate (%) after SFT, Pass@1 (Table 3)

All models use Qwen-2.5-Coder as the base model. Δ is Ours minus SWE-Gym.[^jainR2EGymProceduralEnvironments2025]

| Model size | Lite: Base-model | Lite: SWE-Gym | Lite: Ours | Lite: Δ | Verified: Base-model | Verified: SWE-Gym | Verified: Ours | Verified: Δ |
|---|---|---|---|---|---|---|---|---|
| 7B | 1.0 (±1.0) | 10.0 (±2.4) | 11.0 (±0.8) | +1.0 | 1.8 (±1.3) | 10.6 (±2.1) | 19.0 (±1.0) | +8.4 |
| 14B | 2.7 (±1.9) | 12.7 (±2.3) | 20.67 (±0.7) | +7.97 | 4.0 (±1.6) | 16.4 (±2.0) | 26.8 (±1.4) | +10.4 |
| 32B | 3.0 (±1.4) | 15.3 (±2.5) | 23.77 (±0.8) | +8.47 | 7.0 (±1.3) | 20.6 (±2.1) | 34.4 (±1.2) | +13.8 |

All rows: [^jainR2EGymProceduralEnvironments2025]

- Trajectory scaling was tested from 100 to 3,200 trajectories on the 14B and 32B models. Performance improves with diminishing returns; the 14B model begins to saturate at approximately 800 samples, while the 32B model still improves.[^jainR2EGymProceduralEnvironments2025]

### Training ablations (Pass@1 %)

| Ablation | Config | Pass@1 (%) |
|---|---|---|
| Adding Thoughts | With | 34.4 |
| Adding Thoughts | Without | 30.4 |
| Real vs. Synthetic (400 trajectories each) | Real | 28.0 |
| Real vs. Synthetic (400 trajectories each) | Synthetic | 27.8 |

All rows: [^jainR2EGymProceduralEnvironments2025]

The running text gives the with-thoughts figure as 34.2%, while the table gives 34.4.[^jainR2EGymProceduralEnvironments2025]

### SWE-Bench Verified comparison (Table 4)

| Method | Model | Type | Verified |
|---|---|---|---|
| *Proprietary models* | | | |
| Agentless-1.5 | GPT-4o | Pipeline | 34.0 |
| Agentless | O1 | Pipeline | 48.0 |
| Claude + Tools | Claude-3.6-Sonnet | Agent | 49.0 |
| Agentless-1.5 | Claude-3.6-Sonnet | Pipeline | 50.8 |
| OpenHands | Claude-3.6-Sonnet | Agent | 53.0 |
| Claude + Tools | Claude-3.7-Sonnet | Agent | 62.3 |
| Claude + Tools (Best@Any) | Claude-3.7-Sonnet | Agent | 70.3 |
| *Open-source models* | | | |
| SWE-SynInfer | Lingma-SWE-GPT-72B | Agent | 30.2 |
| SWE-Fixer | SWE-Fixer-72B | Pipeline | 30.2 |
| SWE-Gym (Best@16 w/ Verifier) | SWE-Gym-32B | Agent | 32.0 |
| [SWE-RL](weiSWERLAdvancingLLM2025.md) (Best@500 w/ Tests) | SWE-RL-70B | Pipeline | 41.0 |
| Agentless | DeepSeek-R1 | Pipeline | 49.2 |
| R2E-Gym (Pass@1) | R2E-Gym-32B | Agent | 34.4 |
| R2E-Gym (Best@16 w/ Hybrid) | R2E-Gym-32B | Agent | 49.4 |
| R2E-Gym (Best@26 w/ Hybrid) | R2E-Gym-32B | Agent | 51.0 |

All rows: [^jainR2EGymProceduralEnvironments2025]

### Verifier analysis

- With more editing-agent rollouts, Best@K plateaus for both verifiers, converging to 43.7% (execution-based) and 42.8% (execution-free). The hybrid verifier adds 7-8% and reaches a Best@26 of 51%.[^jainR2EGymProceduralEnvironments2025]
- Execution-based verifiers have limited distinguishability: for the majority of problems, less than 20% of tests differentiate between top-ranked correct and incorrect patches. Most generated tests either do not reproduce the bug or do not pass the ground-truth patch.[^jainR2EGymProceduralEnvironments2025]
- Toxic tests (tests that pass incorrect patches but fail correct ones) are rare, but reach up to 10% of total tests for a small subset of problems.[^jainR2EGymProceduralEnvironments2025]
- Execution-free verifiers rely on trajectory features such as agent thoughts. An attention analysis shows the verifier attending disproportionately to agent thoughts.[^jainR2EGymProceduralEnvironments2025]

Effect of verifier input on the execution-free verifier (Figure 7a):[^jainR2EGymProceduralEnvironments2025]

| Verifier input | Accuracy (%) | Best@26 (%) |
|---|---|---|
| Final Patch + Traj. | 71.82 | 42.8 |
| Patch Only | 68.01 | 37.6 |
| Traj. - Thoughts | 68.77 | 41.4 |

### Hybrid verifier ablations (SWE-Bench Verified)

| Comparison | Without | With |
|---|---|---|
| Generated reproduction tests added to regression tests | 47.4% | 51.0% |
| Agent-generated tests in place of Agentless tests | 48.8% | 51.0% |
| $\mathrm{Top}_{n}$ filtering | 49.8% | 51.0% |

All rows: [^jainR2EGymProceduralEnvironments2025]

- Regression tests alone improve performance from 42.9% to 47.4%.[^jainR2EGymProceduralEnvironments2025]
- Increasing editing-agent rollouts from 16 to 21 improves Best@K from 47.6% to 48.4%, while sampling 5 more test-agent rollouts gives Best@K 49.3%. Test-agent rollouts are usually considerably cheaper than editing-agent rollouts.[^jainR2EGymProceduralEnvironments2025]
- The fixed in-context example given to the testing agent (from Django) improves test generation for ∼2% of problems.[^jainR2EGymProceduralEnvironments2025]

## Limitations

- Repository installation is semi-manual and challenging to scale; the authors aim to rely more on LLMs in the future.[^jainR2EGymProceduralEnvironments2025]
- Due to computational constraints, training used a maximum context length of 20K.[^jainR2EGymProceduralEnvironments2025]
- With more training trajectories, the rate of improvement diminishes or even plateaus for smaller models.[^jainR2EGymProceduralEnvironments2025]
- All 51% and 49.4% results depend on test-time scaling over multiple rollouts; Pass@1 is 34.4%.[^jainR2EGymProceduralEnvironments2025]
- The source is inconsistent in places: the training subset is 4578 environments in the main text and 4538 (named R2E-Gym-lite) in Appendix B, and the with-thoughts Pass@1 is 34.4 in the table and 34.2% in the text.[^jainR2EGymProceduralEnvironments2025]
- The paper has no dedicated limitations section.

## Related

- Datasets: [R2E-Gym](../datasets/r2e-gym.md), [SWE-Gym](../datasets/swe-gym.md)
- Benchmarks: [SWE-Bench Verified](../benchmarks/swe-bench-verified.md), [SWE-Bench Lite](../benchmarks/swe-bench-lite.md), [SWE-bench](../benchmarks/swe-bench.md)
- Methods proposed: [SweGen](../methods/swegen.md), [Hybrid verifier](../methods/hybrid-verifier.md)
- Methods built on or analyzed: [Execution-based verifier](../methods/execution-based-verifier.md), [Execution-free verifier](../methods/execution-free-verifier.md), [Back-translation](../methods/back-translation.md), [Test-time scaling](../methods/test-time-scaling.md), [ReAct](../methods/react.md)
- Systems compared or built on: [OpenHands](../methods/openhands.md), [Agentless](../methods/agentless.md)
- Papers in this wiki cited by this paper: [SWE-RL](weiSWERLAdvancingLLM2025.md), [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md)

[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
