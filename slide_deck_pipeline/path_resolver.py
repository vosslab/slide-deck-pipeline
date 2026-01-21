# Standard Library
import os


#============================================
def _list_subdirs(root: str) -> list[str]:
	"""
	Return immediate subdirectories of a root path.

	Args:
		root: Root directory.

	Returns:
		list[str]: Sorted subdirectory paths.
	"""
	if not root or not os.path.isdir(root):
		return []
	entries = []
	for entry in os.listdir(root):
		path = os.path.join(root, entry)
		if os.path.isdir(path):
			entries.append(path)
	return sorted(entries)


#============================================
def _collect_matches(roots: list[str], relative_path: str) -> list[str]:
	"""
	Collect matching paths across roots.

	Args:
		roots: Root directories.
		relative_path: Relative path or filename.

	Returns:
		list[str]: Sorted matches.
	"""
	matches = []
	for root in roots:
		if not root:
			continue
		candidate = os.path.join(root, relative_path)
		if os.path.exists(candidate):
			matches.append(os.path.abspath(candidate))
	return sorted(matches)


#============================================
def resolve_path(
	target_path: str,
	input_dir: str | None = None,
	strict: bool = False,
) -> tuple[str, list[str]]:
	"""
	Resolve a file path using deterministic search order for relative paths.

	Args:
		target_path: File path (absolute or relative).
		input_dir: Optional base directory (for example YAML or CSV directory).
		strict: Treat ambiguous matches as errors.

	Returns:
		tuple[str, list[str]]: Resolved path and warnings.
	"""
	if not target_path:
		raise ValueError("Path is required.")
	warnings = []
	if os.path.isabs(target_path):
		if os.path.exists(target_path):
			return (target_path, warnings)
		raise FileNotFoundError(f"Path not found: {target_path}")
	cwd = os.getcwd()
	cwd_parent = os.path.abspath(os.path.join(cwd, ".."))
	levels = [
		[cwd],
		[cwd_parent],
		_list_subdirs(cwd),
	]
	if input_dir:
		levels.extend(
			[
				[os.path.abspath(input_dir)],
				[os.path.abspath(os.path.join(input_dir, ".."))],
				_list_subdirs(input_dir),
			]
		)
	for roots in levels:
		matches = _collect_matches(roots, target_path)
		if not matches:
			continue
		if len(matches) == 1:
			return (matches[0], warnings)
		if strict:
			raise ValueError(
				f"Ambiguous path matches for {target_path}: {matches}"
			)
		warnings.append(
			f"Ambiguous path matches for {target_path}; using {matches[0]}"
		)
		return (matches[0], warnings)
	raise FileNotFoundError(f"Path not found: {target_path}")
