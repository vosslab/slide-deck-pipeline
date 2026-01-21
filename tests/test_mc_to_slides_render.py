import pathlib

import pytest

pptx = pytest.importorskip("pptx")

import slide_deck_pipeline.mc_parser as mc_parser
import slide_deck_pipeline.mc_to_slides as mc_to_slides
import slide_deck_pipeline.pptx_text as pptx_text

assert pptx


#============================================
def test_render_mc_deck(tmp_path: pathlib.Path) -> None:
	"""
	Render a small MC deck from text.
	"""
	content = "\n".join(
		[
			"1. What is 2+3?",
			"a) 4",
			"*b) 5",
			"2. Pick dinosaurs.",
			"[*] Triceratops",
			"[ ] Mammoth",
		]
	)
	questions, warnings, stats = mc_parser.parse_questions(content, strict=False)
	assert warnings == []
	assert stats["skipped_questions"] == 0
	output_path = tmp_path / "quiz.pptx"
	mc_to_slides.render_questions_to_pptx(
		questions,
		str(output_path),
		preserve_newlines=False,
	)
	presentation = pptx.Presentation(str(output_path))
	assert len(presentation.slides) == 2
	slide_text = pptx_text.extract_slide_text(presentation.slides[0])
	assert "What is 2+3?" in slide_text
	assert "A) 4" in slide_text
	assert "Answer: B" in slide_text
	second_text = pptx_text.extract_slide_text(presentation.slides[1])
	assert "Pick dinosaurs." in second_text
	assert "[ ] Triceratops" in second_text
	assert "Answer: A" in second_text
