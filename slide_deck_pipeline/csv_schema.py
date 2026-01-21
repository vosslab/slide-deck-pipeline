import csv
import hashlib
import os
import lxml.etree as xml_et


CSV_COLUMNS = [
	"source_pptx",
	"source_slide_index",
	"slide_hash",
	"master_name",
	"layout_type",
	"asset_types",
	"title_text",
	"body_text",
	"notes_text",
]
CONTEXT_COLUMNS = ("title_text", "body_text", "notes_text")
XML_PARSER = xml_et.XMLParser(resolve_entities=False, no_network=True, recover=False)


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
def sanitize_context_text(text: str | None) -> str:
	"""
	Sanitize context text for CSV output.

	Args:
		text: Input text or None.

	Returns:
		str: Sanitized text.
	"""
	if not text:
		return ""
	ascii_only = "".join(ch for ch in text if ord(ch) < 128)
	for ch in (",", "\t", "\n", "\r"):
		ascii_only = ascii_only.replace(ch, " ")
	return " ".join(ascii_only.split())


#============================================
def compute_slide_hash(
	slide_xml: bytes,
	notes_text: str = "",
	rel_hashes: dict[str, str] | None = None,
	rel_tokens: list[tuple[str, str]] | None = None,
) -> str:
	"""
	Compute a stable slide hash from slide content.

	Args:
		slide_xml: Slide XML bytes.
		notes_text: Speaker notes text.

	Returns:
		str: Slide hash.
	"""
	normalized_notes = normalize_text(notes_text)
	if not isinstance(slide_xml, (bytes, bytearray)):
		raise TypeError("slide_xml must be bytes.")
	payload = normalize_slide_xml(bytes(slide_xml), rel_hashes)
	if rel_tokens:
		payload += b"\n--rels--\n" + repr(tuple(rel_tokens)).encode("utf-8")
	if normalized_notes:
		payload += b"\n--notes--\n" + normalized_notes.encode("utf-8")
	digest = hashlib.sha256(payload).hexdigest()
	return digest[:16]


#============================================
def normalize_slide_xml(
	slide_xml: bytes,
	rel_hashes: dict[str, str] | None = None,
) -> bytes:
	"""
	Normalize slide XML into a stable signature.

	Args:
		slide_xml: Slide XML bytes.

	Returns:
		bytes: Normalized XML signature bytes.
	"""
	try:
		root = xml_et.fromstring(slide_xml, parser=XML_PARSER)
	except xml_et.XMLSyntaxError:
		return slide_xml
	signature = build_xml_signature(root, rel_hashes)
	return repr(signature).encode("utf-8")


#============================================
def build_xml_signature(
	element,
	rel_hashes: dict[str, str] | None = None,
) -> tuple:
	"""
	Build a stable signature for an XML element tree.

	Args:
		element: XML element.

	Returns:
		tuple: Signature tuple.
	"""
	if rel_hashes is None:
		rel_hashes = {}
	attrs = []
	for attr_key, attr_value in element.attrib.items():
		if attr_value in rel_hashes:
			attrs.append((attr_key, rel_hashes[attr_value]))
			continue
		if should_ignore_attr(attr_key):
			continue
		attrs.append((attr_key, attr_value))
	attrs = tuple(sorted(attrs))
	children = tuple(build_xml_signature(child, rel_hashes) for child in list(element))
	text = (element.text or "").strip()
	tail = (element.tail or "").strip()
	return (element.tag, attrs, text, children, tail)


#============================================
def should_ignore_attr(attr_key: str) -> bool:
	"""
	Return True for volatile attribute keys to ignore.

	Args:
		attr_key: Attribute key (may include namespace).

	Returns:
		bool: True if attribute should be ignored.
	"""
	local_name = attr_key.split("}")[-1]
	return local_name in ("id", "name")


#============================================
def compute_text_hash(text: str) -> str:
	"""
	Compute a stable hash for normalized text.

	Args:
		text: Input text.

	Returns:
		str: Text hash.
	"""
	normalized = normalize_text(text)
	digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
	return digest[:16]


#============================================
def is_header_row(row: dict[str, str]) -> bool:
	"""
	Check whether a row repeats the CSV header.

	Args:
		row: CSV row.

	Returns:
		bool: True if the row matches header values.
	"""
	for column in CSV_COLUMNS:
		if row.get(column) != column:
			return False
	return True


#============================================
def sanitize_row_context(row: dict[str, str]) -> dict[str, str]:
	"""
	Sanitize context text fields in a CSV row.

	Args:
		row: CSV row.

	Returns:
		dict[str, str]: Sanitized row.
	"""
	sanitized = dict(row)
	for column in CONTEXT_COLUMNS:
		if column in sanitized:
			sanitized[column] = sanitize_context_text(sanitized[column])
	return sanitized


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
		reader = csv.reader(handle)
		rows = []
		for row in reader:
			if not row:
				continue
			normalized = [field.strip() for field in row]
			if all(not field for field in normalized):
				continue
			if normalized == CSV_COLUMNS:
				continue
			if len(row) != len(CSV_COLUMNS):
				raise ValueError(
					"CSV row does not match expected schema. "
					f"Expected {CSV_COLUMNS}, got {row}."
				)
			rows.append(dict(zip(CSV_COLUMNS, row)))
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
			writer.writerow(sanitize_row_context(row))
