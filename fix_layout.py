#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.layout_fixer as layout_fixer


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Fix slide layouts by rearranging text based on sensible rules (title length, title vs body size, etc.)."
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
		help="Output PPTX or ODP path (default: <input>_layout_fixed.pptx)",
	)
	parser.add_argument(
		"--inplace",
		dest="inplace",
		help="Allow writing edits to the input file",
		action="store_true",
	)
	parser.add_argument(
		"-v",
		"--verbose",
		dest="verbose",
		help="Show analysis for all slides, not just changed ones",
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
		if args.inplace:
			output_path = args.input_path
		else:
			base_name, extension = os.path.splitext(args.input_path)
			if extension.lower() not in (".pptx", ".odp"):
				extension = ".pptx"
			output_path = f"{base_name}_layout_fixed{extension}"

	print("\nAnalyzing and fixing layouts...")
	slides, swaps, moves = layout_fixer.fix_layout(
		args.input_path,
		output_path,
		args.inplace,
		args.verbose,
	)
	print(f"\nSummary:")
	print(f"  Slides inspected: {slides}")
	print(f"  Title/body swaps: {swaps}")
	print(f"  Title moves to body: {moves}")
	print(f"  Total changes: {swaps + moves}")
	print(f"\nWrote output: {output_path}")


if __name__ == "__main__":
	main()
