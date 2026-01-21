# Standard Library
import os

# local repo modules
import slide_deck_pipeline.spec_schema as spec_schema


TYPE_LABELS = {
	"title_slide": "title_slide",
	"title slide": "title_slide",
	"title_content": "title_content",
	"title content": "title_content",
	"centered_text": "centered_text",
	"centered text": "centered_text",
	"blank": "blank",
	"blank slide": "blank",
}


#============================================
def normalize_type_label(label: str) -> str:
	"""
	Normalize a Markdown type label into a layout_type.

	Args:
		label: Raw label string.

	Returns:
		str: layout_type name.
	"""
	if not label:
		return ""
	key = label.strip().lower().replace("#", "").strip()
	if key in TYPE_LABELS:
		return TYPE_LABELS[key]
	return spec_schema.normalize_layout_type(key, allow_unknown=True)


#============================================
def split_slides(text: str) -> list[list[str]]:
	"""
	Split Markdown text into slide blocks.

	Args:
		text: Markdown content.

	Returns:
		list[list[str]]: List of slide blocks.
	"""
	blocks = []
	current = []
	for raw_line in text.splitlines():
		line = raw_line.rstrip()
		if line.strip() == "---":
			if current:
				blocks.append(current)
				current = []
			continue
		current.append(line)
	if current:
		blocks.append(current)
	return blocks


#============================================
def parse_slide_block(lines: list[str]) -> dict:
	"""
	Parse a single slide block into a spec entry.

	Args:
		lines: Slide lines.

	Returns:
		dict: Slide entry.
	"""
	layout_type = ""
	title = None
	subtitle = None
	bullets = []
	stage = "type"
	for line in lines:
		if not line.strip():
			continue
		if line.startswith("# "):
			if stage == "type":
				layout_type = normalize_type_label(line[2:])
				stage = "title"
				continue
			if stage in ("title", "subtitle", "body"):
				if title is None:
					title = line[2:].strip()
					stage = "subtitle"
					continue
				raise ValueError("Multiple title lines in slide block.")
		if line.startswith("## "):
			if subtitle is None:
				subtitle = line[3:].strip()
				stage = "body"
				continue
			raise ValueError("Multiple subtitle lines in slide block.")
		if line.startswith("- "):
			bullets.append(line[2:].strip())
			stage = "body"
			continue
		raise ValueError(f"Unsupported Markdown line: {line}")
	if not layout_type:
		raise ValueError("Slide block missing type line.")
	if layout_type not in ("title_slide", "title_content", "centered_text", "blank"):
		raise ValueError(f"Unsupported slide type: {layout_type}")
	if layout_type == "blank":
		if title or subtitle or bullets:
			raise ValueError("Blank slides cannot include title, subtitle, or bullets.")
	if layout_type == "title_slide" and bullets:
		raise ValueError("Title slide cannot include bullets.")
	if layout_type == "title_content" and not title:
		raise ValueError("Title content slides require a title.")
	if layout_type == "centered_text" and not bullets:
		raise ValueError("Centered text slides require bullets.")
	entry = {"layout_type": layout_type}
	if title:
		entry["title"] = title
	if subtitle:
		entry["subtitle"] = subtitle
	if bullets:
		entry["bodies"] = [{"bullets": bullets}]
	return entry


#============================================
def parse_markdown(text: str) -> dict:
	"""
	Parse constrained Markdown into a YAML spec dict.

	Args:
		text: Markdown content.

	Returns:
		dict: Spec payload.
	"""
	slides = []
	for block in split_slides(text):
		entry = parse_slide_block(block)
		slides.append(entry)
	return {
		"version": 1,
		"defaults": {"layout_type": "title_content"},
		"slides": slides,
	}


#============================================
def load_markdown(path: str) -> str:
	"""
	Load Markdown content from disk.

	Args:
		path: Markdown file path.

	Returns:
		str: Markdown content.
	"""
	if not os.path.exists(path):
		raise FileNotFoundError(f"Markdown file not found: {path}")
	with open(path, "r", encoding="utf-8") as handle:
		return handle.read()


#============================================
def markdown_to_spec(path: str) -> dict:
	"""
	Load Markdown and return a parsed spec.

	Args:
		path: Markdown file path.

	Returns:
		dict: Spec payload.
	"""
	content = load_markdown(path)
	return parse_markdown(content)
