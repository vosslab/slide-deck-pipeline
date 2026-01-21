# Standard Library
import os
import shutil
import subprocess


LIBREOFFICE_APP_PATH = "/Applications/LibreOffice.app/Contents/MacOS/soffice"


#============================================
def find_soffice() -> str | None:
	"""
	Return the soffice binary path if available.

	Returns:
		str | None: Path to soffice or None.
	"""
	if os.path.exists(LIBREOFFICE_APP_PATH):
		return LIBREOFFICE_APP_PATH
	return shutil.which("soffice")


#============================================
def require_soffice() -> str:
	"""
	Return the soffice binary path or raise.

	Returns:
		str: Path to soffice.
	"""
	soffice_bin = find_soffice()
	if not soffice_bin:
		raise FileNotFoundError("soffice not found. Install LibreOffice to convert ODP.")
	return soffice_bin


#============================================
def convert_odp_to_pptx(odp_path: str, work_dir: str) -> str:
	"""
	Convert an ODP file to PPTX using soffice.

	Args:
		odp_path: Path to the ODP file.
		work_dir: Output directory for the converted PPTX.

	Returns:
		str: Path to the converted PPTX file.
	"""
	soffice_bin = require_soffice()
	command = [
		soffice_bin,
		"--headless",
		"--norestore",
		"--safe-mode",
		"--convert-to",
		"pptx",
		"--outdir",
		work_dir,
		odp_path,
	]
	result = subprocess.run(command, capture_output=True, text=True, cwd=work_dir)
	if result.returncode != 0:
		message = result.stderr.strip() or result.stdout.strip()
		raise RuntimeError(f"ODP conversion failed: {message}")
	base_name = os.path.splitext(os.path.basename(odp_path))[0]
	pptx_path = os.path.join(work_dir, f"{base_name}.pptx")
	if not os.path.exists(pptx_path):
		raise FileNotFoundError(f"Converted PPTX not found: {pptx_path}")
	return pptx_path


#============================================
def convert_pptx_to_odp(pptx_path: str, output_path: str) -> None:
	"""
	Convert a PPTX to ODP using soffice.

	Args:
		pptx_path: Path to PPTX file.
		output_path: Desired ODP output path.
	"""
	soffice_bin = require_soffice()
	output_dir = os.path.dirname(output_path) or "."
	command = [
		soffice_bin,
		"--headless",
		"--norestore",
		"--safe-mode",
		"--convert-to",
		"odp",
		"--outdir",
		output_dir,
		pptx_path,
	]
	result = subprocess.run(command, capture_output=True, text=True, cwd=output_dir)
	if result.returncode != 0:
		message = result.stderr.strip() or result.stdout.strip()
		raise RuntimeError(f"PPTX to ODP conversion failed: {message}")
	expected_name = f"{os.path.splitext(os.path.basename(pptx_path))[0]}.odp"
	converted_path = os.path.join(output_dir, expected_name)
	if not os.path.exists(converted_path):
		raise FileNotFoundError(f"Converted ODP not found: {converted_path}")
	if os.path.abspath(converted_path) != os.path.abspath(output_path):
		os.replace(converted_path, output_path)
