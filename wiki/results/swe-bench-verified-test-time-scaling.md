---
type: Result
title: Test-time scaling with a verifier raises SWE-bench Verified scores above single-attempt scores
description: R2E-Gym and SWE-RM both report large gains on SWE-bench Verified from selecting among many rollouts with a verifier.
tags: [swe-bench, test-time-scaling, software-engineering-agents]
sources:
  - id: jainR2EGymProceduralEnvironments2025
    resource: zotero://select/items/@jainR2EGymProceduralEnvironments2025
    title: "R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents"
  - id: shumSWERMExecutionfreeFeedback2025
    resource: zotero://select/items/@shumSWERMExecutionfreeFeedback2025
    title: "SWE-RM: Execution-Free Feedback for Software Engineering Agents"
---

# Test-time scaling with a verifier raises SWE-bench Verified scores above single-attempt scores

## Claim

Selecting one patch from many rollouts with a verifier raises SWE-bench Verified scores well above the single-attempt score of the same model.

## Numbers

| Model | Single attempt | With selection | Budget | Reported by |
|---|---|---|---|---|
| R2E-Gym 32B agent | 34.4 | 51.0 | Best@26, hybrid verifier | [R2E-Gym](../papers/jainR2EGymProceduralEnvironments2025.md)[^jainR2EGymProceduralEnvironments2025] |
| Qwen3-Coder-Max | 67.0% | 74.6% | RM@32, SWE-RM | [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md)[^shumSWERMExecutionfreeFeedback2025] |
| Qwen3-Coder-Flash | 51.6% | 62.0% | RM@32, SWE-RM | [SWE-RM](../papers/shumSWERMExecutionfreeFeedback2025.md)[^shumSWERMExecutionfreeFeedback2025] |

## Conditions

- R2E-Gym's hybrid verifier combines an execution-based and an execution-free verifier; each alone plateaus at 43.7% and 42.8%.[^jainR2EGymProceduralEnvironments2025]
- SWE-RM is an execution-free reward model.[^shumSWERMExecutionfreeFeedback2025]

## Related

- [SWE-bench Verified](../benchmarks/swe-bench-verified.md)
- [Test-time scaling](../methods/test-time-scaling.md), [Execution-free verifier](../methods/execution-free-verifier.md)
- [Which SWE-bench Verified scores are comparable?](../questions/swe-bench-verified-comparability.md)

[^jainR2EGymProceduralEnvironments2025]: Jain et al. 2025
[^shumSWERMExecutionfreeFeedback2025]: Shum et al. 2025
