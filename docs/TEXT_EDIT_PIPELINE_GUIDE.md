# Text edit pipeline guide

## Goal
- Export slide text blocks, edit them in YAML, and apply the changes back to a
  deck without changing layouts.
- Keep edits deterministic with slide and text hashes.

## Quick workflow summary
- Export text blocks with `export_slide_text.py`.
- Edit the YAML patch file.
- Apply edits with `apply_text_edits.py`.
- Review the summary counts for mismatches and missing targets.

## Scripts you will use
- `export_slide_text.py` exports editable text blocks to YAML.
- `apply_text_edits.py` applies YAML patches back onto a deck.

## Step 1: Export text blocks
```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 export_slide_text.py \
  -i lecture.pptx
```

Defaults: `lecture.pptx` -> `lecture_text_edits.yaml`.

Optional flags:
- `-n`, `--include-notes` to include speaker notes blocks.
- `-s`, `--include-subtitle` to include subtitle placeholders.
- `-f`, `--include-footer` to include footer placeholders.

If you include subtitle or footer blocks here, use the same flags when applying
patches so the box ids line up.

## Step 2: Edit the YAML patch file
The exporter writes a YAML file with slide hashes, box ids, and the current
text. Edit only the text or bullets, not the hashes, unless you intend to
override the safety checks.

Minimal example:

```yaml
version: 1
source_pptx: lecture.pptx
patches:
  - source_slide_index: 3
    slide_hash: "2e17a21f"
    boxes:
      - box_id: "title"
        text_hash_before: "8b1c2f4e"
        text: "New title text"
      - box_id: "body_1"
        text_hash_before: "f2a9d3c0"
        bullets:
          - "First bullet"
          - ["Sub bullet A", "Sub bullet B"]
```

Notes:
- `bullets` is optional. If present, it replaces `text` and supports nested
  lists up to 4 levels deep.
- If you prefer plain text, keep `text` and use leading tab characters to
  indicate bullet depth.
- You can lock a box by setting `locked: true` or `edit_status: locked`.

## Step 3: Apply the edits
```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 apply_text_edits.py \
  -i lecture_text_edits.yaml
```

The patch file must include `source_pptx`, which is used to locate the input
deck with the shared path resolver.

Optional flags:
- `-f`, `--force` to apply edits even if text hashes mismatch.
- `-s`, `--include-subtitle` and `-r`, `--include-footer` to match boxes that
  were exported with those flags.
- `--inplace` to allow writing edits to the input file.

## Step 4: Review the summary
`apply_text_edits.py` prints counts for updated blocks, skipped locked blocks,
missing targets, text hash mismatches, and slide hash mismatches. If mismatches
show up, re-export and re-apply to align with the current deck.

## Related docs
- [docs/TEXT_EDITING_PLAN.md](docs/TEXT_EDITING_PLAN.md)
- [docs/USAGE.md](docs/USAGE.md)
