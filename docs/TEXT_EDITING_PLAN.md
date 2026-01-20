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
- Template dependency: target resolution prefers placeholders in the template
  layouts. If a slide is not template-based, fall back to best-effort matching
  and mark it in the report.

## Addressing scheme
- Address text by placeholder, not by shape order.
- Each editable block emits:
  - `source_pptx`
  - `source_slide_index`
  - `slide_hash`
  - `box_id` (stable id within the slide)
  - `shape_name` (if present)
  - `placeholder_type` (best-effort string; do not use as a primary key)
  - `text_hash_before` (normalized)
  - `text` (editable field)
- Primary key stays `source_pptx` + `source_slide_index` + `box_id`.
- `box_id` rules:
  - For placeholders: `title`, `subtitle`, `body_1`, `body_2`.
  - Else: normalized `shape_name` when available.
  - Else: `box_<n>` with a guard hash in the exporter.
- Text normalization for `text_hash_before`: trim whitespace, normalize newlines,
  collapse multiple spaces, and preserve bullet indentation markers.
- Require `slide_hash` so edits apply only to the intended slide version.

## Hash definition
- Compute full SHA-256 over normalized text content.
- Store the first 16 hex characters (64 bits) as the hash string.
- Hashes are integrity locks for drift detection, not security features.

## Edit artifact format
- Use a separate file from the indexing CSV.
- Use YAML with one file per deck and a list of slide patches.
- Keep YAML simple: no anchors, no complex tags.
- Include `edit_status` or `locked` to freeze blocks from edits.
- Bullets round-trip as plain text with `\n` and leading tabs for indentation by
  default, or use nested bullet lists when explicitly enabled.

### YAML schema (v1)
```yaml
version: 1
source_pptx: talk.pptx
patches:
  - source_slide_index: 12
    slide_hash: "2e17a21f"
    boxes:
      - box_id: "title"
        text_hash_before: "8b1c2f4e"
        text: |
          New title text
      - box_id: "body_1"
        text_hash_before: "f2a9d3c0"
        bullets:
          - "First bullet"
          - ["Sub bullet A", "Sub bullet B"]
          - "Second bullet"
```

## Insertion rules
- Locate the target text block using the addressing scheme.
- Verify `text_hash_before` still matches before applying edits.
- Replace text while preserving paragraph structure when possible.
- Failure modes:
  - Missing slide: skip and report.
  - Target not found: skip and report.
  - Hash mismatch: warn and skip unless forced by a flag.
  - On mismatch, report old/new hashes and a short text excerpt.
  - Slide hash mismatch: skip and report.

## Formatting policy
- Default: preserve formatting from the existing placeholder and replace text
  only.
- Optional: apply canonical formatting rules after insertion.

## Bullet handling
- If `bullets` exists, render it depth-first:
  - A string is a bullet at the current level.
  - A list increases indentation level by 1 for its contents.
- Reject dicts or numbers inside `bullets`.
- Support blank lines with an empty string `""`.
- Enforce a maximum nesting depth (for example 4).

## Validation and reporting
- Extract step emits a summary table of targets.
- Insert step emits a diff-style report: updated, skipped, mismatched, missing.
- Optional overflow risk heuristic (line count and font size) for new text.

## Pipeline integration
- Option A: edit source decks first, then index and rebuild.
- Option B: rebuild into the unified deck, then apply text edits.
- Default: Option B to keep edits on the canonical layout.

## Tool naming
- Extract: `export_slide_text.py`.
- Apply: `apply_text_edits.py`.
