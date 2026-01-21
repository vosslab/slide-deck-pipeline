import pathlib

import pytest

pptx = pytest.importorskip("pptx")

import slide_deck_pipeline.pptx_text as pptx_text
import slide_deck_pipeline.text_to_slides as text_to_slides

assert pptx


#============================================
def test_render_default_layout(tmp_path: pathlib.Path) -> None:
	"""
	Render a simple deck using default layouts.
	"""
	spec_path = tmp_path / "spec.yaml"
	spec_path.write_text("version: 1\nslides: []\n", encoding="utf-8")
	output_path = tmp_path / "output.pptx"
	spec = {
		"version": 1,
		"template_deck": None,
		"defaults": {"layout_type": "title_content", "master_name": None},
		"slides": [
			{
				"layout_type": "title_content",
				"title": "Hello",
				"subtitle": None,
				"bodies": [{"bullets": ["Point one"]}],
				"image": None,
				"images": None,
			}
		],
	}
	text_to_slides.render_to_pptx(
		spec,
		str(spec_path),
		None,
		str(output_path),
		strict=False,
	)
	presentation = pptx.Presentation(str(output_path))
	assert len(presentation.slides) == 1
	slide = presentation.slides[0]
	assert slide.shapes.title.text == "Hello"
	body_text = pptx_text.extract_body_text(slide)
	assert "Point one" in body_text
