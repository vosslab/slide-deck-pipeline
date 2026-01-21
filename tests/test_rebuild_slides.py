import pytest

pptx = pytest.importorskip("pptx")

import rebuild_slides


class FakeMaster:
	def __init__(self, name: str) -> None:
		self.name = name


class FakeLayout:
	def __init__(self, name: str, master_name: str = "") -> None:
		self.name = name
		self.slide_master = FakeMaster(master_name)


class FakePresentation:
	def __init__(self, layouts: list[FakeLayout]) -> None:
		self.slide_layouts = layouts


class FakeParagraph:
	def __init__(self) -> None:
		self.text = ""
		self.level = 0


class FakeTextFrame:
	def __init__(self) -> None:
		self.paragraphs = [FakeParagraph()]
		self.text = ""

	def clear(self) -> None:
		self.paragraphs = [FakeParagraph()]
		self.text = ""

	def add_paragraph(self) -> FakeParagraph:
		paragraph = FakeParagraph()
		self.paragraphs.append(paragraph)
		return paragraph


class FakePlaceholderFormat:
	def __init__(self, placeholder_type: int) -> None:
		self.type = placeholder_type


class FakeShape:
	def __init__(
		self,
		is_placeholder: bool = False,
		placeholder_type: int | None = None,
		text_frame: FakeTextFrame | None = None,
	) -> None:
		self.is_placeholder = is_placeholder
		self.placeholder_format = FakePlaceholderFormat(placeholder_type or 0)
		self.has_text_frame = text_frame is not None
		self.text_frame = text_frame
		self.inserted = []

	def insert_picture(self, stream) -> None:
		self.inserted.append(stream)


class FakeShapes:
	def __init__(self, shapes: list[FakeShape], title: FakeShape | None = None) -> None:
		self._shapes = shapes
		self.title = title
		self.pictures = []

	def __iter__(self):
		return iter(self._shapes)

	def add_picture(self, path, left, top, width=None, height=None) -> None:
		self.pictures.append((path, left, top, width, height))


class FakePresentationDimensions:
	def __init__(self, width, height) -> None:
		self.slide_width = width
		self.slide_height = height


class FakePart:
	def __init__(self, presentation) -> None:
		self.presentation = presentation


class FakeSlide:
	def __init__(self, shapes: FakeShapes, width, height) -> None:
		self.shapes = shapes
		self.part = FakePart(FakePresentationDimensions(width, height))


#============================================
def test_normalize_name() -> None:
	"""
	Normalize names to matching tokens.
	"""
	assert rebuild_slides.normalize_name("Title And Content") == "title_and_content"
	assert rebuild_slides.normalize_name("") == ""


#============================================
def test_select_layout_with_master() -> None:
	"""
	Select a layout using master and layout names.
	"""
	layouts = [
		FakeLayout("Title and Content", "Core"),
		FakeLayout("Title and Content", "Alt"),
	]
	presentation = FakePresentation(layouts)
	layout = rebuild_slides.select_layout(presentation, "Alt", "Title and Content")
	assert layout.slide_master.name == "Alt"


#============================================
def test_select_layout_fallback() -> None:
	"""
	Fall back to the first layout when no hint matches.
	"""
	layouts = [FakeLayout("First"), FakeLayout("Second")]
	presentation = FakePresentation(layouts)
	layout = rebuild_slides.select_layout(presentation, "", "unknown")
	assert layout.name == "First"


#============================================
def test_parse_body_lines() -> None:
	"""
	Parse body text into levels and text.
	"""
	body = "Top\n\tSub\n\t\tDeep"
	lines = rebuild_slides.parse_body_lines(body)
	assert lines == [(0, "Top"), (1, "Sub"), (2, "Deep")]


#============================================
def test_set_title() -> None:
	"""
	Set title text when a title placeholder exists.
	"""
	title_frame = FakeTextFrame()
	title_shape = FakeShape(text_frame=title_frame)
	shapes = FakeShapes([title_shape], title=title_shape)
	slide = FakeSlide(shapes, pptx.util.Inches(10), pptx.util.Inches(7.5))
	rebuild_slides.set_title(slide, "Title")
	assert title_frame.text == "Title"


#============================================
def test_find_body_placeholder() -> None:
	"""
	Find the body placeholder by type.
	"""
	body_shape = FakeShape(
		is_placeholder=True,
		placeholder_type=pptx.enum.shapes.PP_PLACEHOLDER.BODY,
		text_frame=FakeTextFrame(),
	)
	other_shape = FakeShape(is_placeholder=True, placeholder_type=0)
	shapes = FakeShapes([other_shape, body_shape])
	slide = FakeSlide(shapes, pptx.util.Inches(10), pptx.util.Inches(7.5))
	found = rebuild_slides.find_body_placeholder(slide)
	assert found == body_shape


#============================================
def test_set_body_text() -> None:
	"""
	Set body text with indentation levels.
	"""
	body_shape = FakeShape(
		is_placeholder=True,
		placeholder_type=pptx.enum.shapes.PP_PLACEHOLDER.BODY,
		text_frame=FakeTextFrame(),
	)
	shapes = FakeShapes([body_shape])
	slide = FakeSlide(shapes, pptx.util.Inches(10), pptx.util.Inches(7.5))
	rebuild_slides.set_body_text(slide, "Item\n\tSub")
	assert len(body_shape.text_frame.paragraphs) == 2
	assert body_shape.text_frame.paragraphs[0].text == "Item"
	assert body_shape.text_frame.paragraphs[0].level == 0
	assert body_shape.text_frame.paragraphs[1].text == "Sub"
	assert body_shape.text_frame.paragraphs[1].level == 1


#============================================
def test_place_images_grid_calls_add_picture() -> None:
	"""
	Add pictures with a simple grid layout.
	"""
	shapes = FakeShapes([])
	slide = FakeSlide(shapes, pptx.util.Inches(10), pptx.util.Inches(7.5))
	rebuild_slides.place_images_grid(slide, [b"a", b"b", b"c"])
	assert len(shapes.pictures) == 3
	for path, left, top, width, height in shapes.pictures:
		assert width > 0
		assert height > 0


#============================================
def test_insert_images_uses_placeholder() -> None:
	"""
	Insert a single image into a picture placeholder.
	"""
	picture_shape = FakeShape(
		is_placeholder=True,
		placeholder_type=pptx.enum.shapes.PP_PLACEHOLDER.PICTURE,
	)
	shapes = FakeShapes([picture_shape])
	slide = FakeSlide(shapes, pptx.util.Inches(10), pptx.util.Inches(7.5))
	rebuild_slides.insert_images(slide, [b"only"])
	assert len(picture_shape.inserted) == 1
	assert shapes.pictures == []


#============================================
