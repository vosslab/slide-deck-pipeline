#!/usr/bin/env python3

# Standard Library
import argparse
import csv
import os
import random


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Remove duplicate slides from a slide CSV by randomly selecting one row per hash."
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
		help="Output CSV path (default: <input>_deduped.csv)",
	)
	parser.add_argument(
		"--inplace",
		dest="inplace",
		help="Overwrite the input CSV in-place",
		action="store_true",
	)
	parser.add_argument(
		"--hash-column",
		dest="hash_column",
		default="slide_hash",
		help="Hash column name (default: slide_hash)",
	)
	parser.add_argument(
		"--seed",
		dest="seed",
		default="",
		help="Optional random seed (int) for reproducible selection",
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
def dedupe_rows_random_choice(
	rows: list[dict[str, str]],
	hash_column: str,
	rng: random.Random,
) -> tuple[list[dict[str, str]], int]:
	"""
	Remove duplicates by selecting one row per hash value at random.

	The output preserves the original CSV row order (we keep whichever chosen
	row indices appear in the input).

	Args:
		rows: Input rows.
		hash_column: Column containing a hash key.
		rng: Random generator.

	Returns:
		tuple[list[dict[str, str]], int]: (deduped_rows, removed_count).
	"""
	indices_by_hash: dict[str, list[int]] = {}
	keep_indices: set[int] = set()
	for idx, row in enumerate(rows):
		hash_value = (row.get(hash_column) or "").strip()
		if not hash_value:
			keep_indices.add(idx)
			continue
		indices_by_hash.setdefault(hash_value, []).append(idx)

	removed = 0
	for hash_value, indices in indices_by_hash.items():
		if len(indices) == 1:
			keep_indices.add(indices[0])
			continue
		chosen = rng.choice(indices)
		keep_indices.add(chosen)
		removed += len(indices) - 1

	deduped = [row for idx, row in enumerate(rows) if idx in keep_indices]
	return (deduped, removed)


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
		output_csv = f"{base}_deduped{ext or '.csv'}"

	seed = None
	if str(args.seed).strip() != "":
		if not str(args.seed).strip().lstrip("-").isdigit():
			raise ValueError("--seed must be an integer.")
		seed = int(str(args.seed).strip())
	rng = random.Random(seed)

	fieldnames, rows = load_rows(args.input_csv)
	if args.hash_column not in fieldnames:
		raise ValueError(f"Hash column not found: {args.hash_column}")
	deduped, removed = dedupe_rows_random_choice(rows, args.hash_column, rng)
	write_rows(output_csv, fieldnames, deduped)

	print(f"Wrote output: {output_csv}")
	print(f"Rows before: {len(rows)}")
	print(f"Rows after:  {len(deduped)}")
	print(f"Removed:     {removed}")
	if seed is not None:
		print(f"Seed:        {seed}")


if __name__ == "__main__":
	main()

