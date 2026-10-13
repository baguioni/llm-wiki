# Research Wiki Schema

This folder is an LLM-maintained research wiki. It follows the "LLM Wiki" pattern and
the Open Knowledge Format (OKF) v0.2. Follow every rule below in every session.

## Layout

```
CLAUDE.md                 # this schema
.claude/commands/         # ingest.md, query.md, lint.md
raw/                      # immutable sources
  library.bib             # Better BibTeX auto-export from Zotero
  papers/                 # extracted full text: <citekey>.md + <citekey>/ images (gitignored)
  tool/extract.py         # PDF -> markdown converter
  tool/requirements.txt
wiki/                     # the OKF bundle root
  index.md  log.md
  papers/  methods/  datasets/  benchmarks/  results/
  questions/  experiments/  analyses/
```

Python lives in `.venv/` at the root. Run the extractor as
`.venv/bin/python raw/tool/extract.py` (plain `python` is not on the PATH).

## Roles

- Claude is the only writer of `wiki/`. The human supplies sources and asks questions.
  Obsidian is a read-only viewer.
- `raw/` is read-only. The only permitted action there is running
  `raw/tool/extract.py`. Never hand-edit its output, `library.bib`, or anything else
  in `raw/`.
- Raw sources are the source of truth. Every factual claim and number in the wiki must
  come from a file in `raw/`, never from memory. If a fact is not in `raw/`, do not
  write it.

## Page types (OKF concepts)

Every non-reserved `.md` file in `wiki/` is a concept with YAML frontmatter.

| type           | folder        | purpose                                          |
|----------------|---------------|--------------------------------------------------|
| Paper          | papers/       | one page per paper, filename = citekey           |
| Method         | methods/      | a technique or algorithm across papers           |
| Dataset        | datasets/     | a dataset and how papers use it                  |
| Benchmark      | benchmarks/   | an eval setup and reported results / SOTA        |
| Result         | results/      | a specific quantitative finding worth tracking   |
| Open Question  | questions/    | unresolved questions, gaps, contradictions       |
| Experiment     | experiments/  | my own experiments                               |
| Analysis       | analyses/     | comparisons and syntheses filed back from /query |

Recommended body sections per type. Omit a section that has no sourced content. Do
not fill a section from memory.

- **Paper** (`papers/<citekey>.md`): Summary, Contributions, Method,
  Experiments & Results (tables with exact numbers), Limitations, Related (links).
- **Method** (`methods/`): Overview, How it works, Variants, Papers using it,
  Strengths & Limitations, Related.
- **Dataset** (`datasets/`): Overview, Composition (size, splits, format),
  Usage across papers, Known issues, Related.
- **Benchmark** (`benchmarks/`): Setup (task, metric, protocol), Results table (one row
  per paper, exact numbers), Current SOTA, Superseded claims, Caveats, Related.
- **Result** (`results/`): Claim (one sentence), Conditions (model, data, hardware,
  settings), Numbers, Comparisons, Related.
- **Open Question** (`questions/`): Question, Why it matters, Evidence so far,
  Conflicting claims, What would resolve it, Related.
- **Experiment** (`experiments/`): Goal, Setup, Procedure, Results, Interpretation,
  Next steps, Related. The human supplies the data; record where it came from.
- **Analysis** (`analyses/`): Question, Answer, Evidence (tables, comparisons),
  Caveats, Related.

### Frontmatter (OKF §4.1)

```yaml
---
type: Method                       # REQUIRED, one of the types above
title: Speculative Decoding
description: One sentence summary, reused in index.md.
tags: [inference, decoding]
sources:
  - id: leviathan2023fast          # Better BibTeX citekey
    resource: zotero://select/items/@leviathan2023fast
    title: Fast Inference from Transformers via Speculative Decoding
---
```

- `type` is required and must be one of the eight types above.
- `sources[].id` is always the citekey. `resource` is the Zotero URI
  (`zotero://select/items/@<citekey>`), or the DOI or arXiv URL if the paper is not in
  Zotero.
- Unknown extra keys are allowed. Preserve them when editing a page.
- Paper pages carry the Zotero collections of the paper. Copy the `collections` list
  from the frontmatter of `raw/papers/<citekey>.md` to a `collections` key on the
  Paper page, and add each collection to `tags` in lowercase-kebab-case
  (`speculative drafter` becomes `speculative-drafter`).

## Attribution (OKF §5.1)

- Attribute every claim with a footnote whose label is a `sources[].id`:
  `Acceptance rate improves with draft size.[^leviathan2023fast]`
  Put the footnote definition at the bottom of the page:
  `[^leviathan2023fast]: Leviathan et al. 2023`
