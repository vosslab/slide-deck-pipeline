# Concept implementation plan

## Goal
- Build a repeatable index, merge, rebuild pipeline for PPTX decks that is
  deterministic in Python and flexible in the LLM merge step.

## Scope
- Index PPTX slides to a structured CSV index.
- Merge sources into a single CSV with provenance tracking.
- Rebuild a new PPTX from the merged spec using a theme template and the source
  decks referenced in the CSV.
- Support ODP inputs by converting to PPTX before indexing or rebuild.

## Data model and identifiers
- Define a slide record with stable keys: source_pptx, source_slide_index,
  slide_hash, master_name, layout_name, asset_types, title_text, body_text,
  notes_text.
- Generate slide_hash from a stable CRC32 of source_pptx + slide_index +
- normalized slide text.
- Keep binary image data out of the CSV; resolve images from source slides.
- Keep the CSV as the ordering and selection surface; avoid design authority in
  CSV fields. asset_types/title_text/body_text/notes_text are context only and
  are not editable in the CSV. Use YAML for text edit patches.
- Normalize text for hashing (whitespace, bullet markers, case rules).

### CSV column reference
- `source_pptx`: source PPTX or ODP basename.
- `source_slide_index`: integer slide index starting at 1.
- `slide_hash`: content fingerprint for the slide.
- `master_name`: editable target template master name.
- `layout_name`: editable target template layout name.
- `asset_types`: context only; not editable in the CSV.
- `title_text`: context only; not editable in the CSV.
- `body_text`: context only; not editable in the CSV.
- `notes_text`: context only; not editable in the CSV.

## Phase 1: Indexing
- Implement a PPTX indexer that outputs per-slide records without exporting images.
- Capture notes_text and source layout names for reference.
- Emit a validation report: missing text, missing source decks, and unsupported
  shapes.

## Phase 2: Merge and canonical spec
- Define a canonical CSV schema with ordered slides and provenance.
- Provide LLM instructions that enforce:
  - Reuse slide_hash when keeping a slide.
  - Create new slide_hash when merging content, with provenance list.
  - Keep master_name/layout_name explicit and only from the template deck.
- Implement a validator that checks CSV headers, missing source deck files, and
  master/layout validity before rebuild.

## Phase 3: Rebuild
- Start from a template PPTX with approved masters and layouts.
- Select layouts from the template deck using master_name/layout_name.
- Insert title/body text and notes with explicit formatting.
- Insert images by reading them from the source slides referenced in the CSV.
- Apply theme rules for fonts, sizes, colors, spacing, and bullet indentation.

## Deduplication strategy
- Use slide_hash for exact text matches.
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
- Document the canonical spec schema and master/layout selection rules.

## Slide hash behavior
- Rebuild locates the source slide by (`source_pptx`, `source_slide_index`).
- Rebuild recomputes `slide_hash` from the current slide content.
- If the recomputed hash does not match the CSV `slide_hash`, the slide is
  rejected.

## Slide hash definition
- Compute full SHA-256 over normalized slide content.
- Store the first 16 hex characters (64 bits) as the hash string.
- Hashes are integrity locks for drift detection, not security features.

## Milestones
- M1: Extractor and schema validator in place.
- M2: Canonical spec merge workflow validated end to end.
- M3: Rebuild with template theme and consistent layout rules.
