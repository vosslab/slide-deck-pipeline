#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.aspect_fixer as aspect_fixer


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Fix picture aspect ratios in a PPTX or ODP file."
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
		help="Output PPTX or ODP path (default: <input>_aspect_fixed.pptx)",
	)
	parser.add_argument(
		"--inplace",
		dest="inplace",
		help="Allow writing edits to the input file",
		action="store_true",
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
		base_name, extension = os.path.splitext(args.input_path)
		if extension.lower() not in (".pptx", ".odp"):
			extension = ".pptx"
		output_path = f"{base_name}_aspect_fixed{extension}"
	total, adjusted = aspect_fixer.fix_aspect(
		args.input_path,
		output_path,
		args.inplace,
	)
	print(f"Pictures inspected: {total}")
	print(f"Pictures adjusted: {adjusted}")
	print(f"Wrote output: {output_path}")


if __name__ == "__main__":
	main()
