# Essays — Collected Writing of Paul Graham (print-ready book)

A curated print-ready book of 40 of Paul Graham's best-known essays,
assembled from paulgraham.com, grouped chronologically into four parts.

## Files

- `manuscript.md` — the full book in pure Markdown (YAML front matter,
  title page, per-part epigraphs, hand-written Table of Contents, and the
  40 essays grouped into four era-based parts).
- `book.pdf` — 6×9in print-ready PDF generated with pandoc.
- `raw/` — the 40 extracted essays, one Markdown file each
  (`NN-slug.md`), in chronological order.
- `index.csv` — `number, title, date, word_count` for all 40 essays.
- `gen.py` — the generator that produces `raw/`, `index.csv`, and
  `manuscript.md` from the two source data files below.

## Provenance

The task described extracting from a local `source.txt`, but no such file
existed in the repository, and `paulgraham.com` / `web.archive.org` are
blocked by this environment's outbound network policy. Essay text was
therefore taken from two public, raw-accessible mirrors of the essays:

- Essay list, dates, and canonical URLs:
  `mckaywrigley/paul-graham-gpt` → `scripts/pg.json`
- Paragraph-faithful Markdown body text:
  `lmmsoft/paul_graham_essays` → `pg_essays_metadata.json`

To rebuild from scratch:

    curl -sSL -o pg.json   https://raw.githubusercontent.com/mckaywrigley/paul-graham-gpt/main/scripts/pg.json
    curl -sSL -o meta.json https://raw.githubusercontent.com/lmmsoft/paul_graham_essays/main/pg_essays_metadata.json
    python3 gen.py
    pandoc manuscript.md -o book.pdf --wrap=auto

## Curation

40 essays were selected as a "best of" and grouped by era:

- Part One — Hackers and Painters (2001–2004): 9 essays
- Part Two — The Startup Playbook (2005–2008): 9 essays
- Part Three — Ideas and Determination (2009–2013): 11 essays
- Part Four — Work, Wealth, and Life (2014–2022): 11 essays

Each part opens with an epigraph quoted from one of its essays. Essays
are ordered chronologically. All text is verbatim Paul Graham; only
site navigation, the "Want to start a startup?" promo, translation
links, and a few scrape artifacts (corrupted em dashes, `déclassé`,
`Gödel`) were cleaned. Essay footnotes ("Notes") are preserved.

The full catalog of 200+ essays is available; this edition is the
curated 40-essay selection requested.
