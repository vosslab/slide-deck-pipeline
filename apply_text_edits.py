#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.text_editing as text_editing


parse_text_lines = text_editing.parse_text_lines
render_bullets = text_editing.render_bullets
resolve_box_text = text_editing.resolve_box_text
should_skip_box = text_editing.should_skip_box
set_shape_text = text_editing.set_shape_text
apply_text_edits = text_editing.apply_text_edits
apply_and_save = text_editing.apply_and_save
set_notes_text = text_editing.set_notes_text


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Apply text edits from a YAML patch file."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="patch_path",
		required=True,
		help="YAML patch file",
	)
	parser.add_argument(
		"-o",
		"--output",
		dest="output_path",
		default="",
		help="Output PPTX or ODP path (default: <input>_edited.pptx)",
	)
	parser.add_argument(
		"--inplace",
		dest="inplace",
		help="Allow writing edits to the input file",
		action="store_true",
	)
	parser.add_argument(
		"-f",
		"--force",
		dest="force",
		help="Apply edits even if text hashes mismatch",
		action="store_true",
	)
	parser.add_argument(
		"-F",
		"--no-force",
		dest="force",
		help="Skip edits when text hashes mismatch",
		action="store_false",
	)
	parser.set_defaults(force=False)
	parser.add_argument(
		"-s",
		"--include-subtitle",
		dest="include_subtitle",
		help="Include subtitle placeholders in matching",
		action="store_true",
	)
	parser.add_argument(
		"-S",
		"--no-include-subtitle",
		dest="include_subtitle",
		help="Skip subtitle placeholders in matching",
		action="store_false",
	)
	parser.set_defaults(include_subtitle=False)
	parser.add_argument(
		"-r",
		"--include-footer",
		dest="include_footer",
		help="Include footer placeholders in matching",
		action="store_true",
	)
	parser.add_argument(
		"-R",
		"--no-include-footer",
		dest="include_footer",
		help="Skip footer placeholders in matching",
		action="store_false",
	)
	parser.set_defaults(include_footer=False)
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""
	Main entry point.
	"""
	args = parse_args()
	patch_path = args.patch_path
	output_path = args.output_path
	if not output_path:
		base_name = os.path.splitext(patch_path)[0]
		output_path = f"{base_name}_edited.pptx"
	apply_text_edits(
		None,
		patch_path,
		output_path,
		args.force,
		args.include_subtitle,
		args.include_footer,
		args.inplace,
	)
	print(f"Wrote output: {output_path}")


if __name__ == "__main__":
	main()
