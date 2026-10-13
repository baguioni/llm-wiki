---
type: Paper
title: "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"
description: Introduces the agent-computer interface (ACI) and SWE-agent, an LM agent whose custom file viewer, editor, search, and context management commands resolve 12.47% of SWE-bench with GPT-4 Turbo.
tags: [software-engineering-agents, agent-computer-interface, llm-agents, code-editing, swe-bench, ai899]
collections: [ai899]
authors: [John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press]
doi: 10.48550/arXiv.2405.15793
arxiv: "2405.15793"
arxiv_version: 2405.15793v3
code: https://swe-agent.com/
sources:
  - id: yangSWEagentAgentComputerInterfaces2024
    resource: zotero://select/items/@yangSWEagentAgentComputerInterfaces2024
    title: "SWE-Agent: Agent-Computer Interfaces Enable Automated Software Engineering"
---

# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

Text source: arXiv HTML, version `2405.15793v3`.

## Summary

The paper argues that language model (LM) agents are a new category of end user with their own needs and abilities, and that they benefit from interfaces built for them rather than interfaces built for humans, such as the Linux shell.[^yangSWEagentAgentComputerInterfaces2024] It names the abstraction layer between an LM agent and a computer the [agent-computer interface (ACI)](../methods/agent-computer-interface.md): the ACI specifies the commands available to the LM, how environment state is communicated back, and how the history of commands and observations is formatted into the LM input.[^yangSWEagentAgentComputerInterfaces2024]

[SWE-agent](../methods/swe-agent.md) is an agent composed of an LM and an ACI for software engineering. It offers a small set of simple actions for viewing, searching, and editing files, uses guardrails to prevent common mistakes, and returns specific, concise feedback at every turn.[^yangSWEagentAgentComputerInterfaces2024] With GPT-4 Turbo, SWE-agent solves 12.47% (286/2294) of the full [SWE-bench](../benchmarks/swe-bench.md) test set and 18.00% (54/300) of [SWE-bench Lite](../benchmarks/swe-bench-lite.md), against a previous best resolve rate of 3.8% by a non-interactive, retrieval-augmented system.[^yangSWEagentAgentComputerInterfaces2024] On [HumanEvalFix](../benchmarks/humanevalfix.md) the abstract and Table 2 report a pass@1 rate of 87.7% (Python).[^yangSWEagentAgentComputerInterfaces2024]

## Contributions

- The concept of the agent-computer interface (ACI), with a demonstration that careful ACI design substantially improves LM agent performance without modifying the underlying LM's weights.[^yangSWEagentAgentComputerInterfaces2024]
- SWE-agent, an open-sourced system that gives LMs an ACI for solving real-world software engineering tasks.[^yangSWEagentAgentComputerInterfaces2024]
- Four ACI design principles: actions should be simple and easy to understand; actions should be compact and efficient; environment feedback should be informative but concise; guardrails mitigate error propagation and hasten recovery.[^yangSWEagentAgentComputerInterfaces2024]
- Ablations of the editor, search, file viewer, and context management on SWE-bench Lite, plus an analysis of agent trajectories and failure modes.[^yangSWEagentAgentComputerInterfaces2024]
- The paper states that, to the best of the authors' knowledge, SWE-agent is the first work to explore language agents for end-to-end software engineering.[^yangSWEagentAgentComputerInterfaces2024]

## Method

### Design process

The LM is held fixed and the ACI is designed around it: the actions, their documentation, and the environment feedback are shaped to complement the LM's limitations and abilities.[^yangSWEagentAgentComputerInterfaces2024] The authors (1) manually inspected agent behavior on a small set of hand-picked examples from the SWE-bench development split to identify difficulties and propose improvements, and (2) ran a grid search over window size, history processing, and decoding temperature.[^yangSWEagentAgentComputerInterfaces2024]

At each step SWE-agent generates a thought and a command and then incorporates the feedback from the command's execution, following [ReAct](../methods/react.md).[^yangSWEagentAgentComputerInterfaces2024] It is built atop the Linux shell, so common Linux commands and utilities remain available.[^yangSWEagentAgentComputerInterfaces2024]

### ACI components

