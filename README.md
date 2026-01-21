# Slide deck pipeline

Build and remix slide decks with four pipelines: lecture merging via CSV,
targeted text edits via YAML patches, text-to-slides generation from Markdown
or YAML, and multiple-choice quiz decks with click-to-reveal answers.

## Pipelines
- [docs/LECTURE_MERGE_GUIDE.md](docs/LECTURE_MERGE_GUIDE.md): index, merge, and
  rebuild decks with CSV as the ordering surface.
- [docs/TEXT_EDIT_PIPELINE_GUIDE.md](docs/TEXT_EDIT_PIPELINE_GUIDE.md): export
  slide text blocks, edit YAML, and apply changes back to a deck.
- [docs/TEXT_TO_SLIDES_GUIDE.md](docs/TEXT_TO_SLIDES_GUIDE.md): author
  constrained Markdown or YAML and render a PPTX deck.
- [docs/MC_TO_SLIDES_GUIDE.md](docs/MC_TO_SLIDES_GUIDE.md): build a quiz deck
  from text with a popup answer reveal.

## Documentation
- [docs/INSTALL.md](docs/INSTALL.md): setup requirements and dependencies.
- [docs/USAGE.md](docs/USAGE.md): CLI usage and examples.
- [docs/CONCEPT_IMPLEMENTATION_PLAN.md](docs/CONCEPT_IMPLEMENTATION_PLAN.md):
  pipeline constraints and shared concepts.
- [docs/MC_TO_SLIDES.md](docs/MC_TO_SLIDES.md): multiple-choice deck plan.
- [docs/TEXT_EDITING_PLAN.md](docs/TEXT_EDITING_PLAN.md): text edit schema and
  matching rules.
- [docs/TEXT_TO_SLIDES_PLAN.md](docs/TEXT_TO_SLIDES_PLAN.md): text-to-slides
  schema and template contract.
- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md): components and data flow.
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md): repo layout and where to add work.
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): known issues and fixes.

## Quick start
```bash
python3 index_slide_deck.py -i input.pptx
```

Merge CSV rows externally, then rebuild a deck with `rebuild_slides.py` (see
[docs/USAGE.md](docs/USAGE.md)). Defaults: `input.pptx` -> `input.csv`,
`merged.csv` -> `merged.pptx`.

## Testing
```bash
python3 -m pytest
```
