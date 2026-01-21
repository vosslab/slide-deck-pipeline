import pytest

import slide_deck_pipeline.csv_schema as csv_schema


#============================================
def test_normalize_text_preserves_tabs() -> None:
	"""
	Keep leading tabs while normalizing whitespace.
	"""
	raw = "\tItem one  \n\t\tSub  item\n\n  Loose  text "
	expected = "\tItem one\n\t\tSub item\nLoose text"
	assert csv_schema.normalize_text(raw) == expected


#============================================
def test_slide_hash_consistent() -> None:
	"""
	Ensure slide hash is stable and sensitive to changes.
	"""
	first = csv_schema.compute_slide_hash("Title\nBody", "Notes")
	second = csv_schema.compute_slide_hash("Title\nBody", "Notes")
	third = csv_schema.compute_slide_hash("Title\nBody changed", "Notes")
	assert first == second
	assert first != third


#============================================
def test_text_hash_consistent() -> None:
	"""
	Ensure text hash is stable and sensitive to changes.
	"""
	first = csv_schema.compute_text_hash("Title\nBody")
	second = csv_schema.compute_text_hash("Title\nBody")
	third = csv_schema.compute_text_hash("Title\nBody changed")
	assert first == second
	assert first != third


#============================================
def test_validate_headers_ok() -> None:
	"""
	Accept the expected schema headers.
	"""
	csv_schema.validate_headers(list(csv_schema.CSV_COLUMNS))


#============================================
def test_validate_headers_error() -> None:
	"""
	Reject incorrect schema headers.
	"""
	headers = list(csv_schema.CSV_COLUMNS)
	headers.append("extra")
	with pytest.raises(ValueError):
		csv_schema.validate_headers(headers)
