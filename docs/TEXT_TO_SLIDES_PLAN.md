# Text to slides plan

## Purpose
- Generate a slide deck from instructor-authored text, optionally using a
  template deck, with a small, well-defined set of supported layout types.
- Keep authoring simple, predictable, and safe for non-programmers.

## Goals
- Keep instructor authoring simple and predictable.
- Use library defaults by default. Optionally use a template deck for theme,
  slide size, masters, and layouts.
- Keep supported layout types small (about 12) and deterministic.
- Keep the CLI scripts thin. Put worker logic in slide_deck_pipeline/.

## Non-goals
- Do not infer free-form layouts beyond the supported layout types.
- Do not modify images or other non-text assets.
- Do not edit charts, SmartArt, embedded objects, or equations.
- Do not attempt to control master slide content. Use deck defaults (library
  default or template deck). Instructors can change masters and styling after
  PPTX creation.

## Terms
- Template deck: the master PPTX used as the canonical source of slide size,
  masters, and layouts for output.
- layout_type: a semantic label like title or content that maps to one template
  layout.
- layout_type is the same semantic class used in the CSV merge pipeline.
- Spec: the canonical YAML representation of the deck content and slide order.

## Inputs and outputs
Inputs:
- Canonical YAML spec file.
- Template deck (PPTX, optional).

Outputs:
- PPTX slide deck generated from library defaults or a template deck.

## High-level pipeline
Authoring path:
1. Instructor writes constrained Markdown.
2. `md_to_slides_yaml.py` converts Markdown to a canonical YAML spec.
3. Instructor optionally edits the YAML spec (advanced use).
4. `text_to_slides.py` renders PPTX from the YAML spec and optional template
   deck.

Rendering path (text_to_slides):
1. Load YAML spec.
2. Validate schema and layout types.
3. Resolve layouts from defaults or a template deck.
4. Render slides by selecting layouts and filling placeholders.
5. Emit a short summary and warnings.

## Canonical YAML spec format
YAML schema (v1):

```yaml
version: 1
template_deck: lecture_template.pptx   # optional

defaults:
  layout_type: content
  master_name: light                   # optional, only with template_deck

slides:
  - layout_type: title_slide
    title: Abiotic Factors
    subtitle: What shapes where organisms can live?

  - layout_type: title_content
    title: Abiotic factors
    bodies:
      - bullets:
          - Temperature
          - Water
          - Oxygen
          - Salinity
          - Sunlight
          - Soil

  - layout_type: centered_text
    bodies:
      - bullets:
          - Practice
          - Today: examples and a short activity

  - layout_type: blank
```

Rules:
- `version` is required.
- `slides` is required and ordered.
- Each slide must include `layout_type`.
- `bodies` is a list of body blocks, one per body placeholder in order.
- Each body block may contain `bullets` as a flat list of strings (no nesting).
- `template_deck` may be provided in YAML or via CLI flag. The CLI flag
  overrides YAML.
- If `template_deck` is absent, ignore `master_name`.

## Supported layout types (v1)
Allowed `layout_type` values (snake_case), matching the 12 built-in Impress
layouts shown in the screenshot:
- blank
- title_slide
- title_content
- title_2_content
- title_only
- centered_text
- title_2_content_and_content
- title_content_and_2_content
- title_2_content_over_content
- title_content_over_content
- title_4_content
- title_6_content

Aliases (accepted input, normalized to the canonical values above):
- blank_slide -> blank
- title -> title_slide
- title_slide -> title_slide
- title_content -> title_content
- title_and_content -> title_content
- title_2_content -> title_2_content
- title_and_2_content -> title_2_content
- title_only -> title_only
- centered_text -> centered_text
- title_2_content_and_content -> title_2_content_and_content
- title_content_and_2_content -> title_content_and_2_content
- title_2_content_over_content -> title_2_content_over_content
- title_content_over_content -> title_content_over_content
- title_4_content -> title_4_content
- title_6_content -> title_6_content

### Placeholder fill rules
- For each layout_type, fill title, subtitle, and body placeholders that exist
  in the selected layout.
