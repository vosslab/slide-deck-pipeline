# Standard Library
import re


QUESTION_RE = re.compile(r"^([0-9]+)\.\s*(.*)$")
LETTER_CHOICE_RE = re.compile(r"^(\*?)([A-Za-z])\)\s*(.*)$")
CHECKBOX_CHOICE_RE = re.compile(r"^\[\s*(\*?)\s*\]\s*(.*)$")


#============================================
def parse_questions(
	text: str,
	strict: bool,
) -> tuple[list[dict[str, object]], list[str], dict[str, int]]:
	"""
	Parse a multiple choice question file.

	Args:
		text: Input text content.
		strict: Treat invalid questions as errors.

	Returns:
		tuple[list[dict[str, object]], list[str], dict[str, int]]: Questions,
		warnings, and stats.
	"""
	warnings: list[str] = []
	questions: list[dict[str, object]] = []
	stats = {
		"total_questions": 0,
		"skipped_questions": 0,
	}
	current = None
	pending_title = ""
	for line_number, raw_line in enumerate(text.splitlines(), 1):
		line = raw_line.rstrip()
		if not line.strip():
			continue
		if current is None:
			title = parse_title_line(line)
			if title is not None:
				pending_title = title
				continue
			match = QUESTION_RE.match(line)
			if match:
				current = start_question(match, line_number, pending_title)
				pending_title = ""
				continue
			warnings.append(
				f"Line {line_number}: ignoring content before first question."
			)
			continue
		match = QUESTION_RE.match(line)
		if match:
			finish_question(current, questions, warnings, stats, strict)
			current = start_question(match, line_number, pending_title)
			pending_title = ""
			continue
		title = parse_title_line(line)
		if title is not None and not current.get("choices_started", False):
			current["title"] = title
			continue
		if line.startswith("..."):
			feedback = line[3:].lstrip()
			current["feedback_lines"].append(feedback)
			continue
		if parse_choice_line(line, current):
			continue
		if current.get("choices_started", False):
			warnings.append(
				f"Line {line_number}: ignoring unexpected line after choices."
			)
			continue
		current["prompt_lines"].append(line.strip())
	if current is not None:
		finish_question(current, questions, warnings, stats, strict)
	return (questions, warnings, stats)


#============================================
def parse_title_line(line: str) -> str | None:
	"""
	Parse a Title: line when present.

	Args:
		line: Input line.

	Returns:
		str | None: Title text or None if not a title line.
	"""
	if not line.startswith("Title:"):
		return None
	return line[len("Title:"):].strip()


#============================================
def start_question(
	match: re.Match,
	line_number: int,
	pending_title: str,
) -> dict[str, object]:
	"""
	Start a new question record.

	Args:
		match: Question regex match.
		line_number: Line number for the question start.
		pending_title: Optional title to apply.

	Returns:
		dict[str, object]: New question record.
	"""
	number_text = match.group(1)
	prompt = match.group(2).strip()
	record = {
		"number": int(number_text),
		"line_number": line_number,
		"title": pending_title or "",
		"prompt_lines": [prompt] if prompt else [],
		"options": [],
		"style": "",
		"errors": [],
		"choices_started": False,
		"feedback_lines": [],
	}
	return record


#============================================
def parse_choice_line(line: str, current: dict[str, object]) -> bool:
	"""
	Parse an answer choice line into the current question.

	Args:
		line: Input line.
		current: Current question record.

	Returns:
		bool: True if a choice line was parsed.
	"""
	letter_match = LETTER_CHOICE_RE.match(line)
	if letter_match:
		mark = letter_match.group(1)
		label = letter_match.group(2)
		text = letter_match.group(3).strip()
		return add_choice(current, "lettered", label, text, bool(mark))
	check_match = CHECKBOX_CHOICE_RE.match(line)
	if check_match:
		mark = check_match.group(1)
		text = check_match.group(2).strip()
		return add_choice(current, "checkbox", "", text, bool(mark))
	return False


#============================================
def add_choice(
	current: dict[str, object],
	style: str,
	label: str,
	text: str,
	correct: bool,
) -> bool:
	"""
	Add a choice to the current question.

	Args:
		current: Current question record.
		style: Choice style ("lettered" or "checkbox").
		label: Choice label (for lettered).
		text: Choice text.
		correct: True if marked correct.

	Returns:
		bool: True when a choice is added.
	"""
	current["choices_started"] = True
	current_style = current.get("style", "")
	if current_style and current_style != style:
		current["errors"].append("Mixed choice label styles.")
		return True
	if not current_style:
		current["style"] = style
	current["options"].append(
		{"label": label, "text": text, "correct": correct}
	)
	return True


#============================================
def finish_question(
	current: dict[str, object],
	questions: list[dict[str, object]],
	warnings: list[str],
	stats: dict[str, int],
	strict: bool,
) -> None:
	"""
	Validate and store a parsed question.

	Args:
		current: Current question record.
		questions: Output question list.
		warnings: Warning list to append to.
		strict: Treat invalid questions as errors.
	"""
	stats["total_questions"] += 1
	errors = list(current.get("errors", []))
	options = list(current.get("options", []))
	if len(options) < 2:
		errors.append("Fewer than two answer choices.")
	style = current.get("style", "")
	correct_count = sum(1 for option in options if option.get("correct"))
	if style == "lettered":
		if correct_count != 1:
			errors.append("Single-answer question must have exactly one correct.")
	if style == "checkbox":
		if correct_count < 1:
			errors.append("Multiple-answer question must have at least one correct.")
	if not style:
		errors.append("No answer choices found.")
	if errors:
		message = format_question_error(current, errors)
		if strict:
			raise ValueError(message)
		warnings.append(message)
		stats["skipped_questions"] += 1
		return
	if style == "checkbox":
		assign_checkbox_labels(options)
	questions.append(current)


#============================================
def assign_checkbox_labels(options: list[dict[str, object]]) -> None:
	"""
	Assign letter labels to checkbox options by order.

	Args:
		options: Option list to modify in place.
	"""
	for index, option in enumerate(options):
		label = chr(ord("A") + index)
		option["label"] = label


#============================================
def format_question_error(current: dict[str, object], errors: list[str]) -> str:
	"""
	Format an invalid question error message.

	Args:
		current: Question record.
		errors: Error strings.

	Returns:
		str: Combined warning message.
	"""
	number = current.get("number", "?")
	line_number = current.get("line_number", "?")
	detail = "; ".join(errors)
	return f"Question {number} (line {line_number}): {detail}"
