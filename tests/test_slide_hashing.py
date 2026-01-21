import base64

import pytest

pptx = pytest.importorskip("pptx")

import index_slide_deck
import slide_deck_pipeline.csv_schema as csv_schema
import slide_deck_pipeline.pptx_hash as pptx_hash

assert pptx


#============================================
def build_sample_pptx(path) -> None:
	"""
	Build a simple PPTX with one title and body slide.
	"""
	presentation = pptx.Presentation()
	layout = presentation.slide_layouts[1]
	slide = presentation.slides.add_slide(layout)
	slide.shapes.title.text = "Title"
	body = slide.shapes.placeholders[1]
	body.text = "Body text"
	presentation.save(path)


#============================================
def build_ordered_shapes_pptx(
	path,
	first_text: str,
	second_text: str,
) -> None:
	"""
	Build a PPTX with a single blank slide and two textboxes in the given order.
	"""
	presentation = pptx.Presentation()
	layout = presentation.slide_layouts[6]
	slide = presentation.slides.add_slide(layout)
	box_one = slide.shapes.add_textbox(
		100000,
		100000,
		3000000,
		500000,
	)
	box_one.text_frame.text = first_text
	box_two = slide.shapes.add_textbox(
		100000,
		800000,
		3000000,
		500000,
	)
	box_two.text_frame.text = second_text
	presentation.save(path)


#============================================
def build_picture_pptx(path, image_bytes: bytes) -> None:
	"""
	Build a PPTX with a single picture on a blank slide.
	"""
	presentation = pptx.Presentation()
	layout = presentation.slide_layouts[6]
	slide = presentation.slides.add_slide(layout)
	image_path = path.replace(".pptx", ".png")
	with open(image_path, "wb") as handle:
		handle.write(image_bytes)
	slide.shapes.add_picture(
		image_path,
		100000,
		100000,
		1000000,
		1000000,
	)
	presentation.save(path)


#============================================
def test_compute_slide_hash_changes_with_notes() -> None:
	"""
	Slide hash should change when notes change.
	"""
	slide_xml = b"<slide>Title</slide>"
	first = csv_schema.compute_slide_hash(slide_xml, "Notes A")
	second = csv_schema.compute_slide_hash(slide_xml, "Notes B")
	assert first != second


#============================================
def test_compute_slide_hash_from_slide_stable(tmp_path) -> None:
	"""
	Hashing the same slide repeatedly should be stable.
	"""
	pptx_path = tmp_path / "hash_stable.pptx"
	build_sample_pptx(str(pptx_path))
	presentation = pptx.Presentation(str(pptx_path))
	slide = presentation.slides[0]
	hash_one, _, _ = pptx_hash.compute_slide_hash_from_slide(slide)
	hash_two, _, _ = pptx_hash.compute_slide_hash_from_slide(slide)
	assert hash_one == hash_two


#============================================
def test_index_rows_hash_matches_pristine_slide(tmp_path) -> None:
	"""
	Index rows should use a hash matching the pristine slide structure.
	"""
	pptx_path = tmp_path / "hash_index.pptx"
	build_sample_pptx(str(pptx_path))
	presentation = pptx.Presentation(str(pptx_path))
	pristine_slide = presentation.slides[0]
	pristine_hash, _, _ = pptx_hash.compute_slide_hash_from_slide(pristine_slide)
	rows = index_slide_deck.index_rows(str(pptx_path), "hash_index.pptx")
	assert rows[0]["slide_hash"] == pristine_hash


#============================================
def test_slide_hash_changes_with_shape_order(tmp_path) -> None:
	"""
	Hash should change when shape order changes.
	"""
	ordered_path = tmp_path / "ordered.pptx"
	reversed_path = tmp_path / "reversed.pptx"
	build_ordered_shapes_pptx(str(ordered_path), "First", "Second")
	build_ordered_shapes_pptx(str(reversed_path), "Second", "First")
	ordered_presentation = pptx.Presentation(str(ordered_path))
	reversed_presentation = pptx.Presentation(str(reversed_path))
	ordered_hash, _, _ = pptx_hash.compute_slide_hash_from_slide(
		ordered_presentation.slides[0]
	)
	reversed_hash, _, _ = pptx_hash.compute_slide_hash_from_slide(
		reversed_presentation.slides[0]
	)
	assert ordered_hash != reversed_hash


#============================================
def test_slide_hash_changes_with_picture(tmp_path) -> None:
	"""
	Hash should change when picture content changes.
	"""
	png_one = base64.b64decode(
		"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMA"
		"ASsJTYQAAAAASUVORK5CYII="
	)
	png_two = base64.b64decode(
		"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQAB"
		"JBSQGQAAAABJRU5ErkJggg=="
	)
	first_path = tmp_path / "picture_one.pptx"
	second_path = tmp_path / "picture_two.pptx"
	build_picture_pptx(str(first_path), png_one)
	build_picture_pptx(str(second_path), png_two)
	first_presentation = pptx.Presentation(str(first_path))
	second_presentation = pptx.Presentation(str(second_path))
	first_hash, _, _ = pptx_hash.compute_slide_hash_from_slide(
		first_presentation.slides[0]
	)
	second_hash, _, _ = pptx_hash.compute_slide_hash_from_slide(
		second_presentation.slides[0]
	)
	assert first_hash != second_hash
