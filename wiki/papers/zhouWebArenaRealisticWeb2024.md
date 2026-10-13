---
type: Paper
title: "WebArena: A Realistic Web Environment for Building Autonomous Agents"
description: A standalone, self-hostable web environment of fully functional websites with an 812-task benchmark that scores web agents by the functional correctness of task completion.
tags: [web-agents, benchmark, autonomous-agents, llm-agents, evaluation, ai899]
collections: [ai899]
authors: [Shuyan Zhou, Frank F. Xu, Hao Zhu, Xuhui Zhou, Robert Lo, Abishek Sridhar, Xianyi Cheng, Tianyue Ou, Yonatan Bisk, Daniel Fried, Uri Alon, Graham Neubig]
arxiv: "2307.13854"
arxiv_version: 2307.13854v4
code: https://webarena.dev/
sources:
  - id: zhouWebArenaRealisticWeb2024
    resource: zotero://select/items/@zhouWebArenaRealisticWeb2024
    title: "WebArena: A Realistic Web Environment for Building Autonomous Agents"
---

# WebArena: A Realistic Web Environment for Building Autonomous Agents

Text source: arXiv HTML, version `2307.13854v4`.

## Summary

Existing environments for evaluating language-guided agents over-simplify real-world situations: they have limited functionality and task diversity, some are static resources restricted to cached states, and many evaluate by comparing the surface form of action sequences with a reference instead of checking functional correctness.[^zhouWebArenaRealisticWeb2024]

[WebArena](../benchmarks/webarena.md) is a realistic and reproducible web environment. It has four fully operational, self-hosted web applications (online shopping, discussion forums, collaborative development, and business content management), utility tools (map, calculator, scratchpad), and knowledge resources such as English Wikipedia and user manuals.[^zhouWebArenaRealisticWeb2024] It ships with a benchmark of 812 long-horizon tasks, each given as a high-level natural language intent and evaluated for functional correctness.[^zhouWebArenaRealisticWeb2024] The best GPT-4-based agent reaches an end-to-end task success rate of 14.41%, against a human performance of 78.24%.[^zhouWebArenaRealisticWeb2024]

## Contributions

- A standalone web environment built from open-source software with data imported from real-world counterparts, delivered as Docker containers with gym-APIs.[^zhouWebArenaRealisticWeb2024]
- A benchmark of 812 test examples instantiated from 241 templates, with a metric per example that evaluates the functional correctness of the execution.[^zhouWebArenaRealisticWeb2024]
- Baseline agents built with few-shot in-context learning on GPT-4, GPT-3.5, and text-bison-001, with and without chain-of-thought reasoning, and an error analysis.[^zhouWebArenaRealisticWeb2024]
- The paper states that WebArena is the first web environment to consider multi-tab web-based tasks, and to its knowledge the first publicly available agent evaluation environment with pre-logged-in user profiles that have distinct roles.[^zhouWebArenaRealisticWeb2024]

## Method

### Environment

- The environment is $\mathcal{E}=\langle\mathcal{S},\mathcal{A},\mathcal{O},\mathcal{T}\rangle$ with a deterministic transition function defined by the implementation of each website. A reward function $r(\mathbf{a}_1^T,\mathbf{s}_1^T)$ measures the success of a task execution.[^zhouWebArenaRealisticWeb2024]
- Website categories were chosen by analyzing approximately 200 examples from the authors' own web browser histories, then taking the four most salient categories.[^zhouWebArenaRealisticWeb2024]
- Reproducibility comes from not relying on live websites, which avoids CAPTCHAs, unpredictable content modifications, and configuration changes.[^zhouWebArenaRealisticWeb2024]

| Site | Implementation | Data |
|---|---|---|
| E-commerce (OneStopShop) | Adobe Magento | approximately 90$k$ products with prices, options, descriptions, images, and reviews, spanning over 300 product categories |
| Social forum (Reddit) | Postmill | 95 subreddits, 127390 posts, and 661781 users |
| Collaborative development | GitLab | 300 repositories and more than 1000 accounts with at least one commit to a repository |
| Content management system (CMS) | Adobe Magento's admin portal | sample data provided in the official guide |
| Map | OpenStreetMap | northeast US region only, due to data storage constraints |
| Wikipedia | Kiwix, offline English Wikipedia | knowledge cutoff of May 2023 |
| Calculator, scratchpad | implemented by the authors | not applicable |
| User manuals | scraped from the official websites | GitLab and Adobe Commerce Merchant documentation |

All rows: [^zhouWebArenaRealisticWeb2024]

- **Delivery and reset.** Each website is a separate, fully self-contained Docker image that includes the site's data. Resetting to the initial state means restarting the container from the original image, which takes from a few seconds to one minute depending on the website.[^zhouWebArenaRealisticWeb2024]
- **User roles.** Each platform has a unique user profile: a shopping customer with over 35 orders within a span of two years, a GitLab user who maintains several popular open-source projects, an active Reddit user, and a CMS shop owner with full read-and-write access. Users are logged in automatically with a pre-cached cookie.[^zhouWebArenaRealisticWeb2024]

### Observation and action space

