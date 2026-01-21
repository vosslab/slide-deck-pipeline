# Install

Install means having Python 3 available with the required modules so the root
CLI scripts can run, plus LibreOffice if you plan to convert ODP files.

## Requirements
- Python 3.12 (see [Brewfile](Brewfile)).
- `python-pptx`, `PyYAML`, and `lxml` (see [pip_requirements.txt](pip_requirements.txt)).
- LibreOffice `soffice` binary for ODP conversion (see [Brewfile](Brewfile)).

## Install steps
- Clone the repo.
- Install Python dependencies with `pip install -r pip_requirements.txt`.
- Install Homebrew dependencies with `brew bundle`.

## Verify install
```bash
python3 index_slide_deck.py --help
```

## Known gaps
- TODO: Confirm whether a virtual environment name or setup workflow is expected.
