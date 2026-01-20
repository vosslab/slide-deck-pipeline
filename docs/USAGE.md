# Usage

Use the root scripts to extract slides to CSV, merge CSVs externally, and
rebuild a new PPTX or ODP from the merged CSV.

## Quick start
```bash
python3 extract_slides.py -i input.pptx -o slides.csv
```

```bash
python3 rebuild_slides.py -i merged.csv -o merged.pptx
```

## CLI
- Extract script: [extract_slides.py](extract_slides.py)
  - `-i`, `--input`: input PPTX or ODP path.
  - `-o`, `--output`: output CSV path.
  - `-a`, `--assets-dir`: assets directory (defaults to `<output_csv>_assets`).
- Rebuild script: [rebuild_slides.py](rebuild_slides.py)
  - `-i`, `--input`: merged CSV path.
  - `-o`, `--output`: output PPTX or ODP path.
  - `-a`, `--assets-dir`: assets directory (defaults to `<input_csv>_assets`).
  - `-t`, `--template`: template PPTX path.
- Validate script: [validate_csv.py](validate_csv.py)
  - `-i`, `--input`: merged CSV path.
  - `-a`, `--assets-dir`: assets directory (defaults to `<input_csv>_assets`).
  - `-c`, `--check-assets`: verify image assets exist.
  - `-C`, `--no-check-assets`: skip asset checks.
  - `-s`, `--strict`: require text and fingerprint hashes to match.
  - `-S`, `--no-strict`: skip hash validation.

## Examples
```bash
python3 extract_slides.py -i deck.odp -o deck.csv -a deck_assets
```

```bash
python3 rebuild_slides.py -i merged.csv -o merged.odp -t template.pptx
```

```bash
python3 validate_csv.py -i merged.csv -c -s
```

## Inputs and outputs
- Inputs: `.pptx` or `.odp` for extraction, merged `.csv` for rebuild.
- Outputs: `.csv` plus an assets directory on extract, `.pptx` or `.odp` on rebuild.

## Known gaps
- TODO: Document the CSV merge rules and LLM instructions for stitching rows.
- TODO: Provide a canonical template PPTX and the supported layout hints.