| Component | Commands | Behavior |
|---|---|---|
| Search and navigation | `find_file`, `search_file`, `search_dir` | `find_file` searches for filenames in the repository; `search_file` and `search_dir` locate strings in a file or in the files of a directory. Output is a summary of results. At most 50 results are returned per query; beyond that, results are not reported and the agent is asked to write a more specific query. |
| File viewer | `open`, `goto`, `scroll_down`, `scroll_up` | Shows a window of at most 100 lines of the open file. Displays the full path of the file, the total number of lines, the number of lines omitted before and after the window, and a line number prepended to each visible line. |
| File editor | `edit`, `create` | `edit` takes 3 required arguments (start line, end line, replacement text) and replaces that line range in the open file in a single step. After the edit, the file viewer automatically shows the updated content. |
| Task | `submit` | Generates and submits the patch from all previous edits and closes the shell. |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

- **Linting guardrail.** A code linter is integrated into `edit`. After an edit is applied, `flake8 --isolated --select=F821,F822,F831,E111,E112,E113,E999,E902` is run on the open file. If it produces output, the edit is reverted and the agent sees the error, what the edit would have looked like, and the original file content.[^yangSWEagentAgentComputerInterfaces2024] The guardrail assumes the original codebase of each task instance is well-formed.[^yangSWEagentAgentComputerInterfaces2024]
- **Context management.** Agents receive instructions, documentation, and demonstrations on the correct use of bash and ACI commands. Observations preceding the last 5 are each collapsed into a single line.[^yangSWEagentAgentComputerInterfaces2024] If a command produces no output, the message "Your command ran successfully and did not produce any output" is shown.[^yangSWEagentAgentComputerInterfaces2024]
- **Malformed responses.** A malformed generation triggers an error response asking the agent to try again; once a valid generation is received, all past error messages except the first are omitted. If a model generates 3 malformed responses in a row, the episode terminates early.[^yangSWEagentAgentComputerInterfaces2024]
- **Instance tips.** The instance template includes manually written tips derived from failure modes observed on the development set.[^yangSWEagentAgentComputerInterfaces2024]

### Implementation

The environment is heavily influenced by the [InterCode](../methods/intercode.md) library, adopts its interactive coding task formulation, and uses Docker containers for reproducible and safe execution.[^yangSWEagentAgentComputerInterfaces2024] An ACI is specified by a single `.yaml` configuration file with four categories of components: prompt templates, command files (bash or Python functions), control flow (response parsing and history processing), and environment variables.[^yangSWEagentAgentComputerInterfaces2024]

## Experiments & Results

### Setup

- Datasets: SWE-bench (2294 task instances from 12 repositories of popular Python packages) for main results; SWE-bench Lite (a canonical subset of 300 instances focused on self-contained functional bug fixes) for ablations and analysis; HumanEvalFix (164 problems per language) for basic code editing.[^yangSWEagentAgentComputerInterfaces2024]
- Models: GPT-4 Turbo (`gpt-4-1106-preview`, 128k token context window) and Claude 3 Opus (`claude-3-opus-20240229`, 200k token context window).[^yangSWEagentAgentComputerInterfaces2024] Llama 3 and DeepSeek Coder were tried, but the paper reports their performance in the agent setting as subpar.[^yangSWEagentAgentComputerInterfaces2024]
- Baselines: non-interactive [RAG](../methods/retrieval-augmented-generation.md) with BM25 retrieval, as established in SWE-bench; and Shell-only, an agent that interacts with a Linux shell process, adapted from InterCode.[^yangSWEagentAgentComputerInterfaces2024]
- Metrics: % Resolved (pass@1), the proportion of instances for which all tests pass after the generated patch is applied; and $ Avg. Cost, the API inference cost averaged over all successfully resolved instances. The per-instance budget is $4; when a run exceeds it, existing edits are submitted automatically.[^yangSWEagentAgentComputerInterfaces2024]
- Configuration used for the test sets: temperature 0.0, window 100, history Last-5.[^yangSWEagentAgentComputerInterfaces2024]

### Main results (Table 1)

