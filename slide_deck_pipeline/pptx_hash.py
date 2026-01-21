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
	slide_hash = csv_schema.compute_slide_hash(slide_xml, notes_text)
	return (slide_hash, notes_text, slide_xml)
