# Usage

Use the root scripts to index slides to CSV, merge CSVs externally, and
rebuild a new PPTX or ODP from the merged CSV and original source files.
The CSV is only a slide ordering and selection surface; text edits use YAML
patch files.
CSV context fields (layout_confidence/layout_reasons/asset_types/title/body/notes)
are for context only and are not editable.
The editable layout controls are `master_name` and `layout_type`.

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
  - `-t`, `--template`: template PPTX path for master/layout validation.
  - `-s`, `--strict`: recompute slide hashes from source slides.
  - `-S`, `--no-strict`: skip slide hash validation.
- Export text script: [export_slide_text.py](export_slide_text.py)
  - `-i`, `--input`: input PPTX or ODP path.
  - `-o`, `--output`: output YAML path (defaults to `<input>_text_edits.yaml`).
  - `-n`, `--include-notes`: include speaker notes blocks.
  - `-s`, `--include-subtitle`: include subtitle placeholders.
  - `-f`, `--include-footer`: include footer placeholders.
- Apply text script: [apply_text_edits.py](apply_text_edits.py)
  - `-i`, `--input`: input PPTX or ODP path.
  - `-p`, `--patches`: YAML patch file.
  - `-o`, `--output`: output PPTX or ODP path (defaults to `<input>_edited.pptx`).
  - `-f`, `--force`: apply edits even if text hashes mismatch.
  - `-s`, `--include-subtitle`: include subtitle placeholders in matching.
  - `-r`, `--include-footer`: include footer placeholders in matching.

## Examples
```bash
python3 index_slide_deck.py -i deck.odp
```

```bash
python3 rebuild_slides.py -i merged.csv -o merged.odp -t template.pptx
```

```bash
python3 validate_csv.py -i merged.csv -c -s -t template.pptx
```

```bash
python3 export_slide_text.py -i merged.pptx -n
```

```bash
python3 apply_text_edits.py -i merged.pptx -p merged_text_edits.yaml
```

## Inputs and outputs
- Inputs: `.pptx` or `.odp` for indexing, merged `.csv` for rebuild, YAML for text edits.
- Outputs: `.csv` from indexing, `.pptx` or `.odp` on rebuild, YAML patch files.
- Rebuild requires access to the source PPTX or ODP files referenced by the CSV.

## Migration note
- Assets directories are no longer produced or consumed.
- Merged CSVs must preserve `source_pptx` and slide identifiers so rebuild can
  resolve images from the source decks.

## Known gaps
- TODO: Document the CSV merge rules and LLM instructions for stitching rows.
- TODO: Provide a canonical template PPTX and the supported layout hints.
