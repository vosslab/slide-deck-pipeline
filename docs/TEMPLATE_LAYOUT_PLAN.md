# Template layout plan

## Terms
- Template deck: the master PPTX used as the canonical source of slide size,
  masters, and layouts for rebuild.
- Master: a slide master inside the template deck that defines base styles for
  its layouts.
- Layout: a slide layout under a master that defines placeholders and geometry
  for a specific slide pattern.

## Goals
- Rebuild every slide onto the canvas defined by the template deck.
- Keep layout types small (3 to 6) and deterministic.
- Enforce typography, spacing, and image fit rules in code.
- Rebuild renders new slides using template placeholders. Source slides are used
  only as content sources (text, images).

## Template requirements
- Slide size and aspect ratio are defined by the template deck and are the
  output size for every rebuild.
- The template deck includes layouts that map to the `master_name` and
  `layout_type` columns.
- Each layout provides placeholders for title and body text.
- Figure layouts include a picture placeholder or a known figure box.
- The template deck may include multiple masters; each row specifies
  `(master_name, layout_type)`.

## Layout selection
- The CSV is only a slide ordering and selection surface.
- Layouts are sourced from the template deck at rebuild time.
- The CSV provides editable `master_name` and `layout_type` per row.
- Layout geometry comes from template placeholders (source of truth).
- Rebuild maps `(master_name, layout_type)` to concrete layout names in the
  template deck.

## Typography rules
- Title font family, size, and color are fixed per template.
- Body font family, size, bullet indentation, and line spacing are fixed.
- Rely on office app text autofit behavior when available.
- If autofit is not available in the rebuild path, warn and optionally truncate
  when strict mode is enabled.

## Image placement rules
- Images use `contain` to preserve aspect ratio and avoid stretching.
- Default anchor is `center` for predictable cropping.
- Captions use a fixed style and align to the figure box.

## Aspect ratio policy
- Source slide aspect ratios do not affect output size.
- Place images without changing their aspect ratio.
- Avoid stretch; rely on template defaults or `contain` behavior to preserve aspect.

### CSV column reference
- `source_pptx`: source PPTX or ODP basename.
- `source_slide_index`: integer slide index starting at 1.
- `slide_hash`: content fingerprint for the slide.
- `master_name`: editable target template master name.
- `layout_type`: editable semantic layout type.
- `asset_types`: context only; not editable in the CSV.
- `title_text`: context only; not editable in the CSV.
- `body_text`: context only; not editable in the CSV.
- `notes_text`: context only; not editable in the CSV.

## Slide hash behavior
- Rebuild locates the source slide by (`source_pptx`, `source_slide_index`).
- Rebuild recomputes `slide_hash` from the current slide content.
- If the recomputed hash does not match the CSV `slide_hash`, the slide is
  rejected.

## Slide hash definition
- Compute full SHA-256 over a structural signature (ordered shape tokens and
  notes text). Exclude volatile ids and slide numbers.
- Store the first 16 hex characters (64 bits) as the hash string.
- Hashes are integrity locks for drift detection, not security features.

## Validation checks
- Let the office app handle text fitting inside boxes.
- Warn on images below a minimum resolution threshold.
- Flag objects placed outside box bounds.

## Testing
- Add a small template fixture deck that includes all layouts.
- Add source decks with mixed aspect ratios and image types.
- Verify output matches template placeholders and typography rules.
- Maintain golden outputs for a few fixtures, compared by slide raster diffs or
  by hash of extracted text plus image count.
