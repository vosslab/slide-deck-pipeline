# slide-deck-pipeline

Extract PPTX or ODP slide decks to CSV with assets, merge rows externally, and
rebuild a themed PPTX or ODP from a template for workflows that consolidate
multiple decks.

## Documentation
- [docs/INSTALL.md](docs/INSTALL.md): setup requirements and dependencies.
- [docs/USAGE.md](docs/USAGE.md): CLI usage and examples.
- [docs/CONCEPT_IMPLEMENTATION_PLAN.md](docs/CONCEPT_IMPLEMENTATION_PLAN.md):
  pipeline plan and constraints.
- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md): components and data flow.
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md): repo layout and where to add work.
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): known issues and fixes.

## Quick start
```bash
python3 extract_slides.py -i input.pptx -o slides.csv
```

Merge CSV rows externally, then rebuild a deck with `rebuild_slides.py` (see
[docs/USAGE.md](docs/USAGE.md)).

## Testing
```bash
python3 -m pytest
```
