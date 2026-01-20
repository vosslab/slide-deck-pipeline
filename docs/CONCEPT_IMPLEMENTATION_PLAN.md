# Concept implementation plan

## Goal
- Build a repeatable extract, merge, rebuild pipeline for PPTX decks that is
  deterministic in Python and flexible in the LLM merge step.

## Scope
- Extract PPTX slides to a structured CSV plus assets.
- Merge sources into a single CSV with provenance tracking.
- Rebuild a new PPTX from the merged spec using a theme template.
- Support ODP inputs by converting to PPTX before extraction or rebuild.

## Data model and identifiers
- Define a slide record with stable keys: source_pptx, source_slide_index,
  slide_uid, title_text, body_text, notes_text, layout_hint, image_refs,
  image_hashes, text_hash, slide_fingerprint.
- Generate slide_uid from a stable hash of source_pptx + slide_index +
  normalized text + image hashes (or UUID + stored fingerprint).
- Store image_refs and hashes as ordered lists encoded in CSV fields.
- Keep binary image data out of the CSV; store only asset references.
- Keep CSV as the only canonical structure; avoid JSON or YAML nesting.
- Normalize text for hashing (whitespace, bullet markers, case rules).

## Phase 1: Extraction
- Implement a PPTX extractor that outputs per-slide records and exports images
  to assets/<slide_uid>_imgNN.ext.
- Capture notes_text and layout_hint when available.
- Hash images (SHA256 for exact match, perceptual hash for near-dup).
- Emit a validation report: missing text, missing images, and unsupported shapes.

## Phase 2: Merge and canonical spec
- Define a canonical CSV schema with ordered slides and provenance.
- Provide LLM instructions that enforce:
  - Reuse slide_uid when keeping a slide.
  - Create new slide_uid when merging content, with provenance list.
  - Keep layout_hint explicit and only from a small allowed set.
- Implement a validator that checks CSV headers, missing assets, and
  layout_hint validity before rebuild.

## Phase 3: Rebuild
- Start from a template PPTX with approved masters and layouts.
- Map layout_hint to template layouts with fixed bounding boxes.
- Insert title/body text and notes with explicit formatting.
- Insert images by image_refs with consistent sizing and alignment rules.
- Apply theme rules for fonts, sizes, colors, spacing, and bullet indentation.

## Deduplication strategy
- Use text_hash for exact text matches.
- Use slide_fingerprint (text + image hashes) for slide-level dedup.
- Allow near-dup review for cases where titles collide but images differ.

## Layout and theme constraints
- Keep 3 to 6 layout types and document each with box coordinates.
- Avoid master edits in code; prefer explicit formatting and a template base.
- Track layouts that cannot be rebuilt due to unsupported objects.

## CLI and configuration
- Provide a minimal CLI with explicit input/output paths and mode flags.
- Separate commands: extract, merge-csv-validate, rebuild.
- Store defaults in code, not environment variables.

## Testing and validation
- Add small fixture PPTX files for smoke tests.
- Test extract output schema, asset export, and hash stability.
- Test rebuild output by checking slide count and expected text presence.

## Documentation updates
- Add usage docs for extract, merge, and rebuild flows.
- Document the canonical spec schema and supported layout hints.

## Milestones
- M1: Extractor and schema validator in place.
- M2: Canonical spec merge workflow validated end to end.
- M3: Rebuild with template theme and consistent layout rules.
