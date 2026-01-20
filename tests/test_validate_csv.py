import slide_csv
import validate_csv


#============================================
def build_row(
	slide_uid: str,
	source_slide_index: str = "1",
	text_hash: str = "",
	slide_fingerprint: str = "",
	image_refs: str = "",
	image_hashes: str = "",
) -> dict[str, str]:
	"""
	Build a basic CSV row for validation.
	"""
	return {
		"source_pptx": "deck.pptx",
		"source_slide_index": source_slide_index,
		"slide_uid": slide_uid,
		"title_text": "Title",
		"body_text": "Body",
		"notes_text": "",
		"layout_hint": "title_and_content",
		"image_refs": image_refs,
		"image_hashes": image_hashes,
		"text_hash": text_hash,
		"slide_fingerprint": slide_fingerprint,
	}


#============================================
def test_validate_rows_ok_strict() -> None:
	"""
	Accept valid rows when strict hashing is enabled.
	"""
	text_hash = slide_csv.compute_text_hash("Title", "Body", "")
	slide_fingerprint = slide_csv.compute_slide_fingerprint(
		"Title",
		"Body",
		"",
		[],
	)
	row = build_row(
		slide_uid="uid1",
		text_hash=text_hash,
		slide_fingerprint=slide_fingerprint,
		image_refs="",
		image_hashes="",
	)
	rows = [row]
	errors, warnings = validate_csv.validate_rows(
		rows,
		assets_dir="assets",
		check_assets=False,
		strict=True,
	)
	assert not errors
	assert not warnings


#============================================
def test_validate_rows_duplicate_uid() -> None:
	"""
	Detect duplicate slide_uid values.
	"""
	rows = [build_row("dup"), build_row("dup")]
	errors, warnings = validate_csv.validate_rows(
		rows,
		assets_dir="assets",
		check_assets=False,
		strict=False,
	)
	assert any("duplicate slide_uid" in item for item in errors)
	assert warnings


#============================================
def test_validate_rows_missing_hashes_warning() -> None:
	"""
	Warn when hashes are missing in non-strict mode.
	"""
	rows = [build_row("uid1")]
	errors, warnings = validate_csv.validate_rows(
		rows,
		assets_dir="assets",
		check_assets=False,
		strict=False,
	)
	assert not errors
	assert any("text_hash is missing" in item for item in warnings)
	assert any("slide_fingerprint is missing" in item for item in warnings)


#============================================
def test_validate_rows_bad_slide_index() -> None:
	"""
	Detect invalid slide indices.
	"""
	rows = [build_row("uid1", source_slide_index="zero")]
	errors, warnings = validate_csv.validate_rows(
		rows,
		assets_dir="assets",
		check_assets=False,
		strict=False,
	)
	assert any("invalid source_slide_index" in item for item in errors)
