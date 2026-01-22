#!/usr/bin/env python3

# Standard Library
import argparse
import csv
import os


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Set master_name for every row in a slide CSV."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_csv",
		default="merged.csv",
		help="Input CSV path (default: merged.csv)",
	)
	parser.add_argument(
		"-o",
		"--output",
		dest="output_csv",
		default="",
		help="Output CSV path (default: <input>_master.csv)",
	)
	parser.add_argument(
		"--inplace",
		dest="inplace",
		help="Overwrite the input CSV in-place",
		action="store_true",
	)
	parser.add_argument(
		"-m",
		"--master-name",
		dest="master_name",
		required=True,
		help="Master name to set (example: custom)",
	)
	parser.add_argument(
		"--only-empty",
		dest="only_empty",
		help="Only set master_name when it is empty",
		action="store_true",
	)
	args = parser.parse_args()
	return args


#============================================
def load_rows(path: str) -> tuple[list[str], list[dict[str, str]]]:
	"""
	Load CSV fieldnames and rows.

	Args:
		path: CSV path.

	Returns:
		tuple[list[str], list[dict[str, str]]]: (fieldnames, rows).
	"""
	with open(path, newline="", encoding="utf-8") as handle:
		reader = csv.DictReader(handle)
		fieldnames = list(reader.fieldnames or [])
		return (fieldnames, list(reader))


#============================================
def write_rows(path: str, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
	"""
	Write rows to a CSV file.

	Args:
		path: Output path.
		fieldnames: Column names.
		rows: Row dicts.
	"""
	with open(path, "w", newline="", encoding="utf-8") as handle:
		writer = csv.DictWriter(handle, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(rows)


#============================================
def apply_master_name_to_rows(
	rows: list[dict[str, str]],
	master_name: str,
	only_empty: bool,
) -> tuple[int, int]:
	"""
	Apply master_name to rows.

	Args:
		rows: CSV rows (mutated in-place).
		master_name: Master name value to set.
		only_empty: Only set when master_name is empty.

	Returns:
		tuple[int, int]: (updated, skipped)
	"""
	updated = 0
	skipped = 0
	for row in rows:
		if only_empty and (row.get("master_name") or "").strip():
			skipped += 1
			continue
		row["master_name"] = master_name
		updated += 1
	return (updated, skipped)


#============================================
def main() -> None:
	"""
	Main entry point.
	"""
	args = parse_args()
	if args.inplace and args.output_csv:
		raise ValueError("Use either --inplace or --output, not both.")

	output_csv = args.output_csv
	if args.inplace:
		output_csv = args.input_csv
	elif not output_csv:
		base, ext = os.path.splitext(args.input_csv)
		output_csv = f"{base}_master{ext or '.csv'}"

	fieldnames, rows = load_rows(args.input_csv)
	if "master_name" not in fieldnames:
		raise ValueError("CSV missing required column: master_name")

	updated, skipped = apply_master_name_to_rows(
		rows,
		args.master_name,
		args.only_empty,
	)

	write_rows(output_csv, fieldnames, rows)
	print(f"Wrote output: {output_csv}")
	print(f"Rows:        {len(rows)}")
	print(f"Updated:     {updated}")
	print(f"Skipped:     {skipped}")


if __name__ == "__main__":
	main()
