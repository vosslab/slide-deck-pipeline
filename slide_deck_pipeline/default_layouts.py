# PIP3 modules
import pptx

# local repo modules
import slide_deck_pipeline.template as template


#============================================
def build_default_layout_map(
	presentation: pptx.Presentation,
	strict: bool,
) -> tuple[dict[str, object], list[str]]:
	"""
	Build a layout_type to layout map using library defaults.

	Args:
		presentation: Default presentation.
		strict: Treat warnings as errors.

	Returns:
		tuple[dict, list[str]]: Layout map and warnings.
	"""
	layout_map: dict[str, object] = {}
	warnings = []
	for layout in presentation.slide_layouts:
		layout_type = template.layout_name_to_layout_type(layout.name)
		if not layout_type:
			continue
		if layout_type in layout_map:
			message = f"Duplicate default layout mapping for {layout_type}."
			if strict:
				raise ValueError(message)
			warnings.append(message)
			continue
		layout_map[layout_type] = layout
	return (layout_map, warnings)


#============================================
def resolve_default_layout(
	layout_map: dict[str, object],
	layout_type: str,
	strict: bool,
) -> tuple[object, list[str]]:
	"""
	Resolve a layout from the default layout map.

	Args:
		layout_map: layout_type to layout mapping.
		layout_type: layout_type.
		strict: Treat warnings as errors.

	Returns:
		tuple[object, list[str]]: Layout and warnings.
	"""
	warnings = []
	if layout_type in layout_map:
		return (layout_map[layout_type], warnings)
	message = f"Default layout {layout_type} not found."
	if strict:
		raise ValueError(message)
	warnings.append(message)
	fallback = layout_map.get("title_content")
	if fallback:
		return (fallback, warnings)
	any_layout = list(layout_map.values())
	if not any_layout:
		raise ValueError("Default presentation has no layouts.")
	return (any_layout[0], warnings)
