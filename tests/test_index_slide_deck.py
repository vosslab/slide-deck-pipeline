import pytest

pptx = pytest.importorskip("pptx")

import index_slide_deck
import slide_deck_pipeline.csv_schema as csv_schema


class FakeParagraph:
	def __init__(self, text: str, level: int = 0) -> None:
		self.text = text
		self.level = level


class FakeTextFrame:
	def __init__(self, paragraphs: list[FakeParagraph]) -> None:
		self.paragraphs = paragraphs


class FakeShape:
	def __init__(
		self,
		text_frame: FakeTextFrame | None = None,
		shape_type: int | None = None,
		image: object | None = None,
		shape_id: int = 1,
	) -> None:
		self.has_text_frame = text_frame is not None
		self.text_frame = text_frame
		self.shape_type = shape_type
		self.image = image
		self.shape_id = shape_id


class FakeShapes:
	def __init__(self, shapes: list[FakeShape], title: FakeShape | None = None) -> None:
		self._shapes = shapes
		self.title = title

	def __iter__(self):
		return iter(self._shapes)


class FakeSlide:
	def __init__(self, shapes) -> None:
		self.shapes = shapes


class FakeImage:
	def __init__(self, blob: bytes, ext: str) -> None:
		self.blob = blob
		self.ext = ext


#============================================
def test_normalize_layout_hint() -> None:
	"""
	Normalize layout names to hint tokens.
	"""
	assert index_slide_deck.normalize_layout_hint("Title and Content") == "title_and_content"
	assert index_slide_deck.normalize_layout_hint("Section Header") == "section_header"
	assert index_slide_deck.normalize_layout_hint("") == "custom"


#============================================
def test_extract_paragraph_lines() -> None:
	"""
	Extract paragraph lines with indentation.
	"""
	paragraphs = [
		FakeParagraph("Top", 0),
		FakeParagraph("Sub", 1),
		FakeParagraph("", 0),
	]
	frame = FakeTextFrame(paragraphs)
	lines = index_slide_deck.extract_paragraph_lines(frame)
	assert lines == ["Top", "\tSub"]


#============================================
def test_extract_body_text_skips_title() -> None:
	"""
	Skip title shape when extracting body text.
	"""
	title_frame = FakeTextFrame([FakeParagraph("Title", 0)])
	title_shape = FakeShape(text_frame=title_frame)
	body_frame = FakeTextFrame([FakeParagraph("Body", 0)])
	body_shape = FakeShape(text_frame=body_frame)
	shapes = FakeShapes([title_shape, body_shape], title=title_shape)
	slide = FakeSlide(shapes)
	assert index_slide_deck.extract_body_text(slide) == "Body"


#============================================
def test_collect_slide_images() -> None:
	"""
	Collect image blobs and hashes from picture shapes.
	"""
	image = FakeImage(b"data", "png")
	picture = FakeShape(
		text_frame=None,
		shape_type=pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE,
		image=image,
		shape_id=5,
	)
	other = FakeShape(text_frame=None, shape_type=pptx.enum.shapes.MSO_SHAPE_TYPE.AUTO_SHAPE)
	slide = FakeSlide([picture, other])
	images = index_slide_deck.collect_slide_images(slide, "deck.pptx", 1)
	assert len(images) == 1
	assert images[0]["hash"] == csv_schema.hash_text("data")
	expected_locator = csv_schema.build_image_locator("deck.pptx", 1, 5)
	assert images[0]["locator"] == expected_locator


#============================================
def test_build_slide_row() -> None:
	"""
	Build a slide row with stable hashes and IDs.
	"""
	row = index_slide_deck.build_slide_row(
		"deck.pptx",
		2,
		"Title",
		"Body",
		"Notes",
		"title_and_content",
		["pptx:deck.pptx#slide=2#shape_id=4"],
		["hash1"],
	)
	assert row["source_pptx"] == "deck.pptx"
	assert row["source_slide_index"] == "2"
	assert row["layout_hint"] == "title_and_content"
	assert row["image_locators"] == "pptx:deck.pptx#slide=2#shape_id=4"
	expected_uid = csv_schema.compute_slide_uid(
		"deck.pptx",
		2,
		"Title",
		"Body",
		"Notes",
		["hash1"],
	)
	assert row["slide_uid"] == expected_uid
