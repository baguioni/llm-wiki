---
type: Paper
title: "Agent World Model: Infinity Synthetic Environments for Agentic Reinforcement Learning"
description: Open-source pipeline that synthesizes 1,000 code-driven, SQLite-backed, MCP-exposed tool-use environments with verification code, used to train Qwen3 agents with GRPO that generalize to out-of-distribution benchmarks.
tags: [environment-synthesis, agentic-reinforcement-learning, tool-use-agents, synthetic-data, mcp, grpo, llm-as-a-judge, ai899]
collections: [ai899]
authors: [Zhaoyang Wang, Canwen Xu, Boyi Liu, Yite Wang, Siwei Han, Zhewei Yao, Huaxiu Yao, Yuxiong He]
year: 2026
doi: 10.48550/arXiv.2602.10090
arxiv: "2602.10090"
arxiv_version: 2602.10090v3
code: https://github.com/Snowflake-Labs/agent-world-model
sources:
  - id: wangAgentWorldModel2026
    resource: zotero://select/items/@wangAgentWorldModel2026
    title: "Agent World Model: Infinity Synthetic Environments for Agentic Reinforcement Learning"
---

# Agent World Model: Infinity Synthetic Environments for Agentic Reinforcement Learning

Text source: arXiv HTML, version `2602.10090v3`.

## Summary

Training tool-use agents with reinforcement learning needs many diverse, reliable environments, and these are scarce. Real-world environments are expensive and often expose no public API, human-created sets are small ($\tau^{2}$-bench and TheMCPCompany contain three and five environments), and LLM-simulated environments hallucinate state transitions and need an LLM call per step.[^wangAgentWorldModel2026]

[Agent World Model](../methods/agent-world-model.md) (AWM) is an open-source pipeline that synthesizes executable tool-use environments from scratch. Starting from a scenario description, it generates user tasks, a SQLite database schema and sample data, a Python toolset exposed through the [Model Context Protocol](../methods/mcp.md) (MCP), and per-task verification code.[^wangAgentWorldModel2026] The pipeline produced 1,000 environments, 35,062 tools, and 10,000 tasks paired with verification code, which the authors state is, to the best of their knowledge, the largest open-source environment set to date.[^wangAgentWorldModel2026] Qwen3 agents trained on these environments with [GRPO](../methods/grpo.md) improve over the base models on three out-of-distribution benchmarks: [BFCLv3](../benchmarks/bfcl.md), [$\tau^{2}$-bench](../benchmarks/tau2-bench.md), and [MCP-Universe](../benchmarks/mcp-universe.md).[^wangAgentWorldModel2026]

## Contributions

- AWM, an open-source pipeline for automatic generation of executable tool-use environments with database-backed state consistency.[^wangAgentWorldModel2026]
- 1,000 ready-to-use diverse environments suitable for large-scale RL training.[^wangAgentWorldModel2026]
- Empirical results showing that agents trained on AWM generalize to out-of-distribution unseen environments.[^wangAgentWorldModel2026]

## Method

### Environments as POMDPs

Each environment is a partially observable Markov decision process. The database defines the state space, the interface layer defines the action space (tool calls), the observation space (tool responses), and the transition function, and verification provides the task-specific reward functions.[^wangAgentWorldModel2026]

### Synthesis pipeline

| Stage | What is generated | Details |
|---|---|---|
| Scenario | 1,000 unique scenario descriptions | Self-Instruct style expansion from 100 seed popular domain names; an LLM classifier keeps stateful scenarios with CRUD operations; embedding deduplication with cosine similarity threshold 0.85; category caps |
| Task | $k=10$ tasks per scenario, 10,000 in total | Tasks must be API-solvable (no UI-dependent actions) and assume a post-authentication context |
| Database | SQLite schema and sample data | The LLM infers the entities, attributes, and relations needed to make every task feasible, then creates records that satisfy each task's preconditions |
| Interface | Toolset schema, then a Python MCP server | Two stages (schema, then code); generated code has SQLAlchemy ORM models, Pydantic request/response models, and FastAPI endpoint handlers |
| Verification | A Python verification function per task | Compares database state before and after agent execution and returns changed records, expected outcomes, and diagnostic signals, plus natural-language success and failure criteria |

