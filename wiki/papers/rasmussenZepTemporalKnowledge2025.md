---
type: Paper
title: "Zep: A Temporal Knowledge Graph Architecture for Agent Memory"
description: Agent memory layer built on Graphiti, a temporally-aware knowledge graph engine with episodic, semantic entity, and community subgraphs and hybrid graph retrieval.
tags: [agent-memory, knowledge-graph, temporal-knowledge-graph, retrieval-augmented-generation, llm-agents, ai899]
collections: [ai899]
authors: [Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, Daniel Chalef]
arxiv: "2501.13956"
arxiv_version: 2501.13956v1
code: https://github.com/getzep/graphiti
sources:
  - id: rasmussenZepTemporalKnowledge2025
    resource: zotero://select/items/@rasmussenZepTemporalKnowledge2025
    title: "Zep: A Temporal Knowledge Graph Architecture for Agent Memory"
---

# Zep: A Temporal Knowledge Graph Architecture for Agent Memory

Text source: arXiv HTML, version `2501.13956v1`.

## Summary

[Zep](../methods/zep.md) is a memory layer service for AI agents, powered by [Graphiti](../methods/graphiti.md), a dynamic, temporally-aware knowledge graph engine.[^rasmussenZepTemporalKnowledge2025] The authors argue that existing [retrieval-augmented generation](../methods/retrieval-augmented-generation.md) approaches focus on largely static corpora, while agents need a continuously evolving memory built from conversations and business data.[^rasmussenZepTemporalKnowledge2025] Graphiti updates the knowledge graph with new information in a non-lossy manner and keeps a timeline of facts and relationships, including their periods of validity.[^rasmussenZepTemporalKnowledge2025]

On the [Deep Memory Retrieval](../benchmarks/deep-memory-retrieval.md) (DMR) benchmark, Zep scores 94.8% against 93.4% for [MemGPT](../methods/memgpt.md).[^rasmussenZepTemporalKnowledge2025] On [LongMemEval](../benchmarks/longmemeval.md), the paper reports accuracy improvements of up to 18.5% and a 90% reduction in response latency compared to baseline implementations.[^rasmussenZepTemporalKnowledge2025]

## Contributions

- Zep, a graph-based approach to LLM memory that incorporates semantic and episodic memory alongside entity and community summaries.[^rasmussenZepTemporalKnowledge2025]
- A bi-temporal model for LLM-based knowledge graph construction, which the authors describe as a novel advancement.[^rasmussenZepTemporalKnowledge2025]
- Evaluation on DMR and LongMemEval, including latency measurements for the retrieval mechanisms.[^rasmussenZepTemporalKnowledge2025]

## Method

### Graph structure

Memory is a [temporally-aware dynamic knowledge graph](../methods/temporal-knowledge-graph.md) $\mathcal{G}=(\mathcal{N},\mathcal{E},\phi)$ with three hierarchical tiers of subgraphs.[^rasmussenZepTemporalKnowledge2025]

| Subgraph | Nodes | Edges |
|---|---|---|
| Episode | Episodes hold raw input data (messages, text, or JSON) and serve as a non-lossy data store. | Episodic edges connect episodes to the semantic entities they reference. |
| Semantic entity | Entities extracted from episodes and resolved with existing graph entities. | Semantic edges are relationships (facts) between entities. |
| Community | Communities are clusters of strongly connected entities with high-level summarizations. | Community edges connect communities to their entity members. |

All rows: [^rasmussenZepTemporalKnowledge2025]

The split into episodic and semantic subgraphs draws from AriGraph, and the community nodes build on [GraphRAG](../methods/graphrag.md).[^rasmussenZepTemporalKnowledge2025]

### Episodes and the bi-temporal model

