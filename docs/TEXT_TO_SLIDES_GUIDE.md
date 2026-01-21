# Text to slides guide

## Goal
- Build a PPTX deck from instructor-authored Markdown or YAML, optionally using
  a template deck for masters, layouts, and styling.

## Quick workflow summary
- Write constrained Markdown.
- Convert it to a YAML spec with `md_to_slides_yaml.py`.
- Optionally edit the YAML spec for advanced layouts or images.
- Render a PPTX with `text_to_slides.py`.

## Scripts you will use
- `md_to_slides_yaml.py` converts constrained Markdown into a YAML spec.
- `text_to_slides.py` renders a PPTX from the YAML spec.

## Step 1: Write constrained Markdown
Slides are separated by `---`. Each slide starts with a type line using `#`.

Supported Markdown types:
- `title_slide`
- `title_content`
- `centered_text`
- `blank`

Minimal example:

```text
# title_slide
# Abiotic Factors
## What shapes where organisms can live?
---
# title_content
# Abiotic factors
- Temperature
- Water
- Oxygen
---
# centered_text
- Practice
- Today: examples and a short activity
---
# blank
```

If you need additional layout types or images, edit the YAML spec directly
after conversion.

## Step 2: Convert Markdown to YAML
```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 md_to_slides_yaml.py \
  -i lecture.md \
  -o lecture.yaml
```

## Step 3: (Optional) Edit the YAML spec
The YAML spec supports all layout types defined in the text-to-slides plan and
adds image fields.

Key fields:
- `template_deck`: optional template PPTX.
- `defaults.layout_type`: default layout type for slides.
- `defaults.master_name`: template master name (only used with a template deck).
- `slides[].layout_type`, `title`, `subtitle`, `bodies`, `image`, `images`.

## Step 4: Render slides
```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 text_to_slides.py \
  -i lecture.yaml \
  -t lecture_template.pptx \
  -o lecture.pptx
```

Defaults: `lecture.yaml` -> `lecture.pptx` when `-o` is omitted.

Use `--strict` to treat warnings as errors.

## Image path resolution
Relative image paths are resolved with a deterministic search order:

1. Current working directory.
2. Parent of the current working directory.
3. Immediate subdirectories of the current working directory.
4. YAML input file directory.
5. Parent of the YAML input file directory.
6. Immediate subdirectories of the YAML input file directory.

If multiple matches exist at the same search level, the first sorted path is
used with a warning (strict mode raises an error).

## Related docs
- [docs/TEXT_TO_SLIDES_PLAN.md](docs/TEXT_TO_SLIDES_PLAN.md)
- [docs/USAGE.md](docs/USAGE.md)
