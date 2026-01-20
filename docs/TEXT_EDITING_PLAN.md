# Text editing plan

## Goals
- Provide narrowly scoped, deterministic text edits on slide decks.
- Keep edits reversible and auditable with explicit targeting metadata.
- Avoid layout drift by preserving placeholder structure by default.

## Non-goals
- Do not edit charts, SmartArt, tables rendered as images, embedded objects, or
  equations.
- Do not modify images or other non-text assets.

## Supported text surfaces
- Title and body placeholders only (default).
- Optional: speaker notes.
- Optional: subtitle and footer placeholders if they are stable in the template.

## Addressing scheme
- Address text by placeholder, not by shape order.
- Each editable block emits:
  - `source_file`
  - `slide_index`
  - `target` (enum): title, body, subtitle, notes, footer
  - `shape_name` (if present)
  - `placeholder_type` (if detectable)
  - `text_hash_before` (normalized)
  - `text` (editable field)

## Edit artifact format
- Use a separate file from the indexing CSV.
- Recommended: `deck_text.csv` for simple workflows.
- Optional: `deck_text.jsonl` if multiline or metadata becomes complex.
- Include `edit_status` or `locked` to freeze blocks from edits.

## Insertion rules
- Locate the target text block using the addressing scheme.
- Verify `text_hash_before` still matches before applying edits.
- Replace text while preserving paragraph structure when possible.
- Failure modes:
  - Missing slide: skip and report.
  - Target not found: skip and report.
  - Hash mismatch: warn and skip unless forced by a flag.

## Formatting policy
- Default: preserve formatting from the existing placeholder and replace text
  only.
- Optional: apply canonical formatting rules after insertion.

## Validation and reporting
- Extract step emits a summary table of targets.
- Insert step emits a diff-style report: updated, skipped, mismatched, missing.
- Optional overflow risk heuristic (line count and font size) for new text.

## Pipeline integration
- Option A: edit source decks first, then index and rebuild.
- Option B: rebuild into the unified deck, then apply text edits.
- Default: Option B to keep edits on the canonical layout.

## Tool naming
- Extract: `export_slide_text.py` or `extract_text.py`.
- Apply: `apply_text_edits.py` or `patch_slide_text.py`.
