# Standard Library
import os

# local repo modules
import slide_deck_pipeline.path_resolver as path_resolver
import slide_deck_pipeline.soffice_tools as soffice_tools


#============================================
def resolve_input_pptx(input_path: str, temp_dir: str | None) -> tuple[str, str]:
	"""
	Return a PPTX path and a source basename for matching.

	Args:
		input_path: Input PPTX or ODP path.
		temp_dir: Temporary directory for conversions, or None.

	Returns:
		tuple[str, str]: Resolved PPTX path and source basename.
	"""
	resolved_path, warnings = path_resolver.resolve_path(
		input_path,
		input_dir=None,
		strict=False,
	)
	for message in warnings:
		print(f"Warning: {message}")
	source_name = os.path.basename(resolved_path)
	lowered = resolved_path.lower()
	if lowered.endswith(".pptx"):
		return (resolved_path, source_name)
	if lowered.endswith(".odp"):
		if not temp_dir:
			raise ValueError("Temporary directory required for ODP conversion.")
		pptx_path = soffice_tools.convert_odp_to_pptx(resolved_path, temp_dir)
		return (pptx_path, source_name)
	raise ValueError("Input must be a .pptx or .odp file.")
