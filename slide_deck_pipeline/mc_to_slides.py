# Standard Library
import copy
import os
import re
import shutil
import tempfile
import zipfile

# PIP3 modules
import lxml.etree as etree

# local repo modules
import slide_deck_pipeline.mc_template as mc_template


CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SLIDE_CONTENT_TYPE = (
	"application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
)


#============================================
def render_questions_to_pptx(
	questions: list[dict[str, object]],
	output_path: str,
	preserve_newlines: bool,
) -> list[str]:
	"""
	Render questions into a PPTX file.

	Args:
		questions: Parsed question records.
		output_path: Output PPTX path.
		preserve_newlines: Keep prompt and feedback line breaks.

	Returns:
		list[str]: Warnings.
	"""
	template_dir = mc_template.get_template_source_dir()
	mc_template.validate_template_source(template_dir)
	(
		template_slide_path,
		template_rels_path,
		shape_ids,
		warnings,
	) = mc_template.find_template_slide(template_dir)
	template_tree = etree.parse(template_slide_path)
	template_root = template_tree.getroot()
	with tempfile.TemporaryDirectory(prefix="mc_to_slides_") as temp_dir:
		working_dir = os.path.join(temp_dir, "pptx")
		shutil.copytree(template_dir, working_dir)
		clear_existing_slides(working_dir)
		slides_dir = os.path.join(working_dir, "ppt", "slides")
		rels_dir = os.path.join(slides_dir, "_rels")
		for index, question in enumerate(questions, 1):
			slide_name = f"slide{index}.xml"
			slide_path = os.path.join(slides_dir, slide_name)
			slide_root = copy.deepcopy(template_root)
			apply_question_to_slide(
				slide_root,
				shape_ids,
				question,
				preserve_newlines,
			)
			write_xml(slide_root, slide_path)
			rels_name = f"{slide_name}.rels"
			rels_path = os.path.join(rels_dir, rels_name)
			shutil.copyfile(template_rels_path, rels_path)
		slide_rids = update_presentation_rels(
			working_dir,
			len(questions),
		)
		update_presentation_xml(
			working_dir,
			slide_rids,
		)
		update_content_types(
			working_dir,
			len(questions),
		)
		write_pptx(working_dir, output_path)
	return warnings


#============================================
def clear_existing_slides(working_dir: str) -> None:
	"""
	Remove existing slide XML files from a working directory.

	Args:
		working_dir: Template working directory.
	"""
	slides_dir = os.path.join(working_dir, "ppt", "slides")
	if not os.path.isdir(slides_dir):
		return
	for filename in os.listdir(slides_dir):
		if not filename.startswith("slide") or not filename.endswith(".xml"):
			continue
		path = os.path.join(slides_dir, filename)
		os.remove(path)
	rels_dir = os.path.join(slides_dir, "_rels")
	if not os.path.isdir(rels_dir):
		return
	for filename in os.listdir(rels_dir):
		if not filename.startswith("slide") or not filename.endswith(".xml.rels"):
			continue
		path = os.path.join(rels_dir, filename)
		os.remove(path)


#============================================
def apply_question_to_slide(
	slide_root,
	shape_ids: dict[str, str],
	question: dict[str, object],
	preserve_newlines: bool,
) -> None:
	"""
	Apply question text to a slide XML tree.

	Args:
		slide_root: Slide XML root element.
		shape_ids: Mapping of required shape ids.
		question: Question record.
		preserve_newlines: Keep prompt and feedback line breaks.
	"""
	prompt_lines = format_prompt_lines(question, preserve_newlines)
	option_lines = format_option_lines(question)
	answer_lines = format_answer_lines(question, preserve_newlines)
	set_shape_lines(slide_root, shape_ids["question"], prompt_lines)
	set_shape_lines(slide_root, shape_ids["options"], option_lines)
	set_shape_lines(slide_root, shape_ids["popup"], answer_lines)


#============================================
def format_prompt_lines(
	question: dict[str, object],
	preserve_newlines: bool,
) -> list[str]:
	"""
	Format prompt lines for rendering.

	Args:
		question: Question record.
		preserve_newlines: Keep prompt line breaks.

	Returns:
		list[str]: Prompt lines.
	"""
	lines = list(question.get("prompt_lines", []))
	if preserve_newlines:
		return normalize_lines(lines, preserve_newlines=True)
	combined = normalize_whitespace(" ".join(lines))
	return [combined] if combined else []


#============================================
def format_option_lines(question: dict[str, object]) -> list[str]:
	"""
	Format option lines for rendering.

	Args:
		question: Question record.

	Returns:
		list[str]: Option lines.
	"""
	lines = []
	style = question.get("style", "")
	for option in question.get("options", []):
		label = str(option.get("label", "")).upper()
		text = normalize_whitespace(str(option.get("text", "")))
		if style == "checkbox":
			lines.append(f"[ ] {text}".strip())
		else:
			lines.append(f"{label}) {text}".strip())
	return lines


