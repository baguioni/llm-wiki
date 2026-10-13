# Benchmarks

* [Berkeley Function Calling Leaderboard (BFCL)](bfcl.md) - Function-calling benchmark for LLMs, reported in the wiki as BFCL v2 and BFCLv3, and also used as a ReAct agent workload for serving systems.
* [Deep Memory Retrieval (DMR)](deep-memory-retrieval.md) - Conversational memory task built on Multi-Session Chat, in which an agent answers a question that refers back to prior chat sessions and is scored by an LLM judge.
* [Humanity's Last Exam (HLE)](hle.md) - Expert-written question benchmark that the wiki's papers use to test deep academic and logical reasoning of web agents and as a tool-heavy serving workload.
* [Online-Mind2Web](online-mind2web.md) - Web navigation benchmark that evaluates agents on live websites with an LLM-as-judge for task success, also called Mind2Web-Online.
* [Spec-Bench](spec-bench.md) - Benchmark and codebase for comparing speculative decoding methods by speedup over vanilla decoding across 13 task categories.
* [SWE-bench](swe-bench.md) - Benchmark of 2,294 GitHub-issue resolution tasks from 12 Python repositories, scored by the share of issues whose tests pass after the generated patch is applied.
* [SWE-bench Lite](swe-bench-lite.md) - Canonical 300-instance subset of the SWE-bench test set focused on self-contained functional bug fixes, used for ablations, small-model comparisons, and as a serving workload.
* [SWE-bench Verified](swe-bench-verified.md) - Human-verified 500-problem subset of SWE-bench for resolving real GitHub issues, reported in this wiki at rollout budgets from greedy pass@1 to reranking over 500 patches.
* [Terminal-Bench](terminal-bench.md) - Benchmark of realistic, human-verified command-line tasks, used in this wiki as an out-of-domain check for RL-trained coding agents and as an agentic serving workload.
* [WebArena](webarena.md) - Self-hosted web environment with 812 long-horizon tasks that scores web agents by the functional correctness of task completion.
* [WebArena-Lite](webarena-lite.md) - Human-verified subset of WebArena with 165 test cases, used to compare trained open-model web agents and proprietary LLM agents by task success rate.
* [WebShop](webshop.md) - Web-based problem-solving benchmark in which an agent navigates an e-commerce website to locate and purchase products given requests from clients.