- **Observation:** the web page URL, the opened tabs, and the content of the focused tab. Content can be rendered as raw HTML (DOM tree), a screenshot (RGB array), or the accessibility tree, which is a subset of the DOM tree with the elements relevant for displaying the page. Content can be limited to the viewport.[^zhouWebArenaRealisticWeb2024]
- **Actions** (three groups: element operations, tab actions, URL navigation):[^zhouWebArenaRealisticWeb2024]

| Action Type | Description |
|---|---|
| noop | Do nothing |
| click(elem) | Click at an element |
| hover(elem) | Hover on an element |
| type(elem, text) | Type to an element |
| press(key_comb) | Press a key comb |
| scroll(dir) | Scroll up and down |
| tab_focus(index) | focus on $i$-th tab |
| new_tab | Open a new tab |
| tab_close | Close current tab |
| go_back | Visit the last URL |
| go_forward | Undo go_back |
| goto(URL) | Go to URL |

- An element can be selected by on-screen coordinates $(x,y)$ or by a unique element ID prepended to each element, which turns element selection into an $n$-way classification problem.[^zhouWebArenaRealisticWeb2024]

### Benchmark construction

- Intents were written by the authors to be abstract and high-level (not solvable in one or two actions), creative, and formulated as templates with variables. There are 241 templates and 812 instantiated intents, an average of 3.3 examples per template.[^zhouWebArenaRealisticWeb2024]
- Three intent categories: information seeking (a textual response is expected), site navigation, and content and configuration operation.[^zhouWebArenaRealisticWeb2024]
- **Unachievable tasks** are labeled "N/A", and the agent is expected to produce an equivalent response.[^zhouWebArenaRealisticWeb2024]

Evaluation functions:[^zhouWebArenaRealisticWeb2024]

| Function | Applies to | Check |
|---|---|---|
| `exact_match` | information seeking ($r_{\textrm{info}}$) | only an answer identical to the reference scores one |
| `must_include` | information seeking ($r_{\textrm{info}}$) | any answer containing the reference scores one |
| `fuzzy_match` | information seeking ($r_{\textrm{info}}$) | gpt-4-0613 judges whether the answer is semantically equivalent to the reference; only "correct" scores one |
| $r_{\textrm{prog}}(\mathbf{s})$ | site navigation, content & config | a locator (database query, website API call, or JavaScript element selection) retrieves the critical content from the intermediate states, then `exact_match` or `must_include` checks annotated keywords |

- **Annotation.** Each information-seeking reference answer was annotated twice, and a third annotator finalized disagreements. Evaluation programs were written by three of the authors.[^zhouWebArenaRealisticWeb2024]

### Baseline agents

- Three LLMs with two prompting strategies, each with two in-context examples: direct next-action prediction, and chain-of-thought (CoT) reasoning before the action.[^zhouWebArenaRealisticWeb2024]
- **UA hint:** an instruction that asks the agent to stop (answer "N/A") if it believes the task is impossible.[^zhouWebArenaRealisticWeb2024]
- Observation: the accessibility tree with element IDs.[^zhouWebArenaRealisticWeb2024]
- Models: GPT-3.5-turbo-16k-0613, GPT-4-0613, and text-bison-001, with a temperature of $1.0$ and a top-$p$ of $0.9$. The maximum number of state transitions is 30. Execution halts if the same action is repeated more than three times on the same observation or if the agent generates three consecutive invalid actions. text-bison-001 gets ten retries to generate a valid action.[^zhouWebArenaRealisticWeb2024]

## Experiments & Results

### End-to-end task success rate (Table 2)

SR is the success rate (%) over all tasks, SR$_{\textrm{AC}}$ over achievable tasks, and SR$_{\textrm{UA}}$ over unachievable tasks.[^zhouWebArenaRealisticWeb2024]

| CoT | UA Hint | Model | SR | SR$_{\textrm{AC}}$ | SR$_{\textrm{UA}}$ |
|---|---|---|---|---|---|
| ✓ | ✓ | text-bison-001 | 5.05 | 4.00 | 27.78 |
| ✗ | ✓ | GPT-3.5 | 6.41 | 4.90 | 38.89 |
| ✓ | ✓ | GPT-3.5 | 8.75 | 6.44 | 58.33 |
| ✓ | ✓ | GPT-4 | 11.70 | 8.63 | 77.78 |
| ✗ | ✗ | GPT-3.5 | 5.10 | 4.90 | 8.33 |
| ✓ | ✗ | GPT-3.5 | 6.16 | 6.06 | 8.33 |
| ✓ | ✗ | GPT-4 | 14.41 | 13.02 | 44.44 |
| - | ✓ | Human | 78.24 | 77.30 | 100.00 |

All rows: [^zhouWebArenaRealisticWeb2024]

- With the UA hint, CoT brings a 2.34% improvement for GPT-3.5 over the version without it.[^zhouWebArenaRealisticWeb2024]
- GPT-3.5-turbo-16k-0613 with CoT, no UA hint, and temperature 0.0 has an SR of 6.28 (Table 5).[^zhouWebArenaRealisticWeb2024]

### Human performance

