import pytest

import slide_deck_pipeline.layout_classifier as layout_classifier


class FakePlaceholderFormat:
	def __init__(self, placeholder_type: int) -> None:
		self.type = placeholder_type


class FakeShape:
	def __init__(
		self,
		placeholder_type: int,
		left: int,
		top: int,
		width: int,
		height: int,
	) -> None:
		self.is_placeholder = True
		self.placeholder_format = FakePlaceholderFormat(placeholder_type)
		self.left = left
		self.top = top
		self.width = width
		self.height = height


class FakeShapes:
	def __init__(self, shapes: list[FakeShape]) -> None:
		self._shapes = shapes

	def __iter__(self):
		return iter(self._shapes)


class FakeSlide:
	def __init__(self, shapes: list[FakeShape]) -> None:
		self.shapes = FakeShapes(shapes)


#============================================
def resolve_placeholder(name: str) -> int:
	"""
	Resolve a placeholder constant if available.
	"""
	placeholders = pytest.importorskip("pptx.enum.shapes").PP_PLACEHOLDER
	value = getattr(placeholders, name, None)
	if value is None:
		pytest.skip(f"Placeholder {name} not available in this pptx version.")
	return value


#============================================
def make_slide(shapes: list[FakeShape]) -> FakeSlide:
	"""
	Build a fake slide with placeholder shapes.
	"""
	return FakeSlide(shapes)


#============================================
def test_title_slide_classification() -> None:
	"""
	Classify a title slide with title and subtitle placeholders.
	"""
	title = resolve_placeholder("TITLE")
	subtitle = resolve_placeholder("SUBTITLE")
	slide = make_slide(
		[
			FakeShape(title, 0, 0, 400, 100),
			FakeShape(subtitle, 0, 120, 400, 100),
		]
	)
	layout, confidence, reasons = layout_classifier.classify_layout_type(
		slide,
		800,
		600,
		"Title",
		"",
	)
	assert layout == "title_slide"
	assert confidence >= 0.8
	assert "title_and_subtitle" in reasons


#============================================
def test_title_only_classification() -> None:
	"""
	Classify a title-only slide.
	"""
	title = resolve_placeholder("TITLE")
	slide = make_slide([FakeShape(title, 0, 0, 400, 100)])
	layout, confidence, reasons = layout_classifier.classify_layout_type(
		slide,
		800,
		600,
		"Title",
		"",
	)
	assert layout == "title_only"
	assert confidence >= 0.8
	assert "title_only" in reasons


#============================================
def test_title_content_classification() -> None:
	"""
	Classify a title with one body placeholder.
	"""
	title = resolve_placeholder("TITLE")
	body = resolve_placeholder("BODY")
	slide = make_slide(
		[
			FakeShape(title, 0, 0, 400, 100),
			FakeShape(body, 0, 150, 400, 300),
		]
	)
	layout, confidence, reasons = layout_classifier.classify_layout_type(
		slide,
		800,
		600,
		"Title",
		"Body",
	)
	assert layout == "title_content"
	assert confidence >= 0.8
	assert "title_and_body" in reasons


#============================================
def test_subtitle_like_body_classification() -> None:
	"""
	Treat short centered body text as subtitle-like with low confidence.
	"""
	title = resolve_placeholder("TITLE")
	body = resolve_placeholder("BODY")
	slide = make_slide(
		[
			FakeShape(title, 0, 0, 800, 100),
			FakeShape(body, 200, 120, 400, 80),
		]
	)
	layout, confidence, reasons = layout_classifier.classify_layout_type(
		slide,
		800,
		600,
		"Title",
		"Short line",
	)
	assert layout == "title_slide"
	assert confidence <= 0.6
	assert "title_and_body_subtitle_like" in reasons


#============================================
def test_two_content_classification() -> None:
	"""
	Classify a title with two body placeholders split left-right.
	"""
	title = resolve_placeholder("TITLE")
	body = resolve_placeholder("BODY")
	slide = make_slide(
		[
			FakeShape(title, 0, 0, 600, 100),
			FakeShape(body, 0, 150, 300, 300),
			FakeShape(body, 330, 150, 300, 300),
		]
	)
	layout, confidence, reasons = layout_classifier.classify_layout_type(
		slide,
		800,
		600,
		"Title",
		"Body",
	)
	assert layout == "two_content"
	assert confidence >= 0.8
	assert "two_body_split" in reasons


#============================================
def test_centered_text_classification() -> None:
	"""
	Classify centered text with no title.
	"""
	body = resolve_placeholder("BODY")
	slide = make_slide([FakeShape(body, 200, 200, 400, 200)])
	layout, confidence, reasons = layout_classifier.classify_layout_type(
		slide,
		800,
		600,
		"",
		"Body",
	)
	assert layout == "centered_text"
	assert confidence >= 0.7
	assert "centered_body" in reasons


#============================================
def test_blank_classification() -> None:
	"""
	Classify blank slides with no placeholders and no text.
	"""
	slide = make_slide([])
	layout, confidence, reasons = layout_classifier.classify_layout_type(
		slide,
		800,
		600,
		"",
		"",
	)
	assert layout == "blank"
	assert confidence == 1.0
	assert "no_placeholders_no_text" in reasons
