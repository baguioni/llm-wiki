---
type: Benchmark
title: WebShop
description: Web-based problem-solving benchmark in which an agent navigates an e-commerce website to locate and purchase products given requests from clients.
tags: [web-agents, benchmark, e-commerce, llm-agents]
sources:
  - id: shinnReflexionLanguageAgents2023
    resource: zotero://select/items/@shinnReflexionLanguageAgents2023
    title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
  - id: zhouWebArenaRealisticWeb2024
    resource: zotero://select/items/@zhouWebArenaRealisticWeb2024
    title: "WebArena: A Realistic Web Environment for Building Autonomous Agents"
---

# WebShop

## Setup

- **Task.** WebShop is a web-based problem-solving benchmark that tests agents to navigate an e-commerce website to locate and purchase products given requests from clients.[^shinnReflexionLanguageAgents2023]
- The wiki's papers do not state the metric, the number of tasks, or the evaluation protocol of the benchmark itself.

## Results

No paper in the wiki states a numeric WebShop score in its text.

| System | Score | Setting / budget | Reported by |
|---|---|---|---|
| [ReAct](../methods/react.md) + [Reflexion](../methods/reflexion.md) | not stated (figure only) | two-shot agent, 100 environments, runs terminated after four trials | [Shinn et al. 2023](../papers/shinnReflexionLanguageAgents2023.md)[^shinnReflexionLanguageAgents2023] |
| ReAct | not stated (figure only) | 100 customer shopping requests | [Shinn et al. 2023](../papers/shinnReflexionLanguageAgents2023.md)[^shinnReflexionLanguageAgents2023] |

- ReAct + Reflexion fails to significantly outperform ReAct.[^shinnReflexionLanguageAgents2023]
- The runs were terminated after only four trials because the agent did not show signs of improvement and did not generate helpful, intuitive self-reflections after failed attempts.[^shinnReflexionLanguageAgents2023]
- The authors conclude that Reflexion is unable to solve tasks that require a significant amount of diversity and exploration.[^shinnReflexionLanguageAgents2023]

## Caveats

- The Reflexion result is a negative result in an appendix on limitations, shown as a figure without numbers in the text.[^shinnReflexionLanguageAgents2023]
- Shinn et al. contrast WebShop with two other tasks. In AlfWorld, the agent can explore adequately because the permissible actions can be seen in the observations. In HotPotQA, the agent faces a similar search query task but is more successful, because the search space for Wikipedia articles is more diverse and requires less precise search queries.[^shinnReflexionLanguageAgents2023]
- The WebArena paper's benchmark comparison marks Webshop as having dynamic interaction and functional-correctness evaluation, and as lacking a realistic environment and diverse human tasks.[^zhouWebArenaRealisticWeb2024]

## Papers using it

- [Reflexion](../papers/shinnReflexionLanguageAgents2023.md): the limitation experiment above.[^shinnReflexionLanguageAgents2023]
- [WebArena](../papers/zhouWebArenaRealisticWeb2024.md): compares against Webshop in its benchmark table, and its shopping website obtains data resources from actual online sites, such as the data included in the Webshop data dump.[^zhouWebArenaRealisticWeb2024]

## Related

- Benchmarks: [WebArena](webarena.md)
- Datasets contrasted by Shinn et al.: [ALFWorld](../datasets/alfworld.md), [HotpotQA](../datasets/hotpotqa.md)
- Methods: [ReAct](../methods/react.md), [Reflexion](../methods/reflexion.md)

[^shinnReflexionLanguageAgents2023]: Shinn et al. 2023
[^zhouWebArenaRealisticWeb2024]: Zhou et al. 2024
