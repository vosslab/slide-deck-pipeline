import pytest

import slide_deck_pipeline.md_to_slides_yaml as md_to_slides_yaml


#============================================
def test_parse_markdown_basic() -> None:
	"""
	Parse a simple Markdown deck.
	"""
	content = "\n".join(
		[
			"# Title Slide",
			"# Intro",
			"## Subtitle here",
			"---",
			"# Title Content",
			"# Main Topic",
			"- Point one",
			"- Point two",
			"---",
			"# Centered Text",
			"- Practice",
			"---",
			"# Blank",
		]
	)
	spec = md_to_slides_yaml.parse_markdown(content)
	assert spec["version"] == 1
	assert len(spec["slides"]) == 4
	assert spec["slides"][0]["layout_type"] == "title_slide"
	assert spec["slides"][1]["layout_type"] == "title_content"
	assert spec["slides"][2]["layout_type"] == "centered_text"
	assert spec["slides"][3]["layout_type"] == "blank"


#============================================
def test_parse_markdown_blank_rejects_content() -> None:
	"""
	Reject content inside a blank slide.
	"""
	content = "\n".join(
		[
			"# Blank",
			"- Not allowed",
		]
	)
	with pytest.raises(ValueError):
		md_to_slides_yaml.parse_markdown(content)
