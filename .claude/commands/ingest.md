---
description: Ingest papers from raw/library.bib into the wiki
argument-hint: "[citekey ...]"
---

Ingest papers into the wiki. Follow every rule in `CLAUDE.md`.

Input: `$ARGUMENTS` (zero or more citekeys; empty means all new papers).

1. Run `.venv/bin/python raw/tool/extract.py $ARGUMENTS`. With no arguments it extracts
   every new bib entry. Read the per-paper result lines. Report each failed paper and
   continue with the rest. Never edit the extractor output.
   With no arguments, the papers to ingest are every citekey that has
   `raw/papers/<citekey>.md` but no `wiki/papers/<citekey>.md`.
2. For each paper, read `raw/papers/<citekey>.md` in full. Look at the images in
   `raw/papers/<citekey>/` when figures carry key results.
3. Create `wiki/papers/<citekey>.md` (type `Paper`) with these sections: Summary,
   Contributions, Method, Experiments & Results (with tables and exact numbers),
   Limitations, and Related (links). Fully attribute it with footnotes. Take the
   title, DOI, arXiv id, and `collections` from the frontmatter of
   `raw/papers/<citekey>.md`. Add each collection to `tags` in lowercase-kebab-case.
4. Create or update every relevant Method, Dataset, Benchmark, and Result page. Add
   this paper to their `sources` and cite it in the body. Read `wiki/index.md` first
   to find existing pages, so that you update a page instead of duplicating it.
5. Apply the contradiction and SOTA rules from `CLAUDE.md`:
   - Conflict with an existing claim: keep both, add a `# Contradictions` section,
     and create or update an Open Question page that links to both.
   - New result beats a recorded SOTA: update the Benchmark page and mark the old
     claim as superseded, with its footnote kept.
6. Update the affected index files (`wiki/index.md` and each subfolder `index.md`),
   append an **Ingest** entry to `wiki/log.md`, and report which pages were created
   or changed.
