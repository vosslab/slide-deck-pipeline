# Lecture merge guide

## Goal
- Combine multiple PPTX decks into a single, ordered lecture deck using CSV
  exports as the sorting and selection surface.
- Work like an educator: curate the narrative flow first, then refine layout and
  text placement.

## Quick workflow summary
- Place source PPTX files in the repo root.
- Run `index_slide_deck.py` on each PPTX to generate per-deck CSVs.
- Merge the CSV rows into one file and sort by a column that matches your
  teaching goal.
- Edit `master_name` and `layout_type` to select the target template styling.
- Rebuild a merged PPTX with `rebuild_slides.py`.
- Repeat until the lecture flow reads well.

## Scripts you will use
- `index_slide_deck.py` indexes each PPTX into a CSV.
- `validate_csv.py` checks CSV format, source availability, and hash integrity.
- `rebuild_slides.py` builds a new PPTX from the merged CSV.
- `test_script.sh` runs the full pipeline over all root-level PPTX files.

## Step 1: Index each source deck
Run this for each deck you want to merge.

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 index_slide_deck.py \
  -i lecture01-chap44.pptx

/opt/homebrew/opt/python@3.12/bin/python3.12 index_slide_deck.py \
  -i lecture03-chap52.pptx
```

Each command writes a CSV with the same basename as the PPTX.

## Step 2: Read the CSV columns
The CSV is the sorting surface. It is not a design tool. Only two columns are
editable.

| Column | Description | Editable |
| --- | --- | --- |
| source_pptx | Source PPTX basename. | NO |
| source_slide_index | Slide index (1-based). | NO |
| slide_hash | Slide content fingerprint. | NO |
| master_name | Template master name for styling. | YES |
| layout_type | Semantic layout type selector. | YES |
| asset_types | Context tag for images/tables/charts/media. Let this guide sorting. | NO |
| title_text | Context text for the title box. | NO |
| body_text | Context text for the body box. | NO |
| notes_text | Speaker notes text. | NO |

Notes:
- The context text is sanitized to remove commas and newlines so it stays
  single-line in CSV.
- Layout classification may be imperfect. Editing `layout_type` is your manual
  override.

## Step 3: Merge and sort CSV rows
When you combine multiple CSV files, remove repeated headers and then sort the
rows by a column that aligns with your lecture flow.

Optional: use the merge helper to handle globs and sorting in one step.

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 merge_index_csv_files.py \
  -i *.csv --sort-by source_slide_index -o merged.csv
```

Minimal merge example:

```bash
cat lecture01-chap44.csv lecture03-chap52.csv \
  | grep -v '^source_pptx' \
  | sort -t, -k7,7 \
  > merged_body.csv

head -n 1 lecture01-chap44.csv > header.csv
cat header.csv merged_body.csv > merged.csv
```

The `-k7,7` choice sorts by `title_text`. Use a different column if needed.

## Sorting strategies for educators
Pick a sorting key based on how you want to teach.

### Sort by title_text for narrative flow
Use this when you want a chronological storyline.

```bash
sort -t, -k7,7 merged_body.csv > merged_body.csv
```

### Sort by body_text to group similar explanations
Use this to cluster similar paragraphs or definitions.

```bash
sort -t, -k8,8 merged_body.csv > merged_body.csv
```

### Sort by asset_types to isolate visual slides
Use this to separate image-heavy slides for demos or labs.

```bash
sort -t, -k6,6 merged_body.csv > merged_body.csv
```

### Sort by layout_type to group slide types
Use this to batch your edits by layout choice.

```bash
sort -t, -k5,5 merged_body.csv > merged_body.csv
```

### Sort by source_pptx to keep chapters together
Use this when you want to preserve source order.

```bash
sort -t, -k1,1 -k2,2n merged_body.csv > merged_body.csv
```

## Step 4: Edit master_name and layout_type
Think of `layout_type` as your lecture flow tool:
- Set all intro slides to `title_slide`.
- Use `title_content` for most teaching slides.
- Use `two_content` for comparisons.
- Use `blank` or `custom` only when needed.

`master_name` controls the visual style. Use it to switch between light/dark or
branded templates.

Example edit:

```
lecture01-chap44.pptx,26,4288d77838cb175e,custom,title_content,image,Abiotic Factors,Abiotic factors affect distribution,
```

If you change `layout_type`, rebuild will use the template layout for that
master and layout type. It will not change slide text unless you do it in the
source deck or a text patch.

## Step 5: Validate and rebuild
Run validation before rebuild if you are doing major edits.

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 validate_csv.py \
  -i merged.csv -t template.pptx -S
```

Rebuild the merged deck:

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 rebuild_slides.py \
  -i merged.csv -o lecture_merged.pptx
```

## Using test_script.sh for a full pipeline pass
This script indexes all root-level PPTX files, merges their CSVs, and rebuilds
`super.pptx`. It also normalizes `master_name` to a single value.

```bash
./test_script.sh
```

Adjust the script for your lecture:
- `SORT_COLUMN` sets the CSV column number used for sorting.
- Set `MASTER_NAME` to force a single master for all slides.
- Replace or remove the hard-coded `grep` filter if you do not want topic
  filtering.

## Example: build a mixed lecture
Goal: Create a single lecture on ecology by blending two chapter decks.

1) Index both decks.

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 index_slide_deck.py \
  -i lecture01-chap44.pptx
/opt/homebrew/opt/python@3.12/bin/python3.12 index_slide_deck.py \
  -i lecture03-chap52.pptx
```

2) Merge and sort by title_text for narrative flow.

```bash
cat lecture01-chap44.csv lecture03-chap52.csv \
  | grep -v '^source_pptx' \
  | sort -t, -k7,7 \
  > merged_body.csv
head -n 1 lecture01-chap44.csv > header.csv
cat header.csv merged_body.csv > merged.csv
```

3) Edit `layout_type` for consistent layouts.

```text
lecture01-chap44.pptx,26,4288d77838cb175e,custom,title_content,image,Abiotic Factors,Abiotic factors affect distribution,
lecture03-chap52.pptx,12,abf8a67e307e149f,custom,title_content,image,Abiotic Factors,Abiotic factors affect distribution,
```

4) Rebuild the merged lecture.

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 rebuild_slides.py \
  -i merged.csv -o ecology_lecture.pptx
```

## Tips for strong lecture flow
- Use `title_text` to identify the arc of the lecture, then group related
  slides by `title_text` or `body_text`.
- Use `asset_types` to cluster high-visual slides for demos or labs.
- Keep `layout_type` consistent within a topic block to reduce visual jitter.
- Use `notes_text` to select slides that already include teaching prompts.

## Related docs
- [docs/USAGE.md](docs/USAGE.md)
- [docs/TEMPLATE_LAYOUT_PLAN.md](docs/TEMPLATE_LAYOUT_PLAN.md)
