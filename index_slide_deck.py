#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import tempfile

# PIP3 modules
import pptx
import pptx.enum.shapes

# local repo modules
import slide_deck_pipeline.csv_schema as csv_schema


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Index slide content into a CSV."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_path",
		required=True,
		help="Input PPTX or ODP file",
	)
	parser.add_argument(
		"-o",
		"--output",
		dest="output_csv",
		default="",
		help="Output CSV path (default: <input>.csv)",
	)
	args = parser.parse_args()
	return args


#============================================
def convert_odp_to_pptx(odp_path: str, work_dir: str) -> str:
	"""
	Convert an ODP file to PPTX using soffice.

	Args:
		odp_path: Path to the ODP file.
		work_dir: Output directory for the converted PPTX.

	Returns:
		str: Path to the converted PPTX file.
	"""
	soffice_bin = shutil.which("soffice")
	if not soffice_bin:
		raise FileNotFoundError("soffice not found. Install LibreOffice to convert ODP.")
	command = [
		soffice_bin,
		"--headless",
		"--convert-to",
		"pptx",
		"--outdir",
		work_dir,
		odp_path,
	]
	result = subprocess.run(command, capture_output=True, text=True, cwd=work_dir)
	if result.returncode != 0:
		message = result.stderr.strip() or result.stdout.strip()
		raise RuntimeError(f"ODP conversion failed: {message}")
	base_name = os.path.splitext(os.path.basename(odp_path))[0]
	pptx_path = os.path.join(work_dir, f"{base_name}.pptx")
	if not os.path.exists(pptx_path):
		raise FileNotFoundError(f"Converted PPTX not found: {pptx_path}")
	return pptx_path


#============================================
def resolve_input_pptx(input_path: str, temp_dir: str | None) -> tuple[str, str]:
	"""
	Return a PPTX path and a source basename for CSV rows.

	Args:
		input_path: Input PPTX or ODP path.
		temp_dir: Temporary directory for conversions, or None.

	Returns:
		tuple[str, str]: Resolved PPTX path and source basename.
	"""
	source_name = os.path.basename(input_path)
	lowered = input_path.lower()
	if lowered.endswith(".pptx"):
		return (input_path, source_name)
	if lowered.endswith(".odp"):
		if not temp_dir:
			raise ValueError("Temporary directory required for ODP conversion.")
		pptx_path = convert_odp_to_pptx(input_path, temp_dir)
		return (pptx_path, source_name)
	raise ValueError("Input must be a .pptx or .odp file.")


#============================================
def extract_paragraph_lines(text_frame: pptx.text.text.TextFrame) -> list[str]:
	"""
	Extract text frame paragraphs with indentation markers.

	Args:
		text_frame: TextFrame instance.

	Returns:
		list[str]: Lines with leading tab indentation.
	"""
	lines = []
	for paragraph in text_frame.paragraphs:
		text = paragraph.text.strip()
		if not text:
			continue
		indent = "\t" * paragraph.level
		lines.append(f"{indent}{text}")
	return lines


#============================================
def extract_table_text(table: pptx.table.Table) -> list[str]:
	"""
	Extract text from a table.

	Args:
		table: Table instance.

	Returns:
		list[str]: Table cell lines.
	"""
	lines = []
	for row in table.rows:
		for cell in row.cells:
			if not cell.text_frame:
				continue
			lines.extend(extract_paragraph_lines(cell.text_frame))
	return lines


#============================================
def extract_chart_title_text(chart) -> list[str]:
	"""
	Extract chart title text when available.

	Args:
		chart: Chart instance.

	Returns:
		list[str]: Chart title lines.
	"""
	if not chart:
		return []
	if not getattr(chart, "has_title", False):
		return []
	chart_title = getattr(chart, "chart_title", None)
	if not chart_title or not getattr(chart_title, "text_frame", None):
		return []
	return extract_paragraph_lines(chart_title.text_frame)


#============================================
def extract_shape_text(shape) -> list[str]:
	"""
	Extract text from a shape, including tables and chart titles.

	Args:
		shape: Shape instance.

	Returns:
		list[str]: Text lines.
	"""
	lines = []
	if (
		getattr(shape, "shape_type", None)
		== pptx.enum.shapes.MSO_SHAPE_TYPE.GROUP
		and hasattr(shape, "shapes")
	):
		for nested in shape.shapes:
			lines.extend(extract_shape_text(nested))
		return lines
	if getattr(shape, "has_text_frame", False):
		lines.extend(extract_paragraph_lines(shape.text_frame))
	if getattr(shape, "has_table", False):
		lines.extend(extract_table_text(shape.table))
	if getattr(shape, "has_chart", False):
		lines.extend(extract_chart_title_text(shape.chart))
	return lines


