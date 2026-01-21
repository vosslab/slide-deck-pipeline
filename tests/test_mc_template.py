import slide_deck_pipeline.mc_template as mc_template


#============================================
def test_find_template_slide() -> None:
	"""
	Locate the MC template slide and required shape ids.
	"""
	template_dir = mc_template.get_template_source_dir()
	mc_template.validate_template_source(template_dir)
	_, _, shape_ids, _ = mc_template.find_template_slide(template_dir)
	assert "question" in shape_ids
	assert "options" in shape_ids
	assert "popup" in shape_ids
