#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.reporting as reporting
import slide_deck_pipeline.spec_schema as spec_schema
import slide_deck_pipeline.text_to_slides as text_to_slides


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Render slides from a YAML spec."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_path",
		required=True,
		help="YAML spec file",
	)
	parser.add_argument(
		"-t",
		"--template",
		dest="template_path",
		default="",
		help="Template PPTX path (optional)",
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
		help="Treat warnings as errors",
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
	template_override = args.template_path or None
	spec, warnings = spec_schema.load_yaml_spec(
		args.input_path,
		template_override=template_override,
		strict=args.strict,
	)
	if warnings and args.strict:
		raise ValueError("Strict mode enabled with warnings.")
	text_to_slides.render_to_pptx(
		spec,
		args.input_path,
		template_override,
		output_path,
		args.strict,
	)
	reporting.print_warnings(warnings)


if __name__ == "__main__":
	main()
