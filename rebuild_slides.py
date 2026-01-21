#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.rebuild as rebuild


normalize_name = rebuild.normalize_name
build_layout_map = rebuild.build_layout_map
select_layout = rebuild.select_layout
parse_body_lines = rebuild.parse_body_lines
set_title = rebuild.set_title
find_body_placeholder = rebuild.find_body_placeholder
set_body_text = rebuild.set_body_text
set_notes_text = rebuild.set_notes_text
collect_source_images = rebuild.collect_source_images
place_images_grid = rebuild.place_images_grid
insert_images = rebuild.insert_images
get_slide_dimensions = rebuild.get_slide_dimensions
rebuild_from_csv = rebuild.rebuild_from_csv


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
		default="",
		help="Output PPTX or ODP path (default: <input_csv>.pptx)",
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
def main() -> None:
	"""
	Main entry point.
	"""
	args = parse_args()
	output_path = args.output_path
	if not output_path:
		base_name = os.path.splitext(args.input_csv)[0]
		output_path = f"{base_name}.pptx"
	rebuild_from_csv(
		args.input_csv,
		output_path,
		args.template_path,
	)


if __name__ == "__main__":
	main()