| Setting | SWE-bench % Resolved | SWE-bench $ Avg. Cost | SWE-bench Lite % Resolved | SWE-bench Lite $ Avg. Cost |
|---|---|---|---|---|
| RAG w/ GPT-4 Turbo | 1.31 | 0.13 | 2.67 | 0.13 |
| RAG w/ Claude 3 Opus | 3.79 | 0.25 | 4.33 | 0.25 |
| Shell-only agent w/ GPT-4 Turbo | - | - | 11.00 | 1.46 |
| Shell-only agent w/o Demonstration | - | - | 7.33 | 0.79 |
| SWE-agent w/ GPT-4 Turbo | 12.47 | 1.59 | 18.00 | 1.67 |
| SWE-agent w/ Claude 3 Opus | 10.46 | 2.59 | 13.00 | 2.18 |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

- Compared to RAG on Lite, SWE-agent is 8-13x more costly but yields a 6.7-fold improved % Resolved rate.[^yangSWEagentAgentComputerInterfaces2024]
- SWE-agent shows a 64% relative increase compared to Shell-only, both with GPT-4 Turbo.[^yangSWEagentAgentComputerInterfaces2024]

### HumanEvalFix pass@1 (Table 2)

Scores other than SWE-agent are as reported in Yu et al.[^yangSWEagentAgentComputerInterfaces2024]

| Model | Python | JS | Java |
|---|---|---|---|
| CodeLLaMa-instruct-13B | 29.2 | 19.5 | 32.3 |
| GPT-4 | 47.0 | 48.2 | 50.0 |
| DeepseekCoder-CodeAlpaca-6.7B | 49.4 | 51.8 | 45.1 |
| WaveCoder-DS-6.7B | 57.9 | 52.4 | 57.3 |
| SWE-agent w/ GPT-4 Turbo | 87.7 | 89.7 | 87.9 |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

The abstract and Table 2 give 87.7%, while the running text of Section 5 gives an $88.3$% pass@1 rate on HumanEvalFix. The paper does not explain the difference.[^yangSWEagentAgentComputerInterfaces2024]

### ACI ablations on SWE-bench Lite (Table 3)

SWE-agent w/ GPT-4 Turbo. % Resolved, with the drop from the default configuration (18.0).[^yangSWEagentAgentComputerInterfaces2024]

| Component | Variant | % Resolved | Change |
|---|---|---|---|
| Editor | edit action w/ linting (default) | 18.0 | |
| Editor | edit action (without linting) | 15.0 | ↓ 3.0 |
| Editor | No edit | 10.3 | ↓ 7.7 |
| Search | Summarized (default) | 18.0 | |
| Search | Iterative | 12.0 | ↓ 6.0 |
| Search | No search | 15.7 | ↓ 2.3 |
| File viewer | 100 lines (default) | 18.0 | |
| File viewer | 30 lines | 14.3 | ↓ 3.7 |
| File viewer | Full file | 12.7 | ↓ 5.3 |
| Context | Last 5 Obs. (default) | 18.0 | |
| Context | Full history | 15.0 | ↓ 3.0 |
| Context | w/o demo. | 16.3 | ↓ 1.7 |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

Iterative search, which shows results one by one with `next` and `prev` as in Vim or VSCode, performs worse than having no search tools at all, because agents tend to look through every match exhaustively and exhaust their cost budget or context window.[^yangSWEagentAgentComputerInterfaces2024]

### Hyperparameter sweep (Table 5)

Subset of 37 instances sampled randomly from the SWE-bench dev split; % Resolved is the mean across 5 samples.[^yangSWEagentAgentComputerInterfaces2024]

| Model | Temperature | Window | History | % Resolved |
|---|---|---|---|---|
| GPT-4 Turbo | 0.0 | 100 | Full | 14.1 |
| GPT-4 Turbo | 0.0 | 100 | Last 5 Obs. | 15.1 |
| GPT-4 Turbo | 0.0 | 200 | Full | 9.2 |
| GPT-4 Turbo | 0.0 | 200 | Last 5 Obs. | 10.8 |
| GPT-4 Turbo | 0.2 | 100 | Full | 10.8 |
| GPT-4 Turbo | 0.2 | 100 | Last 5 Obs. | 12.4 |
| GPT-4 Turbo | 0.2 | 200 | Full | 8.7 |
| GPT-4 Turbo | 0.2 | 200 | Last 5 Obs. | 10.8 |
| Claude 3 Opus | 0.0 | 100 | Full | 5.4 |
| Claude 3 Opus | 0.0 | 100 | Last 5 Obs. | 8.1 |
| Claude 3 Opus | 0.0 | 200 | Full | 7.0 |
| Claude 3 Opus | 0.0 | 200 | Last 5 Obs. | 7.1 |
| Claude 3 Opus | 0.2 | 100 | Full | 7.4 |
| Claude 3 Opus | 0.2 | 100 | Last 5 Obs. | 8.1 |
| Claude 3 Opus | 0.2 | 200 | Full | 8.1 |
| Claude 3 Opus | 0.2 | 200 | Last 5 Obs. | 6.8 |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

