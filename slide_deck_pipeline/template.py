# Standard Library
import os

# PIP3 modules
import pptx

# local repo modules
import slide_deck_pipeline.spec_schema as spec_schema


#============================================
def normalize_layout_name(name: str) -> str:
	"""
	Normalize a layout name for matching to layout_type.

	Args:
		name: Layout name.

	Returns:
		str: Normalized name.
	"""
	value = (
		(name or "")
		.strip()
		.lower()
		.replace(",", " ")
		.replace("/", " ")
		.replace("-", " ")
	)
	return replace_whitespace(value)


#============================================
def replace_whitespace(value: str) -> str:
	"""
	Collapse whitespace to single underscores.

	Args:
		value: Input string.

	Returns:
		str: Normalized value.
	"""
	parts = value.split()
	return "_".join(parts)


#============================================
def layout_name_to_layout_type(name: str) -> str:
	"""
	Map a layout name to a canonical layout_type.

	Args:
		name: Layout name.

	Returns:
		str: layout_type or empty string if unknown.
	"""
	normalized = normalize_layout_name(name)
	return spec_schema.normalize_layout_type(normalized, allow_unknown=True)


#============================================
def normalize_master_name(name: str) -> str:
	"""
	Normalize a master name for matching.

	Args:
		name: Master name.

	Returns:
		str: Normalized master name.
	"""
	return spec_schema.normalize_name(name)


#============================================
def load_template(path: str) -> pptx.Presentation:
	"""
	Load a template deck.

	Args:
		path: PPTX template path.

	Returns:
		pptx.Presentation: Loaded presentation.
	"""
	if not os.path.exists(path):
		raise FileNotFoundError(f"Template deck not found: {path}")
	return pptx.Presentation(path)


#============================================
def build_layout_map(
	presentation: pptx.Presentation,
	strict: bool,
) -> tuple[dict[tuple[str, str], object], list[str]]:
	"""
	Build a (master_name, layout_type) to layout map.

	Args:
		presentation: Template presentation.
		strict: Treat warnings as errors.

	Returns:
		tuple[dict, list[str]]: Layout map and warnings.
	"""
	layout_map: dict[tuple[str, str], object] = {}
	warnings = []
	for layout in presentation.slide_layouts:
		layout_type = layout_name_to_layout_type(layout.name)
		if not layout_type:
			continue
		master = getattr(layout, "slide_master", None)
		master_name = normalize_master_name(getattr(master, "name", ""))
		key = (master_name, layout_type)
		if key in layout_map:
			message = f"Duplicate layout mapping for {key}."
			if strict:
				raise ValueError(message)
			warnings.append(message)
			continue
		layout_map[key] = layout
	return (layout_map, warnings)


#============================================
def resolve_layout(
	layout_map: dict[tuple[str, str], object],
	master_name: str,
	layout_type: str,
	strict: bool,
) -> tuple[object, list[str]]:
	"""
	Resolve a layout from a layout map.

	Args:
		layout_map: Mapping of (master_name, layout_type) to layout.
		master_name: Master name.
		layout_type: layout_type.
		strict: Treat warnings as errors.

	Returns:
		tuple[object, list[str]]: Layout and warnings.
	"""
	warnings = []
	key = (normalize_master_name(master_name), layout_type)
	if key in layout_map:
		return (layout_map[key], warnings)
	candidates = [
		item for item in layout_map.items() if item[0][1] == layout_type
	]
	if candidates:
		choice = sorted(candidates, key=lambda item: item[0])[0]
		message = f"Layout {key} not found; using {choice[0]}."
		if strict:
			raise ValueError(message)
		warnings.append(message)
		return (choice[1], warnings)
	message = f"Layout {key} not found in template."
	if strict:
		raise ValueError(message)
	warnings.append(message)
	fallback = list(layout_map.values())
	if not fallback:
		raise ValueError("Template deck has no layouts.")
	return (fallback[0], warnings)
