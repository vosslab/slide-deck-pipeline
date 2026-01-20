import argparse
import os

# local repo modules
import slide_csv


#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Validate a merged slide CSV and related assets."
	)
	parser.add_argument(
		"-i",
		"--input",
		dest="input_csv",
		required=True,
		help="Input merged CSV path",
	)
	parser.add_argument(
		"-a",
		"--assets-dir",
		dest="assets_dir",
		default="",
		help="Assets directory (default: <input_csv>_assets)",
	)
	parser.add_argument(
		"-c",
		"--check-assets",
		dest="check_assets",
		help="Check image assets exist",
		action="store_true",
	)
	parser.add_argument(
		"-C",
		"--no-check-assets",
		dest="check_assets",
		help="Skip image asset checks",
		action="store_false",
	)
	parser.set_defaults(check_assets=True)
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
def resolve_assets_dir(input_csv: str, assets_dir: str) -> str:
	"""
	Resolve the assets directory.

	Args:
		input_csv: Input CSV path.
		assets_dir: Assets directory or empty string.

	Returns:
		str: Resolved assets directory.
	"""
	if assets_dir:
		return assets_dir
	base_name = os.path.splitext(input_csv)[0]
	return f"{base_name}_assets"


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
	assets_dir: str,
	check_assets: bool,
	strict: bool,
) -> tuple[list[str], list[str]]:
	"""
	Validate merged CSV rows.

	Args:
		rows: CSV rows.
		assets_dir: Assets directory path.
		check_assets: Whether to check asset files exist.
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

		slide_index = normalize_row_value(row, "source_slide_index")
		if not is_positive_int(slide_index):
			errors.append(f"Row {index}: invalid source_slide_index {slide_index}.")

		layout_hint = normalize_row_value(row, "layout_hint")
		if not layout_hint:
			warnings.append(f"Row {index}: missing layout_hint.")

		image_refs = slide_csv.split_list_field(
			normalize_row_value(row, "image_refs")
		)
		image_hashes = slide_csv.split_list_field(
			normalize_row_value(row, "image_hashes")
		)
		if image_refs and not image_hashes:
			warnings.append(f"Row {index}: image_refs present without image_hashes.")
		if image_hashes and not image_refs:
			errors.append(f"Row {index}: image_hashes present without image_refs.")
		if image_refs and image_hashes:
			if len(image_refs) != len(image_hashes):
				errors.append(f"Row {index}: image_refs and image_hashes length mismatch.")

		if check_assets and image_refs:
			if not os.path.isdir(assets_dir):
				errors.append(f"Row {index}: assets_dir not found: {assets_dir}.")
			else:
				for ref in image_refs:
					path = os.path.join(assets_dir, ref)
					if not os.path.exists(path):
						errors.append(f"Row {index}: missing asset {ref}.")

		if strict:
			title_text = normalize_row_value(row, "title_text")
			body_text = normalize_row_value(row, "body_text")
			notes_text = normalize_row_value(row, "notes_text")
			expected_text_hash = slide_csv.compute_text_hash(
				title_text,
				body_text,
				notes_text,
			)
			expected_fingerprint = slide_csv.compute_slide_fingerprint(
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
	assets_dir = resolve_assets_dir(args.input_csv, args.assets_dir)
	rows = slide_csv.read_slide_csv(args.input_csv)
	errors, warnings = validate_rows(
		rows,
		assets_dir,
		args.check_assets,
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