One task was sampled from each of 170 templates and performed by five computer science graduate students.[^zhouWebArenaRealisticWeb2024]

| Metric | Value |
|---|---|
| Avg. Time | 110s |
| Success Rate (info) | 74.68% |
| Success Rate (others) | 81.32% |
| Success Rate (all) | 78.24% |

All rows: [^zhouWebArenaRealisticWeb2024]

50% of the human failures are due to misinterpreting the intent, incomplete answers, and incomplete executions. The remaining failures are more severe, with off-target executions.[^zhouWebArenaRealisticWeb2024]

### Analysis

- **Early stopping.** With the UA hint, GPT-4 erroneously identifies 54.9% of feasible tasks as impossible. Removing the hint raises GPT-4's overall success rate to 14.41%, and GPT-4 still recognizes 44.44% of unachievable tasks.[^zhouWebArenaRealisticWeb2024]
- GPT-3.5 rarely gives reasons of non-achievability. It tends to hallucinate incorrect answers, repeat invalid actions, or exceed the step limits.[^zhouWebArenaRealisticWeb2024]
- **Consistency across a template.** Of the 61 templates with at least one successful execution on the GPT models (no UA hint), GPT-4 reaches a 100% task success rate on only four templates, and GPT-3.5 on none.[^zhouWebArenaRealisticWeb2024]
- **Observation bias.** The GPT-4 agent tends to latch onto the first related piece of information it encounters without verifying its relevance or accuracy.[^zhouWebArenaRealisticWeb2024]
- **Observation interpretation.** GPT-4 occasionally overlooks granular information such as previously entered input, and often neglects the previous action information given with the observation.[^zhouWebArenaRealisticWeb2024]

### fuzzy_match accuracy

- In a manual check of 40 examples, 39 are identical to human judgment.[^zhouWebArenaRealisticWeb2024]
- Among the 82 examples that require GPT-4 for evaluation, the answer of 49 (60%) is a date or time duration.[^zhouWebArenaRealisticWeb2024]

Accuracy (%) on judging whether dates and time durations in different formats are equivalent (Table 6):[^zhouWebArenaRealisticWeb2024]

| Dataset | gpt-4-0613 | gpt-4-1106-preview |
|---|---|---|
| Date (900 examples) | 100 | 100 |
| Time duration (900 examples) | 100 | 100 |

### Comparison with other benchmarks (Table 4)

| Benchmark | Dynamic Interaction? | Realistic Environment? | Diverse Human Tasks? | Functional Correctness? |
|---|---|---|---|---|
| [Mind2Web](../benchmarks/mind2web.md) | ✗ | ✓ | ✓ | ✗ |
| Form/QAWoB | ✗ | ✓ | ✓ | ✗ |
| [MiniWoB++](../benchmarks/miniwob.md) | ✓ | ✗ | ✗ | ✓ |
| [Webshop](../benchmarks/webshop.md) | ✓ | ✗ | ✗ | ✓ |
| ALFRED | ✓ | ✗ | ✗ | ✓ |
| VirtualHome | ✗ | ✗ | ✓ | ✗ |
| AndroidEnv | ✓ | ✓ | ✗ | ✗ |
| WebArena | ✓ | ✓ | ✓ | ✓ |

All rows: [^zhouWebArenaRealisticWeb2024]

## Limitations

- Human performance may differ with annotators of different demographics. Many tasks need domain-specific knowledge, for example what a git merge request is.[^zhouWebArenaRealisticWeb2024]
- Small differences in instruction design change agent behavior: the UA hint helps on unachievable tasks and hurts on achievable ones.[^zhouWebArenaRealisticWeb2024]
- `fuzzy_match` depends on a GPT-4 judge.[^zhouWebArenaRealisticWeb2024]
- Environment reset by restarting Docker containers has what the paper calls a non-negligible but small impact on evaluation time.[^zhouWebArenaRealisticWeb2024]
- The map covers only the northeast US region.[^zhouWebArenaRealisticWeb2024]
- The source gives three different template counts in different contexts: 241 templates in total, one task sampled from each of 170 templates for human performance, and 61 templates in the per-template success analysis. It does not explain the 170 figure.[^zhouWebArenaRealisticWeb2024]
- The paper has no dedicated limitations section.

## Related

- Benchmark introduced: [WebArena](../benchmarks/webarena.md)
- Benchmarks compared: [Mind2Web](../benchmarks/mind2web.md), [MiniWoB++](../benchmarks/miniwob.md), [Webshop](../benchmarks/webshop.md)
- Methods used by the baseline agents: [Chain-of-thought prompting](../methods/chain-of-thought.md), [In-context learning](../methods/in-context-learning.md), [Accessibility tree observation](../methods/accessibility-tree.md)
- Papers in this wiki cited by this paper: [Reflexion](shinnReflexionLanguageAgents2023.md) (cited for failure recovery and self-correction), [Voyager](wangVOYAGEROpenEndedEmbodied.md) (cited for memory components and skill reuse)[^zhouWebArenaRealisticWeb2024]

[^zhouWebArenaRealisticWeb2024]: Zhou et al. 2024
