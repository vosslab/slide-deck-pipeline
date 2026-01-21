import pathlib

import pytest

import slide_deck_pipeline.spec_schema as spec_schema


#============================================
def write_yaml(path: pathlib.Path, content: str) -> None:
	"""
	Write a YAML file to disk.
	"""
	path.write_text(content, encoding="utf-8")


#============================================
def test_load_yaml_spec_normalizes_layouts(tmp_path: pathlib.Path) -> None:
	"""
	Normalize layout_type aliases and warn on ignored master_name.
	"""
	yaml_path = tmp_path / "spec.yaml"
	write_yaml(
		yaml_path,
		"\n".join(
			[
				"version: 1",
				"defaults:",
				"  layout_type: content",
				"  master_name: light",
				"slides:",
				"  - layout_type: title",
				"    title: Hello",
			]
		)
		+ "\n",
	)
	spec, warnings = spec_schema.load_yaml_spec(str(yaml_path), strict=False)
	assert spec["defaults"]["layout_type"] == "title_content"
	assert spec["slides"][0]["layout_type"] == "title_slide"
	assert any("master_name is ignored" in message for message in warnings)


#============================================
def test_load_yaml_spec_rejects_bad_bodies(tmp_path: pathlib.Path) -> None:
	"""
	Reject non-list bodies values.
	"""
	yaml_path = tmp_path / "spec.yaml"
	write_yaml(
		yaml_path,
		"\n".join(
			[
				"version: 1",
				"slides:",
				"  - layout_type: title_content",
				"    title: Hello",
				"    bodies: not_a_list",
			]
		)
		+ "\n",
	)
	with pytest.raises(ValueError):
		spec_schema.load_yaml_spec(str(yaml_path), strict=False)


#============================================
def test_load_yaml_spec_image_conflict_strict(tmp_path: pathlib.Path) -> None:
	"""
	Reject image and images together in strict mode.
	"""
	yaml_path = tmp_path / "spec.yaml"
	write_yaml(
		yaml_path,
		"\n".join(
			[
				"version: 1",
				"slides:",
				"  - layout_type: title_content",
				"    title: Hello",
				"    image: fig01.png",
				"    images:",
				"      - fig02.png",
			]
		)
		+ "\n",
	)
	with pytest.raises(ValueError):
		spec_schema.load_yaml_spec(str(yaml_path), strict=True)
