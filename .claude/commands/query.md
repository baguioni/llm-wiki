---
description: Answer a question from the wiki, with attribution
argument-hint: "<question>"
---

Answer this question from the wiki. Follow every rule in `CLAUDE.md`.

Question: $ARGUMENTS

1. Read `wiki/index.md`, then the relevant pages. Go to `raw/papers/` only when the
   wiki lacks the detail. Do not answer from memory.
2. Answer with footnote attribution to citekeys (`[^citekey]`), with the footnote
   definitions at the end of the answer. Copy numbers exactly.
3. If the answer is a reusable synthesis (a comparison, analysis, or newly found
   connection), file it as an Analysis page in `wiki/analyses/`. Link it from the
   pages it draws on, update `wiki/analyses/index.md` and `wiki/index.md`, and append
   an **Analysis** entry to `wiki/log.md`. Tell me which page you filed.
4. If the answer exposes a gap (the sources do not answer the question, or they
   disagree), create an Open Question page in `wiki/questions/`, update the indexes,
   and log it.