### Variance and pass@k (Table 10)

6 separate runs of SWE-agent with GPT-4 on SWE-bench Lite.[^yangSWEagentAgentComputerInterfaces2024]

| | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Run 6 |
|---|---|---|---|---|---|---|
| Resolve % | 17.33 | 18.00 | 18.00 | 18.67 | 17.33 | 18.33 |

| | Pass@1 | Pass@2 | Pass@3 | Pass@4 | Pass@5 | Pass@6 |
|---|---|---|---|---|---|---|
| Pass@k | 17.94 | 23.89 | 27.35 | 29.67 | 31.33 | 32.67 |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

The paper concludes that average performance variance is relatively low, but per-instance resolution can change considerably.[^yangSWEagentAgentComputerInterfaces2024]

### Performance by year on SWE-bench Lite (Table 7)

| Year (instances) | SWE-agent GPT 4 | SWE-agent Claude 3 Opus | RAG GPT 4 | RAG Claude 3 Opus | RAG Claude 2 |
|---|---|---|---|---|---|
| 2023 (30) | 23.33% | 13.33% | 3.33% | 3.33% | 0.0% |
| 2022 (57) | 21.05% | 17.54% | 5.26% | 7.02% | 1.75% |
| 2021 (42) | 23.81% | 11.90% | 2.38% | 4.76% | 2.38% |
| 2020 (66) | 10.61% | 07.58% | 3.03% | 1.52% | 1.52% |
| Before 2020 (105) | 17.14% | 10.48% | 0.95% | 4.76% | 5.71% |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

The paper finds no clear correlation between a task instance's creation year and its resolution rate.[^yangSWEagentAgentComputerInterfaces2024] A per-repository breakdown is given in Table 6 of the paper; for example, SWE-agent w/ GPT 4 resolves 26.32% of django/django (114 instances) and 10.39% of sympy/sympy (77 instances) on SWE-bench Lite.[^yangSWEagentAgentComputerInterfaces2024]

### Agent behavior

- **Trajectory shape.** Trajectories begin with reproduction (`create`) or localization (`find_file`/`search_dir`); from turn 5 onwards the most frequent two actions are `edit` and `python`.[^yangSWEagentAgentComputerInterfaces2024] The most frequent opening pattern in resolved trajectories is `create, edit, python`, which appears 156 times at turns 1-3.[^yangSWEagentAgentComputerInterfaces2024]
- **Turns to resolution.** On resolved instances of the full test set, SWE-agent w/ GPT-4 takes an average of 14.71 turns, with a median of 12 turns and 75% of trajectories completed within 18 turns. On Lite, SWE-agent w/ Claude 3 Opus takes an average of 12.71 turns, a median of 13 turns, and 75% of trajectories complete within 15 turns.[^yangSWEagentAgentComputerInterfaces2024]
- **Agents succeed quickly and fail slowly.** Successful instances solved by SWE-agent w/ GPT 4 finish with a median cost of $1.21 and 12 steps, compared to a mean of $2.52 and 21 steps for unsuccessful ones. 93.0% of resolved instances are submitted before exhausting the cost budget, compared to 69.0% of instances overall.[^yangSWEagentAgentComputerInterfaces2024] The authors suspect that increasing the maximum budget or token limit is unlikely to substantially increase performance.[^yangSWEagentAgentComputerInterfaces2024]
- **Submit vs. cost exit.** For SWE-agent with GPT-4 Turbo on full SWE-bench, 14.3% of task instances that end with a `submit` are resolved, against 3.1% for those finishing on `exit_cost`.[^yangSWEagentAgentComputerInterfaces2024]
- **Failed edits.** Out of 2294 task instances, 1185 (51.7%) of SWE-agent w/ GPT-4 Turbo trajectories have 1+ failed edits (edits that raise a linting error), with a median of 3 failed edits per such trajectory and a max of 33. Out of 286 resolved instances, 113 (31.5%) have at least one failed edit.[^yangSWEagentAgentComputerInterfaces2024]
- **Edit recovery.** Any attempt at editing has a 90.5% chance of eventually being successful; this drops to 57.2% after a single failed edit. Across all task instances there are 810 successful recoveries versus 555 unsuccessful ones.[^yangSWEagentAgentComputerInterfaces2024]
- **File localization.** Measured as F1 between the files edited or removed by the prediction and by the gold patch, SWE-agent w/ GPT-4 Turbo achieves 59.05%, while BM25 w/ Claude 3 Opus produces 45.47%.[^yangSWEagentAgentComputerInterfaces2024]
- **Patch size.** Models tend to generate larger edits than the corresponding gold solution, which the paper largely attributes to additional reproduction code. For resolved instances, SWE-agent w/ GPT-4 Turbo patches add 3.0 / 5.7 lines (median / mean) against 2.0 / 3.58 for the gold patches.[^yangSWEagentAgentComputerInterfaces2024]

