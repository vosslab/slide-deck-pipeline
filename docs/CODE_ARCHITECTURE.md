# Code architecture

## Overview
- The repo provides four pipelines: lecture merge via CSV indexing and rebuild,
  text edits via YAML patches, text-to-slides generation from Markdown or YAML,
  and multiple-choice quiz decks with click-to-reveal answers.
- The CSV is only a slide ordering and selection surface; text edits are handled
  by separate YAML patch files.
- Common parsing, hashing, and template logic live in
  [slide_deck_pipeline/](slide_deck_pipeline/) so root scripts stay thin.

## Major components
- Lecture merge pipeline:
  - [index_slide_deck.py](index_slide_deck.py) indexes PPTX or ODP into CSV.
  - [merge_index_csv_files.py](merge_index_csv_files.py) merges CSVs with glob
    support and optional sorting.
  - [rebuild_slides.py](rebuild_slides.py) rebuilds a PPTX from a merged CSV and
    supports optional ODP output via conversion.
  - [validate_csv.py](validate_csv.py) validates merged CSVs and optional hash
    integrity.
- Text edit pipeline:
  - [export_slide_text.py](export_slide_text.py) exports editable text blocks to
    a YAML patch file.
  - [apply_text_edits.py](apply_text_edits.py) applies YAML text patches back
    onto a PPTX or ODP.
- Text-to-slides pipeline:
  - [md_to_slides_yaml.py](md_to_slides_yaml.py) converts constrained Markdown
    into a YAML spec.
  - [text_to_slides.py](text_to_slides.py) renders PPTX from the YAML spec and
    optional template deck.
- MC to slides pipeline:
  - [mc_to_slides.py](mc_to_slides.py) renders a PPTX from quiz text using the
    template source under [template_src/](template_src/).
- Shared core modules:
  - [slide_deck_pipeline/csv_schema.py](slide_deck_pipeline/csv_schema.py) defines
    the CSV schema and stable hashes used by both pipeline ends.
  - [slide_deck_pipeline/csv_validation.py](slide_deck_pipeline/csv_validation.py)
    contains shared CSV validation helpers.
- [slide_deck_pipeline/pptx_text.py](slide_deck_pipeline/pptx_text.py) extracts
  normalized slide text for hashing and text edits.
- [slide_deck_pipeline/pptx_hash.py](slide_deck_pipeline/pptx_hash.py) computes
  slide hashes using normalized slide XML and relationships.
- [slide_deck_pipeline/layout_classifier.py](slide_deck_pipeline/layout_classifier.py)
  classifies slides into semantic layout types.
- [slide_deck_pipeline/text_boxes.py](slide_deck_pipeline/text_boxes.py) maps
  slides to stable text box identifiers for export and apply.
- [slide_deck_pipeline/path_resolver.py](slide_deck_pipeline/path_resolver.py)
  resolves relative files with a deterministic search order.
- [slide_deck_pipeline/text_normalization.py](slide_deck_pipeline/text_normalization.py)
  centralizes whitespace and name normalization helpers.
- [slide_deck_pipeline/mc_parser.py](slide_deck_pipeline/mc_parser.py),
  [slide_deck_pipeline/mc_template.py](slide_deck_pipeline/mc_template.py), and
  [slide_deck_pipeline/mc_to_slides.py](slide_deck_pipeline/mc_to_slides.py)
  implement the quiz text parsing and XML slide cloning.
- [slide_deck_pipeline/spec_schema.py](slide_deck_pipeline/spec_schema.py),
  [slide_deck_pipeline/template.py](slide_deck_pipeline/template.py), and
  [slide_deck_pipeline/default_layouts.py](slide_deck_pipeline/default_layouts.py)
  implement text-to-slides spec validation and template selection.
- [tests/](tests/) includes repo hygiene checks, pipeline tests, and smoke tests.

## Data flow
- Lecture merge: [index_slide_deck.py](index_slide_deck.py) reads PPTX (or ODP
  converted to PPTX) and writes a CSV index. CSV rows are merged (manually or
  with [merge_index_csv_files.py](merge_index_csv_files.py)), then
  [rebuild_slides.py](rebuild_slides.py) applies template layouts, inserts text
  and images, and saves PPTX or ODP. Rebuild requires access to the source PPTX
  or ODP files referenced in the CSV.
- Text edits: [export_slide_text.py](export_slide_text.py) emits YAML patches,
  edits are made in YAML, then [apply_text_edits.py](apply_text_edits.py)
  reapplies them to a deck.
- Text-to-slides: [md_to_slides_yaml.py](md_to_slides_yaml.py) converts Markdown
  to YAML, then [text_to_slides.py](text_to_slides.py) validates the spec and
  renders a PPTX with optional template layouts.
- MC to slides: [mc_to_slides.py](mc_to_slides.py) parses quiz text, clones the
  popup template slide from [template_src/](template_src/), and writes a PPTX.

## Design constraint
- Rebuild is not possible from CSV alone, because binary assets remain inside
  the source decks.

## Testing and verification
- Repo hygiene and pipeline tests live under [tests/](tests/) and are run with
  pytest.
- [test_script.sh](test_script.sh) runs a full index, merge, and rebuild pass
  over root-level PPTX files.

## Extension points
- Add layout selection or template rules in
  [slide_deck_pipeline/rebuild.py](slide_deck_pipeline/rebuild.py) and
  [slide_deck_pipeline/template.py](slide_deck_pipeline/template.py).
- Add new spec fields or layout types in
  [slide_deck_pipeline/spec_schema.py](slide_deck_pipeline/spec_schema.py) and
  [slide_deck_pipeline/default_layouts.py](slide_deck_pipeline/default_layouts.py).
- Add quiz template shape mapping rules in
  [slide_deck_pipeline/mc_template.py](slide_deck_pipeline/mc_template.py).
- Add new CLI helpers as root scripts following
  [docs/REPO_STYLE.md](docs/REPO_STYLE.md).

## Known gaps
- Confirm the preferred template PPTX and layout naming conventions.
- Confirm the CSV merge ordering rules for automated workflows.
- Verify git status and ignored files (git commands were skipped by request).
