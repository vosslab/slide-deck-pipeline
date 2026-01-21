#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.csv_schema as csv_schema
import slide_deck_pipeline.csv_validation as csv_validation


normalize_row_value = csv_validation.normalize_row_value
is_positive_int = csv_validation.is_positive_int
is_hex_hash = csv_validation.is_hex_hash
load_template_layout_types = csv_validation.load_template_layout_types
validate_rows = csv_validation.validate_rows
format_messages = csv_validation.format_messages


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Validate a merged slide CSV and related sources."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_csv",
		required=True,
		help="Input merged CSV path",
	)
	parser.add_argument(
		"-t",
		"--template",
		dest="template_path",
		default="",
		help="Template PPTX path for master/layout validation",
	)
	parser.add_argument(
		"-c",
		"--check-sources",
		dest="check_sources",
		help="Check source PPTX or ODP files exist",
		action="store_true",
	)
	parser.add_argument(
		"-C",
		"--no-check-sources",
		dest="check_sources",
		help="Skip source file checks",
		action="store_false",
	)
	parser.set_defaults(check_sources=True)
	parser.add_argument(
		"-s",
		"--strict",
		dest="strict",
		help="Require slide hashes to match source slides",
		action="store_true",
	)
	parser.add_argument(
		"-S",
		"--no-strict",
		dest="strict",
		help="Skip slide hash validation",
		action="store_false",
	)
	parser.set_defaults(strict=False)
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""
	Main entry point.
	"""
	args = parse_args()
	rows = csv_schema.read_slide_csv(args.input_csv)
	csv_dir = os.path.dirname(os.path.abspath(args.input_csv))
	errors, warnings = validate_rows(
		rows,
		csv_dir,
		args.check_sources,
		args.strict,
		args.template_path,
	)
	if warnings:
		for line in format_messages("WARN", warnings):
			print(line)
	if errors:
		for line in format_messages("ERROR", errors):
			print(line)
		raise RuntimeError(f"CSV validation failed with {len(errors)} errors.")
	print("CSV validation OK.")


if __name__ == "__main__":
	main()