All rows: [^wangAgentWorldModel2026]

- **Execution-based self-correction.** Each generated component is run in an isolated environment. On an error, the error message and code are fed back to the LLM for regeneration, for up to five iterations. Up to 10% errors are allowed in each stage to reduce costs.[^wangAgentWorldModel2026]
- **Code-augmented LLM-as-a-Judge.** The final verdict comes from an [LLM-as-a-Judge](../methods/llm-as-a-judge.md) that combines the agent trajectory with the structured verification signals, and returns one of {Completed, Partially Completed, Agent Error, Environment Error}. The authors argue that code-only verification is brittle under environment imperfections.[^wangAgentWorldModel2026]
- **Two-level tool abstraction.** The agent uses exactly two meta-tools, `list_tools` and `call_tool`, so it discovers each environment's toolset dynamically.[^wangAgentWorldModel2026]

### Reward design

The reward combines step-level format correctness with task-level outcome verification.[^wangAgentWorldModel2026]

- Task-level reward $R_{\tau}$: 1.0 if Completed, 0.1 if Partially Completed, 0.0 otherwise.[^wangAgentWorldModel2026]
- Step-level reward $r_t$: $-1.0$ if a format violation triggers early termination at step $t$; $R_{\tau}$ broadcast to all action steps if the rollout terminates normally; otherwise 0.[^wangAgentWorldModel2026]
- An environment or server error is classified as an environment error with reward $r_t=0$.[^wangAgentWorldModel2026]

### History-aware training

Deployed agents often see a truncated history, while RL pipelines optimize all actions of a rollout in one forward pass over the full history, which creates a distribution mismatch.[^wangAgentWorldModel2026] AWM applies the same sliding-window truncation during optimization: a rollout with $T$ assistant turns is split into $T$ training samples, each conditioned on the system prompt, the initial user message, the first assistant-tool exchange (the `list_tools` call), and the $w=3$ most recent turns, with loss only on the tokens of turn $t$.[^wangAgentWorldModel2026] The GRPO advantage is $A^{(k)}=(R^{(k)}-\bar{R})/\sigma_{R}$ over a group of $G$ rollouts.[^wangAgentWorldModel2026]

## Experiments & Results

### Pipeline statistics

Costs are averaged per 100 samples with GPT-5 as the generation model (Table 1).[^wangAgentWorldModel2026]

| Synthesis Stage | Success (%) | # Trial | Cost ($) |
|---|---|---|---|
| Scenario | – | – | 0.43 |
| Task | – | – | 0.56 |
| Database | 88.3 | 1.12 | 3.59 |
| Sample Data | 88.2 | 1.12 | 13.75 |
| Toolset Schema | – | – | 23.74 |
| Env Code | 86.8 | 1.13 | 12.81 |
| Verification | – | – | 2.21 |
| Total | – | – | 57.09 |

Environment complexity (Table 2). Agent steps and unique tools are measured with Claude-4.5-Sonnet as the agent and a step budget of 20; the completion rate is 62.6%, and 13.7% of tasks exceeded the step budget.[^wangAgentWorldModel2026]

