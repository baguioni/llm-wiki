---
description: Check the wiki for conformance, link, attribution, and consistency problems
---

Lint the wiki. Follow every rule in `CLAUDE.md`. Extra instructions, if any: $ARGUMENTS

Check for and report:

- conformance problems (missing or unparseable frontmatter, missing `type`, a `type`
  not in the schema, reserved names `index.md` / `log.md` misused)
- broken links and orphan pages (no inbound links)
- footnotes with no matching `sources` entry, and `sources` entries never cited
- index files out of sync with the pages, or descriptions that differ from the
  frontmatter
- contradictions between pages that are not yet flagged
- superseded SOTA claims
- concepts mentioned on two or more pages that have no page of their own
- citekeys in `raw/library.bib` that have not been ingested (no
  `wiki/papers/<citekey>.md`)

Then:

1. Fix mechanical issues automatically: index sync, footnote mismatches, and flagging
   contradictions (add the `# Contradictions` section and the Open Question page).
   Take every fact from `raw/`, never from memory.
2. Report issues that need judgment. Do not guess a fix for them.
3. Append a **Lint** entry to `wiki/log.md` with the counts of fixed and reported
   issues.
4. Suggest new sources or questions to investigate.
5. If the wiki has more than about 300 pages, suggest adding qmd as a search tool.
