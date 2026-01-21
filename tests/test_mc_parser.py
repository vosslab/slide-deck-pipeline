import pytest

import slide_deck_pipeline.mc_parser as mc_parser


#============================================
def test_parse_single_answer() -> None:
	"""
	Parse a simple single-answer question.
	"""
	content = "\n".join(
		[
			"1. What is 2+3?",
			"a) 4",
			"*b) 5",
		]
	)
	questions, warnings, stats = mc_parser.parse_questions(content, strict=False)
	assert warnings == []
	assert stats["total_questions"] == 1
	assert stats["skipped_questions"] == 0
	assert len(questions) == 1
	question = questions[0]
	assert question["style"] == "lettered"
	options = question["options"]
	assert len(options) == 2
	assert options[0]["correct"] is False
	assert options[1]["correct"] is True


#============================================
def test_parse_checkbox_question() -> None:
	"""
	Parse a checkbox-style question.
	"""
	content = "\n".join(
		[
			"1. Pick dinosaurs.",
			"[*] Triceratops",
			"[ ] Mammoth",
		]
	)
	questions, warnings, stats = mc_parser.parse_questions(content, strict=False)
	assert warnings == []
	assert stats["total_questions"] == 1
	assert stats["skipped_questions"] == 0
	question = questions[0]
	assert question["style"] == "checkbox"
	options = question["options"]
	assert options[0]["label"] == "A"
	assert options[1]["label"] == "B"
	assert options[0]["correct"] is True


#============================================
def test_prompt_continuation_lines() -> None:
	"""
	Preserve prompt continuation lines.
	"""
	content = "\n".join(
		[
			"1. First line",
			"Second line",
			"*a) Yes",
			"b) No",
		]
	)
	questions, _, _ = mc_parser.parse_questions(content, strict=False)
	question = questions[0]
	assert question["prompt_lines"] == ["First line", "Second line"]


#============================================
def test_strict_rejects_invalid() -> None:
	"""
	Reject invalid questions in strict mode.
	"""
	content = "\n".join(
		[
			"1. Missing correct",
			"a) One",
			"b) Two",
		]
	)
	with pytest.raises(ValueError):
		mc_parser.parse_questions(content, strict=True)
