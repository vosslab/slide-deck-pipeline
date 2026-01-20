# Theme and layout plan

## Goals
- Rebuild every slide onto a canonical 16:10 canvas from a master template.
- Keep layout types small (3 to 6) and deterministic.
- Enforce typography, spacing, and image fit rules in code.

## Template requirements
- Slide size is 16:10 and is the output size for every rebuild.
- Template includes layouts that match allowed `layout_hint` values.
- Each layout provides placeholders for title and body text.
- Figure layouts include a picture placeholder or a known figure box.

## Layout registry
- Allowed layout hints (example set):
  - `title_and_content`
  - `section_header`
  - `two_column`
  - `blank`
- Each layout defines box coordinates for:
  - Title box
  - Body box
  - Figure box
  - Caption box (optional)
- Box coordinates use the template slide size as the reference frame.

## Typography rules
- Title font family, size, and color are fixed per template.
- Body font family, size, bullet indentation, and line spacing are fixed.
- Enforce a max line count per box; flag overflow.

## Image placement rules
- Each image uses a fit policy:
  - `contain`: preserve aspect ratio, letterbox if needed.
  - `cover`: crop to fill the box.
  - `stretch`: avoid unless explicitly requested.
- Default fit policy is `contain`.
- Default anchor is `center` for predictable cropping.
- Captions use a fixed style and align to the figure box.

## Aspect ratio policy
- Source slide aspect ratios do not affect output size.
- 4:3 and 16:9 images are fit into 16:10 boxes using the image fit policy.
- Prefer `contain` for charts and screenshots; allow `cover` for full-bleed photos.

## CSV additions
- `template_name` (optional): selects the template when multiple exist.
- `slide_type`: explicit layout hint that maps to a template layout.
- `image_fit`: per-image fit metadata aligned with `image_locators`.
- `image_anchor`: per-image anchor metadata aligned with `image_locators`.

## Validation checks
- Flag text overflow by measuring rendered text against box height.
- Enforce a minimum font size.
- Warn on images below a minimum resolution threshold.
- Flag objects placed outside box bounds.

## Testing
- Add a small template fixture deck that includes all layouts.
- Add source decks with mixed aspect ratios and image types.
- Verify output matches layout registry box bounds and typography rules.
