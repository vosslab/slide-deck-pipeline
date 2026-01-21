# File structure

## Top-level layout
- [AGENTS.md](AGENTS.md): agent instructions and workflow guardrails.
- [README.md](README.md): project overview and doc links.
- [slide_deck_pipeline/](slide_deck_pipeline/): shared modules used by CLI scripts.
- [slide_deck_pipeline/csv_schema.py](slide_deck_pipeline/csv_schema.py): CSV
  schema and hashing utilities.
- [slide_deck_pipeline/pptx_text.py](slide_deck_pipeline/pptx_text.py): slide
  text extraction helpers.
- [slide_deck_pipeline/text_boxes.py](slide_deck_pipeline/text_boxes.py): text
  box mapping helpers for text edit patches.
- [index_slide_deck.py](index_slide_deck.py): index slides to CSV.
- [rebuild_slides.py](rebuild_slides.py): rebuild slides from merged CSV.
- [validate_csv.py](validate_csv.py): validate merged CSVs and source references.
- [export_slide_text.py](export_slide_text.py): export text edit patches.
- [apply_text_edits.py](apply_text_edits.py): apply text edit patches.
- [docs/](docs/): repository documentation.
- [tests/](tests/): repo hygiene checks and unit tests.
- [devel/](devel/): developer helper scripts.
- [LICENSE](LICENSE): license terms.

## Key subtrees
- [docs/](docs/): documentation and style guides.
- [tests/](tests/): pytest-based checks, including lint and formatting rules.
- [devel/](devel/): helper scripts such as changelog tooling.

## Generated artifacts
- [report_pyflakes.txt](report_pyflakes.txt),
  [report_shebang.txt](report_shebang.txt),
  [report_ascii_compliance.txt](report_ascii_compliance.txt),
  [report_bandit.txt](report_bandit.txt),
  [report_pyright.txt](report_pyright.txt) are generated test reports.
- [.DS_Store](.DS_Store) is a local macOS artifact.

## Documentation map
- Root docs: [README.md](README.md), [AGENTS.md](AGENTS.md), [LICENSE](LICENSE).
- Core docs: [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md),
  [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md),
  [docs/CONCEPT_IMPLEMENTATION_PLAN.md](docs/CONCEPT_IMPLEMENTATION_PLAN.md),
  [docs/INSTALL.md](docs/INSTALL.md),
  [docs/USAGE.md](docs/USAGE.md),
  [docs/NEWS.md](docs/NEWS.md),
  [docs/RELATED_PROJECTS.md](docs/RELATED_PROJECTS.md),
  [docs/RELEASE_HISTORY.md](docs/RELEASE_HISTORY.md),
  [docs/ROADMAP.md](docs/ROADMAP.md),
  [docs/TODO.md](docs/TODO.md),
  [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
- Style guides: [docs/MARKDOWN_STYLE.md](docs/MARKDOWN_STYLE.md),
  [docs/PYTHON_STYLE.md](docs/PYTHON_STYLE.md),
  [docs/REPO_STYLE.md](docs/REPO_STYLE.md).

## Where to add new work
- Add new scripts at the repo root to keep tooling simple.
- Add tests under [tests/](tests/) with `test_*.py`.
- Add docs under [docs/](docs/) using SCREAMING_SNAKE_CASE names.
