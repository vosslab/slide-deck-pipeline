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
def test_list_field_roundtrip() -> None:
	"""
	Split and join list fields consistently.
	"""
	items = ["a.png", "b.png", "c.png"]
	joined = csv_schema.join_list_field(items)
	assert joined == "a.png|b.png|c.png"
	assert csv_schema.split_list_field(joined) == items
	assert csv_schema.split_list_field("") == []


#============================================
def test_hashes_consistent() -> None:
	"""
	Ensure text hash is stable and sensitive to changes.
	"""
	first = csv_schema.compute_text_hash("Title", "Body", "Notes")
	second = csv_schema.compute_text_hash("Title", "Body", "Notes")
	third = csv_schema.compute_text_hash("Title", "Body changed", "Notes")
	assert first == second
	assert first != third


#============================================
def test_slide_uid_changes_with_images() -> None:
	"""
	Ensure slide UID changes when images change.
	"""
	uid_a = csv_schema.compute_slide_uid(
		"deck.pptx",
		1,
		"Title",
		"Body",
		"",
		["hash1", "hash2"],
	)
	uid_b = csv_schema.compute_slide_uid(
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


#============================================
def test_image_locator_roundtrip() -> None:
	"""
	Build and parse image locator strings.
	"""
	locator = csv_schema.build_image_locator("deck.pptx", 12, 5)
	parsed = csv_schema.parse_image_locator(locator)
	assert parsed is not None
	assert parsed["source"] == "deck.pptx"
	assert parsed["slide"] == "12"
	assert parsed["shape_id"] == "5"