- Episodes are one of three types: message, text, or JSON. The paper focuses on the message type.[^rasmussenZepTemporalKnowledge2025]
- Each message has a reference timestamp $t_{\text{ref}}$, which lets Zep resolve relative or partial dates in the content, such as "next Thursday".[^rasmussenZepTemporalKnowledge2025]
- Timeline $T$ is the chronological ordering of events. Timeline $T'$ is the transactional order of Zep's data ingestion.[^rasmussenZepTemporalKnowledge2025]
- Episodes and their derived semantic edges keep bidirectional indices, so semantic artifacts can be traced to their sources and episodes can retrieve their entities and facts.[^rasmussenZepTemporalKnowledge2025]

### Entities

- Entity extraction processes the current message and the last $n$ messages, with $n=4$. The speaker is automatically extracted as an entity.[^rasmussenZepTemporalKnowledge2025]
- A reflection technique inspired by [Reflexion](../methods/reflexion.md) follows the initial extraction to minimize hallucinations and enhance coverage.[^rasmussenZepTemporalKnowledge2025]
- Each entity name is embedded into a 1024-dimensional vector space for cosine similarity search over existing entity nodes. A separate full-text search runs on entity names and summaries. An LLM then resolves the candidates with an entity resolution prompt, and a duplicate gets an updated name and summary.[^rasmussenZepTemporalKnowledge2025]
- Data is written to the graph with predefined Cypher queries instead of LLM-generated database queries.[^rasmussenZepTemporalKnowledge2025]

### Facts, temporal extraction, and edge invalidation

- The same fact can be extracted multiple times between different entities, which lets Graphiti model multi-entity facts through hyper-edges.[^rasmussenZepTemporalKnowledge2025]
- Edge deduplication uses a hybrid search constrained to edges between the same entity pair as the proposed new edge.[^rasmussenZepTemporalKnowledge2025]
- Four timestamps are stored on edges: $t'_{\text{created}}$ and $t'_{\text{expired}}$ on $T'$ record when a fact was created or invalidated in the system, and $t_{\text{valid}}$ and $t_{\text{invalid}}$ on $T$ record the range during which the fact held true.[^rasmussenZepTemporalKnowledge2025]
- An LLM compares new edges against semantically related existing edges. For temporally overlapping contradictions, the affected edge's $t_{\text{invalid}}$ is set to the $t_{\text{valid}}$ of the invalidating edge. Graphiti prioritizes new information.[^rasmussenZepTemporalKnowledge2025]

### Communities

- Community detection uses a [label propagation](../methods/label-propagation.md) algorithm instead of the Leiden algorithm used in GraphRAG, because label propagation has a straightforward dynamic extension.[^rasmussenZepTemporalKnowledge2025]
- A new entity node is assigned to the community held by the plurality of its neighbors, and the community summary is updated. Communities gradually diverge from a full label propagation run, so periodic community refreshes remain necessary.[^rasmussenZepTemporalKnowledge2025]
- Community summaries come from an iterative map-reduce-style summarization of member nodes. Community names containing key terms are embedded for cosine similarity search.[^rasmussenZepTemporalKnowledge2025]

### Retrieval

Retrieval is $f(\alpha)=\chi(\rho(\varphi(\alpha)))=\beta$, which maps a text query $\alpha$ to a text context $\beta$.[^rasmussenZepTemporalKnowledge2025]

| Step | What it does |
|---|---|
| Search ($\varphi$) | Returns lists of semantic edges, entity nodes, and community nodes. Three functions: cosine semantic similarity search, Okapi BM25 full-text search, and breadth-first search within $n$-hops. The first two use Neo4j's implementation of Lucene. |
| Reranker ($\rho$) | [Reciprocal Rank Fusion](../methods/reciprocal-rank-fusion.md), Maximal Marginal Relevance, an episode-mentions reranker (frequency of mentions within a conversation), a node distance reranker (graph distance from a centroid node), and cross-encoders. |
| Constructor ($\chi$) | Formats the results as text: the fact and $t_{\text{valid}}$, $t_{\text{invalid}}$ fields for edges, the name and summary for entities, and the summary for communities. |

All rows: [^rasmussenZepTemporalKnowledge2025]

