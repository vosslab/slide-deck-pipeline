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
	Index rows should use a hash matching the pristine slide XML.
	"""
	pptx_path = tmp_path / "hash_index.pptx"
	build_sample_pptx(str(pptx_path))
	presentation = pptx.Presentation(str(pptx_path))
	pristine_slide = presentation.slides[0]
	pristine_hash, _, _ = pptx_hash.compute_slide_hash_from_slide(pristine_slide)
	rows = index_slide_deck.index_rows(str(pptx_path), "hash_index.pptx")
	assert rows[0]["slide_hash"] == pristine_hash
