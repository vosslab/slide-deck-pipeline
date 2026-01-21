# MC to slides plan

## Purpose
- Generate an interactive multiple choice slide deck from instructor-authored
  quiz text.
- The output deck is designed for in-class use, with one question per slide and
  an answer popup revealed on click.

## Goals
- Use a single, instructor-friendly plain text input format.
- Keep parsing and slide output deterministic.
- Generate one slide per question.
- Preserve a click-to-reveal answer popup from a template slide.
- Keep the CLI python script thin and put logic in `slide_deck_pipeline/`.

## Non-goals
- Do not support free-form layout selection.
- Do not generate or edit PPTX animations in code.
- Do not support non-multiple-choice question types (essay, numerical,
  fill-in-the-blank, file upload).
- Do not attempt to style master slides; use the template as-is.

## Terms
- Question file: the input plain text quiz file.
- Template source: the unpacked PPTX package directory under
  `templates_src/`.
- Packed template: a generated PPTX created at runtime from the template
  source.
- Popup answer: a hidden answer text box that appears via click animation.

## Input format (text2qti-style quiz text)
This tool supports a strict subset of the text2qti text format.

### Supported question styles
Single-answer multiple choice:

```text
1. What is 2+3?
a) 6
b) 1
*c) 5
```

Optional question title and feedback:

```text
Title: An addition question
1. What is 2+3?
... General question feedback.
a) 6
b) 1
*c) 5
```

Multiple-answer questions (checkbox style):

```text
1. Which of the following are dinosaurs?
[ ] Woolly mammoth
[*] Tyrannosaurus rex
[*] Triceratops
[ ] Smilodon fatalis
```

### Parsing rules
- A question begins with a number prefix at column 0: `N.` where N is an
  integer.
  - The question number can optionally be stripped from the question during slide creation
- The question prompt is the remainder of that line plus any continuation lines
  until the first answer choice.
- Answer choices are either:
  - Lettered choices: `a)`, `b)`, `c)`, ...
  - Checkbox choices: `[ ]` and `[*]`
- Correct answers are marked with a leading `*` for lettered choices or `[*]`
  for checkbox choices.
- Optional title line: `Title: ...` applies to the next question only.
- Optional feedback lines begin with `...` and are included in the answer
  popup.

## Validation requirements
A parsed question is valid only if:
- It has at least 2 answer choices.
- Single-answer questions have exactly 1 correct answer.
- Multiple-answer questions have at least 1 correct answer.
- Answer choice labels are consistent within a question (do not mix `a)` and
  `[ ]`).

Invalid questions are skipped with a warning and recorded in the summary.
In `--strict` mode, any invalid question aborts the run with a non-zero exit.

## Output format
Output is a PPTX deck.

### Slide structure
- One slide per question.
- Each slide contains:
  - Question prompt
  - Answer choices
  - Hidden popup answer box (revealed on click)

### Answer popup content
Single-answer:

```text
Answer: C
<feedback if present>
```

Multiple-answer:

```text
Answers: B, D
<feedback if present>
```

## Template requirement (popup animation)
This tool does not generate animations in code. It uses a pre-authored slide
with an animation that reveals the answer popup on click.

### Template source location (committed)
- `templates_src/mc_popup_template/`

### Packed template behavior (not committed)
- The tool packs the template source into a temporary PPTX at runtime.
- Packed template artifacts are build outputs and must not be committed.

## Required template slide contract
The template must contain at least one slide that provides:
- A visible question text box
- A visible options text box
- A hidden answer popup text box with an entrance animation (on click)

The template slide must include deterministic addressing for these shapes.

### Required shape names (recommended and enforced)
- `MC_QUESTION`
- `MC_OPTIONS`
- `MC_ANSWER_POPUP`

If any shape name is missing, the run fails with an error because the template
is a hard dependency.

### Animation requirement
- `MC_ANSWER_POPUP` must have an entrance animation that reveals it on click.
- The tool preserves animation by cloning the template slide and replacing
  text.

## Rendering algorithm
For each parsed question:
1. Clone the template slide that contains the popup animation.
2. Replace text in `MC_QUESTION` with the prompt text.
3. Replace text in `MC_OPTIONS` with the formatted options list.
4. Replace text in `MC_ANSWER_POPUP` with:
   - `Answer: X` or `Answers: X, Y`
   - followed by feedback lines if present
5. Append the slide to the output deck.

## Formatting rules
- Preserve template text formatting (fonts, sizes, colors) as much as possible.
- Do not restyle in code.
- Options are rendered as one line per option in display order.
- Lettered questions display as `A) ...`, `B) ...`.
- Checkbox questions display as `[ ] ...` for all options.
- Correctness is only revealed via the popup.

## Text normalization
- By default, prompt and option text is normalized for slide rendering:
  - Replace newlines and tabs with spaces.
  - Collapse multiple spaces.
  - Trim leading and trailing whitespace.
- Feedback lines in the answer popup are kept as separate lines by default.
- Optional flag `--preserve-newlines` keeps original line breaks in prompt and
  feedback text.

## CLI design
### mc_to_slides.py
Usage:
- `./mc_to_slides.py -i quiz.txt -o quiz.pptx`
- `python3 mc_to_slides.py -i quiz.txt`

Flags:
- `-i`, `--input`: quiz text file (required)
- `-o`, `--output`: output PPTX file (optional; defaults to input basename with
  `.pptx`)
- `--strict`: treat invalid questions as errors
- `--preserve-newlines`: keep original line breaks in prompt and feedback text

## Reporting
At minimum, print:
- Number of questions parsed
- Number of slides generated
- Number of questions skipped, with reasons

Optional (future) report file:
- Write a small CSV or JSON summary of question ids, correct answers, and slide
  numbers.

## Code organization
Entrypoint script (thin orchestrator):
- `mc_to_slides.py`
  - Parse args
  - Load input text
  - Call worker modules
  - Write PPTX
  - Print summary

Worker modules (logic lives in `slide_deck_pipeline/`):
- `slide_deck_pipeline/mc_parser.py`
  - Parse question file into a normalized question model
- `slide_deck_pipeline/mc_template.py`
  - Pack `templates_src/mc_popup_template/` into a temporary PPTX
  - Load the packed template
  - Locate required named shapes
- `slide_deck_pipeline/mc_to_slides.py`
  - Clone template slide per question
  - Replace text in named shapes
  - Return output presentation object
- `slide_deck_pipeline/reporting.py`
  - Warnings and summary formatting

## Testing plan
Unit tests:
- Parse single-answer question blocks.
- Parse multiple-answer checkbox blocks.
- Skip invalid questions with warnings in default mode.
- Reject invalid questions in strict mode.
- Normalize prompt continuation lines by default.
- Preserve prompt continuation lines with `--preserve-newlines`.
- Extract and preserve feedback lines.

Template tests:
- Verify the template source packs into a valid PPTX.
- Verify required shape names exist.
- Verify the template slide contains timing XML for animations (presence
  check).

Integration tests:
- Convert a small quiz file into PPTX.
- Verify:
  - Slide count equals question count
  - Extracted text includes question and options
  - Answer popup text exists on each slide
