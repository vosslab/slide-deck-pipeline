# Standard Library
import re


#============================================
def normalize_whitespace(value: str) -> str:
	"""
	Normalize whitespace by collapsing runs to single spaces.

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
		text = normalize_whitespace(line)
		if text:
			cleaned.append(text)
	return cleaned


#============================================
def parse_tab_indented_lines(
	text_value: str,
	keep_blank_lines: bool,
	strip_text: bool,
) -> list[tuple[int, str]]:
	"""
	Parse text into tab-indented lines.

	Args:
		text_value: Text with leading tabs for indentation.
		keep_blank_lines: Preserve empty lines as blank entries.
		strip_text: Strip text content after removing tabs.

	Returns:
		list[tuple[int, str]]: List of (level, text).
	"""
	if not text_value:
		return []
	lines = []
	cleaned = text_value.replace("\r\n", "\n").replace("\r", "\n")
	for raw_line in cleaned.split("\n"):
		if raw_line == "":
			if keep_blank_lines:
				lines.append((0, ""))
			continue
		if not keep_blank_lines and not raw_line.strip():
			continue
		level = len(raw_line) - len(raw_line.lstrip("\t"))
		text = raw_line.lstrip("\t")
		if strip_text:
			text = text.strip()
		lines.append((level, text))
	return lines


#============================================
def normalize_simple_name(value: str) -> str:
	"""
	Normalize a name for simple matching.

	Args:
		value: Input value.

	Returns:
		str: Normalized value.
	"""
	if not value:
		return ""
	return value.strip().lower().replace(" ", "_")
