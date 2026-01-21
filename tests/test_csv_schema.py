import pathlib

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
	first = csv_schema.compute_slide_hash(b"<slide>Title</slide>", "Notes")
	second = csv_schema.compute_slide_hash(b"<slide>Title</slide>", "Notes")
	third = csv_schema.compute_slide_hash(b"<slide>Other</slide>", "Notes")
	assert first == second
	assert first != third


#============================================
def test_slide_hash_ignores_ids() -> None:
	"""
	Ignore volatile id and name attributes in slide hashes.
	"""
	xml_one = b"<slide id='1' name='Slide 1'><shape>Text</shape></slide>"
	xml_two = b"<slide id='2' name='Slide 2'><shape>Text</shape></slide>"
	first = csv_schema.compute_slide_hash(xml_one, "")
	second = csv_schema.compute_slide_hash(xml_two, "")
	assert first == second


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
def test_sanitize_context_text() -> None:
	"""
	Strip commas, tabs, newlines, and non-ascii characters.
	"""
	raw = "Title, with\tcomma\nand\nlines caf\u00e9"
	cleaned = csv_schema.sanitize_context_text(raw)
	assert "," not in cleaned
	assert "\t" not in cleaned
	assert "\n" not in cleaned
	assert "\r" not in cleaned
	assert all(ord(ch) < 128 for ch in cleaned)


#============================================
def test_read_slide_csv_skips_header_rows(tmp_path: pathlib.Path) -> None:
	"""
	Skip repeated header rows inside CSV data.
	"""
	csv_path = tmp_path / "sample.csv"
	headers = ",".join(csv_schema.CSV_COLUMNS)
	lines = [
		headers,
		"deck.pptx,1,deadbeefdeadbeef,Master,Layout,,Title,Body,Notes",
		headers,
		"deck.pptx,2,feedfacefeedface,Master,Layout,,Title2,Body2,Notes2",
	]
	csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
	rows = csv_schema.read_slide_csv(str(csv_path))
	assert len(rows) == 2
	assert rows[0]["source_slide_index"] == "1"
	assert rows[1]["source_slide_index"] == "2"
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
