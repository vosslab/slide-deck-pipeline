import slide_deck_pipeline.csv_schema as csv_schema
import validate_csv


#============================================
def build_row(
	slide_hash: str,
	source_slide_index: str = "1",
	master_name: str = "Master",
	layout_name: str = "Layout",
	asset_types: str = "image",
) -> dict[str, str]:
	"""
	Build a basic CSV row for validation.
	"""
	return {
		"source_pptx": "deck.pptx",
		"source_slide_index": source_slide_index,
		"slide_hash": slide_hash,
		"master_name": master_name,
		"layout_name": layout_name,
		"asset_types": asset_types,
		"title_text": "Title",
		"body_text": "Body",
		"notes_text": "",
	}


#============================================
def test_validate_rows_ok() -> None:
	"""
	Accept valid rows when hashing is not enforced.
	"""
	slide_hash = csv_schema.compute_slide_hash(b"<slide>Title</slide>", "")
	row = build_row(
		slide_hash=slide_hash,
	)
	rows = [row]
	errors, warnings = validate_csv.validate_rows(
		rows,
		csv_dir="",
		check_sources=False,
		strict=False,
		template_path="",
	)
	assert not errors
	assert not warnings


#============================================
def test_validate_rows_missing_layout() -> None:
	"""
	Detect missing layout_name values.
	"""
	slide_hash = csv_schema.compute_slide_hash(b"<slide>Title</slide>", "")
	rows = [build_row(slide_hash, layout_name="")]
	errors, warnings = validate_csv.validate_rows(
		rows,
		csv_dir="",
		check_sources=False,
		strict=False,
		template_path="",
	)
	assert any("missing layout_name" in item for item in errors)
	assert not warnings


#============================================
def test_validate_rows_bad_hash_format() -> None:
	"""
	Detect invalid slide_hash formats.
	"""
	rows = [build_row("not-a-hash")]
	errors, warnings = validate_csv.validate_rows(
		rows,
		csv_dir="",
		check_sources=False,
		strict=False,
		template_path="",
	)
	assert any("slide_hash must be 16 hex characters" in item for item in errors)
	assert not warnings


#============================================
def test_validate_rows_bad_slide_index() -> None:
	"""
	Detect invalid slide indices.
	"""
	slide_hash = csv_schema.compute_slide_hash(b"<slide>Title</slide>", "")
	rows = [build_row(slide_hash, source_slide_index="zero")]
	errors, warnings = validate_csv.validate_rows(
		rows,
		csv_dir="",
		check_sources=False,
		strict=False,
		template_path="",
	)
	assert any("invalid source_slide_index" in item for item in errors)
