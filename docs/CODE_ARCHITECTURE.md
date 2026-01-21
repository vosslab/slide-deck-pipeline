# Code architecture

## Overview
- The repo provides a slide deck pipeline that indexes PPTX content to CSV,
  merges CSVs externally, and rebuilds a PPTX or ODP with a template by pulling
  assets from the source decks referenced in the CSV.
- The CSV is only a slide ordering and selection surface; text edits are handled
  by separate YAML patch files.
- The CSV schema and hashing utilities live in
  [slide_deck_pipeline/csv_schema.py](slide_deck_pipeline/csv_schema.py) to keep
  indexing and rebuild in sync.

## Major components
- [index_slide_deck.py](index_slide_deck.py) indexes PPTX or ODP (via conversion)
  into a CSV.
- [slide_deck_pipeline/csv_schema.py](slide_deck_pipeline/csv_schema.py) defines
  the CSV schema and stable hashes used by both pipeline ends.
- [slide_deck_pipeline/pptx_text.py](slide_deck_pipeline/pptx_text.py) extracts
  normalized slide text for hashing and text edits.
- [slide_deck_pipeline/text_boxes.py](slide_deck_pipeline/text_boxes.py) maps
  slides to stable text box identifiers for export and apply.
- [rebuild_slides.py](rebuild_slides.py) rebuilds a PPTX from a merged CSV and
  supports optional ODP output via conversion.
- [export_slide_text.py](export_slide_text.py) exports editable text blocks to a
  YAML patch file.
- [apply_text_edits.py](apply_text_edits.py) applies YAML text patches back onto
  a PPTX or ODP.
- [docs/concept.txt](docs/concept.txt) and
  [docs/CONCEPT_IMPLEMENTATION_PLAN.md](docs/CONCEPT_IMPLEMENTATION_PLAN.md)
  capture the intended pipeline shape and constraints.
- [tests/](tests/) includes repo hygiene tests and CSV utility tests.

## Data flow
- Index: [index_slide_deck.py](index_slide_deck.py) reads PPTX (or ODP converted
  to PPTX) and writes a CSV index.
- Merge: an external LLM or manual process stitches CSV rows into one ordered
  CSV (no JSON or YAML structure).
- Rebuild: [rebuild_slides.py](rebuild_slides.py) reads the merged CSV, applies
  a template layout, inserts text and images, and saves PPTX or ODP. Rebuild
  requires access to the source PPTX or ODP files referenced in the CSV.
- Text edits: [export_slide_text.py](export_slide_text.py) emits YAML patches,
  [apply_text_edits.py](apply_text_edits.py) reapplies them to a deck.

## Design constraint
- Rebuild is not possible from CSV alone, because binary assets remain inside
  the source decks.

## Testing and verification
- Repo hygiene and lint tests live under [tests/](tests/) and are run with
  pytest.
- CSV utilities are covered by
  [tests/test_csv_schema.py](tests/test_csv_schema.py).

## Extension points
- Add layout hint mappings and theme enforcement logic in
  [rebuild_slides.py](rebuild_slides.py).
- Add validation or CSV merge helpers as new root scripts following
  [docs/REPO_STYLE.md](docs/REPO_STYLE.md).
- Expand indexing rules for additional PPTX shapes in
  [index_slide_deck.py](index_slide_deck.py).

## Known gaps
- Verify the required Python dependencies and document them in a manifest.
- Confirm the expected CSV merge rules and align the validator with them.
- Confirm the preferred template PPTX and layout naming conventions.