#============================================
def extract_body_text(slide: pptx.slide.Slide) -> str:
	"""
	Extract body text from non-title text frames.

	Args:
		slide: Slide instance.

	Returns:
		str: Body text with newline separators.
	"""
	lines = []
	title_shape = slide.shapes.title
	for shape in slide.shapes:
		if title_shape and shape == title_shape:
			continue
		lines.extend(extract_shape_text(shape))
	return "\n".join(lines)


#============================================
def extract_notes_text(slide: pptx.slide.Slide) -> str:
	"""
	Extract speaker notes text from a slide.

	Args:
		slide: Slide instance.

	Returns:
		str: Notes text.
	"""
	if not slide.has_notes_slide:
		return ""
	notes_frame = slide.notes_slide.notes_text_frame
	if not notes_frame:
		return ""
	return notes_frame.text or ""


#============================================
def extract_slide_text(slide: pptx.slide.Slide) -> str:
	"""
	Extract all on-slide text for hashing.

	Args:
		slide: Slide instance.

	Returns:
		str: Slide text.
	"""
	lines = []
	for shape in slide.shapes:
		lines.extend(extract_shape_text(shape))
	return "\n".join(lines)


#============================================
def build_slide_row(
	source_name: str,
	slide_index: int,
	title_text: str,
	body_text: str,
	notes_text: str,
	slide_text: str,
	master_name: str,
	layout_name: str,
) -> dict[str, str]:
	"""
	Build a CSV row for a slide.

	Args:
		source_name: Source PPTX basename.
		slide_index: 1-based slide index.
		title_text: Title text.
		body_text: Body text.
		notes_text: Notes text.
		master_name: Template master name.
		layout_name: Template layout name.

	Returns:
		dict[str, str]: CSV row.
	"""
	slide_hash = csv_schema.compute_slide_hash(source_name, slide_index, slide_text)
	return {
		"source_pptx": source_name,
		"source_slide_index": str(slide_index),
		"slide_hash": slide_hash,
		"master_name": master_name,
		"layout_name": layout_name,
		"title_text": title_text,
		"body_text": body_text,
		"notes_text": notes_text,
	}


#============================================
def index_slides_to_csv(input_path: str, output_csv: str) -> None:
	"""
	Index slides to CSV.

	Args:
		input_path: Input PPTX or ODP path.
		output_csv: Output CSV path.
	"""
	needs_conversion = input_path.lower().endswith(".odp")
	if needs_conversion:
		with tempfile.TemporaryDirectory() as temp_dir:
			pptx_path, source_name = resolve_input_pptx(input_path, temp_dir)
			rows = index_rows(pptx_path, source_name)
	else:
		pptx_path, source_name = resolve_input_pptx(input_path, None)
		rows = index_rows(pptx_path, source_name)
	csv_schema.write_slide_csv(output_csv, rows)


#============================================
def index_rows(
	pptx_path: str,
	source_name: str,
) -> list[dict[str, str]]:
	"""
	Index rows from a PPTX path.

	Args:
		pptx_path: Path to PPTX.
		source_name: Source basename for CSV rows.

	Returns:
		list[dict[str, str]]: CSV rows.
	"""
	presentation = pptx.Presentation(pptx_path)
	rows = []
	for index, slide in enumerate(presentation.slides, 1):
		title_text = ""
		if slide.shapes.title and slide.shapes.title.text_frame:
			title_text = slide.shapes.title.text_frame.text or ""
		body_text = extract_body_text(slide)
		notes_text = extract_notes_text(slide)
		slide_text = extract_slide_text(slide)
		layout_name = slide.slide_layout.name
		row = build_slide_row(
			source_name,
			index,
			title_text,
			body_text,
			notes_text,
			slide_text,
			"",
			layout_name,
		)
		rows.append(row)
	return rows


#============================================
def main() -> None:
	"""
	Main entry point.
	"""
	args = parse_args()
	output_csv = args.output_csv
	if not output_csv:
		base_name = os.path.splitext(args.input_path)[0]
		output_csv = f"{base_name}.csv"
	index_slides_to_csv(args.input_path, output_csv)


if __name__ == "__main__":
	main()
