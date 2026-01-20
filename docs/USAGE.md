# Usage

Use the root scripts to index slides to CSV, merge CSVs externally, and
rebuild a new PPTX or ODP from the merged CSV and original source files.

## Quick start
```bash
python3 index_slide_deck.py -i input.pptx
```

```bash
python3 rebuild_slides.py -i merged.csv
```

Defaults: `input.pptx` -> `input.csv`, `merged.csv` -> `merged.pptx`.

## CLI
- Index script: [index_slide_deck.py](index_slide_deck.py)
  - `-i`, `--input`: input PPTX or ODP path.
  - `-o`, `--output`: output CSV path (defaults to `<input>.csv`).
- Rebuild script: [rebuild_slides.py](rebuild_slides.py)
  - `-i`, `--input`: merged CSV path.
  - `-o`, `--output`: output PPTX or ODP path (defaults to `<input_csv>.pptx`).
  - `-t`, `--template`: template PPTX path.
- Validate script: [validate_csv.py](validate_csv.py)
  - `-i`, `--input`: merged CSV path.
  - `-c`, `--check-sources`: verify source PPTX or ODP files exist.
  - `-C`, `--no-check-sources`: skip source file checks.
  - `-s`, `--strict`: require text and fingerprint hashes to match.
  - `-S`, `--no-strict`: skip hash validation.
  - Validates `image_locators` format and alignment with `image_hashes`.

## Examples
```bash
python3 index_slide_deck.py -i deck.odp
```

```bash
python3 rebuild_slides.py -i merged.csv -o merged.odp -t template.pptx
```

```bash
python3 validate_csv.py -i merged.csv -c -s
```

## Inputs and outputs
- Inputs: `.pptx` or `.odp` for indexing, merged `.csv` for rebuild.
- Outputs: `.csv` from indexing, `.pptx` or `.odp` on rebuild.
- Rebuild requires access to the source PPTX or ODP files referenced by the CSV.

## Migration note
- Assets directories are no longer produced or consumed.
- Merged CSVs must preserve `source_pptx` and slide identifiers so rebuild can
  resolve images from the source decks.
- Preserve `image_locators` and `image_hashes` so images stay aligned.

## Known gaps
- TODO: Document the CSV merge rules and LLM instructions for stitching rows.
- TODO: Provide a canonical template PPTX and the supported layout hints.