#============================================
def format_answer_lines(
	question: dict[str, object],
	preserve_newlines: bool,
) -> list[str]:
	"""
	Format answer popup lines for rendering.

	Args:
		question: Question record.
		preserve_newlines: Keep feedback line breaks.

	Returns:
		list[str]: Answer popup lines.
	"""
	correct_labels = []
	for option in question.get("options", []):
		if option.get("correct"):
			label = str(option.get("label", "")).upper()
			if label:
				correct_labels.append(label)
	prefix = "Answer" if len(correct_labels) == 1 else "Answers"
	answer_line = f"{prefix}: {', '.join(correct_labels)}"
	lines = [answer_line]
	feedback_lines = list(question.get("feedback_lines", []))
	lines.extend(normalize_lines(feedback_lines, preserve_newlines))
	return [line for line in lines if line]


#============================================
def normalize_lines(lines: list[str], preserve_newlines: bool) -> list[str]:
	"""
	Normalize a list of lines.

	Args:
		lines: Input lines.
		preserve_newlines: Keep line boundaries.

	Returns:
		list[str]: Normalized lines.
	"""
	cleaned = []
	for line in lines:
		if preserve_newlines:
			text = normalize_whitespace(line)
		else:
			text = normalize_whitespace(line)
		if text:
			cleaned.append(text)
	return cleaned


#============================================
def normalize_whitespace(value: str) -> str:
	"""
	Normalize whitespace for rendering.

	Args:
		value: Input string.

	Returns:
		str: Normalized string.
	"""
	if not value:
		return ""
	text = value.replace("\t", " ").replace("\r", "\n")
	text = re.sub(r"\s+", " ", text)
	return text.strip()


#============================================
def set_shape_lines(
	slide_root,
	shape_id: str,
	lines: list[str],
) -> None:
	"""
	Set text lines on a shape within a slide XML tree.

	Args:
		slide_root: Slide XML root element.
		shape_id: Shape id to update.
		lines: Text lines to render.
	"""
	shape = find_shape_by_id(slide_root, shape_id)
	if shape is None:
		raise ValueError(f"Shape id {shape_id} not found in slide.")
	tx_body = shape.find(".//p:txBody", mc_template.PRESENTATION_NS)
	if tx_body is None:
		return
	ppr, rpr, end_rpr = extract_text_style(tx_body)
	for child in list(tx_body):
		if child.tag == f"{{{mc_template.PRESENTATION_NS['a']}}}p":
			tx_body.remove(child)
	if not lines:
		lines = [""]
	for line in lines:
		paragraph = build_paragraph(line, ppr, rpr, end_rpr)
		tx_body.append(paragraph)


#============================================
def find_shape_by_id(slide_root, shape_id: str):
	"""
	Find a shape element by id.

	Args:
		slide_root: Slide XML root.
		shape_id: Shape id to match.

	Returns:
		object | None: Shape element or None.
	"""
	for element in slide_root.findall(".//p:cNvPr", mc_template.PRESENTATION_NS):
		if element.get("id") != shape_id:
			continue
		parent = element.getparent()
		if parent is None:
			continue
		shape = parent.getparent()
		return shape
	return None


#============================================
def extract_text_style(tx_body) -> tuple[object | None, object | None, object | None]:
	"""
	Extract paragraph and run styling from a text body.

	Args:
		tx_body: Text body element.

	Returns:
		tuple: (pPr, rPr, endParaRPr) elements or None.
	"""
	paragraph = tx_body.find("a:p", mc_template.PRESENTATION_NS)
	if paragraph is None:
		return (None, None, None)
	ppr = paragraph.find("a:pPr", mc_template.PRESENTATION_NS)
	run = paragraph.find("a:r", mc_template.PRESENTATION_NS)
	rpr = None
	if run is not None:
		rpr = run.find("a:rPr", mc_template.PRESENTATION_NS)
	end_rpr = paragraph.find("a:endParaRPr", mc_template.PRESENTATION_NS)
	return (ppr, rpr, end_rpr)


#============================================
def build_paragraph(
	text: str,
	ppr,
	rpr,
	end_rpr,
):
	"""
	Build a paragraph element with text and styling.

	Args:
		text: Paragraph text.
		ppr: Paragraph properties element.
		rpr: Run properties element.
		end_rpr: End paragraph run properties element.

	Returns:
		object: Paragraph element.
	"""
	paragraph = etree.Element(f"{{{mc_template.PRESENTATION_NS['a']}}}p")
	if ppr is not None:
		paragraph.append(copy.deepcopy(ppr))
	run = etree.SubElement(
		paragraph, f"{{{mc_template.PRESENTATION_NS['a']}}}r"
	)
	if rpr is not None:
		run.append(copy.deepcopy(rpr))
	text_node = etree.SubElement(
		run, f"{{{mc_template.PRESENTATION_NS['a']}}}t"
	)
	text_node.text = text
	if end_rpr is not None:
		paragraph.append(copy.deepcopy(end_rpr))
	return paragraph


