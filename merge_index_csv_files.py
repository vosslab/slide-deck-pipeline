#!/usr/bin/env python3

# Standard Library
import argparse
import glob
import os

# local repo modules
import slide_deck_pipeline.csv_schema as csv_schema


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Merge slide index CSV files into one CSV."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_paths",
		required=True,
		nargs="+",
		help="Input CSV paths or glob patterns",
	)
	parser.add_argument(
		"-o",
		"--output",
		dest="output_path",
		default="merged.csv",
		help="Output CSV path (default: merged.csv)",
	)
	parser.add_argument(
		"--sort-by",
		dest="sort_by",
		default="",
		choices=csv_schema.CSV_COLUMNS,
		help="Sort by a CSV column",
	)
	args = parser.parse_args()
	return args


#============================================
def expand_inputs(input_paths: list[str]) -> list[str]:
	"""
	Expand glob patterns into concrete file paths.

	Args:
		input_paths: Input paths or glob patterns.

	Returns:
		list[str]: Expanded file paths.
	"""
	expanded: list[str] = []
	seen: set[str] = set()
	for entry in input_paths:
		paths = []
		if glob.has_magic(entry):
			paths = sorted(glob.glob(entry))
			if not paths:
				raise FileNotFoundError(f"No matches for pattern: {entry}")
		else:
			paths = [entry]
		for path in paths:
			if path in seen:
				continue
			seen.add(path)
			expanded.append(path)
	return expanded


#============================================
def sort_rows(
	rows: list[dict[str, str]],
	sort_by: str,
) -> list[dict[str, str]]:
	"""
	Sort rows by a column with numeric auto-detection.

	Args:
		rows: CSV rows to sort.
		sort_by: Column name to sort by.

	Returns:
		list[dict[str, str]]: Sorted rows.
	"""
	if not sort_by:
		return list(rows)
	values = [row.get(sort_by, "") for row in rows]
	numeric_values = [value for value in values if value != ""]
	use_numeric = numeric_values and all(value.isdigit() for value in numeric_values)
	if use_numeric:
		# Keep non-numeric values at the end if they appear.
		def sort_key(row: dict[str, str]) -> tuple[int, int | str]:
			value = row.get(sort_by, "")
			if value.isdigit():
				return (0, int(value))
			if value:
				return (1, value)
			return (2, "")
		sorted_rows = sorted(rows, key=sort_key)
		return sorted_rows
	def sort_key(row: dict[str, str]) -> str:
		value = row.get(sort_by, "")
		return value.lower()
	sorted_rows = sorted(rows, key=sort_key)
	return sorted_rows


#============================================
def main() -> None:
	"""
	Main entry point.
	"""
	args = parse_args()
	input_paths = expand_inputs(args.input_paths)
	rows = []
	for path in input_paths:
		if not os.path.exists(path):
			raise FileNotFoundError(f"CSV file not found: {path}")
		rows.extend(csv_schema.read_slide_csv(path))
	if args.sort_by:
		rows = sort_rows(rows, args.sort_by)
	csv_schema.write_slide_csv(args.output_path, rows)
	print(f"Merged {len(input_paths)} files into {args.output_path}.")
	print(f"Rows written: {len(rows)}")


if __name__ == "__main__":
	main()