### Failure modes

Unresolved trajectories of SWE-agent w/ GPT-4 Turbo on SWE-bench Lite (n=248) were categorized automatically with GPT-4o (`gpt-4o-2024-05-13`) into 9 manually defined categories; on a hand-labeled validation set of 15 instances the LM's labels agree with the authors' on 87% of instances.[^yangSWEagentAgentComputerInterfaces2024]

| Failure category | Share of unresolved instances |
|---|---|
| Incorrect Implementation or Overly Specific Implementation | 52.0% |
| Failed Edit Recovery | 23.4% |
| Remaining failure modes | less than 25% |

All rows: [^yangSWEagentAgentComputerInterfaces2024]

## Limitations

- The final configuration has a small toolkit. The authors suggest adding tools such as web browsing, static/dynamic analysis, spectrum based fault localization, or test generation via fuzzing.[^yangSWEagentAgentComputerInterfaces2024]
- The ACI development process and case studies are done manually; automating part or all of the process is left to future work.[^yangSWEagentAgentComputerInterfaces2024]
- The scope is exclusively programmatic tasks such as software engineering and code generation; whether the ACI principles transfer to other domains is open.[^yangSWEagentAgentComputerInterfaces2024]
- The editing guardrail forces some edits to be done in a particular order, and the 50-result search limit forces the model to generate another query, which can be an expensive operation.[^yangSWEagentAgentComputerInterfaces2024]
- Agents struggle to use later turns: if the initial approach in the first 10 to 20 turns does not yield a good solution, the agent tends to continue local editing rather than explore further.[^yangSWEagentAgentComputerInterfaces2024]
- The authors are unsure whether demonstrations help agents with domain specific problem solving; they think the demonstration primarily helps the agent issue properly formatted commands.[^yangSWEagentAgentComputerInterfaces2024]
- The ACI was developed for GPT-4 Turbo; with Claude 3 Opus, slightly less than 50% of all task instances are submitted intentionally, and the slight majority are auto-submitted when the cost limit is hit.[^yangSWEagentAgentComputerInterfaces2024]

## Related

- Methods: [SWE-agent](../methods/swe-agent.md), [Agent-computer interface](../methods/agent-computer-interface.md), [ReAct](../methods/react.md), [InterCode](../methods/intercode.md), [Retrieval-augmented generation](../methods/retrieval-augmented-generation.md)
- Benchmarks: [SWE-bench](../benchmarks/swe-bench.md), [SWE-bench Lite](../benchmarks/swe-bench-lite.md), [HumanEvalFix](../benchmarks/humanevalfix.md)
- Papers in this wiki cited by this paper: [Reflexion](shinnReflexionLanguageAgents2023.md), [MemGPT](packerMemGPTLLMsOperating2024.md)

[^yangSWEagentAgentComputerInterfaces2024]: Yang et al. 2024
