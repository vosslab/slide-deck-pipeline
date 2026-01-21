import slide_deck_pipeline.pptx_hash as pptx_hash


class FakeTargetPart:
	def __init__(self, blob: bytes) -> None:
		self.blob = blob


class FakeRel:
	def __init__(self, blob: bytes) -> None:
		self.is_external = False
		self.target_part = FakeTargetPart(blob)
		self.target_ref = ""


#============================================
def test_relationship_payload_normalizes_ids() -> None:
	"""
	Normalize xml payloads so ids do not affect hashes.
	"""
	xml_one = b"<slide id='1' name='Slide 1'><shape>Text</shape></slide>"
	xml_two = b"<slide id='2' name='Slide 2'><shape>Text</shape></slide>"
	payload_one = pptx_hash.relationship_payload(FakeRel(xml_one))
	payload_two = pptx_hash.relationship_payload(FakeRel(xml_two))
	assert payload_one == payload_two
