#!/usr/bin/env python3
"""Convert Zotero PDFs to markdown (with images) for the research wiki.

Usage:
    python raw/tool/extract.py                      # every bib entry not yet extracted
    python raw/tool/extract.py <citekey> [...]      # specific papers
    python raw/tool/extract.py --force <citekey>    # re-extract
    python raw/tool/extract.py --pdf <path> --citekey <key>   # PDF not in the bib
    python raw/tool/extract.py --backend arxiv|marker|pymupdf4llm|auto

Backends, in `auto` order:
    arxiv        arXiv HTML (built from the authors' LaTeX); needs an arXiv id and network
    marker       marker-pdf on the Zotero PDF
    pymupdf4llm  text-layer extraction from the Zotero PDF

Output: raw/papers/<citekey>.md plus images in raw/papers/<citekey>/.
The output is deterministic tool output. Never edit it by hand.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Callable
from urllib.parse import urljoin, urlparse

RAW_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BIB = RAW_DIR / "library.bib"
DEFAULT_OUT = RAW_DIR / "papers"

BACKENDS = ("arxiv", "marker", "pymupdf4llm")
PACKAGES = {"marker": "marker-pdf", "pymupdf4llm": "pymupdf4llm"}
BACKEND_LABELS = {"arxiv": "arxiv-html"}
ARXIV_HTML_VERSION = "1.0"  # version of the HTML -> markdown conversion in this file
ARXIV_ID_RE = re.compile(r"^(\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?$")
ARXIV_DOI_RE = re.compile(r"^10\.48550/arxiv\.(.+)$", re.IGNORECASE)
USER_AGENT = "research-wiki-extract/1.0 (personal research wiki)"
REQUEST_DELAY = 0.3  # seconds between arXiv requests
ARXIV_API_DELAY = 3.0  # arXiv asks for at most one API request every 3 seconds
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}

IMAGE_LINK_RE = re.compile(r"!\[([^\]]*)\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_IMG_RE = re.compile(r"(<img\b[^>]*?\bsrc=[\"'])([^\"']+)([\"'])", re.IGNORECASE)
CITEKEY_RE = re.compile(r"^[^\s/\\:*?\"<>|]+$")


class ExtractError(Exception):
    pass


# --------------------------------------------------------------------------- bib


def load_bib(bib_path: Path) -> dict[str, dict]:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser

    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    with bib_path.open(encoding="utf-8") as handle:
        database = bibtexparser.load(handle, parser=parser)
    return {entry["ID"]: entry for entry in database.entries}


def _split_unescaped(text: str, separator: str) -> list[str]:
    return re.split(r"(?<!\\)" + re.escape(separator), text)


def _unescape(text: str) -> str:
    return re.sub(r"\\([\\:;{}])", r"\1", text).strip()


def pdf_candidates(file_field: str) -> list[str]:
    """Return possible PDF paths from a bib `file` field, in order.

    Handles the Better BibTeX form (`/abs/path.pdf`) and the Zotero form
    (`Name:/abs/path.pdf:application/pdf`), with attachments separated by `;`.
    """
    candidates: list[str] = []
    for attachment in _split_unescaped(file_field, ";"):
        attachment = attachment.strip()
        if not attachment:
            continue
        whole = _unescape(attachment)
        if whole.lower().endswith(".pdf"):
            candidates.append(whole)
        parts = _split_unescaped(attachment, ":")
        for index, part in enumerate(parts):
            path = _unescape(part)
            if path.lower().endswith(".pdf"):
                candidates.append(path)
            # Windows drive letter split off by the ":" separator (C:/path.pdf).
            if len(path) == 1 and path.isalpha() and index + 1 < len(parts):
                joined = path + ":" + _unescape(parts[index + 1])
                if joined.lower().endswith(".pdf"):
                    candidates.append(joined)
    return list(dict.fromkeys(candidates))


def find_pdf(entry: dict, bib_path: Path) -> Path:
    file_field = entry.get("file", "")
    if not file_field.strip():
        raise ExtractError("bib entry has no `file` field")
    candidates = pdf_candidates(file_field)
    for candidate in candidates:
        path = Path(candidate).expanduser()
        if not path.is_absolute():
            path = bib_path.parent / path
        if path.is_file():
            return path
    if not candidates:
        raise ExtractError("no .pdf attachment in `file` field")
    raise ExtractError(f"PDF not found on disk: {candidates[0]}")


def clean_bib_value(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    while "{" in value or "}" in value:
        stripped = re.sub(r"\{([^{}]*)\}", r"\1", value)
        if stripped == value:
            stripped = value.replace("{", "").replace("}", "")
        value = stripped
    return value.strip()


# ---------------------------------------------------------------------- backends


def backend_version(backend: str) -> str:
    if backend == "arxiv":
        return ARXIV_HTML_VERSION
    try:
        return metadata.version(PACKAGES[backend])
    except metadata.PackageNotFoundError:
        return "unknown"


PdfGetter = Callable[[], Path]

_marker_converter = None


def convert_marker(get_pdf: PdfGetter, work_dir: Path, entry: dict) -> tuple[str, dict]:
    """marker-pdf 2.x API: PdfConverter + text_from_rendered."""
    global _marker_converter
    pdf = get_pdf()
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    if _marker_converter is None:
        from marker.settings import settings

        settings.OUTPUT_IMAGE_FORMAT = "PNG"  # lossless figures, default is JPEG
        # Page headers and footers are dropped by marker's markdown renderer.
        config = {"output_format": "markdown", "paginate_output": False}
        _marker_converter = PdfConverter(artifact_dict=create_model_dict(), config=config)
    rendered = _marker_converter(str(pdf))
    text, _, images = text_from_rendered(rendered)
    for name, image in (images or {}).items():
        target = work_dir / Path(name).name
        image.save(target)
    return text, {}


def convert_pymupdf4llm(get_pdf: PdfGetter, work_dir: Path, entry: dict) -> tuple[str, dict]:
    import pymupdf4llm

    text = pymupdf4llm.to_markdown(
        str(get_pdf()),
        write_images=True,
        image_path=str(work_dir),
        image_format="png",
        header=False,
        footer=False,
        show_progress=False,
    )
    return text, {}


# ------------------------------------------------------------------ arxiv backend


def _title_words(title: str) -> list[str]:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).split()


def arxiv_title_search(title: str) -> str:
    """Find an arXiv id by title. Accepts only an exact match of the title words."""
    import xml.etree.ElementTree as ElementTree
    from urllib.parse import urlencode

    words = _title_words(title)
    if len(words) < 3:
        raise ExtractError("no arXiv id in bib entry, and the title is too short to search")
    query = urlencode({"search_query": 'ti:"' + " ".join(words) + '"', "max_results": 10})
    time.sleep(ARXIV_API_DELAY)
    raw, _ = http_get(f"https://export.arxiv.org/api/query?{query}")
    atom = {"a": "http://www.w3.org/2005/Atom"}
    for found in ElementTree.fromstring(raw).findall("a:entry", atom):
        if _title_words(found.findtext("a:title", "", atom)) == words:
            identifier = found.findtext("a:id", "", atom).rsplit("/abs/", 1)[-1]
            identifier = re.sub(r"v\d+$", "", identifier)
            if ARXIV_ID_RE.match(identifier):
                return identifier
    raise ExtractError("no arXiv id in bib entry, and no exact title match on arXiv")


def arxiv_id(entry: dict) -> str:
    eprint = clean_bib_value(entry.get("eprint", ""))
    prefix = clean_bib_value(entry.get("archiveprefix", "") or entry.get("eprinttype", ""))
    if eprint and prefix.lower() in ("", "arxiv") and ARXIV_ID_RE.match(eprint):
        return eprint
    match = ARXIV_DOI_RE.match(clean_bib_value(entry.get("doi", "")))
    if match and ARXIV_ID_RE.match(match.group(1)):
        return match.group(1)
    raise ExtractError("no arXiv id in bib entry")


def http_get(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    time.sleep(REQUEST_DELAY)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read(), response.geturl()
    except urllib.error.HTTPError as error:
        raise ExtractError(f"HTTP {error.code} for {url}") from error
    except urllib.error.URLError as error:
        raise ExtractError(f"cannot reach {url}: {error.reason}") from error


def _latex(math) -> str:
    text = math.get("alttext") or math.get_text(" ", strip=True)
    text = re.sub(r"%\s*\n\s*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def convert_arxiv(get_pdf: PdfGetter, work_dir: Path, entry: dict) -> tuple[str, dict]:
    """Convert the arXiv HTML rendering (LaTeXML) of a paper to markdown."""
    from bs4 import BeautifulSoup
    from markdownify import MarkdownConverter

    found_by_title = False
    try:
        identifier = arxiv_id(entry)
    except ExtractError:
        identifier = arxiv_title_search(clean_bib_value(entry.get("title", "")))
        found_by_title = True
    raw, page_url = http_get(f"https://arxiv.org/html/{identifier}")
    html = raw.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one("article.ltx_document")
    if root is None:
        raise ExtractError(f"arXiv has no HTML version of {identifier}")
    if root.select_one(".ltx_bibliography") is None:
        # arXiv's LaTeX conversion sometimes stops early and drops the rest of the paper.
        raise ExtractError(f"arXiv HTML of {identifier} is truncated (no reference list)")

    base_id = re.sub(r"v\d+$", "", identifier)
    versions = re.findall(re.escape(base_id) + r"(v\d+)", html)
    versioned = base_id + max(versions, key=lambda v: versions.count(v)) if versions else identifier

    stash: list[str] = []

    def hold(value: str) -> str:
        stash.append(value)
        return f"@@HOLD{len(stash) - 1}@@"

    def paragraph(value: str):
        tag = soup.new_tag("p")
        tag.string = hold(value)
        return tag

    # Page furniture and elements with no content value.
    for element in root.select(
        "nav, script, style, button, .ltx_pagination, .ltx_page_footer, .ltx_page_header, "
        ".ltx_listing_data, .ltx_ERROR, .sr-only"
    ):
        element.decompose()

    # LaTeXML renders some tables with <span> elements. Turn them into real tables.
    span_tables = {
        "ltx_tabular": "table",
        "ltx_thead": "thead",
        "ltx_tbody": "tbody",
        "ltx_tfoot": "tfoot",
        "ltx_tr": "tr",
        "ltx_th": "th",
        "ltx_td": "td",
    }
    for span in root.find_all("span"):
        classes = span.get("class") or []
        for css_class, tag_name in span_tables.items():
            if css_class in classes:
                span.name = tag_name
                break

    # Numbered display equations: one $$ block per row, with the equation number.
    for table in root.select("table.ltx_eqn_table"):
        if table.find_parent("table", class_="ltx_eqn_table") or table.parent is None:
            continue
        blocks = []
        for row in table.find_all("tr"):
            maths = [_latex(math) for math in row.find_all("math")]
            maths = [math for math in maths if math]
            if not maths:
                continue
            tag = row.select_one(".ltx_tag_equation")
            number = tag.get_text(strip=True).strip("()") if tag else ""
            body = " ".join(maths) + (f" \\tag{{{number}}}" if number else "")
            blocks.append(f"$$\n{body}\n$$")
        if blocks:
            table.replace_with(paragraph("\n\n".join(blocks)))
        else:
            table.decompose()

    for math in root.find_all("math"):
        latex = _latex(math)
        if math.get("display") == "block":
            math.replace_with(paragraph(f"$$\n{latex}\n$$"))
        else:
            math.replace_with(hold(f"${latex}$"))

    # Footnotes are inline in LaTeXML output.
    for note in root.select(".ltx_note"):
        content = note.select_one(".ltx_note_content")
        if content is None:
            continue
        for mark in content.select(".ltx_note_mark, .ltx_tag_note"):
            mark.decompose()
        note.replace_with(f" (footnote: {content.get_text(' ', strip=True)})")

    for link in root.select('a[href^="#"]'):
        link.unwrap()
    for bold in root.select("span.ltx_font_bold"):
        bold.name = "b"
    for caption in root.find_all("figcaption"):
        caption.name = "p"

    # Figures: download raster images, save inline SVG drawings.
    for embedded in root.find_all(["object", "embed"]):
        source = embedded.get("data") or embedded.get("src")
        if source:
            embedded.replace_with(soup.new_tag("img", src=source))
        else:
            embedded.decompose()
    counter = 0
    for image in root.find_all("img"):
        source = image.get("src", "")
        if not source or source.startswith("data:"):
            image.decompose()
            continue
        counter += 1
        suffix = Path(urlparse(source).path).suffix.lower()
        name = f"img{counter}{suffix if suffix in IMAGE_SUFFIXES else '.png'}"
        try:
            data, _ = http_get(urljoin(page_url, source))
        except ExtractError:
            image.replace_with(f"[image not available: {source}]")
            continue
        (work_dir / name).write_bytes(data)
        image.attrs = {"src": name, "alt": ""}
    for drawing in root.find_all("svg"):
        counter += 1
        name = f"img{counter}.svg"
        if not drawing.get("xmlns"):
            drawing["xmlns"] = "http://www.w3.org/2000/svg"
        (work_dir / name).write_text(str(drawing), encoding="utf-8")
        picture = soup.new_tag("img", src=name, alt="")
        drawing.replace_with(picture)

    # Tables with row spans do not fit pipe tables. Keep them as plain HTML tables.
    for table in root.find_all("table"):
        if table.parent is None or table.find_parent("table"):
            continue
        if not table.find(lambda tag: tag.name in ("td", "th") and tag.get("rowspan", "1") != "1"):
            continue
        for tag in table.find_all(True):
            if tag.name in ("table", "thead", "tbody", "tfoot", "tr", "td", "th", "b", "br"):
                tag.attrs = {k: v for k, v in tag.attrs.items() if k in ("colspan", "rowspan")}
            else:
                tag.unwrap()
        table.attrs = {}
        table.replace_with(paragraph(re.sub(r"\s*\n\s*", " ", str(table))))

    text = MarkdownConverter(heading_style="ATX", bullets="-").convert_soup(root)
    for _ in range(3):  # held values can contain other held values
        text = re.sub(r"@@HOLD(\d+)@@", lambda match: stash[int(match.group(1))], text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text.strip()) < 2000:
        raise ExtractError(f"arXiv HTML of {identifier} has almost no text")
    extra = {}
    if found_by_title:
        # The bib entry has no arXiv id. The id comes from an exact title match.
        extra["arxiv"] = json.dumps(base_id)
        extra["arxiv_id_from"] = "title-search"
    extra["arxiv_version"] = versioned
    extra["source_html"] = f"https://arxiv.org/html/{versioned}"
    return text, extra


CONVERTERS = {"arxiv": convert_arxiv, "marker": convert_marker, "pymupdf4llm": convert_pymupdf4llm}


# ------------------------------------------------------------------------ output


def relink_images(text: str, work_dir: Path, image_dir: Path, citekey: str) -> tuple[str, int]:
    """Move images to image_dir as fig_N.<ext> and rewrite links to <citekey>/fig_N.<ext>."""
    available = {path.name: path for path in work_dir.iterdir() if path.is_file()}
    renamed: dict[str, str] = {}

    def new_name(target: str) -> str | None:
        name = Path(target.replace("%20", " ")).name
        if name not in available:
            return None
        if name not in renamed:
            suffix = Path(name).suffix.lower() or ".png"
            renamed[name] = f"fig_{len(renamed) + 1}{suffix}"
        return renamed[name]

    def replace_markdown(match: re.Match) -> str:
        name = new_name(match.group(2))
        if name is None:
            return match.group(0)
        return f"![{match.group(1)}]({citekey}/{name})"

    def replace_html(match: re.Match) -> str:
        name = new_name(match.group(2))
        if name is None:
            return match.group(0)
        return f"{match.group(1)}{citekey}/{name}{match.group(3)}"

    text = IMAGE_LINK_RE.sub(replace_markdown, text)
    text = HTML_IMG_RE.sub(replace_html, text)

    if renamed:
        image_dir.mkdir(parents=True, exist_ok=True)
        for old, new in renamed.items():
            shutil.move(str(available[old]), str(image_dir / new))
    return text, len(renamed)


def frontmatter(
    citekey: str, entry: dict, backend: str, in_bib: bool, pdf: Path | None, extra: dict
) -> str:
    title = clean_bib_value(entry.get("title", "")) or citekey
    doi = clean_bib_value(entry.get("doi", ""))
    arxiv = clean_bib_value(entry.get("eprint", ""))
    if in_bib or pdf is None:
        source = f"zotero://select/items/@{citekey}"
    else:
        source = pdf.resolve().as_uri()
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        "---",
        "type: Paper Text",
        f"citekey: {citekey}",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"source_pdf: {source}",
    ]
    if doi:
        lines.append(f"doi: {doi}")
    if arxiv:
        lines.append(f"arxiv: {json.dumps(arxiv)}")
    collections = [name.strip() for name in entry.get("groups", "").split(",") if name.strip()]
    if collections:
        lines.append(f"collections: {json.dumps(collections, ensure_ascii=False)}")
    for key, value in extra.items():
        lines.append(f"{key}: {value}")
    label = BACKEND_LABELS.get(backend, backend)
    lines.append(f"extracted: {{ by: process:{label}/{backend_version(backend)}, at: {stamp} }}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def extract_one(
    citekey: str,
    get_pdf: PdfGetter,
    entry: dict,
    in_bib: bool,
    backends: list[str],
    out_dir: Path,
) -> tuple[str, int]:
    errors = []
    for backend in backends:
        with tempfile.TemporaryDirectory(prefix="extract_") as tmp:
            work_dir = Path(tmp)
            try:
                text, extra = CONVERTERS[backend](get_pdf, work_dir, entry)
                if not text or not text.strip():
                    raise ExtractError("backend returned empty text")
            except Exception as error:  # noqa: BLE001 - try the next backend
                errors.append(f"{backend}: {type(error).__name__}: {error}")
                continue

            image_dir = out_dir / citekey
            if image_dir.exists():
                shutil.rmtree(image_dir)
            text, image_count = relink_images(text, work_dir, image_dir, citekey)
            body = text.strip() + "\n"
            target = out_dir / f"{citekey}.md"
            partial = target.with_suffix(".md.partial")
            try:
                pdf = get_pdf()
            except ExtractError:
                pdf = None
            partial.write_text(
                frontmatter(citekey, entry, backend, in_bib, pdf, extra) + body,
                encoding="utf-8",
            )
            partial.replace(target)
            return backend, image_count
    raise ExtractError("; ".join(errors))


# --------------------------------------------------------------------------- cli


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Zotero PDFs to markdown with images.",
    )
    parser.add_argument("citekeys", nargs="*", help="citekeys to convert (default: all new)")
    parser.add_argument("--force", action="store_true", help="re-extract existing papers")
    parser.add_argument("--pdf", type=Path, help="convert a PDF that is not in the bib")
    parser.add_argument("--citekey", help="citekey to use with --pdf")
    parser.add_argument(
        "--backend",
        choices=("auto",) + BACKENDS,
        default="auto",
        help="auto = arxiv, then marker, then pymupdf4llm on failure (default)",
    )
    parser.add_argument("--bib", type=Path, default=DEFAULT_BIB, help="path to library.bib")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory")
    args = parser.parse_args(argv)
    if bool(args.pdf) != bool(args.citekey):
        parser.error("--pdf and --citekey must be used together")
    if args.pdf and args.citekeys:
        parser.error("do not combine positional citekeys with --pdf")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    backends = list(BACKENDS) if args.backend == "auto" else [args.backend]
    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    entries: dict[str, dict] = {}
    if args.bib.is_file():
        try:
            entries = load_bib(args.bib)
        except Exception as error:  # noqa: BLE001
            print(f"ERROR cannot parse {args.bib}: {error}", file=sys.stderr)
            return 1
    elif not args.pdf:
        print(
            f"ERROR {args.bib} not found. Enable the Better BibTeX auto-export to that "
            "path, with the `file` field included.",
            file=sys.stderr,
        )
        return 1

    if args.pdf:
        jobs = [args.citekey]
    elif args.citekeys:
        jobs = list(dict.fromkeys(args.citekeys))
    else:
        jobs = [key for key in entries if args.force or not (out_dir / f"{key}.md").exists()]

    done = skipped = 0
    failed: list[str] = []
    for citekey in jobs:
        try:
            if not CITEKEY_RE.match(citekey):
                raise ExtractError("citekey is not a safe filename")
            if (out_dir / f"{citekey}.md").exists() and not args.force:
                print(f"SKIP  {citekey}: already extracted (use --force)")
                skipped += 1
                continue
            if args.pdf:
                pdf = args.pdf.expanduser()
                if not pdf.is_file():
                    raise ExtractError(f"PDF not found: {pdf}")
                entry, in_bib = entries.get(citekey, {}), citekey in entries
                get_pdf = lambda pdf=pdf: pdf  # noqa: E731
            else:
                if citekey not in entries:
                    raise ExtractError(f"citekey not in {args.bib.name}")
                entry, in_bib = entries[citekey], True
                get_pdf = lambda entry=entry: find_pdf(entry, args.bib)  # noqa: E731
            backend, image_count = extract_one(citekey, get_pdf, entry, in_bib, backends, out_dir)
            label = BACKEND_LABELS.get(backend, backend)
            print(f"OK    {citekey}: {label}/{backend_version(backend)}, {image_count} images")
            done += 1
        except Exception as error:  # noqa: BLE001 - log and continue
            print(f"FAIL  {citekey}: {error}")
            failed.append(citekey)

    print(f"\nSummary: {done} extracted, {skipped} skipped, {len(failed)} failed")
    if failed:
        print("Failed: " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
