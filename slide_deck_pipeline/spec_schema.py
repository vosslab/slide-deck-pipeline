# Standard Library
import os

# PIP3 modules
import yaml


LAYOUT_TYPE_ALIASES = {
	"blank": "blank",
	"blank_slide": "blank",
	"title": "title_slide",
	"title_slide": "title_slide",
	"title_content": "title_content",
	"title_and_content": "title_content",
	"content": "title_content",
	"title_2_content": "title_2_content",
	"title_and_2_content": "title_2_content",
	"title_only": "title_only",
	"centered_text": "centered_text",
	"title_2_content_and_content": "title_2_content_and_content",
	"title_content_and_2_content": "title_content_and_2_content",
	"title_2_content_over_content": "title_2_content_over_content",
	"title_content_over_content": "title_content_over_content",
	"title_4_content": "title_4_content",
	"title_6_content": "title_6_content",
}

SUPPORTED_LAYOUT_TYPES = sorted(set(LAYOUT_TYPE_ALIASES.values()))


#============================================
def normalize_name(value: str) -> str:
	"""
	Normalize a label for matching.

	Args:
		value: Input value.

	Returns:
		str: Normalized value.
	"""
	if not value:
		return ""
	return (
		value.strip()
		.lower()
		.replace("/", "_")
		.replace(",", "_")
		.replace(" ", "_")
	)


#============================================
def normalize_layout_type(value: str, allow_unknown: bool = False) -> str:
	"""
	Normalize a layout_type value to a canonical name.

	Args:
		value: Input layout_type.
		allow_unknown: Return empty string for unknown values.

	Returns:
		str: Canonical layout_type.
	"""
	key = normalize_name(value)
	if not key:
		return ""
	if key in LAYOUT_TYPE_ALIASES:
		return LAYOUT_TYPE_ALIASES[key]
	if allow_unknown:
		return ""
	raise ValueError(f"Unsupported layout_type: {value}")


#============================================
def validate_bodies(bodies: list[object], strict: bool) -> tuple[list[dict], list[str]]:
	"""
	Validate bodies list in a slide entry.

	Args:
		bodies: Body blocks.
		strict: Treat warnings as errors.

	Returns:
		tuple[list[dict], list[str]]: Normalized bodies and warnings.
	"""
	warnings = []
	normalized = []
	for index, body in enumerate(bodies, 1):
		if not isinstance(body, dict):
			raise ValueError(f"Body {index} must be a mapping.")
		allowed = {"bullets"}
		unknown = [key for key in body.keys() if key not in allowed]
		if unknown:
			raise ValueError(f"Body {index} has unsupported fields: {unknown}")
		bullets = body.get("bullets", [])
		if bullets is None:
			bullets = []
		if not isinstance(bullets, list):
			raise ValueError(f"Body {index} bullets must be a list.")
		cleaned = []
		for bullet in bullets:
			if not isinstance(bullet, str):
				raise ValueError(f"Body {index} bullets must be strings.")
			cleaned.append(bullet)
		normalized.append({"bullets": cleaned})
	return (normalized, warnings)


#============================================
def validate_slide_entry(
	entry: dict,
	default_layout_type: str,
	strict: bool,
) -> tuple[dict, list[str]]:
	"""
	Validate and normalize a slide entry.

	Args:
		entry: Slide entry mapping.
		default_layout_type: Default layout_type.
		strict: Treat warnings as errors.

	Returns:
		tuple[dict, list[str]]: Normalized entry and warnings.
	"""
	if not isinstance(entry, dict):
		raise ValueError("Each slide entry must be a mapping.")
	allowed = {"layout_type", "title", "subtitle", "bodies", "image", "images"}
	unknown = [key for key in entry.keys() if key not in allowed]
	if unknown:
		raise ValueError(f"Slide entry has unsupported fields: {unknown}")
	layout_type = entry.get("layout_type") or default_layout_type
	if not layout_type:
		raise ValueError("Slide entry missing layout_type.")
	normalized_layout = normalize_layout_type(layout_type)
	title = entry.get("title")
	subtitle = entry.get("subtitle")
	if title is not None and not isinstance(title, str):
		raise ValueError("Slide title must be a string.")
	if subtitle is not None and not isinstance(subtitle, str):
		raise ValueError("Slide subtitle must be a string.")
	image = entry.get("image")
	images = entry.get("images")
	warnings = []
	if image is not None and not isinstance(image, str):
		raise ValueError("Slide image must be a string path.")
	if images is not None:
		if not isinstance(images, list):
			raise ValueError("Slide images must be a list.")
		for item in images:
			if not isinstance(item, str):
				raise ValueError("Slide images must be string paths.")
	if image and images:
		message = "Slide entry has both image and images."
		if strict:
			raise ValueError(message)
		warnings.append(message)
	bodies = entry.get("bodies", [])
	if bodies is None:
		bodies = []
	if not isinstance(bodies, list):
		raise ValueError("Slide bodies must be a list.")
	normalized_bodies, body_warnings = validate_bodies(bodies, strict)
	warnings.extend(body_warnings)
	return (
		{
			"layout_type": normalized_layout,
			"title": title,
			"subtitle": subtitle,
			"bodies": normalized_bodies,
			"image": image,
			"images": images,
		},
		warnings,
	)


#============================================
def load_yaml_spec(
	input_path: str,
	template_override: str | None = None,
	strict: bool = False,
) -> tuple[dict, list[str]]:
	"""
	Load and validate a text-to-slides YAML spec.

	Args:
		input_path: YAML file path.
		template_override: Optional template deck override.
		strict: Treat warnings as errors.

	Returns:
		tuple[dict, list[str]]: Normalized spec and warnings.
	"""
	if not os.path.exists(input_path):
		raise FileNotFoundError(f"Spec file not found: {input_path}")
	with open(input_path, "r", encoding="utf-8") as handle:
		payload = yaml.safe_load(handle)
	if not isinstance(payload, dict):
		raise ValueError("Spec must be a YAML mapping.")
	version = payload.get("version")
	if version != 1:
		raise ValueError("Spec version must be 1.")
	template_deck = payload.get("template_deck")
	if template_override:
		template_deck = template_override
	defaults = payload.get("defaults", {})
	if defaults is None:
		defaults = {}
	if not isinstance(defaults, dict):
		raise ValueError("defaults must be a mapping.")
	default_layout = defaults.get("layout_type", "")
	if default_layout:
		default_layout = normalize_layout_type(default_layout)
	master_name = defaults.get("master_name")
	warnings = []
	if master_name is not None and not isinstance(master_name, str):
		raise ValueError("defaults.master_name must be a string.")
	if master_name and not template_deck:
		warnings.append("defaults.master_name is ignored without template_deck.")
	slides = payload.get("slides", [])
	if not isinstance(slides, list):
		raise ValueError("slides must be a list.")
	if not slides:
		warnings.append("No slides defined in spec.")
	normalized_slides = []
	for entry in slides:
		normalized_entry, entry_warnings = validate_slide_entry(
			entry,
			default_layout,
			strict,
		)
		normalized_slides.append(normalized_entry)
		warnings.extend(entry_warnings)
	return (
		{
			"version": 1,
			"template_deck": template_deck,
			"defaults": {
				"layout_type": default_layout or None,
				"master_name": master_name,
			},
			"slides": normalized_slides,
		},
		warnings,
	)