- Missing placeholders trigger warnings and the corresponding text is dropped.
- Multi-body layouts fill bodies in order using the `bodies` list.
- If `bodies` is missing, all body placeholders are left empty.
- Extra bodies beyond available placeholders trigger warnings and are dropped.

Expected placeholder counts by layout_type:

| layout_type | title placeholder | subtitle placeholder | body placeholders |
| --- | --- | --- | --- |
| blank | 0 | 0 | 0 |
| title_slide | 1 | 1 | 0 |
| title_content | 1 | 0 | 1 |
| title_2_content | 1 | 0 | 2 |
| title_only | 1 | 0 | 0 |
| centered_text | 0 | 0 | 1 |
| title_2_content_and_content | 1 | 0 | 3 |
| title_content_and_2_content | 1 | 0 | 3 |
| title_2_content_over_content | 1 | 0 | 3 |
| title_content_over_content | 1 | 0 | 2 |
| title_4_content | 1 | 0 | 4 |
| title_6_content | 1 | 0 | 6 |

Notes:
- Subtitle placeholders are only expected for title_slide. If a template layout
  provides a subtitle placeholder in other layouts, it is filled when `subtitle`
  is present.
- centered_text uses the first body placeholder only.

## Template contract
Applies only when `template_deck` is provided.

The template deck must provide the layouts required by the layout types used in
the spec.

Placeholder requirements:
- title_slide/title_only: title placeholder, optional subtitle placeholder.
- title_content: title placeholder and one body placeholder.
- title_2_content/title_4_content/title_6_content: title placeholder and the
  matching number of body placeholders.
- centered_text: centered body placeholder (title placeholder optional).
- blank: no placeholders required.

Layout mapping strategy:
- If `template_deck` is absent, use default library layouts (no master_name).
- If `template_deck` is present, a mapping table resolves:
  - (master_name, layout_type) -> template layout name
- `master_name` defaults from YAML `defaults.master_name` unless overridden by
  CLI.
- If a requested layout is missing in the template deck:
  - strict mode: error
  - default mode: warn and fall back to the default master and layout_type
    mapping if possible; otherwise error

## Text handling
Formatting policy:
- Preserve formatting from template placeholders.
- Do not restyle fonts, sizes, or colors in code except bullet paragraph
  creation.

Bullets:
- Each body block uses its `bullets` list to populate one body placeholder.
- Each bullet string becomes one paragraph at bullet level 0.
- No nested bullet levels in v1.

Overflow policy:
- Prefer office app autofit behavior when present in the template placeholders.
- If reliable autofit cannot be guaranteed by the output toolchain, warn on
  likely overflow using simple heuristics (line count and long lines).
- Optional strict mode may truncate with a visible marker.

## Image insertion spec (v1)
Scope:
- Support image insertion by file path.
- Use the python-pptx default behavior for inserting images into picture
  placeholders.
- Images are only supported for layout_type values that include predefined
  picture placeholders in the 12 supported layouts.
- Do not support explicit fit modes in v1. The tool relies on python-pptx
  defaults. If the default behaves like cover, the tool uses cover. If the
  default changes, the tool follows that behavior.

YAML fields:
Single image:
```yaml
image: fig01.png
```

Multiple images (placed in order):
```yaml
images:
  - fig01.png
  - fig02.jpg
```

Image file resolution:
- If an image path is absolute, use it directly.
- If an image path is relative, resolve it using a deterministic search order.

Search order for a relative image filename `name.ext`:
1. Current working directory (CWD)
2. CWD parent directory (`CWD/..`)
3. Immediate subdirectories of CWD (`CWD/*/`)
4. YAML input file directory (`input_file_dir/`)
5. Parent of YAML input file directory (`input_file_dir/..`)
6. Immediate subdirectories of YAML input file directory (`input_file_dir/*/`)

Rules:
- Stop at the first match.
- If multiple matches are found at the same search level, treat as ambiguous:
  - strict mode: error
  - default mode: warn and pick the first match in sorted path order
- Do not recurse beyond one directory level for subdirectory checks.

Placement rule:
- For the selected layout_type, locate the predefined picture placeholders for
  that layout.
- Assign images to picture placeholders in placeholder order.
- If both `image` and `images` are present, error in strict mode, otherwise
  prefer `images`.

