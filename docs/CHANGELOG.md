# Changelog

## 2026-01-20
- Added the concept implementation plan document.
- Updated the plan to reflect CSV-only merging and ODP conversion support.
- Added initial indexing/rebuild scripts and shared CSV utilities.
- Added slide CSV unit tests.
- Added architecture and file structure documentation.
- Linked architecture docs from the README.
- Added install and usage documentation stubs.
- Added non-IO unit tests for index and rebuild helpers.
- Skipped tests for commit_changelog due to subprocess and git usage.
- Added docset stubs for news, related projects, release history, roadmap, todo,
  and troubleshooting.
- Updated the documentation map to include the new docs.
- Refreshed the README structure and doc links.
- Clarified the README overview audience.
- Added a merged CSV validation script and tests.
- Documented the validation CLI in usage docs and file structure.
- Switched to CSV indexing without exported assets and removed assets-dir usage.
- Defaulted index/rebuild outputs to input filenames with new extensions.
- Renamed the index script and updated docs to match index-only behavior.
- Added image locators to the CSV schema and rebuild resolution logic.
- Updated architecture, usage, and concept docs to reflect locator-based rebuilds.
- Renamed `extract_slides.py` to `index_slide_deck.py`.
- Added shebangs to CLI scripts and fixed ODP source conversion in rebuild.
- Added a theme and layout planning document.
