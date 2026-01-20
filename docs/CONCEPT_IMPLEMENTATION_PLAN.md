# Concept implementation plan

## Goal
- Build a repeatable index, merge, rebuild pipeline for PPTX decks that is
  deterministic in Python and flexible in the LLM merge step.

## Scope
- Index PPTX slides to a structured CSV.
- Merge sources into a single CSV with provenance tracking.
- Rebuild a new PPTX from the merged spec using a theme template and the source
  decks referenced in the CSV.
- Support ODP inputs by converting to PPTX before indexing or rebuild.

## Data model and identifiers
- Define a slide record with stable keys: source_pptx, source_slide_index,
  slide_uid, title_text, body_text, notes_text, layout_hint, image_locators,
  image_hashes, text_hash, slide_fingerprint.
- Generate slide_uid from a stable hash of source_pptx + slide_index +
  normalized text + image hashes (or UUID + stored fingerprint).
- Store image locators and hashes as ordered lists encoded in CSV fields.
- Keep binary image data out of the CSV; resolve images from source slides.
- Keep CSV as the only canonical structure; avoid JSON or YAML nesting.
- Normalize text for hashing (whitespace, bullet markers, case rules).

### Image locator format
- Store each locator as a compact string that can be parsed, for example:
  - pptx:deck.pptx#slide=12#shape_id=5
- Keep image_hashes aligned with image_locators for integrity checks.

## Phase 1: Indexing
- Implement a PPTX indexer that outputs per-slide records without exporting images.
- Capture notes_text and layout_hint when available.
- Record image locators and hashes (SHA256 for exact match).
- Emit a validation report: missing text, missing source decks, and unsupported
  shapes.

## Phase 2: Merge and canonical spec
- Define a canonical CSV schema with ordered slides and provenance.
- Provide LLM instructions that enforce:
  - Reuse slide_uid when keeping a slide.
  - Create new slide_uid when merging content, with provenance list.
  - Keep layout_hint explicit and only from a small allowed set.
- Implement a validator that checks CSV headers, missing source deck files,
  image locator validity, and layout_hint validity before rebuild.

## Phase 3: Rebuild
- Start from a template PPTX with approved masters and layouts.
- Map layout_hint to template layouts with fixed bounding boxes.
- Insert title/body text and notes with explicit formatting.
- Insert images by resolving image locators against source decks and verify
  with image_hashes when available.
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
- Separate commands: index, merge-csv-validate, rebuild.
- Store defaults in code, not environment variables.

## Testing and validation
- Add small fixture PPTX files for smoke tests.
- Test index output schema and hash stability.
- Test rebuild output by checking slide count and expected text presence.

## Documentation updates
- Add usage docs for index, merge, and rebuild flows.
- Document the canonical spec schema and supported layout hints.

## Milestones
- M1: Extractor and schema validator in place.
- M2: Canonical spec merge workflow validated end to end.
- M3: Rebuild with template theme and consistent layout rules.
