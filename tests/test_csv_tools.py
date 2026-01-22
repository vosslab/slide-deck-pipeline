import random

import pytest

import remove_duplicate_slides_from_csv as remove_duplicate
import set_master_name_in_csv as set_master


#============================================
def test_set_master_name_overwrites_all_rows() -> None:
	"""
	apply_master_name_to_rows overwrites master_name on every row by default.
	"""
	rows = [
		{"master_name": "", "slide_hash": "a"},
		{"master_name": "old", "slide_hash": "b"},
	]
	updated, skipped = set_master.apply_master_name_to_rows(
		rows,
		"custom",
		only_empty=False,
	)
	assert updated == 2
	assert skipped == 0
	assert [row["master_name"] for row in rows] == ["custom", "custom"]


#============================================
def test_set_master_name_only_empty_skips_non_empty() -> None:
	"""
	apply_master_name_to_rows can skip rows that already have a master_name.
	"""
	rows = [
		{"master_name": "", "slide_hash": "a"},
		{"master_name": "keep", "slide_hash": "b"},
		{"master_name": "  ", "slide_hash": "c"},
	]
	updated, skipped = set_master.apply_master_name_to_rows(
		rows,
		"custom",
		only_empty=True,
	)
	assert updated == 2
	assert skipped == 1
	assert [row["master_name"] for row in rows] == ["custom", "keep", "custom"]


#============================================
def test_remove_duplicate_slides_is_reproducible_with_seed() -> None:
	"""
	dedupe_rows_random_choice is deterministic when using the same RNG seed.
	"""
	rows = [
		{"slide_hash": "aaa", "source_slide_index": "1"},
		{"slide_hash": "aaa", "source_slide_index": "2"},
		{"slide_hash": "bbb", "source_slide_index": "3"},
		{"slide_hash": "aaa", "source_slide_index": "4"},
		{"slide_hash": "", "source_slide_index": "5"},
	]

	rng_one = random.Random(123)
	deduped_one, removed_one = remove_duplicate.dedupe_rows_random_choice(
		rows,
		"slide_hash",
		rng_one,
	)
	rng_two = random.Random(123)
	deduped_two, removed_two = remove_duplicate.dedupe_rows_random_choice(
		rows,
		"slide_hash",
		rng_two,
	)

	assert removed_one == 2
	assert removed_two == 2
	assert [row["source_slide_index"] for row in deduped_one] == [
		row["source_slide_index"] for row in deduped_two
	]

	# One 'aaa' row kept, 'bbb' kept, blank-hash row always kept.
	assert sum(1 for row in deduped_one if row["slide_hash"] == "aaa") == 1
	assert sum(1 for row in deduped_one if row["slide_hash"] == "bbb") == 1
	assert sum(1 for row in deduped_one if row["slide_hash"] == "") == 1


#============================================
def test_remove_duplicate_slides_keeps_unique_hashes() -> None:
	"""
	Unique hashes are never removed.
	"""
	rows = [
		{"slide_hash": "a", "source_slide_index": "1"},
		{"slide_hash": "b", "source_slide_index": "2"},
		{"slide_hash": "c", "source_slide_index": "3"},
	]
	deduped, removed = remove_duplicate.dedupe_rows_random_choice(
		rows,
		"slide_hash",
		random.Random(0),
	)
	assert removed == 0
	assert deduped == rows

