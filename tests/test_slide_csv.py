import pytest

import slide_csv


#============================================
def test_normalize_text_preserves_tabs() -> None:
	"""
	Keep leading tabs while normalizing whitespace.
	"""
	raw = "\tItem one  \n\t\tSub  item\n\n  Loose  text "
	expected = "\tItem one\n\t\tSub item\nLoose text"
	assert slide_csv.normalize_text(raw) == expected


#============================================
def test_list_field_roundtrip() -> None:
	"""
	Split and join list fields consistently.
	"""
	items = ["a.png", "b.png", "c.png"]
	joined = slide_csv.join_list_field(items)
	assert joined == "a.png|b.png|c.png"
	assert slide_csv.split_list_field(joined) == items
	assert slide_csv.split_list_field("") == []


#============================================
def test_hashes_consistent() -> None:
	"""
	Ensure text hash is stable and sensitive to changes.
	"""
	first = slide_csv.compute_text_hash("Title", "Body", "Notes")
	second = slide_csv.compute_text_hash("Title", "Body", "Notes")
	third = slide_csv.compute_text_hash("Title", "Body changed", "Notes")
	assert first == second
	assert first != third


#============================================
def test_slide_uid_changes_with_images() -> None:
	"""
	Ensure slide UID changes when images change.
	"""
	uid_a = slide_csv.compute_slide_uid(
		"deck.pptx",
		1,
		"Title",
		"Body",
		"",
		["hash1", "hash2"],
	)
	uid_b = slide_csv.compute_slide_uid(
		"deck.pptx",
		1,
		"Title",
		"Body",
		"",
		["hash1", "hash3"],
	)
	assert uid_a != uid_b


#============================================
def test_validate_headers_ok() -> None:
	"""
	Accept the expected schema headers.
	"""
	slide_csv.validate_headers(list(slide_csv.CSV_COLUMNS))


#============================================
def test_validate_headers_error() -> None:
	"""
	Reject incorrect schema headers.
	"""
	headers = list(slide_csv.CSV_COLUMNS)
	headers.append("extra")
	with pytest.raises(ValueError):
		slide_csv.validate_headers(headers)
