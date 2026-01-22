# File structure

## Top-level layout
- [AGENTS.md](AGENTS.md): agent instructions and workflow guardrails.
- [README.md](README.md): project overview and doc links.
- [slide_deck_pipeline/](slide_deck_pipeline/): shared modules used by CLI scripts.
- [slide_deck_pipeline/csv_schema.py](slide_deck_pipeline/csv_schema.py): CSV
  schema and hashing utilities.
- [slide_deck_pipeline/csv_validation.py](slide_deck_pipeline/csv_validation.py):
  CSV validation helpers shared by the CLI.
- [slide_deck_pipeline/layout_classifier.py](slide_deck_pipeline/layout_classifier.py):
  semantic layout classification helpers.
- [slide_deck_pipeline/pptx_hash.py](slide_deck_pipeline/pptx_hash.py): slide
  hashing helpers including relationship normalization.
- [slide_deck_pipeline/pptx_text.py](slide_deck_pipeline/pptx_text.py): slide
  text extraction helpers.
- [slide_deck_pipeline/text_boxes.py](slide_deck_pipeline/text_boxes.py): text
  box mapping helpers for text edit patches.
- [slide_deck_pipeline/text_editing.py](slide_deck_pipeline/text_editing.py):
  text edit workflow helpers.
- [slide_deck_pipeline/text_export.py](slide_deck_pipeline/text_export.py):
  text export workflow helpers.
- [slide_deck_pipeline/text_to_slides.py](slide_deck_pipeline/text_to_slides.py):
  text-to-slides rendering helpers.
- [slide_deck_pipeline/mc_to_slides.py](slide_deck_pipeline/mc_to_slides.py):
  quiz slide rendering helpers.
- [slide_deck_pipeline/aspect_fixer.py](slide_deck_pipeline/aspect_fixer.py):
  picture aspect ratio fixer helpers.
- [slide_deck_pipeline/text_overflow_fixer.py](slide_deck_pipeline/text_overflow_fixer.py):
  text overflow fixer helpers (enable shrink text on overflow).
- [slide_deck_pipeline/image_utils.py](slide_deck_pipeline/image_utils.py):
  picture sizing and fitting helpers.
- [index_slide_deck.py](index_slide_deck.py): index slides to CSV.
- [merge_index_csv_files.py](merge_index_csv_files.py): merge slide index CSVs.
- [rebuild_slides.py](rebuild_slides.py): rebuild slides from merged CSV.
- [validate_csv.py](validate_csv.py): validate merged CSVs and source references.
- [export_slide_text.py](export_slide_text.py): export text edit patches.
- [apply_text_edits.py](apply_text_edits.py): apply text edit patches.
- [aspect_fixer.py](aspect_fixer.py): fix picture aspect ratios in PPTX or ODP.
- [shrink_text_on_overflow.py](shrink_text_on_overflow.py): enable shrink text on overflow for all text boxes in PPTX or ODP.
- [md_to_slides_yaml.py](md_to_slides_yaml.py): convert Markdown to YAML specs.
- [text_to_slides.py](text_to_slides.py): render PPTX from YAML specs.
- [mc_to_slides.py](mc_to_slides.py): render quiz decks from text files.
- [MC_TO_SLIDES_template.pptx](MC_TO_SLIDES_template.pptx): quiz template PPTX source.
- [MC_TO_SLIDES_template.odp](MC_TO_SLIDES_template.odp): quiz template ODP source.
- [template_src/](template_src/): unpacked PPTX templates used at runtime.
- [Brewfile](Brewfile): Homebrew dependency manifest.
- [docs/](docs/): repository documentation.
- [pip_requirements.txt](pip_requirements.txt): Python runtime dependencies.
- [pip_requirements-dev.txt](pip_requirements-dev.txt): Python dev/test dependencies.
- [tests/](tests/): repo hygiene checks and unit tests.
- [devel/](devel/): developer helper scripts.
- [test_script.sh](test_script.sh): lecture merge pipeline helper script.
- [LICENSE](LICENSE): license terms.

## Key subtrees
- [docs/](docs/): documentation and style guides.
- [tests/](tests/): pytest-based checks, including lint and formatting rules.
- [devel/](devel/): helper scripts such as changelog tooling.
- [template_src/](template_src/): unpacked template PPTX sources, including MC.

## Generated artifacts
- [report_pyflakes.txt](report_pyflakes.txt),
  [report_shebang.txt](report_shebang.txt),
  [report_ascii_compliance.txt](report_ascii_compliance.txt),
  [report_bandit.txt](report_bandit.txt),
  [report_pyright.txt](report_pyright.txt) are generated test reports.
- [.pytest_cache/](.pytest_cache/): pytest cache data.
- [.DS_Store](.DS_Store) is a local macOS artifact.

## Documentation map
- Root docs: [README.md](README.md), [AGENTS.md](AGENTS.md), [LICENSE](LICENSE).
- Core docs: [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md),
  [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md),
  [docs/CONCEPT_IMPLEMENTATION_PLAN.md](docs/CONCEPT_IMPLEMENTATION_PLAN.md),
  [docs/INSTALL.md](docs/INSTALL.md),
  [docs/USAGE.md](docs/USAGE.md),
  [docs/LECTURE_MERGE_GUIDE.md](docs/LECTURE_MERGE_GUIDE.md),
  [docs/TEXT_EDIT_PIPELINE_GUIDE.md](docs/TEXT_EDIT_PIPELINE_GUIDE.md),
  [docs/TEXT_TO_SLIDES_GUIDE.md](docs/TEXT_TO_SLIDES_GUIDE.md),
  [docs/MC_TO_SLIDES_GUIDE.md](docs/MC_TO_SLIDES_GUIDE.md),
  [docs/TEXT_EDITING_PLAN.md](docs/TEXT_EDITING_PLAN.md),
  [docs/TEXT_TO_SLIDES_PLAN.md](docs/TEXT_TO_SLIDES_PLAN.md),
  [docs/MC_TO_SLIDES.md](docs/MC_TO_SLIDES.md),
  [docs/TEMPLATE_LAYOUT_PLAN.md](docs/TEMPLATE_LAYOUT_PLAN.md),
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
