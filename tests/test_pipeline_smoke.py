import pathlib

import pytest

pptx = pytest.importorskip("pptx")

import index_slide_deck
import rebuild_slides
import slide_deck_pipeline.csv_schema as csv_schema


#============================================
def create_pptx(path: pathlib.Path, title: str, body_lines: list[str]) -> None:
	"""
	Create a small PPTX with a title and body slide.
	"""
	presentation = pptx.Presentation()
	layout = presentation.slide_layouts[1]
	slide = presentation.slides.add_slide(layout)
	title_shape = slide.shapes.title
	if title_shape and title_shape.text_frame:
		title_shape.text_frame.text = title
	body_shape = None
	for shape in slide.shapes:
		if not shape.is_placeholder:
			continue
		placeholder_type = shape.placeholder_format.type
		if placeholder_type == pptx.enum.shapes.PP_PLACEHOLDER.BODY:
			body_shape = shape
			break
	if body_shape and body_shape.text_frame:
		text_frame = body_shape.text_frame
		text_frame.clear()
		for index, line in enumerate(body_lines):
			if index == 0:
				paragraph = text_frame.paragraphs[0]
			else:
				paragraph = text_frame.add_paragraph()
			paragraph.text = line
	presentation.save(path)


#============================================
def test_pipeline_index_merge_rebuild(tmp_path: pathlib.Path) -> None:
	"""
	Index, merge, and rebuild a small deck.
	"""
	first_path = tmp_path / "first.pptx"
	second_path = tmp_path / "second.pptx"
	create_pptx(first_path, "First", ["Alpha", "Beta"])
	create_pptx(second_path, "Second", ["Gamma", "Delta"])

	first_csv = tmp_path / "first.csv"
	second_csv = tmp_path / "second.csv"
	index_slide_deck.index_slides_to_csv(str(first_path), str(first_csv))
	index_slide_deck.index_slides_to_csv(str(second_path), str(second_csv))

	rows = []
	rows.extend(csv_schema.read_slide_csv(str(first_csv)))
	rows.extend(csv_schema.read_slide_csv(str(second_csv)))
	rows.sort(key=lambda row: (int(row["source_slide_index"]), row["source_pptx"]))

	merged_csv = tmp_path / "merged.csv"
	csv_schema.write_slide_csv(str(merged_csv), rows)

	output_path = tmp_path / "merged.pptx"
	rebuild_slides.rebuild_from_csv(
		str(merged_csv),
		str(output_path),
		"",
	)
	assert output_path.exists()
	merged = pptx.Presentation(str(output_path))
	assert len(merged.slides) == 2