The search field is the fact field for semantic edges, the entity name for entity nodes, and the community name for community nodes.[^rasmussenZepTemporalKnowledge2025] Breadth-first search can take nodes as seeds, for example recent episodes.[^rasmussenZepTemporalKnowledge2025] The authors note that their community search parallels the high-level key search in [LightRAG](../methods/lightrag.md).[^rasmussenZepTemporalKnowledge2025]

## Experiments & Results

### Setup

- Embedding and reranking: BGE-m3 models from BAAI.[^rasmussenZepTemporalKnowledge2025]
- Graph construction: gpt-4o-mini-2024-07-18. Chat agent: gpt-4o-mini-2024-07-18 and gpt-4o-2024-11-20. The DMR evaluation also uses gpt-4-turbo-2024-04-09 for comparability with MemGPT.[^rasmussenZepTemporalKnowledge2025]
- The experimental setup section states that the 20 most relevant edges (facts) and entity nodes (entity summaries) are retrieved, while the DMR section states that the top 10 most relevant nodes and edges are retrieved.[^rasmussenZepTemporalKnowledge2025]
- LongMemEval experiments ran between December 2024 and January 2025 from a consumer laptop in Boston, MA, connecting to Zep's service in AWS us-west-2. This added network latency to Zep's measurements that was not present in the baseline evaluations.[^rasmussenZepTemporalKnowledge2025]
- LongMemEval answers are judged by GPT-4o with the question-specific prompts of the benchmark. DMR answers are compared with the golden answers by an LLM judge.[^rasmussenZepTemporalKnowledge2025]

### Deep Memory Retrieval (Table 1)

DMR has 500 multi-session conversations, a subset of the [Multi-Session Chat](../datasets/multi-session-chat.md) dataset, each with 5 chat sessions of up to 12 messages per session and one question/answer pair. `†` marks results reported in the MemGPT paper.[^rasmussenZepTemporalKnowledge2025]

| Memory | Model | Score |
|---|---|---|
| Recursive Summarization† | gpt-4-turbo | 35.3% |
| Conversation Summaries | gpt-4-turbo | 78.6% |
| MemGPT† | gpt-4-turbo | 93.4% |
| Full-conversation | gpt-4-turbo | 94.4% |
| Zep | gpt-4-turbo | 94.8% |
| Conversation Summaries | gpt-4o-mini | 88.0% |
| Full-conversation | gpt-4o-mini | 98.0% |
| Zep | gpt-4o-mini | 98.2% |

All rows: [^rasmussenZepTemporalKnowledge2025]

- The authors could not reproduce MemGPT's results with gpt-4o-mini because of insufficient methodological details in the published work.[^rasmussenZepTemporalKnowledge2025]
- Each DMR conversation contains only 60 messages, which fits within current LLM context windows.[^rasmussenZepTemporalKnowledge2025]
- The authors criticize DMR: it uses only single-turn, fact-retrieval questions, many questions have ambiguous phrasing, and it poorly represents real-world enterprise use cases.[^rasmussenZepTemporalKnowledge2025]

### LongMemEval (Table 2)

The LongMemEval_s dataset has conversations averaging approximately 115,000 tokens and six question types.[^rasmussenZepTemporalKnowledge2025]

| Memory | Model | Score | Latency | Latency IQR | Avg Context Tokens |
|---|---|---|---|---|---|
| Full-context | gpt-4o-mini | 55.4% | 31.3 s | 8.76 s | 115k |
| Zep | gpt-4o-mini | 63.8% | 3.20 s | 1.31 s | 1.6k |
| Full-context | gpt-4o | 60.2% | 28.9 s | 6.01 s | 115k |
| Zep | gpt-4o | 71.2% | 2.58 s | 0.684 s | 1.6k |

All rows: [^rasmussenZepTemporalKnowledge2025]

