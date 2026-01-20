# Install

Install means having Python 3 available with the required modules so the root
CLI scripts can run, plus LibreOffice if you plan to convert ODP files.

## Requirements
- Python 3 (exact version not specified in repo).
- `python-pptx` (imported as `pptx` in [extract_slides.py](extract_slides.py) and
  [rebuild_slides.py](rebuild_slides.py)).
- LibreOffice `soffice` binary for ODP conversion.

## Install steps
- Clone the repo.
- Install Python dependencies once a dependency manifest is defined.
- Install LibreOffice if you need ODP input or output.

## Verify install
```bash
python3 extract_slides.py --help
```

## Known gaps
- TODO: Add a dependency manifest (for example `pip_requirements.txt`).
- TODO: Confirm the supported Python version for users.
- TODO: Confirm whether a virtual environment name or setup workflow is expected.
