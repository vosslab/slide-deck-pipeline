#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.indexing as indexing


extract_paragraph_lines = indexing.extract_paragraph_lines
extract_body_text = indexing.extract_body_text
extract_notes_text = indexing.extract_notes_text
collect_asset_types = indexing.collect_asset_types
describe_shape_type = indexing.describe_shape_type
is_supported_shape = indexing.is_supported_shape
collect_unsupported_shapes = indexing.collect_unsupported_shapes
resolve_master_name = indexing.resolve_master_name
report_index_warnings = indexing.report_index_warnings
report_layout_confidence = indexing.report_layout_confidence
build_slide_row = indexing.build_slide_row
index_rows = indexing.index_rows
index_slides_to_csv = indexing.index_slides_to_csv


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