| Metric (#) | Mean | Median | Top 90% |
|---|---|---|---|
| Database Tables | 18.5 | 18.0 | 25.0 |
| Sample Data Records | 129.3 | 121.0 | 192.0 |
| Exposed Tools | 35.1 | 35.0 | 45.0 |
| Environment Code Lines | 1,984.7 | 1,944.0 | 2,586.0 |
| Agent Steps per Task | 8.5 | 6.0 | 20.0 |
| Unique Tools used per Task | 7.1 | 6.0 | 12.0 |

Comparison with existing programming-based environments (Table 3).[^wangAgentWorldModel2026]

| Method | Syn. | Reliance | SQL | # Envs | # Tools | # Code |
|---|---|---|---|---|---|---|
| $\tau$-bench | no | Human | no | 2 | 12.5 | – |
| $\tau^{2}$-bench | no | Human | no | 3 | 22.7 | – |
| MCP-Universe | no | Real APIs | – | 11 | 12.1 | – |
| AutoForge | yes | Tool Doc | no | 10 | – | – |
| [EnvScaler](../methods/envscaler.md) | yes | Task Set | no | 191 | 18.6 | 662.1 |
| AWM | yes | Names Only | yes | 1,000 | 35.1 | 1984.7 |

### Training setup

- Generator and judge: GPT-5.[^wangAgentWorldModel2026]
- Base agents: Qwen3 thinking models at 4B, 8B, and 14B.[^wangAgentWorldModel2026]
- Training is implemented on AgentFly and verl, on a subset of 526 environments and 3,315 tasks.[^wangAgentWorldModel2026]
- GRPO hyperparameters: learning rate $7\times 10^{-7}$, batch size 64, mini-batch size 16, 16 rollouts per task, 1,024 isolated environment instances per step, up to 96 optimization steps, KL coefficient 0.001, entropy coefficient 0.0, clip ratio (high) 0.28, rollout temperature 1.0, max response length 2,048, max model context 32,000, max interaction turn 20, history window size 3.[^wangAgentWorldModel2026]
- Evaluation: temperature 0.6, top-$k$=20, top-$p$=0.95, context window extended to 131,072 tokens via RoPE scaling, history limit loosened to $w=10$ turns for long-context tasks.[^wangAgentWorldModel2026]
- Baselines: Base (untrained model); Simulator (RL in LLM-simulated environments with GPT-5 as the transition model, same tasks and toolsets as AWM); EnvScaler (a concurrent method with 191 programming-based environments). EnvScaler did not release a 14B model.[^wangAgentWorldModel2026]

### Main results (Table 4)

BFCLv3 leaderboard. "Hall." is the hallucination category.[^wangAgentWorldModel2026]

| Size | Method | Non-Live | Live | Multi-Turn | Hall. | Overall |
|---|---|---|---|---|---|---|
| 4B | Base | 61.44 | 63.95 | 39.38 | 73.93 | 54.92 |
| 4B | Simulator | 66.10 | 62.69 | 37.75 | 75.48 | 55.52 |
| 4B | EnvScaler | 60.31 | 64.25 | 37.63 | 85.25 | 54.06 |
| 4B | AWM | 78.60 | 76.91 | 37.99 | 73.70 | 64.50 |
| 8B | Base | 59.58 | 58.03 | 43.88 | 76.42 | 53.83 |
| 8B | Simulator | 56.35 | 59.36 | 41.88 | 74.06 | 52.53 |
| 8B | EnvScaler | 33.67 | 31.83 | 45.00 | 90.30 | 36.83 |
| 8B | AWM | 80.44 | 72.39 | 45.00 | 70.80 | 65.94 |
| 14B | Base | 69.48 | 67.28 | 47.00 | 77.94 | 61.25 |
| 14B | Simulator | 77.23 | 73.43 | 52.38 | 76.91 | 67.68 |
| 14B | AWM | 81.46 | 77.20 | 51.88 | 78.37 | 70.18 |

$\tau^{2}$-bench (verified version). Pass@k is task success rate allowing $k$ attempts; Pass@1 is averaged over 4 runs.[^wangAgentWorldModel2026]

| Size | Method | Airline | Retail | Telecom | Overall Pass@1 | Overall Pass@4 |
|---|---|---|---|---|---|---|
| 4B | Base | 21.00 | 19.96 | 9.43 | 15.83 | 34.89 |
| 4B | Simulator | 15.50 | 18.64 | 7.90 | 13.67 | 35.25 |
| 4B | EnvScaler | 31.50 | 44.30 | 12.50 | 28.96 | 51.80 |
| 4B | AWM | 19.00 | 30.26 | 16.45 | 22.57 | 43.89 |
| 8B | Base | 26.50 | 34.43 | 18.42 | 26.44 | 50.72 |
| 8B | Simulator | 34.00 | 32.24 | 29.17 | 31.30 | 54.32 |
| 8B | EnvScaler | 31.50 | 49.56 | 32.68 | 39.39 | 63.31 |
| 8B | AWM | 38.50 | 41.23 | 23.47 | 33.45 | 55.40 |
| 14B | Base | 27.00 | 65.35 | 12.28 | 36.69 | 55.40 |
| 14B | Simulator | 21.50 | 48.90 | 18.20 | 31.39 | 55.40 |
| 14B | AWM | 31.50 | 63.60 | 17.76 | 39.03 | 57.19 |

MCP-Universe task success rates. 3D design tasks and repository management tasks are excluded.[^wangAgentWorldModel2026]

| Size | Method | Location | Financial | Browser | Web | Multi | Overall |
|---|---|---|---|---|---|---|---|
| 4B | Base | 2.86 | 25.00 | 0.00 | 0.00 | 0.00 | 6.15 |
| 4B | Simulator | 0.00 | 15.00 | 5.88 | 2.00 | 0.00 | 6.15 |
| 4B | EnvScaler | 0.00 | 17.50 | 2.94 | 0.00 | 0.00 | 4.47 |
| 4B | AWM | 0.00 | 22.50 | 2.94 | 2.00 | 5.00 | 6.70 |
| 8B | Base | 0.00 | 22.50 | 5.88 | 2.00 | 0.00 | 6.70 |
| 8B | Simulator | 5.71 | 10.00 | 8.82 | 4.00 | 0.00 | 6.15 |
| 8B | EnvScaler | 0.00 | 17.50 | 5.88 | 2.00 | 0.00 | 5.59 |
| 8B | AWM | 8.57 | 35.00 | 8.82 | 0.00 | 5.00 | 11.17 |
| 14B | Base | 0.00 | 27.50 | 5.88 | 2.00 | 5.00 | 8.38 |
| 14B | Simulator | 2.86 | 30.00 | 8.82 | 6.00 | 0.00 | 10.62 |
| 14B | AWM | 8.57 | 32.50 | 11.77 | 4.00 | 0.00 | 12.29 |

- On $\tau^{2}$-bench, EnvScaler scores higher than AWM at 4B and 8B. The paper describes AWM as competitive with EnvScaler and consistently above Simulator.[^wangAgentWorldModel2026]
- EnvScaler regresses on BFCLv3 (-8.93) and MCP-Universe (-1.39) on average, while AWM improves over Base on all benchmarks. The authors suggest this is plausibly because EnvScaler relies on existing tasks for synthesis that may overlap with $\tau^{2}$-bench.[^wangAgentWorldModel2026]
- AWM is modestly weaker on the BFCLv3 hallucination category, which the authors attribute to the format correctness reward that always encourages tool use and penalizes refusals.[^wangAgentWorldModel2026]

Gains by task complexity, 8B agent (Table 5).[^wangAgentWorldModel2026]

| Bucket | BFCLv3 Base | BFCLv3 AWM | $\Delta$ | $\tau^{2}$ Base | $\tau^{2}$ AWM | $\Delta$ |
|---|---|---|---|---|---|---|
| Simple | 53.6 | 80.3 | +26.7 | 32.7 | 41.9 | +9.3 |
| Medium | 60.0 | 75.3 | +15.3 | 22.7 | 28.8 | +6.2 |
| Hard | 43.9 | 45.0 | +1.1 | 20.5 | 25.0 | +4.5 |

### Environment quality (Table 6)

100 sampled environments, two LLM judges. Scores are on a 1-5 scale.[^wangAgentWorldModel2026]

| Metric | AWM (GPT-5.1) | EnvScaler (GPT-5.1) | AWM (Claude 4.5) | EnvScaler (Claude 4.5) |
|---|---|---|---|---|
| Task Feasibility | 3.68±1.02 | 2.94±1.25 | 3.99±0.81 | 3.14±1.29 |
| Data Alignment | 4.04±0.91 | 3.73±0.89 | 4.84±0.50 | 4.11±1.02 |
| Toolset Completeness | 3.65±0.87 | 2.89±0.79 | 4.98±0.14 | 4.06±0.87 |
| Envs w/ Bugs | 74% | 88% | 83% | 83% |
| # Bugs per Env | 4.13 | 1.82 | 2.70 | 2.21 |
| Blocked Tasks | 14.0% | 57.1% | 11.5% | 46.8% |

- Manual inspection attributes 44% of AWM bugs to unhandled edge input cases and 14% to operations conflicting with database constraints.[^wangAgentWorldModel2026]
- During RL training the environment error rate stays around 4%.[^wangAgentWorldModel2026]

Generator model comparison on 100 environments, 1,000 tasks (Table 7).[^wangAgentWorldModel2026]

| Metric | GPT-5 | Claude-4.5 | Qwen3.5 |
|---|---|---|---|
| Database Synthesis success (%) | 88.3 | 100.0 | 79.0 |
| Sample Data Synthesis success (%) | 88.2 | 100.0 | 97.0 |
| Env. Code Synthesis success (%) | 86.8 | 99.0 | 77.0 |
| Task Feasibility (1-5) | 3.99 | 3.84 | 3.15 |
| Data Alignment (1-5) | 4.84 | 4.92 | 4.32 |
| Toolset Completeness (1-5) | 4.98 | 4.97 | 4.30 |
| Envs w/ Bugs (%) | 83 | 89 | 100 |
| # Bugs per Env | 2.70 | 2.11 | 3.82 |
| Mean Pairwise Distance | 0.34 | 0.31 | 0.35 |

### Task difficulty (Table 8)

Pass@1 (%) on synthesized tasks. Buckets are defined by required tool calls: 1-3, 4-6, 7-10, and 11+.[^wangAgentWorldModel2026]

| | Simple | Medium | Hard | Very Hard |
|---|---|---|---|---|
| Tasks Ratio (%) | 35.1 | 31.5 | 15.7 | 17.7 |
| Avg. Steps | 3.3 | 5.8 | 9.1 | 17.9 |
| GPT-5.1 | 61.7 | 27.0 | 11.9 | 3.0 |
| Sonnet-4.5 | 68.4 | 71.8 | 63.3 | 31.0 |
| Both Pass | 45.3 | 24.9 | 11.5 | 3.0 |
| Neither Pass | 15.2 | 26.2 | 36.3 | 69.0 |

Overall the two models achieve 36.1% and 62.6% Pass@1. In the RL training logs, 27.1%, 23.7%, and 28.2% of tasks are never solved by Qwen3-4B/8B/14B during the entire training process (14B only optimizes for 32 steps).[^wangAgentWorldModel2026]

### Diversity

Embedding diversity stays stable as the pool grows and category coverage increases steadily (reported as a figure).[^wangAgentWorldModel2026] At the code level, the cross-environment AST function duplicate rate (TSED, threshold ≥ 0.5) is 0.0%, token Jaccard is 0.183 mean and 0.324 max, endpoint name Jaccard is 0.004, and class name Jaccard is 0.009.[^wangAgentWorldModel2026]

### Verification design (Table 9)

| Size | Verification | BFCLv3 | $\tau^{2}$ P@1 | $\tau^{2}$ P@4 | MCP |
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

The extra cost of GPT-5 as the judge is about $1.80 per training step (at most 1,024 samples).[^wangAgentWorldModel2026]

Judge reliability on 100 sampled trajectories from the 8B agent, each judged 5 times (Tables 10 and 13).[^wangAgentWorldModel2026]

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

### Format correctness reward

With the step-level format reward, the format error ratio converges quickly to a low level and average rollout time drops by about 27%. Without it, the format error ratio stays above 20% even after 50 optimization steps and the task completion rate saturates below 40%.[^wangAgentWorldModel2026]

### History-aware training (Table 11, 4B model)

"Aligned" uses the same history limit (HL) setting for training and inference. "Misaligned" uses opposite settings.[^wangAgentWorldModel2026]

| Setting | Method | BFCLv3 | $\tau^{2}$ P@1 | $\tau^{2}$ P@4 | MCP |
|---|---|---|---|---|---|
| Aligned | w/ HL | 64.50 | 22.57 | 43.89 | 6.70 |
| Aligned | w/o HL | 55.35 | 15.92 | 36.33 | 6.15 |
| Misaligned | w/ HL | 61.85 | 9.35 | 15.11 | 5.03 |
| Misaligned | w/o HL | 56.80 | 16.10 | 33.09 | 6.15 |

### Environment scaling (Figure 4, 4B model)

Values are read from the bar labels of the figure; the source gives them only in the figure.[^wangAgentWorldModel2026]

| # Environments | Method | BFCL | $\tau^{2}$ | MCP |
|---|---|---|---|---|
| 10 | AWM | 48.0 | 14.2 | 3.9 |
| 100 | AWM | 57.0 | 16.6 | 6.1 |
| 191 | AWM | 57.6 | 16.4 | 6.1 |
| 191 | EnvScaler | 54.1 | 29.0 | 4.5 |
| 526 | AWM | 64.5 | 22.6 | 6.7 |

Training on 10 environments leads to severe performance degradation, which the authors attribute to likely overfitting. At a matched count AWM outperforms EnvScaler on BFCLv3 and MCP-Universe.[^wangAgentWorldModel2026]

## Limitations

- The pipeline is a fixed generation process with no self-evolving loop in which a trained agent helps synthesize new environments.[^wangAgentWorldModel2026]
- Self-correction works by trial and error on runtime errors, without deeper semantic validation. Tasks do not span multiple scenarios or environments.[^wangAgentWorldModel2026]
- Agents are trained on 526 of the 1,000 environments, and only on the Qwen3 family at 4B, 8B, and 14B.[^wangAgentWorldModel2026]
- 74% of environments contain at least one bug and about 4% of RL rollouts hit runtime errors. Behavior under intentionally injected adversarial perturbations is not evaluated.[^wangAgentWorldModel2026]
- Tasks assume a post-authentication context, so access-control behavior is not trained.[^wangAgentWorldModel2026]
- AWM does not target conversational interaction, omits refusal scenarios, and excludes browser automation and information retrieval, which the three evaluation benchmarks respectively require or stress.[^wangAgentWorldModel2026]
- Synthetic environments may not fully reflect real-world scenarios.[^wangAgentWorldModel2026]

## Related

- Methods: [Agent World Model](../methods/agent-world-model.md), [GRPO](../methods/grpo.md), [LLM-as-a-Judge](../methods/llm-as-a-judge.md), [Model Context Protocol](../methods/mcp.md)
- Methods compared against: [EnvScaler](../methods/envscaler.md)
- Benchmarks: [BFCL](../benchmarks/bfcl.md), [$\tau^{2}$-bench](../benchmarks/tau2-bench.md), [MCP-Universe](../benchmarks/mcp-universe.md)
- Papers in this wiki cited by this paper: [SWE-agent](yangSWEagentAgentComputerInterfaces2024.md)

[^wangAgentWorldModel2026]: Wang et al. 2026
