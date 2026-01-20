import csv
import hashlib
import os


CSV_COLUMNS = [
	"source_pptx",
	"source_slide_index",
	"slide_uid",
	"title_text",
	"body_text",
	"notes_text",
	"layout_hint",
	"image_refs",
	"image_hashes",
	"text_hash",
	"slide_fingerprint",
]
LIST_DELIMITER = "|"


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
def split_list_field(value: str | None) -> list[str]:
	"""
	Split a delimited list field from CSV.

	Args:
		value: Field value or None.

	Returns:
		list[str]: List of items.
	"""
	if not value:
		return []
	items = [item for item in value.split(LIST_DELIMITER) if item]
	return items


#============================================
def join_list_field(items: list[str]) -> str:
	"""
	Join a list into a delimited CSV field.

	Args:
		items: Items to join.

	Returns:
		str: Delimited field value.
	"""
	if not items:
		return ""
	return LIST_DELIMITER.join(items)


#============================================
def hash_text(value: str) -> str:
	"""
	Hash a string with sha256.

	Args:
		value: Input text.

	Returns:
		str: Hex digest.
	"""
	return hashlib.sha256(value.encode("utf-8")).hexdigest()


#============================================
def compute_text_hash(title_text: str, body_text: str, notes_text: str) -> str:
	"""
	Compute a hash for slide text fields.

	Args:
		title_text: Title text.
		body_text: Body text.
		notes_text: Notes text.

	Returns:
		str: Text hash.
	"""
	parts = [
		normalize_text(title_text),
		normalize_text(body_text),
		normalize_text(notes_text),
	]
	joined = "\n".join(parts)
	return hash_text(joined)


#============================================
def compute_slide_fingerprint(
	title_text: str,
	body_text: str,
	notes_text: str,
	image_hashes: list[str],
) -> str:
	"""
	Compute a fingerprint that includes text and images.

	Args:
		title_text: Title text.
		body_text: Body text.
		notes_text: Notes text.
		image_hashes: Ordered image hashes.

	Returns:
		str: Slide fingerprint.
	"""
	text_hash = compute_text_hash(title_text, body_text, notes_text)
	joined_images = join_list_field(image_hashes)
	return hash_text(f"{text_hash}\n{joined_images}")


#============================================
def compute_slide_uid(
	source_pptx: str,
	slide_index: int,
	title_text: str,
	body_text: str,
	notes_text: str,
	image_hashes: list[str],
) -> str:
	"""
	Compute a stable slide UID from source and content.

	Args:
		source_pptx: Source PPTX basename.
		slide_index: 1-based slide index.
		title_text: Title text.
		body_text: Body text.
		notes_text: Notes text.
		image_hashes: Ordered image hashes.

	Returns:
		str: Slide UID.
	"""
	text_hash = compute_text_hash(title_text, body_text, notes_text)
	joined_images = join_list_field(image_hashes)
	key = f"{source_pptx}:{slide_index}:{text_hash}:{joined_images}"
	return hash_text(key)


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