The paper describes these as a 15.2% accuracy improvement over the baseline with gpt-4o-mini and an 18.5% improvement with gpt-4o, and as reducing response times by approximately 90%.[^rasmussenZepTemporalKnowledge2025]

### LongMemEval by question type (Table 3)

| Question Type | Model | Full-context | Zep | Delta |
|---|---|---|---|---|
| single-session-preference | gpt-4o-mini | 30.0% | 53.3% | 77.7%↑ |
| single-session-assistant | gpt-4o-mini | 81.8% | 75.0% | 9.06%↓ |
| temporal-reasoning | gpt-4o-mini | 36.5% | 54.1% | 48.2%↑ |
| multi-session | gpt-4o-mini | 40.6% | 47.4% | 16.7%↑ |
| knowledge-update | gpt-4o-mini | 76.9% | 74.4% | 3.36%↓ |
| single-session-user | gpt-4o-mini | 81.4% | 92.9% | 14.1%↑ |
| single-session-preference | gpt-4o | 20.0% | 56.7% | 184%↑ |
| single-session-assistant | gpt-4o | 94.6% | 80.4% | 17.7%↓ |
| temporal-reasoning | gpt-4o | 45.1% | 62.4% | 38.4%↑ |
| multi-session | gpt-4o | 44.3% | 57.9% | 30.7%↑ |
| knowledge-update | gpt-4o | 78.2% | 83.3% | 6.52%↑ |
| single-session-user | gpt-4o | 81.4% | 92.9% | 14.1%↑ |

All rows: [^rasmussenZepTemporalKnowledge2025]

## Limitations

- Performance drops on single-session-assistant questions, by 17.7% for gpt-4o and 9.06% for gpt-4o-mini. With gpt-4o-mini, knowledge-update also drops by 3.36%.[^rasmussenZepTemporalKnowledge2025]
- The authors state that additional development may be needed to improve less capable models' understanding of Zep's temporal data.[^rasmussenZepTemporalKnowledge2025]
- The DMR gains over MemGPT and over the full-conversation baselines are described by the authors as marginal.[^rasmussenZepTemporalKnowledge2025]
- MemGPT could not be evaluated on LongMemEval. The framework does not support direct ingestion of existing message histories, and the workaround of adding messages to the archival history did not produce successful question responses.[^rasmussenZepTemporalKnowledge2025]
- The experiments cover a subset of the search functionality. The connections between episodes and their derived semantic edges are not directly examined, and the experiments retrieve only edges (facts) and entity nodes.[^rasmussenZepTemporalKnowledge2025]
- No existing benchmark assesses Zep's ability to synthesize conversation history with structured business data, and its traditional RAG capabilities are not evaluated against established benchmarks.[^rasmussenZepTemporalKnowledge2025]
- Dynamic community updates drift from a full label propagation run and need periodic refreshes.[^rasmussenZepTemporalKnowledge2025]
- The paper has no dedicated limitations section.

## Related

- Proposed: [Zep](../methods/zep.md), [Graphiti](../methods/graphiti.md), [Temporal knowledge graph](../methods/temporal-knowledge-graph.md)
- Builds on: [Retrieval-augmented generation](../methods/retrieval-augmented-generation.md), [GraphRAG](../methods/graphrag.md), [Label propagation](../methods/label-propagation.md), [Reciprocal Rank Fusion](../methods/reciprocal-rank-fusion.md), [Reflexion](../methods/reflexion.md), [LightRAG](../methods/lightrag.md)
- Compared against: [MemGPT](../methods/memgpt.md)
- Benchmarks: [Deep Memory Retrieval](../benchmarks/deep-memory-retrieval.md), [LongMemEval](../benchmarks/longmemeval.md)
- Datasets: [Multi-Session Chat](../datasets/multi-session-chat.md)
- Papers in this wiki cited by this paper: [MemGPT](packerMemGPTLLMsOperating2024.md), [Reflexion](shinnReflexionLanguageAgents2023.md)

[^rasmussenZepTemporalKnowledge2025]: Rasmussen et al. 2025
