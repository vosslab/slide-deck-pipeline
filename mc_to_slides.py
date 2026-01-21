#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.mc_parser as mc_parser
import slide_deck_pipeline.mc_to_slides as mc_to_slides
import slide_deck_pipeline.reporting as reporting


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Render multiple choice slides from quiz text."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_path",
		required=True,
		help="Quiz text file",
	)
	parser.add_argument(
		"-o",
		"--output",
		dest="output_path",
		default="",
		help="Output PPTX path (default: <input>.pptx)",
	)
	parser.add_argument(
		"--strict",
		dest="strict",
		help="Treat invalid questions as errors",
		action="store_true",
	)
	parser.add_argument(
		"--preserve-newlines",
		dest="preserve_newlines",
		help="Preserve prompt and feedback line breaks",
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
		base_name = os.path.splitext(args.input_path)[0]
		output_path = f"{base_name}.pptx"
	with open(args.input_path, "r", encoding="utf-8") as handle:
		content = handle.read()
	questions, warnings, stats = mc_parser.parse_questions(content, args.strict)
	template_warnings = mc_to_slides.render_questions_to_pptx(
		questions,
		output_path,
		args.preserve_newlines,
	)
	warnings.extend(template_warnings)
	reporting.print_summary("Questions parsed", stats["total_questions"])
	reporting.print_summary("Slides generated", len(questions))
	reporting.print_summary("Questions skipped", stats["skipped_questions"])
	reporting.print_warnings(warnings)
	print(f"Wrote output: {output_path}")


if __name__ == "__main__":
	main()
