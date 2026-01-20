import argparse
import math
import os
import shutil
import subprocess
import tempfile

# PIP3 modules
import pptx
import pptx.enum.shapes
import pptx.util

# local repo modules
import slide_csv


LAYOUT_HINT_ALIASES = {
	"title_and_object": "title_and_content",
	"title_only": "section_header",
	"two_content": "two_column",
}


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Rebuild a PPTX from a merged slide CSV."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_csv",
		required=True,
		help="Input merged CSV path",
	)
	parser.add_argument(
		"-o",
		"--output",
		dest="output_path",
		required=True,
		help="Output PPTX or ODP path",
	)
	parser.add_argument(
		"-a",
		"--assets-dir",
		dest="assets_dir",
		default="",
		help="Assets directory (default: <input_csv>_assets)",
	)
	parser.add_argument(
		"-t",
		"--template",
		dest="template_path",
		default="",
		help="Template PPTX path",
	)
	args = parser.parse_args()
	return args


#============================================
def convert_pptx_to_odp(pptx_path: str, output_path: str) -> None:
	"""
	Convert a PPTX to ODP using soffice.

	Args:
		pptx_path: Path to PPTX file.
		output_path: Desired ODP output path.
	"""
	soffice_bin = shutil.which("soffice")
	if not soffice_bin:
		raise FileNotFoundError("soffice not found. Install LibreOffice to convert ODP.")
	output_dir = os.path.dirname(output_path) or "."
	command = [
		soffice_bin,
		"--headless",
		"--convert-to",
		"odp",
		"--outdir",
		output_dir,
		pptx_path,
	]
	result = subprocess.run(command, capture_output=True, text=True, cwd=output_dir)
	if result.returncode != 0:
		message = result.stderr.strip() or result.stdout.strip()
		raise RuntimeError(f"PPTX to ODP conversion failed: {message}")
	expected_name = f"{os.path.splitext(os.path.basename(pptx_path))[0]}.odp"
	converted_path = os.path.join(output_dir, expected_name)
	if not os.path.exists(converted_path):
		raise FileNotFoundError(f"Converted ODP not found: {converted_path}")
	if os.path.abspath(converted_path) != os.path.abspath(output_path):
		os.replace(converted_path, output_path)


#============================================
def normalize_layout_name(name: str) -> str:
	"""
	Normalize a layout name to a hint token.

	Args:
		name: Layout name.

	Returns:
		str: Normalized name.
	"""
	if not name:
		return ""
	return name.strip().lower().replace(" ", "_")


#============================================
def select_layout(presentation: pptx.Presentation, layout_hint: str) -> pptx.slide.SlideLayout:
	"""
	Select a slide layout based on a hint.

	Args:
		presentation: Presentation instance.
		layout_hint: Layout hint token.

	Returns:
		pptx.slide.SlideLayout: Selected layout.
	"""
	layout_map = {}
	for layout in presentation.slide_layouts:
		key = normalize_layout_name(layout.name)
		if key and key not in layout_map:
			layout_map[key] = layout
	hint = normalize_layout_name(layout_hint)
	if hint in layout_map:
		return layout_map[hint]
	alias = LAYOUT_HINT_ALIASES.get(hint)
	if alias and alias in layout_map:
		return layout_map[alias]
	if presentation.slide_layouts:
		return presentation.slide_layouts[0]
	raise ValueError("No slide layouts available in template.")


#============================================
def parse_body_lines(body_text: str) -> list[tuple[int, str]]:
	"""
	Parse body text into indentation levels.

	Args:
		body_text: Body text with leading tabs for indentation.

	Returns:
		list[tuple[int, str]]: List of (level, text).
	"""
	if not body_text:
		return []
	lines = []
	cleaned = body_text.replace("\r\n", "\n").replace("\r", "\n")
	for raw_line in cleaned.split("\n"):
		if not raw_line.strip():
			continue
		level = len(raw_line) - len(raw_line.lstrip("\t"))
		text = raw_line.lstrip("\t").strip()
		lines.append((level, text))
	return lines


#============================================
def set_title(slide: pptx.slide.Slide, title_text: str) -> None:
	"""
	Set the slide title if a title placeholder exists.

	Args:
		slide: Slide instance.
		title_text: Title text.
	"""
	if not title_text:
		return
	title_shape = slide.shapes.title
	if not title_shape:
		return
	if not title_shape.text_frame:
		return
	title_shape.text_frame.text = title_text


#============================================
def find_body_placeholder(slide: pptx.slide.Slide) -> pptx.shapes.base.BaseShape | None:
	"""
	Find the primary body placeholder on a slide.

	Args:
		slide: Slide instance.

	Returns:
		pptx.shapes.base.BaseShape | None: Body shape or None.
	"""
	for shape in slide.shapes:
		if not shape.is_placeholder:
			continue
		placeholder_type = shape.placeholder_format.type
		if placeholder_type == pptx.enum.shapes.PP_PLACEHOLDER.BODY:
			return shape
	for shape in slide.shapes:
		if shape.has_text_frame and shape != slide.shapes.title:
			return shape
	return None


