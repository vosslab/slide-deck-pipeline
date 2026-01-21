# Text to slides plan

## Purpose
- Generate a slide deck from instructor-authored text, optionally using a
  template deck, with a small, well-defined set of supported layout types.
- Keep authoring simple, predictable, and safe for non-programmers.

## Goals
- Keep instructor authoring simple and predictable.
- Use library defaults by default. Optionally use a template deck for theme,
  slide size, masters, and layouts.
- Keep supported layout types small (3 to 6) and deterministic.
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
  - layout_type: title
    title: Abiotic Factors
    subtitle: What shapes where organisms can live?

  - layout_type: content
    title: Abiotic factors
    bullets:
      - Temperature
      - Water
      - Oxygen
      - Salinity
      - Sunlight
      - Soil

  - layout_type: section
    title: Practice
    subtitle: Today: examples and a short activity

  - layout_type: blank
```

Rules:
- `version` is required.
- `slides` is required and ordered.
- Each slide must include `layout_type`.
- `bullets` is a flat list of strings in v1 (no nesting).
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

### title
Required:
- `title`

Optional:
- `subtitle`

Behavior:
- Fill title placeholder.
- Fill subtitle placeholder if present; otherwise warn and drop subtitle.

### content
Required:
- `title`

Optional:
- `bullets`

Behavior:
- Fill title placeholder.
- Render bullets into the body placeholder, one paragraph per item.
- If bullets are missing, leave body empty.

### section
Required:
- `title`

Optional:
- `subtitle`

Behavior:
- Uses a section layout. Fill placeholders as for title.

### blank
No fields required.

Behavior:
- Create a blank slide using the blank layout.

## Template contract
Applies only when `template_deck` is provided.

The template deck must provide the layouts needed by the supported layout types.

Minimum required layouts:
- title
- content
- section
- blank

Placeholder requirements:
- title: title placeholder, optional subtitle placeholder.
- content: title placeholder, body placeholder.
- section: title placeholder, optional subtitle placeholder.
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
- Each bullet string becomes one paragraph at bullet level 0.
- No nested bullet levels in v1.

Overflow policy:
- Prefer office app autofit behavior when present in the template placeholders.
- If reliable autofit cannot be guaranteed by the output toolchain, warn on
  likely overflow using simple heuristics (line count and long lines).
- Optional strict mode may truncate with a visible marker.

## Validation
Spec validation:
- YAML schema version matches supported versions.
- layout_type values are supported.
- Field types are correct (title and subtitle strings, bullets list of strings).
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
  - `# Content`
  - `# Section`
  - `# Blank`
- Within a slide:
  - Next `#` line is title.
  - `##` line is subtitle.
  - `- ` lines are bullets.

Converter rules:
- Unknown layout_type labels are errors.
- Multiple titles or subtitles in one slide are errors.
- Non-bullet paragraphs in content slides are errors in v1.

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
  - fill placeholders (title, subtitle, bullets)
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