Rendering rule (python-pptx default):
- For each assigned image, call `placeholder.insert_picture(resolved_path)`.
- The tool does not attempt to modify cropping or scaling beyond what
  python-pptx applies by default.

Validation:
- If image or images are provided for a layout_type with zero picture
  placeholders:
  - strict mode: error
  - default mode: warn and drop images
- If more images are provided than picture placeholders for the selected
  layout_type:
  - strict mode: error
  - default mode: warn and drop extras
- If fewer images are provided than picture placeholders, leave remaining
  placeholders empty.

Reporting:
- Report per slide: number of images placed, number dropped (if any), and the
  resolved placeholder count for the selected layout_type.

## Shared path resolution
- The image path search order above should be reused as a shared helper across
  tools when resolving relative PPTX and asset paths, to keep behavior
  consistent and predictable.

## Validation
Spec validation:
- YAML schema version matches supported versions.
- layout_type values are supported.
- Field types are correct (title/subtitle strings, bodies list of blocks, and
  bullets list of strings).
- Required fields exist per layout_type.

Template validation:
- Template deck loads successfully.
- Required layouts exist for the selected `master_name`.
- Required placeholders exist in each mapped layout.

## CLI design

### text_to_slides.py (YAML only)
Usage:
- `./text_to_slides.py -i deck.yaml -t template.pptx -o output.pptx`
- `python3 text_to_slides.py -i deck.yaml -t template.pptx`

Flags:
- `-i`, `--input`: YAML spec file (required).
- `-t`, `--template`: template deck path (optional if present in YAML; overrides
  YAML if provided).
- `-o`, `--output`: output PPTX path (optional; defaults to input basename with
  `.pptx`).
- `--strict`: treat warnings as errors.

### md_to_slides_yaml.py (converter)
Purpose:
- Convert constrained Markdown into the canonical YAML spec.

Usage:
- `./md_to_slides_yaml.py -i deck.md -o deck.yaml`
- `python3 md_to_slides_yaml.py -i deck.md -o deck.yaml`

Markdown constraints:
- Slides separated by a line containing only `---`.
- Each slide begins with a type line:
  - `# Title Slide`
  - `# Title Content`
  - `# Centered Text`
  - `# Blank`
- Within a slide:
  - Next `#` line is title.
  - `##` line is subtitle.
  - `- ` lines are bullets.

Converter rules:
- Unknown layout_type labels are errors.
- Multiple titles or subtitles in one slide are errors.
- Non-bullet paragraphs in content slides are errors in v1.
- v1 Markdown conversion emits only the layout types listed above unless the
  Markdown format is extended to support multiple bodies.

## Code organization
Entry scripts (thin orchestrators):
- `text_to_slides.py`: parse args, load spec, call pipeline functions, print
  summary.
- `md_to_slides_yaml.py`: parse args, call parser, write YAML.

Worker modules (all logic in slide_deck_pipeline/):
- `slide_deck_pipeline/default_layouts.py`
  - resolve built-in layout_type to library default layouts
- `slide_deck_pipeline/spec_schema.py`
  - load YAML
  - validate schema
  - normalize defaults
- `slide_deck_pipeline/md_to_slides_yaml.py`
  - parse constrained Markdown
  - produce spec dict
- `slide_deck_pipeline/template.py`
  - load template deck
  - list masters and layouts
  - resolve (master_name, layout_type) -> layout
  - locate placeholders
- `slide_deck_pipeline/text_to_slides.py`
  - render spec to PPTX using template utilities
  - fill placeholders (title, subtitle, bodies)
- `slide_deck_pipeline/reporting.py`
  - warnings and summary formatting

## Testing plan
Unit tests:
- Markdown parser conversions and error cases.
- YAML schema validation.
- Template mapping resolution and missing layout handling.

Integration tests:
- Render a small deck against a fixture template deck.
- Verify slide count and extracted text content per slide.

Golden checks (lightweight):
- Compare extracted slide text and slide count from rendered PPTX.

## Naming decision
- Script: `md_to_slides_yaml.py` (explicit output intent).
- Worker module: `slide_deck_pipeline/md_to_slides_yaml.py`.
- Main renderer stays `text_to_slides.py`.
