#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.text_export as text_export


build_box_record = text_export.build_box_record
export_slide_text = text_export.export_slide_text
write_yaml = text_export.write_yaml


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Export slide text blocks to a YAML patch file."
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
		dest="output_path",
		default="",
		help="Output YAML path (default: <input>_text_edits.yaml)",
	)
	parser.add_argument(
		"-n",
		"--include-notes",
		dest="include_notes",
		help="Include speaker notes blocks",
		action="store_true",
	)
	parser.add_argument(
		"-N",
		"--no-include-notes",
		dest="include_notes",
		help="Skip speaker notes blocks",
		action="store_false",
	)
	parser.set_defaults(include_notes=False)
	parser.add_argument(
		"-s",
		"--include-subtitle",
		dest="include_subtitle",
		help="Include subtitle placeholders",
		action="store_true",
	)
	parser.add_argument(
		"-S",
		"--no-include-subtitle",
		dest="include_subtitle",
		help="Skip subtitle placeholders",
		action="store_false",
	)
	parser.set_defaults(include_subtitle=False)
	parser.add_argument(
		"-f",
		"--include-footer",
		dest="include_footer",
		help="Include footer placeholders",
		action="store_true",
	)
	parser.add_argument(
		"-F",
		"--no-include-footer",
		dest="include_footer",
		help="Skip footer placeholders",
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
	output_path = args.output_path
	if not output_path:
		base_name = os.path.splitext(args.input_path)[0]
		output_path = f"{base_name}_text_edits.yaml"
	export_slide_text(
		args.input_path,
		output_path,
		args.include_notes,
		args.include_subtitle,
		args.include_footer,
	)


if __name__ == "__main__":
	main()
