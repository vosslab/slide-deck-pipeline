import csv
import os
import zlib


CSV_COLUMNS = [
	"source_pptx",
	"source_slide_index",
	"slide_hash",
	"master_name",
	"layout_name",
	"title_text",
	"body_text",
	"notes_text",
]


#============================================
def normalize_text(text: str | None) -> str:
	"""
	Normalize text for hashing and comparison.

	Args:
		text: Input text or None.

	Returns:
		str: Normalized text.
	"""
	if not text:
		return ""
	cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
	lines = []
	for raw_line in cleaned.split("\n"):
		line = raw_line.rstrip()
		if not line.strip():
			continue
		leading_tabs = len(line) - len(line.lstrip("\t"))
		content = line.lstrip("\t").strip()
		content = " ".join(content.split())
		line_out = ("\t" * leading_tabs) + content
		lines.append(line_out)
	return "\n".join(lines)


#============================================
def compute_slide_hash(
	source_pptx: str,
	slide_index: int,
	slide_text: str,
) -> str:
	"""
	Compute a stable slide hash from source and text content.

	Args:
		source_pptx: Source PPTX basename.
		slide_index: 1-based slide index.
		slide_text: Full slide text content.

	Returns:
		str: Slide hash.
	"""
	normalized_text = normalize_text(slide_text)
	key = f"{source_pptx}:{slide_index}:{normalized_text}"
	crc_value = zlib.crc32(key.encode("utf-8")) & 0xFFFFFFFF
	return f"{crc_value:08x}"


#============================================
def validate_headers(headers: list[str]) -> None:
	"""
	Ensure the CSV headers match the expected schema.

	Args:
		headers: Header list.
	"""
	if headers != CSV_COLUMNS:
		raise ValueError(
			"CSV headers do not match expected schema. "
			f"Expected {CSV_COLUMNS}, got {headers}."
		)


#============================================
def read_slide_csv(path: str) -> list[dict[str, str]]:
	"""
	Read slide records from a CSV file.

	Args:
		path: CSV file path.

	Returns:
		list[dict[str, str]]: Slide rows.
	"""
	if not os.path.exists(path):
		raise FileNotFoundError(f"CSV file not found: {path}")
	with open(path, "r", encoding="utf-8", newline="") as handle:
		reader = csv.DictReader(handle)
		headers = reader.fieldnames or []
		validate_headers(headers)
		rows = []
		for row in reader:
			rows.append(row)
		return rows


#============================================
def write_slide_csv(path: str, rows: list[dict[str, str]]) -> None:
	"""
	Write slide records to a CSV file.

	Args:
		path: CSV file path.
		rows: Slide rows to write.
	"""
	with open(path, "w", encoding="utf-8", newline="") as handle:
		writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
		writer.writeheader()
		for row in rows:
			writer.writerow(row)
