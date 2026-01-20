#!/usr/bin/env python3

import argparse
import os

# local repo modules
import slide_deck_pipeline.csv_schema as csv_schema


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
		help="Require hashes to match recomputed values",
		action="store_true",
	)
	parser.add_argument(
		"-S",
		"--no-strict",
		dest="strict",
		help="Skip hash validation",
		action="store_false",
	)
	parser.set_defaults(strict=False)
	args = parser.parse_args()
	return args


#============================================
def resolve_source_path(source_pptx: str, csv_dir: str) -> str:
	"""
	Resolve a source path using the CSV directory as fallback.

	Args:
		source_pptx: Source PPTX or ODP path.
		csv_dir: Directory containing the CSV.

	Returns:
		str: Resolved source path.
	"""
	if os.path.exists(source_pptx):
		return source_pptx
	if csv_dir:
		candidate = os.path.join(csv_dir, source_pptx)
		if os.path.exists(candidate):
			return candidate
	return source_pptx


#============================================
def normalize_row_value(row: dict[str, str], key: str) -> str:
	"""
	Normalize a CSV row field to a string.

	Args:
		row: CSV row.
		key: Column name.

	Returns:
		str: Normalized value.
	"""
	value = row.get(key)
	if value is None:
		return ""
	if isinstance(value, str):
		return value
	return str(value)


#============================================
def sources_match(locator_source: str, row_source: str) -> bool:
	"""
	Check whether locator and row sources refer to the same file.

	Args:
		locator_source: Source from locator.
		row_source: Source from CSV row.

	Returns:
		bool: True if sources match.
	"""
	if locator_source == row_source:
		return True
	if os.path.basename(locator_source) == os.path.basename(row_source):
		return True
	return False


#============================================
def is_positive_int(value: str) -> bool:
	"""
	Check whether a string is a positive integer.

	Args:
		value: Input string.

	Returns:
		bool: True if value is a positive integer.
	"""
	if not value:
		return False
	if not value.isdigit():
		return False
	parsed = int(value)
	return parsed > 0


#============================================
def validate_rows(
	rows: list[dict[str, str]],
	csv_dir: str,
	check_sources: bool,
	strict: bool,
) -> tuple[list[str], list[str]]:
	"""
	Validate merged CSV rows.

	Args:
		rows: CSV rows.
		csv_dir: Directory containing the CSV.
		check_sources: Whether to check source files exist.
		strict: Whether to validate hashes and fingerprints.

	Returns:
		tuple[list[str], list[str]]: Errors and warnings.
	"""
	errors = []
	warnings = []
	seen_uids = set()
	if not rows:
		warnings.append("No rows found in CSV.")
		return (errors, warnings)
	for index, row in enumerate(rows, 1):
		slide_uid = normalize_row_value(row, "slide_uid")
		if not slide_uid:
			errors.append(f"Row {index}: missing slide_uid.")
		if slide_uid and slide_uid in seen_uids:
			errors.append(f"Row {index}: duplicate slide_uid {slide_uid}.")
		seen_uids.add(slide_uid)

		source_pptx = normalize_row_value(row, "source_pptx")
		if not source_pptx:
			errors.append(f"Row {index}: missing source_pptx.")
		else:
			extension = os.path.splitext(source_pptx)[1].lower()
			if extension not in (".pptx", ".odp"):
				warnings.append(f"Row {index}: unexpected source_pptx extension.")
			if check_sources:
				resolved_path = resolve_source_path(source_pptx, csv_dir)
				if not os.path.exists(resolved_path):
					errors.append(f"Row {index}: source_pptx not found.")

		slide_index = normalize_row_value(row, "source_slide_index")
		if not is_positive_int(slide_index):
			errors.append(f"Row {index}: invalid source_slide_index {slide_index}.")
		slide_index_value = slide_index

		layout_hint = normalize_row_value(row, "layout_hint")
		if not layout_hint:
			warnings.append(f"Row {index}: missing layout_hint.")

		image_locators = csv_schema.split_list_field(
			normalize_row_value(row, "image_locators")
		)
		image_hashes = csv_schema.split_list_field(
			normalize_row_value(row, "image_hashes")
		)
		if image_locators and image_hashes:
			if len(image_locators) != len(image_hashes):
				errors.append(
					f"Row {index}: image_locators and image_hashes length mismatch."
				)
		if image_locators and not image_hashes:
			warnings.append(f"Row {index}: image_locators present without image_hashes.")
		if image_hashes and not image_locators:
			warnings.append(f"Row {index}: image_hashes present without image_locators.")

		if image_locators:
			for locator in image_locators:
				parsed = csv_schema.parse_image_locator(locator)
				if not parsed:
					errors.append(f"Row {index}: invalid image_locator {locator}.")
					continue
				locator_source = parsed.get("source", "")
				if not sources_match(locator_source, source_pptx):
					errors.append(f"Row {index}: image_locator source mismatch.")
				locator_slide = parsed.get("slide", "")
				if locator_slide != slide_index_value:
					errors.append(f"Row {index}: image_locator slide mismatch.")
				shape_id = parsed.get("shape_id", "")
				if not shape_id or not shape_id.isdigit():
					errors.append(f"Row {index}: image_locator shape_id invalid.")

		if strict:
			title_text = normalize_row_value(row, "title_text")
			body_text = normalize_row_value(row, "body_text")
			notes_text = normalize_row_value(row, "notes_text")
			expected_text_hash = csv_schema.compute_text_hash(
				title_text,
				body_text,
				notes_text,
			)
			expected_fingerprint = csv_schema.compute_slide_fingerprint(
				title_text,
				body_text,
				notes_text,
				image_hashes,
			)
			text_hash = normalize_row_value(row, "text_hash")
			if text_hash != expected_text_hash:
				errors.append(f"Row {index}: text_hash mismatch.")
			slide_fingerprint = normalize_row_value(row, "slide_fingerprint")
			if slide_fingerprint != expected_fingerprint:
				errors.append(f"Row {index}: slide_fingerprint mismatch.")
		else:
			text_hash = normalize_row_value(row, "text_hash")
			if not text_hash:
				warnings.append(f"Row {index}: text_hash is missing.")
			slide_fingerprint = normalize_row_value(row, "slide_fingerprint")
			if not slide_fingerprint:
				warnings.append(f"Row {index}: slide_fingerprint is missing.")
	return (errors, warnings)


#============================================
def format_messages(label: str, messages: list[str]) -> list[str]:
	"""
	Format validation messages with a label.

	Args:
		label: Message label.
		messages: List of messages.

	Returns:
		list[str]: Formatted lines.
	"""
	lines = []
	for message in messages:
		lines.append(f"{label}: {message}")
	return lines


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
