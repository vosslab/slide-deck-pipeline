import pytest

pptx = pytest.importorskip("pptx")

import index_slide_deck
import slide_deck_pipeline.csv_schema as csv_schema

assert pptx


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
		has_table: bool = False,
		has_chart: bool = False,
	) -> None:
		self.has_text_frame = text_frame is not None
		self.text_frame = text_frame
		self.shape_type = shape_type
		self.image = image
		self.shape_id = shape_id
		self.has_table = has_table
		self.has_chart = has_chart


class FakeShapes:
	def __init__(self, shapes: list[FakeShape], title: FakeShape | None = None) -> None:
		self._shapes = shapes
		self.title = title

	def __iter__(self):
		return iter(self._shapes)


class FakeSlide:
	def __init__(self, shapes) -> None:
		self.shapes = shapes


class FakeMaster:
	def __init__(self, name: str) -> None:
		self.name = name


class FakeLayout:
	def __init__(self, name: str, master_name: str = "") -> None:
		self.name = name
		self.slide_master = FakeMaster(master_name)


class FakeSlideWithLayout:
	def __init__(self, shapes, layout) -> None:
		self.shapes = shapes
		self._layout = layout

	@property
	def slide_layout(self):
		return self._layout


class FakeSlideLayoutError:
	def __init__(self, shapes) -> None:
		self.shapes = shapes

	@property
	def slide_layout(self):
		raise ValueError("multiple relationships")


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
def test_collect_asset_types() -> None:
	"""
	Summarize slide asset types.
	"""
	image_shape = FakeShape(
		shape_type=pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE,
	)
	second_image = FakeShape(
		shape_type=pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE,
	)
	table_shape = FakeShape(has_table=True)
	shapes = FakeShapes([image_shape, second_image, table_shape])
	slide = FakeSlide(shapes)
	assert index_slide_deck.collect_asset_types(slide) == "images_2|table"


#============================================
def test_resolve_master_name_fallback() -> None:
	"""
	Fall back to custom master name on errors.
	"""
	shapes = FakeShapes([])
	slide = FakeSlideLayoutError(shapes)
	master_name, warning = index_slide_deck.resolve_master_name(slide)
	assert master_name == "custom"
	assert warning is not None


#============================================
def test_resolve_master_name_ok() -> None:
	"""
	Read master names when available.
	"""
	shapes = FakeShapes([])
	layout = FakeLayout("Layout Name", "Master Name")
	slide = FakeSlideWithLayout(shapes, layout)
	master_name, warning = index_slide_deck.resolve_master_name(slide)
	assert master_name == "Master Name"
	assert warning is None


#============================================
def test_build_slide_row() -> None:
	"""
	Build a slide row with stable hashes.
	"""
	row = index_slide_deck.build_slide_row(
		"deck.pptx",
		2,
		"Title",
		"Body",
		"Notes",
		csv_schema.compute_slide_hash(b"<slide>Title</slide>", "Notes"),
		"Master",
		"title_content",
		0.9,
		"title_and_body",
		"image",
	)
	assert row["source_pptx"] == "deck.pptx"
	assert row["source_slide_index"] == "2"
	assert row["master_name"] == "Master"
	assert row["layout_type"] == "title_content"
	assert row["layout_confidence"] == "0.90"
	assert row["layout_reasons"] == "title_and_body"
	assert row["asset_types"] == "image"
	expected_hash = csv_schema.compute_slide_hash(b"<slide>Title</slide>", "Notes")
	assert row["slide_hash"] == expected_hash
