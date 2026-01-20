import pytest

pytest.skip(
	"Skip commit_changelog tests: relies on git, subprocess, files, and user input.",
	allow_module_level=True,
)