- Every footnote label must match a `sources` entry on the same page. Every `sources`
  entry should be cited at least once.
- Copy numbers exactly from `raw/papers/<citekey>.md`. Never round or estimate them.
  Keep the units and the precision that the source uses.

## Links (OKF §6)

- Use standard markdown links, not `[[wikilinks]]`.
- Use relative paths (`../methods/speculative-decoding.md`). Do not use `/`-absolute
  paths, because the Obsidian vault root differs from the bundle root (`wiki/`).
- Filenames are lowercase-kebab-case. Paper pages use the citekey as the filename.
- Broken links are allowed. They mark knowledge not yet written, and lint reports them.

## Contradictions

- Never silently overwrite a claim. When a new source conflicts with a page:
  1. Keep both attributed claims.
  2. Add a `# Contradictions` section to the page that explains the conflict.
  3. Create or update an Open Question page that links to both.
- When a new result beats a recorded SOTA, update the Benchmark page and mark the old
  claim as superseded. Keep the old claim and its footnote.

## index.md (OKF §8)

- `wiki/index.md` and an `index.md` in each subfolder list every concept, grouped
  under headings, one line each:
  `* [Title](relative-path.md) - description from frontmatter`
- Title and description must equal the page's frontmatter `title` and `description`.
- Index files have no frontmatter, except `okf_version: "0.2"` in `wiki/index.md`.
- Update the indexes on every change.
- To search, read `wiki/index.md` first, then drill into pages.
- When the wiki passes about 300 pages, suggest adding qmd as a search tool.

## log.md (OKF §9)

- `wiki/log.md` holds the history of changes, newest first:

```
## 2026-10-13
* **Ingest**: [Fast Inference ...](papers/leviathan2023fast.md); updated 4 pages.
* **Analysis**: Filed [Draft model comparison](analyses/draft-model-comparison.md).
* **Lint**: Fixed 3 broken links; 2 issues reported.
```

- Date headings use `YYYY-MM-DD`. Add new entries under today's heading, and create
  the heading at the top if it does not exist.
- Each entry starts with a bold verb: Ingest, Creation, Update, Analysis, Lint, or
  Deprecation.

## Reserved names and conformance (OKF §3.1, §11)

- `index.md` and `log.md` are reserved and are never concept pages.
- Every other `.md` file in `wiki/` must have parseable frontmatter with a non-empty
  `type`.

## Commands

The full procedures are in `.claude/commands/`.

- `/ingest [citekey ...]` ([ingest.md](.claude/commands/ingest.md)): run the
  extractor, read each paper in full, write the Paper page, create or update the
  related Method, Dataset, Benchmark, and Result pages, apply the contradiction and
  SOTA rules, then update the indexes and the log. With no arguments it ingests every
  new bib entry.
- `/query <question>` ([query.md](.claude/commands/query.md)): answer from the wiki
  with footnote attribution. File reusable syntheses as Analysis pages, and file gaps
  as Open Question pages.
- `/lint` ([lint.md](.claude/commands/lint.md)): check conformance, links,
  attribution, index sync, contradictions, superseded SOTA, missing concept pages, and
  bib entries not yet ingested. Fix mechanical issues, report the rest, and log it.

## Extractor reference

```
.venv/bin/python raw/tool/extract.py                       # all bib entries not yet extracted
.venv/bin/python raw/tool/extract.py <citekey> [...]       # specific papers
.venv/bin/python raw/tool/extract.py --force <citekey>     # re-extract
.venv/bin/python raw/tool/extract.py --pdf <path> --citekey <key>   # PDF not in the bib
.venv/bin/python raw/tool/extract.py --backend arxiv|marker|pymupdf4llm|auto
```

`auto` (default) tries the backends in this order and uses the first that succeeds:

1. `arxiv`: converts the arXiv HTML rendering (built from the authors' LaTeX). Needs
   an arXiv id in the bib entry (`eprint`, or a `10.48550/arXiv.*` DOI) and network
   access. Fast, and equations are the original LaTeX.
2. `marker`: marker-pdf on the Zotero PDF.
3. `pymupdf4llm`: text-layer extraction from the Zotero PDF.

The script exits non-zero if any paper fails.

The `extracted.by` key in `raw/papers/<citekey>.md` records the backend. For the
`arxiv` backend, the text comes from the arXiv version in `arxiv_version`, which can
differ from the PDF in Zotero (for example, the conference version). When a Paper
page is built from arXiv HTML, state the `arxiv_version` in its Summary. If the human
reports a number that differs from the published version, re-extract with
`--force --backend marker` and treat the difference as a contradiction.
