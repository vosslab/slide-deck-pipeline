# Standard Library
import os
import subprocess

# PIP3 modules
import lxml.etree as etree


PRESENTATION_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
SLIDE_REL_TYPE = (
	"http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
)
PRESENTATION_NS = {
	"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
	"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

SHAPE_NAME_QUESTION = "MC_QUESTION"
SHAPE_NAME_OPTIONS = "MC_OPTIONS"
SHAPE_NAME_POPUP = "MC_ANSWER_POPUP"


#============================================
def get_repo_root() -> str:
	"""
	Return the repository root path using git.

	Returns:
		str: Repository root directory.
	"""
	result = subprocess.run(
		["git", "rev-parse", "--show-toplevel"],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
	)
	if result.returncode != 0:
		message = result.stderr.strip() or "Failed to resolve repo root."
		raise RuntimeError(message)
	root = result.stdout.strip()
	if not root:
		raise RuntimeError("Git repository root is empty.")
	return root


#============================================
def get_template_source_dir() -> str:
	"""
	Return the template source directory.

	Returns:
		str: Template source path.
	"""
	repo_root = get_repo_root()
	candidates = [
		os.path.join(repo_root, "template_src", "MC_TO_SLIDES_template"),
		os.path.join(repo_root, "templates_src", "MC_TO_SLIDES_template"),
	]
	for path in candidates:
		if os.path.isdir(path):
			return path
	raise FileNotFoundError(
		"Template source not found under template_src/MC_TO_SLIDES_template."
	)


#============================================
def validate_template_source(template_dir: str) -> None:
	"""
	Validate required template source files exist.

	Args:
		template_dir: Template source path.
	"""
	required = [
		"[Content_Types].xml",
		os.path.join("ppt", "presentation.xml"),
		os.path.join("ppt", "_rels", "presentation.xml.rels"),
		os.path.join("ppt", "slides", "slide1.xml"),
		os.path.join("ppt", "slides", "_rels", "slide1.xml.rels"),
	]
	for rel_path in required:
		path = os.path.join(template_dir, rel_path)
		if not os.path.exists(path):
			raise FileNotFoundError(f"Missing template file: {path}")


#============================================
def find_template_slide(template_dir: str) -> tuple[str, str, dict[str, str], list[str]]:
	"""
	Locate the template slide and required shape ids.

	Args:
		template_dir: Template source path.

	Returns:
		tuple[str, str, dict[str, str], list[str]]: Slide path, rels path,
			shape ids, and warnings.
	"""
	slides_dir = os.path.join(template_dir, "ppt", "slides")
	rel_dir = os.path.join(slides_dir, "_rels")
	slide_paths = [
		path
		for path in sorted(os.listdir(slides_dir))
		if path.startswith("slide") and path.endswith(".xml")
	]
	for filename in slide_paths:
		slide_path = os.path.join(slides_dir, filename)
		tree = etree.parse(slide_path)
		slide_root = tree.getroot()
		shape_ids, warnings = resolve_shape_ids(slide_root)
		if shape_ids:
			rels_name = f"{filename}.rels"
			rels_path = os.path.join(rel_dir, rels_name)
			if not os.path.exists(rels_path):
				raise FileNotFoundError(f"Missing slide rels: {rels_path}")
			return (slide_path, rels_path, shape_ids, warnings)
	raise ValueError("No template slide found with required text shapes.")


#============================================
def resolve_shape_ids(slide_root) -> tuple[dict[str, str], list[str]]:
	"""
	Resolve required shape ids from a slide.

	Args:
		slide_root: Slide XML root.

	Returns:
		tuple[dict[str, str], list[str]]: Shape id map and warnings.
	"""
	warnings: list[str] = []
	name_map = build_shape_name_map(slide_root)
	question_id = name_map.get(normalize_shape_name(SHAPE_NAME_QUESTION), "")
	options_id = name_map.get(normalize_shape_name(SHAPE_NAME_OPTIONS), "")
	popup_id = name_map.get(normalize_shape_name(SHAPE_NAME_POPUP), "")
	if not popup_id:
		popup_id = find_animation_target_id(slide_root)
		if popup_id:
			warnings.append("Using animation target for popup shape id.")
	if not question_id:
		question_id = find_placeholder_id(slide_root, ["title", "ctrTitle"])
		if question_id:
			warnings.append("Using title placeholder for question text.")
	if not options_id:
		options_id = find_placeholder_id(slide_root, ["body"])
		if not options_id:
			options_id = find_placeholder_id(slide_root, [], exclude_ids=[question_id])
		if options_id:
			warnings.append("Using body placeholder for options text.")
	if not (question_id and options_id and popup_id):
		return ({}, warnings)
	return (
		{
			"question": question_id,
			"options": options_id,
			"popup": popup_id,
		},
		warnings,
	)


#============================================
def build_shape_name_map(slide_root) -> dict[str, str]:
	"""
	Build a map of normalized shape names to ids.

	Args:
		slide_root: Slide XML root.

	Returns:
		dict[str, str]: Name to id mapping.
	"""
	name_map: dict[str, str] = {}
	for element in slide_root.findall(".//p:cNvPr", PRESENTATION_NS):
		name = element.get("name", "")
		shape_id = element.get("id", "")
		normalized = normalize_shape_name(name)
		if not normalized or not shape_id:
			continue
		name_map[normalized] = shape_id
	return name_map


#============================================
def normalize_shape_name(name: str) -> str:
	"""
	Normalize a shape name for comparisons.

	Args:
		name: Shape name.

	Returns:
		str: Normalized name.
	"""
	return (name or "").strip().upper()


#============================================
def find_animation_target_id(slide_root) -> str:
	"""
	Return the first animation target shape id, if present.

	Args:
		slide_root: Slide XML root.

	Returns:
		str: Shape id or empty string.
	"""
	target = slide_root.find(".//p:timing//p:spTgt", PRESENTATION_NS)
	if target is None:
		return ""
	shape_id = target.get("spid", "")
	return shape_id or ""


#============================================
def find_placeholder_id(
	slide_root,
	types: list[str],
	exclude_ids: list[str] | None = None,
) -> str:
	"""
	Find a placeholder shape id by type.

	Args:
		slide_root: Slide XML root.
		types: Placeholder types to match (empty to match any placeholder).
		exclude_ids: Shape ids to skip.

	Returns:
		str: Shape id or empty string.
	"""
	ignore = set(exclude_ids or [])
	for placeholder in slide_root.findall(".//p:ph", PRESENTATION_NS):
		nv_pr = placeholder.getparent()
		if nv_pr is None:
			continue
		nv_sp_pr = nv_pr.getparent()
		if nv_sp_pr is None:
			continue
		shape = nv_sp_pr.getparent()
		if shape is None:
			continue
		nv = shape.find("p:nvSpPr/p:cNvPr", PRESENTATION_NS)
		if nv is None:
			continue
		shape_id = nv.get("id", "")
		if not shape_id or shape_id in ignore:
			continue
		ph_type = placeholder.get("type", "")
		if types and ph_type not in types:
			continue
		return shape_id
	return ""
