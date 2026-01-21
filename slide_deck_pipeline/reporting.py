#============================================
def print_warnings(warnings: list[str]) -> None:
	"""
	Print warnings if present.

	Args:
		warnings: Warning messages.
	"""
	if not warnings:
		return
	print("Warnings:")
	for message in warnings:
		print(f"- {message}")


#============================================
def print_summary(label: str, count: int) -> None:
	"""
	Print a simple summary line.

	Args:
		label: Summary label.
		count: Count value.
	"""
	print(f"{label}: {count}")