#============================================
def update_presentation_rels(
	working_dir: str,
	slide_count: int,
) -> list[str]:
	"""
	Update presentation relationships for slide parts.

	Args:
		working_dir: Template working directory.
		slide_count: Number of slides.

	Returns:
		list[str]: Assigned slide rIds in order.
	"""
	rels_path = os.path.join(
		working_dir,
		"ppt",
		"_rels",
		"presentation.xml.rels",
	)
	tree = etree.parse(rels_path)
	root = tree.getroot()
	used_ids = set()
	for rel in list(root):
		rel_id = rel.get("Id", "")
		rel_type = rel.get("Type", "")
		if rel_type == mc_template.SLIDE_REL_TYPE:
			root.remove(rel)
			continue
		if rel_id:
			used_ids.add(rel_id)
	slide_rids = allocate_rids(used_ids, slide_count)
	for index, rid in enumerate(slide_rids, 1):
		rel = etree.Element(f"{{{REL_NS}}}Relationship")
		rel.set("Id", rid)
		rel.set("Type", mc_template.SLIDE_REL_TYPE)
		rel.set("Target", f"slides/slide{index}.xml")
		root.append(rel)
	tree.write(rels_path, xml_declaration=True, encoding="UTF-8")
	return slide_rids


#============================================
def update_presentation_xml(
	working_dir: str,
	slide_rids: list[str],
) -> None:
	"""
	Update presentation.xml with slide id list.

	Args:
		working_dir: Template working directory.
		slide_rids: Slide relationship ids.
	"""
	pres_path = os.path.join(working_dir, "ppt", "presentation.xml")
	ns = {
		"p": mc_template.PRESENTATION_NS["p"],
		"r": R_NS,
	}
	tree = etree.parse(pres_path)
	root = tree.getroot()
	sld_list = root.find("p:sldIdLst", ns)
	if sld_list is None:
		sld_list = etree.SubElement(
			root, f"{{{mc_template.PRESENTATION_NS['p']}}}sldIdLst"
		)
	for child in list(sld_list):
		sld_list.remove(child)
	start_id = 256
	for index, rid in enumerate(slide_rids):
		sld_id = etree.SubElement(
			sld_list, f"{{{mc_template.PRESENTATION_NS['p']}}}sldId"
		)
		sld_id.set("id", str(start_id + index))
		sld_id.set(f"{{{R_NS}}}id", rid)
	tree.write(pres_path, xml_declaration=True, encoding="UTF-8")


#============================================
def update_content_types(working_dir: str, slide_count: int) -> None:
	"""
	Update [Content_Types].xml with slide overrides.

	Args:
		working_dir: Template working directory.
		slide_count: Number of slides.
	"""
	types_path = os.path.join(working_dir, "[Content_Types].xml")
	tree = etree.parse(types_path)
	root = tree.getroot()
	for override in list(root):
		if override.tag != f"{{{CONTENT_TYPES_NS}}}Override":
			continue
		part = override.get("PartName", "")
		if part.startswith("/ppt/slides/slide") and part.endswith(".xml"):
			root.remove(override)
	for index in range(1, slide_count + 1):
		override = etree.Element(f"{{{CONTENT_TYPES_NS}}}Override")
		override.set("PartName", f"/ppt/slides/slide{index}.xml")
		override.set("ContentType", SLIDE_CONTENT_TYPE)
		root.append(override)
	tree.write(types_path, xml_declaration=True, encoding="UTF-8")


#============================================
def allocate_rids(used_ids: set[str], count: int) -> list[str]:
	"""
	Allocate new relationship ids.

	Args:
		used_ids: Existing relationship ids.
		count: Number of ids to allocate.

	Returns:
		list[str]: Allocated rIds.
	"""
	rids = []
	candidate = 1
	while len(rids) < count:
		rid = f"rId{candidate}"
		if rid not in used_ids:
			rids.append(rid)
			used_ids.add(rid)
		candidate += 1
	return rids


#============================================
def write_xml(root, path: str) -> None:
	"""
	Write XML element tree to disk.

	Args:
		root: XML root element.
		path: Output path.
	"""
	tree = etree.ElementTree(root)
	tree.write(path, xml_declaration=True, encoding="UTF-8")


#============================================
def write_pptx(source_dir: str, output_path: str) -> None:
	"""
	Write a PPTX file from a source directory.

	Args:
		source_dir: Directory containing PPTX parts.
		output_path: Output PPTX path.
	"""
	with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
		for root, dirs, files in os.walk(source_dir):
			dirs.sort()
			files.sort()
			for filename in files:
				path = os.path.join(root, filename)
				rel_path = os.path.relpath(path, source_dir)
				archive.write(path, rel_path)
