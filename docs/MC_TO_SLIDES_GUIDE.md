# MC to slides guide

## Goal
- Generate an interactive multiple choice slide deck from quiz text with one
  question per slide and a click-to-reveal answer popup.

## Quick workflow summary
- Prepare the template source with the required popup animation.
- Write the quiz text file.
- Render the deck with `mc_to_slides.py`.
- Review the summary counts and warnings.

## Script you will use
- `mc_to_slides.py` renders a PPTX from quiz text and the template source.

## Step 1: Prepare the template source
The tool expects an unpacked PPTX directory at:
- `template_src/MC_TO_SLIDES_template/` (preferred)
- `templates_src/MC_TO_SLIDES_template/` (fallback)

The template slide must contain:
- A question text box.
- An options text box.
- A hidden answer popup text box with a click-to-reveal animation.

Recommended shape names:
- `MC_QUESTION`
- `MC_OPTIONS`
- `MC_ANSWER_POPUP`

If these names are missing, the tool tries to fall back to the animation target
or placeholders and emits warnings. If it cannot identify all three shapes, the
run fails.

## Step 2: Write quiz text
Single-answer example:

```text
1. What is 2+3?
a) 6
b) 1
*c) 5
```

Multiple-answer example:

```text
1. Which of the following are dinosaurs?
[ ] Woolly mammoth
[*] Tyrannosaurus rex
[*] Triceratops
[ ] Smilodon fatalis
```

Optional feedback lines start with `...` and appear in the answer popup.

## Step 3: Render the deck
```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 mc_to_slides.py \
  -i quiz.txt \
  -o quiz.pptx
```

Optional flags:
- `--strict` to treat invalid questions as errors.
- `--preserve-newlines` to keep original line breaks in prompt and feedback
  text.

## Step 4: Review the summary
The script reports:
- Questions parsed.
- Slides generated.
- Questions skipped (with warnings).

## Related docs
- [docs/MC_TO_SLIDES.md](docs/MC_TO_SLIDES.md)
- [docs/USAGE.md](docs/USAGE.md)
