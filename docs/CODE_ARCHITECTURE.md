# Code architecture

## Overview
- The repo provides a slide deck pipeline that extracts PPTX content to CSV with
  assets, merges CSVs externally, and rebuilds a PPTX or ODP with a template.
- The CSV schema and hashing utilities live in [slide_csv.py](slide_csv.py) to
  keep extraction and rebuild in sync.

## Major components
- [extract_slides.py](extract_slides.py) extracts PPTX or ODP (via conversion)
  into a CSV plus assets folder.
- [slide_csv.py](slide_csv.py) defines the CSV schema, list encoding, and stable
  hashes and IDs used by both pipeline ends.
- [rebuild_slides.py](rebuild_slides.py) rebuilds a PPTX from a merged CSV and
  supports optional ODP output via conversion.
- [docs/concept.txt](docs/concept.txt) and
  [docs/CONCEPT_IMPLEMENTATION_PLAN.md](docs/CONCEPT_IMPLEMENTATION_PLAN.md)
  capture the intended pipeline shape and constraints.
- [tests/](tests/) includes repo hygiene tests and CSV utility tests.

## Data flow
- Extract: [extract_slides.py](extract_slides.py) reads PPTX (or ODP converted to
  PPTX) and writes a CSV plus image assets.
- Merge: an external LLM or manual process stitches CSV rows into one ordered
  CSV (no JSON or YAML structure).
- Rebuild: [rebuild_slides.py](rebuild_slides.py) reads the merged CSV, applies
  a template layout, inserts text and images, and saves PPTX or ODP.

## Testing and verification
- Repo hygiene and lint tests live under [tests/](tests/) and are run with
  pytest.
- CSV utilities are covered by [tests/test_slide_csv.py](tests/test_slide_csv.py).

## Extension points
- Add layout hint mappings and theme enforcement logic in
  [rebuild_slides.py](rebuild_slides.py).
- Add validation or CSV merge helpers as new root scripts following
  [docs/REPO_STYLE.md](docs/REPO_STYLE.md).
- Expand extraction rules for additional PPTX shapes in
  [extract_slides.py](extract_slides.py).

## Known gaps
- Verify the required Python dependencies and document them in a manifest.
- Confirm the expected CSV merge rules and add a validator script if needed.
- Confirm the preferred template PPTX and layout naming conventions.
