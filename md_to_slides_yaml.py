#!/usr/bin/env python3

import argparse
import os

# PIP3 modules
import yaml

# local repo modules
import slide_deck_pipeline.md_to_slides_yaml as md_to_slides_yaml


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Convert constrained Markdown to slides YAML."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_path",
		required=True,
		help="Markdown input file",
	)
	parser.add_argument(
		"-o",
		"--output",
		dest="output_path",
		default="",
		help="Output YAML path (default: <input>.yaml)",
	)
	args = parser.parse_args()
	return args


#============================================
def write_yaml(output_path: str, payload: dict) -> None:
	"""
	Write a YAML file.

	Args:
		output_path: YAML output path.
		payload: Spec payload.
	"""
	with open(output_path, "w", encoding="utf-8") as handle:
		yaml.safe_dump(
			payload,
			handle,
			default_flow_style=False,
			sort_keys=False,
			allow_unicode=False,
		)


#============================================
def main() -> None:
	"""
	Main entry point.
	"""
	args = parse_args()
	output_path = args.output_path
	if not output_path:
		base_name = os.path.splitext(args.input_path)[0]
		output_path = f"{base_name}.yaml"
	payload = md_to_slides_yaml.markdown_to_spec(args.input_path)
	write_yaml(output_path, payload)
	print(f"Wrote YAML: {output_path}")


if __name__ == "__main__":
	main()