#============================================
def set_body_text(slide: pptx.slide.Slide, body_text: str) -> None:
	"""
	Set the body text in the best placeholder.

	Args:
		slide: Slide instance.
		body_text: Body text with indentation markers.
	"""
	lines = parse_body_lines(body_text)
	if not lines:
		return
	body_shape = find_body_placeholder(slide)
	if not body_shape:
		return
	text_frame = body_shape.text_frame
	if not text_frame:
		return
	text_frame.clear()
	for index, (level, text) in enumerate(lines):
		if index == 0:
			paragraph = text_frame.paragraphs[0]
		else:
			paragraph = text_frame.add_paragraph()
		paragraph.text = text
		paragraph.level = level


#============================================
def resolve_assets_dir(input_csv: str, assets_dir: str) -> str:
	"""
	Resolve the assets directory.

	Args:
		input_csv: Input CSV path.
		assets_dir: Assets directory or empty string.

	Returns:
		str: Resolved assets directory.
	"""
	resolved_dir = assets_dir
	if not resolved_dir:
		base_name = os.path.splitext(input_csv)[0]
		resolved_dir = f"{base_name}_assets"
	return resolved_dir


#============================================
def build_image_paths(assets_dir: str, image_refs: list[str]) -> list[str]:
	"""
	Resolve image reference filenames to full paths.

	Args:
		assets_dir: Assets directory.
		image_refs: Image reference filenames.

	Returns:
		list[str]: Full image paths.
	"""
	paths = []
	for ref in image_refs:
		path = os.path.join(assets_dir, ref)
		if not os.path.exists(path):
			raise FileNotFoundError(f"Missing image asset: {path}")
		paths.append(path)
	return paths


#============================================
def place_images_grid(slide: pptx.slide.Slide, image_paths: list[str]) -> None:
	"""
	Place images on a slide using a simple grid.

	Args:
		slide: Slide instance.
		image_paths: Image file paths.
	"""
	if not image_paths:
		return
	cols = 1
	if len(image_paths) > 1:
		cols = 2
	rows = int(math.ceil(len(image_paths) / cols))
	margin = pptx.util.Inches(0.5)
	slide_width = slide.part.presentation.slide_width
	slide_height = slide.part.presentation.slide_height
	cell_width = (slide_width - (margin * (cols + 1))) // cols
	cell_height = (slide_height - (margin * (rows + 1))) // rows
	for index, image_path in enumerate(image_paths):
		row = index // cols
		col = index % cols
		left = margin + (cell_width + margin) * col
		top = margin + (cell_height + margin) * row
		slide.shapes.add_picture(
			image_path,
			left,
			top,
			width=cell_width,
			height=cell_height,
		)


#============================================
def insert_images(slide: pptx.slide.Slide, image_paths: list[str]) -> None:
	"""
	Insert images into a slide.

	Args:
		slide: Slide instance.
		image_paths: Image file paths.
	"""
	if not image_paths:
		return
	picture_placeholders = []
	for shape in slide.shapes:
		if not shape.is_placeholder:
			continue
		if shape.placeholder_format.type == pptx.enum.shapes.PP_PLACEHOLDER.PICTURE:
			picture_placeholders.append(shape)
	if len(image_paths) == 1 and picture_placeholders:
		picture_placeholders[0].insert_picture(image_paths[0])
		return
	place_images_grid(slide, image_paths)


#============================================
def rebuild_from_csv(
	input_csv: str,
	output_path: str,
	assets_dir: str,
	template_path: str,
) -> None:
	"""
	Rebuild a presentation from CSV rows.

	Args:
		input_csv: Input merged CSV path.
		output_path: Output PPTX or ODP path.
		assets_dir: Assets directory.
		template_path: Template PPTX path or empty string.
	"""
	resolved_assets_dir = resolve_assets_dir(input_csv, assets_dir)
	rows = slide_csv.read_slide_csv(input_csv)
	if template_path:
		presentation = pptx.Presentation(template_path)
	else:
		presentation = pptx.Presentation()
	for row in rows:
		layout = select_layout(presentation, row["layout_hint"])
		slide = presentation.slides.add_slide(layout)
		set_title(slide, row["title_text"])
		set_body_text(slide, row["body_text"])
		image_refs = slide_csv.split_list_field(row["image_refs"])
		image_paths = build_image_paths(resolved_assets_dir, image_refs)
		insert_images(slide, image_paths)
	if output_path.lower().endswith(".odp"):
		with tempfile.TemporaryDirectory() as temp_dir:
			temp_pptx = os.path.join(temp_dir, "merged.pptx")
			presentation.save(temp_pptx)
			convert_pptx_to_odp(temp_pptx, output_path)
		return
	presentation.save(output_path)


#============================================
def main() -> None:
	"""
	Main entry point.
	"""
	args = parse_args()
	rebuild_from_csv(
		args.input_csv,
		args.output_path,
		args.assets_dir,
		args.template_path,
	)


if __name__ == "__main__":
	main()
