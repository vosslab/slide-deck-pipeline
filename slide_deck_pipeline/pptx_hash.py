# Standard Library
import hashlib

# local repo modules
import slide_deck_pipeline.csv_schema as csv_schema
import slide_deck_pipeline.pptx_text as pptx_text


#============================================
def extract_slide_xml(slide) -> bytes:
	"""
	Return slide XML bytes.

	Args:
		slide: Slide instance.

	Returns:
		bytes: Slide XML.
	"""
	return slide.part.blob


#============================================
def build_relationship_hashes(slide) -> tuple[dict[str, str], list[tuple[str, str]]]:
	"""
	Hash slide relationships so rel ids can be normalized.

	Args:
		slide: Slide instance.

	Returns:
		tuple[dict[str, str], list[tuple[str, str]]]: Rel id hashes and tokens.
	"""
	rel_hashes: dict[str, str] = {}
	rel_tokens: list[tuple[str, str]] = []
	rels = getattr(slide.part, "rels", {})
	for rel_id, rel in rels.items():
		payload = relationship_payload(rel)
		digest = hashlib.sha256(payload).hexdigest()[:16]
		rel_hashes[rel_id] = digest
		rel_tokens.append((str(getattr(rel, "reltype", "")), digest))
	rel_tokens.sort()
	return (rel_hashes, rel_tokens)


#============================================
def relationship_payload(rel) -> bytes:
	"""
	Build stable payload bytes for a relationship target.

	Args:
		rel: Relationship instance.

	Returns:
		bytes: Payload bytes for hashing.
	"""
	if getattr(rel, "is_external", False):
		target_ref = str(getattr(rel, "target_ref", ""))
		return target_ref.encode("utf-8")
	target_part = getattr(rel, "target_part", None)
	if target_part is not None and hasattr(target_part, "blob"):
		return bytes(target_part.blob)
	target_ref = str(getattr(rel, "target_ref", ""))
	return target_ref.encode("utf-8")


#============================================
def compute_slide_hash_from_slide(
	slide,
	notes_text: str | None = None,
) -> tuple[str, str, bytes]:
	"""
	Compute slide hash and return slide XML and notes text.

	Args:
		slide: Slide instance.
		notes_text: Optional notes text to reuse.

	Returns:
		tuple[str, str, bytes]: Slide hash, notes text, slide XML bytes.
	"""
	if notes_text is None:
		notes_text = pptx_text.extract_notes_text(slide)
	slide_xml = extract_slide_xml(slide)
	rel_hashes, rel_tokens = build_relationship_hashes(slide)
	slide_hash = csv_schema.compute_slide_hash(
		slide_xml,
		notes_text,
		rel_hashes=rel_hashes,
		rel_tokens=rel_tokens,
	)
	return (slide_hash, notes_text, slide_xml)
